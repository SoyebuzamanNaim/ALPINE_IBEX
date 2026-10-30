/**
 * FLARE-X Aerospace Mission Control Frontend Application
 * Interacts with FastAPI backend or operates in resilient client-side fallback mode.
 * Presents curated NASA microgravity observations and gated model inference.
 */

// API Base URL (auto-detect if served by FastAPI, else fallback to localhost:8000)
const API_BASE = (window.location.protocol.startsWith('http') && !window.location.origin.includes('file'))
  ? (window.location.hostname === 'localhost' && window.location.port && window.location.port !== '8000' && window.location.port !== '80' && window.location.port !== '443'
      ? 'http://localhost:8000'
      : '')
  : 'http://localhost:8000';

function escapeHTML(value) {
  return String(value ?? '').replace(/[&<>"']/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[char]);
}

function safeHttpUrl(value, fallback = '#') {
  if (!String(value ?? '').trim()) return fallback;
  try {
    const url = new URL(String(value ?? ''), window.location.origin);
    return url.protocol === 'https:' || url.protocol === 'http:' ? url.href : fallback;
  } catch (_) {
    return fallback;
  }
}

// ============================================================================
// Published NASA flammability boundary - NTRS 20210011385, BASS-II Summary
// Report, Eq (6.1). This is NASA's own fitted boundary, not a model we trained,
// so it needs no backend, no model artifact and carries no accuracy claim.
//
//   X_O2 = 6*exp(-0.5*a) + 0.0167*a + 13.4        [vol %, a in 1/s]
//   a    = (3/2)*(U/r)*(r/r_o)^0.5                 r_o = 0.318 cm
//   regime separator: U/U_D = 1 with U_D = 2 cm/s
//
// Fitted to cast-PMMA rods over 13.6-22.2 % O2. It describes extinction of an
// ESTABLISHED flame, so it does not predict whether ignition will take hold.
// ============================================================================
const NASA_BOUNDARY = {
  R_O: 0.318,                       // cm, the 1/4-inch base rod radius
  U_D: 2.0,                         // cm/s, diffusive velocity
  CITATION: 'NTRS 20210011385 Eq (6.1)',
  URL: 'https://ntrs.nasa.gov/citations/20210011385',
  VALID_O2: [13.6, 22.2],
  VALID_FLOW: [0, 55],             // BASS-II rod tests described in the report abstract
  NOMINAL_PRESSURE_KPA: 101.3,   // ISS glovebox conditions; no pressure-dependent fit
  // radii of the three cast-PMMA rods flown in BASS-II, in cm
  RADII: { '1/4 inch': 0.3175, '3/8 inch': 0.47625, '1/2 inch': 0.635 },

  stretch(U_cm_s, r_cm) {
    if (!(r_cm > 0)) return NaN;
    return 1.5 * (U_cm_s / r_cm) * Math.sqrt(r_cm / this.R_O);
  },
  limitO2(a) {
    return 6.0 * Math.exp(-0.5 * a) + 0.0167 * a + 13.4;
  },
  regime(U_cm_s) {
    return U_cm_s > this.U_D ? 'blowoff' : 'quench';
  },
  // Returns null when the published fit does not cover the request.
  evaluate(o2_pct, U_cm_s, r_cm) {
    const a = this.stretch(U_cm_s, r_cm);
    if (!isFinite(a)) return null;
    const limit = this.limitO2(a);
    return {
      stretch: a,
      limitO2: limit,
      margin: o2_pct - limit,
      regime: this.regime(U_cm_s),
      flammable: o2_pct > limit,
      inFitRange: o2_pct >= this.VALID_O2[0] && o2_pct <= this.VALID_O2[1],
      citation: this.CITATION,
      url: this.URL
    };
  }
};

// Current Scenario State
const state = {
  material: 'PMMA',
  rod_radius_cm: 0.3175,   // 1/4-inch cast PMMA rod, the BASS-II base case
  oxygen_pct: 21.0,
  pressure_kpa: 101.3,
  flow_cm_s: 5.0,
  extrapolate: false,
  boundaryData: null,
  activeTab: 'view-scenario-lab',
  sweepRunning: false,
  experiments: [],
  materialCounts: {},
  sweepInterval: null
};

const FUEL_PROPERTIES = {
  'PMMA': { desc: 'Thermally thick / non-charring acrylic', prop: 'Density: 1.18 g/cm³ · C₅H₈O₂' },
  'Cellulose': { desc: 'Thermally thin ashless filter paper', prop: 'Density: 1.50 g/cm³ · C₆H₁₀O₅' },
  'Cotton': { desc: 'Thin woven porous fabric specimen', prop: 'Density: 1.54 g/cm³ · Natural' },
  'Nomex': { desc: 'Flame-resistant aramid synthetic polymer', prop: 'Aramid' },
  'Cotton-Fiberglass': { desc: 'Composite fabric specimen', prop: 'Cotton and fiberglass' },
  'Mylar': { desc: 'Polyester film specimen', prop: 'Polyester' },
  'Silicone': { desc: 'Silicone specimen', prop: 'Elastomer' },
  'Ultem': { desc: 'Polyetherimide specimen', prop: 'Polyetherimide' }
};

// Smooth Tabular Number Ticker (Emil Kowalski Spec)
function animateNumber(element, endVal, suffix = '', duration = 200) {
  if (!element) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    element.textContent = `${endVal}${suffix}`;
    element._currentVal = endVal;
    return;
  }
  const startVal = typeof element._currentVal === 'number' ? element._currentVal : (parseFloat(element.textContent) || 0);
  const startTime = performance.now();
  const delta = endVal - startVal;

  function step(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const easeProgress = 1 - Math.pow(1 - progress, 3);
    const current = Math.round(startVal + delta * easeProgress);
    element.textContent = `${current}${suffix}`;
    if (progress < 1) {
      requestAnimationFrame(step);
    } else {
      element._currentVal = endVal;
    }
  }
  requestAnimationFrame(step);
}

// Background reticle pulse loop
let reticleAnimId = null;
function startReticleLoop() {
  if (reticleAnimId) return;
  let lastTime = 0;
  function loop(now) {
    if (state.activeTab === 'view-scenario-lab' && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      if (now - lastTime > 40) {
        lastTime = now;
        drawBoundaryCanvas();
      }
    }
    reticleAnimId = requestAnimationFrame(loop);
  }
  reticleAnimId = requestAnimationFrame(loop);
}

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
  setupTabs();
  setupSliders();
  setupPresets();
  setupNlpParser();
  setupCanvasInteraction();
  setupSweepView();
  setupAtlasView();
  setupConflictExplorer();
  setupCoverageMapView();
  setupCitationInspector();
  
  // Initial prediction & boundary fetch
  triggerScenarioEvaluation();
  fetchBoundarySlice();
  loadDatasetsAndModel();
  loadModelStatus();
  startReticleLoop();
  updateCoordHud();
});

// Tab Navigation
function setupTabs() {
  const tabs = document.querySelectorAll('.ops-nav-btn, .nav-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => {
        t.classList.remove('active');
        t.setAttribute('aria-selected', 'false');
      });
      tab.classList.add('active');
      tab.setAttribute('aria-selected', 'true');

      const targetId = tab.getAttribute('aria-controls');
      document.querySelectorAll('.view-panel').forEach(panel => {
        if (panel.id === targetId) {
          panel.classList.add('active');
          panel.removeAttribute('hidden');
        } else {
          panel.classList.remove('active');
          panel.setAttribute('hidden', 'true');
        }
      });
      state.activeTab = targetId;

      if (targetId === 'view-scenario-lab') {
        drawBoundaryCanvas();
      } else if (targetId === 'view-counterfactual-sweep') {
        fetchSweepData();
        drawSweepCanvas();
      } else if (targetId === 'view-conflict-explorer') {
        loadConflictExplorerData();
      } else if (targetId === 'view-coverage-map') {
        loadCoverageMapData();
      }
    });
  });
}

// Sliders and Inputs Setup
function setupSliders() {
  const o2Slider = document.getElementById('input-o2');
  const pSlider = document.getElementById('input-pressure');
  const flowSlider = document.getElementById('input-flow');
  const matSelect = document.getElementById('input-material');
  const extrapToggle = document.getElementById('toggle-extrapolate');

  o2Slider.addEventListener('input', (e) => {
    state.oxygen_pct = parseFloat(e.target.value);
    document.getElementById('readout-o2').textContent = `${state.oxygen_pct.toFixed(1)} %`;
    updateCoordHud();
    debounceEvaluation();
    scheduleSweepRefresh();
  });

  pSlider.addEventListener('input', (e) => {
    state.pressure_kpa = parseFloat(e.target.value);
    document.getElementById('readout-pressure').textContent = `${state.pressure_kpa.toFixed(1)} kPa`;
    updateCoordHud();
    debounceEvaluation();
    debounceBoundarySlice();
    scheduleSweepRefresh();
  });

  flowSlider.addEventListener('input', (e) => {
    state.flow_cm_s = parseFloat(e.target.value);
    document.getElementById('readout-flow').textContent = `${state.flow_cm_s.toFixed(1)} cm/s`;
    updateCoordHud();
    debounceEvaluation();
    scheduleSweepRefresh();
  });

  matSelect.addEventListener('change', (e) => {
    state.material = e.target.value;
    updateMaterialInfo();
    triggerScenarioEvaluation();
    fetchBoundarySlice();
    scheduleSweepRefresh();
  });

  extrapToggle.addEventListener('change', (e) => {
    state.extrapolate = e.target.checked;
    if (state.extrapolate) {
      o2Slider.max = '50.0';
      flowSlider.max = '65.0';
      o2Slider.value = '42.0';
      state.oxygen_pct = 42.0;
      document.getElementById('readout-o2').textContent = '42.0 %';
    } else {
      o2Slider.max = '34.0';
      flowSlider.max = '45.0';
      o2Slider.value = '21.0';
      state.oxygen_pct = 21.0;
      document.getElementById('readout-o2').textContent = '21.0 %';
    }
    updateCoordHud();
    triggerScenarioEvaluation();
    scheduleSweepRefresh();
  });
}

function updateMaterialInfo() {
  const count = state.materialCounts[state.material];
  const sampleBadge = document.getElementById('mat-samples-badge');
  if (sampleBadge) sampleBadge.textContent = count == null ? 'Evidence count unavailable' : `${count} observations`;
  const fuelProp = FUEL_PROPERTIES[state.material] || { desc: 'Solid fuel', prop: 'Microgravity' };
  const specInfo = document.getElementById('fuel-spec-info');
  if (specInfo) {
    const description = document.createElement('span');
    const property = document.createElement('span');
    description.textContent = fuelProp.desc;
    property.className = 'spec-prop';
    property.textContent = fuelProp.prop;
    specInfo.replaceChildren(description, property);
  }
  const ribbonFuel = document.getElementById('ribbon-active-fuel');
  if (ribbonFuel) ribbonFuel.textContent = `${state.material} (${fuelProp.desc.split('/')[0].trim()})`;
}

