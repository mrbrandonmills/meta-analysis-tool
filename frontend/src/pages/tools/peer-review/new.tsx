import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Layout from '@/components/layout/Layout'
import { AgentPipeline, AgentState, AgentStep } from '@/components/workflow/AgentPipeline'
import {
  FileText,
  Upload,
  Loader,
  CheckCircle2,
  AlertCircle,
  Download,
  ArrowRight,
  Sparkles,
  ThumbsUp,
  ThumbsDown,
  MessageSquare,
  BookOpen,
  AlertTriangle,
  Target,
  Eye,
  Brain,
  Shield
} from 'lucide-react'
import { useRouter } from 'next/router'

interface PeerReviewFormData {
  manuscript_title: string
  manuscript_text: string
  review_type: 'constructive' | 'technical' | 'ethical'
  reviewer_name: string
  focus_areas: string[]
}

interface ReviewResponse {
  id: string
  status: string
  message: string
  workflow: any
}

interface GeneratedReviewData {
  summary: string
  recommendation: 'accept' | 'minor_revision' | 'major_revision' | 'reject'
  strengths: string[]
  weaknesses: string[]
  detailed_comments: Array<{
    section: string
    comments: string
    suggestions: string[]
  }>
  technical_accuracy: number
  novelty: number
  clarity: number
  confidence: number
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://meta-analysis-tool-production.up.railway.app'

const reviewTypeOptions = [
  {
    value: 'constructive',
    label: 'Constructive Review',
    description: 'Balanced feedback with actionable suggestions',
    icon: ThumbsUp
  },
  {
    value: 'technical',
    label: 'Technical Review',
    description: 'Deep dive into methodology and analysis',
    icon: Brain
  },
  {
    value: 'ethical',
    label: 'Ethical Review',
    description: 'Focus on research ethics and integrity',
    icon: Shield
  }
]

const focusAreaOptions = [
  { value: 'methodology', label: 'Methodology' },
  { value: 'statistics', label: 'Statistical Analysis' },
  { value: 'literature', label: 'Literature Review' },
  { value: 'clarity', label: 'Writing Clarity' },
  { value: 'novelty', label: 'Novelty & Significance' },
  { value: 'ethics', label: 'Research Ethics' }
]

const PeerReviewNewPage: React.FC = () => {
  const router = useRouter()
  const [formData, setFormData] = useState<PeerReviewFormData>({
    manuscript_title: '',
    manuscript_text: '',
    review_type: 'constructive',
    reviewer_name: '',
    focus_areas: ['methodology', 'clarity']
  })

  const [reviewId, setReviewId] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isExecuting, setIsExecuting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [agentSteps, setAgentSteps] = useState<AgentStep[]>([])
  const [reviewData, setReviewData] = useState<GeneratedReviewData | null>(null)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)

  const handleInputChange = (field: keyof PeerReviewFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setUploadedFile(file)

    // Read file content
    const reader = new FileReader()
    reader.onload = (e) => {
      const text = e.target?.result as string
      // Extract text from the file (simplified - in production, use proper PDF/DOCX parsing)
      setFormData(prev => ({ ...prev, manuscript_text: text.substring(0, 10000) }))
    }
    reader.readAsText(file)
  }

