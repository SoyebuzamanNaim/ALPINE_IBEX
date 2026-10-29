"""Exercise the browser boundary refusal without a full DOM dependency."""

import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


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
