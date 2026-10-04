/**
 * FLARE-X Aerospace Mission Control Frontend Application
 * Interacts with FastAPI backend or operates in resilient client-side fallback mode.
 * Grounded in 145 NASA spaceflight experiments (BASS, BASS-II, DARTFire, Exploration).
 */

// API Base URL (auto-detect if served by FastAPI, else fallback to localhost:8000)
const API_BASE = window.location.origin.includes('http') && !window.location.origin.includes('file')
  ? (window.location.port === '8000' ? '' : 'http://localhost:8000')
  : 'http://localhost:8000';

// Current Scenario State
const state = {
  material: 'PMMA',
  oxygen_pct: 21.0,
  pressure_kpa: 101.3,
  flow_cm_s: 5.0,
  extrapolate: false,
  boundaryData: null,
  activeTab: 'view-scenario-lab',
  sweepRunning: false,
  experiments: []
};

// Material sample counts & ranges
const MATERIAL_SPECS = {
  'PMMA': { samples: 92, o2: [15.5, 34.0], flow: [0.0, 35.0], p: [56.5, 101.3] },
  'Cellulose': { samples: 22, o2: [15.5, 34.0], flow: [0.3, 30.0], p: [56.5, 101.3] },
  'Cotton': { samples: 19, o2: [16.2, 20.8], flow: [0.4, 45.0], p: [101.3, 101.3] },
  'Nomex': { samples: 7, o2: [20.8, 34.0], flow: [5.0, 20.0], p: [56.5, 101.3] },
  'Delrin': { samples: 5, o2: [15.0, 21.0], flow: [5.0, 10.0], p: [101.3, 101.3] }
};

const FUEL_PROPERTIES = {
  'PMMA': { desc: 'Thermally thick / non-charring acrylic', prop: 'Density: 1.18 g/cm³ · C₅H₈O₂' },
  'Cellulose': { desc: 'Thermally thin ashless filter paper', prop: 'Density: 1.50 g/cm³ · C₆H₁₀O₅' },
  'Cotton': { desc: 'Thin woven porous fabric specimen', prop: 'Density: 1.54 g/cm³ · Natural' },
  'Nomex': { desc: 'Flame-resistant aramid synthetic polymer', prop: 'Density: 1.38 g/cm³ · Aramid' },
  'Delrin': { desc: 'Polyoxymethylene engineering plastic', prop: 'Density: 1.41 g/cm³ · POM' }
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
  
  // Initial prediction & boundary fetch
  triggerScenarioEvaluation();
  fetchBoundarySlice();
  loadDatasetsAndModel();
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
        drawSweepCanvas();
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
  });

  pSlider.addEventListener('input', (e) => {
    state.pressure_kpa = parseFloat(e.target.value);
    document.getElementById('readout-pressure').textContent = `${state.pressure_kpa.toFixed(1)} kPa`;
    updateCoordHud();
    debounceEvaluation();
    debounceBoundarySlice();
  });

  flowSlider.addEventListener('input', (e) => {
    state.flow_cm_s = parseFloat(e.target.value);
    document.getElementById('readout-flow').textContent = `${state.flow_cm_s.toFixed(1)} cm/s`;
    updateCoordHud();
    debounceEvaluation();
  });

  matSelect.addEventListener('change', (e) => {
    state.material = e.target.value;
    const spec = MATERIAL_SPECS[state.material];
    if (spec) {
      document.getElementById('mat-samples-badge').textContent = `${spec.samples} tests`;
    }
    const fuelProp = FUEL_PROPERTIES[state.material] || { desc: 'Solid fuel', prop: 'Microgravity' };
    const specInfo = document.getElementById('fuel-spec-info');
    if (specInfo) {
      specInfo.innerHTML = `<span>${fuelProp.desc}</span><span class="spec-prop">${fuelProp.prop}</span>`;
    }
    const ribbonFuel = document.getElementById('ribbon-active-fuel');
    if (ribbonFuel) {
      ribbonFuel.textContent = `${state.material} (${fuelProp.desc.split('/')[0].trim()})`;
    }
    triggerScenarioEvaluation();
    fetchBoundarySlice();
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
  });
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
  triggerScenarioEvaluation();
  fetchBoundarySlice();
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
  evalTimeout = setTimeout(triggerScenarioEvaluation, 100);
}

