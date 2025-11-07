import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { StatisticsPanel } from '@/components/visualizations/StatisticsPanel';
import { sampleMetaAnalysisResults } from '@/data/sampleMetaAnalysis';

describe('StatisticsPanel', () => {
  it('renders the statistics panel title', () => {
    render(<StatisticsPanel results={sampleMetaAnalysisResults} />);

    expect(screen.getByText('Meta-Analysis Statistics')).toBeInTheDocument();
  });

  it('displays model type', () => {
    render(<StatisticsPanel results={sampleMetaAnalysisResults} />);

    expect(screen.getByText(/Random Effects Model/i)).toBeInTheDocument();
  });

  it('shows overall effect section', () => {
    render(<StatisticsPanel results={sampleMetaAnalysisResults} />);

    expect(screen.getByText(/Overall Effect/i)).toBeInTheDocument();
  });

  it('shows heterogeneity assessment section', () => {
    render(<StatisticsPanel results={sampleMetaAnalysisResults} />);

    expect(screen.getByText(/Heterogeneity Assessment/i)).toBeInTheDocument();
  });

  it('toggles sections on click', () => {
    render(<StatisticsPanel results={sampleMetaAnalysisResults} />);

    // Find the heterogeneity section button
    const heterogeneityButton = screen.getByText(/Heterogeneity Assessment/i).closest('button');

    if (heterogeneityButton) {
      // Initially should be expanded (showing I² statistic)
      expect(screen.getByText(/I² statistic/i)).toBeInTheDocument();

      // Click to collapse
      fireEvent.click(heterogeneityButton);

      // Should be collapsed now
      expect(screen.queryByText(/I² statistic/i)).not.toBeInTheDocument();

      // Click to expand again
      fireEvent.click(heterogeneityButton);

      // Should be expanded again
      expect(screen.getByText(/I² statistic/i)).toBeInTheDocument();
    }
  });

  it('displays publication bias section when available', () => {
    render(<StatisticsPanel results={sampleMetaAnalysisResults} />);

    // Click to expand publication bias section
    const publicationButton = screen.getByText(/Publication Bias/i).closest('button');
    if (publicationButton) {
      fireEvent.click(publicationButton);
      expect(screen.getByText(/Egger's Regression Test/i)).toBeInTheDocument();
    }
  });

  it('shows subgroup analyses when enabled and available', () => {
    render(
      <StatisticsPanel
        results={sampleMetaAnalysisResults}
        showSubgroups={true}
      />
    );

    if (sampleMetaAnalysisResults.subgroupAnalyses) {
      expect(screen.getByText(/Subgroup Analyses/i)).toBeInTheDocument();
    }
  });

  it('hides subgroup analyses when disabled', () => {
    render(
      <StatisticsPanel
        results={sampleMetaAnalysisResults}
        showSubgroups={false}
      />
    );

    expect(screen.queryByText(/Subgroup Analyses/i)).not.toBeInTheDocument();
  });

  it('shows sensitivity analyses when enabled and available', () => {
    render(
      <StatisticsPanel
        results={sampleMetaAnalysisResults}
        showSensitivity={true}
      />
    );

    if (sampleMetaAnalysisResults.sensitivityAnalyses) {
      expect(screen.getByText(/Sensitivity Analyses/i)).toBeInTheDocument();
    }
  });

  it('hides sensitivity analyses when disabled', () => {
    render(
      <StatisticsPanel
        results={sampleMetaAnalysisResults}
        showSensitivity={false}
      />
    );

    expect(screen.queryByText(/Sensitivity Analyses/i)).not.toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <StatisticsPanel
        results={sampleMetaAnalysisResults}
        className="custom-stats"
      />
    );

    const wrapper = container.querySelector('.custom-stats');
    expect(wrapper).toBeInTheDocument();
  });

  it('displays heterogeneity interpretation', () => {
    render(<StatisticsPanel results={sampleMetaAnalysisResults} />);

    // The interpretation should be visible in the heterogeneity section
    // Look for common interpretations like "Low", "Moderate", "Substantial", or "Considerable"
    const hasInterpretation =
      screen.queryByText(/Low heterogeneity/i) ||
      screen.queryByText(/Moderate heterogeneity/i) ||
      screen.queryByText(/Substantial heterogeneity/i) ||
      screen.queryByText(/Considerable heterogeneity/i);

    expect(hasInterpretation).toBeInTheDocument();
  });
});