  const toggleFocusArea = (area: string) => {
    setFormData(prev => ({
      ...prev,
      focus_areas: prev.focus_areas.includes(area)
        ? prev.focus_areas.filter(a => a !== area)
        : [...prev.focus_areas, area]
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError(null)

    try {
      const response = await fetch(`${API_URL}/api/v1/peer-review/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      })

      if (!response.ok) {
        throw new Error(`Failed to create review: ${response.statusText}`)
      }

      const data: ReviewResponse = await response.json()
      setReviewId(data.id)

      // Initialize agent steps
      const steps = [
        {
          id: '1',
          name: 'Document Analysis',
          description: 'Parsing manuscript structure and content',
          icon: BookOpen,
          state: AgentState.PENDING
        },
        {
          id: '2',
          name: 'Literature Context',
          description: 'Analyzing citations and related work',
          icon: Sparkles,
          state: AgentState.PENDING
        },
        {
          id: '3',
          name: 'Methodology Review',
          description: 'Evaluating research methods and design',
          icon: Brain,
          state: AgentState.PENDING
        },
        {
          id: '4',
          name: 'Quality Assessment',
          description: 'Assessing technical accuracy and rigor',
          icon: Target,
          state: AgentState.PENDING
        },
        {
          id: '5',
          name: 'Ethical Review',
          description: 'Checking research ethics and integrity',
          icon: Shield,
          state: AgentState.PENDING
        },
        {
          id: '6',
          name: 'Review Generation',
          description: 'Creating comprehensive peer review',
          icon: FileText,
          state: AgentState.PENDING
        }
      ]
      setAgentSteps(steps)

      // Auto-execute
      await executeReview(data.id, steps)
    } catch (err: any) {
      setError(err.message || 'Failed to create review')
    } finally {
      setIsSubmitting(false)
    }
  }

  const executeReview = async (id: string, steps: AgentStep[]) => {
    setIsExecuting(true)

    try {
      const response = await fetch(`${API_URL}/api/v1/peer-review/execute/${id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error('Failed to execute review')
      }

      // Poll for status updates
      pollStatus(id, steps)
    } catch (err: any) {
      setError(err.message || 'Failed to execute review')
      setIsExecuting(false)
    }
  }

  const pollStatus = async (id: string, steps: AgentStep[]) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`${API_URL}/api/v1/peer-review/status/${id}`)

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

          // Fetch the generated review
          const reviewResponse = await fetch(`${API_URL}/api/v1/peer-review/result/${id}`)
          if (reviewResponse.ok) {
            const reviewResult = await reviewResponse.json()
            setReviewData(reviewResult)
          }

          // Mark all steps as completed
          setAgentSteps(steps.map(step => ({ ...step, state: AgentState.COMPLETED })))
        } else if (status.status === 'failed') {
          clearInterval(interval)
          setIsExecuting(false)
          setError(status.message || 'Review generation failed')

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

  const downloadReview = async (format: 'pdf' | 'docx') => {
    if (reviewId) {
      window.open(`${API_URL}/api/v1/peer-review/download/${reviewId}?format=${format}`, '_blank')
    }
  }

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation) {
      case 'accept':
        return 'text-green-600 bg-green-100'
      case 'minor_revision':
        return 'text-blue-600 bg-blue-100'
      case 'major_revision':
        return 'text-yellow-600 bg-yellow-100'
      case 'reject':
        return 'text-red-600 bg-red-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  const getRecommendationIcon = (recommendation: string) => {
    switch (recommendation) {
      case 'accept':
        return CheckCircle2
      case 'minor_revision':
        return Eye
      case 'major_revision':
        return AlertTriangle
      case 'reject':
        return ThumbsDown
      default:
        return MessageSquare
    }
  }

  return (
    <Layout title="New Peer Review">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="p-3 rounded-xl bg-purple-100 text-purple-600">
              <FileText className="w-6 h-6" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900">New Peer Review</h1>
          </div>
          <p className="text-gray-600">
            AI-powered manuscript review with 6 specialized analysis agents
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
        {!reviewId ? (
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
                placeholder="e.g., The Effect of Machine Learning on Medical Diagnosis"
                className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all"
                required
              />
            </div>

            {/* File Upload or Text Input */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Manuscript Content *
              </label>

              {/* File Upload Button */}
              <div className="mb-4">
                <label
                  htmlFor="file-upload"
                  className="inline-flex items-center gap-2 px-4 py-2 bg-purple-50 text-purple-600 rounded-lg border-2 border-dashed border-purple-300 hover:bg-purple-100 cursor-pointer transition-all"
                >
                  <Upload className="w-5 h-5" />
                  <span className="text-sm font-medium">
                    {uploadedFile ? uploadedFile.name : 'Upload PDF/DOCX'}
                  </span>
                </label>
                <input
                  id="file-upload"
                  type="file"
                  accept=".pdf,.doc,.docx,.txt"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <p className="text-xs text-gray-500 mt-2">
                  Or paste the manuscript text below
                </p>
              </div>

              {/* Text Area */}
              <textarea
                value={formData.manuscript_text}
                onChange={(e) => handleInputChange('manuscript_text', e.target.value)}
                placeholder="Paste the full manuscript text here, including abstract, introduction, methods, results, and discussion..."
                className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all font-mono text-sm"
                rows={12}
                required
              />
              <p className="text-xs text-gray-500 mt-2">
                {formData.manuscript_text.length} characters
              </p>
            </div>

            {/* Review Type */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-3">
                Review Type *
              </label>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {reviewTypeOptions.map((option) => {
                  const Icon = option.icon
                  return (
                    <motion.button
                      key={option.value}
                      type="button"
                      onClick={() => handleInputChange('review_type', option.value)}
                      className={`p-4 rounded-xl border-2 transition-all text-left ${
                        formData.review_type === option.value
                          ? 'border-purple-500 bg-purple-50'
                          : 'border-gray-200 bg-white hover:border-purple-300'
                      }`}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <Icon className={`w-6 h-6 mb-2 ${
                        formData.review_type === option.value ? 'text-purple-600' : 'text-gray-400'
                      }`} />
                      <h3 className={`text-sm font-semibold mb-1 ${
                        formData.review_type === option.value ? 'text-purple-900' : 'text-gray-900'
                      }`}>
                        {option.label}
                      </h3>
                      <p className="text-xs text-gray-600">
                        {option.description}
                      </p>
                    </motion.button>
                  )
                })}
              </div>
            </div>

            {/* Focus Areas */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-3">
                Focus Areas (Optional)
              </label>
              <div className="flex flex-wrap gap-2">
                {focusAreaOptions.map((option) => (
                  <motion.button
                    key={option.value}
                    type="button"
                    onClick={() => toggleFocusArea(option.value)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                      formData.focus_areas.includes(option.value)
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    {option.label}
                  </motion.button>
                ))}
              </div>
            </div>

            {/* Reviewer Name (Optional) */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Reviewer Name (Optional)
              </label>
              <input
                type="text"
                value={formData.reviewer_name}
                onChange={(e) => handleInputChange('reviewer_name', e.target.value)}
                placeholder="Dr. Jane Smith"
                className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all"
              />
            </div>

            {/* Submit Button */}
            <div className="flex gap-4">
              <motion.button
                type="submit"
                disabled={isSubmitting}
                className="flex-1 px-6 py-4 bg-purple-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-glow-purple transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                whileHover={{ scale: isSubmitting ? 1 : 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
              >
                <span className="flex items-center justify-center gap-2">
                  {isSubmitting ? (
                    <>
                      <Loader className="w-5 h-5 animate-spin" />
                      Creating Review...
                    </>
                  ) : (
                    <>
                      Generate Review
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

            {/* Generated Review */}
            {reviewData && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.4 }}
                className="bg-white/60 backdrop-blur-sm rounded-2xl p-8 border border-gray-200 shadow-soft space-y-6"
              >
                {/* Success Header */}
                <div className="text-center pb-6 border-b border-gray-200">
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 text-green-600 mb-4">
                    <CheckCircle2 className="w-8 h-8" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">
                    Review Complete!
                  </h3>
                  <p className="text-gray-600">
                    Your comprehensive peer review is ready
                  </p>
                </div>

                {/* Recommendation */}
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-3">Recommendation</h4>
                  <div className="flex items-center gap-3">
                    {(() => {
                      const Icon = getRecommendationIcon(reviewData.recommendation)
                      return (
                        <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${getRecommendationColor(reviewData.recommendation)}`}>
                          <Icon className="w-5 h-5" />
                          <span className="font-semibold capitalize">
                            {reviewData.recommendation.replace('_', ' ')}
                          </span>
                        </div>
                      )
                    })()}
                    <div className="flex gap-2 text-sm text-gray-600">
                      <span>Confidence: {Math.round(reviewData.confidence * 100)}%</span>
                    </div>
                  </div>
                </div>

                {/* Summary */}
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-3">Overall Assessment</h4>
                  <div className="p-4 rounded-xl bg-gray-50 border border-gray-200">
                    <p className="text-gray-700 leading-relaxed">{reviewData.summary}</p>
                  </div>
                </div>

                {/* Ratings */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="p-4 rounded-xl bg-blue-50 border border-blue-200">
                    <div className="text-2xl font-bold text-blue-600 mb-1">
                      {reviewData.technical_accuracy}/5
                    </div>
                    <div className="text-sm text-blue-700">Technical Accuracy</div>
                  </div>
                  <div className="p-4 rounded-xl bg-purple-50 border border-purple-200">
                    <div className="text-2xl font-bold text-purple-600 mb-1">
                      {reviewData.novelty}/5
                    </div>
                    <div className="text-sm text-purple-700">Novelty</div>
                  </div>
                  <div className="p-4 rounded-xl bg-green-50 border border-green-200">
                    <div className="text-2xl font-bold text-green-600 mb-1">
                      {reviewData.clarity}/5
                    </div>
                    <div className="text-sm text-green-700">Clarity</div>
                  </div>
                </div>

                {/* Strengths */}
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                    <ThumbsUp className="w-4 h-4 text-green-600" />
                    Strengths
                  </h4>
                  <ul className="space-y-2">
                    {reviewData.strengths.map((strength, index) => (
                      <li key={index} className="flex items-start gap-2 text-gray-700">
                        <CheckCircle2 className="w-4 h-4 text-green-600 flex-shrink-0 mt-1" />
                        <span>{strength}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Weaknesses */}
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-yellow-600" />
                    Areas for Improvement
                  </h4>
                  <ul className="space-y-2">
                    {reviewData.weaknesses.map((weakness, index) => (
                      <li key={index} className="flex items-start gap-2 text-gray-700">
                        <AlertTriangle className="w-4 h-4 text-yellow-600 flex-shrink-0 mt-1" />
                        <span>{weakness}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Detailed Comments by Section */}
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                    <MessageSquare className="w-4 h-4 text-purple-600" />
                    Detailed Comments
                  </h4>
                  <div className="space-y-4">
                    {reviewData.detailed_comments.map((comment, index) => (
                      <div key={index} className="p-4 rounded-xl bg-purple-50 border border-purple-200">
                        <h5 className="font-semibold text-purple-900 mb-2">{comment.section}</h5>
                        <p className="text-gray-700 mb-3">{comment.comments}</p>
                        {comment.suggestions.length > 0 && (
                          <div>
                            <div className="text-sm font-medium text-purple-700 mb-1">Suggestions:</div>
                            <ul className="space-y-1">
                              {comment.suggestions.map((suggestion, sIndex) => (
                                <li key={sIndex} className="text-sm text-gray-600 pl-4 border-l-2 border-purple-300">
                                  {suggestion}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Download Buttons */}
                <div className="pt-6 border-t border-gray-200">
                  <div className="flex gap-4 justify-center">
                    <motion.button
                      onClick={() => downloadReview('pdf')}
                      className="px-6 py-3 bg-purple-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-glow-purple transition-all duration-300"
                      whileHover={{ scale: 1.05, y: -2 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <span className="flex items-center gap-2">
                        <Download className="w-5 h-5" />
                        Download as PDF
                      </span>
                    </motion.button>
                    <motion.button
                      onClick={() => downloadReview('docx')}
                      className="px-6 py-3 bg-white text-purple-600 rounded-xl font-semibold border-2 border-purple-600 hover:bg-purple-50 transition-all duration-300"
                      whileHover={{ scale: 1.05, y: -2 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <span className="flex items-center gap-2">
                        <Download className="w-5 h-5" />
                        Download as DOCX
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
                </div>
              </motion.div>
            )}

            {/* Executing Status */}
            {isExecuting && !reviewData && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="bg-purple-50 rounded-xl p-4 border border-purple-200 flex items-center gap-3"
              >
                <Loader className="w-5 h-5 text-purple-600 animate-spin" />
                <span className="text-sm font-medium text-purple-900">
                  Generating review... This may take several minutes.
                </span>
              </motion.div>
            )}
          </div>
        )}
      </div>
    </Layout>
  )
}

export default PeerReviewNewPage