// Preset Buttons
function setupPresets() {
  const pIss = document.getElementById('preset-iss-standard');
  const pExp = document.getElementById('preset-exploration');
  const pNear = document.getElementById('preset-near-extinction');

  function clearPresetActives() {
    [pIss, pExp, pNear].forEach(p => p && p.classList.remove('active-preset'));
  }

  pIss.addEventListener('click', () => {
    clearPresetActives();
    pIss.classList.add('active-preset');
    updateInputs(21.0, 101.3, 5.0, 'PMMA');
  });
  pExp.addEventListener('click', () => {
    clearPresetActives();
    pExp.classList.add('active-preset');
    updateInputs(34.0, 56.5, 10.0, 'PMMA');
  });
  pNear.addEventListener('click', () => {
    clearPresetActives();
    pNear.classList.add('active-preset');
    updateInputs(16.5, 101.3, 3.0, 'PMMA');
  });
}

function updateInputs(o2, p, flow, mat) {
  state.oxygen_pct = o2;
  state.pressure_kpa = p;
  state.flow_cm_s = flow;
  state.material = mat;

  document.getElementById('input-o2').value = o2;
  document.getElementById('input-pressure').value = p;
  document.getElementById('input-flow').value = flow;
  document.getElementById('input-material').value = mat;

  document.getElementById('readout-o2').textContent = `${o2.toFixed(1)} %`;
  document.getElementById('readout-pressure').textContent = `${p.toFixed(1)} kPa`;
  document.getElementById('readout-flow').textContent = `${flow.toFixed(1)} cm/s`;

  updateCoordHud();
  updateMaterialInfo();
  triggerScenarioEvaluation();
  fetchBoundarySlice();
  scheduleSweepRefresh();
}

function updateCoordHud() {
  const hud = document.getElementById('coord-hud-val');
  if (hud) {
    hud.textContent = `${state.oxygen_pct.toFixed(1)}% O₂ · ${state.flow_cm_s.toFixed(1)} cm/s · ${state.pressure_kpa.toFixed(1)} kPa`;
  }
}

// Interactive Canvas Point & Drag Handler
function setupCanvasInteraction() {
  const canvas = document.getElementById('flammability-boundary-canvas');
  if (!canvas) return;

  let isDragging = false;

  function probeFromEvent(e) {
    if (!state.boundaryData) return;
    const rect = canvas.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const clickY = e.clientY - rect.top;

    const padLeft = 70;
    const padBottom = 45;
    const padRight = 35;
    const padTop = 35;
    const plotW = rect.width - padLeft - padRight;
    const plotH = rect.height - padTop - padBottom;

    const b = state.boundaryData;
    const o2Min = b.oxygen_range[0];
    const o2Max = b.oxygen_range[1];
    const flowMin = b.flow_range[0];
    const flowMax = b.flow_range[1];

    if (clickX < padLeft || clickX > padLeft + plotW || clickY < padTop || clickY > padTop + plotH) return;

    const normX = Math.max(0, Math.min(1, (clickX - padLeft) / plotW));
    const normY = Math.max(0, Math.min(1, (padTop + plotH - clickY) / plotH));

    const newO2 = Math.round((o2Min + normX * (o2Max - o2Min)) * 10) / 10;
    const newFlow = Math.round((flowMin + normY * (flowMax - flowMin)) * 10) / 10;

    state.oxygen_pct = newO2;
    state.flow_cm_s = newFlow;

    const o2In = document.getElementById('input-o2');
    const fIn = document.getElementById('input-flow');
    if (o2In) o2In.value = newO2;
    if (fIn) fIn.value = newFlow;

    document.getElementById('readout-o2').textContent = `${newO2.toFixed(1)} %`;
    document.getElementById('readout-flow').textContent = `${newFlow.toFixed(1)} cm/s`;

    updateCoordHud();
    debounceEvaluation();
    scheduleSweepRefresh();
  }

  canvas.addEventListener('pointerdown', (e) => {
    isDragging = true;
    probeFromEvent(e);
  });
  window.addEventListener('pointermove', (e) => {
    if (isDragging) probeFromEvent(e);
  });
  window.addEventListener('pointerup', () => {
    isDragging = false;
  });
}

// Debounce Utilities
let evalTimeout = null;
function debounceEvaluation() {
  clearTimeout(evalTimeout);
  setNearestEvidenceStatus('Loading observations for the selected conditions…');
  evalTimeout = setTimeout(triggerScenarioEvaluation, 100);
}

let boundaryTimeout = null;
function debounceBoundarySlice() {
  clearTimeout(boundaryTimeout);
  state.boundaryData = null;
  drawOfflineCanvas('Loading boundary for selected conditions…');
  boundaryTimeout = setTimeout(fetchBoundarySlice, 200);
}

// Trigger Scenario Prediction API
let evaluationGeneration = 0;
function setNearestEvidenceStatus(message) {
  const list = document.getElementById('nearest-cards-list');
  if (list) list.textContent = message;
}

