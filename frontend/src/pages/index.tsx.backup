import { useState } from 'react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function Home() {
  const [researchQuestion, setResearchQuestion] = useState('')
  const [topic, setTopic] = useState('')
  const [peerReviewOnly, setPeerReviewOnly] = useState(false)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [executionResult, setExecutionResult] = useState<any>(null)
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState<any>(null)

  const createMetaAnalysis = async () => {
    setLoading(true)
    try {
      const response = await axios.post(`${API_URL}/api/v1/meta-analysis/create`, {
        research_question: researchQuestion,
        topic: topic,
        inclusion_criteria: [
          'Randomized controlled trial',
          'Adult population (18+)',
          'Published in peer-reviewed journal'
        ],
        exclusion_criteria: [
          'Non-English language',
          'Qualitative studies'
        ],
        databases: ['pubmed', 'arxiv', 'europepmc', 'core'],
        peer_review_only: peerReviewOnly
      })
      setResult(response.data)
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setLoading(false)
    }
  }

  const executeMetaAnalysis = async () => {
    if (!result?.id) return
    setLoading(true)
    try {
      const response = await axios.post(`${API_URL}/api/v1/meta-analysis/execute/${result.id}`)
      setExecutionResult(response.data)
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setLoading(false)
    }
  }

  const getCredibilityColor = (level: string) => {
    switch (level?.toUpperCase()) {
      case 'HIGH':
        return 'bg-green-100 border-green-300 text-green-900'
      case 'MEDIUM':
        return 'bg-yellow-100 border-yellow-300 text-yellow-900'
      case 'LOW':
        return 'bg-orange-100 border-orange-300 text-orange-900'
      case 'VERY_LOW':
        return 'bg-red-100 border-red-300 text-red-900'
      default:
        return 'bg-gray-100 border-gray-300 text-gray-900'
    }
  }

  const getCredibilityDot = (level: string) => {
    switch (level?.toUpperCase()) {
      case 'HIGH':
        return '🟢'
      case 'MEDIUM':
        return '🟡'
      case 'LOW':
        return '🟠'
      case 'VERY_LOW':
        return '🔴'
      default:
        return '⚪'
    }
  }

  const askQuestion = async () => {
    setLoading(true)
    try {
      const response = await axios.post(`${API_URL}/api/v1/meta-analysis/ask`, {
        question: question
      })
      setAnswer(response.data)
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Meta-Analysis Research Platform
          </h1>
          <p className="text-lg text-gray-600">
            AI-powered meta-analysis using specialized research agents
          </p>
        </header>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4">Create Meta-Analysis</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Research Question
              </label>
              <input
                type="text"
                value={researchQuestion}
                onChange={(e) => setResearchQuestion(e.target.value)}
                placeholder="e.g., What is the effect of mindfulness on anxiety?"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Topic
              </label>
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g., Mindfulness and Anxiety"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="peerReviewOnly"
                checked={peerReviewOnly}
                onChange={(e) => setPeerReviewOnly(e.target.checked)}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="peerReviewOnly" className="text-sm text-gray-700">
                Peer-reviewed studies only (exclude preprints)
              </label>
            </div>

            <button
              onClick={createMetaAnalysis}
              disabled={loading || !researchQuestion || !topic}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating...' : 'Create Meta-Analysis'}
            </button>
          </div>

          {result && (
            <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-md">
              <h3 className="font-semibold text-green-900 mb-2">Workflow Created!</h3>
              <p className="text-sm text-green-800">
                Analysis ID: {result.id}
              </p>
              <p className="text-sm text-green-800 mb-4">
                Status: {result.status}
              </p>
              <button
                onClick={executeMetaAnalysis}
                disabled={loading}
                className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {loading ? 'Executing...' : 'Execute Meta-Analysis'}
              </button>
            </div>
          )}
        </div>

        {executionResult && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-2xl font-semibold mb-4">Analysis Results</h2>

            {/* Search Results */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-2">Search Results</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
                  <p className="text-sm text-blue-600 font-medium">Total Found</p>
                  <p className="text-2xl font-bold text-blue-900">{executionResult.search_results?.total_found || 0}</p>
                </div>
                <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
                  <p className="text-sm text-blue-600 font-medium">Databases</p>
                  <p className="text-sm text-blue-900">{executionResult.search_results?.databases?.join(', ') || 'N/A'}</p>
                </div>
              </div>
            </div>

            {/* Screening Results */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-2">Screening Results</h3>
              <div className="grid grid-cols-3 gap-4">
                <div className="p-3 bg-green-50 border border-green-200 rounded-md">
                  <p className="text-sm text-green-600 font-medium">Included</p>
                  <p className="text-2xl font-bold text-green-900">{executionResult.screening_results?.included || 0}</p>
                </div>
                <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                  <p className="text-sm text-red-600 font-medium">Excluded</p>
                  <p className="text-2xl font-bold text-red-900">{executionResult.screening_results?.excluded || 0}</p>
                </div>
                <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                  <p className="text-sm text-yellow-600 font-medium">Uncertain</p>
                  <p className="text-2xl font-bold text-yellow-900">{executionResult.screening_results?.uncertain || 0}</p>
                </div>
              </div>
            </div>

            {/* Credibility Breakdown */}
            {executionResult.credibility_results && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-2">📊 Credibility Breakdown</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div className="p-3 bg-green-50 border border-green-200 rounded-md">
                    <p className="text-sm text-green-600 font-medium">🟢 High</p>
                    <p className="text-2xl font-bold text-green-900">{executionResult.credibility_results.breakdown?.high || 0}</p>
                  </div>
                  <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                    <p className="text-sm text-yellow-600 font-medium">🟡 Medium</p>
                    <p className="text-2xl font-bold text-yellow-900">{executionResult.credibility_results.breakdown?.medium || 0}</p>
                  </div>
                  <div className="p-3 bg-orange-50 border border-orange-200 rounded-md">
                    <p className="text-sm text-orange-600 font-medium">🟠 Low</p>
                    <p className="text-2xl font-bold text-orange-900">{executionResult.credibility_results.breakdown?.low || 0}</p>
                  </div>
                  <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                    <p className="text-sm text-red-600 font-medium">🔴 Very Low</p>
                    <p className="text-2xl font-bold text-red-900">{executionResult.credibility_results.breakdown?.very_low || 0}</p>
                  </div>
                </div>

                {/* Individual Studies with Credibility */}
                {executionResult.credibility_results.studies_with_scores && executionResult.credibility_results.studies_with_scores.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-3">Studies with Credibility Scores</h4>
                    <div className="space-y-3 max-h-96 overflow-y-auto">
                      {executionResult.credibility_results.studies_with_scores.slice(0, 10).map((study: any, idx: number) => (
                        <div
                          key={idx}
                          className={`p-4 border-2 rounded-md ${getCredibilityColor(study.credibility?.level)}`}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-2 mb-2">
                                <span className="text-2xl">{getCredibilityDot(study.credibility?.level)}</span>
                                <span className="font-semibold text-sm uppercase">{study.credibility?.level} CREDIBILITY</span>
                                <span className="text-sm font-bold">Score: {study.credibility?.score}/100</span>
                              </div>
                              <h5 className="font-semibold mb-1">{study.title}</h5>
                              <p className="text-xs mb-2">
                                {study.authors} | {study.journal} ({study.year})
                              </p>
                              {study.credibility?.reasoning && (
                                <p className="text-xs mb-2">{study.credibility.reasoning}</p>
                              )}
                              <div className="flex items-center space-x-4 text-xs">
                                {study.credibility?.is_peer_reviewed && (
                                  <span className="bg-white bg-opacity-50 px-2 py-1 rounded">✅ Peer-Reviewed</span>
                                )}
                                {study.credibility?.is_preprint && (
                                  <span className="bg-white bg-opacity-50 px-2 py-1 rounded">📄 Preprint</span>
                                )}
                                {study.credibility?.replicability && (
                                  <span className="bg-white bg-opacity-50 px-2 py-1 rounded">
                                    Replicability: {study.credibility.replicability}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4">Ask Questions</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Your Question
              </label>
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="e.g., How did you determine which studies to include?"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <button
              onClick={askQuestion}
              disabled={loading || !question}
              className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {loading ? 'Asking...' : 'Ask Q&A Agent'}
            </button>
          </div>

          {answer && (
            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
              <h3 className="font-semibold text-blue-900 mb-2">Answer:</h3>
              <p className="text-sm text-blue-800 mb-2">{answer.answer}</p>
              <p className="text-xs text-blue-600">
                Confidence: {(answer.confidence * 100).toFixed(0)}%
              </p>

              {answer.follow_up_suggestions && (
                <div className="mt-4">
                  <p className="text-xs font-semibold text-blue-900 mb-2">
                    Suggested follow-ups:
                  </p>
                  <ul className="text-xs text-blue-700 list-disc list-inside">
                    {answer.follow_up_suggestions.map((q: string, i: number) => (
                      <li key={i}>{q}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-semibold mb-4">Available Agents</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { name: 'Coordinator', color: 'purple' },
              { name: 'Search', color: 'blue' },
              { name: 'Screening', color: 'green' },
              { name: 'Quality Assessment', color: 'yellow' },
              { name: 'Data Extraction', color: 'orange' },
              { name: 'Statistical', color: 'red' },
              { name: 'Report', color: 'pink' },
              { name: 'Q&A', color: 'indigo' },
            ].map((agent) => (
              <div
                key={agent.name}
                className={`p-3 bg-${agent.color}-50 border border-${agent.color}-200 rounded-md`}
              >
                <h3 className={`font-semibold text-${agent.color}-900`}>
                  {agent.name} Agent
                </h3>
                <p className={`text-xs text-${agent.color}-700`}>
                  Specialized agent for {agent.name.toLowerCase()} tasks
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
