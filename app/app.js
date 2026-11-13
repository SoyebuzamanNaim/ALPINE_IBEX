/**
 * FLARE-X Aerospace Mission Control Frontend Application
 * Interacts with FastAPI backend or operates in resilient client-side fallback mode.
 * Presents curated NASA microgravity observations and gated model inference.
 */

// Local static previews on 5500/5501 connect to FastAPI on 8000.
// FastAPI-hosted pages use their own origin; deployments may set FLARE_API_BASE explicitly.
const localPreview = ['localhost', '127.0.0.1'].includes(window.location.hostname) && ['5500', '5501'].includes(window.location.port);
const API_BASE = window.FLARE_API_BASE || (localPreview
  ? `${window.location.protocol}//${window.location.hostname}:8000`
  : window.location.protocol === 'file:' ? 'http://localhost:8000' : '');

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
// Fitted to concurrent-flow cast-PMMA rods over 13.6-22.2 % O2. It describes
// extinction of an ESTABLISHED flame, so it does not predict whether ignition will take hold.
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
      initialO2Offset: o2_pct - limit,
      regime: this.regime(U_cm_s),
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
  sweepMode: null,
  publishedSweep: null,
  sweepObservations: [],
  sweepEvidenceError: null,
  activeTab: 'view-scenario-lab',
  sweepRunning: false,
  experiments: [],
  materialCounts: {},
  modelMeta: null,
  connectionError: false,
  sweepInterval: null
};

const FUEL_PROPERTIES = {
  'PMMA': { desc: 'Acrylic films, rods and slabs', prop: 'Geometry is not a model input' },
  'Cellulose': { desc: 'Thin cellulose laboratory wipes', prop: 'Geometry is not a model input' },
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
  if (element._animationId) cancelAnimationFrame(element._animationId);
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
      element._animationId = requestAnimationFrame(step);
    } else {
      element._currentVal = endVal;
    }
  }
  element._animationId = requestAnimationFrame(step);
}