async function triggerScenarioEvaluation() {
  const generation = ++evaluationGeneration;
  const payload = {
    oxygen_pct: state.oxygen_pct,
    pressure_kpa: state.pressure_kpa,
    flow_cm_s: state.flow_cm_s,
    material: state.material
  };
  setNearestEvidenceStatus('Loading observations for the selected conditions…');
  const isCurrent = () => generation === evaluationGeneration &&
    payload.oxygen_pct === state.oxygen_pct &&
    payload.pressure_kpa === state.pressure_kpa &&
    payload.flow_cm_s === state.flow_cm_s &&
    payload.material === state.material;

  try {
    const res = await fetch(`${API_BASE}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const data = await res.json();
    if (!isCurrent()) return;
    renderPredictionResults(data);
  } catch (err) {
    if (!isCurrent()) return;
    console.warn('API unreachable; falling back to the published NASA boundary:', err);
    // No simulated model output. We show NASA's own published boundary instead,
    // which is deterministic and needs no backend.
    renderPublishedBoundary(payload);
  }
}

// Render Prediction UI according to the 4-Tier Scientific State Protocol
function renderPredictionResults(data) {
  const alertBanner = document.getElementById('envelope-alert-banner');
  const alertTitle = document.getElementById('alert-title');
  const alertMsg = document.getElementById('alert-message');
  const badge = document.getElementById('regime-badge');
  const confPill = document.getElementById('confidence-pill');
  const briefing = document.getElementById('operator-briefing-text');
  const expText = document.getElementById('explanation-text-display');

  // Scientific State Protocol elements
  const stateTierPill = document.getElementById('state-tier-pill');
  const stateTierLabel = document.getElementById('state-tier-label');
  const stateTierExplainer = document.getElementById('state-tier-explainer');

  // Probability elements
  const pNoSpread = document.getElementById('val-prob-no-spread');
  const pMarginal = document.getElementById('val-prob-marginal');
  const pSpread = document.getElementById('val-prob-spread');
  const bNoSpread = document.getElementById('bar-seg-no-spread');
  const bMarginal = document.getElementById('bar-seg-marginal');
  const bSpread = document.getElementById('bar-seg-spread');

  // Physics Telemetry Elements
  const o2 = state.oxygen_pct;
  const flow = state.flow_cm_s;
  const da = flow > 0.1 ? (Math.pow(o2 / 21.0, 2) * (15.0 / flow)).toFixed(1) : '> 50.0';
  const pe = (flow * 0.5 / 0.22).toFixed(1);

  const daEl = document.getElementById('telemetry-damkohler');
  const peEl = document.getElementById('telemetry-peclet');
  const mgEl = document.getElementById('telemetry-margin');

  // These are coarse scaling heuristics for operator intuition only. They are NOT model
  // outputs and are not fitted to the NASA data. Ferkul (NTRS 19890014267) reports that the
  // Damkohler number alone does not predict spread or extinction near the quench limit.
  if (daEl) daEl.textContent = `Da ~ ${da} — illustrative scaling only, not a model output`;
  if (peEl) peEl.textContent = `Pe ~ ${pe} — illustrative scaling only, not a model output`;
  if (mgEl) {
    mgEl.textContent = 'Not established for this material and geometry';
    mgEl.className = 'phys-val';
  }

  if (data.status === 'conflicting_evidence' || data.status === 'insufficient_material_evidence' || data.status === 'audit_failed') {
    const conflict = data.status === 'conflicting_evidence';
    const sparse = data.status === 'insufficient_material_evidence';
    const reason = data.explanation || (conflict
      ? 'Experiments at identical model inputs have conflicting outcomes.'
      : sparse
        ? 'Too few distinct conditions are recorded for this material.'
        : 'The final evidence audit failed; no model result is released.');
    if (stateTierPill) stateTierPill.className = 'state-tier-pill tier-abstention';
    if (stateTierLabel) stateTierLabel.textContent = conflict ? 'CONFLICTING EVIDENCE'
      : sparse ? 'INSUFFICIENT MATERIAL EVIDENCE' : 'EVIDENCE AUDIT FAILED';
    if (stateTierExplainer) stateTierExplainer.textContent = conflict
      ? 'The four model inputs do not resolve these observations'
      : sparse ? 'Too few distinct observations for a material-specific estimate'
        : 'Final evidence verification did not pass';
    if (alertBanner) alertBanner.classList.remove('hidden');
    if (alertTitle) alertTitle.textContent = conflict ? 'EXPERIMENTAL OUTCOMES DISAGREE'
      : sparse ? 'MATERIAL EVIDENCE IS TOO SPARSE' : 'FINAL EVIDENCE AUDIT FAILED';
    if (alertMsg) alertMsg.textContent = reason;
    if (badge) {
      badge.className = 'regime-status-badge regime-refusal';
      badge.textContent = conflict ? 'CONFLICTING EVIDENCE · NO INFERENCE'
        : sparse ? 'INSUFFICIENT EVIDENCE · NO INFERENCE' : 'AUDIT FAILED · NO INFERENCE';
    }
    if (confPill) confPill.textContent = 'NO PROBABILITY AVAILABLE';
    [pNoSpread, pMarginal, pSpread].forEach(el => { if (el) el.textContent = 'N/A'; });
    [bNoSpread, bMarginal, bSpread].forEach(el => { if (el) el.style.width = '0%'; });
    if (briefing) briefing.textContent = conflict
      ? 'Observed outcomes differ at these recorded conditions. Inspect both source experiments; no single outcome is supported.'
      : sparse ? 'Too few distinct material conditions have been recorded to support a model estimate. Inspect the available source observations.'
        : 'The model result failed its final evidence audit and has been withheld. Inspect the available source observations.';
    if (expText) expText.textContent = reason;
    renderNearestExperiments(data.nearest_experiments || []);
    drawBoundaryCanvas();
    return;
  }

  if (data.status === 'model_unvalidated') {
    const validationReason = data.explanation || data.warning_message || 'Model validation is unavailable.';
    if (stateTierPill) stateTierPill.className = 'state-tier-pill tier-abstention';
    if (stateTierLabel) stateTierLabel.textContent = 'MODEL INFERENCE WITHHELD';
    if (stateTierExplainer) stateTierExplainer.textContent = validationReason;
    if (alertBanner) alertBanner.classList.remove('hidden');
    if (alertTitle) alertTitle.textContent = 'MODEL VALIDATION GATE';
    if (alertMsg) alertMsg.textContent = validationReason;
    if (badge) {
      badge.className = 'regime-status-badge regime-refusal';
      badge.textContent = 'MODEL INFERENCE WITHHELD';
    }
    if (confPill) confPill.textContent = 'NO PROBABILITY AVAILABLE';
    [pNoSpread, pMarginal, pSpread].forEach(el => { if (el) el.textContent = 'N/A'; });
    [bNoSpread, bMarginal, bSpread].forEach(el => { if (el) el.style.width = '0%'; });
    if (briefing) briefing.textContent = `Model inference is withheld: ${validationReason} Available NASA observations can be inspected below.`;
    if (expText) expText.textContent = validationReason;
    renderNearestExperiments(data.nearest_experiments || []);
    drawBoundaryCanvas();
    return;
  }

  if (!data.in_training_range) {
    // TIER 3: INSUFFICIENT EVIDENCE / ABSTENTION
    if (stateTierPill) {
      stateTierPill.className = 'state-tier-pill tier-abstention';
      if (stateTierLabel) stateTierLabel.textContent = 'INSUFFICIENT EVIDENCE (ABSTENTION)';
      if (stateTierExplainer) stateTierExplainer.textContent = 'Requested conditions exceed the documented model envelope';
    }

    if (alertBanner) alertBanner.classList.remove('hidden');
    if (alertTitle) alertTitle.textContent = 'CRITICAL SAFETY REFUSAL: CONDITIONS OUTSIDE AUDITED ENVELOPE';
    const reasons = (data.out_of_range_reasons || []).map(r => r.reason).join(' ');
    if (alertMsg) alertMsg.textContent = reasons || data.warning_message || 'Requested parameters are outside NASA training data.';

    if (badge) {
      badge.className = 'regime-status-badge regime-refusal';
      badge.textContent = 'SAFETY REFUSAL: OUT OF ENVELOPE';
    }
    if (confPill) confPill.textContent = 'INFERENCE REFUSED';

    if (pNoSpread) pNoSpread.textContent = 'N/A';
    if (pMarginal) pMarginal.textContent = 'N/A';
    if (pSpread) pSpread.textContent = 'N/A';
    if (bNoSpread) bNoSpread.style.width = '0%';
    if (bMarginal) bMarginal.style.width = '0%';
    if (bSpread) bSpread.style.width = '0%';

    if (briefing) {
      briefing.textContent = `MODEL REFUSAL: The requested combination is outside the supported research envelope. Nearby observations remain available for inspection; no operational conclusion is made.`;
    }
    if (expText) {
      expText.textContent = data.explanation || 'Requested conditions are outside the published experimental envelope. No prediction is made.';
    }
  } else {
    // In-Domain: Check if it's Tier 1 (Verified Observation) or Tier 2 (Model Estimate)
    if (alertBanner) alertBanner.classList.add('hidden');

    const exactMatch = (data.nearest_experiments || []).find(e =>
      e.material === state.material &&
      Math.abs(e.oxygen_pct - state.oxygen_pct) < 0.001 &&
      Math.abs(e.pressure_kpa - state.pressure_kpa) < 0.001 &&
      Math.abs(e.flow_cm_s - state.flow_cm_s) < 0.001
    );

    if (exactMatch) {
      // A matching observation supports inspection, but does not turn the model result into a measurement.
      if (stateTierPill) {
        stateTierPill.className = 'state-tier-pill tier-estimate';
        if (stateTierLabel) stateTierLabel.textContent = 'MODEL ESTIMATE';
        if (stateTierExplainer) stateTierExplainer.textContent = `Matching observation: ${exactMatch.experiment_id} (${exactMatch.outcome})`;
      }
    } else {
      // TIER 2: MODEL ESTIMATE
      if (stateTierPill) {
        stateTierPill.className = 'state-tier-pill tier-estimate';
        if (stateTierLabel) stateTierLabel.textContent = 'MODEL ESTIMATE';
        if (stateTierExplainer) stateTierExplainer.textContent = `Supervised model · Grouped CV ${(data.model.cv_accuracy * 100).toFixed(1)}% · research estimate`;
      }
    }

    const pred = data.prediction;
    const probs = data.probabilities;

    if (badge) {
      badge.className = `regime-status-badge regime-${pred ? pred.replace('_', '-') : 'spread'}`;
      badge.textContent = pred === 'spread' ? 'Sustained Flame Spread' : (pred === 'marginal_spread' ? 'Marginal Spread (Unsteady)' : 'Extinction / No Spread');
    }

    const confPct = Math.round((probs[pred] || 0) * 100);
    if (confPill) confPill.textContent = `${confPct}% Probability`;

    const pctNo = Math.round((probs.no_spread || 0) * 100);
    const pctMarg = Math.round((probs.marginal_spread || 0) * 100);
    const pctSp = Math.round((probs.spread || 0) * 100);

    animateNumber(pNoSpread, pctNo, '%', 200);
    animateNumber(pMarginal, pctMarg, '%', 200);
    animateNumber(pSpread, pctSp, '%', 200);

    if (bNoSpread) bNoSpread.style.width = `${pctNo}%`;
    if (bMarginal) bMarginal.style.width = `${pctMarg}%`;
    if (bSpread) bSpread.style.width = `${pctSp}%`;

    if (briefing) {
      if (pred === 'spread') {
        briefing.textContent = `MODEL ESTIMATE: Flame spread is predicted for this scenario. Inspect the cited observations and experimental limitations before using this result.`;
      } else if (pred === 'marginal_spread') {
        briefing.textContent = 'MODEL ESTIMATE: Marginal spread is predicted for this scenario. The precise behavior is uncertain; inspect the cited observations and limitations.';
      } else {
        briefing.textContent = `MODEL ESTIMATE: No sustained spread is predicted for this scenario. This result does not establish operational safety or flight certification.`;
      }
    }

    if (expText) {
      expText.textContent = data.explanation || 'Prediction generated from empirical gradient boosted model.';
    }
  }

  // Render Nearest Experiments List
  renderNearestExperiments(data.nearest_experiments || []);

  // Update canvas reticle
  drawBoundaryCanvas();
}

// TIER 4: SERVICE UNAVAILABLE (Honest state without simulated mock predictions)
// Render the published NASA boundary result. Used when the backend is unreachable
// (the static GitHub Pages deployment) and as a physics cross-check when it is not.
// Shows an oxygen margin against NASA's own fitted limit. No probabilities are
// shown, because a deterministic boundary does not produce any.
function renderPublishedBoundary(payload) {
  setNearestEvidenceStatus('Nearest observations require the backend service.');
  const o2 = payload.oxygen_pct, U = payload.flow_cm_s, mat = payload.material;
  const el = (id) => document.getElementById(id);
  const banner = el('envelope-alert-banner'), aTitle = el('alert-title'), aMsg = el('alert-message');
  const badge = el('regime-badge'), pill = el('confidence-pill');
  const briefing = el('operator-briefing-text'), expText = el('explanation-text-display');
  const tierPill = el('state-tier-pill'), tierLabel = el('state-tier-label'), tierExp = el('state-tier-explainer');

  // No probabilities exist for a deterministic boundary.
  ['val-prob-no-spread', 'val-prob-marginal', 'val-prob-spread'].forEach((id) => {
    const n = el(id); if (n) n.textContent = 'n/a';
  });
  ['bar-seg-no-spread', 'bar-seg-marginal', 'bar-seg-spread'].forEach((id) => {
    const n = el(id); if (n) n.style.width = '0%';
  });

  if (tierPill) {
    tierPill.className = 'state-tier-pill tier-physics';
    if (tierLabel) tierLabel.textContent = 'PUBLISHED NASA BOUNDARY';
    if (tierExp) tierExp.textContent = `${NASA_BOUNDARY.CITATION} · deterministic, not a trained model`;
  }

  // The fit is for cast-PMMA rods only. Say so rather than extrapolating it.
  if (mat !== 'PMMA') {
    if (banner) banner.classList.remove('hidden');
    if (aTitle) aTitle.textContent = 'OUTSIDE THE PUBLISHED BOUNDARY FIT';
    if (aMsg) aMsg.textContent = `${NASA_BOUNDARY.CITATION} was fitted to cast-PMMA rods. It is not validated for ${mat}, so no margin is reported here. Use the flight-archive view to see the real experiments for this material.`;
    if (badge) { badge.className = 'regime-status-badge regime-refusal'; badge.textContent = 'NO PUBLISHED BOUNDARY FOR THIS MATERIAL'; }
    if (pill) pill.textContent = 'NOT APPLICABLE';
    if (briefing) briefing.textContent = `The published NASA boundary covers cast-PMMA rods. For ${mat}, this tool can show you the real flight tests that exist but cannot place you against a validated limit.`;
    if (expText) expText.textContent = '';
    return;
  }

  // Equation 6.1 was fitted to cast-PMMA rod tests in the ISS glovebox at
  // nominal cabin pressure and 0–55 cm/s flow; it has no pressure term.
  if (Math.abs(payload.pressure_kpa - NASA_BOUNDARY.NOMINAL_PRESSURE_KPA) > 0.05 ||
      payload.flow_cm_s < NASA_BOUNDARY.VALID_FLOW[0] ||
      payload.flow_cm_s > NASA_BOUNDARY.VALID_FLOW[1] ||
      !Number.isFinite(payload.pressure_kpa) || !Number.isFinite(payload.flow_cm_s)) {
    if (banner) banner.classList.remove('hidden');
    if (aTitle) aTitle.textContent = 'OUTSIDE DOCUMENTED BOUNDARY CONDITIONS';
    if (aMsg) aMsg.textContent = `${NASA_BOUNDARY.CITATION} describes cast-PMMA rod tests at nominal ${NASA_BOUNDARY.NOMINAL_PRESSURE_KPA} kPa and ${NASA_BOUNDARY.VALID_FLOW[0]}–${NASA_BOUNDARY.VALID_FLOW[1]} cm/s flow. No margin is reported for this pressure or flow.`;
    if (badge) { badge.className = 'regime-status-badge regime-refusal'; badge.textContent = 'OUTSIDE PUBLISHED PRESSURE OR FLOW'; }
    if (pill) pill.textContent = 'NOT APPLICABLE';
    if (briefing) briefing.textContent = 'The published boundary has no validated pressure adjustment for these conditions, so the tool cannot report a boundary margin.';
    if (expText) expText.textContent = '';
    return;
  }

  const r = state.rod_radius_cm || NASA_BOUNDARY.R_O;
  const res = NASA_BOUNDARY.evaluate(o2, U, r);
  if (!res) return;

  if (!res.inFitRange) {
    if (banner) banner.classList.remove('hidden');
    if (aTitle) aTitle.textContent = 'OUTSIDE THE RANGE THE BOUNDARY WAS FITTED OVER';
    if (aMsg) aMsg.textContent = `${NASA_BOUNDARY.CITATION} was fitted over ${NASA_BOUNDARY.VALID_O2[0]} to ${NASA_BOUNDARY.VALID_O2[1]} % O2. At ${o2.toFixed(1)} %, no boundary margin is reported.`;
    if (badge) { badge.className = 'regime-status-badge regime-refusal'; badge.textContent = 'OUTSIDE PUBLISHED OXYGEN RANGE'; }
    if (pill) pill.textContent = 'NOT APPLICABLE';
    if (briefing) briefing.textContent = `The published cast-PMMA boundary covers ${NASA_BOUNDARY.VALID_O2[0]} to ${NASA_BOUNDARY.VALID_O2[1]} % O2. This scenario is outside that range, so the tool cannot report a boundary margin.`;
    if (expText) expText.textContent = '';
    return;
  }

  const m = res.margin, sign = m >= 0 ? '+' : '';
  const near = Math.abs(m) < 1.0;        // within 1 % O2 of the limit

  if (banner) {
    if (!near) banner.classList.add('hidden');
    else banner.classList.remove('hidden');
  }
  if (near && aTitle) {
    aTitle.textContent = 'WITHIN 1 % O2 OF THE PUBLISHED LIMIT';
    if (aMsg) aMsg.textContent = 'This condition sits close to the flammability boundary, where NASA\'s own data shows outcomes depend on ignition history. Treat it as undetermined rather than safe.';
  }

  if (badge) {
    badge.className = 'regime-status-badge ' + (near ? 'regime-marginal' : (res.flammable ? 'regime-spread' : 'regime-no-spread'));
    badge.textContent = near ? 'NEAR THE LIMIT — UNDETERMINED'
      : (res.flammable ? 'ABOVE THE FLAMMABILITY LIMIT' : 'BELOW THE FLAMMABILITY LIMIT');
  }
  if (pill) pill.textContent = `${sign}${m.toFixed(2)} % O2 vs limit`;

  if (briefing) {
    briefing.textContent = near
      ? `At ${o2.toFixed(1)} % O2 and ${U} cm/s the condition is ${Math.abs(m).toFixed(2)} percentage points from NASA's published limit of ${res.limitO2.toFixed(2)} % O2. That is inside the band where the flight data itself is inconsistent, so this is not a safety clearance.`
      : (res.flammable
        ? `At ${o2.toFixed(1)} % O2 and ${U} cm/s, a flame on cast PMMA is ${m.toFixed(2)} percentage points of oxygen ABOVE NASA's published limit of ${res.limitO2.toFixed(2)} %. Reducing oxygen by ${m.toFixed(2)} points would reach the boundary.`
        : `At ${o2.toFixed(1)} % O2 and ${U} cm/s, the condition is ${Math.abs(m).toFixed(2)} points BELOW NASA's published limit of ${res.limitO2.toFixed(2)} %, so an established flame would be expected to extinguish. This says nothing about whether an ignition source could start one.`);
  }
  if (expText) {
    expText.innerHTML = `Stretch rate a = ${res.stretch.toFixed(1)} s<sup>-1</sup> for a ${(r * 2 * 10).toFixed(2)} mm diameter rod, placing this in the <strong>${escapeHTML(res.regime)}</strong> regime (separator U/U<sub>D</sub> = 1, U<sub>D</sub> = ${NASA_BOUNDARY.U_D} cm/s). The limit comes from <a href="${escapeHTML(safeHttpUrl(res.url, NASA_BOUNDARY.URL))}" target="_blank" rel="noopener noreferrer" class="citation-ntrs-link">${escapeHTML(res.citation)} ↗</a>, fitted by NASA to cast-PMMA rods. It describes extinction of an <em>established</em> flame and does not predict ignition.`;
  }
}

function renderOfflineUnavailable(payload, err) {
  const alertBanner = document.getElementById('envelope-alert-banner');
  const alertTitle = document.getElementById('alert-title');
  const alertMsg = document.getElementById('alert-message');
  const badge = document.getElementById('regime-badge');
  const confPill = document.getElementById('confidence-pill');
  const briefing = document.getElementById('operator-briefing-text');
  const expText = document.getElementById('explanation-text-display');

  const stateTierPill = document.getElementById('state-tier-pill');
  const stateTierLabel = document.getElementById('state-tier-label');
  const stateTierExplainer = document.getElementById('state-tier-explainer');

  if (stateTierPill) {
    stateTierPill.className = 'state-tier-pill tier-offline';
    if (stateTierLabel) stateTierLabel.textContent = 'SERVICE OFFLINE';
    if (stateTierExplainer) stateTierExplainer.textContent = 'Backend Service Unavailable · Simulation Disabled for Scientific Integrity';
  }

  if (alertBanner) alertBanner.classList.remove('hidden');
  if (alertTitle) alertTitle.textContent = 'BACKEND INFERENCE SERVICE UNAVAILABLE';
  if (alertMsg) {
    alertMsg.textContent = `The FLARE-X FastAPI backend is currently unreachable at ${API_BASE}. To run live predictions and nearest flight experiment retrieval, launch the backend using 'bash scripts/run_local.sh' or 'uvicorn src.api.main:app'. In strict accordance with NASA scientific standards, simulated prediction fallbacks are disabled to prevent presenting unverified numbers as research data.`;
  }

  if (badge) {
    badge.className = 'regime-status-badge regime-refusal';
    badge.textContent = 'SERVER OFFLINE · NO SIMULATION';
  }
  if (confPill) confPill.textContent = 'INFERENCE OFFLINE';

  const pNoSpread = document.getElementById('val-prob-no-spread');
  const pMarginal = document.getElementById('val-prob-marginal');
  const pSpread = document.getElementById('val-prob-spread');
  const bNoSpread = document.getElementById('bar-seg-no-spread');
  const bMarginal = document.getElementById('bar-seg-marginal');
  const bSpread = document.getElementById('bar-seg-spread');

  if (pNoSpread) pNoSpread.textContent = '—';
  if (pMarginal) pMarginal.textContent = '—';
  if (pSpread) pSpread.textContent = '—';
  if (bNoSpread) bNoSpread.style.width = '0%';
  if (bMarginal) bMarginal.style.width = '0%';
  if (bSpread) bSpread.style.width = '0%';

  if (briefing) {
    briefing.textContent = `OFFLINE NOTICE: Live model inference is paused while the backend service is offline. To prevent misleading scientific conclusions, FLARE-X does not generate hardcoded synthetic probabilities or fictional flight records.`;
  }
  if (expText) {
    expText.textContent = `Backend connection error: ${err.message}. Start the Python service to enable live ML inference.`;
  }

  const container = document.getElementById('nearest-cards-list');
  if (container) {
    container.innerHTML = '<p class="module-explainer" style="color: var(--text-muted); padding: 12px;">Real-time nearest-neighbor retrieval offline. Connect backend to inspect NASA flight experiments.</p>';
  }
}

// Render Nearest Experiments Cards with Provenance Tracing
function renderNearestExperiments(experiments) {
  const container = document.getElementById('nearest-cards-list');
  if (!container) return;
  container.innerHTML = '';

  if (experiments.length === 0) {
    container.innerHTML = '<p class="module-explainer">No matching experiments found.</p>';
    return;
  }

  experiments.forEach(exp => {
    const item = document.createElement('div');
    item.className = 'flight-obs-card';

    const dist = exp.distance !== undefined ? `d = ${exp.distance.toFixed(3)}` : 'Exact match';
    const outcomeClass = exp.outcome === 'spread' ? 'badge-spread' : (exp.outcome === 'marginal_spread' ? 'badge-marginal' : 'badge-no-spread');
    const reportUrl = safeHttpUrl(exp.source_url || `https://ntrs.nasa.gov/citations/${encodeURIComponent(exp.report_id || '')}`, 'https://ntrs.nasa.gov/');
    const eid = exp.experiment_id || 'EXP_OBS';

    item.innerHTML = `
      <div class="obs-top-line">
        <span class="obs-id">${escapeHTML(eid)} · ${escapeHTML(exp.material)}</span>
        <span class="obs-distance">${escapeHTML(dist)}</span>
      </div>
      <div class="obs-conditions">
        ${escapeHTML(exp.oxygen_pct)}% O₂ · ${escapeHTML(exp.pressure_kpa)} kPa · ${escapeHTML(exp.flow_cm_s)} cm/s
      </div>
      <div class="obs-bottom-line">
        <span class="badge-outcome ${outcomeClass}">${escapeHTML(exp.outcome || 'observed')}</span>
        <div class="obs-actions" style="display: flex; gap: 8px; align-items: center;">
          <button type="button" class="btn-trace-cite" title="Inspect full provenance and NTRS citation">
            Trace Citation ↗
          </button>
          <a href="${reportUrl}" target="_blank" rel="noopener noreferrer" class="citation-ntrs-link">
            NTRS ${escapeHTML(exp.report_id || 'Report')}
          </a>
        </div>
      </div>
    `;
    item.querySelector('.btn-trace-cite').addEventListener('click', () => window.inspectProvenance(eid));
    container.appendChild(item);
  });
}


// Fetch 2-D Boundary Slice
let boundaryGeneration = 0;
async function fetchBoundarySlice() {
  const generation = ++boundaryGeneration;
  const material = state.material;
  const pressure = state.pressure_kpa;
  const isCurrent = () => generation === boundaryGeneration &&
    material === state.material && pressure === state.pressure_kpa;
  const caption = document.getElementById('canvas-slice-caption');
  if (caption) {
    caption.textContent = `Fixed slice at Pressure = ${pressure.toFixed(1)} kPa, Material = ${material}`;
  }
  state.boundaryData = null;
  drawOfflineCanvas('Loading boundary for selected conditions…');

  try {
    const url = `${API_BASE}/boundary?material=${encodeURIComponent(material)}&pressure_kpa=${pressure}&o2_steps=28&flow_steps=28`;
    const res = await fetch(url);
    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.detail || `HTTP error ${res.status}`);
    }
    const data = await res.json();
    if (!isCurrent()) return;
    state.boundaryData = data;
    drawBoundaryCanvas();
  } catch (err) {
    if (!isCurrent()) return;
    console.warn('Boundary slice fetch failed:', err);
    state.boundaryData = null;
    drawOfflineCanvas(err.message);
  }
}

