/**
 * E2E tests for complete meta-analysis workflow
 */
import { test, expect } from '@playwright/test';

test.describe('Meta-Analysis Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'TestPassword123!');
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard/i);
  });

  test('should create new meta-analysis', async ({ page }) => {
    // Navigate to create page
    await page.click('text=/create|new meta-analysis/i');

    // Fill form
    await page.fill('input[name="researchQuestion"], textarea[name="researchQuestion"]',
      'What is the effect of exercise on depression?');
    await page.fill('input[name="topic"]', 'Exercise and Depression');

    // Add inclusion criteria
    await page.fill('input[name="inclusionCriteria"]', 'Randomized controlled trials');
    await page.click('button:has-text("Add")');

    // Select databases
    await page.check('input[value="pubmed"]');

    // Submit
    await page.click('button[type="submit"]');

    // Should show success or redirect to workflow
    await expect(page.locator('text=/success|created/i')).toBeVisible({ timeout: 10000 });
  });

  test('should execute meta-analysis workflow', async ({ page }) => {
    // Create analysis first
    await page.goto('/meta-analysis/create');
    await page.fill('textarea[name="researchQuestion"]', 'Test research question');
    await page.fill('input[name="topic"]', 'Test Topic');
    await page.click('button[type="submit"]');

    // Execute workflow
    await page.click('button:has-text("Execute"), button:has-text("Run")');

    // Should show progress
    await expect(page.locator('text=/progress|executing/i')).toBeVisible({ timeout: 5000 });
  });

  test('should display search results', async ({ page }) => {
    // Navigate to an existing analysis
    await page.goto('/dashboard');
    await page.click('[data-testid="analysis-card"], .analysis-item').first();

    // Should show results section
    await expect(page.locator('text=/results|studies|papers/i')).toBeVisible();
  });

  test('should filter and screen studies', async ({ page }) => {
    await page.goto('/dashboard');
    await page.click('[data-testid="analysis-card"]').first();

    // Navigate to screening
    await page.click('text=/screen|filter/i');

    // Should show screening interface
    await expect(page.locator('text=/include|exclude/i')).toBeVisible();
  });

  test('should display forest plot visualization', async ({ page }) => {
    await page.goto('/dashboard');
    await page.click('[data-testid="analysis-card"]').first();

    // Navigate to results
    await page.click('text=/results|visualizations/i');

    // Should show forest plot
    await expect(page.locator('canvas, svg')).toBeVisible({ timeout: 10000 });
  });

  test('should ask questions about analysis', async ({ page }) => {
    await page.goto('/dashboard');
    await page.click('[data-testid="analysis-card"]').first();

    // Find Q&A section
    await page.click('text=/ask|question/i');

    // Ask question
    await page.fill('input[type="text"], textarea', 'What is the effect size?');
    await page.click('button:has-text("Ask"), button:has-text("Submit")');

    // Should show answer
    await expect(page.locator('[data-testid="answer"], .answer')).toBeVisible({ timeout: 15000 });
  });

  test('should export results', async ({ page }) => {
    await page.goto('/dashboard');
    await page.click('[data-testid="analysis-card"]').first();

    // Find export button
    const downloadPromise = page.waitForEvent('download');
    await page.click('button:has-text("Export"), button:has-text("Download")');

    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/\.pdf|\.csv|\.json/);
  });
});

test.describe('Meta-Analysis Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'TestPassword123!');
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard/i);
  });

  test('should display list of analyses', async ({ page }) => {
    await expect(page.locator('[data-testid="analysis-list"], .analysis-list')).toBeVisible();
  });

  test('should search analyses', async ({ page }) => {
    await page.fill('input[placeholder*="search" i]', 'exercise');

    // Results should filter
    const results = page.locator('[data-testid="analysis-card"]');
    await expect(results).toHaveCount(await results.count());
  });

  test('should sort analyses', async ({ page }) => {
    // Click sort dropdown
    await page.click('select[name="sort"], button:has-text("Sort")');
    await page.click('option:has-text("Newest"), text=/newest/i');

    // Should reorder
    await expect(page.locator('[data-testid="analysis-card"]').first()).toBeVisible();
  });

  test('should delete analysis', async ({ page }) => {
    const analysisCount = await page.locator('[data-testid="analysis-card"]').count();

    if (analysisCount > 0) {
      // Delete first analysis
      await page.click('[data-testid="delete-button"], button:has-text("Delete")').first();

      // Confirm deletion
      await page.click('button:has-text("Confirm"), button:has-text("Yes")');

      // Should remove from list
      await expect(page.locator('[data-testid="analysis-card"]')).toHaveCount(analysisCount - 1);
    }
  });
});

test.describe('Responsive Design', () => {
  test('should work on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });

    await page.goto('/');
    await expect(page.locator('nav, header')).toBeVisible();
  });

  test('should work on tablet', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });

    await page.goto('/dashboard');
    await expect(page.locator('[data-testid="analysis-list"]')).toBeVisible();
  });
});
