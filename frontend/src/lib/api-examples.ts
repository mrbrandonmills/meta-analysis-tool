/**
 * Meta-Analysis API Usage Examples
 *
 * This file demonstrates how to use the updated metaAnalysisApi client
 * to interact with the backend endpoints.
 */

import { metaAnalysisApi, MetaAnalysisRequest } from './api';

// ==============================================
// EXAMPLE 1: Create a New Meta-Analysis
// ==============================================

export async function createMetaAnalysisExample() {
  try {
    // Prepare the request data
    const requestData: MetaAnalysisRequest = {
      research_question: 'What are the effects of mindfulness meditation on anxiety in adults?',
      topic: 'Mindfulness and Anxiety',
      inclusion_criteria: [
        'Randomized controlled trials',
        'Adult participants (18+ years)',
        'Mindfulness-based interventions',
        'Anxiety as primary outcome measure',
      ],
      exclusion_criteria: [
        'Non-English language publications',
        'Qualitative studies',
        'Case studies or case series',
        'Pediatric populations',
      ],
      databases: ['pubmed', 'arxiv', 'europepmc', 'core'],
      peer_review_only: true,
      expert_name: 'Dr. Sarah Chen',
    };

    // Create the meta-analysis
    const response = await metaAnalysisApi.createMetaAnalysis(requestData);

    console.log('Meta-analysis created:', {
      id: response.id,
      status: response.status,
      message: response.message,
      workflow: response.workflow,
    });

    // Save the analysis ID for later use
    return response.id;
  } catch (error) {
    console.error('Failed to create meta-analysis:', error);
    throw error;
  }
}

// ==============================================
// EXAMPLE 2: Execute a Meta-Analysis
// ==============================================

export async function executeMetaAnalysisExample(analysisId: string) {
  try {
    // Execute the meta-analysis workflow
    const response = await metaAnalysisApi.executeMetaAnalysis(analysisId);

    console.log('Meta-analysis execution results:', {
      analysisId: response.analysis_id,
      status: response.status,
      searchResults: {
        totalFound: response.search_results.total_found,
        databases: response.search_results.databases,
      },
      screeningResults: {
        totalScreened: response.screening_results.total_screened,
        included: response.screening_results.included,
        excluded: response.screening_results.excluded,
        uncertain: response.screening_results.uncertain,
      },
      credibilityResults: {
        totalEvaluated: response.credibility_results.total_evaluated,
        breakdown: response.credibility_results.breakdown,
      },
      nextSteps: response.next_steps,
    });

    // Display credibility-assessed studies
    console.log('Studies with credibility scores:');
    response.credibility_results.studies_with_scores.forEach((study) => {
      console.log(`- ${study.title}`);
      console.log(`  Score: ${study.credibility_score}`);
      console.log(`  Peer Reviewed: ${study.is_peer_reviewed}`);
      console.log(`  Venue Type: ${study.venue_type}`);
      if (study.red_flags.length > 0) {
        console.log(`  Red Flags: ${study.red_flags.join(', ')}`);
      }
    });

    return response;
  } catch (error) {
    console.error('Failed to execute meta-analysis:', error);
    throw error;
  }
}

// ==============================================
// EXAMPLE 3: Poll for Status Updates
// ==============================================

export async function pollStatusExample(analysisId: string) {
  try {
    const pollInterval = 2000; // 2 seconds
    const maxPolls = 150; // 5 minutes max (150 * 2 seconds)
    let pollCount = 0;

    const poll = async (): Promise<void> => {
      const status = await metaAnalysisApi.getStatus(analysisId);

      console.log(`Status update (${pollCount + 1}/${maxPolls}):`, {
        id: status.id,
        status: status.status,
        decisions: status.decisions,
      });

      // Check if analysis is complete
      if (status.status === 'completed') {
        console.log('Meta-analysis completed!');
        return;
      }

      if (status.status === 'failed') {
        console.error('Meta-analysis failed!');
        return;
      }

      // Continue polling if not complete
      pollCount++;
      if (pollCount < maxPolls) {
        await new Promise((resolve) => setTimeout(resolve, pollInterval));
        await poll();
      } else {
        console.warn('Max polling attempts reached');
      }
    };

    await poll();
  } catch (error) {
    console.error('Failed to poll status:', error);
    throw error;
  }
}