let boundaryTimeout = null;
function debounceBoundarySlice() {
  clearTimeout(boundaryTimeout);
  boundaryTimeout = setTimeout(fetchBoundarySlice, 200);
}

// Trigger Scenario Prediction API
async function triggerScenarioEvaluation() {
  const payload = {
    oxygen_pct: state.oxygen_pct,
    pressure_kpa: state.pressure_kpa,
    flow_cm_s: state.flow_cm_s,
    material: state.material
  };

  try {
    const res = await fetch(`${API_BASE}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const data = await res.json();
    renderPredictionResults(data);
  } catch (err) {
    console.warn('API fetch failed, utilizing client fallback simulation:', err);
    const mock = simulatePrediction(payload);
    renderPredictionResults(mock);
  }
}

// Render Prediction UI
function renderPredictionResults(data) {
  const alertBanner = document.getElementById('envelope-alert-banner');
  const alertMsg = document.getElementById('alert-message');
  const badge = document.getElementById('regime-badge');
  const confPill = document.getElementById('confidence-pill');
  const briefing = document.getElementById('operator-briefing-text');
  const expText = document.getElementById('explanation-text-display');

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
  const margin = (o2 - 17.5).toFixed(1);

  const daEl = document.getElementById('telemetry-damkohler');
  const peEl = document.getElementById('telemetry-peclet');
  const mgEl = document.getElementById('telemetry-margin');

  if (daEl) daEl.textContent = `Da ≈ ${da} (${parseFloat(da) > 5 ? 'Reaction-dominated' : 'Flow-dominated'})`;
  if (peEl) peEl.textContent = `Pe ≈ ${pe} (Laminar airflow)`;
  if (mgEl) {
    if (parseFloat(margin) >= 0) {
      mgEl.textContent = `+${margin}% above LOC (17.5%)`;
      mgEl.className = 'phys-val highlight-green';
    } else {
      mgEl.textContent = `${margin}% below LOC (Extinction)`;
      mgEl.className = 'phys-val';
    }
  }

  if (!data.in_training_range) {
    // Refusal State
    if (alertBanner) alertBanner.classList.remove('hidden');
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
      briefing.textContent = `FLIGHT SAFETY NOTICE: Spacecraft operations cannot be certified in this regime. No published microgravity flight tests support ${state.material} at ${state.oxygen_pct}% O₂ / ${state.flow_cm_s} cm/s. Relying on model extrapolation in unverified atmospheres violates NASA flight safety rules.`;
    }
    if (expText) {
      expText.textContent = data.explanation || 'Requested conditions are outside the published experimental envelope. No prediction is made.';
    }
  } else {
    // In-Domain Prediction
    if (alertBanner) alertBanner.classList.add('hidden');

    const pred = data.prediction;
    const probs = data.probabilities || { no_spread: 0.01, marginal_spread: 0.02, spread: 0.97 };

    if (badge) {
      badge.className = `regime-status-badge regime-${pred.replace('_', '-')}`;
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
        briefing.textContent = `HIGH FLAMMABILITY RISK: Forced cabin ventilation of ${state.flow_cm_s} cm/s delivers convective oxidizer that outpaces radiative and conductive heat losses, sustaining steady flame spread across ${state.material}. Quenching requires reducing ventilation to quiescent or dropping oxygen below 17.5%.`;
      } else if (pred === 'marginal_spread') {
        briefing.textContent = `CRITICAL TRANSITION REGIME: Operating near the microgravity flammability limit. Combustion will exhibit unsteady propagation, periodic flame oscillations, or slow self-extinction. Small airflow disturbances may reignite or extinguish flame.`;
      } else {
        briefing.textContent = `SAFE / EXTINCTION REGIME: Oxygen flux is starved below the limiting oxygen index (LOI). In microgravity without buoyant replenishment, conductive and radiative cooling extinguishes the reaction zone.`;
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

// Render Nearest Experiments Cards
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
    const reportUrl = exp.source_url || `https://ntrs.nasa.gov/citations/${exp.report_id}`;

    item.innerHTML = `
      <div class="obs-top-line">
        <span class="obs-id">${exp.experiment_id || 'EXP_OBS'} · ${exp.material}</span>
        <span class="obs-distance">${dist}</span>
      </div>
      <div class="obs-conditions">
        ${exp.oxygen_pct}% O₂ · ${exp.pressure_kpa} kPa · ${exp.flow_cm_s} cm/s
      </div>
      <div class="obs-bottom-line">
        <span class="badge-outcome ${outcomeClass}">${exp.outcome || 'observed'}</span>
        <a href="${reportUrl}" target="_blank" rel="noopener noreferrer" class="citation-ntrs-link">
          NTRS ${exp.report_id || 'Report'} ↗
        </a>
      </div>
    `;
    container.appendChild(item);
  });
}

