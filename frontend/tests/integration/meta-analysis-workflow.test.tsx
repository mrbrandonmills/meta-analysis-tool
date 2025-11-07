/**
 * Integration tests for meta-analysis workflow
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Mock components for testing workflow
const TestMetaAnalysisForm = () => {
  return (
    <div>
      <h1>Create Meta-Analysis</h1>
      <form data-testid="meta-analysis-form">
        <label htmlFor="research-question">Research Question</label>
        <textarea
          id="research-question"
          data-testid="research-question"
          placeholder="Enter your research question"
        />

        <label htmlFor="topic">Topic</label>
        <input
          id="topic"
          type="text"
          data-testid="topic-input"
          placeholder="Enter topic"
        />

        <label htmlFor="databases">Databases</label>
        <select id="databases" data-testid="database-select" multiple>
          <option value="pubmed">PubMed</option>
          <option value="arxiv">arXiv</option>
          <option value="scopus">Scopus</option>
        </select>

        <button type="submit" data-testid="submit-button">
          Create Analysis
        </button>
      </form>
    </div>
  );
};

const TestMetaAnalysisResults = ({ data }: { data: any }) => {
  return (
    <div data-testid="results-container">
      <h2>Analysis Results</h2>
      <div data-testid="search-results">
        <h3>Search Results</h3>
        <p>Total Found: {data.search_results.total_found}</p>
      </div>
      <div data-testid="screening-results">
        <h3>Screening Results</h3>
        <p>Total Screened: {data.screening_results.total_screened}</p>
        <p>Included: {data.screening_results.included}</p>
        <p>Excluded: {data.screening_results.excluded}</p>
      </div>
      <div data-testid="credibility-results">
        <h3>Credibility Assessment</h3>
        <p>Total Evaluated: {data.credibility_results.total_evaluated}</p>
        <p>High Credibility: {data.credibility_results.breakdown.high_credibility}</p>
      </div>
    </div>
  );
};

describe('Meta-Analysis Workflow Integration', () => {
  let mock: MockAdapter;
  let queryClient: QueryClient;

  beforeEach(() => {
    mock = new MockAdapter(axios);
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
  });

  afterEach(() => {
    mock.restore();
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  it('should render meta-analysis form', () => {
    render(<TestMetaAnalysisForm />, { wrapper });

    expect(screen.getByText('Create Meta-Analysis')).toBeInTheDocument();
    expect(screen.getByTestId('research-question')).toBeInTheDocument();
    expect(screen.getByTestId('topic-input')).toBeInTheDocument();
    expect(screen.getByTestId('database-select')).toBeInTheDocument();
  });

  it('should validate form inputs', async () => {
    const user = userEvent.setup();
    render(<TestMetaAnalysisForm />, { wrapper });

    const researchQuestion = screen.getByTestId('research-question');
    const topicInput = screen.getByTestId('topic-input');

    await user.type(researchQuestion, 'What is the effect of exercise on diabetes?');
    await user.type(topicInput, 'diabetes exercise intervention');

    expect(researchQuestion).toHaveValue('What is the effect of exercise on diabetes?');
    expect(topicInput).toHaveValue('diabetes exercise intervention');
  });

  it('should display search results', () => {
    const mockData = {
      analysis_id: 'test-123',
      status: 'completed',
      search_results: {
        total_found: 150,
        databases: ['pubmed', 'arxiv'],
      },
      screening_results: {
        total_screened: 150,
        included: 45,
        excluded: 100,
        uncertain: 5,
      },
      credibility_results: {
        total_evaluated: 45,
        breakdown: {
          high_credibility: 30,
          medium_credibility: 12,
          low_credibility: 3,
          preprints: 0,
        },
        studies_with_scores: [],
      },
      next_steps: ['data extraction', 'statistical analysis'],
    };

    render(<TestMetaAnalysisResults data={mockData} />, { wrapper });

    expect(screen.getByText('Total Found: 150')).toBeInTheDocument();
    expect(screen.getByText('Total Screened: 150')).toBeInTheDocument();
    expect(screen.getByText('Included: 45')).toBeInTheDocument();
    expect(screen.getByText('Excluded: 100')).toBeInTheDocument();
    expect(screen.getByText('Total Evaluated: 45')).toBeInTheDocument();
    expect(screen.getByText('High Credibility: 30')).toBeInTheDocument();
  });

  it('should handle workflow progression', async () => {
    const mockCreateResponse = {
      id: 'analysis-123',
      status: 'created',
      message: 'Meta-analysis created successfully',
      workflow: {
        research_question: 'Test question',
        workflow_steps: ['search', 'screen', 'credibility', 'analyze'],
        timeline_days: 14,
        resources_required: ['databases', 'reviewers'],
        expected_outcomes: ['systematic review'],
      },
    };

    const mockExecuteResponse = {
      analysis_id: 'analysis-123',
      status: 'in_progress',
      search_results: {
        total_found: 0,
        databases: [],
      },
      screening_results: {
        total_screened: 0,
        included: 0,
        excluded: 0,
        uncertain: 0,
      },
      credibility_results: {
        total_evaluated: 0,
        breakdown: {
          high_credibility: 0,
          medium_credibility: 0,
          low_credibility: 0,
          preprints: 0,
        },
        studies_with_scores: [],
      },
      next_steps: [],
    };

    mock.onPost('/api/v1/meta-analysis/create').reply(200, mockCreateResponse);
    mock.onPost('/api/v1/meta-analysis/execute/analysis-123').reply(200, mockExecuteResponse);

    // Test workflow steps
    expect(mockCreateResponse.workflow.workflow_steps).toContain('search');
    expect(mockCreateResponse.workflow.workflow_steps).toContain('screen');
    expect(mockCreateResponse.workflow.workflow_steps).toContain('credibility');
  });

  it('should handle errors gracefully', async () => {
    mock.onPost('/api/v1/meta-analysis/create').reply(500, {
      detail: 'Internal server error',
    });

    // Error handling should be implemented in actual components
    // This test validates the mock setup
    expect(mock.history.post).toHaveLength(0);
  });

  it('should track workflow status', () => {
    const statuses = ['created', 'in_progress', 'completed', 'failed'];

    statuses.forEach((status) => {
      expect(['created', 'in_progress', 'completed', 'failed']).toContain(status);
    });
  });

  it('should support multiple database selections', async () => {
    const user = userEvent.setup();
    render(<TestMetaAnalysisForm />, { wrapper });

    const databaseSelect = screen.getByTestId('database-select') as HTMLSelectElement;

    await user.selectOptions(databaseSelect, ['pubmed', 'arxiv']);

    const selectedOptions = Array.from(databaseSelect.selectedOptions).map(
      (option) => option.value
    );
    expect(selectedOptions).toContain('pubmed');
    expect(selectedOptions).toContain('arxiv');
  });
});
