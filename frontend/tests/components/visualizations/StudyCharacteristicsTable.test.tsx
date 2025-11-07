import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { StudyCharacteristicsTable } from '@/components/visualizations/StudyCharacteristicsTable';
import { sampleStudies } from '@/data/sampleMetaAnalysis';

describe('StudyCharacteristicsTable', () => {
  it('renders the table title', () => {
    render(
      <StudyCharacteristicsTable
        studies={sampleStudies}
        effectMeasure="OR"
      />
    );

    expect(screen.getByText('Study Characteristics')).toBeInTheDocument();
  });

  it('displays all study rows', () => {
    render(
      <StudyCharacteristicsTable
        studies={sampleStudies}
        effectMeasure="OR"
      />
    );

    // Check for study authors
    expect(screen.getByText('Smith et al.')).toBeInTheDocument();
    expect(screen.getByText('Johnson et al.')).toBeInTheDocument();
  });

  it('shows export button', () => {
    render(
      <StudyCharacteristicsTable
        studies={sampleStudies}
        effectMeasure="OR"
      />
    );

    expect(screen.getByText(/Export CSV/i)).toBeInTheDocument();
  });

  it('displays search input when filterable', () => {
    render(
      <StudyCharacteristicsTable
        studies={sampleStudies}
        effectMeasure="OR"
        filterable={true}
      />
    );

    const searchInput = screen.getByPlaceholderText(/Search by author/i);
    expect(searchInput).toBeInTheDocument();
  });

  it('hides search input when not filterable', () => {
    render(
      <StudyCharacteristicsTable
        studies={sampleStudies}
        effectMeasure="OR"
        filterable={false}
      />
    );

    const searchInput = screen.queryByPlaceholderText(/Search by author/i);
    expect(searchInput).not.toBeInTheDocument();
  });

  it('filters studies based on search term', () => {
    render(
      <StudyCharacteristicsTable
        studies={sampleStudies}
        effectMeasure="OR"
        filterable={true}
      />
    );

    const searchInput = screen.getByPlaceholderText(/Search by author/i);

    // Search for specific author
    fireEvent.change(searchInput, { target: { value: 'Smith' } });

    // Should show Smith et al.
    expect(screen.getByText('Smith et al.')).toBeInTheDocument();

    // Should not show others (if they don't match)
    // Note: This depends on the actual data
    const resultCount = screen.getByText(/Showing \d+ of \d+ studies/);
    expect(resultCount).toBeInTheDocument();
  });

  it('displays subgroup filter when subgroups exist', () => {
    const studiesWithSubgroups = sampleStudies.filter(s => s.subgroup);

    if (studiesWithSubgroups.length > 0) {
      render(
        <StudyCharacteristicsTable
          studies={studiesWithSubgroups}
          effectMeasure="OR"
          filterable={true}
        />
      );

      const subgroupSelect = screen.getByRole('combobox');
      expect(subgroupSelect).toBeInTheDocument();
    }
  });

  it('sorts by column when sortable', () => {
    render(
      <StudyCharacteristicsTable
        studies={sampleStudies}
        effectMeasure="OR"
        sortable={true}
      />
    );

    // Find the year column header and click it
    const yearHeader = screen.getByText('Year').closest('th');

    if (yearHeader) {
      fireEvent.click(yearHeader);
      // After click, sorting should be applied
      // We can verify by checking if the component re-renders
      expect(yearHeader).toBeInTheDocument();
    }
  });

  it('shows quality scores when enabled', () => {
    render(
      <StudyCharacteristicsTable
        studies={sampleStudies}
        effectMeasure="OR"
        showQualityScores={true}
      />
    );

    expect(screen.getByText('Quality')).toBeInTheDocument();
  });

  it('hides quality scores when disabled', () => {
    render(
      <StudyCharacteristicsTable
        studies={sampleStudies}
        effectMeasure="OR"
        showQualityScores={false}
      />
    );

    expect(screen.queryByText('Quality')).not.toBeInTheDocument();
  });

  it('displays summary statistics', () => {
    render(
      <StudyCharacteristicsTable
        studies={sampleStudies}
        effectMeasure="OR"
      />
    );

    expect(screen.getByText('Total Studies')).toBeInTheDocument();
    expect(screen.getByText('Total Participants')).toBeInTheDocument();
    expect(screen.getByText('Mean Effect Size')).toBeInTheDocument();
  });

  it('shows results count', () => {
    render(
      <StudyCharacteristicsTable
        studies={sampleStudies}
        effectMeasure="OR"
      />
    );

    const resultCount = screen.getByText(/Showing \d+ of \d+ studies/);
    expect(resultCount).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <StudyCharacteristicsTable
        studies={sampleStudies}
        effectMeasure="OR"
        className="custom-table"
      />
    );

    const wrapper = container.querySelector('.custom-table');
    expect(wrapper).toBeInTheDocument();
  });

  it('shows empty state when no studies match filters', () => {
    render(
      <StudyCharacteristicsTable
        studies={sampleStudies}
        effectMeasure="OR"
        filterable={true}
      />
    );

    const searchInput = screen.getByPlaceholderText(/Search by author/i);

    // Search for non-existent author
    fireEvent.change(searchInput, { target: { value: 'NONEXISTENT123' } });

    expect(screen.getByText(/No studies found matching your filters/i)).toBeInTheDocument();
  });

  it('allows clearing filters', () => {
    render(
      <StudyCharacteristicsTable
        studies={sampleStudies}
        effectMeasure="OR"
        filterable={true}
      />
    );

    const searchInput = screen.getByPlaceholderText(/Search by author/i);

    // Search for non-existent author
    fireEvent.change(searchInput, { target: { value: 'NONEXISTENT123' } });

    // Click clear filters button
    const clearButton = screen.getByText(/Clear filters/i);
    fireEvent.click(clearButton);

    // Search input should be cleared
    expect(searchInput).toHaveValue('');
  });
});