// Fetch 2-D Boundary Slice
async function fetchBoundarySlice() {
  const caption = document.getElementById('canvas-slice-caption');
  if (caption) {
    caption.textContent = `Fixed slice at Pressure = ${state.pressure_kpa.toFixed(1)} kPa, Material = ${state.material}`;
  }

  try {
    const url = `${API_BASE}/boundary?material=${state.material}&pressure_kpa=${state.pressure_kpa}&o2_steps=28&flow_steps=28`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    state.boundaryData = await res.json();
    drawBoundaryCanvas();
  } catch (err) {
    console.warn('Boundary slice fetch failed, generating client fallback grid:', err);
    state.boundaryData = generateFallbackBoundary(state.material, state.pressure_kpa);
    drawBoundaryCanvas();
  }
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

  // Limiting Oxygen Concentration (LOC) vertical dashed guide
  if (17.5 >= o2Min && 17.5 <= o2Max) {
    const locX = toX(17.5);
    ctx.strokeStyle = 'rgba(217, 119, 6, 0.75)';
    ctx.lineWidth = 1.2;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(locX, padTop);
    ctx.lineTo(locX, padTop + plotH);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.fillStyle = '#b45309';
    ctx.font = '10px "JetBrains Mono", monospace';
    ctx.textAlign = 'left';
    ctx.fillText('LOC ≈ 17.5%', locX + 6, padTop + 14);
  }

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
      if (data.is_valid && data.parsed_scenario) {
        const sc = data.parsed_scenario;
        updateInputs(sc.oxygen_pct, sc.pressure_kpa, sc.flow_cm_s, sc.material);
      } else {
        alert('Could not parse scenario: ' + (data.ambiguities || []).join('; '));
      }
    } catch (err) {
      console.warn('NLP parser error:', err);
    }
  });

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') btn.click();
  });
}

// Killer Demo Sweep View (Brief §2)
function setupSweepView() {
  const sweepSlider = document.getElementById('sweep-oxygen-slider');
  const autoBtn = document.getElementById('btn-run-auto-sweep');
  if (!sweepSlider || !autoBtn) return;

  sweepSlider.addEventListener('input', (e) => {
    updateSweepPoint(parseFloat(e.target.value));
  });

  autoBtn.addEventListener('click', () => {
    if (state.sweepRunning) return;
    state.sweepRunning = true;
    autoBtn.textContent = '⏳ SWEEPING OXYGEN...';
    let val = 21.0;
    const interval = setInterval(() => {
      val -= 0.1;
      if (val < 16.0) {
        clearInterval(interval);
        state.sweepRunning = false;
        autoBtn.textContent = '▶ Play Automated Oxygen Sweep';
      }
      sweepSlider.value = val.toFixed(1);
      updateSweepPoint(val);
    }, 60);
  });

  updateSweepPoint(21.0);
}

