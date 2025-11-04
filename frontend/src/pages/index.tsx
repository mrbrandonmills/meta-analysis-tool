import { useState } from 'react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function Home() {
  const [researchQuestion, setResearchQuestion] = useState('')
  const [topic, setTopic] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
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
        databases: ['pubmed']
      })
      setResult(response.data)
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setLoading(false)
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
              <h3 className="font-semibold text-green-900 mb-2">Success!</h3>
              <p className="text-sm text-green-800">
                Analysis ID: {result.id}
              </p>
              <p className="text-sm text-green-800">
                Status: {result.status}
              </p>
            </div>
          )}
        </div>

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
