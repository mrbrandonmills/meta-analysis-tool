# Meta-Analysis API - Quick Reference

## Import
```typescript
import { metaAnalysisApi } from '@/lib/api';
```

## Methods

### Create Meta-Analysis
```typescript
const response = await metaAnalysisApi.createMetaAnalysis({
  research_question: string,
  topic: string,
  inclusion_criteria?: string[],
  exclusion_criteria?: string[],
  databases?: string[],
  peer_review_only?: boolean,
  expert_name?: string | null,
});
// Returns: { id, status, message, workflow }
```

### Execute Meta-Analysis
```typescript
const response = await metaAnalysisApi.executeMetaAnalysis(analysisId);
// Returns: { analysis_id, status, search_results, screening_results, credibility_results, next_steps }
```

### Get Status
```typescript
const response = await metaAnalysisApi.getStatus(analysisId);
// Returns: { id, status, decisions }
```

### Get Audit Trail
```typescript
const response = await metaAnalysisApi.getAuditTrail(analysisId);
// Returns: { entries: [...] }
```

### Ask Question
```typescript
const response = await metaAnalysisApi.askQuestion(question, analysisId?);
// Returns: { question, answer, confidence, sources, follow_up_suggestions }
```

### Get Report
```typescript
const response = await metaAnalysisApi.getReport(analysisId);
// Returns: { id, status, format, sections }
```

## Complete Workflow

```typescript
// 1. Create
const analysis = await metaAnalysisApi.createMetaAnalysis({
  research_question: 'Your question',
  topic: 'Your topic',
  inclusion_criteria: ['Criterion 1', 'Criterion 2'],
  databases: ['pubmed', 'arxiv'],
});

// 2. Execute
await metaAnalysisApi.executeMetaAnalysis(analysis.id);

// 3. Poll Status
const interval = setInterval(async () => {
  const status = await metaAnalysisApi.getStatus(analysis.id);
  if (status.status === 'completed') {
    clearInterval(interval);
    // Get report
    const report = await metaAnalysisApi.getReport(analysis.id);
  }
}, 2000);
```

## React Hook Example

```typescript
import { useState, useEffect } from 'react';

function useMetaAnalysis() {
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>('idle');

  const create = async (data) => {
    const response = await metaAnalysisApi.createMetaAnalysis(data);
    setAnalysisId(response.id);
    return response;
  };

  const execute = async () => {
    if (!analysisId) return;
    await metaAnalysisApi.executeMetaAnalysis(analysisId);
    setStatus('executing');
  };

  useEffect(() => {
    if (status !== 'executing' || !analysisId) return;

    const interval = setInterval(async () => {
      const statusResponse = await metaAnalysisApi.getStatus(analysisId);
      if (statusResponse.status === 'completed') {
        setStatus('completed');
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [status, analysisId]);

  return { create, execute, status, analysisId };
}
```

## Endpoints Reference

| Method | Endpoint | Type |
|--------|----------|------|
| createMetaAnalysis | `/api/v1/meta-analysis/create` | POST |
| executeMetaAnalysis | `/api/v1/meta-analysis/execute/{id}` | POST |
| getStatus | `/api/v1/meta-analysis/status/{id}` | GET |
| getAuditTrail | `/api/v1/meta-analysis/audit/{id}` | GET |
| askQuestion | `/api/v1/meta-analysis/ask` | POST |
| getReport | `/api/v1/meta-analysis/report/{id}` | GET |