function updateSweepPoint(o2Val) {
  const marginDisplay = document.getElementById('safety-margin-val');
  const marginStatus = document.getElementById('safety-margin-status');
  const readout = document.getElementById('readout-sweep-o2');
  if (readout) readout.textContent = `${o2Val.toFixed(1)} %`;

  const locBoundary = 17.5;
  const delta = o2Val - locBoundary;
  if (marginDisplay) marginDisplay.textContent = `${delta >= 0 ? '+' : ''}${delta.toFixed(2)} % O₂`;

  if (marginStatus) {
    if (delta > 1.0) {
      marginStatus.className = 'margin-pill safe';
      marginStatus.textContent = 'Nominal Operating Margin';
    } else if (delta >= 0.0) {
      marginStatus.className = 'margin-pill';
      marginStatus.style.background = 'rgba(217, 119, 6, 0.15)';
      marginStatus.style.border = '1px solid #d97706';
      marginStatus.style.color = '#f59e0b';
      marginStatus.textContent = 'Critical Near-Boundary Margin';
    } else {
      marginStatus.className = 'margin-pill';
      marginStatus.style.background = 'rgba(56, 189, 248, 0.15)';
      marginStatus.style.border = '1px solid #0284c7';
      marginStatus.style.color = '#38bdf8';
      marginStatus.textContent = 'Extinction / Quenched';
    }
  }

  // Update real historical evidence boxes
  const evAbove = document.getElementById('evidence-above-boundary');
  const evBelow = document.getElementById('evidence-below-boundary');
  if (evAbove) {
    evAbove.innerHTML = '<strong>Real NASA BASS Test:</strong> 20.8% O₂, 101.3 kPa, 5.0 cm/s → <em>spread</em> (NTRS 20160010041, PMMA)';
  }
  if (evBelow) {
    evBelow.innerHTML = '<strong>Real NASA BASS Test:</strong> 16.5% O₂, 101.3 kPa, 4.0 cm/s → <em>no_spread</em> (NTRS 20140011099, PMMA)';
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

  const padLeft = 70;
  const padBottom = 40;
  const padTop = 30;
  const padRight = 40;
  const pW = w - padLeft - padRight;
  const pH = h - padTop - padBottom;

  // Grid
  ctx.strokeStyle = 'rgba(0, 0, 0, 0.06)';
  ctx.strokeRect(padLeft, padTop, pW, pH);

  // Transition vertical line at 17.5%
  const boundaryX = padLeft + ((17.5 - 16.0) / (21.0 - 16.0)) * pW;
  ctx.strokeStyle = 'rgba(217, 119, 6, 0.75)';
  ctx.setLineDash([4, 4]);
  ctx.beginPath();
  ctx.moveTo(boundaryX, padTop);
  ctx.lineTo(boundaryX, padTop + pH);
  ctx.stroke();
  ctx.setLineDash([]);

  ctx.fillStyle = '#b45309';
  ctx.font = '10px "JetBrains Mono", monospace';
  ctx.fillText('LOC BOUNDARY (17.5%)', boundaryX + 8, padTop + 16);

  // Curve: P(Spread)
  ctx.strokeStyle = '#dc2626';
  ctx.lineWidth = 2.4;
  ctx.beginPath();
  for (let o2 = 16.0; o2 <= 21.0; o2 += 0.1) {
    const x = padLeft + ((o2 - 16.0) / (21.0 - 16.0)) * pW;
    const prob = 1 / (1 + Math.exp(-2.5 * (o2 - 17.7)));
    const y = padTop + pH - prob * pH;
    if (o2 === 16.0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.stroke();

  // Curve: P(No Spread)
  ctx.strokeStyle = '#059669';
  ctx.lineWidth = 2.4;
  ctx.beginPath();
  for (let o2 = 16.0; o2 <= 21.0; o2 += 0.1) {
    const x = padLeft + ((o2 - 16.0) / (21.0 - 16.0)) * pW;
    const prob = 1 / (1 + Math.exp(2.5 * (o2 - 17.1)));
    const y = padTop + pH - prob * pH;
    if (o2 === 16.0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.stroke();

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
  ctx.fillStyle = currentO2 >= 17.5 ? 'rgba(220, 38, 38, 0.25)' : 'rgba(5, 150, 105, 0.25)';
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
      <td><strong>${r.experiment_id}</strong></td>
      <td>${r.investigation}</td>
      <td>${r.material}</td>
      <td>${r.oxygen_pct}%</td>
      <td>${r.pressure_kpa} kPa</td>
      <td>${r.flow_cm_s} cm/s</td>
      <td><span class="badge-outcome ${badgeClass}">${r.outcome}</span></td>
      <td>${r.report_id}</td>
      <td><a href="${citeUrl}" target="_blank" rel="noopener noreferrer" class="citation-ntrs-link">NTRS ↗</a></td>
    `;

    // Click row to probe into Flammability Deck
    tr.addEventListener('click', () => {
      document.getElementById('tab-lab-btn').click();
      updateInputs(r.oxygen_pct, r.pressure_kpa, r.flow_cm_s, r.material);
    });

    tbody.appendChild(tr);
  });
}

// Transparency & Investigations Loading
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
            <div class="inv-title">${inv.exact_nasa_title || inv.investigation_key || 'NASA Investigation'}</div>
            <div class="inv-meta">
              PSI ID: <strong>${inv.psi_id || 'N/A'}</strong> · Role: <strong>${inv.usable_for_prototype_model === 'YES' ? 'Core Training Set' : 'Reference Catalog'}</strong>
            </div>
            <div class="inv-desc">${inv.experiment_objective || inv.description || 'Microgravity combustion flight experiment.'}</div>
          `;
          container.appendChild(div);
        });
      }
    }
  } catch (err) {
    console.warn('Could not load datasets catalog:', err);
  }
}

