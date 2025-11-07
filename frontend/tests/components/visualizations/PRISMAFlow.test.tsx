import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { PRISMAFlow } from '@/components/visualizations/PRISMAFlow';
import { samplePRISMAFlowData } from '@/data/sampleMetaAnalysis';

describe('PRISMAFlow', () => {
  it('renders the PRISMA Flow Diagram title', () => {
    render(<PRISMAFlow data={samplePRISMAFlowData} />);

    expect(screen.getByText('PRISMA Flow Diagram')).toBeInTheDocument();
  });

  it('displays identification phase', () => {
    render(<PRISMAFlow data={samplePRISMAFlowData} />);

    expect(screen.getByText('Identification')).toBeInTheDocument();
    expect(screen.getByText(/Records identified through database searching/i)).toBeInTheDocument();
  });

  it('displays screening phase', () => {
    render(<PRISMAFlow data={samplePRISMAFlowData} />);

    expect(screen.getByText('Screening')).toBeInTheDocument();
    expect(screen.getByText(/Records screened/i)).toBeInTheDocument();
  });

  it('displays eligibility phase', () => {
    render(<PRISMAFlow data={samplePRISMAFlowData} />);

    expect(screen.getByText('Eligibility')).toBeInTheDocument();
    expect(screen.getByText(/Full-text articles assessed/i)).toBeInTheDocument();
  });

  it('displays included phase', () => {
    render(<PRISMAFlow data={samplePRISMAFlowData} />);

    expect(screen.getByText('Included')).toBeInTheDocument();
    expect(screen.getByText(/Studies included in qualitative synthesis/i)).toBeInTheDocument();
  });

  it('shows correct counts', () => {
    render(<PRISMAFlow data={samplePRISMAFlowData} />);

    // Check for specific numbers from sample data - use getAllByText since numbers appear in multiple places
    const recordsIdentifiedElements = screen.getAllByText(samplePRISMAFlowData.identification.recordsIdentified.toLocaleString());
    expect(recordsIdentifiedElements.length).toBeGreaterThan(0);

    const studiesIncludedElements = screen.getAllByText(samplePRISMAFlowData.included.studiesIncluded.toLocaleString());
    expect(studiesIncludedElements.length).toBeGreaterThan(0);
  });

  it('displays summary statistics', () => {
    render(<PRISMAFlow data={samplePRISMAFlowData} />);

    expect(screen.getByText('Initial Records')).toBeInTheDocument();
    expect(screen.getByText('Total Excluded')).toBeInTheDocument();
    expect(screen.getByText('Final Included')).toBeInTheDocument();
    expect(screen.getByText('Inclusion Rate')).toBeInTheDocument();
  });

  it('calculates inclusion rate correctly', () => {
    render(<PRISMAFlow data={samplePRISMAFlowData} />);

    const expectedRate = (
      (samplePRISMAFlowData.included.studiesIncluded /
        samplePRISMAFlowData.identification.recordsIdentified) *
      100
    ).toFixed(1);

    expect(screen.getByText(`${expectedRate}%`)).toBeInTheDocument();
  });

  it('shows PRISMA guidelines note', () => {
    render(<PRISMAFlow data={samplePRISMAFlowData} />);

    expect(screen.getByText(/PRISMA 2020 guidelines/i)).toBeInTheDocument();
  });

  it('shows interactive hint when interactive is true', () => {
    render(<PRISMAFlow data={samplePRISMAFlowData} interactive={true} />);

    expect(screen.getByText(/hover over boxes for details/i)).toBeInTheDocument();
  });

  it('hides interactive hint when interactive is false', () => {
    render(<PRISMAFlow data={samplePRISMAFlowData} interactive={false} />);

    expect(screen.queryByText(/hover over boxes for details/i)).not.toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <PRISMAFlow
        data={samplePRISMAFlowData}
        className="custom-prisma"
      />
    );

    const wrapper = container.querySelector('.custom-prisma');
    expect(wrapper).toBeInTheDocument();
  });

  it('shows meta-analysis count when provided', () => {
    const dataWithMA = {
      ...samplePRISMAFlowData,
      included: {
        ...samplePRISMAFlowData.included,
        studiesInMetaAnalysis: 10,
      },
    };

    render(<PRISMAFlow data={dataWithMA} />);

    expect(screen.getByText(/Studies included in quantitative synthesis/i)).toBeInTheDocument();
  });

  it('displays all phase labels', () => {
    render(<PRISMAFlow data={samplePRISMAFlowData} />);

    const phases = ['Identification', 'Screening', 'Eligibility', 'Included'];

    phases.forEach(phase => {
      expect(screen.getByText(phase)).toBeInTheDocument();
    });
  });

  it('calculates total excluded correctly', () => {
    render(<PRISMAFlow data={samplePRISMAFlowData} />);

    const expectedTotal =
      samplePRISMAFlowData.screening.recordsExcluded +
      samplePRISMAFlowData.eligibility.fullTextExcluded;

    expect(screen.getByText(expectedTotal.toLocaleString())).toBeInTheDocument();
  });
});
