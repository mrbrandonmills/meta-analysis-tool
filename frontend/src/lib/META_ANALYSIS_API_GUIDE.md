# Meta-Analysis API Client Guide

This guide explains the updated Meta-Analysis API client and how to use it in your frontend application.

## Overview

The Meta-Analysis API client has been completely updated to match the current backend endpoints. The old project-based endpoints have been replaced with a new workflow-based architecture.

## What Changed

### Old Endpoints (Removed)
```typescript
// These endpoints NO LONGER EXIST
/meta-analysis/{projectId}/search
/meta-analysis/{projectId}/screen
/meta-analysis/{projectId}/credibility
/meta-analysis/{projectId}/extract
/meta-analysis/{projectId}/analyze
/meta-analysis/{projectId}/prisma
```

### New Endpoints (Current)
```typescript
POST   /api/v1/meta-analysis/create         // Create new meta-analysis
POST   /api/v1/meta-analysis/execute/{id}   // Execute the workflow
GET    /api/v1/meta-analysis/status/{id}    // Get current status
GET    /api/v1/meta-analysis/audit/{id}     // Get audit trail
POST   /api/v1/meta-analysis/ask            // Ask Q&A questions
GET    /api/v1/meta-analysis/report/{id}    // Get final report
```

## API Methods

### 1. createMetaAnalysis()

Creates a new meta-analysis and initializes the coordinator agent.

**Signature:**
```typescript
createMetaAnalysis(data: MetaAnalysisRequest): Promise<MetaAnalysisResponse>
```

**Request Type:**
```typescript
interface MetaAnalysisRequest {
  research_question: string;
  topic: string;
  inclusion_criteria?: string[];
  exclusion_criteria?: string[];
  databases?: string[];
  peer_review_only?: boolean;
  expert_name?: string | null;
}
```

**Response Type:**
```typescript
interface MetaAnalysisResponse {
  id: string;
  status: string;
  message: string;
  workflow: {
    research_question: string;
    workflow_steps: string[];
    timeline_days: number;
    resources_required: string[];
    expected_outcomes: string[];
  };
}
```

**Example:**
```typescript
import { metaAnalysisApi } from '@/lib/api';

const response = await metaAnalysisApi.createMetaAnalysis({
  research_question: 'What are the effects of mindfulness on anxiety?',
  topic: 'Mindfulness and Anxiety',
  inclusion_criteria: [
    'Randomized controlled trials',
    'Adult participants',
  ],
  exclusion_criteria: [
    'Non-English publications',
    'Case studies',
  ],
  databases: ['pubmed', 'arxiv', 'europepmc'],
  peer_review_only: true,
  expert_name: 'Dr. Sarah Chen',
});

const analysisId = response.id; // Save this for later use
```

---

### 2. executeMetaAnalysis()

Executes the meta-analysis workflow (search, screening, credibility assessment).

**Signature:**
```typescript
executeMetaAnalysis(analysisId: string): Promise<ExecuteResponse>
```

**Response Type:**
```typescript
interface ExecuteResponse {
  analysis_id: string;
  status: string;
  search_results: {
    total_found: number;
    databases: string[];
  };
  screening_results: {
    total_screened: number;
    included: number;
    excluded: number;
    uncertain: number;
  };
  credibility_results: {
    total_evaluated: number;
    breakdown: {
      high_credibility: number;
      medium_credibility: number;
      low_credibility: number;
      preprints: number;
    };
    studies_with_scores: Array<{
      title: string;
      credibility_score: number;
      is_peer_reviewed: boolean;
      venue_type: string;
      red_flags: string[];
    }>;
  };
  next_steps: string[];
}
```

**Example:**
```typescript
const results = await metaAnalysisApi.executeMetaAnalysis(analysisId);

console.log(`Found ${results.search_results.total_found} studies`);
console.log(`Included ${results.screening_results.included} after screening`);
console.log(`High credibility: ${results.credibility_results.breakdown.high_credibility}`);
```

---

### 3. getStatus()

Gets the current status of a meta-analysis.

**Signature:**
```typescript
getStatus(analysisId: string): Promise<StatusResponse>
```

**Response Type:**
```typescript
interface StatusResponse {
  id: string;
  status: string;
  decisions: number;
}
```

**Example:**
```typescript
const status = await metaAnalysisApi.getStatus(analysisId);
console.log(`Status: ${status.status}`);
console.log(`Decisions made: ${status.decisions}`);
```

**Use Case: Polling**
```typescript
const pollStatus = async (analysisId: string) => {
  const interval = setInterval(async () => {
    const status = await metaAnalysisApi.getStatus(analysisId);

    if (status.status === 'completed') {
      clearInterval(interval);
      console.log('Analysis complete!');
    } else if (status.status === 'failed') {
      clearInterval(interval);
      console.error('Analysis failed!');
    }
  }, 2000);
};
```

