import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const REPORT_DIR = path.resolve(
  __dirname,
  '../../../backend/tests/benchmarks/reports'
);

function ensureReportDir() {
  if (!fs.existsSync(REPORT_DIR)) {
    fs.mkdirSync(REPORT_DIR, { recursive: true });
  }
}

type ScenarioConfig = {
  id: string;
  researchQuestion: string;
  databases: string[];
  minStudies: number;
};

// Just the first scenario for smoke test
const smokeScenario: ScenarioConfig = {
  id: 'S1_mental_health_cbtherapy',
  researchQuestion:
    'What is the effect of CBT on depressive symptoms in adults compared to usual care?',
  databases: ['PubMed', 'PsycINFO'],
  minStudies: 5,
};

test('Smoke test - Single scenario E2E', async ({ page }) => {
  test.setTimeout(360000); // 6 minutes for entire test
  console.log(`▶ Running smoke test: ${smokeScenario.id}`);

  await page.goto('http://localhost:3000/tools/meta-analysis/new', { waitUntil: 'networkidle' });

  // Fill research question
  await page.getByTestId('research-question').fill(smokeScenario.researchQuestion);

  // Select databases
  for (const db of smokeScenario.databases) {
    await page.getByTestId('database-select').selectOption({ label: db });
  }

  // Fill min studies
  const minInput = page.getByTestId('min-studies');
  if (await minInput.isVisible().catch(() => false)) {
    await minInput.fill(String(smokeScenario.minStudies));
  }

  // Run meta-analysis
  await page.getByTestId('run-meta-analysis').click();

  // Wait for form to disappear (indicates submission was successful)
  await page.getByTestId('run-meta-analysis').waitFor({ state: 'hidden', timeout: 10000 });

  console.log('✅ Form submitted, waiting for progress tracker...');

  // Wait for progress tracker or results to appear
  // The page should show either the progress tracker or results
  await page.waitForTimeout(5000); // Give backend time to start processing

  console.log('⏳ Waiting for analysis to complete (up to 5 minutes)...');

  // Wait for results summary (extended timeout for meta-analysis processing)
  const summary = page.getByTestId('results-summary');
  await expect(summary).toBeVisible({ timeout: 300000 }); // 5 minutes

  // Verify summary has content
  const summaryText = await summary.textContent();
  expect(summaryText && summaryText.trim().length).toBeGreaterThan(0);

  // Download JSON and MD
  ensureReportDir();

  const jsonPath = path.join(REPORT_DIR, `${smokeScenario.id}.json`);
  const mdPath = path.join(REPORT_DIR, `${smokeScenario.id}.md`);

  // JSON download
  const [jsonDownload] = await Promise.all([
    page.waitForEvent('download'),
    page.getByTestId('download-json').click(),
  ]);
  await jsonDownload.saveAs(jsonPath);

  // Markdown download
  const [mdDownload] = await Promise.all([
    page.waitForEvent('download'),
    page.getByTestId('download-markdown').click(),
  ]);
  await mdDownload.saveAs(mdPath);

  console.log(`✅ Smoke test completed - Files saved to ${REPORT_DIR}`);
});