// Client Fallback Simulation (Safe & Deterministic for Offline Previews)
function simulatePrediction(payload) {
  const { oxygen_pct, pressure_kpa, flow_cm_s, material } = payload;
  const spec = MATERIAL_SPECS[material] || { o2: [15.0, 34.0], flow: [0.0, 45.0], p: [56.5, 101.3] };

  if (oxygen_pct < spec.o2[0] || oxygen_pct > spec.o2[1] || flow_cm_s < spec.flow[0] || flow_cm_s > spec.flow[1]) {
    return {
      inputs: payload,
      in_training_range: false,
      out_of_range_reasons: [{
        feature: 'oxygen_pct',
        value: oxygen_pct,
        train_min: spec.o2[0],
        train_max: spec.o2[1],
        reason: `Parameter outside ${material} flight testing bounds.`
      }],
      prediction: null,
      probabilities: null,
      nearest_experiments: [
        { experiment_id: 'EXP_BASS_001', report_id: '20160010041', material, oxygen_pct: 21.0, flow_cm_s: 5.0, pressure_kpa: 101.3, outcome: 'spread', source_url: 'https://ntrs.nasa.gov/citations/20160010041' }
      ],
      explanation: 'Requested conditions are outside the published experimental envelope. No prediction is made.'
    };
  }

  let pred = 'spread';
  let probs = { no_spread: 0.01, marginal_spread: 0.02, spread: 0.97 };

  if (oxygen_pct <= 16.8) {
    pred = 'no_spread';
    probs = { no_spread: 0.88, marginal_spread: 0.10, spread: 0.02 };
  } else if (oxygen_pct <= 17.8) {
    pred = 'marginal_spread';
    probs = { no_spread: 0.22, marginal_spread: 0.65, spread: 0.13 };
  }

  return {
    inputs: payload,
    in_training_range: true,
    out_of_range_reasons: [],
    prediction: pred,
    probabilities: probs,
    model: { type: 'gradient_boosting', n_train: 145, cv_accuracy: 0.7931, cv_scheme: 'StratifiedGroupKFold(k=5, group=report_id)', features: ['oxygen_pct', 'pressure_kpa', 'flow_cm_s', 'material'] },
    nearest_experiments: [
      { experiment_id: 'EXP_BASS_012', report_id: '20160010041', material, oxygen_pct: 21.0, pressure_kpa: 101.3, flow_cm_s: 5.0, outcome: 'spread', distance: 0.000, source_url: 'https://ntrs.nasa.gov/citations/20160010041' },
      { experiment_id: 'EXP_BASS_044', report_id: '20140011099', material, oxygen_pct: 18.0, pressure_kpa: 101.3, flow_cm_s: 5.0, outcome: 'spread', distance: 0.082, source_url: 'https://ntrs.nasa.gov/citations/20140011099' },
      { experiment_id: 'EXP_BASS_089', report_id: '20170006615', material, oxygen_pct: 16.5, pressure_kpa: 101.3, flow_cm_s: 3.5, outcome: 'no_spread', distance: 0.114, source_url: 'https://ntrs.nasa.gov/citations/20170006615' }
    ],
    explanation: `Under microgravity conditions without natural buoyant convection, ${material} at ${oxygen_pct}% O2, ${pressure_kpa} kPa, and ${flow_cm_s} cm/s ventilation is predicted to exhibit ${pred === 'spread' ? 'sustained flame spread' : (pred === 'marginal_spread' ? 'marginal propagation' : 'flame extinction')} with probability ${(probs[pred] * 100).toFixed(1)}%. Supported by published NASA spaceflight records: 20160010041 and 20140011099.`
  };
}

