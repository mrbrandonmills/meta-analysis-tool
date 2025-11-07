/**
 * Unit tests for API client
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import {
  authApi,
  metaAnalysisApi,
  projectsApi,
  healthApi,
  setTokens,
  clearTokens,
  getAccessToken,
  isAuthenticated,
} from '@/lib/api';

describe('API Client', () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(axios);
    clearTokens();
    localStorage.clear();
  });

  afterEach(() => {
    mock.restore();
  });

  describe('Token Management', () => {
    it('should store and retrieve access token', () => {
      const token = 'test-access-token';
      setTokens(token, 'refresh-token');

      expect(getAccessToken()).toBe(token);
      expect(isAuthenticated()).toBe(true);
    });

    it('should clear tokens', () => {
      setTokens('access-token', 'refresh-token');
      expect(isAuthenticated()).toBe(true);

      clearTokens();
      expect(isAuthenticated()).toBe(false);
      expect(getAccessToken()).toBeNull();
    });
  });

  describe('Auth API', () => {
    it('should login successfully', async () => {
      const mockResponse = {
        access_token: 'test-access-token',
        refresh_token: 'test-refresh-token',
        token_type: 'bearer',
        user: {
          id: '1',
          email: 'test@example.com',
          name: 'Test User',
          role: 'researcher',
        },
      };

      mock.onPost('/api/v1/auth/login').reply(200, mockResponse);

      const result = await authApi.login({
        username: 'test@example.com',
        password: 'password123',
      });

      expect(result).toEqual(mockResponse);
      expect(getAccessToken()).toBe('test-access-token');
    });

    it('should handle login failure', async () => {
      mock.onPost('/api/v1/auth/login').reply(401, {
        detail: 'Invalid credentials',
      });

      await expect(
        authApi.login({
          username: 'test@example.com',
          password: 'wrongpassword',
        })
      ).rejects.toThrow();
    });

    it('should register successfully', async () => {
      const mockResponse = {
        access_token: 'test-access-token',
        refresh_token: 'test-refresh-token',
        token_type: 'bearer',
        user: {
          id: '1',
          email: 'new@example.com',
          name: 'New User',
          role: 'researcher',
        },
      };

      mock.onPost('/api/v1/auth/register').reply(200, mockResponse);

      const result = await authApi.register({
        email: 'new@example.com',
        password: 'password123',
        name: 'New User',
        institution: 'Test University',
      });

      expect(result).toEqual(mockResponse);
      expect(getAccessToken()).toBe('test-access-token');
    });

    it('should get current user', async () => {
      setTokens('test-access-token', 'test-refresh-token');

      const mockUser = {
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        role: 'researcher',
      };

      mock.onGet('/api/v1/auth/me').reply(200, mockUser);

      const result = await authApi.getCurrentUser();
      expect(result).toEqual(mockUser);
    });
  });

  describe('Meta-Analysis API', () => {
    beforeEach(() => {
      setTokens('test-access-token', 'test-refresh-token');
    });

    it('should create meta-analysis', async () => {
      const mockResponse = {
        id: 'analysis-1',
        status: 'created',
        message: 'Meta-analysis created successfully',
        workflow: {
          research_question: 'Test question',
          workflow_steps: ['search', 'screen', 'analyze'],
          timeline_days: 14,
          resources_required: ['databases', 'reviewers'],
          expected_outcomes: ['systematic review'],
        },
      };

      mock.onPost('/api/v1/meta-analysis/create').reply(200, mockResponse);

      const result = await metaAnalysisApi.createMetaAnalysis({
        research_question: 'Test question',
        topic: 'Test topic',
        inclusion_criteria: ['criteria1'],
        exclusion_criteria: ['criteria2'],
      });

      expect(result).toEqual(mockResponse);
      expect(result.id).toBe('analysis-1');
    });

    it('should execute meta-analysis', async () => {
      const mockResponse = {
        analysis_id: 'analysis-1',
        status: 'completed',
        search_results: {
          total_found: 100,
          databases: ['pubmed', 'arxiv'],
        },
        screening_results: {
          total_screened: 100,
          included: 25,
          excluded: 70,
          uncertain: 5,
        },
        credibility_results: {
          total_evaluated: 25,
          breakdown: {
            high_credibility: 15,
            medium_credibility: 8,
            low_credibility: 2,
            preprints: 0,
          },
          studies_with_scores: [],
        },
        next_steps: ['data extraction'],
      };

      mock.onPost('/api/v1/meta-analysis/execute/analysis-1').reply(200, mockResponse);

      const result = await metaAnalysisApi.executeMetaAnalysis('analysis-1');
      expect(result).toEqual(mockResponse);
    });

    it('should get analysis status', async () => {
      const mockResponse = {
        id: 'analysis-1',
        status: 'in_progress',
        decisions: 5,
      };

      mock.onGet('/api/v1/meta-analysis/status/analysis-1').reply(200, mockResponse);

      const result = await metaAnalysisApi.getStatus('analysis-1');
      expect(result).toEqual(mockResponse);
    });

    it('should get audit trail', async () => {
      const mockResponse = {
        entries: [
          {
            timestamp: '2024-01-01T00:00:00Z',
            agent_id: 'agent-1',
            agent_name: 'Search Agent',
            agent_role: 'search',
            action: 'search_pubmed',
            decision: { include: true },
          },
        ],
      };

      mock.onGet('/api/v1/meta-analysis/audit/analysis-1').reply(200, mockResponse);

      const result = await metaAnalysisApi.getAuditTrail('analysis-1');
      expect(result).toEqual(mockResponse);
    });
  });

  describe('Projects API', () => {
    beforeEach(() => {
      setTokens('test-access-token', 'test-refresh-token');
    });

    it('should list projects', async () => {
      const mockResponse = {
        projects: [
          { id: '1', name: 'Project 1', status: 'active' },
          { id: '2', name: 'Project 2', status: 'completed' },
        ],
        total: 2,
      };

      mock.onGet('/api/v1/projects').reply(200, mockResponse);

      const result = await projectsApi.list();
      expect(result.projects).toHaveLength(2);
    });

    it('should get single project', async () => {
      const mockProject = {
        id: '1',
        name: 'Test Project',
        status: 'active',
        tool_type: 'meta_analysis',
      };

      mock.onGet('/api/v1/projects/1').reply(200, mockProject);

      const result = await projectsApi.get('1');
      expect(result).toEqual(mockProject);
    });

    it('should create project', async () => {
      const newProject = {
        name: 'New Project',
        tool_type: 'meta_analysis',
        description: 'Test description',
      };

      mock.onPost('/api/v1/projects').reply(201, { id: '3', ...newProject });

      const result = await projectsApi.create(newProject);
      expect(result.id).toBe('3');
      expect(result.name).toBe('New Project');
    });

    it('should delete project', async () => {
      mock.onDelete('/api/v1/projects/1').reply(204);

      await expect(projectsApi.delete('1')).resolves.not.toThrow();
    });
  });

  describe('Health API', () => {
    it('should check health', async () => {
      const mockResponse = {
        status: 'healthy',
        timestamp: '2024-01-01T00:00:00Z',
        version: '0.1.0',
      };

      mock.onGet('/api/v1/health').reply(200, mockResponse);

      const result = await healthApi.check();
      expect(result.status).toBe('healthy');
    });

    it('should get detailed health', async () => {
      const mockResponse = {
        status: 'healthy',
        services: {
          database: { status: 'healthy' },
          redis: { status: 'healthy' },
          anthropic_api: { status: 'healthy' },
        },
      };

      mock.onGet('/api/v1/health/detailed').reply(200, mockResponse);

      const result = await healthApi.detailed();
      expect(result.services).toBeDefined();
      expect(result.services.database.status).toBe('healthy');
    });
  });

  describe('Error Handling', () => {
    it('should handle 401 unauthorized', async () => {
      mock.onGet('/api/v1/auth/me').reply(401, { detail: 'Unauthorized' });

      await expect(authApi.getCurrentUser()).rejects.toThrow();
    });

    it('should handle 404 not found', async () => {
      mock.onGet('/api/v1/projects/nonexistent').reply(404, { detail: 'Not found' });

      await expect(projectsApi.get('nonexistent')).rejects.toThrow();
    });

    it('should handle 500 server error', async () => {
      mock.onGet('/api/v1/health').reply(500, { detail: 'Internal server error' });

      await expect(healthApi.check()).rejects.toThrow();
    });

    it('should handle network errors', async () => {
      mock.onGet('/api/v1/health').networkError();

      await expect(healthApi.check()).rejects.toThrow();
    });
  });
});