function drawOfflineCanvas(message = 'Decision boundary unavailable. Check the backend connection.') {
  const canvas = document.getElementById('flammability-boundary-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#f8fafc';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#64748b';
  ctx.font = '13px monospace';
  ctx.textAlign = 'center';
  ctx.fillText(message, canvas.width / 2, canvas.height / 2);
}

// Draw 2-D Flammability Map on HTML5 Canvas
function drawBoundaryCanvas() {
  const canvas = document.getElementById('flammability-boundary-canvas');
  if (!canvas || !state.boundaryData) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;

  ctx.clearRect(0, 0, w, h);
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, w, h);

  const padLeft = 70;
  const padBottom = 45;
  const padRight = 35;
  const padTop = 35;
  const plotW = w - padLeft - padRight;
  const plotH = h - padTop - padBottom;

  const b = state.boundaryData;
  const o2Min = b.oxygen_range[0];
  const o2Max = b.oxygen_range[1];
  const flowMin = b.flow_range[0];
  const flowMax = b.flow_range[1];

  function toX(o2) {
    return padLeft + ((o2 - o2Min) / (o2Max - o2Min)) * plotW;
  }
  function toY(flow) {
    return padTop + plotH - ((flow - flowMin) / (flowMax - flowMin)) * plotH;
  }

  // 1. Draw Grid Cells Shaded by Predicted Regime (Light Theme Inks)
  const o2Grid = b.oxygen_grid;
  const flowGrid = b.flow_grid;
  const cellW = plotW / (o2Grid.length - 1);
  const cellH = plotH / (flowGrid.length - 1);

  for (let j = 0; j < flowGrid.length; j++) {
    for (let i = 0; i < o2Grid.length; i++) {
      const pred = b.grid_predictions[j][i];
      if (!pred) {
        ctx.fillStyle = 'rgba(203, 213, 225, 0.25)';
      } else if (pred === 'spread') {
        ctx.fillStyle = 'rgba(239, 68, 68, 0.16)';
      } else if (pred === 'marginal_spread') {
        ctx.fillStyle = 'rgba(245, 158, 11, 0.16)';
      } else {
        ctx.fillStyle = 'rgba(16, 185, 129, 0.16)';
      }

      const cx = toX(o2Grid[i]) - cellW / 2;
      const cy = toY(flowGrid[j]) - cellH / 2;
      ctx.fillRect(Math.max(padLeft, cx), Math.max(padTop, cy), cellW, cellH);
    }
  }

  // 2. Draw Scientific Axes & Precision Grid Lines
  ctx.strokeStyle = 'rgba(0, 0, 0, 0.06)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  // X grid
  for (let o2 = Math.ceil(o2Min); o2 <= o2Max; o2 += 3) {
    const x = toX(o2);
    ctx.moveTo(x, padTop);
    ctx.lineTo(x, padTop + plotH);
  }
  // Y grid
  for (let f = Math.ceil(flowMin); f <= flowMax; f += 5) {
    const y = toY(f);
    ctx.moveTo(padLeft, y);
    ctx.lineTo(padLeft + plotW, y);
  }
  ctx.stroke();

  // Outer Plot Border
  ctx.strokeStyle = '#cbd5e1';
  ctx.lineWidth = 1;
  ctx.strokeRect(padLeft, padTop, plotW, plotH);

  // 3. Draw Axis Labels & Numbers
  ctx.fillStyle = '#475569';
  ctx.font = '11px "JetBrains Mono", monospace';
  ctx.textAlign = 'center';
  for (let o2 = Math.ceil(o2Min); o2 <= o2Max; o2 += 3) {
    ctx.fillText(`${o2}%`, toX(o2), padTop + plotH + 20);
  }
  ctx.font = '12px "Inter", sans-serif';
  ctx.fillStyle = '#1e293b';
  ctx.fillText('Oxygen Concentration, X_O₂ (% by volume)', padLeft + plotW / 2, h - 8);

  ctx.font = '11px "JetBrains Mono", monospace';
  ctx.fillStyle = '#475569';
  ctx.textAlign = 'right';
  for (let f = Math.ceil(flowMin); f <= flowMax; f += 5) {
    ctx.fillText(`${f}`, padLeft - 10, toY(f) + 4);
  }
  ctx.save();
  ctx.translate(18, padTop + plotH / 2);
  ctx.rotate(-Math.PI / 2);
  ctx.font = '12px "Inter", sans-serif';
  ctx.fillStyle = '#1e293b';
  ctx.textAlign = 'center';
  ctx.fillText('Forced Ventilation Velocity, v_g (cm/s)', 0, 0);
  ctx.restore();

  // 4. Overlaid Real Historical NASA Experiments (Scatter Dots)
  (b.real_experiments || []).forEach(exp => {
    if (exp.oxygen_pct < o2Min || exp.oxygen_pct > o2Max || exp.flow_cm_s < flowMin || exp.flow_cm_s > flowMax) {
      return;
    }
    const ex = toX(exp.oxygen_pct);
    const ey = toY(exp.flow_cm_s);

    ctx.beginPath();
    ctx.arc(ex, ey, 4.5, 0, Math.PI * 2);
    if (exp.outcome === 'spread') {
      ctx.fillStyle = '#dc2626';
    } else if (exp.outcome === 'marginal_spread') {
      ctx.fillStyle = '#d97706';
    } else {
      ctx.fillStyle = '#059669';
    }
    ctx.fill();
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 1.5;
    ctx.stroke();
  });

  // 5. Active User Query Reticle with Animated Radar Halo Ring
  if (state.oxygen_pct >= o2Min && state.oxygen_pct <= o2Max && state.flow_cm_s >= flowMin && state.flow_cm_s <= flowMax) {
    const qx = toX(state.oxygen_pct);
    const qy = toY(state.flow_cm_s);

    const now = performance.now();
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const pulseFactor = reducedMotion ? 0 : Math.sin(now * 0.0035);
    const ringRadius = 8.5 + (reducedMotion ? 0 : 4 * (0.5 + 0.5 * pulseFactor));
    const ringAlpha = reducedMotion ? 0.6 : (0.25 + 0.35 * (0.5 + 0.5 * pulseFactor));

    // Outer Precision Radar Halo
    ctx.beginPath();
    ctx.arc(qx, qy, ringRadius, 0, Math.PI * 2);
    ctx.strokeStyle = `rgba(29, 78, 216, ${ringAlpha})`;
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // Solid Target Ring
    ctx.beginPath();
    ctx.arc(qx, qy, 7, 0, Math.PI * 2);
    ctx.strokeStyle = '#1d4ed8';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Center Core Dot
    ctx.beginPath();
    ctx.arc(qx, qy, 2, 0, Math.PI * 2);
    ctx.fillStyle = '#ffffff';
    ctx.fill();
    ctx.strokeStyle = '#1d4ed8';
    ctx.lineWidth = 1;
    ctx.stroke();

    // Crosshairs
    ctx.strokeStyle = 'rgba(29, 78, 216, 0.65)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(qx - 14, qy);
    ctx.lineTo(qx + 14, qy);
    ctx.moveTo(qx, qy - 14);
    ctx.lineTo(qx, qy + 14);
    ctx.stroke();

    // Coordinate tag box
    ctx.fillStyle = 'rgba(255, 255, 255, 0.96)';
    ctx.strokeStyle = '#1d4ed8';
    ctx.lineWidth = 1;
    const tagText = `${state.oxygen_pct.toFixed(1)}% · ${state.flow_cm_s.toFixed(1)} cm/s`;
    ctx.font = '10px "JetBrains Mono", monospace';
    const tagW = ctx.measureText(tagText).width + 10;
    const tagX = Math.min(qx + 10, padLeft + plotW - tagW);
    const tagY = Math.max(qy - 20, padTop + 2);
    ctx.fillRect(tagX, tagY, tagW, 18);
    ctx.strokeRect(tagX, tagY, tagW, 18);
    ctx.fillStyle = '#0f172a';
    ctx.textAlign = 'left';
    ctx.fillText(tagText, tagX + 5, tagY + 13);
  }
}