function clearProbabilityDisplay(value = 'N/A') {
  for (const suffix of ['no-spread', 'marginal', 'spread']) {
    const label = document.getElementById(`val-prob-${suffix}`);
    if (label) {
      if (label._animationId) cancelAnimationFrame(label._animationId);
      label._animationId = null;
      label._currentVal = undefined;
      label.textContent = value;
    }
    const bar = document.getElementById(`bar-seg-${suffix}`);
    if (bar) bar.style.width = '0%';
  }
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
  document.getElementById('api-docs-link').href = `${API_BASE}/docs`;
  document.getElementById('model-metadata-link').href = `${API_BASE}/model`;
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
  setupEvidenceActions();
  
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
  const tabs = document.querySelectorAll('[role="tab"]');
  tabs.forEach(tab => {
    tab.tabIndex = tab.getAttribute('aria-selected') === 'true' ? 0 : -1;
    tab.addEventListener('keydown', event => {
      const index = Array.from(tabs).indexOf(tab);
      const target = event.key === 'ArrowRight' ? (index + 1) % tabs.length
        : event.key === 'ArrowLeft' ? (index + tabs.length - 1) % tabs.length
          : event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1 : null;
      if (target !== null) { event.preventDefault(); tabs[target].focus(); tabs[target].click(); }
    });
    tab.addEventListener('click', () => {
      tabs.forEach(t => {
        t.classList.remove('active');
        t.setAttribute('aria-selected', 'false');
        t.tabIndex = -1;
      });
      tab.classList.add('active');
      tab.setAttribute('aria-selected', 'true');
      tab.tabIndex = 0;
      tab.scrollIntoView({ block: 'nearest', inline: 'nearest' });

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
      if (targetId !== 'view-counterfactual-sweep') {
        clearTimeout(sweepRefreshTimeout);
        if (state.sweepInterval != null) {
          clearInterval(state.sweepInterval);
          state.sweepInterval = null;
          state.sweepRunning = false;
          const button = document.getElementById('btn-run-auto-sweep');
          if (button) button.textContent = '▶ Play oxygen sweep';
        }
      }

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
    updateCoordHud();
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
      state.flow_cm_s = Math.min(state.flow_cm_s, 45.0);
      flowSlider.value = state.flow_cm_s;
      document.getElementById('readout-flow').textContent = `${state.flow_cm_s} cm/s`;
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
  if (sampleBadge) sampleBadge.textContent = count == null
    ? state.modelMeta ? '0 recorded observations' : 'Evidence count unavailable' : `${count} observations`;
  const domain = state.modelMeta?.training_range?.per_material?.[state.material];
  const domainText = document.getElementById('material-domain');
  if (domainText) domainText.textContent = domain
    ? `Recorded ranges: ${domain.oxygen_pct.min}–${domain.oxygen_pct.max}% O₂; ${domain.pressure_kpa.min}–${domain.pressure_kpa.max} kPa; ${domain.flow_cm_s.min}–${domain.flow_cm_s.max} cm/s. Joint coverage is also required.`
    : 'Recorded material ranges require the backend connection.';
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

  for (const [id, value] of [['input-o2', o2], ['input-pressure', p], ['input-flow', flow]]) {
    const input = document.getElementById(id);
    input.min = Math.min(Number(input.min), value);
    input.max = Math.max(Number(input.max), value);
    input.value = value;
  }
  const materialInput = document.getElementById('input-material');
  if (!Array.from(materialInput.options).some(option => option.value === mat)) {
    const option = document.createElement('option');
    option.value = mat;
    option.textContent = `${mat} (no recorded observations)`;
    materialInput.appendChild(option);
  }
  materialInput.value = mat;

  document.getElementById('readout-o2').textContent = `${o2.toFixed(1)} %`;
  document.getElementById('readout-pressure').textContent = `${p.toFixed(1)} kPa`;
  document.getElementById('readout-flow').textContent = `${flow} cm/s`;

  updateCoordHud();
  updateMaterialInfo();
  triggerScenarioEvaluation();
  fetchBoundarySlice();
  scheduleSweepRefresh();
}

function updateCoordHud() {
  ++parseGeneration;
  const feedback = document.getElementById('nlp-feedback');
  if (feedback) feedback.style.display = 'none';
  for (const [id, o2, pressure, flow] of [
    ['preset-iss-standard', 21, 101.3, 5], ['preset-exploration', 34, 56.5, 10],
    ['preset-near-extinction', 16.5, 101.3, 3],
  ]) {
    document.getElementById(id)?.classList?.toggle('active-preset', state.material === 'PMMA' &&
      state.oxygen_pct === o2 && state.pressure_kpa === pressure && state.flow_cm_s === flow);
  }
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
    const width = canvas.width || rect.width;
    const height = canvas.height || rect.height;
    const clickX = (e.clientX - rect.left) * width / rect.width;
    const clickY = (e.clientY - rect.top) * height / rect.height;

    const padLeft = 70;
    const padBottom = 45;
    const padRight = 35;
    const padTop = 35;
    const plotW = width - padLeft - padRight;
    const plotH = height - padTop - padBottom;

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

let currentEvidence = null;
function renderEvidenceOverview(experiments, inputs, datasetHash = null) {
  const status = document.getElementById('evidence-overview-status');
  const body = document.getElementById('evidence-overview-body');
  const download = document.getElementById('download-evidence');
  currentEvidence = {scenario: inputs, observations: experiments, dataset_sha256: datasetHash || state.modelMeta?.dataset_sha256 || null,
    summary_method: 'deterministic_record_template', scope: 'current FLARE-X dataset',
    ranking: 'Normalized numerical proximity plus material penalty; not scientific reliability'};
  if (status) status.textContent = experiments.length
    ? experiments.some(exp => exp.material === inputs.material)
      ? `${experiments.length} ranked indexed observations. Similar conditions can have different outcomes; inspect the source context.`
      : `No observations for ${inputs.material} in the current FLARE-X dataset. Showing ${experiments.length} different-material records for context.`
    : 'No matching observations in the current FLARE-X dataset';
  const selected = experiments[0];
  if (body) body.innerHTML = selected ? `
    <p class="selected-observation"><strong>${escapeHTML(selected.experiment_id)}</strong> · ${escapeHTML(selected.material)} · curated label: ${escapeHTML(selected.outcome)}</p>
    <p><strong>Source observation:</strong> ${escapeHTML(selected.outcome_raw || 'Not recorded')}</p>
    <p><strong>Conditions differ:</strong> ${escapeHTML(selected.interpretation?.conditions_differ?.join(' ') || 'Comparison unavailable.')}</p>
    <p><strong>Cannot conclude:</strong> ${escapeHTML(selected.interpretation?.cannot_conclude || 'Similarity does not establish the requested outcome or safety.')}</p>
    <p><a href="${safeHttpUrl(selected.source_url)}" target="_blank" rel="noopener noreferrer">Read NTRS ${escapeHTML(selected.report_id)}</a></p>
    <p class="module-explainer">The ranked record cards show the full similarity ranking and citation tracing. Summary method: deterministic template.</p>` : '';
  if (download) download.disabled = experiments.length === 0;
}

function setupEvidenceActions() {
  document.getElementById('download-evidence')?.addEventListener('click', () => {
    if (!currentEvidence) return;
    const url = URL.createObjectURL(new Blob([JSON.stringify(currentEvidence, null, 2)], {type: 'application/json'}));
    const link = document.createElement('a');
    link.href = url;
    link.download = 'flare-x-evidence.json';
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  let searchGeneration = 0;
  document.getElementById('report-search-form')?.addEventListener('submit', async event => {
    event.preventDefault();
    const generation = ++searchGeneration;
    const query = document.getElementById('report-search-input').value.trim();
    const status = document.getElementById('report-search-status');
    const results = document.getElementById('report-search-results');
    if (!query) return;
    results.replaceChildren();
    status.textContent = 'Searching indexed NASA report abstracts…';
    try {
      const response = await fetch(`${API_BASE}/reports/search?query=${encodeURIComponent(query)}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      if (generation !== searchGeneration) return;
      status.textContent = `${data.reports.length} reports matched by lexical relevance, not scientific reliability.`;
      data.reports.forEach(report => {
        const item = document.createElement('article');
        item.innerHTML = `<h3><a href="${safeHttpUrl(report.source_url)}" target="_blank" rel="noopener noreferrer">${escapeHTML(report.title)}</a></h3>
          <p>${escapeHTML(report.abstract || 'No abstract indexed.')}</p><p class="module-explainer">NTRS ${escapeHTML(report.report_id)} · Indexed abstract; verify claims in the source report.</p>`;
        results.appendChild(item);
      });
    } catch (error) {
      if (generation === searchGeneration) status.textContent = 'Report search unavailable. Check the API connection and try again.';
    }
  });
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
  currentEvidence = null;
  const evidenceStatus = document.getElementById('evidence-overview-status');
  const evidenceBody = document.getElementById('evidence-overview-body');
  const evidenceDownload = document.getElementById('download-evidence');
  if (evidenceStatus) evidenceStatus.textContent = 'Looking up indexed observations for these conditions…';
  if (evidenceBody) evidenceBody.innerHTML = '';
  if (evidenceDownload) evidenceDownload.disabled = true;
  clearProbabilityDisplay();
  const badge = document.getElementById('regime-badge');
  if (badge) badge.textContent = 'Checking selected conditions…';
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
    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.detail || `HTTP error ${res.status}`);
    }
    const data = await res.json();
    if (!isCurrent()) return;
    if (state.connectionError) { state.connectionError = false; loadModelStatus(); }
    renderPredictionResults(data);
    renderEvidenceOverview(data.nearest_experiments || [], payload);
  } catch (err) {
    if (!isCurrent()) return;
    state.connectionError = true;
    const status = document.getElementById('status-text');
    const dot = document.getElementById('status-dot');
    const gate = document.getElementById('model-gate-text');
    if (status) status.textContent = 'Live estimate unavailable · published reference only';
    if (dot) dot.className = 'heartbeat-pulse status-offline';
    if (gate) { gate.textContent = 'ESTIMATE UNAVAILABLE'; gate.className = 'metric-status-offline'; }
    console.warn('API unreachable; falling back to the published NASA boundary:', err);
    // No simulated model output. We show NASA's own published boundary instead,
    // which is deterministic and needs no backend.
    renderPublishedBoundary(payload);
    const message = document.getElementById('alert-message');
    if (message) message.textContent = `Live estimate unavailable (${err.message}). ${message.textContent}`;
    // Evidence retrieval does not depend on a usable model artifact.
    try {
      const response = await fetch(`${API_BASE}/evidence`, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)});
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const evidence = await response.json();
      if (!isCurrent()) return;
      state.materialCounts = evidence.material_counts || {};
      updateMaterialInfo();
      renderNearestExperiments(evidence.nearest_experiments || []);
      renderEvidenceOverview(evidence.nearest_experiments || [], payload, evidence.dataset_sha256);
      if (status) status.textContent = 'Evidence online · research model unavailable';
    } catch (evidenceError) {
      if (isCurrent() && evidenceStatus) evidenceStatus.textContent = 'Evidence lookup unavailable. Connect the API and try again.';
    }
  }
}

// Render Prediction UI according to the 4-Tier Scientific State Protocol
function renderPredictionResults(data) {
  if (!data.probabilities) clearProbabilityDisplay();
  const alertBanner = document.getElementById('envelope-alert-banner');
  if (alertBanner?.dataset) alertBanner.dataset.kind = !data.in_training_range ? 'out-of-range' :
    data.status === 'model_unvalidated' ? 'validation' : 'evidence';
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
    if (alertTitle) alertTitle.textContent = 'CONDITIONS OUTSIDE THE INDEXED MODEL DOMAIN';
    const reasons = (data.out_of_range_reasons || []).map(r => r.reason).join(' ');
    if (alertMsg) alertMsg.textContent = reasons || data.warning_message || 'Requested parameters are outside NASA training data.';

    if (badge) {
      badge.className = 'regime-status-badge regime-refusal';
      badge.textContent = 'MODEL REFUSAL: OUT OF ENVELOPE';
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
        if (stateTierExplainer) stateTierExplainer.textContent = 'Exploratory research estimate · no independent validation';
      }
    }

    const pred = data.prediction;
    const probs = data.probabilities;

    if (badge) {
      badge.className = `regime-status-badge regime-${pred ? pred.replace('_', '-') : 'spread'}`;
      badge.textContent = pred === 'spread' ? 'Sustained Flame Spread' : (pred === 'marginal_spread' ? 'Marginal Spread (Unsteady)' : 'Extinction / No Spread');
    }

    const confPct = Math.round((probs[pred] || 0) * 100);
    if (confPill) confPill.textContent = `${confPct}% estimated class probability`;

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
      expText.textContent = data.explanation || 'Exploratory estimate from the current research model.';
    }
    if (data.warning_message && briefing) briefing.textContent += ` ${data.warning_message}`;
  }

  // Render Nearest Experiments List
  renderNearestExperiments(data.nearest_experiments || []);

  // Update canvas reticle
  drawBoundaryCanvas();
}

// TIER 4: SERVICE UNAVAILABLE (Honest state without simulated mock predictions)
// Render the published NASA boundary result. Used when the backend is unreachable
// (the static GitHub Pages deployment) and as a physics cross-check when it is not.
// Shows NASA's fitted reference and labels the input-to-fit offset. No probabilities are
// shown, because a deterministic boundary does not produce any.
function renderPublishedBoundary(payload) {
  setNearestEvidenceStatus('Nearest observations require the backend service.');
  const o2 = payload.oxygen_pct, U = payload.flow_cm_s, mat = payload.material;
  const el = (id) => document.getElementById(id);
  const banner = el('envelope-alert-banner'), aTitle = el('alert-title'), aMsg = el('alert-message');
  if (banner?.dataset) banner.dataset.kind = 'published';
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

  // The fit is for concurrent-flow cast-PMMA rods only. Say so rather than extrapolating it.
  if (mat !== 'PMMA') {
    if (banner) banner.classList.remove('hidden');
    if (aTitle) aTitle.textContent = 'OUTSIDE THE PUBLISHED BOUNDARY FIT';
    if (aMsg) aMsg.textContent = `${NASA_BOUNDARY.CITATION} was fitted to concurrent-flow cast-PMMA rods. It is not validated for ${mat}, so no margin is reported here. Use the flight-archive view to see the real experiments for this material.`;
    if (badge) { badge.className = 'regime-status-badge regime-refusal'; badge.textContent = 'NO PUBLISHED BOUNDARY FOR THIS MATERIAL'; }
    if (pill) pill.textContent = 'NOT APPLICABLE';
    if (briefing) briefing.textContent = `The published NASA boundary covers concurrent-flow cast-PMMA rods. For ${mat}, this tool can show you the real flight tests that exist but cannot place you against a validated limit.`;
    if (expText) expText.textContent = '';
    return;
  }

  // Equation 6.1 was fitted to concurrent-flow cast-PMMA rod tests in the ISS glovebox at
  // nominal cabin pressure and 0–55 cm/s flow; it has no pressure term.
  if (Math.abs(payload.pressure_kpa - NASA_BOUNDARY.NOMINAL_PRESSURE_KPA) > 0.05 ||
      payload.flow_cm_s < NASA_BOUNDARY.VALID_FLOW[0] ||
      payload.flow_cm_s > NASA_BOUNDARY.VALID_FLOW[1] ||
      !Number.isFinite(payload.pressure_kpa) || !Number.isFinite(payload.flow_cm_s)) {
    if (banner) banner.classList.remove('hidden');
    if (aTitle) aTitle.textContent = 'OUTSIDE DOCUMENTED BOUNDARY CONDITIONS';
    if (aMsg) aMsg.textContent = `${NASA_BOUNDARY.CITATION} describes concurrent-flow cast-PMMA rod tests at nominal ${NASA_BOUNDARY.NOMINAL_PRESSURE_KPA} kPa and ${NASA_BOUNDARY.VALID_FLOW[0]}–${NASA_BOUNDARY.VALID_FLOW[1]} cm/s flow. No margin is reported for this pressure or flow.`;
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

  const offset = res.initialO2Offset;
  if (banner) banner.classList.remove('hidden');
  if (aTitle) aTitle.textContent = 'PUBLISHED FIT USES POST-BURN OXYGEN';
  if (aMsg) aMsg.textContent = 'The selected oxygen is an initial condition. NASA fitted this extinction curve using oxygen measured after burning, so an extinction margin cannot be determined from this input.';
  if (badge) {
    badge.className = 'regime-status-badge regime-marginal';
    badge.textContent = 'PUBLISHED REFERENCE ONLY';
  }
  if (pill) pill.textContent = `${offset >= 0 ? '+' : ''}${offset.toFixed(2)} initial O₂ offset`;
  if (briefing) briefing.textContent = `At ${U} cm/s, NASA's concurrent-flow fit is ${res.limitO2.toFixed(2)} % post-burn O₂. The selected ${o2.toFixed(1)} % is initial O₂, so the ${Math.abs(offset).toFixed(2)}-point numerical difference is not an extinction margin or a predicted outcome.`;
  if (expText) {
    expText.innerHTML = `Stretch rate a = ${res.stretch.toFixed(1)} s<sup>-1</sup> for a ${(r * 2 * 10).toFixed(2)} mm diameter rod, on the <strong>${escapeHTML(res.regime)}</strong> branch (separator U/U<sub>D</sub> = 1, U<sub>D</sub> = ${NASA_BOUNDARY.U_D} cm/s). The limit comes from <a href="${escapeHTML(safeHttpUrl(res.url, NASA_BOUNDARY.URL))}" target="_blank" rel="noopener noreferrer" class="citation-ntrs-link">${escapeHTML(res.citation)} ↗</a>, fitted by NASA to concurrent-flow cast-PMMA rods using post-burn oxygen. It describes extinction of an <em>established</em> flame and does not predict ignition.`;
  }
}

function renderOfflineUnavailable(payload, err) {
  const alertBanner = document.getElementById('envelope-alert-banner');
  if (alertBanner?.dataset) alertBanner.dataset.kind = 'offline';
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
    alertMsg.textContent = 'The research API is unavailable. No simulated results are shown. Start the service or reconnect the deployed API to inspect live observations.';
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
    container.innerHTML = '<p class="module-explainer">No matching observations in the current FLARE-X dataset</p>';
    return;
  }

  experiments.forEach((exp, index) => {
    const item = document.createElement('div');
    item.className = 'flight-obs-card';

    const dist = Number.isFinite(exp.distance) ? `Similarity #${index + 1} · d = ${exp.distance.toFixed(3)}` : 'Similarity distance unavailable';
    const outcomeClass = exp.outcome === 'spread' ? 'badge-spread' : (exp.outcome === 'marginal_spread' ? 'badge-marginal' : 'badge-no-spread');
    const reportUrl = safeHttpUrl(exp.source_url || `https://ntrs.nasa.gov/citations/${encodeURIComponent(exp.report_id || '')}`, 'https://ntrs.nasa.gov/');
    const eid = exp.experiment_id || 'EXP_OBS';
    const ranking = exp.similarity_ranking;
    const interpretation = exp.interpretation;
    const ranges = ranking?.feature_ranges;
    const displayRanges = ranges && Object.fromEntries(Object.entries(ranges).map(([key, value]) => [key, Number(value.toFixed(4))]));
    const rankingText = ranges
      ? `Distance = √[(ΔO₂/${displayRanges.oxygen_pct})² + (Δpressure/${displayRanges.pressure_kpa})² + (Δairflow/${displayRanges.flow_cm_s})²] + ${ranking.material_penalty} material penalty. Lower is closer, not more reliable.`
      : 'Similarity ranking uses oxygen, pressure and airflow proximity with a material penalty; it does not measure scientific reliability.';

    item.innerHTML = `
      <div class="obs-top-line">
        <span class="obs-id">${escapeHTML(eid)} · ${escapeHTML(exp.material)}</span>
        <span class="obs-distance">${escapeHTML(dist)}</span>
      </div>
      <div class="obs-conditions">
        ${escapeHTML(exp.oxygen_pct)}% O₂ · ${escapeHTML(exp.pressure_kpa)} kPa · ${escapeHTML(exp.flow_cm_s)} cm/s
      </div>
      <p class="obs-context">Geometry: ${escapeHTML(exp.sample_geometry || 'not recorded')} · Thickness: ${escapeHTML(exp.sample_thickness_mm ?? 'not recorded')}${exp.sample_thickness_mm != null ? ' mm' : ''} · Flow direction: ${escapeHTML(exp.flow_direction || 'not recorded')}. Ignition history: not recorded as a structured field.</p>
      <div class="obs-interpretation">
        <p><strong>What was observed:</strong> ${escapeHTML(interpretation?.observed || exp.similarity_explanation || exp.outcome || 'Not recorded')}${exp.outcome_interpreted ? ' Outcome label interpreted from the source.' : ''}</p>
        <p><strong>Source observation:</strong> ${escapeHTML(exp.outcome_raw || 'not recorded')}</p>
        <p><strong>Which conditions differ:</strong> ${escapeHTML(interpretation?.conditions_differ?.join(' ') || 'Comparison unavailable.')}</p>
        <p><strong>What cannot be concluded:</strong> ${escapeHTML(interpretation?.cannot_conclude || 'Nearby observations do not establish the requested outcome or operational safety.')}</p>
      </div>
      <details class="obs-ranking"><summary>Why this record matches</summary>
        <p>${escapeHTML(rankingText)}</p>
        <p>Within display tolerances (not exact matches): ${escapeHTML((exp.matched_variables || []).join('; ') || 'None reported')}. Tolerances: 1 oxygen percentage point, 5 kPa and 2 cm/s; material must match.</p>
        <p>Outside display tolerances: ${escapeHTML((exp.mismatched_variables || []).join('; ') || 'None reported')}.</p>
        <p>Source notes: ${escapeHTML(exp.extraction_notes || 'not recorded')}</p>
      </details>
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
  ctx.font = '11px "Inter", monospace';
  ctx.textAlign = 'center';
  for (let o2 = Math.ceil(o2Min); o2 <= o2Max; o2 += 3) {
    ctx.fillText(`${o2}%`, toX(o2), padTop + plotH + 20);
  }
  ctx.font = '12px "Inter", sans-serif';
  ctx.fillStyle = '#1e293b';
  ctx.fillText('Oxygen Concentration, X_O₂ (% by volume)', padLeft + plotW / 2, h - 8);

  ctx.font = '11px "Inter", monospace';
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
    ctx.strokeStyle = '#164c78';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Center Core Dot
    ctx.beginPath();
    ctx.arc(qx, qy, 2, 0, Math.PI * 2);
    ctx.fillStyle = '#ffffff';
    ctx.fill();
    ctx.strokeStyle = '#164c78';
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
    ctx.strokeStyle = '#164c78';
    ctx.lineWidth = 1;
    const tagText = `${state.oxygen_pct.toFixed(1)}% · ${state.flow_cm_s.toFixed(1)} cm/s`;
    ctx.font = '10px "Inter", monospace';
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
let parseGeneration = 0;
function setupNlpParser() {
  const btn = document.getElementById('nlp-query-submit');
  const input = document.getElementById('nlp-query-input');
  if (!btn || !input) return;

  btn.addEventListener('click', async () => {
    const text = input.value.trim();
    if (!text) return;
    const generation = ++parseGeneration;
    const isCurrent = () => generation === parseGeneration && input.value.trim() === text;
    const feedbackEl = document.getElementById('nlp-feedback');
    if (feedbackEl) {
      feedbackEl.textContent = 'Reading scenario…';
      feedbackEl.style.display = 'block';
    }

    try {
      const res = await fetch(`${API_BASE}/scenario/parse`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: text })
      });
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const data = await res.json();
      if (!isCurrent()) return;
      if (data.is_valid && data.parsed_scenario) {
        if (feedbackEl) {
          const notes = [...(data.assumptions || [])];
          if (data.unmodeled_context?.length) notes.push('Additional gas composition, geometry, flow direction or ignition context is not represented by the four ranked inputs; agreement remains unknown.');
          feedbackEl.textContent = notes.join(' ');
          feedbackEl.style.display = notes.length ? 'block' : 'none';
        }
        const sc = data.parsed_scenario;
        updateInputs(sc.oxygen_pct, sc.pressure_kpa, sc.flow_cm_s, sc.material);
      } else {
        const msg = 'Could not parse scenario: ' + ((data.ambiguities || []).join('; ') || 'Add oxygen, pressure, flow, and material.');
        if (feedbackEl) {
          feedbackEl.textContent = msg;
          feedbackEl.style.display = 'block';
        } else {
          console.warn(msg);
        }
      }
    } catch (err) {
      if (!isCurrent()) return;
      console.warn('NLP parser error:', err);
      if (feedbackEl) {
        feedbackEl.textContent = 'Scenario search is unavailable. Check the backend connection and try again.';
        feedbackEl.style.display = 'block';
      }
    }
  });

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') btn.click();
  });
  input.addEventListener('input', () => {
    ++parseGeneration;
    const feedback = document.getElementById('nlp-feedback');
    if (feedback) feedback.style.display = 'none';
  });
}

// Oxygen sweep: use guarded model output when available, otherwise the separate
// published BASS-II cast-PMMA relation under its documented conditions.
let sweepGeneration = 0;
let sweepRefreshTimeout = null;
function setSweepCopy(mode, message = '') {
  const setText = (id, value) => {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
  };
  const source = document.getElementById('sweep-source-link');
  const canvas = document.getElementById('sweep-chart-canvas');
  const modelKey = document.getElementById('sweep-model-key');
  if (source) source.hidden = mode !== 'published';
  if (modelKey) modelKey.hidden = mode !== 'model';
  if (mode === 'published') {
    setText('sweep-title', 'Published PMMA oxygen sweep');
    setText('sweep-description', 'NASA BASS-II Eq (6.1) is a concurrent-flow extinction fit for established flames. The plotted test observations show initial oxygen at test start; they are context only because the fit uses oxygen measured after burning. This is not a model prediction or ignition test.');
    setText('sweep-metric-label', 'INITIAL O₂ OFFSET · NOT A SAFETY MARGIN');
    setText('sweep-above-heading', 'Matching concurrent-flow tests');
    setText('sweep-below-heading', 'Measurement basis');
    setText('sweep-above-context', 'Examples show initial oxygen at test start and reported outcome. They provide context only, not validation points for the fitted curve.');
    setText('sweep-below-context', 'NASA fitted Eq (6.1) using oxygen readings after burning at extinction. Initial and post-burn oxygen are different measurements.');
    if (canvas) canvas.setAttribute('aria-label', 'NASA PMMA extinction fit with contextual initial oxygen readings from concurrent-flow tests');
  } else if (mode === 'model') {
    setText('sweep-title', 'Research model oxygen sweep');
    setText('sweep-description', 'Exploratory model estimates across oxygen concentrations for the selected material, pressure, and flow. Probabilities are not validated across reports. Refused points remain blank; transitions do not establish safety.');
    setText('sweep-metric-label', 'MODEL TRANSITION DISTANCE');
    setText('sweep-above-heading', 'Higher oxygen observations');
    setText('sweep-below-heading', 'Lower oxygen observations');
    setText('sweep-above-context', 'Observed outcomes depend on material geometry, airflow, pressure and ignition history. Inspect source records before drawing a conclusion.');
    setText('sweep-below-context', 'A lower oxygen concentration does not by itself establish extinction for every material or geometry. No safety clearance is inferred from this view.');
    if (canvas) canvas.setAttribute('aria-label', 'Exploratory model oxygen probability sweep');
  } else {
    setText('sweep-title', 'Oxygen sweep unavailable for this scenario');
    setText('sweep-description', message);
    setText('sweep-metric-label', 'OXYGEN SWEEP');
    setText('sweep-above-heading', 'Sweep availability');
    setText('sweep-below-heading', 'Inference limits');
    setText('sweep-above-context', '');
    setText('sweep-below-context', '');
    if (canvas) canvas.setAttribute('aria-label', 'Oxygen sweep unavailable');
  }
}

function publishedSweepFor(scenario) {
  if (scenario.material !== 'PMMA' ||
      Math.abs(scenario.pressure_kpa - NASA_BOUNDARY.NOMINAL_PRESSURE_KPA) > 0.05 ||
      scenario.flow_cm_s < NASA_BOUNDARY.VALID_FLOW[0] ||
      scenario.flow_cm_s > NASA_BOUNDARY.VALID_FLOW[1]) return null;
  const limitO2 = NASA_BOUNDARY.limitO2(NASA_BOUNDARY.stretch(scenario.flow_cm_s, state.rod_radius_cm));
  return Number.isFinite(limitO2) ? { limitO2, flow: scenario.flow_cm_s } : null;
}

function configureSweepSlider(mode) {
  const slider = document.getElementById('sweep-oxygen-slider');
  if (!slider) return;
  const [min, max] = mode === 'published' ? NASA_BOUNDARY.VALID_O2 : state.sweepData.range;
  slider.min = String(min);
  slider.max = String(max);
  slider.step = mode === 'published' ? '0.1' : 'any';
  slider.value = String(Math.min(max, Math.max(min, state.oxygen_pct)));
  slider.disabled = false;
  const minTick = document.getElementById('sweep-tick-min');
  const maxTick = document.getElementById('sweep-tick-max');
  if (minTick) minTick.textContent = `| ${min.toFixed(1)}% O₂`;
  if (maxTick) maxTick.textContent = `| ${max.toFixed(1)}% O₂`;
  const autoBtn = document.getElementById('btn-run-auto-sweep');
  if (autoBtn) {
    autoBtn.disabled = false;
    autoBtn.textContent = '▶ Play oxygen sweep';
  }
}
function scheduleSweepRefresh() {
  ++sweepGeneration;
  clearTimeout(sweepRefreshTimeout);
  setSweepUnavailable('Loading sweep for selected conditions…');
  if (state.activeTab === 'view-counterfactual-sweep') {
    sweepRefreshTimeout = setTimeout(fetchSweepData, 150);
  }
}

function setSweepUnavailable(message) {
  if (state.sweepInterval != null) {
    clearInterval(state.sweepInterval);
    state.sweepInterval = null;
  }
  state.sweepRunning = false;
  state.sweepData = null;
  state.sweepMode = null;
  state.publishedSweep = null;
  state.sweepObservations = [];
  state.sweepEvidenceError = null;
  state.dynamicLocBoundary = null;
  state.sweepEvidenceBefore = null;
  state.sweepEvidenceAfter = null;
  state.sweepError = message;
  const slider = document.getElementById('sweep-oxygen-slider');
  const autoBtn = document.getElementById('btn-run-auto-sweep');
  if (slider) slider.disabled = true;
  if (autoBtn) autoBtn.disabled = true;
  if (autoBtn) autoBtn.textContent = '▶ Play oxygen sweep';
  setSweepCopy(null, message);
  const samplingNote = document.getElementById('sweep-sampling-note');
  if (samplingNote) samplingNote.textContent = message;
  updateSweepPoint(state.oxygen_pct);
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
  setSweepUnavailable('Loading oxygen sweep…');
  const start = Math.min(16, scenario.oxygen_pct);
  const end = Math.max(21, scenario.oxygen_pct);
  try {
    const res = await fetch(`${API_BASE}/sweep`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        baseline: scenario,
        param: 'oxygen_pct',
        start,
        end,
        steps: Math.min(100, Math.round((end - start) * 10) + 1)
      })
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.detail || `HTTP error ${res.status}`);
    }
    const sweepData = await res.json();
    if (!isCurrent()) return;
    const trans = sweepData.transitions;
    if (!Array.isArray(sweepData.points) || sweepData.points.length === 0) {
      setSweepUnavailable('The research model returned no sweep points.');
      return;
    }
    const eligible = sweepData.points.filter(point => point.prediction != null && point.probabilities != null);
    const refusals = sweepData.points.filter(point => point.prediction == null);
    const reasons = [...new Set(refusals.map(point => point.warning_message || (point.status || 'estimate refused').replaceAll('_', ' ')))].join(' ');
    if (eligible.length === 0) {
      setSweepUnavailable(`No model estimates: all ${sweepData.points.length} sampled points were refused. ${reasons}`);
      return;
    }
    state.sweepData = sweepData;
    state.sweepMode = 'model';
    state.sweepError = null;
    setSweepCopy('model');
    configureSweepSlider('model');
    const samplingNote = document.getElementById('sweep-sampling-note');
    if (samplingNote) samplingNote.textContent =
      `${scenario.material} · ${scenario.pressure_kpa} kPa · ${scenario.flow_cm_s} cm/s. ` +
      `${eligible.length} of ${sweepData.points.length} sampled points have estimates; ${refusals.length} refused. ` +
      `Oxygen range: ${start}–${end}%. Gaps are refusals, not zero probability. ${reasons}`;
    const slider = document.getElementById('sweep-oxygen-slider');
    const t = (trans || []).find(tr => tr.to_regime === 'spread' || tr.to_regime === 'marginal_spread') || (trans || [])[0];
    state.dynamicLocBoundary = t?.midpoint ?? null;
    state.sweepEvidenceBefore = t?.evidence_before || null;
    state.sweepEvidenceAfter = t?.evidence_after || null;
    updateSweepPoint(parseFloat(slider ? slider.value : 21.0));
  } catch (err) {
    if (!isCurrent()) return;
    const published = publishedSweepFor(scenario);
    if (!published) {
      const reason = scenario.material !== 'PMMA'
        ? 'The published relation applies only to cast-PMMA rods; this material has no available oxygen sweep while model validation is pending.'
        : Math.abs(scenario.pressure_kpa - NASA_BOUNDARY.NOMINAL_PRESSURE_KPA) > 0.05
          ? 'The published PMMA relation has no pressure adjustment. Select 101.3 kPa to explore it; model inference remains withheld.'
          : 'The selected flow is outside the published PMMA relation. Model inference remains withheld.';
      setSweepUnavailable(reason);
      setSweepCopy(null, reason);
      return;
    }
    state.sweepMode = 'published';
    state.publishedSweep = published;
    state.sweepObservations = null;
    state.sweepError = null;
    setSweepCopy('published');
    configureSweepSlider('published');
    const samplingNote = document.getElementById('sweep-sampling-note');
    if (samplingNote) samplingNote.textContent =
      `Published reference range: ${NASA_BOUNDARY.VALID_O2.join('–')}% O₂. ` +
      (scenario.oxygen_pct < NASA_BOUNDARY.VALID_O2[0] || scenario.oxygen_pct > NASA_BOUNDARY.VALID_O2[1]
        ? `Selected scenario oxygen (${scenario.oxygen_pct}%) is outside this range; the reference slider is clamped to its nearest endpoint.`
        : 'The slider compares initial oxygen with the separately scoped post-burn fit.');
    const slider = document.getElementById('sweep-oxygen-slider');
    updateSweepPoint(parseFloat(slider ? slider.value : 21.0));
    loadPublishedSweepObservations(generation, scenario);
  }
}

async function loadPublishedSweepObservations(generation, scenario) {
  try {
    const response = await fetch(`${API_BASE}/experiments?material=PMMA&limit=1000`);
    if (!response.ok) throw new Error(`HTTP error ${response.status}`);
    const data = await response.json();
    if (generation !== sweepGeneration || state.sweepMode !== 'published' ||
        scenario.material !== state.material || scenario.pressure_kpa !== state.pressure_kpa ||
        scenario.flow_cm_s !== state.flow_cm_s) return;
    const diameterMm = state.rod_radius_cm * 20;
    state.sweepObservations = (data.experiments || []).filter((row) =>
      row.investigation === 'BASS-II' && row.sample_geometry === 'rod' &&
      row.flow_direction === 'concurrent' &&
      Math.abs(row.sample_thickness_mm - diameterMm) < 0.1 &&
      Math.abs(row.pressure_kpa - scenario.pressure_kpa) < 0.05 &&
      Math.abs(row.flow_cm_s - scenario.flow_cm_s) < 0.1 &&
      row.oxygen_pct >= NASA_BOUNDARY.VALID_O2[0] &&
      row.oxygen_pct <= NASA_BOUNDARY.VALID_O2[1]);
    updateSweepPoint(parseFloat(document.getElementById('sweep-oxygen-slider')?.value || '21'));
  } catch (error) {
    if (generation !== sweepGeneration || state.sweepMode !== 'published') return;
    state.sweepObservations = [];
    state.sweepEvidenceError = 'Source observations need the backend connection.';
    updateSweepPoint(parseFloat(document.getElementById('sweep-oxygen-slider')?.value || '21'));
  }
}

function renderPublishedSweepEvidence(selectedO2) {
  const observations = state.sweepObservations;
  const count = document.getElementById('tag-above-boundary');
  const examples = document.getElementById('evidence-above-boundary');
  const note = document.getElementById('tag-below-boundary');
  const basis = document.getElementById('evidence-below-boundary');
  if (count) count.textContent = state.sweepEvidenceError
    ? 'Observations unavailable'
    : observations ? `${observations.length} concurrent-flow tests` : 'Loading observations…';
  if (examples) {
    if (!observations) examples.textContent = 'Loading matching BASS-II concurrent-flow rod tests…';
    else if (state.sweepEvidenceError) examples.textContent = state.sweepEvidenceError;
    else if (observations.length === 0) examples.textContent = `No concurrent-flow BASS-II 1/4-inch PMMA rod test at ${state.publishedSweep.flow.toFixed(1)} cm/s is recorded.`;
    else examples.innerHTML = observations
      .slice()
      .sort((a, b) => Math.abs(a.oxygen_pct - selectedO2) - Math.abs(b.oxygen_pct - selectedO2))
      .slice(0, 6)
      .map(row => `<div class="sweep-observation"><strong>${escapeHTML(row.oxygen_pct)}% initial O₂</strong><span>${escapeHTML(row.outcome)} · ${escapeHTML(row.experiment_id)}</span><a href="${escapeHTML(safeHttpUrl(row.source_url, NASA_BOUNDARY.URL))}" target="_blank" rel="noopener noreferrer" class="citation-ntrs-link">NTRS ${escapeHTML(row.report_id)} ↗</a></div>`)
      .join('');
  }
  if (note) note.textContent = 'Fit and observation fields';
  if (basis) basis.textContent = 'Eq (6.1) uses oxygen measured after burning at extinction. These test records provide initial oxygen only, so their points are shown for context and must not be read as measurements above or below the fitted boundary.';
}

function updatePublishedSweepPoint(o2Val) {
  const limit = state.publishedSweep.limitO2;
  const delta = o2Val - limit;
  const distance = document.getElementById('safety-margin-val');
  const status = document.getElementById('safety-margin-status');
  const tick = document.getElementById('tick-loc-boundary');
  if (distance) {
    distance.className = 'margin-figure published';
    distance.textContent = `${delta >= 0 ? '+' : ''}${delta.toFixed(2)} points`;
  }
  if (status) {
    status.className = 'margin-pill published';
    status.textContent = 'Not an extinction margin: NASA used post-burn O₂';
  }
  if (tick) tick.textContent = `${limit.toFixed(2)}% O₂ (NASA fit)`;
  renderPublishedSweepEvidence(o2Val);
  drawSweepCanvas(o2Val);
}

function setupSweepView() {
  const sweepSlider = document.getElementById('sweep-oxygen-slider');
  const autoBtn = document.getElementById('btn-run-auto-sweep');
  if (!sweepSlider || !autoBtn) return;

  sweepSlider.addEventListener('input', (e) => {
    let oxygen = parseFloat(e.target.value);
    if (state.sweepMode === 'model') {
      const nearest = state.sweepData.points.reduce((best, point) =>
        Math.abs(point.oxygen_pct - oxygen) < Math.abs(best.oxygen_pct - oxygen) ? point : best);
      oxygen = nearest.oxygen_pct;
      sweepSlider.value = String(oxygen);
    }
    updateSweepPoint(oxygen);
  });

  sweepSlider.addEventListener('keydown', (event) => {
    const offsets = {ArrowLeft: -1, ArrowDown: -1, ArrowRight: 1, ArrowUp: 1, PageDown: -10, PageUp: 10};
    if (state.sweepMode !== 'model' || (!(event.key in offsets) && !['Home', 'End'].includes(event.key))) return;
    event.preventDefault();
    const points = state.sweepData.points;
    const current = Number(sweepSlider.value);
    let index = points.reduce((best, point, i) => Math.abs(point.oxygen_pct - current) < Math.abs(points[best].oxygen_pct - current) ? i : best, 0);
    index = event.key === 'Home' ? 0 : event.key === 'End' ? points.length - 1 : Math.max(0, Math.min(points.length - 1, index + offsets[event.key]));
    sweepSlider.value = String(points[index].oxygen_pct);
    updateSweepPoint(points[index].oxygen_pct);
  });

  autoBtn.addEventListener('click', () => {
    if (state.sweepRunning || (!state.sweepData && state.sweepMode !== 'published')) return;
    state.sweepRunning = true;
    autoBtn.textContent = 'Sweeping oxygen…';
    const min = Number(sweepSlider.min);
    const max = Number(sweepSlider.max);
    const values = state.sweepMode === 'model'
      ? state.sweepData.points.map(point => point.oxygen_pct).slice().reverse()
      : Array.from({length: Math.round((max - min) * 10) + 1}, (_, index) => Number((max - index / 10).toFixed(1)));
    let index = 0;
    sweepSlider.value = String(values[index]);
    updateSweepPoint(values[index]);
    state.sweepInterval = setInterval(() => {
      if (!state.sweepRunning) return;
      index++;
      sweepSlider.value = String(values[index]);
      updateSweepPoint(values[index]);
      if (index === values.length - 1) {
        clearInterval(state.sweepInterval);
        state.sweepInterval = null;
        state.sweepRunning = false;
        autoBtn.textContent = '▶ Play oxygen sweep';
      }
    }, 60);
  });

}

function updateSweepPoint(o2Val) {
  const marginDisplay = document.getElementById('safety-margin-val');
  const marginStatus = document.getElementById('safety-margin-status');
  const readout = document.getElementById('readout-sweep-o2');
  if (readout) readout.textContent = `${Number(o2Val.toFixed(3))} %`;
  const sampledPoint = state.sweepData?.points.find(point => Math.abs(point.oxygen_pct - o2Val) < 0.0005);
  const hasEstimate = sampledPoint?.prediction != null && sampledPoint?.probabilities != null;
  const pointDetails = document.getElementById('sweep-point-details');
  const refusal = sampledPoint
    ? `No model estimate: ${(sampledPoint.status || 'estimate refused').replaceAll('_', ' ')}. ${sampledPoint.warning_message || ''}`
    : 'No model estimate was sampled at this oxygen value.';
  if (pointDetails) pointDetails.textContent = hasEstimate
    ? `${o2Val}% O₂ — spread: ${(sampledPoint.probabilities.spread * 100).toFixed(2)}%; ` +
      `marginal spread: ${(sampledPoint.probabilities.marginal_spread * 100).toFixed(2)}%; ` +
      `no spread: ${(sampledPoint.probabilities.no_spread * 100).toFixed(2)}%. Exploratory probabilities, not independently validated.`
    : refusal;

  if (state.sweepMode === 'published' && state.publishedSweep) {
    updatePublishedSweepPoint(o2Val);
    return;
  }

  if (!state.sweepData || (state.sweepMode !== 'model' && state.dynamicLocBoundary == null)) {
    if (marginDisplay) marginDisplay.textContent = 'N/A';
    if (marginDisplay) marginDisplay.className = 'margin-figure';
    if (marginStatus) marginStatus.textContent = state.sweepError || 'Research sweep unavailable';
    if (marginStatus) marginStatus.className = 'margin-pill';
    for (const id of ['tag-above-boundary', 'tag-below-boundary', 'tick-loc-boundary', 'evidence-above-boundary', 'evidence-below-boundary']) {
      const el = document.getElementById(id);
      if (el) el.textContent = 'Research sweep unavailable';
    }
    drawSweepCanvas(o2Val);
    return;
  }

  if (state.sweepMode === 'model' && state.dynamicLocBoundary == null) {
    if (marginDisplay) {
      marginDisplay.className = 'margin-figure';
      marginDisplay.textContent = 'N/A';
    }
    if (marginStatus) {
      marginStatus.className = 'margin-pill';
      marginStatus.textContent = hasEstimate ? 'No model transition detected between eligible adjacent samples' : refusal;
    }
    for (const id of ['tag-above-boundary', 'tag-below-boundary', 'tick-loc-boundary']) {
      const el = document.getElementById(id);
      if (el) el.textContent = 'No transition in this range';
    }
    for (const id of ['evidence-above-boundary', 'evidence-below-boundary']) {
      const el = document.getElementById(id);
      if (el) el.textContent = 'No transition-side observation applies to this sweep.';
    }
    drawSweepCanvas(o2Val);
    return;
  }

  if (marginDisplay) marginDisplay.className = 'margin-figure';

  const locBoundary = state.dynamicLocBoundary;
  const delta = o2Val - locBoundary;
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
      : refusal;
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

function drawPublishedSweepCanvas(currentO2) {
  const canvas = document.getElementById('sweep-chart-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const { width: w, height: h } = canvas;
  const [min, max] = NASA_BOUNDARY.VALID_O2;
  const left = 155;
  const right = w - 36;
  const toX = oxygen => left + ((oxygen - min) / (max - min)) * (right - left);
  const limit = state.publishedSweep.limitO2;

  ctx.clearRect(0, 0, w, h);
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, w, h);
  ctx.textAlign = 'left';
  ctx.fillStyle = '#1e293b';
  ctx.font = '13px Inter, sans-serif';
  ctx.fillText('Published extinction fit for an established flame', left, 27);
  ctx.font = '11px "Inter", monospace';
  ctx.fillStyle = '#64748b';
  ctx.fillText('No model probabilities are shown', left, 44);

  ctx.strokeStyle = '#cbd5e1';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(left, 102);
  ctx.lineTo(right, 102);
  ctx.stroke();
  ctx.textAlign = 'center';
  ctx.fillStyle = '#475569';
  [14, 16, 18, 20, 22].forEach(oxygen => {
    const x = toX(oxygen);
    ctx.strokeStyle = '#cbd5e1';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(x, 95);
    ctx.lineTo(x, 109);
    ctx.stroke();
    ctx.fillText(`${oxygen}%`, x, 126);
  });

  const limitX = toX(limit);
  ctx.strokeStyle = '#b45309';
  ctx.lineWidth = 2;
  ctx.setLineDash([5, 4]);
  ctx.beginPath();
  ctx.moveTo(limitX, 56);
  ctx.lineTo(limitX, 248);
  ctx.stroke();
  ctx.setLineDash([]);
  ctx.fillStyle = '#92400e';
  ctx.textAlign = 'left';
  ctx.fillText(`NASA fit ${limit.toFixed(2)}%`, Math.max(left + 5, limitX + 7), 69);

  const selectedX = toX(currentO2);
  ctx.strokeStyle = '#164c78';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(selectedX, 78);
  ctx.lineTo(selectedX, 113);
  ctx.stroke();
  ctx.fillStyle = '#164c78';
  ctx.beginPath();
  ctx.arc(selectedX, 102, 6, 0, Math.PI * 2);
  ctx.fill();
  ctx.textAlign = selectedX > right - 100 ? 'right' : 'left';
  ctx.fillText(`Selected ${currentO2.toFixed(1)}%`, selectedX > right - 100 ? selectedX - 8 : selectedX + 8, 85);

  ctx.textAlign = 'left';
  ctx.fillStyle = '#475569';
  ctx.fillText('Concurrent-flow BASS-II tests · initial O₂ at test start (context only)', left, 158);
  const rowY = { spread: 184, marginal_spread: 210, no_spread: 236 };
  const rowLabel = { spread: 'Spread', marginal_spread: 'Marginal', no_spread: 'No spread' };
  const rowColor = { spread: '#dc2626', marginal_spread: '#d97706', no_spread: '#059669' };
  Object.keys(rowY).forEach(outcome => {
    ctx.textAlign = 'right';
    ctx.fillStyle = '#475569';
    ctx.fillText(rowLabel[outcome], left - 12, rowY[outcome] + 4);
    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(left, rowY[outcome]);
    ctx.lineTo(right, rowY[outcome]);
    ctx.stroke();
  });

  const observations = state.sweepObservations;
  if (observations?.length) {
    observations.forEach((row, index) => {
      const y = rowY[row.outcome];
      if (y == null) return;
      ctx.beginPath();
      ctx.arc(toX(row.oxygen_pct), y + (index % 3 - 1) * 3, 4, 0, Math.PI * 2);
      ctx.fillStyle = rowColor[row.outcome];
      ctx.fill();
    });
  } else {
    ctx.textAlign = 'center';
    ctx.fillStyle = '#64748b';
    ctx.fillText(state.sweepEvidenceError || (observations ? 'No matching observations at this flow.' : 'Loading matching observations…'), (left + right) / 2, 211);
  }
  ctx.textAlign = 'center';
  ctx.fillStyle = '#64748b';
  ctx.fillText('Initial oxygen concentration at test start (% by volume)', (left + right) / 2, h - 8);
}

// Draw Probability vs O2 Curve Canvas for exploratory model output.
function drawSweepCanvas(currentO2 = 21.0) {
  if (state.sweepMode === 'published' && state.publishedSweep) {
    drawPublishedSweepCanvas(currentO2);
    return;
  }
  const canvas = document.getElementById('sweep-chart-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;

  ctx.clearRect(0, 0, w, h);
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, w, h);

  if (!state.sweepData) {
    ctx.fillStyle = '#64748b';
    ctx.font = '13px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('No model estimates available. See the sweep status above.', w / 2, h / 2);
    return;
  }

  const padLeft = 70;
  const padBottom = 40;
  const padTop = 30;
  const padRight = 40;
  const pW = w - padLeft - padRight;
  const pH = h - padTop - padBottom;

  const [min, max] = state.sweepData.range;
  const toX = oxygen => padLeft + ((oxygen - min) / (max - min)) * pW;
  const toY = probability => padTop + pH * (1 - probability);
  ctx.font = '13px Inter, sans-serif';
  ctx.textAlign = 'right';
  for (const probability of [0, 0.25, 0.5, 0.75, 1]) {
    const y = toY(probability);
    ctx.strokeStyle = '#e2e8f0';
    ctx.beginPath(); ctx.moveTo(padLeft, y); ctx.lineTo(padLeft + pW, y); ctx.stroke();
    ctx.fillStyle = '#475569';
    ctx.fillText(`${probability * 100}%`, padLeft - 10, y + 4);
  }
  ctx.textAlign = 'left';
  ctx.fillText('Model probability', padLeft, 18);

  const locBoundary = state.dynamicLocBoundary;
  if (locBoundary != null) {
    const boundaryX = toX(locBoundary);
    ctx.strokeStyle = '#b45309';
    ctx.setLineDash([4, 4]);
    ctx.beginPath(); ctx.moveTo(boundaryX, padTop); ctx.lineTo(boundaryX, padTop + pH); ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = '#92400e';
    ctx.fillText(`Model transition (${locBoundary.toFixed(2)}%)`, Math.min(boundaryX + 8, padLeft + pW - 210), padTop + 16);
  }

  const pts = state.sweepData.points;
  const selected = pts.find(point => Math.abs(point.oxygen_pct - currentO2) < 0.0005);
  // Each refused sample breaks the line; its probability is unknown, not zero.
  for (const [key, color, dash] of [
    ['spread', '#b91c1c', []],
    ['marginal_spread', '#b45309', [7, 4]],
    ['no_spread', '#047857', [2, 4]]
  ]) {
    ctx.strokeStyle = color;
    ctx.lineWidth = 2.4;
    ctx.setLineDash(dash);
    ctx.beginPath();
    let drawing = false;
    for (const point of pts) {
      const probability = point.prediction == null ? null : point.probabilities?.[key];
      if (typeof probability !== 'number' || !Number.isFinite(probability)) {
        drawing = false;
        continue;
      }
      const x = toX(point.oxygen_pct), y = toY(probability);
      if (drawing) ctx.lineTo(x, y);
      else ctx.moveTo(x, y);
      drawing = true;
    }
    ctx.stroke();
    ctx.setLineDash([]);
    const probability = selected?.prediction == null ? null : selected?.probabilities?.[key];
    if (typeof probability === 'number' && Number.isFinite(probability)) {
      ctx.beginPath(); ctx.arc(toX(currentO2), toY(probability), 4, 0, Math.PI * 2);
      ctx.fillStyle = color; ctx.fill();
    }
  }

  ctx.strokeStyle = '#334155';
  ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(toX(currentO2), padTop); ctx.lineTo(toX(currentO2), padTop + pH); ctx.stroke();
  ctx.fillStyle = '#475569';
  ctx.textAlign = 'center';
  for (let index = 0; index <= 5; index++) {
    const oxygen = min + (max - min) * index / 5;
    ctx.fillText(`${Number(oxygen.toFixed(2))}%`, toX(oxygen), padTop + pH + 20);
  }
  ctx.fillText('Oxygen concentration (% by volume)', padLeft + pW / 2, h - 4);
}

// Atlas Table Setup & Data Loading
async function setupAtlasView() {
  const searchInput = document.getElementById('atlas-search-input');
  const matFilter = document.getElementById('atlas-filter-material');
  const outFilter = document.getElementById('atlas-filter-outcome');
  if (!searchInput || !matFilter || !outFilter) return;

  try {
    const res = await fetch(`${API_BASE}/experiments?limit=1000`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const data = await res.json();
    state.experiments = data.experiments;
    renderAtlasTable(state.experiments);
  } catch (err) {
    console.warn('Could not load experiments from API:', err);
    const count = document.getElementById('atlas-count');
    if (count) count.textContent = 'Observations unavailable. Start the local service and reload.';
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
  const count = document.getElementById('atlas-count');
  if (count) count.textContent = `${rows.length} of ${state.experiments.length} observations shown`;

  if (rows.length === 0) {
    tbody.innerHTML = '<tr><td colspan="9">No observations match these filters. Clear the search or choose another material or outcome.</td></tr>';
  }
  rows.forEach(r => {
    const tr = document.createElement('tr');
    const badgeClass = r.outcome === 'spread' ? 'badge-spread' : (r.outcome === 'marginal_spread' ? 'badge-marginal' : 'badge-no-spread');
    const citeUrl = r.source_url || `https://ntrs.nasa.gov/citations/${r.report_id}`;

    tr.innerHTML = `
      <td><button type="button" class="archive-probe" title="Inspect these conditions in the flammability deck">${escapeHTML(r.experiment_id)}</button></td>
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
    state.modelMeta = meta;
    if (currentEvidence && !currentEvidence.dataset_sha256) currentEvidence.dataset_sha256 = meta.dataset_sha256 || null;
    const percent = value => `${(value * 100).toFixed(1)}%`;

    state.materialCounts = Object.fromEntries(
      Object.entries(meta.training_range?.per_material || {}).map(([material, details]) => [material, details.n_samples])
    );
    updateMaterialInfo();

    setText('nav-experiment-count', String(meta.n_train));
    setText('chip-n-train', `${meta.n_train} observations`);
    setText('model-kpi-accuracy', percent(meta.cv_accuracy));
    setText('model-kpi-baseline', percent(meta.majority_baseline_accuracy));
    setText('model-kpi-balanced', percent(meta.cv_balanced_accuracy));
    setText('model-kpi-samples', String(meta.n_train));
    setText('model-kpi-nested', meta.nested_search ? percent(meta.nested_search.accuracy) : 'Unavailable');
    setText('model-validation-note', meta.research_warning || meta.cv_caveat || 'Independent external validation is unavailable.');
    setText('model-fold-heading', `${meta.loro?.n_groups || meta.cv_fold_sizes?.length || 'Report'}-fold report-grouped confusion matrix`);
    setText('dataset-sha', meta.dataset_sha256
      ? `${meta.dataset_sha256.slice(0, 8)}…${meta.dataset_sha256.slice(-8)}`
      : 'Unavailable');
    setText('model-kpi-comparison', health.model_readiness_reason || 'Model readiness unavailable');
    setText('integrity-text', 'Deterministic templates with number and citation checks; scientific interpretation still requires source review. No independent model validation or safety certification.');
    setText('chip-model-type', meta.type === 'linear_svm' ? 'Linear SVM' : meta.type === 'gradient_boosting' ? 'Gradient Boosting' : meta.type || 'Unavailable');
    if (!state.connectionError) {
      setText('status-text', `${meta.n_train} observations · ${health.model_ready ? 'Research model available' : 'Model inference withheld'}`);
      setText('model-gate-text', health.model_ready ? 'RESEARCH ESTIMATES' : 'VALIDATION REQUIRED');
      const dot = document.getElementById('status-dot');
      if (dot) dot.className = `heartbeat-pulse ${health.model_ready ? 'status-ready' : 'status-withheld'}`;
      const gate = document.getElementById('model-gate-text');
      if (gate) gate.className = health.model_ready ? 'metric-status-ready' : 'metric-status-withheld';
    }

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
    state.connectionError = true;
    setText('status-text', currentEvidence ? 'Evidence online · research model unavailable' : 'Backend unavailable · published PMMA boundary only');
    setText('model-gate-text', currentEvidence ? 'MODEL UNAVAILABLE' : 'SERVICE OFFLINE');
    const dot = document.getElementById('status-dot');
    if (dot) dot.className = 'heartbeat-pulse status-offline';
    const gate = document.getElementById('model-gate-text');
    if (gate) gate.className = 'metric-status-offline';
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
        data.investigations.forEach(inv => {
          const div = document.createElement('div');
          div.className = 'investigation-card';
          div.innerHTML = `
            <div class="inv-title">${escapeHTML(inv.exact_nasa_title || inv.investigation_key || 'NASA Investigation')}</div>
            <div class="inv-meta">
              PSI ID: <strong>${escapeHTML(inv.psi_id || 'N/A')}</strong> · Catalog role: <strong>${inv.usable_for_prototype_model === 'YES' ? 'Candidate data source' : 'Reference catalog'}</strong>
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

let conflictGeneration = 0;
async function executeConflictAnalysis(studyA, studyB) {
  const generation = ++conflictGeneration;
  const status = document.getElementById('conflict-status');
  const results = document.getElementById('conflict-results-container');
  if (status) status.textContent = 'Comparing the selected studies…';
  if (results) results.hidden = true;
  try {
    const res = await fetch(`${API_BASE}/api/conflict/compare-studies`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ study_a: studyA, study_b: studyB })
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const data = await res.json();
    if (generation !== conflictGeneration) return;
    renderConflictResults(data);
    if (results) results.hidden = false;
    if (status) status.textContent = '';
  } catch (err) {
    if (generation !== conflictGeneration) return;
    console.warn('Conflict analysis request failed:', err);
    if (status) status.textContent = 'Comparison unavailable. Check the backend connection and try again.';
  }
}

function renderConflictResults(data) {
  const scoreVal = document.getElementById('conflict-score-val');
  const badge = document.getElementById('conflict-verdict-badge');
  const summary = document.getElementById('conflict-verdict-summary');
  const caution = document.getElementById('conflict-caution-text');
  const tbody = document.getElementById('conflict-dimensions-tbody');
  const reconcile = document.getElementById('conflict-reconciliation-text');

  if (scoreVal) scoreVal.textContent = `${data.matching_dimensions ?? '—'} / ${data.dimensions?.length ?? '—'}`;
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
      const statusClass = dim.status === 'MATCH' ? 'status-match' : (dim.status === 'UNKNOWN' ? 'status-mod' : 'status-mismatch');
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
  const status = document.getElementById('coverage-status');
  if (status) status.textContent = 'Loading coverage data…';
  try {
    const res = await fetch(`${API_BASE}/api/coverage-map`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const data = await res.json();
    renderCoverageMap(data);
    if (status) status.textContent = '';
  } catch (err) {
    console.warn('Coverage map fetch failed:', err);
    if (status) status.textContent = 'Coverage data unavailable. Check the backend connection and try again.';
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
        const density = cell ? cell.density : 'NO_INDEXED_OBSERVATIONS';
        const swatchClass = density === 'HIGH' ? 'swatch-high' : (density === 'MODERATE' ? 'swatch-mod' : (density === 'SPARSE' ? 'swatch-sparse' : 'swatch-gap'));
        const mats = (cell && cell.materials && cell.materials.length > 0) ? cell.materials.join(', ') : 'None';
        const tooltip = count === 0 ? 'No matching observations in the current FLARE-X dataset'
          : `Indexed: ${count} runs | Materials: ${mats} | Spread: ${cell?.spread_count || 0}, Marginal: ${cell?.marginal_count || 0}, No spread: ${cell?.no_spread_count || 0}`;

        html += `
          <td class="heatmap-cell ${swatchClass}" title="${escapeHTML(tooltip)}">
            <div class="cell-inner">
              <span class="cell-count">${escapeHTML(count)}</span>
              <span class="cell-density-tag">${count === 0 ? 'NO INDEXED DATA' : escapeHTML(density)}</span>
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
          <span class="gap-risk-pill">TEAM PROPOSAL</span>
        </div>
        <h4 class="gap-title">${escapeHTML(gap.title)}</h4>
        <div class="gap-regime-strip"><strong>Target Regime:</strong> ${escapeHTML(gap.regime)}</div>
        <div class="gap-materials"><strong>Proposed Materials:</strong> ${escapeHTML((gap.materials_affected || []).join(', '))}</div>
        <div class="gap-section">
          <span class="gap-section-label">INDEXED COVERAGE:</span>
          <p class="gap-text">${escapeHTML(gap.coverage_statement)}</p>
          <p class="gap-text">${escapeHTML(Object.entries(gap.material_counts || {}).map(([mat, count]) => `${mat}: ${count}`).join(' · '))}</p>
        </div>
        <div class="gap-section">
          <span class="gap-section-label">SCIENTIFIC RATIONALE:</span>
          <p class="gap-text">${escapeHTML(gap.scientific_rationale)}</p>
        </div>
        <div class="gap-recommended-box">
          <span class="rec-label">TEAM-PROPOSED FOLLOW-UP STUDY:</span>
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

let inspectorTrigger = null;
let citationGeneration = 0;
function setupCitationInspector() {
  const closeBtn = document.getElementById('btn-close-inspector');
  const backdrop = document.getElementById('modal-backdrop-close');
  const modal = document.getElementById('modal-citation-inspector');

  const hide = () => {
    ++citationGeneration;
    if (modal) modal.classList.add('hidden');
    if (inspectorTrigger?.isConnected) inspectorTrigger.focus();
  };

  if (closeBtn) closeBtn.addEventListener('click', hide);
  if (backdrop) backdrop.addEventListener('click', hide);
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && modal && !modal.classList.contains('hidden')) hide();
    if (event.key === 'Tab' && modal && !modal.classList.contains('hidden')) {
      const focusable = Array.from(modal.querySelectorAll('button, a[href]')).filter(el => !el.hidden && !el.disabled);
      const first = focusable[0], last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
    }
  });
}

window.inspectProvenance = async function(experimentId) {
  const modal = document.getElementById('modal-citation-inspector');
  if (!modal) return;
  inspectorTrigger = document.activeElement;
  const generation = ++citationGeneration;

  try {
    const res = await fetch(`${API_BASE}/api/provenance/${encodeURIComponent(experimentId)}`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const data = await res.json();
    if (generation !== citationGeneration) return;

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
    if (reportTitleEl) reportTitleEl.textContent = data.report_title || `NTRS record ${data.report_id}`;
    if (citeEl) citeEl.textContent = data.exact_source_citation || `NASA Report ${data.report_id}`;
    if (invEl) invEl.textContent = `${data.investigation} · Environment: ${String(data.investigation).startsWith('Saffire-') ? 'Cygnus orbital spacecraft' : data.gravity_env || 'Not recorded'}`;
    if (condEl) condEl.textContent = `${data.material} · ${data.oxygen_pct}% O₂ · ${data.pressure_kpa} kPa · ${data.flow_cm_s} cm/s forced flow`;
    if (outcomeEl) outcomeEl.textContent = `${data.outcome} (${data.extraction_notes || 'Observed flame behavior'})`;
    if (notesEl) notesEl.textContent = data.extraction_notes || 'No extraction notes recorded; consult the original source.';
    document.getElementById('inspect-sample-context').textContent =
      `${data.sample_geometry || 'Geometry not recorded'} · ${data.sample_thickness_mm == null ? 'Thickness not recorded' : `${data.sample_thickness_mm} mm`} · ${data.flow_direction || 'Flow direction not recorded'}`;
    document.getElementById('inspect-observation').textContent = data.outcome_raw || 'Source observation text is not recorded.';
    if (ntrsUrlEl) {
      ntrsUrlEl.href = safeHttpUrl(data.source_url || `https://ntrs.nasa.gov/citations/${encodeURIComponent(data.report_id || '')}`, 'https://ntrs.nasa.gov/');
      ntrsUrlEl.hidden = false;
    }
    if (tierPill) tierPill.textContent = data.verification_tier || 'VERIFICATION NOT RECORDED';
    if (originPill) originPill.textContent = data.data_origin || 'ORIGIN NOT RECORDED';

    modal.classList.remove('hidden');
    document.getElementById('btn-close-inspector')?.focus();
  } catch (err) {
    if (generation !== citationGeneration) return;
    console.warn('Could not inspect provenance:', err);
    document.getElementById('inspect-exp-id').textContent = 'Citation unavailable';
    for (const id of ['inspect-report-title', 'inspect-citation', 'inspect-investigation', 'inspect-conditions', 'inspect-outcome', 'inspect-sample-context', 'inspect-observation']) {
      document.getElementById(id).textContent = '—';
    }
    document.getElementById('inspect-notes').textContent = 'Could not load this citation. Check the backend connection and try again.';
    document.getElementById('inspect-tier-pill').textContent = 'VERIFICATION UNAVAILABLE';
    document.getElementById('inspect-origin-pill').textContent = 'ORIGIN UNAVAILABLE';
    document.getElementById('inspect-ntrs-url').hidden = true;
    modal.classList.remove('hidden');
    document.getElementById('btn-close-inspector')?.focus();
  }
};

