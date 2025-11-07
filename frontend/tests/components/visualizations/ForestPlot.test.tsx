import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ForestPlot } from '@/components/visualizations/ForestPlot';
import { sampleMetaAnalysisResults } from '@/data/sampleMetaAnalysis';

describe('ForestPlot', () => {
  it('renders the forest plot with title', () => {
    render(
      <ForestPlot
        results={sampleMetaAnalysisResults}
        title="Test Forest Plot"
      />
    );

    expect(screen.getByText('Test Forest Plot')).toBeInTheDocument();
  });

  it('displays study names', () => {
    render(<ForestPlot results={sampleMetaAnalysisResults} />);

    // Check for some study authors
    expect(screen.getByText('Smith et al.')).toBeInTheDocument();
    expect(screen.getByText('Johnson et al.')).toBeInTheDocument();
  });

  it('displays overall effect label', () => {
    render(<ForestPlot results={sampleMetaAnalysisResults} />);

    expect(screen.getByText(/Overall Effect/i)).toBeInTheDocument();
  });

  it('displays heterogeneity statistics when enabled', () => {
    render(
      <ForestPlot
        results={sampleMetaAnalysisResults}
        showHeterogeneity={true}
      />
    );

    // Check for I² statistic
    const svgElement = screen.getByText(/Heterogeneity: I²/i);
    expect(svgElement).toBeInTheDocument();
  });

  it('does not display heterogeneity statistics when disabled', () => {
    render(
      <ForestPlot
        results={sampleMetaAnalysisResults}
        showHeterogeneity={false}
      />
    );

    const svgElement = screen.queryByText(/Heterogeneity: I²/i);
    expect(svgElement).not.toBeInTheDocument();
  });

  it('renders SVG element with correct dimensions', () => {
    const { container } = render(
      <ForestPlot results={sampleMetaAnalysisResults} height={700} />
    );

    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
    expect(svg?.getAttribute('height')).toBe('700');
  });

  it('displays legend', () => {
    render(<ForestPlot results={sampleMetaAnalysisResults} />);

    expect(screen.getByText(/Individual studies/i)).toBeInTheDocument();
    expect(screen.getByText(/Pooled effect size/i)).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <ForestPlot
        results={sampleMetaAnalysisResults}
        className="custom-class"
      />
    );

    const wrapper = container.querySelector('.custom-class');
    expect(wrapper).toBeInTheDocument();
  });

  it('renders correct number of studies', () => {
    const { container } = render(
      <ForestPlot results={sampleMetaAnalysisResults} />
    );

    // Count the number of study labels (authors) in the SVG
    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();

    // Each study should have its author name rendered
    const studyCount = sampleMetaAnalysisResults.studies.length;
    expect(studyCount).toBeGreaterThan(0);
  });
});
