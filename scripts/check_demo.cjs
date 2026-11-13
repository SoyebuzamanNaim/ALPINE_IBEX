/* Fresh-browser acceptance check against the exact submission URL and real API. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require('playwright');
const url = process.env.FLARE_DEMO_URL;
if (!url) throw new Error('Set FLARE_DEMO_URL to the exact public submission URL (or a local test URL).');
const output = process.env.FLARE_DEMO_OUTPUT || '/tmp/flare-demo';
fs.mkdirSync(output, {recursive: true});
const report = {submission_url: url, checked_at: new Date().toISOString(), checks: [], passed: false};
let browser, page;

async function openWorkbench(context) {
  const tab = await context.newPage();
  await tab.goto(url);
  // Both the Pages root redirect and a directly submitted workbench URL are supported.
  await tab.locator('#nlp-query-input, a[href="../app/"]').first().waitFor();
  if (new URL(tab.url()).pathname.includes('/project-page')) {
    await tab.getByRole('link', {name: 'Open the tool', exact: true}).first().click();
  }
  await tab.locator('#nlp-query-input').waitFor();
  await tab.waitForFunction(() => typeof API_BASE === 'string');
  return tab;
}

(async () => {
  try {
    browser = await chromium.launch({headless: true});
    const context = await browser.newContext({viewport: {width: 1440, height: 1000}, reducedMotion: 'reduce'});
    page = await openWorkbench(context);
    report.workbench_url = page.url();
    report.api_base = await page.evaluate(() => API_BASE || window.location.origin);
    if (process.env.FLARE_API_BASE) {
      assert.equal(report.api_base.replace(/\/$/, ''), process.env.FLARE_API_BASE.replace(/\/$/, ''));
    }
    const health = await page.evaluate(async () => {
      const response = await fetch(`${API_BASE}/health`);
      if (!response.ok) throw new Error(`API health returned HTTP ${response.status}`);
      return response.json();
    });
    assert.ok(health.dataset_rows > 0);
    report.checks.push('Reachable API from the submitted browser origin');

    await page.locator('#nlp-query-input').fill('PMMA at 19% oxygen, 101.3 kPa, 5 cm/s airflow');
    await page.locator('#nlp-query-submit').click();
    await page.waitForFunction(() => currentEvidence?.scenario.oxygen_pct === 19 && currentEvidence?.observations.length > 0);
    const result = await page.evaluate(async () => {
      const response = await fetch(`${API_BASE}/evidence`, {method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(currentEvidence.scenario)});
      if (!response.ok) throw new Error(`Evidence retrieval returned HTTP ${response.status}`);
      return response.json();
    });
    assert.deepEqual(result.scenario, {oxygen_pct: 19, pressure_kpa: 101.3, flow_cm_s: 5, material: 'PMMA'});
    assert.ok(result.nearest_experiments.length > 0);
    const selected = result.nearest_experiments[0];
    assert.equal(selected.interpretation.method, 'deterministic_record_template');
    assert.ok(selected.similarity_ranking.feature_ranges);
    const card = page.locator('.flight-obs-card').first();
    await card.waitFor();
    await page.waitForFunction(id => document.querySelector('.flight-obs-card .obs-id')?.textContent.includes(id), selected.experiment_id);
    assert.match(await card.innerText(), /What was observed:[\s\S]*Which conditions differ:[\s\S]*What cannot be concluded:/);
    assert.match(await card.innerText(), /Geometry:[\s\S]*Flow direction:[\s\S]*Ignition history:/);
    await card.locator('summary').click();
    assert.match(await card.innerText(), /material penalty[\s\S]*not more reliable/);
    assert.match(await card.locator('a').getAttribute('href'), /^https:\/\//);
    report.checks.push('Scenario → live similarity ranking → cited deterministic interpretation');

    await card.locator('.btn-trace-cite').click();
    await page.locator('#modal-citation-inspector').waitFor({state: 'visible'});
    await page.waitForFunction(() => !/LOADING|UNAVAILABLE/.test(document.getElementById('inspect-tier-pill').textContent));
    assert.match(await page.locator('#inspect-ntrs-url').getAttribute('href'), /^https:\/\//);
    await page.keyboard.press('Escape');
    report.checks.push('Original source provenance is reachable');
    await page.locator('.evidence-pane').evaluate(pane => { pane.scrollTop = 0; });
    await page.screenshot({path: path.join(output, 'evidence-desktop.png'), fullPage: true});

    await page.locator('#tab-coverage-btn').click();
    await page.waitForFunction(() => document.getElementById('coverage-status').textContent === '');
    assert.match(await page.locator('.gap-card').first().innerText(), /TEAM PROPOSAL/);
    assert.match(await page.locator('.heatmap-footnote').innerText(), /current FLARE-X dataset/);
    report.checks.push('Dataset-scoped coverage and team proposals');
    await page.screenshot({path: path.join(output, 'coverage-desktop.png'), fullPage: true});

    const mobileContext = await browser.newContext({viewport: {width: 390, height: 844}, reducedMotion: 'reduce'});
    const mobile = await openWorkbench(mobileContext);
    await mobile.locator('.flight-obs-card').first().waitFor();
    assert.ok(await mobile.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1));
    await mobile.screenshot({path: path.join(output, 'evidence-mobile.png'), fullPage: true});
    report.checks.push('Fresh mobile browser loads evidence without page overflow');
    report.passed = true;
    console.log(JSON.stringify(report, null, 2));
  } catch (error) {
    report.error = error.stack || error.message;
    if (page) await page.screenshot({path: path.join(output, 'failure.png'), fullPage: true}).catch(() => {});
    console.error(JSON.stringify(report, null, 2));
    process.exitCode = 1;
  } finally {
    fs.writeFileSync(path.join(output, 'report.json'), JSON.stringify(report, null, 2));
    if (browser) await browser.close();
  }
})();
