import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Layout from '@/components/layout/Layout'
import AgentPipeline, { AgentState, AgentStep } from '@/components/workflow/AgentPipeline'
import {
  Users,
  Plus,
  Trash2,
  Loader,
  CheckCircle2,
  AlertCircle,
  Download,
  ArrowRight,
  Search,
  Brain,
  Award,
  FileText,
  Star,
  TrendingUp,
  Mail,
  Building
} from 'lucide-react'
import { useRouter } from 'next/router'

interface ReviewerMatcherFormData {
  manuscript_title: string
  abstract: string
  research_area: string
  keywords: string[]
  required_expertise: string[]
  exclude_institutions: string[]
  min_publications: number
  prefer_recent_work: boolean
  num_reviewers: number
}

interface Reviewer {
  id: string
  name: string
  email: string
  institution: string
  expertise_score: number
  match_score: number
  publications_count: number
  recent_papers: string[]
  h_index: number
  expertise_areas: string[]
  reasoning: string
}

interface MatchResponse {
  id: string
  status: string
  message: string
  reviewers?: Reviewer[]
  workflow?: any
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://meta-analysis-tool-production.up.railway.app'

const ReviewerMatcherNewPage: React.FC = () => {
  const router = useRouter()
  const [formData, setFormData] = useState<ReviewerMatcherFormData>({
    manuscript_title: '',
    abstract: '',
    research_area: '',
    keywords: [''],
    required_expertise: [''],
    exclude_institutions: [''],
    min_publications: 5,
    prefer_recent_work: true,
    num_reviewers: 3
  })

  const [matchId, setMatchId] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isExecuting, setIsExecuting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [agentSteps, setAgentSteps] = useState<AgentStep[]>([])
  const [reviewers, setReviewers] = useState<Reviewer[]>([])
  const [reportUrl, setReportUrl] = useState<string | null>(null)

  const handleInputChange = (field: keyof ReviewerMatcherFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const addItem = (type: 'keywords' | 'required_expertise' | 'exclude_institutions') => {
    setFormData(prev => ({
      ...prev,
      [type]: [...prev[type], '']
    }))
  }

  const updateItem = (type: 'keywords' | 'required_expertise' | 'exclude_institutions', index: number, value: string) => {
    setFormData(prev => ({
      ...prev,
      [type]: prev[type].map((item, i) => i === index ? value : item)
    }))
  }

  const removeItem = (type: 'keywords' | 'required_expertise' | 'exclude_institutions', index: number) => {
    setFormData(prev => ({
      ...prev,
      [type]: prev[type].filter((_, i) => i !== index)
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError(null)

    try {
      // Filter out empty items
      const cleanedData = {
        ...formData,
        keywords: formData.keywords.filter(k => k.trim()),
        required_expertise: formData.required_expertise.filter(e => e.trim()),
        exclude_institutions: formData.exclude_institutions.filter(i => i.trim())
      }

      const response = await fetch(`${API_URL}/api/v1/reviewer-matcher/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(cleanedData)
      })

      if (!response.ok) {
        throw new Error(`Failed to create matcher request: ${response.statusText}`)
      }

      const data: MatchResponse = await response.json()
      setMatchId(data.id)

      // Initialize agent steps
      const steps: AgentStep[] = [
        {
          id: '1',
          name: 'Profile Search',
          description: 'Searching academic databases for potential reviewers',
          icon: Search,
          state: AgentState.PENDING
        },
        {
          id: '2',
          name: 'Expertise Analysis',
          description: 'Analyzing researcher expertise and publications',
          icon: Brain,
          state: AgentState.PENDING
        },
        {
          id: '3',
          name: 'Quality Assessment',
          description: 'Evaluating reviewer credentials and metrics',
          icon: Award,
          state: AgentState.PENDING
        },
        {
          id: '4',
          name: 'Match Scoring',
          description: 'Calculating match scores based on criteria',
          icon: TrendingUp,
          state: AgentState.PENDING
        },
        {
          id: '5',
          name: 'Results Compilation',
          description: 'Preparing reviewer recommendations',
          icon: FileText,
          state: AgentState.PENDING
        }
      ]
      setAgentSteps(steps)

      // Auto-execute
      await executeMatching(data.id, steps)
    } catch (err: any) {
      setError(err.message || 'Failed to create matcher request')
    } finally {
      setIsSubmitting(false)
    }
  }

  const executeMatching = async (id: string, steps: AgentStep[]) => {
    setIsExecuting(true)

    try {
      const response = await fetch(`${API_URL}/api/v1/reviewer-matcher/execute/${id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error('Failed to execute matching')
      }

      // Poll for status updates
      pollStatus(id, steps)
    } catch (err: any) {
      setError(err.message || 'Failed to execute matching')
      setIsExecuting(false)
    }
  }

  const pollStatus = async (id: string, steps: AgentStep[]) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`${API_URL}/api/v1/reviewer-matcher/status/${id}`)

        if (!response.ok) {
          throw new Error('Failed to get status')
        }

        const status = await response.json()

        // Update agent steps based on status
        const updatedSteps = steps.map((step, index) => {
          if (index < status.completed_steps) {
            return { ...step, state: AgentState.COMPLETED }
          } else if (index === status.completed_steps) {
            return { ...step, state: AgentState.RUNNING, progress: status.progress }
          }
          return step
        })

        setAgentSteps(updatedSteps)

        // Check if complete
        if (status.status === 'completed') {
          clearInterval(interval)
          setIsExecuting(false)

          // Fetch reviewers
          if (status.reviewers) {
            setReviewers(status.reviewers)
          }

          // Mark all steps as completed
          setAgentSteps(steps.map(step => ({ ...step, state: AgentState.COMPLETED })))

          // Set report URL if available
          if (status.report_url) {
            setReportUrl(`${API_URL}${status.report_url}`)
          }
        } else if (status.status === 'failed') {
          clearInterval(interval)
          setIsExecuting(false)
          setError(status.message || 'Matching failed')

          // Mark current step as error
          const errorSteps = updatedSteps.map((step, index) =>
            index === status.completed_steps
              ? { ...step, state: AgentState.ERROR, message: status.message }
              : step
          )
          setAgentSteps(errorSteps)
        }
      } catch (err) {
        console.error('Polling error:', err)
      }
    }, 2000)

    // Stop polling after 5 minutes
    setTimeout(() => {
      clearInterval(interval)
      setIsExecuting(false)
    }, 300000)
  }

  const downloadReport = async () => {
    if (reportUrl) {
      window.open(reportUrl, '_blank')
    }
  }

  return (
    <Layout title="Reviewer Matcher">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="p-3 rounded-xl bg-green-100 text-green-600">
              <Users className="w-6 h-6" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900">Find Expert Reviewers</h1>
          </div>
          <p className="text-gray-600">
            AI-powered matching to find the most qualified reviewers for your manuscript
          </p>
        </motion.div>

        {/* Error Alert */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="p-4 rounded-xl bg-red-50 border border-red-200 flex items-start gap-3"
            >
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-red-900">Error</h3>
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Form or Agent Pipeline */}
        {!matchId ? (
          <motion.form
            onSubmit={handleSubmit}
            className="space-y-6 bg-white/60 backdrop-blur-sm rounded-2xl p-8 border border-gray-200 shadow-soft"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            {/* Manuscript Title */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Manuscript Title *
              </label>
              <input
                type="text"
                value={formData.manuscript_title}
                onChange={(e) => handleInputChange('manuscript_title', e.target.value)}
                placeholder="e.g., A Novel Approach to Deep Learning for Medical Image Analysis"
                className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all"
                required
              />
            </div>

            {/* Abstract */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Abstract *
              </label>
              <textarea
                value={formData.abstract}
                onChange={(e) => handleInputChange('abstract', e.target.value)}
                placeholder="Paste your manuscript abstract here..."
                className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all"
                rows={6}
                required
              />
            </div>

            {/* Research Area */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Research Area *
              </label>
              <input
                type="text"
                value={formData.research_area}
                onChange={(e) => handleInputChange('research_area', e.target.value)}
                placeholder="e.g., Computer Vision, Medical Imaging, Deep Learning"
                className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all"
                required
              />
            </div>

            {/* Keywords */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Keywords
              </label>
              {formData.keywords.map((keyword, index) => (
                <div key={index} className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={keyword}
                    onChange={(e) => updateItem('keywords', index, e.target.value)}
                    placeholder="e.g., convolutional neural networks"
                    className="flex-1 px-4 py-2 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all"
                  />
                  {formData.keywords.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeItem('keywords', index)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  )}
                </div>
              ))}
              <button
                type="button"
                onClick={() => addItem('keywords')}
                className="flex items-center gap-2 text-sm font-medium text-green-600 hover:text-green-700 mt-2"
              >
                <Plus className="w-4 h-4" />
                Add Keyword
              </button>
            </div>

            {/* Required Expertise */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Required Expertise
              </label>
              {formData.required_expertise.map((expertise, index) => (
                <div key={index} className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={expertise}
                    onChange={(e) => updateItem('required_expertise', index, e.target.value)}
                    placeholder="e.g., Medical imaging analysis"
                    className="flex-1 px-4 py-2 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all"
                  />
                  {formData.required_expertise.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeItem('required_expertise', index)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  )}
                </div>
              ))}
              <button
                type="button"
                onClick={() => addItem('required_expertise')}
                className="flex items-center gap-2 text-sm font-medium text-green-600 hover:text-green-700 mt-2"
              >
                <Plus className="w-4 h-4" />
                Add Expertise
              </button>
            </div>

            {/* Exclude Institutions */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Exclude Institutions (Optional)
              </label>
              <p className="text-xs text-gray-500 mb-2">
                Institutions to exclude for conflict of interest
              </p>
              {formData.exclude_institutions.map((institution, index) => (
                <div key={index} className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={institution}
                    onChange={(e) => updateItem('exclude_institutions', index, e.target.value)}
                    placeholder="e.g., Stanford University"
                    className="flex-1 px-4 py-2 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all"
                  />
                  {formData.exclude_institutions.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeItem('exclude_institutions', index)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  )}
                </div>
              ))}
              <button
                type="button"
                onClick={() => addItem('exclude_institutions')}
                className="flex items-center gap-2 text-sm font-medium text-green-600 hover:text-green-700 mt-2"
              >
                <Plus className="w-4 h-4" />
                Add Institution
              </button>
            </div>

            {/* Advanced Settings */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Min Publications */}
              <div>
                <label className="block text-sm font-semibold text-gray-900 mb-2">
                  Minimum Publications
                </label>
                <input
                  type="number"
                  value={formData.min_publications}
                  onChange={(e) => handleInputChange('min_publications', parseInt(e.target.value))}
                  min="0"
                  className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all"
                />
              </div>

              {/* Number of Reviewers */}
              <div>
                <label className="block text-sm font-semibold text-gray-900 mb-2">
                  Number of Reviewers
                </label>
                <input
                  type="number"
                  value={formData.num_reviewers}
                  onChange={(e) => handleInputChange('num_reviewers', parseInt(e.target.value))}
                  min="1"
                  max="10"
                  className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all"
                />
              </div>
            </div>

            {/* Prefer Recent Work */}
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="prefer_recent_work"
                checked={formData.prefer_recent_work}
                onChange={(e) => handleInputChange('prefer_recent_work', e.target.checked)}
                className="w-5 h-5 rounded border-gray-300 text-green-600 focus:ring-green-500"
              />
              <label htmlFor="prefer_recent_work" className="text-sm font-medium text-gray-900">
                Prefer reviewers with recent publications in this area
              </label>
            </div>

            {/* Submit Button */}
            <div className="flex gap-4">
              <motion.button
                type="submit"
                disabled={isSubmitting}
                className="flex-1 px-6 py-4 bg-green-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-glow-green transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                whileHover={{ scale: isSubmitting ? 1 : 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
              >
                <span className="flex items-center justify-center gap-2">
                  {isSubmitting ? (
                    <>
                      <Loader className="w-5 h-5 animate-spin" />
                      Finding Reviewers...
                    </>
                  ) : (
                    <>
                      Find Reviewers
                      <ArrowRight className="w-5 h-5" />
                    </>
                  )}
                </span>
              </motion.button>

              <motion.button
                type="button"
                onClick={() => router.push('/dashboard')}
                className="px-6 py-4 bg-white text-gray-700 rounded-xl font-semibold border border-gray-300 hover:border-gray-400 transition-all duration-300"
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
              >
                Cancel
              </motion.button>
            </div>
          </motion.form>
        ) : (
          <div className="space-y-6">
            {/* Agent Pipeline */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <AgentPipeline steps={agentSteps} />
            </motion.div>

            {/* Reviewer Results */}
            {reviewers.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="space-y-4"
              >
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-bold text-gray-900">
                    Recommended Reviewers
                  </h2>
                  {reportUrl && (
                    <motion.button
                      onClick={downloadReport}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg font-medium shadow-lg hover:shadow-glow-green transition-all duration-300"
                      whileHover={{ scale: 1.05, y: -2 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <span className="flex items-center gap-2">
                        <Download className="w-4 h-4" />
                        Export Report
                      </span>
                    </motion.button>
                  )}
                </div>

                {reviewers.map((reviewer, index) => (
                  <motion.div
                    key={reviewer.id}
                    className="bg-white/60 backdrop-blur-sm rounded-2xl p-6 border border-gray-200 shadow-soft"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: index * 0.1 }}
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-start gap-4">
                        <div className="flex-shrink-0 w-12 h-12 rounded-full bg-green-100 text-green-600 flex items-center justify-center text-xl font-bold">
                          {reviewer.name.charAt(0)}
                        </div>
                        <div>
                          <h3 className="text-xl font-bold text-gray-900">
                            {reviewer.name}
                          </h3>
                          <div className="flex items-center gap-2 text-sm text-gray-600 mt-1">
                            <Building className="w-4 h-4" />
                            {reviewer.institution}
                          </div>
                          {reviewer.email && (
                            <div className="flex items-center gap-2 text-sm text-gray-600 mt-1">
                              <Mail className="w-4 h-4" />
                              {reviewer.email}
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-green-100 text-green-800">
                        <Star className="w-4 h-4 fill-current" />
                        <span className="font-bold">{reviewer.match_score}%</span>
                        <span className="text-xs">Match</span>
                      </div>
                    </div>

                    {/* Metrics */}
                    <div className="grid grid-cols-3 gap-4 mb-4">
                      <div className="p-3 rounded-lg bg-gray-50">
                        <div className="text-xs text-gray-600 mb-1">Publications</div>
                        <div className="text-lg font-bold text-gray-900">
                          {reviewer.publications_count}
                        </div>
                      </div>
                      <div className="p-3 rounded-lg bg-gray-50">
                        <div className="text-xs text-gray-600 mb-1">H-Index</div>
                        <div className="text-lg font-bold text-gray-900">
                          {reviewer.h_index}
                        </div>
                      </div>
                      <div className="p-3 rounded-lg bg-gray-50">
                        <div className="text-xs text-gray-600 mb-1">Expertise</div>
                        <div className="text-lg font-bold text-gray-900">
                          {reviewer.expertise_score}%
                        </div>
                      </div>
                    </div>

                    {/* Expertise Areas */}
                    <div className="mb-4">
                      <div className="text-sm font-semibold text-gray-900 mb-2">
                        Expertise Areas
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {reviewer.expertise_areas.map((area, i) => (
                          <span
                            key={i}
                            className="px-3 py-1 rounded-full bg-green-100 text-green-700 text-sm font-medium"
                          >
                            {area}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Reasoning */}
                    {reviewer.reasoning && (
                      <div className="p-4 rounded-lg bg-green-50 border border-green-200">
                        <div className="text-sm font-semibold text-green-900 mb-1">
                          Why this reviewer?
                        </div>
                        <p className="text-sm text-green-800">{reviewer.reasoning}</p>
                      </div>
                    )}

                    {/* Recent Papers */}
                    {reviewer.recent_papers && reviewer.recent_papers.length > 0 && (
                      <div className="mt-4">
                        <div className="text-sm font-semibold text-gray-900 mb-2">
                          Recent Relevant Papers
                        </div>
                        <ul className="space-y-1">
                          {reviewer.recent_papers.slice(0, 3).map((paper, i) => (
                            <li key={i} className="text-sm text-gray-600 flex gap-2">
                              <span className="text-green-600">•</span>
                              <span className="flex-1">{paper}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </motion.div>
                ))}

                {/* Back to Dashboard */}
                <motion.div
                  className="flex justify-center pt-4"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.4, delay: 0.3 }}
                >
                  <motion.button
                    onClick={() => router.push('/dashboard')}
                    className="px-6 py-3 bg-white text-gray-700 rounded-xl font-semibold border border-gray-300 hover:border-gray-400 transition-all duration-300"
                    whileHover={{ scale: 1.05, y: -2 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    Back to Dashboard
                  </motion.button>
                </motion.div>
              </motion.div>
            )}

            {/* Executing Status */}
            {isExecuting && reviewers.length === 0 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="bg-green-50 rounded-xl p-4 border border-green-200 flex items-center gap-3"
              >
                <Loader className="w-5 h-5 text-green-600 animate-spin" />
                <span className="text-sm font-medium text-green-900">
                  Finding the best reviewers for your manuscript... This may take a few minutes.
                </span>
              </motion.div>
            )}
          </div>
        )}
      </div>
    </Layout>
  )
}

export default ReviewerMatcherNewPage