---

### 4. getAuditTrail()

Gets the complete audit trail showing all agent decisions and reasoning.

**Signature:**
```typescript
getAuditTrail(analysisId: string): Promise<AuditResponse>
```

**Response Type:**
```typescript
interface AuditResponse {
  entries: AuditTrailEntry[];
}

interface AuditTrailEntry {
  timestamp: string;
  agent_id: string;
  agent_name: string;
  agent_role: string;
  action: string;
  decision?: any;
  input_data?: any;
  output_data?: any;
  reasoning?: string;
  confidence?: number;
}
```

**Example:**
```typescript
const audit = await metaAnalysisApi.getAuditTrail(analysisId);

audit.entries.forEach((entry) => {
  console.log(`[${entry.timestamp}] ${entry.agent_name}:`);
  console.log(`  Action: ${entry.action}`);
  console.log(`  Reasoning: ${entry.reasoning}`);
  console.log(`  Confidence: ${entry.confidence}`);
});
```

---

### 5. askQuestion()

Ask questions about the meta-analysis using the Q&A agent.

**Signature:**
```typescript
askQuestion(question: string, analysisId?: string | null): Promise<QAResponse>
```

**Response Type:**
```typescript
interface QAResponse {
  question: string;
  answer: string;
  confidence: number;
  sources: string[];
  follow_up_suggestions: string[];
}
```

**Example:**
```typescript
const qa = await metaAnalysisApi.askQuestion(
  'What search terms were used?',
  analysisId
);

console.log(`Q: ${qa.question}`);
console.log(`A: ${qa.answer}`);
console.log(`Confidence: ${qa.confidence}`);
console.log(`Sources: ${qa.sources.join(', ')}`);
console.log('\nFollow-up questions:');
qa.follow_up_suggestions.forEach((suggestion, i) => {
  console.log(`${i + 1}. ${suggestion}`);
});
```

---

### 6. getReport()

Gets the final APA-formatted report for the meta-analysis.

**Signature:**
```typescript
getReport(analysisId: string): Promise<ReportResponse>
```

**Response Type:**
```typescript
interface ReportResponse {
  id: string;
  status: string;
  format: string;
  sections: string[];
}
```

**Example:**
```typescript
const report = await metaAnalysisApi.getReport(analysisId);

console.log(`Report format: ${report.format}`);
console.log('Sections:');
report.sections.forEach((section) => {
  console.log(`  - ${section}`);
});
```

---

## Complete Workflow Example

Here's a complete example of running a meta-analysis from start to finish:

```typescript
import { metaAnalysisApi, MetaAnalysisRequest } from '@/lib/api';

async function runMetaAnalysis() {
  try {
    // 1. Create the meta-analysis
    console.log('Creating meta-analysis...');
    const request: MetaAnalysisRequest = {
      research_question: 'What are the effects of mindfulness on anxiety?',
      topic: 'Mindfulness and Anxiety',
      inclusion_criteria: [
        'Randomized controlled trials',
        'Adult participants (18+)',
        'Mindfulness interventions',
      ],
      exclusion_criteria: [
        'Non-English publications',
        'Case studies',
      ],
      databases: ['pubmed', 'arxiv', 'europepmc'],
      peer_review_only: true,
    };

    const createResponse = await metaAnalysisApi.createMetaAnalysis(request);
    const analysisId = createResponse.id;
    console.log(`Analysis created with ID: ${analysisId}`);

    // 2. Execute the workflow
    console.log('Executing workflow...');
    const executeResponse = await metaAnalysisApi.executeMetaAnalysis(analysisId);
    console.log(`Found ${executeResponse.search_results.total_found} studies`);
    console.log(`Included ${executeResponse.screening_results.included} studies`);

    // 3. Poll for completion
    console.log('Monitoring progress...');
    const pollInterval = setInterval(async () => {
      const status = await metaAnalysisApi.getStatus(analysisId);
      console.log(`Status: ${status.status}`);

      if (status.status === 'completed') {
        clearInterval(pollInterval);

        // 4. Get the audit trail
        const audit = await metaAnalysisApi.getAuditTrail(analysisId);
        console.log(`Audit trail: ${audit.entries.length} entries`);

        // 5. Ask questions
        const qa = await metaAnalysisApi.askQuestion(
          'What databases were searched?',
          analysisId
        );
        console.log(`Answer: ${qa.answer}`);

        // 6. Get the final report
        const report = await metaAnalysisApi.getReport(analysisId);
        console.log(`Report ready in ${report.format} format`);
      }
    }, 2000);
  } catch (error) {
    console.error('Meta-analysis failed:', error);
  }
}
```

---

## React Component Example

Here's how to use the API in a React component:

