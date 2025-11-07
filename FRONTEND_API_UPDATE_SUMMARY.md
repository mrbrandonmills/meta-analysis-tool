# Frontend API Client Update - Summary

## Date: 2025-11-06

## Overview
Updated the frontend API client (`/frontend/src/lib/api.ts`) to match the current backend endpoints. The old project-based endpoints have been replaced with a new workflow-based architecture.

---

## Changes Made

### 1. Updated `/frontend/src/lib/api.ts`

#### Removed Old Methods:
- `search(projectId, searchParams)` - Old endpoint: `/meta-analysis/{projectId}/search`
- `screen(projectId)` - Old endpoint: `/meta-analysis/{projectId}/screen`
- `assessCredibility(projectId)` - Old endpoint: `/meta-analysis/{projectId}/credibility`
- `extractData(projectId)` - Old endpoint: `/meta-analysis/{projectId}/extract`
- `analyze(projectId)` - Old endpoint: `/meta-analysis/{projectId}/analyze`
- `getPrismaFlow(projectId)` - Old endpoint: `/meta-analysis/{projectId}/prisma`

#### Added New Methods:
- `createMetaAnalysis(data)` - POST `/api/v1/meta-analysis/create`
- `executeMetaAnalysis(analysisId)` - POST `/api/v1/meta-analysis/execute/{analysisId}`
- `getStatus(analysisId)` - GET `/api/v1/meta-analysis/status/{analysisId}`
- `getAuditTrail(analysisId)` - GET `/api/v1/meta-analysis/audit/{analysisId}`
- `askQuestion(question, analysisId?)` - POST `/api/v1/meta-analysis/ask`
- `getReport(analysisId)` - GET `/api/v1/meta-analysis/report/{analysisId}`

#### Added TypeScript Interfaces:
- `MetaAnalysisRequest` - Request payload for creating meta-analysis
- `MetaAnalysisResponse` - Response from creating meta-analysis
- `ExecuteResponse` - Response from executing meta-analysis
- `StatusResponse` - Response from status endpoint
- `AuditTrailEntry` - Individual audit trail entry
- `AuditResponse` - Complete audit trail response
- `QARequest` - Request payload for Q&A endpoint
- `QAResponse` - Response from Q&A endpoint
- `ReportResponse` - Response from report endpoint

---

### 2. Created `/frontend/src/lib/api-examples.ts`

Comprehensive example file with 10 different usage examples:
1. Create a new meta-analysis
2. Execute a meta-analysis
3. Poll for status updates
4. Get audit trail
5. Ask questions (Q&A Agent)
6. Get final report
7. Complete workflow (end-to-end)
8. Error handling
9. Using with React component
10. TypeScript type usage

---

### 3. Created `/frontend/src/lib/META_ANALYSIS_API_GUIDE.md`

Comprehensive documentation including:
- Overview of changes
- Detailed API method documentation
- Request/response type definitions
- Complete workflow examples
- React component examples
- Error handling guide
- Authentication details
- TypeScript benefits
- Migration guide from old API
- Best practices

---

## Backend Endpoints (Current)

All endpoints are prefixed with `/api/v1`:

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/meta-analysis/create` | Create a new meta-analysis |
| POST | `/meta-analysis/execute/{analysis_id}` | Execute the workflow |
| GET | `/meta-analysis/status/{analysis_id}` | Get current status |
| GET | `/meta-analysis/audit/{analysis_id}` | Get audit trail |
| POST | `/meta-analysis/ask` | Ask Q&A questions |
| GET | `/meta-analysis/report/{analysis_id}` | Get final report |

---

## Key Differences: Old vs New

### Old Architecture (Project-Based):
```typescript
// Create project first
const project = await projectsApi.create({...});

// Run analysis steps on project
await metaAnalysisApi.search(project.id, {...});
await metaAnalysisApi.screen(project.id);
await metaAnalysisApi.assessCredibility(project.id);
```

### New Architecture (Workflow-Based):
```typescript
// Create analysis with all parameters
const analysis = await metaAnalysisApi.createMetaAnalysis({
  research_question: '...',
  topic: '...',
  inclusion_criteria: [...],
  exclusion_criteria: [...],
  databases: [...],
});

// Execute entire workflow
await metaAnalysisApi.executeMetaAnalysis(analysis.id);