// Scenario Command Search Parser
function setupNlpParser() {
  const btn = document.getElementById('nlp-query-submit');
  const input = document.getElementById('nlp-query-input');
  if (!btn || !input) return;

  btn.addEventListener('click', async () => {
    const text = input.value.trim();
    if (!text) return;

    try {
      const res = await fetch(`${API_BASE}/scenario/parse`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: text })
      });
      const data = await res.json();
      const feedbackEl = document.getElementById('nlp-feedback');
      if (data.is_valid && data.parsed_scenario) {
        if (feedbackEl) feedbackEl.style.display = 'none';
        const sc = data.parsed_scenario;
        updateInputs(sc.oxygen_pct, sc.pressure_kpa, sc.flow_cm_s, sc.material);
      } else {
        const msg = 'Could not parse scenario: ' + (data.ambiguities || []).join('; ');
        if (feedbackEl) {
          feedbackEl.textContent = msg;
          feedbackEl.style.display = 'block';
        } else {
          console.warn(msg);
        }
      }
    } catch (err) {
      console.warn('NLP parser error:', err);
    }
  });

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') btn.click();
  });
}

// Killer Demo Sweep View (Brief §2) - Completely Dynamic
let sweepGeneration = 0;
let sweepRefreshTimeout = null;
function scheduleSweepRefresh() {
  ++sweepGeneration;
  clearTimeout(sweepRefreshTimeout);
  setSweepUnavailable('Loading sweep for selected conditions…');
  sweepRefreshTimeout = setTimeout(fetchSweepData, 150);
}

