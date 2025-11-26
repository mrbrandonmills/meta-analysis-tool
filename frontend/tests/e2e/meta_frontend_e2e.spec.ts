import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

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
  maxStudies?: number;
};

const scenarios: ScenarioConfig[] = [
  {
    id: 'S1_mental_health_cbtherapy',
    researchQuestion:
      'What is the effect of CBT on depressive symptoms in adults compared to usual care?',
    databases: ['PubMed', 'PsycINFO'],
    minStudies: 5,
  },
  {
    id: 'S2_nutrition_mediterranean',
    researchQuestion:
      'Does a Mediterranean diet reduce cardiovascular events in high-risk adults?',
    databases: ['PubMed', 'Cochrane'],
    minStudies: 5,
  },
  {
    id: 'S3_pain_opioid_alt',
    researchQuestion:
      'What is the effect of non-opioid interventions on chronic low back pain?',
    databases: ['PubMed', 'EMBASE'],
    minStudies: 5,
  },
  {
    id: 'S4_neurology_adhd',
    researchQuestion:
      'What is the effect of stimulant medication on ADHD symptoms in children?',
    databases: ['PubMed', 'CINAHL'],
    minStudies: 3,
  },
  {
    id: 'S5_ai_diagnostic',
    researchQuestion:
      'How accurate are AI-based diagnostic tools compared to radiologists?',
    databases: ['PubMed', 'IEEE Xplore'],
    minStudies: 4,
  },
  {
    id: 'S6_education_online_vs_inperson',
    researchQuestion:
      'Do online courses produce equivalent exam performance compared to in-person courses?',
    databases: ['ERIC', 'PsycINFO'],
    minStudies: 4,
  },
  {
    id: 'S7_sleep_insomnia',
    researchQuestion:
      'What is the effectiveness of CBT-I on insomnia severity compared to control?',
    databases: ['PubMed', 'Cochrane'],
    minStudies: 4,
  },
  {
    id: 'S8_anxiety_mindfulness',
    researchQuestion:
      'Does mindfulness-based stress reduction reduce anxiety symptoms in adults?',
    databases: ['PubMed', 'PsycINFO'],
    minStudies: 4,
  },
  {
    id: 'S9_obesity_exercise',
    researchQuestion:
      'What is the effect of structured exercise programs on BMI in adults with obesity?',
    databases: ['PubMed', 'SPORTDiscus'],
    minStudies: 4,
  },
  {
    id: 'S10_diabetes_glucose',
    researchQuestion:
      'How effective are GLP-1 agonists at lowering HbA1c in type 2 diabetes?',
    databases: ['PubMed', 'EMBASE'],
    minStudies: 4,
  },
];

async function runScenario(page, scenario: ScenarioConfig) {
  await page.goto('http://localhost:3000/tools/meta-analysis/new', { waitUntil: 'networkidle' });

  // Fill research question
  await page.getByTestId('research-question').fill(scenario.researchQuestion);

  // Select databases
  for (const db of scenario.databases) {
    await page.getByTestId('database-select').selectOption({ label: db });
  }

  // Optional: min studies input if present
  const minInput = page.getByTestId('min-studies');
  if (await minInput.isVisible().catch(() => false)) {
    await minInput.fill(String(scenario.minStudies));
  }

  // Run meta-analysis
  await page.getByTestId('run-meta-analysis').click();

  // Wait for results summary
  const summary = page.getByTestId('results-summary');
  await expect(summary).toBeVisible({ timeout: 120000 });

  // Basic sanity: summary text is non-empty
  const summaryText = await summary.textContent();
  expect(summaryText && summaryText.trim().length).toBeGreaterThan(0);

  // Download JSON and MD
  ensureReportDir();

  const jsonPath = path.join(REPORT_DIR, `${scenario.id}.json`);
  const mdPath = path.join(REPORT_DIR, `${scenario.id}.md`);

  // JSON
  const [jsonDownload] = await Promise.all([
    page.waitForEvent('download'),
    page.getByTestId('download-json').click(),
  ]);
  await jsonDownload.saveAs(jsonPath);

  // Markdown
  const [mdDownload] = await Promise.all([
    page.waitForEvent('download'),
    page.getByTestId('download-markdown').click(),
  ]);
  await mdDownload.saveAs(mdPath);
}

test.describe('Meta-analysis frontend E2E benchmark suite', () => {
  test('runs 10 benchmark scenarios end-to-end', async ({ page }) => {
    for (const scenario of scenarios) {
      // eslint-disable-next-line no-console
      console.log(`▶ Running scenario: ${scenario.id}`);
      await runScenario(page, scenario);
      // Small pause between runs to avoid overwhelming backend
      await page.waitForTimeout(2000);
    }
  });
});
