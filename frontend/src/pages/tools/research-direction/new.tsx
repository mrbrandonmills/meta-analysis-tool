import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Layout from '@/components/layout/Layout'
import { AgentPipeline, AgentState, AgentStep } from '@/components/workflow/AgentPipeline'
import {
  Lightbulb,
  Plus,
  Trash2,
  Loader,
  CheckCircle2,
  AlertCircle,
  Download,
  ArrowRight,
  TrendingUp,
  Target,
  Sparkles,
  BookOpen,
  Search,
  Brain,
  BarChart3,
  Award
} from 'lucide-react'
import { useRouter } from 'next/router'

interface ResearchDirectionFormData {
  research_area: string
  existing_literature: string[]
  constraints: string[]
  focus_areas: string[]
  timeframe: string
  impact_level: 'high' | 'medium' | 'low'
  researcher_name: string
}

interface ResearchGap {
  id: string
  title: string
  description: string
  novelty_score: number
  feasibility_score: number
  impact_potential: string
  suggested_approaches: string[]
  related_papers: number
  estimated_timeline: string
}

interface AnalysisResponse {
  id: string
  status: string
  message: string
  research_gaps?: ResearchGap[]
  summary?: {
    total_gaps_identified: number
    high_potential_gaps: number
    recommended_direction: string
  }
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://meta-analysis-tool-production.up.railway.app'

const ResearchDirectionNewPage: React.FC = () => {
  const router = useRouter()
  const [formData, setFormData] = useState<ResearchDirectionFormData>({
    research_area: '',
    existing_literature: [''],
    constraints: [''],
    focus_areas: [''],
    timeframe: '12-24 months',
    impact_level: 'high',
    researcher_name: ''
  })

  const [analysisId, setAnalysisId] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isExecuting, setIsExecuting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [agentSteps, setAgentSteps] = useState<AgentStep[]>([])
  const [researchGaps, setResearchGaps] = useState<ResearchGap[]>([])
  const [summary, setSummary] = useState<any>(null)
  const [reportUrl, setReportUrl] = useState<string | null>(null)

  const handleInputChange = (field: keyof ResearchDirectionFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const addArrayItem = (field: 'existing_literature' | 'constraints' | 'focus_areas') => {
    setFormData(prev => ({
      ...prev,
      [field]: [...prev[field], '']
    }))
  }

  const updateArrayItem = (
    field: 'existing_literature' | 'constraints' | 'focus_areas',
    index: number,
    value: string
  ) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].map((item, i) => (i === index ? value : item))
    }))
  }

  const removeArrayItem = (
    field: 'existing_literature' | 'constraints' | 'focus_areas',
    index: number
  ) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].filter((_, i) => i !== index)
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError(null)

    try {
      // Filter out empty values
      const cleanedData = {
        ...formData,
        existing_literature: formData.existing_literature.filter(l => l.trim()),
        constraints: formData.constraints.filter(c => c.trim()),
        focus_areas: formData.focus_areas.filter(f => f.trim())
      }

      const response = await fetch(`${API_URL}/api/v1/research-direction/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(cleanedData)
      })

      if (!response.ok) {
        throw new Error(`Failed to create analysis: ${response.statusText}`)
      }

      const data: AnalysisResponse = await response.json()
      setAnalysisId(data.id)

      // Initialize agent steps
      const steps: AgentStep[] = [
        {
          id: '1',
          name: 'Literature Review Agent',
          description: 'Analyzing existing research landscape',
          icon: BookOpen,
          state: AgentState.PENDING
        },
        {
          id: '2',
          name: 'Gap Analysis Agent',
          description: 'Identifying unexplored research areas',
          icon: Search,
          state: AgentState.PENDING
        },
        {
          id: '3',
          name: 'Trend Analysis Agent',
          description: 'Detecting emerging research trends',
          icon: TrendingUp,
          state: AgentState.PENDING
        },
        {
          id: '4',
          name: 'Feasibility Assessment Agent',
          description: 'Evaluating research feasibility',
          icon: Target,
          state: AgentState.PENDING
        },
        {
          id: '5',
          name: 'Novelty Scoring Agent',
          description: 'Calculating innovation potential',
          icon: Sparkles,
          state: AgentState.PENDING
        },
        {
          id: '6',
          name: 'Impact Prediction Agent',
          description: 'Predicting research impact',
          icon: BarChart3,
          state: AgentState.PENDING
        },
        {
          id: '7',
          name: 'Recommendation Generator',
          description: 'Synthesizing research directions',
          icon: Brain,
          state: AgentState.PENDING
        }
      ]
      setAgentSteps(steps)

      // Auto-execute
      await executeAnalysis(data.id, steps)
    } catch (err: any) {
      setError(err.message || 'Failed to create analysis')
    } finally {
      setIsSubmitting(false)
    }
  }

  const executeAnalysis = async (id: string, steps: AgentStep[]) => {
    setIsExecuting(true)

    try {
      const response = await fetch(`${API_URL}/api/v1/research-direction/execute/${id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error('Failed to execute analysis')
      }

      // Poll for status updates
      pollStatus(id, steps)
    } catch (err: any) {
      setError(err.message || 'Failed to execute analysis')
      setIsExecuting(false)
    }
  }

  const pollStatus = async (id: string, steps: AgentStep[]) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`${API_URL}/api/v1/research-direction/status/${id}`)

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

          // Mark all steps as completed
          setAgentSteps(steps.map(step => ({ ...step, state: AgentState.COMPLETED })))

          // Set results
          if (status.research_gaps) {
            setResearchGaps(status.research_gaps)
          }
          if (status.summary) {
            setSummary(status.summary)
          }
          if (status.report_url) {
            setReportUrl(`${API_URL}${status.report_url}`)
          }
        } else if (status.status === 'failed') {
          clearInterval(interval)
          setIsExecuting(false)
          setError(status.message || 'Analysis failed')

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

    // Stop polling after 10 minutes
    setTimeout(() => {
      clearInterval(interval)
      setIsExecuting(false)
    }, 600000)
  }

  const downloadReport = () => {
    if (reportUrl) {
      window.open(reportUrl, '_blank')
    }
  }

  const getNoveltyColor = (score: number) => {
    if (score >= 8) return 'text-yellow-600 bg-yellow-100'
    if (score >= 6) return 'text-yellow-500 bg-yellow-50'
    return 'text-gray-600 bg-gray-100'
  }

  const getFeasibilityColor = (score: number) => {
    if (score >= 8) return 'text-green-600 bg-green-100'
    if (score >= 6) return 'text-yellow-600 bg-yellow-100'
    return 'text-orange-600 bg-orange-100'
  }

  return (
    <Layout title="New Research Direction">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="p-3 rounded-xl bg-yellow-100 text-yellow-600">
              <Lightbulb className="w-6 h-6" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900">New Research Direction</h1>
          </div>
          <p className="text-gray-600">
            AI-powered gap analysis to discover novel research opportunities
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

        {/* Form or Results */}
        {!analysisId ? (
          <motion.form
            onSubmit={handleSubmit}
            className="space-y-6 bg-white/60 backdrop-blur-sm rounded-2xl p-8 border border-gray-200 shadow-soft"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            {/* Research Area */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Research Area *
              </label>
              <input
                type="text"
                value={formData.research_area}
                onChange={(e) => handleInputChange('research_area', e.target.value)}
                placeholder="e.g., Machine Learning in Healthcare"
                className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-yellow-500 focus:ring-2 focus:ring-yellow-200 transition-all"
                required
              />
            </div>

            {/* Existing Literature */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Existing Literature Topics
              </label>
              <p className="text-sm text-gray-600 mb-3">
                Key topics or papers that have been extensively researched
              </p>
              {formData.existing_literature.map((item, index) => (
                <div key={index} className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={item}
                    onChange={(e) => updateArrayItem('existing_literature', index, e.target.value)}
                    placeholder="e.g., Deep learning for medical imaging"
                    className="flex-1 px-4 py-2 rounded-lg border border-gray-300 focus:border-yellow-500 focus:ring-2 focus:ring-yellow-200 transition-all"
                  />
                  {formData.existing_literature.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeArrayItem('existing_literature', index)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  )}
                </div>
              ))}
              <button
                type="button"
                onClick={() => addArrayItem('existing_literature')}
                className="flex items-center gap-2 text-sm font-medium text-yellow-600 hover:text-yellow-700 mt-2"
              >
                <Plus className="w-4 h-4" />
                Add Literature Topic
              </button>
            </div>

            {/* Focus Areas */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Focus Areas (Optional)
              </label>
              <p className="text-sm text-gray-600 mb-3">
                Specific areas you'd like to explore
              </p>
              {formData.focus_areas.map((item, index) => (
                <div key={index} className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={item}
                    onChange={(e) => updateArrayItem('focus_areas', index, e.target.value)}
                    placeholder="e.g., Rare disease diagnosis"
                    className="flex-1 px-4 py-2 rounded-lg border border-gray-300 focus:border-yellow-500 focus:ring-2 focus:ring-yellow-200 transition-all"
                  />
                  {formData.focus_areas.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeArrayItem('focus_areas', index)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  )}
                </div>
              ))}
              <button
                type="button"
                onClick={() => addArrayItem('focus_areas')}
                className="flex items-center gap-2 text-sm font-medium text-yellow-600 hover:text-yellow-700 mt-2"
              >
                <Plus className="w-4 h-4" />
                Add Focus Area
              </button>
            </div>

            {/* Constraints */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Constraints (Optional)
              </label>
              <p className="text-sm text-gray-600 mb-3">
                Any limitations or requirements for your research
              </p>
              {formData.constraints.map((item, index) => (
                <div key={index} className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={item}
                    onChange={(e) => updateArrayItem('constraints', index, e.target.value)}
                    placeholder="e.g., Must use publicly available datasets"
                    className="flex-1 px-4 py-2 rounded-lg border border-gray-300 focus:border-yellow-500 focus:ring-2 focus:ring-yellow-200 transition-all"
                  />
                  {formData.constraints.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeArrayItem('constraints', index)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  )}
                </div>
              ))}
              <button
                type="button"
                onClick={() => addArrayItem('constraints')}
                className="flex items-center gap-2 text-sm font-medium text-yellow-600 hover:text-yellow-700 mt-2"
              >
                <Plus className="w-4 h-4" />
                Add Constraint
              </button>
            </div>

            {/* Timeframe & Impact Level */}
            <div className="grid grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-gray-900 mb-2">
                  Research Timeframe
                </label>
                <select
                  value={formData.timeframe}
                  onChange={(e) => handleInputChange('timeframe', e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-yellow-500 focus:ring-2 focus:ring-yellow-200 transition-all"
                >
                  <option value="6-12 months">6-12 months</option>
                  <option value="12-24 months">12-24 months</option>
                  <option value="2-3 years">2-3 years</option>
                  <option value="3+ years">3+ years</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-900 mb-2">
                  Desired Impact Level
                </label>
                <select
                  value={formData.impact_level}
                  onChange={(e) => handleInputChange('impact_level', e.target.value as any)}
                  className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-yellow-500 focus:ring-2 focus:ring-yellow-200 transition-all"
                >
                  <option value="high">High Impact</option>
                  <option value="medium">Medium Impact</option>
                  <option value="low">Incremental Impact</option>
                </select>
              </div>
            </div>

            {/* Researcher Name */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Your Name (Optional)
              </label>
              <input
                type="text"
                value={formData.researcher_name}
                onChange={(e) => handleInputChange('researcher_name', e.target.value)}
                placeholder="Dr. Jane Smith"
                className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-yellow-500 focus:ring-2 focus:ring-yellow-200 transition-all"
              />
            </div>

            {/* Submit Button */}
            <div className="flex gap-4">
              <motion.button
                type="submit"
                disabled={isSubmitting}
                className="flex-1 px-6 py-4 bg-yellow-500 text-white rounded-xl font-semibold shadow-lg hover:shadow-glow-yellow transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                whileHover={{ scale: isSubmitting ? 1 : 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
              >
                <span className="flex items-center justify-center gap-2">
                  {isSubmitting ? (
                    <>
                      <Loader className="w-5 h-5 animate-spin" />
                      Analyzing Research Landscape...
                    </>
                  ) : (
                    <>
                      Discover Research Gaps
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

            {/* Summary Card */}
            {summary && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.4 }}
                className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-2xl p-6 border border-yellow-200"
              >
                <div className="flex items-center gap-3 mb-4">
                  <Award className="w-6 h-6 text-yellow-600" />
                  <h3 className="text-lg font-bold text-gray-900">Analysis Summary</h3>
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Total Gaps</p>
                    <p className="text-2xl font-bold text-yellow-600">
                      {summary.total_gaps_identified}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">High Potential</p>
                    <p className="text-2xl font-bold text-yellow-600">
                      {summary.high_potential_gaps}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Recommended</p>
                    <p className="text-sm font-semibold text-gray-900 mt-2">
                      {summary.recommended_direction}
                    </p>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Research Gaps */}
            {researchGaps.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="space-y-4"
              >
                <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                  <Sparkles className="w-6 h-6 text-yellow-500" />
                  Discovered Research Gaps
                </h2>

                {researchGaps.map((gap, index) => (
                  <motion.div
                    key={gap.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.4, delay: index * 0.1 }}
                    className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-200 shadow-soft hover:shadow-medium transition-all duration-300"
                  >
                    <div className="flex items-start justify-between gap-4 mb-3">
                      <h3 className="text-lg font-bold text-gray-900 flex-1">{gap.title}</h3>
                      <div className="flex gap-2">
                        <div
                          className={`px-3 py-1.5 rounded-lg text-xs font-bold ${getNoveltyColor(
                            gap.novelty_score
                          )}`}
                        >
                          Novelty: {gap.novelty_score}/10
                        </div>
                        <div
                          className={`px-3 py-1.5 rounded-lg text-xs font-bold ${getFeasibilityColor(
                            gap.feasibility_score
                          )}`}
                        >
                          Feasibility: {gap.feasibility_score}/10
                        </div>
                      </div>
                    </div>

                    <p className="text-gray-700 mb-4">{gap.description}</p>

                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div className="p-3 bg-gray-50 rounded-lg">
                        <p className="text-xs text-gray-600 mb-1">Impact Potential</p>
                        <p className="text-sm font-semibold text-gray-900">
                          {gap.impact_potential}
                        </p>
                      </div>
                      <div className="p-3 bg-gray-50 rounded-lg">
                        <p className="text-xs text-gray-600 mb-1">Timeline</p>
                        <p className="text-sm font-semibold text-gray-900">
                          {gap.estimated_timeline}
                        </p>
                      </div>
                    </div>

                    <div className="mb-4">
                      <p className="text-xs font-semibold text-gray-600 mb-2">
                        Suggested Approaches:
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {gap.suggested_approaches.map((approach, i) => (
                          <span
                            key={i}
                            className="px-3 py-1 bg-yellow-50 text-yellow-700 text-xs rounded-full border border-yellow-200"
                          >
                            {approach}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <BookOpen className="w-4 h-4" />
                      <span>{gap.related_papers} related papers found</span>
                    </div>
                  </motion.div>
                ))}
              </motion.div>
            )}

            {/* Download Report Button */}
            {reportUrl && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.4 }}
                className="bg-white/60 backdrop-blur-sm rounded-2xl p-8 border border-gray-200 shadow-soft text-center"
              >
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-yellow-100 text-yellow-600 mb-4">
                  <CheckCircle2 className="w-8 h-8" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">Analysis Complete!</h3>
                <p className="text-gray-600 mb-6">
                  Your research direction report is ready to download
                </p>
                <div className="flex gap-4 justify-center">
                  <motion.button
                    onClick={downloadReport}
                    className="px-6 py-3 bg-yellow-500 text-white rounded-xl font-semibold shadow-lg hover:shadow-glow-yellow transition-all duration-300"
                    whileHover={{ scale: 1.05, y: -2 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <span className="flex items-center gap-2">
                      <Download className="w-5 h-5" />
                      Download Report
                    </span>
                  </motion.button>
                  <motion.button
                    onClick={() => router.push('/dashboard')}
                    className="px-6 py-3 bg-white text-gray-700 rounded-xl font-semibold border border-gray-300 hover:border-gray-400 transition-all duration-300"
                    whileHover={{ scale: 1.05, y: -2 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    Back to Dashboard
                  </motion.button>
                </div>
              </motion.div>
            )}

            {/* Executing Status */}
            {isExecuting && !reportUrl && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="bg-yellow-50 rounded-xl p-4 border border-yellow-200 flex items-center gap-3"
              >
                <Loader className="w-5 h-5 text-yellow-600 animate-spin" />
                <span className="text-sm font-medium text-yellow-900">
                  Analyzing research landscape... This may take several minutes.
                </span>
              </motion.div>
            )}
          </div>
        )}
      </div>
    </Layout>
  )
}

export default ResearchDirectionNewPage
