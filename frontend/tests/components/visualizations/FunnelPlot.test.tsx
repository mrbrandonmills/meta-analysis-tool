import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { FunnelPlot } from '@/components/visualizations/FunnelPlot';
import { sampleMetaAnalysisResults } from '@/data/sampleMetaAnalysis';

describe('FunnelPlot', () => {
  const { studies, overallEffect, publicationBias } = sampleMetaAnalysisResults;

  it('renders the funnel plot with title', () => {
    render(
      <FunnelPlot
        studies={studies}
        overallEffect={overallEffect}
      />
    );

    expect(screen.getByText('Funnel Plot')).toBeInTheDocument();
  });

  it('displays publication bias test results when available', () => {
    render(
      <FunnelPlot
        studies={studies}
        overallEffect={overallEffect}
        publicationBias={publicationBias}
      />
    );

    expect(screen.getByText(/Egger's test:/i)).toBeInTheDocument();
  });

  it('shows warning for significant publication bias', () => {
    const biasedData = {
      ...publicationBias,
      eggersTest: {
        intercept: 2.5,
        pValue: 0.03, // significant
      },
    };

    render(
      <FunnelPlot
        studies={studies}
        overallEffect={overallEffect}
        publicationBias={biasedData}
      />
    );

    expect(screen.getByText(/Possible publication bias/i)).toBeInTheDocument();
  });

  it('displays trim and fill results when available', () => {
    render(
      <FunnelPlot
        studies={studies}
        overallEffect={overallEffect}
        publicationBias={publicationBias}
        showEggersLine={true}
      />
    );

    if (publicationBias?.trimAndFill) {
      expect(screen.getByText(/Trim and Fill:/i)).toBeInTheDocument();
    }
  });

  it('shows interpretation note', () => {
    render(
      <FunnelPlot
        studies={studies}
        overallEffect={overallEffect}
      />
    );

    expect(screen.getByText(/symmetric funnel-shaped distribution/i)).toBeInTheDocument();
  });

  it('renders legend items', () => {
    render(
      <FunnelPlot
        studies={studies}
        overallEffect={overallEffect}
        showContours={true}
        showEggersLine={true}
      />
    );

    expect(screen.getByText(/Individual studies/i)).toBeInTheDocument();
    expect(screen.getByText(/Overall effect/i)).toBeInTheDocument();
  });

  it('renders SVG with correct height', () => {
    const { container } = render(
      <FunnelPlot
        studies={studies}
        overallEffect={overallEffect}
        height={600}
      />
    );

    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
    expect(svg?.getAttribute('height')).toBe('600');
  });

  it('applies custom className', () => {
    const { container } = render(
      <FunnelPlot
        studies={studies}
        overallEffect={overallEffect}
        className="custom-funnel"
      />
    );

    const wrapper = container.querySelector('.custom-funnel');
    expect(wrapper).toBeInTheDocument();
  });

  it('renders correct number of data points', () => {
    const { container } = render(
      <FunnelPlot
        studies={studies}
        overallEffect={overallEffect}
      />
    );

    const circles = container.querySelectorAll('circle');
    expect(circles.length).toBe(studies.length);
  });
});
