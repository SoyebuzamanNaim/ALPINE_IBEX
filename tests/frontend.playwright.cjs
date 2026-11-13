/* Live FastAPI + Chromium integration; no invented predictions or observation responses. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {spawn} = require('node:child_process');
const {chromium} = require('playwright');
const root = path.resolve(__dirname, '..');
const base = process.env.FLARE_TEST_URL || 'http://127.0.0.1:8010';
const frontend = process.env.FLARE_FRONTEND_URL || base;
const output = process.env.FLARE_TEST_OUTPUT || '/tmp/flare-playwright';
fs.mkdirSync(output, {recursive: true});
const checks = [], errors = [];
let failure = null;
const tabs = ['lab', 'conflict', 'coverage', 'sweep', 'atlas', 'model'];
let server, browser, page;
async function check(name, task) {
  await task(); checks.push(name); console.log(`PASS ${name}`);
}
async function scenario(text) {
  await page.locator('#tab-lab-btn').click();
  await page.locator('#nlp-query-input').fill(text);
  const response = page.waitForResponse(r => r.url().endsWith('/predict') && r.request().method() === 'POST');
  await page.locator('#nlp-query-submit').click();
  const data = await (await response).json();
  await page.waitForFunction(() => !document.getElementById('regime-badge').textContent.includes('Checking'));
  return data;
}
async function ready() {
  for (let i = 0; i < 80; i++) {
    try { if ((await fetch(`${base}/health`)).ok) return; } catch {}
    await new Promise(resolve => setTimeout(resolve, 150));
  }
  throw new Error(`Backend did not start at ${base}`);
}
(async () => {
  try {
    if (!process.env.FLARE_TEST_URL) {
      const localPython = path.join(root, '.venv/bin/python');
      const python = process.env.FLARE_TEST_PYTHON || (fs.existsSync(localPython) ? localPython : 'python');
      server = spawn(python, ['-m', 'uvicorn', 'src.api.main:app', '--host', '127.0.0.1', '--port', '8010'], {cwd: root, stdio: ['ignore', 'pipe', 'pipe']});
      const log = fs.createWriteStream(path.join(output, 'server.log'));
      server.stdout.pipe(log); server.stderr.pipe(log);
    }
    await ready();
    browser = await chromium.launch({headless: true});
    const context = await browser.newContext({viewport: {width: 1440, height: 1000}, reducedMotion: 'reduce'});
    page = await context.newPage();
    // Respect the real backend's 60 heavy requests/minute without relaxing its guard.
    const heavyPaths = new Set(['/predict', '/boundary', '/sweep', '/scenario/parse', '/api/conflict/compare-studies']);
    let heavyQueue = Promise.resolve(), lastHeavy = 0;
    await page.route(`${base}/**`, async route => {
      if (route.request().method() !== 'OPTIONS' && heavyPaths.has(new URL(route.request().url()).pathname)) {
        heavyQueue = heavyQueue.then(async () => {
          await new Promise(resolve => setTimeout(resolve, Math.max(0, 1100 - (Date.now() - lastHeavy))));
          lastHeavy = Date.now();
        });
        await heavyQueue;
      }
      await route.continue();
    });
    page.on('pageerror', error => errors.push(error.message));
    page.on('response', response => {
      if (response.url().startsWith(base) && response.status() >= 500) errors.push(`${response.status()} ${response.url()}`);
    });
    await page.goto(frontend);
    await page.waitForFunction(() => document.getElementById('chip-model-type').textContent === 'Linear SVM' && document.getElementById('val-prob-spread').textContent.includes('%'));
    await page.screenshot({path: path.join(output, 'initial-desktop.png'), animations: 'disabled'});
    await check('Evidence desk leads with the source record, supports report search and exports cited evidence', async () => {
      assert.equal(await page.locator('#research-model-panel').getAttribute('open'), null);
      assert.match(await page.locator('#evidence-overview-body').innerText(), /Source observation:[\s\S]*Cannot conclude:/);
      await page.locator('#report-search-input').fill('PMMA extinction');
      await page.locator('#report-search-form button').click();
      await page.locator('#report-search-results article').first().waitFor();
      assert.match(await page.locator('#report-search-status').innerText(), /lexical relevance/);
      assert.match(await page.locator('#report-search-results a').first().getAttribute('href'), /^https:\/\//);
      const downloading = page.waitForEvent('download');
      await page.locator('#download-evidence').click();
      const download = await downloading;
      const bundle = JSON.parse(fs.readFileSync(await download.path(), 'utf8'));
      assert.equal(bundle.summary_method, 'deterministic_record_template');
      assert.equal(bundle.observations.length, 3);
      assert.match(bundle.observations[0].source_url, /^https:\/\//);
      await page.locator('#report-search-input').fill('unmatched-zxqv197341');
      await page.locator('#report-search-form button').click();
      await page.waitForFunction(() => document.getElementById('report-search-status').textContent.startsWith('0 reports'));
      await page.locator('#research-model-panel > summary').click();
    });
    await check('Frontend connects to the selected research SVM backend', async () => {
      const h = await (await page.request.get(`${base}/health`)).json();
      assert.equal(h.model_type, 'linear_svm'); assert.equal(h.model_ready, true); assert.equal(h.release_mode, 'research');
      assert.equal(await page.locator('#chip-cv-acc').count(), 0);
      assert.match(await page.locator('#operator-briefing-text').innerText(), /Exploratory/);
    });
    await check('Similarity ranking explains conditions and limitations without implying reliability', async () => {
      const card = page.locator('.flight-obs-card').first();
      const text = await card.innerText();
      assert.match(text, /What was observed:[\s\S]*Which conditions differ:[\s\S]*What cannot be concluded:/);
      assert.match(text, /Geometry:[\s\S]*Flow direction:[\s\S]*Ignition history:/);
      assert.match(text, /unspecified/);
      await card.locator('summary').click();
      assert.match(await card.innerText(), /material penalty[\s\S]*not more reliable/);
    });
    await check('Citation inspector includes source text, geometry and keyboard focus', async () => {
      await page.locator('.btn-trace-cite').first().click();
      await page.locator('#modal-citation-inspector').waitFor({state: 'visible'});
      assert.match(await page.locator('#inspect-sample-context').innerText(), /sheet|rod|slab/);
      assert.doesNotMatch(await page.locator('#inspect-observation').innerText(), /not recorded/);
      await page.keyboard.press('Shift+Tab');
      assert.equal(await page.locator('#inspect-ntrs-url').evaluate(el => el === document.activeElement), true);
      await page.keyboard.press('Tab');
      assert.equal(await page.locator('#btn-close-inspector').evaluate(el => el === document.activeElement), true);
      await page.keyboard.press('Escape');
      assert.equal(await page.locator('.btn-trace-cite').first().evaluate(el => el === document.activeElement), true);
      const unavailable = route => route.abort('failed');
      await page.route(`${base}/api/provenance/**`, unavailable);
      await page.locator('.btn-trace-cite').first().click();
      await page.locator('#modal-citation-inspector').waitFor({state: 'visible'});
      assert.equal(await page.locator('#inspect-tier-pill').innerText(), 'VERIFICATION UNAVAILABLE');
      assert.equal(await page.locator('#inspect-origin-pill').innerText(), 'ORIGIN UNAVAILABLE');
      assert.equal(await page.locator('#inspect-ntrs-url').isVisible(), false);
      await page.keyboard.press('Escape');
      await page.unroute(`${base}/api/provenance/**`, unavailable);
    });
    await check('All presets, sliders, and out-of-domain refusal agree with the backend', async () => {
      let response = page.waitForResponse(r => r.url().endsWith('/predict'));
      await page.locator('#preset-exploration').click();
      assert.equal((await (await response).json()).prediction, null);
      await page.waitForFunction(() => document.getElementById('val-prob-spread').textContent === 'N/A');
      response = page.waitForResponse(r => r.url().endsWith('/predict'));
      await page.locator('#preset-iss-standard').click(); await response;
      await page.waitForFunction(() => document.getElementById('val-prob-spread').textContent.includes('%'));
      response = page.waitForResponse(r => r.url().endsWith('/predict'));
      await page.locator('#input-o2').evaluate(el => {el.value = '20.2'; el.dispatchEvent(new Event('input', {bubbles: true}));});
      const result = await (await response).json(); assert.equal(result.inputs.oxygen_pct, 20.2);
      assert.equal(await page.locator('#preset-iss-standard').evaluate(el => el.classList.contains('active-preset')), false);
      response = page.waitForResponse(r => r.url().endsWith('/predict'));
      await page.locator('#input-pressure').evaluate(el => {el.value = '90'; el.dispatchEvent(new Event('input', {bubbles: true}));});
      assert.equal((await (await response).json()).inputs.pressure_kpa, 90);
      response = page.waitForResponse(r => r.url().endsWith('/predict'));
      await page.locator('#input-flow').evaluate(el => {el.value = '6.25'; el.dispatchEvent(new Event('input', {bubbles: true}));});
      assert.equal((await (await response).json()).inputs.flow_cm_s, 6.25);
      response = page.waitForResponse(r => r.url().endsWith('/predict'));
      await page.locator('label[for="toggle-extrapolate"]').click();
      assert.equal((await (await response).json()).prediction, null);
      response = page.waitForResponse(r => r.url().endsWith('/predict'));
      await page.locator('label[for="toggle-extrapolate"]').click(); await response;
      response = page.waitForResponse(r => r.url().endsWith('/predict'));
      await page.locator('#preset-near-extinction').click();
      assert.equal((await (await response).json()).inputs.oxygen_pct, 16.5);
    });
    await check('Every material selector reaches matching API evidence and recorded ranges', async () => {
      for (const material of ['PMMA', 'Cellulose', 'Cotton', 'Nomex', 'Cotton-Fiberglass', 'Mylar', 'Silicone', 'Ultem']) {
        const response = page.waitForResponse(r => r.url().endsWith('/predict'));
        await page.locator('#input-material').selectOption(material);
        const data = await (await response).json();
        assert.equal(data.inputs.material, material);
        assert.match(await page.locator('#mat-samples-badge').innerText(), /observations/);
        assert.match(await page.locator('#material-domain').innerText(), /Recorded ranges/);
        if (data.prediction === null) await page.waitForFunction(() => document.getElementById('val-prob-spread').textContent === 'N/A');
      }
    });
    await check('Conflicting and sparse conditions abstain without stale probabilities', async () => {
      let result = await scenario('PMMA at 18% O2, 101.3 kPa, 3 cm/s');
      assert.equal(result.status, 'conflicting_evidence');
      assert.match(await page.locator('#regime-badge').innerText(), /CONFLICTING/);
      assert.equal(await page.locator('#val-prob-spread').innerText(), 'N/A');
      result = await scenario('Cotton at 26.2% O2, 70.7 kPa, 20 cm/s');
      assert.equal(result.status, 'insufficient_material_evidence');
      assert.match(await page.locator('#regime-badge').innerText(), /INSUFFICIENT/);
      const boundary = await (await page.request.get(`${base}/boundary?material=Cotton&pressure_kpa=70.7`)).json();
      assert.ok(boundary.oxygen_range[0] < boundary.oxygen_range[1]);
      assert.ok(boundary.flow_range[0] < boundary.flow_range[1]);
      assert.ok(boundary.grid_predictions.flat().every(value => value === null));
    });
    await check('Scenario parser explains ambiguity and preserves entered source conditions', async () => {
      await page.locator('#nlp-query-input').fill('PMMA without an atmosphere');
      await page.locator('#nlp-query-submit').click();
      await page.waitForFunction(() => document.getElementById('nlp-feedback').textContent.includes('Could not parse'));
      const result = await scenario('Cellulose at 17% O2, 101.3 kPa, 0.81 cm/s');
      assert.equal(result.inputs.flow_cm_s, .81);
      assert.equal(Number(await page.locator('#input-flow').inputValue()), .81);
      assert.match(await page.locator('#readout-flow').innerText(), /0\.81/);
    });
    await check('Archive filters, empty results and keyboard probing work', async () => {
      await page.locator('#tab-atlas-btn').click();
      await page.locator('#atlas-filter-material').selectOption('Cellulose');
      await page.locator('#atlas-filter-outcome').selectOption('no_spread');
      assert.match(await page.locator('#atlas-count').innerText(), /^3 of 200/);
      await page.locator('#atlas-search-input').fill('not-an-experiment');
      assert.match(await page.locator('#atlas-table-body').innerText(), /No observations match/);
      await page.locator('#atlas-search-input').fill('');
      const button = page.locator('#atlas-table-body tr').filter({hasText: '14%'}).first().locator('.archive-probe');
      await button.focus(); await page.keyboard.press('Enter');
      await page.locator('#view-scenario-lab').waitFor({state: 'visible'});
      assert.equal(Number(await page.locator('#input-o2').inputValue()), 14);
      assert.equal(await page.locator('#readout-o2').innerText(), '14.0 %');
    });
    await check('A delayed scenario search cannot replace newer manual conditions', async () => {
      let release, held;
      const waiting = new Promise(resolve => {held = resolve;});
      const blocked = new Promise(resolve => {release = resolve;});
      const delay = async route => {
        const response = await route.fetch();
        held();
        await blocked;
        await route.fulfill({response});
      };
      await page.route(`${base}/scenario/parse`, delay);
      await page.locator('#nlp-query-input').fill('PMMA at 19% O2, 101.3 kPa, 5 cm/s');
      await page.locator('#nlp-query-submit').click();
      await waiting;
      const parsed = page.waitForResponse(r => r.url().endsWith('/scenario/parse'));
      await page.locator('#preset-iss-standard').click();
      release();
      await parsed;
      await page.waitForFunction(() => document.getElementById('val-prob-spread').textContent.includes('%'));
      assert.equal(await page.evaluate(() => state.oxygen_pct), 21);
      assert.equal(await page.locator('#nlp-feedback').isVisible(), false);
      await page.unroute(`${base}/scenario/parse`, delay);
    });
    await check('Boundary canvas probes use its scaled drawing coordinates', async () => {
      await scenario('PMMA at 21% O2, 101.3 kPa, 5 cm/s');
      await page.waitForFunction(() => state.boundaryData?.material === 'PMMA');
      const canvas = page.locator('#flammability-boundary-canvas');
      await canvas.scrollIntoViewIfNeeded(); const box = await canvas.boundingBox();
      const data = await page.evaluate(() => ({range: state.boundaryData.oxygen_range, flow: state.boundaryData.flow_range, width: document.getElementById('flammability-boundary-canvas').width, height: document.getElementById('flammability-boundary-canvas').height}));
      const x = (70 + (data.width - 105) * .4) / data.width * box.width;
      const y = (35 + (data.height - 80) * .6) / data.height * box.height;
      await canvas.click({position: {x, y}});
      const actual = await page.evaluate(() => state.oxygen_pct);
      const expected = Math.round((data.range[0] + .4 * (data.range[1] - data.range[0])) * 10) / 10;
      assert.equal(actual, expected);
    });
    await check('Conflict cases and custom study comparisons load real API results', async () => {
      await page.locator('#tab-conflict-btn').click();
      await page.locator('#conflict-results-container').waitFor({state: 'visible'});
      for (const value of await page.locator('#select-conflict-case option').evaluateAll(nodes => nodes.map(node => node.value))) {
        await page.locator('#select-conflict-case').selectOption(value);
        const response = page.waitForResponse(r => r.url().endsWith('/api/conflict/compare-studies'));
        await page.locator('#btn-load-case').click(); assert.equal((await response).status(), 200);
        await page.locator('#conflict-results-container').waitFor({state: 'visible'});
        assert.ok((await page.locator('#conflict-dimensions-tbody tr').count()) > 0);
      }
      await page.locator('#select-study-a').selectOption('BASS-II'); await page.locator('#select-study-b').selectOption('Saffire');
      const response = page.waitForResponse(r => r.url().endsWith('/api/conflict/compare-studies'));
      await page.locator('#btn-compare-studies').click(); assert.equal((await response).status(), 200);
    });
    await check('Coverage map reconciles totals and renders all data cells', async () => {
      await page.locator('#tab-coverage-btn').click();
      await page.waitForFunction(() => document.getElementById('cov-total-runs').textContent === '200');
      const sum = await page.locator('.cell-count').evaluateAll(nodes => nodes.reduce((sum, node) => sum + Number(node.textContent), 0));
      assert.equal(sum, 200); assert.ok(await page.locator('.gap-card').count() > 0);
      assert.match(await page.locator('.gap-card').first().innerText(), /TEAM PROPOSAL/);
      assert.match(await page.locator('.heatmap-footnote').innerText(), /current FLARE-X dataset/);
    });
    await check('Model provenance distinguishes selected score from nested search and shows seven folds', async () => {
      await page.locator('#tab-model-btn').click();
      assert.equal(await page.locator('#model-kpi-nested').innerText(), '25.5%');
      assert.equal(await page.locator('#model-kpi-accuracy').innerText(), '84.0%');
      assert.match(await page.locator('#model-fold-heading').innerText(), /^7-fold/);
      assert.equal(await page.locator('.investigation-card').count(), (await (await page.request.get(`${base}/datasets`)).json()).count);
    });
    await check('Live oxygen sweep renders points without inventing a transition', async () => {
      await scenario('PMMA at 21% O2, 101.3 kPa, 5 cm/s');
      await page.locator('#tab-sweep-btn').click();
      await page.waitForFunction(() => state.sweepMode === 'model' && state.sweepData?.points.length > 0);
      assert.equal(await page.locator('#sweep-title').innerText(), 'Research model oxygen sweep');
      assert.equal(await page.locator('#safety-margin-val').innerText(), 'N/A');
      assert.match(await page.locator('#safety-margin-status').innerText(), /No model transition/);
      assert.match(await page.locator('#sweep-model-key').innerText(), /Spread[\s\S]*Marginal spread[\s\S]*No spread/);
      assert.ok((await page.locator('#sweep-chart-canvas').boundingBox()).height >= 260, 'Probability scale was compressed by the layout');
      const expected = await page.evaluate(() => state.sweepData.points.find(point => point.oxygen_pct === 21).probabilities);
      for (const probability of Object.values(expected)) {
        assert.ok((await page.locator('#sweep-point-details').innerText()).includes(`${(probability * 100).toFixed(2)}%`));
      }
      await page.locator('#btn-run-auto-sweep').click();
      await page.waitForFunction(() => !state.sweepRunning, null, {timeout: 10000});
      assert.equal(Number(await page.locator('#sweep-oxygen-slider').inputValue()), 16);
    });
    await check('Oxygen sweeps include the selected condition and keyboard controls reach real samples', async () => {
      await scenario('PMMA at 25% O2, 101.3 kPa, 5 cm/s');
      await page.locator('#tab-sweep-btn').click();
      await page.waitForFunction(() => state.sweepMode === 'model');
      const range = await page.evaluate(() => state.sweepData.range);
      assert.ok(range[0] <= 25 && range[1] >= 25);
      assert.equal(Number(await page.locator('#sweep-oxygen-slider').inputValue()), 25);
      await page.locator('#sweep-oxygen-slider').focus();
      await page.keyboard.press('ArrowLeft');
      assert.equal(await page.evaluate(() => state.sweepData.points.some(point => point.oxygen_pct === Number(document.getElementById('sweep-oxygen-slider').value))), true);
      assert.ok(Number(await page.locator('#sweep-oxygen-slider').inputValue()) < 25);
      await page.keyboard.press('End');
      assert.equal(Number(await page.locator('#sweep-oxygen-slider').inputValue()), 25);
    });
    await check('Fully refused oxygen sweeps show reasons and disable playback', async () => {
      for (const query of ['Nomex at 21% O2, 101.3 kPa, 5 cm/s', 'PMMA at 21% O2, 101.3 kPa, 45 cm/s']) {
        await scenario(query);
        await page.locator('#tab-sweep-btn').click();
        await page.waitForFunction(() => document.getElementById('sweep-description').textContent.startsWith('No model estimates: all'));
        assert.equal(await page.locator('#sweep-oxygen-slider').isDisabled(), true);
        assert.equal(await page.locator('#btn-run-auto-sweep').isDisabled(), true);
        assert.equal(await page.locator('#sweep-model-key').isVisible(), false);
        assert.match(await page.locator('#safety-margin-status').innerText(), /refused[\s\S]*outside/i);
        assert.doesNotMatch(await page.locator('#sweep-description').innerText(), /No model transition/);
      }
    });
    await check('A refused oxygen sample retains its conflict reason within a partial sweep', async () => {
      await scenario('PMMA at 21% O2, 101.3 kPa, 3 cm/s');
      await page.locator('#tab-sweep-btn').click();
      await page.waitForFunction(() => state.sweepMode === 'model');
      assert.match(await page.locator('#sweep-sampling-note').innerText(), /[1-9]\d* refused/);
      await page.locator('#sweep-oxygen-slider').evaluate(slider => { slider.value = '18'; slider.dispatchEvent(new Event('input', {bubbles: true})); });
      assert.equal(await page.locator('#safety-margin-val').innerText(), 'N/A');
      assert.match(await page.locator('#sweep-point-details').innerText(), /No model estimate: conflicting evidence/);
      assert.match(await page.locator('#safety-margin-status').innerText(), /conflicting evidence/);
      assert.equal(await page.locator('#btn-run-auto-sweep').isDisabled(), false);
    });
    await check('Keyboard tab navigation and all six views fit desktop, tablet and phones', async () => {
      await page.locator('#tab-lab-btn').focus(); await page.keyboard.press('ArrowRight');
      assert.equal(await page.locator('#tab-conflict-btn').getAttribute('aria-selected'), 'true');
      for (const width of [1920, 1440, 768, 390, 320]) {
        await page.setViewportSize({width, height: width < 768 ? 844 : 1000});
        for (const tab of tabs) {
          await page.locator(`#tab-${tab}-btn`).click();
          if (tab === 'conflict') await page.locator('#conflict-results-container').waitFor({state: 'visible'});
          if (tab === 'coverage') await page.waitForFunction(() => document.getElementById('coverage-status').textContent === '');
          if (tab === 'sweep') await page.waitForFunction(() => state.sweepMode !== null && !document.getElementById('sweep-oxygen-slider').disabled);
          await page.locator('.view-panel.active').evaluate(panel => {panel.scrollTop = 0;});
          const size = await page.evaluate(() => ({content: document.documentElement.scrollWidth, viewport: innerWidth}));
          assert.ok(size.content <= size.viewport + 1, `${tab} overflows at ${width}: ${size.content}`);
          const header = await page.evaluate(() => {
            const brand = document.querySelector('.platform-code').getBoundingClientRect();
            const status = document.querySelector('.telemetry-heartbeat-cell').getBoundingClientRect();
            return {brandRight: brand.right, statusLeft: status.left, brandHeight: brand.height};
          });
          assert.ok(header.brandRight <= header.statusLeft, `Header overlaps at ${width}`);
          assert.ok(header.brandHeight < 30, `Brand wraps at ${width}`);
          assert.equal(await page.locator(`#tab-${tab}-btn`).getAttribute('aria-selected'), 'true');
          await page.screenshot({path: path.join(output, `${width}-${tab}.png`), animations: 'disabled'});
        }
      }
    });
    await check('Overview and workbench navigation reach the correct pages', async () => {
      await page.locator('a[title="Return to Public Project Overview"]').click();
      await page.waitForURL('**/project-page/'); assert.match(await page.title(), /FLARE-X/);
      const response = await page.goto(frontend); assert.equal(response.status(), 200);
      await page.waitForFunction(() => document.getElementById('chip-model-type').textContent === 'Linear SVM');
      assert.equal(new URL(await page.locator('#api-docs-link').getAttribute('href'), frontend).origin, new URL(base).origin);
      assert.equal(new URL(await page.locator('#model-metadata-link').getAttribute('href'), frontend).origin, new URL(base).origin);
    });
    await check('A lost prediction connection clears probabilities and recovers on retry', async () => {
      await page.setViewportSize({width: 1440, height: 1000});
      await page.locator('#research-model-panel > summary').click();
      await page.locator('#preset-iss-standard').click();
      await page.waitForFunction(() => document.getElementById('val-prob-spread').textContent.includes('%'));
      const intercept = route => route.abort('failed');
      await page.route(`${base}/predict`, intercept);
      await page.locator('#preset-near-extinction').click();
      await page.waitForFunction(() => document.getElementById('status-text').textContent.includes('unavailable'));
      assert.equal((await page.locator('#val-prob-spread').innerText()).toLowerCase(), 'n/a');
      assert.match(await page.locator('#alert-message').innerText(), /Live estimate unavailable/);
      await page.waitForFunction(() => currentEvidence?.scenario.oxygen_pct === 16.5 && currentEvidence?.observations.length > 0);
      assert.match(await page.locator('#status-text').innerText(), /Evidence online/);
      assert.match(await page.locator('#evidence-overview-body').innerText(), /Source observation:/);
      await page.unroute(`${base}/predict`, intercept);
      const response = page.waitForResponse(r => r.url().endsWith('/predict'));
      await page.locator('#preset-iss-standard').click(); await response;
      await page.waitForFunction(() => document.getElementById('status-text').textContent.includes('Research model available'));
      assert.match(await page.locator('#val-prob-spread').innerText(), /%/);
    });
    await check('Offline mode shows a separate published reference and explicit unavailable states', async () => {
      const offline = await browser.newContext({viewport: {width: 390, height: 844}, reducedMotion: 'reduce'});
      const p = await offline.newPage(); p.on('pageerror', error => errors.push(error.message));
      await p.route(`${base}/**`, route => {
        const pathname = new URL(route.request().url()).pathname;
        if (/^\/(predict|evidence|reports|model|health|boundary|sweep|experiments|datasets|scenario|api)(\/|$)/.test(pathname)) return route.abort('failed');
        return route.continue();
      });
      await p.goto(frontend);
      await p.waitForFunction(() => /Backend unavailable|Live estimate unavailable/.test(document.getElementById('status-text').textContent));
      await p.locator('#research-model-panel > summary').click();
      assert.match(await p.locator('#state-tier-label').innerText(), /PUBLISHED NASA BOUNDARY/);
      assert.equal((await p.locator('#val-prob-spread').innerText()).toLowerCase(), 'n/a');
      await p.locator('#tab-coverage-btn').click();
      await p.waitForFunction(() => document.getElementById('coverage-status').textContent.includes('unavailable'));
      await p.locator('#tab-conflict-btn').click();
      await p.waitForFunction(() => document.getElementById('conflict-status').textContent.includes('unavailable'));
      await p.screenshot({path: path.join(output, 'offline-mobile.png')});
      await offline.close();
    });
    assert.deepEqual(errors, [], 'Browser or server errors');
  } catch (error) {
    failure = error.stack || String(error);
    if (page && !page.isClosed()) await page.screenshot({path: path.join(output, 'failure.png')}).catch(() => {});
    throw error;
  } finally {
    fs.writeFileSync(path.join(output, 'results.json'), JSON.stringify({base, frontend, checks, errors, failure}, null, 2));
    if (browser) await browser.close();
    if (server) server.kill('SIGTERM');
  }
})().catch(async error => {
  console.error(error);
  if (page && !page.isClosed()) await page.screenshot({path: path.join(output, 'failure.png')}).catch(() => {});
  process.exitCode = 1;
});