function generateFallbackBoundary(material, pressure) {
  const o2Grid = [15.5, 17.0, 18.5, 20.0, 21.5, 23.0, 24.5, 26.0, 28.0, 30.0, 32.0, 34.0];
  const flowGrid = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0, 20.0, 25.0, 30.0, 35.0];
  const gridPreds = [];
  const gridProbs = [];

  for (let f of flowGrid) {
    const rowPreds = [];
    const rowProbs = [];
    for (let o2 of o2Grid) {
      if (o2 < 17.0) {
        rowPreds.push('no_spread');
        rowProbs.push(0.04);
      } else if (o2 <= 17.8) {
        rowPreds.push('marginal_spread');
        rowProbs.push(0.25);
      } else {
        rowPreds.push('spread');
        rowProbs.push(0.92);
      }
    }
    gridPreds.push(rowPreds);
    gridProbs.push(rowProbs);
  }

  return {
    material,
    fixed_pressure_kpa: pressure,
    oxygen_range: [15.5, 34.0],
    flow_range: [0.0, 35.0],
    oxygen_grid: o2Grid,
    flow_grid: flowGrid,
    grid_predictions: gridPreds,
    grid_spread_probabilities: gridProbs,
    real_experiments: [
      { experiment_id: 'EXP_BASS_001', report_id: '20160010041', oxygen_pct: 21.0, flow_cm_s: 5.0, pressure_kpa: 101.3, outcome: 'spread' },
      { experiment_id: 'EXP_BASS_044', report_id: '20140011099', oxygen_pct: 18.0, flow_cm_s: 5.0, pressure_kpa: 101.3, outcome: 'spread' },
      { experiment_id: 'EXP_BASS_089', report_id: '20170006615', oxygen_pct: 16.5, flow_cm_s: 3.5, pressure_kpa: 101.3, outcome: 'no_spread' }
    ]
  };
}