// Monitor progress
const status = await metaAnalysisApi.getStatus(analysis.id);
```

---

## Migration Checklist

If you have components using the old API:

- [ ] Replace `metaAnalysisApi.search()` with `createMetaAnalysis()` + `executeMetaAnalysis()`
- [ ] Replace `metaAnalysisApi.screen()` with polling `getStatus()`
- [ ] Replace `metaAnalysisApi.assessCredibility()` with `getAuditTrail()` to view results
- [ ] Replace `metaAnalysisApi.extractData()` with workflow execution
- [ ] Replace `metaAnalysisApi.analyze()` with workflow execution
- [ ] Replace `metaAnalysisApi.getPrismaFlow()` with `getReport()`
- [ ] Update TypeScript types to use new interfaces
- [ ] Implement status polling for long-running operations
- [ ] Save and use `analysis_id` instead of `project_id`

---

## Example Usage

### Simple Example:
```typescript
import { metaAnalysisApi } from '@/lib/api';

// Create and execute
const analysis = await metaAnalysisApi.createMetaAnalysis({
  research_question: 'What are the effects of mindfulness on anxiety?',
  topic: 'Mindfulness and Anxiety',
  inclusion_criteria: ['RCT', 'Adults'],
  databases: ['pubmed', 'arxiv'],
});

const results = await metaAnalysisApi.executeMetaAnalysis(analysis.id);
console.log(`Found ${results.search_results.total_found} studies`);
```

### React Component Example:
```typescript
const [analysisId, setAnalysisId] = useState<string | null>(null);
const [status, setStatus] = useState('idle');

const handleCreate = async () => {
  const response = await metaAnalysisApi.createMetaAnalysis(formData);
  setAnalysisId(response.id);
  await metaAnalysisApi.executeMetaAnalysis(response.id);
  startPolling(response.id);
};

const startPolling = (id: string) => {
  const interval = setInterval(async () => {
    const statusResponse = await metaAnalysisApi.getStatus(id);
    if (statusResponse.status === 'completed') {
      clearInterval(interval);
      setStatus('completed');
    }
  }, 2000);
};
```

---

## Files Modified

1. `/frontend/src/lib/api.ts` - Updated metaAnalysisApi section (lines 276-443)

## Files Created

1. `/frontend/src/lib/api-examples.ts` - Comprehensive usage examples
2. `/frontend/src/lib/META_ANALYSIS_API_GUIDE.md` - Complete documentation
3. `/FRONTEND_API_UPDATE_SUMMARY.md` - This summary document

---

## Testing Recommendations

1. **Unit Tests**: Create tests for each API method
2. **Integration Tests**: Test the complete workflow
3. **Error Handling**: Test error scenarios (404, 500, network errors)
4. **Authentication**: Test with valid and invalid tokens
5. **Polling**: Test status polling and cleanup

Example test:
```typescript
import { metaAnalysisApi } from '@/lib/api';

describe('metaAnalysisApi', () => {
  it('should create a meta-analysis', async () => {
    const response = await metaAnalysisApi.createMetaAnalysis({
      research_question: 'Test question',
      topic: 'Test topic',
    });

    expect(response.id).toBeDefined();
    expect(response.status).toBe('workflow_created');
  });

  it('should execute a meta-analysis', async () => {
    const createResponse = await metaAnalysisApi.createMetaAnalysis({...});
    const executeResponse = await metaAnalysisApi.executeMetaAnalysis(createResponse.id);

    expect(executeResponse.analysis_id).toBe(createResponse.id);
    expect(executeResponse.search_results).toBeDefined();
  });
});
```

---

## Benefits of Update

1. **Type Safety**: Full TypeScript support with proper interfaces
2. **Better Error Handling**: Automatic error handling via axios interceptors
3. **Authentication**: Built-in token management and refresh
4. **Documentation**: Comprehensive examples and guides
5. **Maintainability**: Cleaner API structure matching backend
6. **Developer Experience**: Autocomplete and type checking in IDE
7. **Consistency**: All methods follow same naming conventions
8. **Future-Proof**: Easy to extend with new endpoints

---

## Next Steps

1. **Update Components**: Migrate any components using the old API
2. **Add Tests**: Create unit and integration tests
3. **Update Documentation**: Update any user-facing documentation
4. **Monitor Performance**: Track API response times and errors
5. **Gather Feedback**: Get developer feedback on new API structure

---

## Support

For questions or issues:
- Review the API Guide: `/frontend/src/lib/META_ANALYSIS_API_GUIDE.md`
- Check examples: `/frontend/src/lib/api-examples.ts`
- Backend routes: `/backend/app/api/v1/meta_analysis.py`
- Contact: Development Team

---

## Version History

- **v2.0** (2025-11-06): Complete rewrite to match new backend architecture
  - Removed project-based endpoints
  - Added workflow-based endpoints
  - Added TypeScript interfaces
  - Added comprehensive documentation

- **v1.0** (Previous): Original project-based implementation