function setSweepUnavailable(message) {
  if (state.sweepInterval != null) {
    clearInterval(state.sweepInterval);
    state.sweepInterval = null;
  }
  state.sweepRunning = false;
  state.sweepData = null;
  state.dynamicLocBoundary = null;
  state.sweepEvidenceBefore = null;
  state.sweepEvidenceAfter = null;
  state.sweepError = message;
  const slider = document.getElementById('sweep-oxygen-slider');
  const autoBtn = document.getElementById('btn-run-auto-sweep');
  if (slider) slider.disabled = true;
  if (autoBtn) autoBtn.disabled = true;
  if (autoBtn) autoBtn.textContent = '▶ Play Automated Oxygen Sweep';
  updateSweepPoint(parseFloat(slider ? slider.value : 21.0));
}

async function fetchSweepData() {
  const generation = ++sweepGeneration;
  const scenario = {
    oxygen_pct: state.oxygen_pct,
    pressure_kpa: state.pressure_kpa,
    flow_cm_s: state.flow_cm_s,
    material: state.material
  };
  const isCurrent = () => generation === sweepGeneration &&
    scenario.oxygen_pct === state.oxygen_pct &&
    scenario.pressure_kpa === state.pressure_kpa &&
    scenario.flow_cm_s === state.flow_cm_s &&
    scenario.material === state.material;
  setSweepUnavailable('Loading validated sweep data…');
  try {
    const res = await fetch(`${API_BASE}/sweep`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        baseline: scenario,
        param: 'oxygen_pct',
        start: 16.0,
        end: 21.0,
        steps: 26
      })
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.detail || `HTTP error ${res.status}`);
    }
    const sweepData = await res.json();
    if (!isCurrent()) return;
    const trans = sweepData.transitions;
    if (!sweepData.points || !trans || trans.length === 0) {
      setSweepUnavailable('No validated regime transition is available for this sweep.');
      return;
    }
    state.sweepData = sweepData;
    state.sweepError = null;
    const slider = document.getElementById('sweep-oxygen-slider');
    const autoBtn = document.getElementById('btn-run-auto-sweep');
    if (slider) slider.disabled = false;
    if (autoBtn) autoBtn.disabled = false;
        const t = trans.find(tr => tr.to_regime === 'spread' || tr.to_regime === 'marginal_spread') || trans[0];
        state.dynamicLocBoundary = t.midpoint;
        state.sweepEvidenceBefore = t.evidence_before;
        state.sweepEvidenceAfter = t.evidence_after;
    updateSweepPoint(parseFloat(slider ? slider.value : 21.0));
  } catch (err) {
    if (!isCurrent()) return;
    console.warn('Dynamic sweep fetch error:', err);
    setSweepUnavailable(err.message);
  }
}

function setupSweepView() {
  const sweepSlider = document.getElementById('sweep-oxygen-slider');
  const autoBtn = document.getElementById('btn-run-auto-sweep');
  if (!sweepSlider || !autoBtn) return;

  sweepSlider.addEventListener('input', (e) => {
    updateSweepPoint(parseFloat(e.target.value));
  });

  autoBtn.addEventListener('click', () => {
    if (state.sweepRunning || !state.sweepData) return;
    state.sweepRunning = true;
    autoBtn.textContent = '⏳ SWEEPING OXYGEN...';
    let val = 21.0;
    state.sweepInterval = setInterval(() => {
      if (!state.sweepRunning) return;
      val = Math.max(16.0, Math.round((val - 0.1) * 10) / 10);
      sweepSlider.value = val.toFixed(1);
      updateSweepPoint(val);
      if (val <= 16.0) {
        clearInterval(state.sweepInterval);
        state.sweepInterval = null;
        state.sweepRunning = false;
        autoBtn.textContent = '▶ Play Automated Oxygen Sweep';
      }
    }, 60);
  });

  fetchSweepData();
}

function updateSweepPoint(o2Val) {
  const marginDisplay = document.getElementById('safety-margin-val');
  const marginStatus = document.getElementById('safety-margin-status');
  const readout = document.getElementById('readout-sweep-o2');
  if (readout) readout.textContent = `${o2Val.toFixed(1)} %`;

  if (!state.sweepData || state.dynamicLocBoundary == null) {
    if (marginDisplay) marginDisplay.textContent = 'N/A';
    if (marginStatus) marginStatus.textContent = state.sweepError || 'Validated sweep unavailable';
    for (const id of ['tag-above-boundary', 'tag-below-boundary', 'tick-loc-boundary', 'evidence-above-boundary', 'evidence-below-boundary']) {
      const el = document.getElementById(id);
      if (el) el.textContent = 'Validated sweep unavailable';
    }
    drawSweepCanvas(o2Val);
    return;
  }

  const locBoundary = state.dynamicLocBoundary;
  const delta = o2Val - locBoundary;
  const sampledPoint = (state.sweepData.points || []).find((point) =>
    Math.abs(point.oxygen_pct - o2Val) < 0.0005);
  const hasEstimate = sampledPoint && sampledPoint.prediction != null;
  if (marginDisplay) marginDisplay.textContent = hasEstimate
    ? `${delta >= 0 ? '+' : ''}${delta.toFixed(2)} % O₂` : 'N/A';

  // Update dynamic boundary tags in UI
  const tagAbove = document.getElementById('tag-above-boundary');
  const tagBelow = document.getElementById('tag-below-boundary');
  const tickLoc = document.getElementById('tick-loc-boundary');
  if (tagAbove) tagAbove.textContent = `Higher-O₂ side of model transition`;
  if (tagBelow) tagBelow.textContent = `Lower-O₂ side of model transition`;
  if (tickLoc) tickLoc.textContent = `${locBoundary.toFixed(1)}% O₂ (model transition)`;

  if (marginStatus) {
    marginStatus.className = 'margin-pill';
    marginStatus.removeAttribute('style');
    marginStatus.textContent = hasEstimate
      ? `Model estimate: ${sampledPoint.prediction.replaceAll('_', ' ')}`
      : 'No model estimate at this point';
  }

  // Update real historical evidence boxes from dynamic sweep results
  const evAbove = document.getElementById('evidence-above-boundary');
  const evBelow = document.getElementById('evidence-below-boundary');
  if (evAbove) {
    const exp = (state.sweepEvidenceAfter && state.sweepEvidenceAfter[0]);
    if (exp) {
      evAbove.innerHTML = `<strong>Real NASA ${escapeHTML(exp.investigation || 'Flight')} Test:</strong> ${escapeHTML(exp.oxygen_pct)}% O₂, ${escapeHTML(exp.pressure_kpa)} kPa, ${escapeHTML(exp.flow_cm_s)} cm/s → <em>${escapeHTML(exp.outcome)}</em> (<a href="${escapeHTML(safeHttpUrl(exp.source_url, '#'))}" target="_blank" rel="noopener noreferrer" class="citation-ntrs-link">NTRS ${escapeHTML(exp.report_id)} ↗</a>, ${escapeHTML(state.material)})`;
    } else {
      evAbove.textContent = 'No cited experiment is available on this side of the model transition.';
    }
  }
  if (evBelow) {
    const exp = (state.sweepEvidenceBefore && state.sweepEvidenceBefore[0]);
    if (exp) {
      evBelow.innerHTML = `<strong>Real NASA ${escapeHTML(exp.investigation || 'Flight')} Test:</strong> ${escapeHTML(exp.oxygen_pct)}% O₂, ${escapeHTML(exp.pressure_kpa)} kPa, ${escapeHTML(exp.flow_cm_s)} cm/s → <em>${escapeHTML(exp.outcome)}</em> (<a href="${escapeHTML(safeHttpUrl(exp.source_url, '#'))}" target="_blank" rel="noopener noreferrer" class="citation-ntrs-link">NTRS ${escapeHTML(exp.report_id)} ↗</a>, ${escapeHTML(state.material)})`;
    } else {
      evBelow.textContent = 'No cited experiment is available on this side of the model transition.';
    }
  }

  drawSweepCanvas(o2Val);
}

// Draw Probability vs O2 Curve Canvas
function drawSweepCanvas(currentO2 = 21.0) {
  const canvas = document.getElementById('sweep-chart-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;

  ctx.clearRect(0, 0, w, h);
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, w, h);

  if (!state.sweepData || state.dynamicLocBoundary == null) {
    ctx.fillStyle = '#64748b';
    ctx.font = '13px monospace';
    ctx.textAlign = 'center';
    ctx.fillText(state.sweepError || 'Validated sweep unavailable', w / 2, h / 2);
    return;
  }

  const padLeft = 70;
  const padBottom = 40;
  const padTop = 30;
  const padRight = 40;
  const pW = w - padLeft - padRight;
  const pH = h - padTop - padBottom;

  // Grid
  ctx.strokeStyle = 'rgba(0, 0, 0, 0.06)';
  ctx.strokeRect(padLeft, padTop, pW, pH);

  // Transition vertical line derived dynamically
  const locBoundary = state.dynamicLocBoundary;
  const boundaryX = padLeft + ((locBoundary - 16.0) / (21.0 - 16.0)) * pW;
  ctx.strokeStyle = 'rgba(217, 119, 6, 0.75)';
  ctx.setLineDash([4, 4]);
  ctx.beginPath();
  ctx.moveTo(boundaryX, padTop);
  ctx.lineTo(boundaryX, padTop + pH);
  ctx.stroke();
  ctx.setLineDash([]);

  ctx.fillStyle = '#b45309';
  ctx.font = '10px "JetBrains Mono", monospace';
  ctx.fillText(`MODEL TRANSITION (${locBoundary.toFixed(1)}%)`, Math.min(boundaryX + 8, padLeft + pW - 180), padTop + 16);

  // Check if we have real sweep points from the backend
  const pts = state.sweepData.points;

  // Refused points leave a gap; they must not be plotted as zero probability.
  const drawProbabilityCurve = (key, color) => {
    ctx.strokeStyle = color;
    ctx.lineWidth = 2.4;
    ctx.beginPath();
    let drawing = false;
    pts.forEach((pt) => {
      const prob = pt.probabilities?.[key];
      if (typeof prob !== 'number' || !Number.isFinite(prob)) {
        drawing = false;
        return;
      }
      const x = padLeft + ((pt.oxygen_pct - 16.0) / (21.0 - 16.0)) * pW;
      const y = padTop + pH - prob * pH;
      if (drawing) ctx.lineTo(x, y);
      else ctx.moveTo(x, y);
      drawing = true;
    });
    ctx.stroke();
  };
  drawProbabilityCurve('spread', '#dc2626');
  drawProbabilityCurve('no_spread', '#059669');

  // Current slider marker
  const curX = padLeft + ((currentO2 - 16.0) / (21.0 - 16.0)) * pW;
  ctx.strokeStyle = '#1e293b';
  ctx.lineWidth = 1.8;
  ctx.beginPath();
  ctx.moveTo(curX, padTop);
  ctx.lineTo(curX, padTop + pH);
  ctx.stroke();

  ctx.beginPath();
  ctx.arc(curX, padTop + pH / 2, 5, 0, Math.PI * 2);
  ctx.fillStyle = currentO2 >= locBoundary ? 'rgba(220, 38, 38, 0.25)' : 'rgba(5, 150, 105, 0.25)';
  ctx.fill();
  ctx.beginPath();
  ctx.arc(curX, padTop + pH / 2, 2.5, 0, Math.PI * 2);
  ctx.fillStyle = '#1d4ed8';
  ctx.fill();

  // Labels
  ctx.fillStyle = '#475569';
  ctx.font = '11px "JetBrains Mono", monospace';
  ctx.textAlign = 'center';
  for (let o2 = 16; o2 <= 21; o2++) {
    const x = padLeft + ((o2 - 16.0) / 5.0) * pW;
    ctx.fillText(`${o2}% O₂`, x, padTop + pH + 20);
  }
}