```typescript
import React, { useState } from 'react';
import { metaAnalysisApi, MetaAnalysisRequest } from '@/lib/api';

export function MetaAnalysisForm() {
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>('idle');
  const [results, setResults] = useState<any>(null);

  const handleSubmit = async (formData: MetaAnalysisRequest) => {
    try {
      setStatus('creating');

      // Create analysis
      const createResponse = await metaAnalysisApi.createMetaAnalysis(formData);
      setAnalysisId(createResponse.id);

      // Execute analysis
      setStatus('executing');
      const executeResponse = await metaAnalysisApi.executeMetaAnalysis(createResponse.id);
      setResults(executeResponse);

      // Start polling
      setStatus('monitoring');
      pollStatus(createResponse.id);
    } catch (error) {
      setStatus('error');
      console.error(error);
    }
  };

  const pollStatus = (id: string) => {
    const interval = setInterval(async () => {
      const statusResponse = await metaAnalysisApi.getStatus(id);

      if (statusResponse.status === 'completed') {
        clearInterval(interval);
        setStatus('completed');
      } else if (statusResponse.status === 'failed') {
        clearInterval(interval);
        setStatus('failed');
      }
    }, 2000);
  };

  return (
    <div>
      <h2>Meta-Analysis</h2>
      <p>Status: {status}</p>

      {results && (
        <div>
          <p>Total found: {results.search_results.total_found}</p>
          <p>Included: {results.screening_results.included}</p>
          <p>Excluded: {results.screening_results.excluded}</p>
        </div>
      )}
    </div>
  );
}
```

---

## Error Handling

All API methods include automatic error handling through the axios interceptor:

- **401 Unauthorized**: Automatically attempts token refresh
- **429 Rate Limited**: Shows toast notification with retry time
- **400/403/404/500**: Shows appropriate error messages

You can also add custom error handling:

```typescript
try {
  await metaAnalysisApi.createMetaAnalysis(data);
} catch (error: any) {
  if (error.response) {
    // Server error
    console.error('Server error:', error.response.status);
    console.error('Details:', error.response.data);
  } else if (error.request) {
    // Network error
    console.error('Network error - no response');
  } else {
    // Other error
    console.error('Error:', error.message);
  }
}
```

---

## Authentication

The API client automatically includes authentication headers from localStorage:

```typescript
// Authentication is handled automatically by the axios interceptor
// No need to manually add headers

// To check if user is authenticated:
import { isAuthenticated } from '@/lib/api';

if (isAuthenticated()) {
  // User is logged in
}
```

---

## TypeScript Benefits

All API methods are fully typed, providing:

1. **Autocomplete**: Your IDE will suggest available methods and properties
2. **Type Safety**: TypeScript will catch type errors at compile time
3. **Documentation**: Hover over methods to see their signatures
4. **Refactoring**: Rename safely with IDE refactoring tools

Example of type safety:

```typescript
const response = await metaAnalysisApi.createMetaAnalysis({
  research_question: 'My question',
  topic: 'My topic',
  // TypeScript will error if you forget required fields
  // or use incorrect types
});

// TypeScript knows the response structure
const id: string = response.id; // ✓ Correct
const id: number = response.id; // ✗ Type error
```

---

## Migration Guide

If you have existing code using the old API, here's how to migrate:

### Before (Old API):
```typescript
// Old project-based approach
await metaAnalysisApi.search(projectId, searchParams);
await metaAnalysisApi.screen(projectId);
await metaAnalysisApi.assessCredibility(projectId);
```

### After (New API):
```typescript
// New workflow-based approach
const response = await metaAnalysisApi.createMetaAnalysis({
  research_question: 'Your question',
  topic: 'Your topic',
  // ... other fields
});

const analysisId = response.id;
await metaAnalysisApi.executeMetaAnalysis(analysisId);

// Poll for status
const status = await metaAnalysisApi.getStatus(analysisId);
```

---

## Best Practices

1. **Save the Analysis ID**: Store the ID returned from `createMetaAnalysis()` for all subsequent operations
2. **Poll for Status**: Use `getStatus()` in a polling loop to monitor long-running analyses
3. **Handle Errors**: Always wrap API calls in try-catch blocks
4. **Use TypeScript Types**: Import and use the provided TypeScript interfaces
5. **Check Authentication**: Verify user is authenticated before making requests
6. **Clean Up Intervals**: Always clear polling intervals when components unmount

---

## Additional Resources

- **API Examples**: See `/frontend/src/lib/api-examples.ts` for comprehensive examples
- **Backend Routes**: See `/backend/app/api/v1/meta_analysis.py` for endpoint details
- **Type Definitions**: See `/frontend/src/lib/api.ts` for all TypeScript types

---

## Support

If you encounter issues:

1. Check the browser console for detailed error messages
2. Verify the API_BASE_URL is correct in your environment
3. Ensure you're authenticated (check localStorage for access_token)
4. Review the backend logs for server-side errors
5. Check that the backend endpoints are running and accessible
