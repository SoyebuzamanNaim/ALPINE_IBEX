"""Exercise the browser boundary refusal without a full DOM dependency."""

import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def test_dynamic_experiment_cards_escape_text_and_reject_unsafe_links():
    if not shutil.which("node"):
        pytest.skip("Node.js is unavailable")

    script = r"""
const fs = require('fs');
const vm = require('vm');
const nodes = new Map();
const cards = [];
const document = {
  addEventListener() {},
  getElementById(id) {
    if (!nodes.has(id)) nodes.set(id, {textContent: '', innerHTML: '', appendChild(child) { cards.push(child); }, replaceChildren() {}});
    return nodes.get(id);
  },
  createElement() {
    return {className: '', innerHTML: '', querySelector() { return {addEventListener() {}}; }};
  }
};
const context = vm.createContext({document, window: {location: {protocol: 'file:', origin: 'null', hostname: ''}}, console});
vm.runInContext(fs.readFileSync('app/app.js', 'utf8'), context);
vm.runInContext(`renderNearestExperiments([{
  experiment_id: 'x</span><img src=x onerror=alert(1)>',
  material: '<svg onload=alert(1)>', distance: 0.1,
  oxygen_pct: 20, pressure_kpa: 101, flow_cm_s: 5,
  outcome: 'spread', report_id: 'R1', source_url: 'javascript:alert(1)'
}])`, context);
const html = cards[0].innerHTML;
if (html.includes('<img src=x') || html.includes('<svg onload=') || html.includes('href="javascript:') ||
    !html.includes('&lt;img') || !html.includes('&lt;svg')) {
  throw new Error(`Dynamic experiment content was not safely encoded: ${html}`);
}
if (cards[0].innerHTML.includes('onclick=')) throw new Error('Dynamic provenance ID was inserted into inline JavaScript');
"""
    result = subprocess.run(
        ["node", "-e", script], cwd=ROOT, capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_sweep_refused_point_has_no_transition_distance_or_fabricated_evidence():
    if not shutil.which("node"):
        pytest.skip("Node.js is unavailable")

    script = r"""
const fs = require('fs');
const vm = require('vm');
const nodes = new Map();
const document = {
  addEventListener() {},
  getElementById(id) {
    if (!nodes.has(id)) nodes.set(id, {
      textContent: '', innerHTML: '', style: {}, className: '',
      removeAttribute() {}
    });
    return nodes.get(id);
  }
};
const context = vm.createContext({ document, window: { location: { protocol: 'file:', origin: 'null', hostname: '' } }, console });
vm.runInContext(fs.readFileSync('app/app.js', 'utf8'), context);
vm.runInContext('drawSweepCanvas = () => {}; state.sweepData = {points: [{oxygen_pct: 18, prediction: null}]}; state.dynamicLocBoundary = 17.5; updateSweepPoint(18)', context);
if (nodes.get('safety-margin-val').textContent !== 'N/A' ||
    nodes.get('safety-margin-status').textContent !== 'No model estimate at this point' ||
    /BASS|16.5%/.test(nodes.get('evidence-below-boundary').textContent + nodes.get('evidence-below-boundary').innerHTML)) {
  throw new Error('Refused sweep point displayed a transition or fabricated evidence');
}
vm.runInContext('state.sweepData = {points: [{oxygen_pct: 17.2, prediction: "spread"}, {oxygen_pct: 17.4, prediction: "no_spread"}]}; updateSweepPoint(17.3)', context);
if (nodes.get('safety-margin-val').textContent !== 'N/A' ||
    nodes.get('safety-margin-status').textContent !== 'No model estimate at this point') {
  throw new Error('Unsampled slider value inherited a neighboring prediction');
}
"""
    result = subprocess.run(
        ["node", "-e", script], cwd=ROOT, capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_sweep_chart_does_not_draw_probability_through_refused_points():
    if not shutil.which("node"):
        pytest.skip("Node.js is unavailable")

    script = r"""
const fs = require('fs');
const vm = require('vm');
const red = [];
const ctx = {
  strokeStyle: '', fillStyle: '', lineWidth: 1,
  clearRect() {}, fillRect() {}, strokeRect() {}, setLineDash() {}, beginPath() {}, stroke() {}, fillText() {}, arc() {}, fill() {},
  moveTo(x, y) { if (this.strokeStyle === '#dc2626') red.push('move'); },
  lineTo(x, y) { if (this.strokeStyle === '#dc2626') red.push('line'); }
};
const document = {
  addEventListener() {},
  getElementById(id) { return id === 'sweep-chart-canvas' ? {width: 1120, height: 280, getContext: () => ctx} : null; }
};
const context = vm.createContext({document, window: {location: {protocol: 'file:', origin: 'null', hostname: ''}}, console});
vm.runInContext(fs.readFileSync('app/app.js', 'utf8'), context);
vm.runInContext('state.dynamicLocBoundary = 17.5; state.sweepData = {points: [{oxygen_pct: 16, probabilities: {spread: 0.8, no_spread: 0.2}}, {oxygen_pct: 17, probabilities: null}, {oxygen_pct: 18, probabilities: {spread: 0.2, no_spread: 0.8}}]}; drawSweepCanvas(18)', context);
if (red.includes('line') || red.filter(x => x === 'move').length !== 2) throw new Error(JSON.stringify(red));
"""
    result = subprocess.run(
        ["node", "-e", script], cwd=ROOT, capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_stale_sweep_response_cannot_restore_old_scenario():
    if not shutil.which("node"):
        pytest.skip("Node.js is unavailable")

    script = r"""
const fs = require('fs');
const vm = require('vm');
const pending = [];
const document = { addEventListener() {}, getElementById() { return null; } };
const fetch = () => new Promise(resolve => pending.push(resolve));
const context = vm.createContext({document, fetch, window: {location: {protocol: 'file:', origin: 'null', hostname: ''}}, console});
vm.runInContext(fs.readFileSync('app/app.js', 'utf8'), context);
(async () => {
  const first = vm.runInContext('fetchSweepData()', context);
  vm.runInContext('state.material = "Silicone"', context);
  const second = vm.runInContext('fetchSweepData()', context);
  const data = material => ({marker: material, points: [{oxygen_pct: 21, prediction: 'spread'}], transitions: [{from_regime: 'no_spread', to_regime: 'spread', midpoint: 20, evidence_before: [], evidence_after: []}]});
  pending[1]({ok: true, json: async () => data('Silicone')});
  await second;
  pending[0]({ok: true, json: async () => data('PMMA')});
  await first;
  const marker = vm.runInContext('state.sweepData.marker', context);
  if (marker !== 'Silicone') throw new Error(`Stale sweep: ${marker}`);
})().catch(err => { console.error(err); process.exitCode = 1; });
"""
    result = subprocess.run(
        ["node", "-e", script], cwd=ROOT, capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_canvas_probe_invalidates_previous_sweep():
    if not shutil.which("node"):
        pytest.skip("Node.js is unavailable")

    script = r"""
const fs = require('fs');
const vm = require('vm');
const listeners = {};
const canvas = {
  addEventListener(name, callback) { listeners[name] = callback; },
  getBoundingClientRect() { return {left: 0, top: 0, width: 500, height: 300}; }
};
const nodes = new Map();
const document = {
  addEventListener() {},
  getElementById(id) {
    if (id === 'flammability-boundary-canvas') return canvas;
    if (id === 'sweep-chart-canvas') return null;
    if (!nodes.has(id)) nodes.set(id, {textContent: '', value: '21'});
    return nodes.get(id);
  }
};
const window = {location: {protocol: 'file:', origin: 'null', hostname: ''}, addEventListener() {}};
const context = vm.createContext({document, window, console, setTimeout: () => 1, clearTimeout() {}});
vm.runInContext(fs.readFileSync('app/app.js', 'utf8'), context);
vm.runInContext('state.boundaryData = {oxygen_range: [16, 21], flow_range: [0, 20]}; state.sweepData = {marker: "old"}; state.dynamicLocBoundary = 17.5; setupCanvasInteraction()', context);
listeners.pointerdown({clientX: 200, clientY: 100});
const remaining = vm.runInContext('state.sweepData', context);
if (remaining !== null) throw new Error('Canvas probe retained old sweep');
"""
    result = subprocess.run(
        ["node", "-e", script], cwd=ROOT, capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_sweep_refresh_cancels_running_animation():
    if not shutil.which("node"):
        pytest.skip("Node.js is unavailable")

    script = r"""
const fs = require('fs');
const vm = require('vm');
const cleared = [];
const document = {addEventListener() {}, getElementById() {return null;}};
const context = vm.createContext({
  document, window: {location: {protocol: 'file:', origin: 'null', hostname: ''}}, console,
  setTimeout: () => 1, clearTimeout() {}, clearInterval: id => cleared.push(id)
});
vm.runInContext(fs.readFileSync('app/app.js', 'utf8'), context);
vm.runInContext('drawSweepCanvas = () => {}; state.sweepInterval = 42; state.sweepRunning = true; scheduleSweepRefresh()', context);
if (JSON.stringify(cleared) !== '[42]' || vm.runInContext('state.sweepRunning', context)) {
  throw new Error('Sweep animation was not cancelled');
}
"""
    result = subprocess.run(
        ["node", "-e", script], cwd=ROOT, capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_auto_sweep_stops_at_slider_minimum():
    if not shutil.which("node"):
        pytest.skip("Node.js is unavailable")

    script = r"""
const fs = require('fs');
const vm = require('vm');
const nodes = new Map();
let tick;
const document = {
  addEventListener() {},
  getElementById(id) {
    if (id === 'sweep-chart-canvas') return null;
    if (!nodes.has(id)) nodes.set(id, {
      textContent: '', value: '21.0', style: {}, className: '',
      addEventListener(name, callback) { this[name] = callback; }, removeAttribute() {}
    });
    return nodes.get(id);
  }
};
const context = vm.createContext({
  document, window: {location: {protocol: 'file:', origin: 'null', hostname: ''}}, console,
  setInterval: callback => {tick = callback; return 42;}, clearInterval() {}
});
vm.runInContext(fs.readFileSync('app/app.js', 'utf8'), context);
vm.runInContext('fetchSweepData = () => {}; state.sweepData = {points: []}; state.dynamicLocBoundary = 17.5; setupSweepView()', context);
nodes.get('btn-run-auto-sweep').click();
for (let i = 0; i < 52; i++) tick();
const readout = nodes.get('readout-sweep-o2').textContent;
if (readout !== '16.0 %' || vm.runInContext('state.sweepRunning', context)) {
  throw new Error(`Auto sweep passed slider minimum: ${readout}`);
}
"""
    result = subprocess.run(
        ["node", "-e", script], cwd=ROOT, capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_conflicting_evidence_is_shown_as_abstention():
    if not shutil.which("node"):
        pytest.skip("Node.js is unavailable")

    script = r"""
const fs = require('fs');
const vm = require('vm');
const nodes = new Map();
const document = {
  addEventListener() {},
  getElementById(id) {
    if (!nodes.has(id)) nodes.set(id, { textContent: '', style: {}, classList: { add() {}, remove() {} } });
    return nodes.get(id);
  }
};
const context = vm.createContext({ document, window: { location: { protocol: 'file:', origin: 'null', hostname: '' } }, console });
vm.runInContext(fs.readFileSync('app/app.js', 'utf8'), context);
vm.runInContext('drawBoundaryCanvas = () => {}; renderNearestExperiments = () => {};', context);
vm.runInContext('renderPredictionResults({status: "conflicting_evidence", in_training_range: true, explanation: "BASS2_O3a_3 and BASS2_O3b_3 disagree", nearest_experiments: []})', context);
if (!nodes.get('regime-badge').textContent.includes('CONFLICTING') ||
    nodes.get('val-prob-spread').textContent !== 'N/A' ||
    !nodes.get('alert-message').textContent.includes('BASS2_O3a_3')) {
  throw new Error('Conflicting evidence was not presented as an abstention');
}
"""
    result = subprocess.run(
        ["node", "-e", script], cwd=ROOT, capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_sparse_material_evidence_is_shown_as_abstention():
    if not shutil.which("node"):
        pytest.skip("Node.js is unavailable")

    script = r"""
const fs = require('fs');
const vm = require('vm');
const nodes = new Map();
const document = {
  addEventListener() {},
  getElementById(id) {
    if (!nodes.has(id)) nodes.set(id, { textContent: '', style: {}, classList: { add() {}, remove() {} } });
    return nodes.get(id);
  }
};
const context = vm.createContext({ document, window: { location: { protocol: 'file:', origin: 'null', hostname: '' } }, console });
vm.runInContext(fs.readFileSync('app/app.js', 'utf8'), context);
vm.runInContext('drawBoundaryCanvas = () => {}; renderNearestExperiments = () => {};', context);
vm.runInContext('renderPredictionResults({status: "insufficient_material_evidence", in_training_range: true, explanation: "Only 1 distinct condition was observed for Cotton", nearest_experiments: []})', context);
if (!nodes.get('regime-badge').textContent.includes('INSUFFICIENT') ||
    nodes.get('val-prob-spread').textContent !== 'N/A' ||
    !nodes.get('alert-message').textContent.includes('Cotton')) {
  throw new Error('Sparse material evidence was not presented as an abstention');
}
"""
    result = subprocess.run(
        ["node", "-e", script], cwd=ROOT, capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_final_audit_failure_is_shown_as_abstention():
    if not shutil.which("node"):
        pytest.skip("Node.js is unavailable")

    script = r"""
const fs = require('fs');
const vm = require('vm');
const nodes = new Map();
const document = {
  addEventListener() {},
  getElementById(id) {
    if (!nodes.has(id)) nodes.set(id, {textContent: '', style: {}, classList: {add() {}, remove() {}}});
    return nodes.get(id);
  }
};
const context = vm.createContext({document, window: {location: {protocol: 'file:', origin: 'null', hostname: ''}}, console});
vm.runInContext(fs.readFileSync('app/app.js', 'utf8'), context);
vm.runInContext('drawBoundaryCanvas = () => {}; renderNearestExperiments = () => {};', context);
vm.runInContext('renderPredictionResults({status: "audit_failed", in_training_range: true, explanation: "Final evidence audit failed", nearest_experiments: []})', context);
if (!nodes.get('regime-badge').textContent.includes('AUDIT FAILED') ||
    nodes.get('val-prob-spread').textContent !== 'N/A' ||
    !nodes.get('alert-message').textContent.includes('audit failed')) {
  throw new Error('Failed audit was displayed as a model estimate');
}
"""
    result = subprocess.run(
        ["node", "-e", script], cwd=ROOT, capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_published_boundary_refuses_outside_oxygen_fit():
    if not shutil.which("node"):
        pytest.skip("Node.js is unavailable")

    script = r"""
const fs = require('fs');
const vm = require('vm');
const nodes = new Map();
const document = {
  addEventListener() {},
  getElementById(id) {
    if (!nodes.has(id)) nodes.set(id, {
      textContent: '', innerHTML: '', style: {},
      classList: { add() {}, remove() {} }
    });
    return nodes.get(id);
  }
};
const context = vm.createContext({ document, window: { location: { protocol: 'file:', origin: 'null', hostname: '' } }, console });
vm.runInContext(fs.readFileSync('app/app.js', 'utf8'), context);
document.getElementById('nearest-cards-list').textContent = 'PMMA observation';
vm.runInContext('renderPublishedBoundary({oxygen_pct: 30, pressure_kpa: 101.3, flow_cm_s: 5, material: "PMMA"})', context);
const badge = nodes.get('regime-badge').textContent;
const pill = nodes.get('confidence-pill').textContent;
const briefing = nodes.get('operator-briefing-text').textContent;
if (!badge.includes('OUTSIDE') || pill !== 'NOT APPLICABLE' || /limit of|points BELOW|points ABOVE/.test(briefing)) {
  throw new Error(JSON.stringify({ badge, pill, briefing }));
}
if (nodes.get('nearest-cards-list').textContent.includes('PMMA observation')) throw new Error('Stale evidence remains');
vm.runInContext('renderPublishedBoundary({oxygen_pct: 21, pressure_kpa: 56.5, flow_cm_s: 5, material: "PMMA"})', context);
if (nodes.get('confidence-pill').textContent !== 'NOT APPLICABLE') throw new Error('Pressure extrapolation shown');
vm.runInContext('renderPublishedBoundary({oxygen_pct: 21, pressure_kpa: 101.3, flow_cm_s: 60, material: "PMMA"})', context);
if (nodes.get('confidence-pill').textContent !== 'NOT APPLICABLE') throw new Error('Flow extrapolation shown');
"""
    result = subprocess.run(
        ["node", "-e", script], cwd=ROOT, capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_stale_boundary_response_is_discarded_after_material_change():
    if not shutil.which("node"):
        pytest.skip("Node.js is unavailable")

    script = r"""
const fs = require('fs');
const vm = require('vm');
const pending = [];
const document = { addEventListener() {}, getElementById() { return null; } };
const fetch = () => new Promise(resolve => pending.push(resolve));
const context = vm.createContext({ document, fetch, window: { location: { protocol: 'file:', origin: 'null', hostname: '' } }, console });
vm.runInContext(fs.readFileSync('app/app.js', 'utf8'), context);
vm.runInContext('drawBoundaryCanvas = () => {}; drawOfflineCanvas = () => {};', context);
(async () => {
  const first = vm.runInContext('fetchBoundarySlice()', context);
  vm.runInContext('state.material = "Silicone"', context);
  const second = vm.runInContext('fetchBoundarySlice()', context);
  pending[1]({ok: true, json: async () => ({material: 'Silicone'})});
  await second;
  pending[0]({ok: true, json: async () => ({material: 'PMMA'})});
  await first;
  const material = vm.runInContext('state.boundaryData.material', context);
  if (material !== 'Silicone') throw new Error(`Stale boundary: ${material}`);
})().catch(err => { console.error(err); process.exitCode = 1; });
"""
    result = subprocess.run(
        ["node", "-e", script], cwd=ROOT, capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_stale_prediction_response_is_discarded_after_material_change():
    if not shutil.which("node"):
        pytest.skip("Node.js is unavailable")

    script = r"""
const fs = require('fs');
const vm = require('vm');
const pending = [];
const rendered = [];
const document = { addEventListener() {}, getElementById() { return null; } };
const fetch = () => new Promise(resolve => pending.push(resolve));
const context = vm.createContext({ document, fetch, window: { location: { protocol: 'file:', origin: 'null', hostname: '' } }, console });
vm.runInContext(fs.readFileSync('app/app.js', 'utf8'), context);
vm.runInContext('renderPredictionResults = data => window.rendered.push(data.material); window.rendered = [];', context);
(async () => {
  const first = vm.runInContext('triggerScenarioEvaluation()', context);
  vm.runInContext('state.material = "Silicone"', context);
  const second = vm.runInContext('triggerScenarioEvaluation()', context);
  pending[1]({ok: true, json: async () => ({material: 'Silicone'})});
  await second;
  pending[0]({ok: true, json: async () => ({material: 'PMMA'})});
  await first;
  if (JSON.stringify(context.window.rendered) !== '["Silicone"]') {
    throw new Error(JSON.stringify(context.window.rendered));
  }
})().catch(err => { console.error(err); process.exitCode = 1; });
"""
    result = subprocess.run(
        ["node", "-e", script], cwd=ROOT, capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