// Atlas Table Setup & Data Loading
async function setupAtlasView() {
  const searchInput = document.getElementById('atlas-search-input');
  const matFilter = document.getElementById('atlas-filter-material');
  const outFilter = document.getElementById('atlas-filter-outcome');
  if (!searchInput || !matFilter || !outFilter) return;

  try {
    const res = await fetch(`${API_BASE}/experiments?limit=200`);
    if (res.ok) {
      const data = await res.json();
      state.experiments = data.experiments;
      renderAtlasTable(state.experiments);
    }
  } catch (err) {
    console.warn('Could not load experiments from API:', err);
  }

  function applyFilters() {
    const q = searchInput.value.toLowerCase();
    const mat = matFilter.value;
    const out = outFilter.value;

    const filtered = state.experiments.filter(exp => {
      const matchQ = !q || JSON.stringify(exp).toLowerCase().includes(q);
      const matchMat = !mat || exp.material === mat;
      const matchOut = !out || exp.outcome === out;
      return matchQ && matchMat && matchOut;
    });
    renderAtlasTable(filtered);
  }

  searchInput.addEventListener('input', applyFilters);
  matFilter.addEventListener('change', applyFilters);
  outFilter.addEventListener('change', applyFilters);
}

function renderAtlasTable(rows) {
  const tbody = document.getElementById('atlas-table-body');
  if (!tbody) return;
  tbody.innerHTML = '';

  rows.slice(0, 100).forEach(r => {
    const tr = document.createElement('tr');
    const badgeClass = r.outcome === 'spread' ? 'badge-spread' : (r.outcome === 'marginal_spread' ? 'badge-marginal' : 'badge-no-spread');
    const citeUrl = r.source_url || `https://ntrs.nasa.gov/citations/${r.report_id}`;

    tr.innerHTML = `
      <td><strong>${escapeHTML(r.experiment_id)}</strong></td>
      <td>${escapeHTML(r.investigation)}</td>
      <td>${escapeHTML(r.material)}</td>
      <td>${escapeHTML(r.oxygen_pct)}%</td>
      <td>${escapeHTML(r.pressure_kpa)} kPa</td>
      <td>${escapeHTML(r.flow_cm_s)} cm/s</td>
      <td><span class="badge-outcome ${badgeClass}">${escapeHTML(r.outcome)}</span></td>
      <td>${escapeHTML(r.report_id)}</td>
      <td><a href="${escapeHTML(safeHttpUrl(citeUrl, 'https://ntrs.nasa.gov/'))}" target="_blank" rel="noopener noreferrer" class="citation-ntrs-link">NTRS ↗</a></td>
    `;

    // Click row to probe into Flammability Deck
    tr.addEventListener('click', (e) => {
      if (e.target.closest('a')) return;
      document.getElementById('tab-lab-btn').click();
      updateInputs(r.oxygen_pct, r.pressure_kpa, r.flow_cm_s, r.material);
    });

    tbody.appendChild(tr);
  });
}

// Transparency & Investigations Loading
async function loadModelStatus() {
  const setText = (id, value) => {
    const element = document.getElementById(id);
    if (element) element.textContent = value;
  };

  try {
    const [modelResponse, healthResponse] = await Promise.all([
      fetch(`${API_BASE}/model`),
      fetch(`${API_BASE}/health`)
    ]);
    if (!modelResponse.ok || !healthResponse.ok) throw new Error('Model metadata unavailable');
    const [meta, health] = await Promise.all([modelResponse.json(), healthResponse.json()]);
    const percent = value => `${(value * 100).toFixed(1)}%`;

    state.materialCounts = Object.fromEntries(
      Object.entries(meta.training_range?.per_material || {}).map(([material, details]) => [material, details.n_samples])
    );
    updateMaterialInfo();

    setText('nav-experiment-count', String(meta.n_train));
    setText('chip-n-train', `${meta.n_train} observations`);
    setText('chip-cv-acc', percent(meta.cv_accuracy));
    setText('chip-base-acc', percent(meta.majority_baseline_accuracy));
    setText('model-kpi-accuracy', percent(meta.cv_accuracy));
    setText('model-kpi-baseline', percent(meta.majority_baseline_accuracy));
    setText('model-kpi-balanced', percent(meta.cv_balanced_accuracy));
    setText('model-kpi-samples', String(meta.n_train));
    setText('dataset-sha', meta.dataset_sha256
      ? `${meta.dataset_sha256.slice(0, 8)}…${meta.dataset_sha256.slice(-8)}`
      : 'Unavailable');
    setText('model-kpi-comparison', health.model_readiness_reason || 'Model readiness unavailable');
    setText('integrity-text', health.model_ready
      ? 'Grouped baseline gate passed; source citations and experimental limits still apply.'
      : health.model_readiness_reason || 'Model inference is withheld.');
    setText('status-text', `${meta.n_train} observations · ${health.model_ready ? 'Research model available' : 'Model inference withheld'}`);

    const body = document.getElementById('model-confusion-body');
    if (body && Array.isArray(meta.confusion_matrix) && Array.isArray(meta.classes)) {
      body.replaceChildren();
      meta.classes.forEach((label, index) => {
        const counts = meta.confusion_matrix[index] || [];
        const row = document.createElement('tr');
        const cells = [
          `${label} (${counts.reduce((sum, value) => sum + value, 0)})`,
          ...counts.map(String),
          percent(meta.per_class_recall?.[label] || 0)
        ];
        cells.forEach(value => {
          const cell = document.createElement('td');
          cell.textContent = value;
          row.appendChild(cell);
        });
        body.appendChild(row);
      });
    }
  } catch (error) {
    setText('status-text', 'Backend unavailable · published PMMA boundary only');
  }
}

async function loadDatasetsAndModel() {
  try {
    const res = await fetch(`${API_BASE}/datasets`);
    if (res.ok) {
      const data = await res.json();
      const container = document.getElementById('investigation-cards-list');
      if (container) {
        container.innerHTML = '';
        data.investigations.slice(0, 10).forEach(inv => {
          const div = document.createElement('div');
          div.className = 'investigation-card';
          div.innerHTML = `
            <div class="inv-title">${escapeHTML(inv.exact_nasa_title || inv.investigation_key || 'NASA Investigation')}</div>
            <div class="inv-meta">
              PSI ID: <strong>${escapeHTML(inv.psi_id || 'N/A')}</strong> · Role: <strong>${inv.usable_for_prototype_model === 'YES' ? 'Core Training Set' : 'Reference Catalog'}</strong>
            </div>
            <div class="inv-desc">${escapeHTML(inv.experiment_objective || inv.description || 'Microgravity combustion flight experiment.')}</div>
          `;
          container.appendChild(div);
        });
      }
    }
  } catch (err) {
    console.warn('Could not load datasets catalog:', err);
  }
}

// ==============================================================================
// FLARE-X EVIDENCE ATLAS: CONFLICT EXPLORER MODULE
// ==============================================================================

const CANONICAL_CASES_MAP = {
  'bass2_vs_saffire': { study_a: 'BASS-II', study_b: 'Saffire' },
  'drop_tower_vs_bass2': { study_a: 'Drop_Tower_Olson', study_b: 'BASS-II' },
  'normobaric_vs_exploration': { study_a: 'BASS-II', study_b: 'Exploration_Atmospheres' },
  'sofie_vs_drop_tower': { study_a: 'SoFIE_MIST', study_b: 'Drop_Tower_Olson' }
};

function setupConflictExplorer() {
  const caseSelect = document.getElementById('select-conflict-case');
  const btnLoadCase = document.getElementById('btn-load-case');
  const selectStudyA = document.getElementById('select-study-a');
  const selectStudyB = document.getElementById('select-study-b');
  const btnCompare = document.getElementById('btn-compare-studies');

  if (btnLoadCase) {
    btnLoadCase.addEventListener('click', () => {
      const caseId = caseSelect.value;
      const pair = CANONICAL_CASES_MAP[caseId];
      if (pair) {
        if (selectStudyA) selectStudyA.value = pair.study_a;
        if (selectStudyB) selectStudyB.value = pair.study_b;
        executeConflictAnalysis(pair.study_a, pair.study_b);
      }
    });
  }

  if (btnCompare) {
    btnCompare.addEventListener('click', () => {
      const a = selectStudyA ? selectStudyA.value : 'BASS-II';
      const b = selectStudyB ? selectStudyB.value : 'Saffire';
      executeConflictAnalysis(a, b);
    });
  }

  // Populate profiles on initial load
  loadConflictProfiles();
}

async function loadConflictProfiles() {
  try {
    const res = await fetch(`${API_BASE}/api/conflict/profiles`);
    if (!res.ok) return;
    const data = await res.json();
    const selectA = document.getElementById('select-study-a');
    const selectB = document.getElementById('select-study-b');

    if (selectA && selectB) {
      selectA.innerHTML = '';
      selectB.innerHTML = '';
      Object.keys(data.profiles || {}).forEach(k => {
        const prof = data.profiles[k];
        const optA = document.createElement('option');
        optA.value = k;
        optA.textContent = prof.title;
        selectA.appendChild(optA);

        const optB = document.createElement('option');
        optB.value = k;
        optB.textContent = prof.title;
        selectB.appendChild(optB);
      });
      selectA.value = 'BASS-II';
      selectB.value = 'Saffire';
    }
  } catch (err) {
    console.warn('Could not load conflict profiles:', err);
  }
}