// ==============================================
// EXAMPLE 4: Get Audit Trail
// ==============================================

export async function getAuditTrailExample(analysisId: string) {
  try {
    const auditTrail = await metaAnalysisApi.getAuditTrail(analysisId);

    console.log(`Audit trail has ${auditTrail.entries.length} entries`);

    // Display each audit entry
    auditTrail.entries.forEach((entry, index) => {
      console.log(`\nEntry ${index + 1}:`);
      console.log(`  Timestamp: ${entry.timestamp}`);
      console.log(`  Agent: ${entry.agent_name} (${entry.agent_role})`);
      console.log(`  Action: ${entry.action}`);

      if (entry.reasoning) {
        console.log(`  Reasoning: ${entry.reasoning}`);
      }

      if (entry.confidence !== undefined) {
        console.log(`  Confidence: ${entry.confidence}`);
      }

      if (entry.decision) {
        console.log('  Decision:', entry.decision);
      }
    });

    return auditTrail;
  } catch (error) {
    console.error('Failed to get audit trail:', error);
    throw error;
  }
}

// ==============================================
// EXAMPLE 5: Ask Questions (Q&A Agent)
// ==============================================

export async function askQuestionExample(
  question: string,
  analysisId?: string
) {
  try {
    const response = await metaAnalysisApi.askQuestion(question, analysisId);

    console.log('Q&A Response:', {
      question: response.question,
      answer: response.answer,
      confidence: response.confidence,
      sources: response.sources,
      followUpSuggestions: response.follow_up_suggestions,
    });

    // Display follow-up suggestions
    if (response.follow_up_suggestions.length > 0) {
      console.log('\nSuggested follow-up questions:');
      response.follow_up_suggestions.forEach((suggestion, index) => {
        console.log(`${index + 1}. ${suggestion}`);
      });
    }

    return response;
  } catch (error) {
    console.error('Failed to ask question:', error);
    throw error;
  }
}

// ==============================================
// EXAMPLE 6: Get Final Report
// ==============================================

export async function getReportExample(analysisId: string) {
  try {
    const report = await metaAnalysisApi.getReport(analysisId);

    console.log('Report generated:', {
      id: report.id,
      status: report.status,
      format: report.format,
      sections: report.sections,
    });

    return report;
  } catch (error) {
    console.error('Failed to get report:', error);
    throw error;
  }
}

// ==============================================
// EXAMPLE 7: Complete Workflow
// ==============================================

export async function completeWorkflowExample() {
  try {
    console.log('=== Starting Complete Meta-Analysis Workflow ===\n');

    // Step 1: Create meta-analysis
    console.log('Step 1: Creating meta-analysis...');
    const analysisId = await createMetaAnalysisExample();
    console.log(`Analysis ID: ${analysisId}\n`);

    // Step 2: Execute meta-analysis
    console.log('Step 2: Executing meta-analysis...');
    await executeMetaAnalysisExample(analysisId);
    console.log('');

    // Step 3: Poll for status
    console.log('Step 3: Monitoring progress...');
    await pollStatusExample(analysisId);
    console.log('');

    // Step 4: Ask questions
    console.log('Step 4: Asking questions...');
    await askQuestionExample(
      'What search terms were used in this meta-analysis?',
      analysisId
    );
    console.log('');

    // Step 5: Get audit trail
    console.log('Step 5: Retrieving audit trail...');
    await getAuditTrailExample(analysisId);
    console.log('');

    // Step 6: Get final report
    console.log('Step 6: Generating final report...');
    await getReportExample(analysisId);
    console.log('');

    console.log('=== Workflow Complete ===');
  } catch (error) {
    console.error('Workflow failed:', error);
    throw error;
  }
}

// ==============================================
// EXAMPLE 8: Error Handling
// ==============================================

