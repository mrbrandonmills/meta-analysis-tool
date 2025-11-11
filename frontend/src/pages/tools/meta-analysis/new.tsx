import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Layout from '@/components/layout/Layout'
import AgentPipeline, { AgentState, AgentStep } from '@/components/workflow/AgentPipeline'
import ProgressTracker from '@/components/workflow/ProgressTracker'
import {
  Microscope,
  Plus,
  Trash2,
  Loader,
  CheckCircle2,
  AlertCircle,
  Download,
  ArrowRight,
  Search,
  Filter,
  Award,
  FileText,
  BarChart3,
  FileDown,
  Bell
} from 'lucide-react'
import { useRouter } from 'next/router'
import { notifyComplete, initializeNotifications } from '@/lib/notifications'

interface MetaAnalysisFormData {
  research_question: string
  topic: string
  inclusion_criteria: string[]
  exclusion_criteria: string[]
  databases: string[]
  peer_review_only: boolean
  expert_name: string
}

interface AnalysisResponse {
  id: string
  status: string
  message: string
  workflow: any
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://meta-analysis-tool-production.up.railway.app'

const MetaAnalysisNewPage: React.FC = () => {
  const router = useRouter()
  const [formData, setFormData] = useState<MetaAnalysisFormData>({
    research_question: '',
    topic: '',
    inclusion_criteria: [''],
    exclusion_criteria: [''],
    databases: ['PubMed'],
    peer_review_only: true,
    expert_name: ''
  })

  const [analysisId, setAnalysisId] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [reportUrl, setReportUrl] = useState<string | null>(null)
  const [notificationsEnabled, setNotificationsEnabled] = useState(false)

  // Initialize notifications on mount
  useEffect(() => {
    initializeNotifications().then(() => {
      setNotificationsEnabled(true)
    })
  }, [])

  const handleInputChange = (field: keyof MetaAnalysisFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const addCriterion = (type: 'inclusion_criteria' | 'exclusion_criteria') => {
    setFormData(prev => ({
      ...prev,
      [type]: [...prev[type], '']
    }))
  }

  const updateCriterion = (type: 'inclusion_criteria' | 'exclusion_criteria', index: number, value: string) => {
    setFormData(prev => ({
      ...prev,
      [type]: prev[type].map((item, i) => i === index ? value : item)
    }))
  }

  const removeCriterion = (type: 'inclusion_criteria' | 'exclusion_criteria', index: number) => {
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
      // Filter out empty criteria
      const cleanedData = {
        ...formData,
        inclusion_criteria: formData.inclusion_criteria.filter(c => c.trim()),
        exclusion_criteria: formData.exclusion_criteria.filter(c => c.trim())
      }

      const response = await fetch(`${API_URL}/api/v1/meta-analysis/create`, {
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

      // Execute the analysis
      await executeAnalysis(data.id)
    } catch (err: any) {
      setError(err.message || 'Failed to create analysis')
    } finally {
      setIsSubmitting(false)
    }
  }

  const executeAnalysis = async (id: string) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/meta-analysis/execute/${id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error('Failed to execute analysis')
      }
    } catch (err: any) {
      setError(err.message || 'Failed to execute analysis')
    }
  }

  const handleComplete = () => {
    // Notify user
    notifyComplete(
      'Meta-Analysis Complete!',
      'Your systematic review has been successfully completed.',
      {
        onClick: () => {
          if (reportUrl) {
            window.open(reportUrl, '_blank')
          }
        }
      }
    )

    // Set report URL
    setReportUrl(`${API_URL}/api/v1/meta-analysis/report/${analysisId}`)
  }

  const downloadReport = async () => {
    if (reportUrl) {
      window.open(reportUrl, '_blank')
    }
  }

  return (
    <Layout title="New Meta-Analysis">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="p-3 rounded-xl bg-blue-100 text-blue-600">
              <Microscope className="w-6 h-6" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900">New Meta-Analysis</h1>
          </div>
          <p className="text-gray-600">
            AI-powered systematic review with 6 specialized research agents
          </p>
          {notificationsEnabled && (
            <div className="mt-2 flex items-center gap-2 text-sm text-green-600">
              <Bell className="w-4 h-4" />
              <span>Notifications enabled - you'll be notified when complete</span>
            </div>
          )}
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

        {/* Form or Progress Tracker */}
        {!analysisId ? (
          <motion.form
            onSubmit={handleSubmit}
            className="space-y-6 bg-white/60 backdrop-blur-sm rounded-2xl p-8 border border-gray-200 shadow-soft"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            {/* Research Question */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Research Question *
              </label>
              <textarea
                value={formData.research_question}
                onChange={(e) => handleInputChange('research_question', e.target.value)}
                placeholder="e.g., What is the effect of cognitive behavioral therapy on depression in adults?"
                className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all"
                rows={3}
                required
              />
            </div>

            {/* Topic */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Topic/Keywords *
              </label>
              <input
                type="text"
                value={formData.topic}
                onChange={(e) => handleInputChange('topic', e.target.value)}
                placeholder="e.g., cognitive behavioral therapy, depression, mental health"
                className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all"
                required
              />
            </div>

            {/* Inclusion Criteria */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Inclusion Criteria
              </label>
              {formData.inclusion_criteria.map((criterion, index) => (
                <div key={index} className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={criterion}
                    onChange={(e) => updateCriterion('inclusion_criteria', index, e.target.value)}
                    placeholder="e.g., Randomized controlled trials"
                    className="flex-1 px-4 py-2 rounded-lg border border-gray-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all"
                  />
                  {formData.inclusion_criteria.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeCriterion('inclusion_criteria', index)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  )}
                </div>
              ))}
              <button
                type="button"
                onClick={() => addCriterion('inclusion_criteria')}
                className="flex items-center gap-2 text-sm font-medium text-primary-600 hover:text-primary-700 mt-2"
              >
                <Plus className="w-4 h-4" />
                Add Criterion
              </button>
            </div>

            {/* Exclusion Criteria */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Exclusion Criteria
              </label>
              {formData.exclusion_criteria.map((criterion, index) => (
                <div key={index} className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={criterion}
                    onChange={(e) => updateCriterion('exclusion_criteria', index, e.target.value)}
                    placeholder="e.g., Non-English studies"
                    className="flex-1 px-4 py-2 rounded-lg border border-gray-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all"
                  />
                  {formData.exclusion_criteria.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeCriterion('exclusion_criteria', index)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  )}
                </div>
              ))}
              <button
                type="button"
                onClick={() => addCriterion('exclusion_criteria')}
                className="flex items-center gap-2 text-sm font-medium text-primary-600 hover:text-primary-700 mt-2"
              >
                <Plus className="w-4 h-4" />
                Add Criterion
              </button>
            </div>

            {/* Peer Review Only */}
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="peer_review_only"
                checked={formData.peer_review_only}
                onChange={(e) => handleInputChange('peer_review_only', e.target.checked)}
                className="w-5 h-5 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <label htmlFor="peer_review_only" className="text-sm font-medium text-gray-900">
                Peer-reviewed studies only (exclude preprints)
              </label>
            </div>

            {/* Expert Name (Optional) */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Your Name (Optional)
              </label>
              <input
                type="text"
                value={formData.expert_name}
                onChange={(e) => handleInputChange('expert_name', e.target.value)}
                placeholder="Dr. Jane Smith"
                className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all"
              />
            </div>

            {/* Submit Button */}
            <div className="flex gap-4">
              <motion.button
                type="submit"
                disabled={isSubmitting}
                className="flex-1 px-6 py-4 bg-primary-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-glow-primary transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                whileHover={{ scale: isSubmitting ? 1 : 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
              >
                <span className="flex items-center justify-center gap-2">
                  {isSubmitting ? (
                    <>
                      <Loader className="w-5 h-5 animate-spin" />
                      Creating Analysis...
                    </>
                  ) : (
                    <>
                      Start Analysis
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
            {/* Progress Tracker */}
            <ProgressTracker
              taskId={analysisId}
              taskType="meta-analysis"
              title="Running Meta-Analysis"
              onComplete={handleComplete}
            />

            {/* Download Report Button */}
            {reportUrl && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.4 }}
                className="bg-white/60 backdrop-blur-sm rounded-2xl p-8 border border-gray-200 shadow-soft text-center"
              >
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 text-green-600 mb-4">
                  <CheckCircle2 className="w-8 h-8" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">
                  Analysis Complete!
                </h3>
                <p className="text-gray-600 mb-6">
                  Your meta-analysis report is ready to download
                </p>
                <div className="flex gap-4 justify-center">
                  <motion.button
                    onClick={downloadReport}
                    className="px-6 py-3 bg-primary-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-glow-primary transition-all duration-300"
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
          </div>
        )}
      </div>
    </Layout>
  )
}

export default MetaAnalysisNewPage