async function loadConflictExplorerData() {
  const selectA = document.getElementById('select-study-a');
  const selectB = document.getElementById('select-study-b');
  const a = selectA && selectA.value ? selectA.value : 'BASS-II';
  const b = selectB && selectB.value ? selectB.value : 'Saffire';
  executeConflictAnalysis(a, b);
}

async function executeConflictAnalysis(studyA, studyB) {
  try {
    const res = await fetch(`${API_BASE}/api/conflict/compare-studies`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ study_a: studyA, study_b: studyB })
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const data = await res.json();
    renderConflictResults(data);
  } catch (err) {
    console.warn('Conflict analysis request failed:', err);
  }
}

function renderConflictResults(data) {
  const scoreVal = document.getElementById('conflict-score-val');
  const badge = document.getElementById('conflict-verdict-badge');
  const summary = document.getElementById('conflict-verdict-summary');
  const caution = document.getElementById('conflict-caution-text');
  const tbody = document.getElementById('conflict-dimensions-tbody');
  const reconcile = document.getElementById('conflict-reconciliation-text');

  if (scoreVal) scoreVal.textContent = (data.comparability_score || 0).toFixed(2);
  if (badge) {
    badge.className = `verdict-badge verdict-${(data.verdict || '').toLowerCase().replace(/_/g, '-')}`;
    badge.textContent = (data.verdict || '').replace(/_/g, ' ');
  }
  if (summary) summary.textContent = data.verdict_summary || '';
  if (caution) caution.textContent = data.cautionary_guidance || '';
  if (reconcile) reconcile.textContent = data.scientific_reconciliation || '';

  // Render dimensions table
  if (tbody) {
    tbody.innerHTML = '';
    (data.dimensions || []).forEach(dim => {
      const tr = document.createElement('tr');
      const statusClass = dim.status === 'MATCH' ? 'status-match' : (dim.status === 'MODERATE_DIFFERENCE' ? 'status-mod' : 'status-mismatch');
      tr.innerHTML = `
        <td><strong>${escapeHTML(dim.dimension)}</strong></td>
        <td>${escapeHTML(dim.study_a)}</td>
        <td>${escapeHTML(dim.study_b)}</td>
        <td><span class="dim-status-pill ${statusClass}">${escapeHTML(String(dim.status).replace(/_/g, ' '))}</span></td>
        <td class="dim-impact-cell">${escapeHTML(dim.physical_impact)}</td>
      `;
      tbody.appendChild(tr);
    });
  }

  // Citations
  const citeA = data.citations?.study_a;
  const citeB = data.citations?.study_b;
  if (citeA) {
    const tA = document.getElementById('cite-title-a');
    const mA = document.getElementById('cite-meta-a');
    const lA = document.getElementById('cite-link-a');
    if (tA) tA.textContent = citeA.name;
    if (mA) mA.textContent = citeA.citation;
    if (lA) lA.href = safeHttpUrl(citeA.url);
  }
  if (citeB) {
    const tB = document.getElementById('cite-title-b');
    const mB = document.getElementById('cite-meta-b');
    const lB = document.getElementById('cite-link-b');
    if (tB) tB.textContent = citeB.name;
    if (mB) mB.textContent = citeB.citation;
    if (lB) lB.href = safeHttpUrl(citeB.url);
  }
}

// ==============================================================================
// FLARE-X EVIDENCE ATLAS: RESEARCH COVERAGE MAP MODULE
// ==============================================================================

function setupCoverageMapView() {
  // Configured for tab clicks
}

async function loadCoverageMapData() {
  try {
    const res = await fetch(`${API_BASE}/api/coverage-map`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const data = await res.json();
    renderCoverageMap(data);
  } catch (err) {
    console.warn('Coverage map fetch failed:', err);
  }
}

function renderCoverageMap(data) {
  const totalRuns = document.getElementById('cov-total-runs');
  const matCount = document.getElementById('cov-materials-count');
  const compPct = document.getElementById('cov-completeness-pct');
  const gapsCount = document.getElementById('cov-gaps-count');
  const container = document.getElementById('coverage-matrix-container');
  const gapsList = document.getElementById('empirical-gaps-list');

  if (totalRuns) totalRuns.textContent = data.total_verified_experiments ?? '—';
  if (matCount) matCount.textContent = data.unique_materials_tested ?? '—';
  if (compPct) compPct.textContent = `${(data.coverage_completeness_pct || 0).toFixed(1)}%`;
  if (gapsCount) gapsCount.textContent = data.untested_gap_cells_count || 0;

  // Render 2D Heatmap Grid
  if (container) {
    const o2Bins = data.matrix_dimensions?.oxygen_bins || [];
    const flowBins = data.matrix_dimensions?.flow_bins || [];
    const grid = data.heatmap_grid || [];

    let html = '<table class="heatmap-table"><thead><tr><th>Oxygen Concentration</th>';
    flowBins.forEach(fb => {
      html += `<th>${escapeHTML(fb.label)}</th>`;
    });
    html += '</tr></thead><tbody>';

    o2Bins.forEach(ob => {
      html += `<tr><td class="row-o2-header"><strong>${escapeHTML(ob.label)}</strong></td>`;
      flowBins.forEach(fb => {
        const cell = grid.find(c => c.o2_bin_id === ob.id && c.flow_bin_id === fb.id);
        const count = cell ? cell.count : 0;
        const density = cell ? cell.density : 'UNTESTED_GAP';
        const swatchClass = density === 'HIGH' ? 'swatch-high' : (density === 'MODERATE' ? 'swatch-mod' : (density === 'SPARSE' ? 'swatch-sparse' : 'swatch-gap'));
        const mats = (cell && cell.materials && cell.materials.length > 0) ? cell.materials.join(', ') : 'None';
        const tooltip = `Tested: ${count} runs | Materials: ${mats} | Spread: ${cell?.spread_count || 0}, Marginal: ${cell?.marginal_count || 0}, Extinction: ${cell?.no_spread_count || 0}`;

        html += `
          <td class="heatmap-cell ${swatchClass}" title="${escapeHTML(tooltip)}">
            <div class="cell-inner">
              <span class="cell-count">${escapeHTML(count)}</span>
              <span class="cell-density-tag">${escapeHTML(String(density).replace('_', ' '))}</span>
            </div>
          </td>
        `;
      });
      html += '</tr>';
    });
    html += '</tbody></table>';
    container.innerHTML = html;
  }

  // Render Empirical White Spaces (Knowledge Gaps)
  if (gapsList) {
    gapsList.innerHTML = '';
    (data.empirical_white_spaces || []).forEach(gap => {
      const card = document.createElement('div');
      card.className = 'gap-card';
      card.innerHTML = `
        <div class="gap-card-header">
          <span class="gap-id-badge">${escapeHTML(gap.gap_id)}</span>
          <span class="gap-risk-pill">HIGH MISSION RISK</span>
        </div>
        <h4 class="gap-title">${escapeHTML(gap.title)}</h4>
        <div class="gap-regime-strip"><strong>Target Regime:</strong> ${escapeHTML(gap.regime)}</div>
        <div class="gap-materials"><strong>Affected Materials:</strong> ${escapeHTML((gap.materials_affected || []).join(', '))}</div>
        <div class="gap-section">
          <span class="gap-section-label">OPERATIONAL RISK:</span>
          <p class="gap-text">${escapeHTML(gap.operational_risk)}</p>
        </div>
        <div class="gap-section">
          <span class="gap-section-label">SCIENTIFIC RATIONALE:</span>
          <p class="gap-text">${escapeHTML(gap.scientific_rationale)}</p>
        </div>
        <div class="gap-recommended-box">
          <span class="rec-label">RECOMMENDED NASA FLIGHT EXPERIMENT:</span>
          <p class="rec-text">${escapeHTML(gap.recommended_experiment)}</p>
        </div>
      `;
      gapsList.appendChild(card);
    });
  }
}

// ==============================================================================
// FLARE-X EVIDENCE ATLAS: CITATION INSPECTOR & PROVENANCE MODAL
// ==============================================================================

function setupCitationInspector() {
  const closeBtn = document.getElementById('btn-close-inspector');
  const backdrop = document.getElementById('modal-backdrop-close');
  const modal = document.getElementById('modal-citation-inspector');

  const hide = () => {
    if (modal) modal.classList.add('hidden');
  };

  if (closeBtn) closeBtn.addEventListener('click', hide);
  if (backdrop) backdrop.addEventListener('click', hide);
}

window.inspectProvenance = async function(experimentId) {
  const modal = document.getElementById('modal-citation-inspector');
  if (!modal) return;

  try {
    const res = await fetch(`${API_BASE}/api/provenance/${encodeURIComponent(experimentId)}`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const data = await res.json();

    const titleEl = document.getElementById('inspect-exp-id');
    const reportTitleEl = document.getElementById('inspect-report-title');
    const citeEl = document.getElementById('inspect-citation');
    const invEl = document.getElementById('inspect-investigation');
    const condEl = document.getElementById('inspect-conditions');
    const outcomeEl = document.getElementById('inspect-outcome');
    const notesEl = document.getElementById('inspect-notes');
    const ntrsUrlEl = document.getElementById('inspect-ntrs-url');
    const tierPill = document.getElementById('inspect-tier-pill');
    const originPill = document.getElementById('inspect-origin-pill');

    if (titleEl) titleEl.textContent = `NASA Experiment ${data.experiment_id}`;
    if (reportTitleEl) reportTitleEl.textContent = data.report_title || `NASA Technical Report ${data.report_id}`;
    if (citeEl) citeEl.textContent = data.exact_source_citation || `NASA Report ${data.report_id}`;
    if (invEl) invEl.textContent = `${data.investigation} · Facility: ${data.gravity_env || 'ISS'}`;
    if (condEl) condEl.textContent = `${data.material} · ${data.oxygen_pct}% O₂ · ${data.pressure_kpa} kPa · ${data.flow_cm_s} cm/s forced flow`;
    if (outcomeEl) outcomeEl.textContent = `${data.outcome} (${data.extraction_notes || 'Observed flame behavior'})`;
    if (notesEl) notesEl.textContent = data.extraction_notes || 'Extracted from peer-reviewed NASA Technical Memorandum data tables.';
    if (ntrsUrlEl) ntrsUrlEl.href = safeHttpUrl(data.source_url || `https://ntrs.nasa.gov/citations/${encodeURIComponent(data.report_id || '')}`, 'https://ntrs.nasa.gov/');
    if (tierPill) tierPill.textContent = data.verification_tier || 'VERIFIED_FLIGHT_TABLE';
    if (originPill) originPill.textContent = data.data_origin || 'direct_measurement';

    modal.classList.remove('hidden');
  } catch (err) {
    console.warn('Could not inspect provenance:', err);
  }
};