export async function errorHandlingExample() {
  try {
    // Attempt to get status for non-existent analysis
    await metaAnalysisApi.getStatus('non-existent-id');
  } catch (error: any) {
    // The apiClient interceptor will automatically handle errors
    // and display toast notifications, but you can also add
    // custom error handling here
    if (error.response) {
      console.error('Server error:', {
        status: error.response.status,
        data: error.response.data,
      });
    } else if (error.request) {
      console.error('Network error - no response received');
    } else {
      console.error('Request error:', error.message);
    }
  }
}

// ==============================================
// EXAMPLE 9: Using with React Component
// ==============================================

/**
 * Example React component using the meta-analysis API
 */
/*
import React, { useState, useEffect } from 'react';
import { metaAnalysisApi, MetaAnalysisRequest } from './api';

export function MetaAnalysisComponent() {
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>('idle');
  const [error, setError] = useState<string | null>(null);

  const createAnalysis = async () => {
    try {
      setError(null);
      setStatus('creating');

      const requestData: MetaAnalysisRequest = {
        research_question: 'Your research question here',
        topic: 'Your topic',
        inclusion_criteria: ['Criterion 1', 'Criterion 2'],
        exclusion_criteria: ['Criterion 1', 'Criterion 2'],
        databases: ['pubmed', 'arxiv'],
        peer_review_only: true,
      };

      const response = await metaAnalysisApi.createMetaAnalysis(requestData);
      setAnalysisId(response.id);
      setStatus('created');
    } catch (err: any) {
      setError(err.message);
      setStatus('error');
    }
  };

  const executeAnalysis = async () => {
    if (!analysisId) return;

    try {
      setError(null);
      setStatus('executing');

      await metaAnalysisApi.executeMetaAnalysis(analysisId);
      setStatus('executing');

      // Start polling
      startPolling();
    } catch (err: any) {
      setError(err.message);
      setStatus('error');
    }
  };

  const startPolling = () => {
    const interval = setInterval(async () => {
      if (!analysisId) return;

      try {
        const statusResponse = await metaAnalysisApi.getStatus(analysisId);

        if (statusResponse.status === 'completed') {
          clearInterval(interval);
          setStatus('completed');
        } else if (statusResponse.status === 'failed') {
          clearInterval(interval);
          setStatus('failed');
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    }, 2000);

    // Stop polling after 5 minutes
    setTimeout(() => clearInterval(interval), 300000);
  };

  return (
    <div>
      <h1>Meta-Analysis</h1>
      <div>Status: {status}</div>
      {error && <div>Error: {error}</div>}

      <button onClick={createAnalysis} disabled={status !== 'idle'}>
        Create Analysis
      </button>

      <button onClick={executeAnalysis} disabled={!analysisId || status !== 'created'}>
        Execute Analysis
      </button>
    </div>
  );
}
*/

// ==============================================
// EXAMPLE 10: TypeScript Type Usage
// ==============================================

/**
 * Example function demonstrating TypeScript type safety
 */
export async function typeSafeExample() {
  // TypeScript will ensure all required fields are present
  const requestData: MetaAnalysisRequest = {
    research_question: 'My research question',
    topic: 'My topic',
    // Optional fields can be omitted
  };

  const response = await metaAnalysisApi.createMetaAnalysis(requestData);

  // TypeScript knows the response structure
  console.log(response.id); // string
  console.log(response.status); // string
  console.log(response.workflow.research_question); // string
  console.log(response.workflow.timeline_days); // number

  // Execute and get strongly-typed response
  const executeResponse = await metaAnalysisApi.executeMetaAnalysis(response.id);

  // Access nested properties with full type safety
  const totalFound = executeResponse.search_results.total_found; // number
  const includedCount = executeResponse.screening_results.included; // number
  const credibilityBreakdown = executeResponse.credibility_results.breakdown;

  console.log({
    totalFound,
    includedCount,
    highCredibility: credibilityBreakdown.high_credibility,
    mediumCredibility: credibilityBreakdown.medium_credibility,
    lowCredibility: credibilityBreakdown.low_credibility,
  });
}
