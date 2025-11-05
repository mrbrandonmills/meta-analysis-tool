'use client'

import React, { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import { motion, AnimatePresence } from 'framer-motion'
import Layout from '@/components/layout/Layout'
import AgentPipeline, { AgentState, AgentStep } from '@/components/workflow/AgentPipeline'
import { useAppStore } from '@/stores/useAppStore'
import { Project, ProjectStatus, ToolType, Workflow, WorkflowStatus } from '@/lib/types'
import {
  ArrowLeft,
  Download,
  Edit,
  Trash2,
  Play,
  Pause,
  RotateCcw,
  CheckCircle2,
  Clock,
  AlertCircle,
  Calendar,
  User,
  Folder,
  FileText,
  BarChart3,
  Microscope,
  Users,
  Lightbulb,
  Share2,
  Copy,
  ExternalLink,
  Loader2,
  AlertTriangle,
  Info,
  TrendingUp,
  Search,
  Filter,
  Award,
  Database
} from 'lucide-react'
import { formatRelativeTime } from '@/lib/utils'
import toast from 'react-hot-toast'

const toolIcons = {
  [ToolType.META_ANALYSIS]: Microscope,
  [ToolType.REVIEWER_MATCHER]: Users,
  [ToolType.PEER_REVIEW]: FileText,
  [ToolType.RESEARCH_DIRECTION]: Lightbulb
}

const toolColors = {
  [ToolType.META_ANALYSIS]: 'blue',
  [ToolType.REVIEWER_MATCHER]: 'green',
  [ToolType.PEER_REVIEW]: 'purple',
  [ToolType.RESEARCH_DIRECTION]: 'yellow'
}

const toolLabels = {
  [ToolType.META_ANALYSIS]: 'Meta-Analysis',
  [ToolType.REVIEWER_MATCHER]: 'Reviewer Matcher',
  [ToolType.PEER_REVIEW]: 'Peer Review',
  [ToolType.RESEARCH_DIRECTION]: 'Research Direction'
}

const statusConfig: Record<ProjectStatus, { icon: any; color: string; label: string; bgColor: string }> = {
  [ProjectStatus.DRAFT]: {
    icon: Clock,
    color: 'gray',
    label: 'Draft',
    bgColor: 'bg-gray-100 text-gray-700 border-gray-200'
  },
  [ProjectStatus.IN_PROGRESS]: {
    icon: Clock,
    color: 'blue',
    label: 'In Progress',
    bgColor: 'bg-blue-100 text-blue-700 border-blue-200'
  },
  [ProjectStatus.COMPLETED]: {
    icon: CheckCircle2,
    color: 'green',
    label: 'Completed',
    bgColor: 'bg-green-100 text-green-700 border-green-200'
  },
  [ProjectStatus.FAILED]: {
    icon: AlertCircle,
    color: 'red',
    label: 'Failed',
    bgColor: 'bg-red-100 text-red-700 border-red-200'
  },
  [ProjectStatus.PAUSED]: {
    icon: Pause,
    color: 'yellow',
    label: 'Paused',
    bgColor: 'bg-yellow-100 text-yellow-700 border-yellow-200'
  },
  [ProjectStatus.CANCELLED]: {
    icon: AlertCircle,
    color: 'gray',
    label: 'Cancelled',
    bgColor: 'bg-gray-100 text-gray-700 border-gray-200'
  }
}

// Agent step icons for pipeline visualization
const agentIcons: Record<string, any> = {
  'search': Search,
  'screening': Filter,
  'quality': Award,
  'extraction': Database,
  'statistical': BarChart3,
  'report': FileText,
  'coordinator': Folder,
  'verification': CheckCircle2
}

const ProjectDetailPage: React.FC = () => {
  const router = useRouter()
  const { id } = router.query
  const { projects, deleteProject, setCurrentProject } = useAppStore()

  const [project, setProject] = useState<Project | null>(null)
  const [loading, setLoading] = useState(true)
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false)
  const [activeTab, setActiveTab] = useState<'overview' | 'workflows' | 'findings' | 'audit'>('overview')

  useEffect(() => {
    if (id && typeof id === 'string') {
      const foundProject = projects.find(p => p.id === id)
      if (foundProject) {
        setProject(foundProject)
        setCurrentProject(foundProject)
        setLoading(false)
      } else {
        // Project not found
        setTimeout(() => {
          setLoading(false)
        }, 500)
      }
    }
  }, [id, projects])

  const handleDelete = () => {
    if (project) {
      deleteProject(project.id)
      toast.success('Project deleted successfully')
      router.push('/projects')
    }
  }

  const handleDownloadReport = () => {
    toast.success('Report downloaded successfully')
    // TODO: Implement actual report download
  }

  const handleShare = () => {
    if (project) {
      navigator.clipboard.writeText(window.location.href)
      toast.success('Project link copied to clipboard')
    }
  }

  const handleEdit = () => {
    if (project) {
      // Navigate to edit page based on tool type
      const editRoutes = {
        [ToolType.META_ANALYSIS]: `/tools/meta-analysis/${project.id}`,
        [ToolType.REVIEWER_MATCHER]: `/tools/reviewer-matcher/${project.id}`,
        [ToolType.PEER_REVIEW]: `/tools/peer-review/${project.id}`,
        [ToolType.RESEARCH_DIRECTION]: `/tools/research-direction/${project.id}`
      }
      router.push(editRoutes[project.toolType as ToolType] || '/dashboard')
    }
  }

  // Convert workflows to agent steps for pipeline visualization
  const getAgentSteps = (): AgentStep[] => {
    if (!project || !project.workflows || project.workflows.length === 0) {
      return []
    }

    return project.workflows.map((workflow, index) => {
      const agentNameLower = workflow.agentName.toLowerCase()
      const iconKey = Object.keys(agentIcons).find(key => agentNameLower.includes(key)) || 'coordinator'

      let state: AgentState
      switch (workflow.status) {
        case WorkflowStatus.COMPLETED:
          state = AgentState.COMPLETED
          break
        case WorkflowStatus.IN_PROGRESS:
          state = AgentState.PROCESSING
          break
        case WorkflowStatus.FAILED:
          state = AgentState.ERROR
          break
        default:
          state = AgentState.PENDING
      }

      return {
        id: workflow.id,
        name: workflow.agentName,
        description: workflow.agentRole,
        icon: agentIcons[iconKey],
        state,
        progress: workflow.progress || 0
      }
    })
  }

  // Calculate overall progress
  const calculateProgress = (): number => {
    if (!project || !project.workflows || project.workflows.length === 0) {
      return 0
    }

    const completedWorkflows = project.workflows.filter(w => w.status === WorkflowStatus.COMPLETED).length
    return Math.round((completedWorkflows / project.workflows.length) * 100)
  }

  if (loading) {
    return (
      <Layout title="Loading...">
        <div className="flex items-center justify-center min-h-[60vh]">
          <Loader2 className="w-8 h-8 text-primary-600 animate-spin" />
        </div>
      </Layout>
    )
  }

  if (!project) {
    return (
      <Layout title="Project Not Found">
        <div className="flex flex-col items-center justify-center min-h-[60vh]">
          <motion.div
            className="text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gray-100 text-gray-400 mb-6">
              <AlertTriangle className="w-10 h-10" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Project Not Found</h1>
            <p className="text-lg text-gray-600 mb-8">
              The project you're looking for doesn't exist or has been deleted.
            </p>
            <motion.button
              className="px-6 py-3 bg-primary-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-glow-primary transition-all duration-300 flex items-center gap-2 mx-auto"
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => router.push('/projects')}
            >
              <ArrowLeft className="w-5 h-5" />
              Back to Projects
            </motion.button>
          </motion.div>
        </div>
      </Layout>
    )
  }

  const Icon = toolIcons[project.toolType as ToolType]
  const color = toolColors[project.toolType as ToolType]
  const StatusIcon = statusConfig[project.status].icon
  const progress = calculateProgress()

  return (
    <Layout title={project.title}>
      <div className="space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          {/* Back Button */}
          <button
            onClick={() => router.push('/projects')}
            className="group flex items-center gap-2 text-gray-600 hover:text-gray-900 font-medium mb-6 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
            Back to Projects
          </button>

          {/* Project Header Card */}
          <div className="p-8 rounded-3xl bg-gradient-to-br from-white/80 to-white/40 backdrop-blur-sm border border-gray-200 shadow-soft">
            <div className="flex items-start justify-between flex-wrap gap-4 mb-6">
              <div className="flex items-start gap-4 flex-1 min-w-0">
                {/* Tool Icon */}
                <motion.div
                  className={`inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-${color}-100 text-${color}-600 shadow-sm flex-shrink-0`}
                  whileHover={{ scale: 1.05, rotate: 5 }}
                  transition={{ type: 'spring', stiffness: 400, damping: 10 }}
                >
                  <Icon className="w-8 h-8" />
                </motion.div>

                <div className="flex-1 min-w-0">
                  {/* Status Badge */}
                  <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-semibold mb-3 border ${statusConfig[project.status].bgColor}`}>
                    <StatusIcon className="w-4 h-4" />
                    {statusConfig[project.status].label}
                  </div>

                  {/* Title */}
                  <h1 className="text-3xl font-bold text-gray-900 mb-2">{project.title}</h1>

                  {/* Description */}
                  {project.description && (
                    <p className="text-lg text-gray-600 mb-4 leading-relaxed">
                      {project.description}
                    </p>
                  )}

                  {/* Meta Info */}
                  <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500">
                    <div className="flex items-center gap-1.5">
                      <Folder className="w-4 h-4" />
                      <span className="font-medium">{toolLabels[project.toolType as ToolType]}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <Calendar className="w-4 h-4" />
                      <span>Updated {formatRelativeTime(project.updatedAt.toString())}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <User className="w-4 h-4" />
                      <span>Project ID: {project.id.slice(0, 8)}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-2 flex-shrink-0">
                <motion.button
                  className="p-3 rounded-xl border border-gray-200 bg-white hover:bg-gray-50 transition-all"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleShare}
                  title="Share Project"
                >
                  <Share2 className="w-5 h-5 text-gray-700" />
                </motion.button>

                {project.status === ProjectStatus.COMPLETED && (
                  <motion.button
                    className="px-4 py-3 rounded-xl border border-gray-200 bg-white hover:bg-gray-50 font-medium text-gray-700 transition-all flex items-center gap-2"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleDownloadReport}
                  >
                    <Download className="w-5 h-5" />
                    Download Report
                  </motion.button>
                )}

                <motion.button
                  className="px-4 py-3 rounded-xl border border-primary-300 bg-primary-50 hover:bg-primary-100 font-medium text-primary-700 transition-all flex items-center gap-2"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleEdit}
                >
                  <Edit className="w-5 h-5" />
                  Edit
                </motion.button>

                <motion.button
                  className="p-3 rounded-xl border border-red-200 bg-red-50 hover:bg-red-100 transition-all"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setDeleteConfirmOpen(true)}
                  title="Delete Project"
                >
                  <Trash2 className="w-5 h-5 text-red-600" />
                </motion.button>
              </div>
            </div>

            {/* Progress Bar */}
            {project.status === ProjectStatus.IN_PROGRESS && (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium text-gray-700">Overall Progress</span>
                  <span className="font-semibold text-gray-900">{progress}%</span>
                </div>
                <div className="w-full h-2.5 bg-gray-100 rounded-full overflow-hidden">
                  <motion.div
                    className={`h-full bg-gradient-to-r from-${color}-500 to-${color}-600 rounded-full`}
                    initial={{ width: 0 }}
                    animate={{ width: `${progress}%` }}
                    transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }}
                  />
                </div>
              </div>
            )}
          </div>
        </motion.div>

        {/* Tabs */}
        <motion.div
          className="flex items-center gap-2 border-b border-gray-200"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          {[
            { id: 'overview', label: 'Overview', icon: Info },
            { id: 'workflows', label: 'Workflows', icon: BarChart3 },
            { id: 'findings', label: 'Findings', icon: TrendingUp },
            { id: 'audit', label: 'Audit Trail', icon: FileText }
          ].map((tab) => {
            const TabIcon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-4 py-3 font-medium transition-all relative ${
                  activeTab === tab.id
                    ? 'text-primary-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <TabIcon className="w-4 h-4" />
                {tab.label}
                {activeTab === tab.id && (
                  <motion.div
                    className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-600"
                    layoutId="activeTab"
                  />
                )}
              </button>
            )
          })}
        </motion.div>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* Project Details */}
                <div className="p-6 rounded-2xl bg-white/60 backdrop-blur-sm border border-gray-200">
                  <h2 className="text-xl font-bold text-gray-900 mb-4">Project Details</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600 mb-1">Tool Type</p>
                      <p className="text-base font-semibold text-gray-900">{toolLabels[project.toolType as ToolType]}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 mb-1">Status</p>
                      <p className="text-base font-semibold text-gray-900">{statusConfig[project.status].label}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 mb-1">Created</p>
                      <p className="text-base font-semibold text-gray-900">
                        {new Date(project.createdAt).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 mb-1">Last Updated</p>
                      <p className="text-base font-semibold text-gray-900">
                        {new Date(project.updatedAt).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Workflows Summary */}
                {project.workflows && project.workflows.length > 0 && (
                  <div className="p-6 rounded-2xl bg-white/60 backdrop-blur-sm border border-gray-200">
                    <h2 className="text-xl font-bold text-gray-900 mb-4">Workflow Status</h2>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                      <div className="p-4 rounded-xl bg-blue-50 border border-blue-200">
                        <p className="text-sm text-blue-600 font-medium mb-1">Total Steps</p>
                        <p className="text-2xl font-bold text-blue-700">{project.workflows.length}</p>
                      </div>
                      <div className="p-4 rounded-xl bg-green-50 border border-green-200">
                        <p className="text-sm text-green-600 font-medium mb-1">Completed</p>
                        <p className="text-2xl font-bold text-green-700">
                          {project.workflows.filter(w => w.status === WorkflowStatus.COMPLETED).length}
                        </p>
                      </div>
                      <div className="p-4 rounded-xl bg-yellow-50 border border-yellow-200">
                        <p className="text-sm text-yellow-600 font-medium mb-1">In Progress</p>
                        <p className="text-2xl font-bold text-yellow-700">
                          {project.workflows.filter(w => w.status === WorkflowStatus.IN_PROGRESS).length}
                        </p>
                      </div>
                      <div className="p-4 rounded-xl bg-red-50 border border-red-200">
                        <p className="text-sm text-red-600 font-medium mb-1">Failed</p>
                        <p className="text-2xl font-bold text-red-700">
                          {project.workflows.filter(w => w.status === WorkflowStatus.FAILED).length}
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Workflows Tab */}
            {activeTab === 'workflows' && (
              <div className="space-y-6">
                {/* Agent Pipeline Visualization */}
                {project.workflows && project.workflows.length > 0 && (
                  <div className="p-6 rounded-2xl bg-white/60 backdrop-blur-sm border border-gray-200">
                    <h2 className="text-xl font-bold text-gray-900 mb-6">Agent Pipeline</h2>
                    <AgentPipeline steps={getAgentSteps()} />
                  </div>
                )}

                {/* Workflow Details */}
                {project.workflows && project.workflows.length > 0 ? (
                  <div className="space-y-4">
                    <h2 className="text-xl font-bold text-gray-900">Workflow Details</h2>
                    {project.workflows.map((workflow, index) => (
                      <motion.div
                        key={workflow.id}
                        className="p-6 rounded-2xl bg-white/60 backdrop-blur-sm border border-gray-200"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3, delay: index * 0.05 }}
                      >
                        <div className="flex items-start justify-between mb-4">
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900">{workflow.agentName}</h3>
                            <p className="text-sm text-gray-600">{workflow.agentRole}</p>
                          </div>
                          <div className={`px-3 py-1.5 rounded-lg text-sm font-semibold ${
                            workflow.status === WorkflowStatus.COMPLETED ? 'bg-green-100 text-green-700' :
                            workflow.status === WorkflowStatus.IN_PROGRESS ? 'bg-blue-100 text-blue-700' :
                            workflow.status === WorkflowStatus.FAILED ? 'bg-red-100 text-red-700' :
                            'bg-gray-100 text-gray-700'
                          }`}>
                            {workflow.status}
                          </div>
                        </div>

                        {workflow.progress !== undefined && (
                          <div className="mb-4">
                            <div className="flex items-center justify-between text-sm mb-2">
                              <span className="text-gray-600">Progress</span>
                              <span className="font-semibold text-gray-900">{workflow.progress}%</span>
                            </div>
                            <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-gradient-to-r from-blue-500 to-blue-600 rounded-full"
                                style={{ width: `${workflow.progress}%` }}
                              />
                            </div>
                          </div>
                        )}

                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <p className="text-gray-600 mb-1">Started</p>
                            <p className="font-medium text-gray-900">
                              {new Date(workflow.startedAt).toLocaleString()}
                            </p>
                          </div>
                          {workflow.completedAt && (
                            <div>
                              <p className="text-gray-600 mb-1">Completed</p>
                              <p className="font-medium text-gray-900">
                                {new Date(workflow.completedAt).toLocaleString()}
                              </p>
                            </div>
                          )}
                          {workflow.durationSeconds && (
                            <div>
                              <p className="text-gray-600 mb-1">Duration</p>
                              <p className="font-medium text-gray-900">
                                {Math.round(workflow.durationSeconds / 60)} minutes
                              </p>
                            </div>
                          )}
                        </div>

                        {workflow.errorMessage && (
                          <div className="mt-4 p-3 rounded-lg bg-red-50 border border-red-200">
                            <p className="text-sm text-red-700 font-medium">Error: {workflow.errorMessage}</p>
                          </div>
                        )}
                      </motion.div>
                    ))}
                  </div>
                ) : (
                  <div className="p-12 rounded-2xl bg-white/60 backdrop-blur-sm border border-gray-200 text-center">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gray-100 text-gray-400 mb-4">
                      <BarChart3 className="w-8 h-8" />
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">No Workflows Yet</h3>
                    <p className="text-gray-600">Workflows will appear here once the project starts processing.</p>
                  </div>
                )}
              </div>
            )}

            {/* Findings Tab */}
            {activeTab === 'findings' && (
              <div className="p-6 rounded-2xl bg-white/60 backdrop-blur-sm border border-gray-200">
                {project.findings && Object.keys(project.findings).length > 0 ? (
                  <div>
                    <h2 className="text-xl font-bold text-gray-900 mb-4">Research Findings</h2>
                    <pre className="text-sm text-gray-700 bg-gray-50 p-4 rounded-xl overflow-auto">
                      {JSON.stringify(project.findings, null, 2)}
                    </pre>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gray-100 text-gray-400 mb-4">
                      <TrendingUp className="w-8 h-8" />
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">No Findings Yet</h3>
                    <p className="text-gray-600">
                      Research findings and results will be displayed here once the analysis is complete.
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Audit Trail Tab */}
            {activeTab === 'audit' && (
              <div className="space-y-4">
                {project.auditTrail && project.auditTrail.length > 0 ? (
                  <>
                    <h2 className="text-xl font-bold text-gray-900">Decision History</h2>
                    {project.auditTrail.map((decision, index) => (
                      <motion.div
                        key={index}
                        className="p-6 rounded-2xl bg-white/60 backdrop-blur-sm border border-gray-200"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3, delay: index * 0.05 }}
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900">{decision.agentName}</h3>
                            <p className="text-sm text-gray-600">{decision.agentRole}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-xs text-gray-500">
                              {new Date(decision.timestamp).toLocaleString()}
                            </p>
                            <div className="mt-1 px-2 py-1 rounded bg-primary-100 text-primary-700 text-xs font-semibold">
                              {Math.round(decision.confidence * 100)}% confidence
                            </div>
                          </div>
                        </div>

                        <div className="space-y-2">
                          <div>
                            <p className="text-sm font-medium text-gray-700 mb-1">Decision:</p>
                            <p className="text-sm text-gray-900">{decision.decision}</p>
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-700 mb-1">Reasoning:</p>
                            <p className="text-sm text-gray-900">{decision.reasoning}</p>
                          </div>
                          {decision.metadata && Object.keys(decision.metadata).length > 0 && (
                            <details className="mt-2">
                              <summary className="text-sm font-medium text-gray-700 cursor-pointer hover:text-gray-900">
                                Additional Metadata
                              </summary>
                              <pre className="mt-2 text-xs text-gray-600 bg-gray-50 p-3 rounded-lg overflow-auto">
                                {JSON.stringify(decision.metadata, null, 2)}
                              </pre>
                            </details>
                          )}
                        </div>
                      </motion.div>
                    ))}
                  </>
                ) : (
                  <div className="p-12 rounded-2xl bg-white/60 backdrop-blur-sm border border-gray-200 text-center">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gray-100 text-gray-400 mb-4">
                      <FileText className="w-8 h-8" />
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">No Audit Trail Yet</h3>
                    <p className="text-gray-600">
                      Agent decisions and reasoning will be recorded here as the project progresses.
                    </p>
                  </div>
                )}
              </div>
            )}
          </motion.div>
        </AnimatePresence>

        {/* Delete Confirmation Modal */}
        <AnimatePresence>
          {deleteConfirmOpen && (
            <motion.div
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setDeleteConfirmOpen(false)}
            >
              <motion.div
                className="bg-white rounded-2xl p-8 max-w-md w-full shadow-2xl"
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex items-center justify-center w-16 h-16 rounded-2xl bg-red-100 text-red-600 mb-4 mx-auto">
                  <AlertTriangle className="w-8 h-8" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 text-center mb-3">Delete Project?</h2>
                <p className="text-gray-600 text-center mb-6">
                  Are you sure you want to delete "{project.title}"? This action cannot be undone.
                </p>
                <div className="flex gap-3">
                  <button
                    onClick={() => setDeleteConfirmOpen(false)}
                    className="flex-1 px-4 py-3 rounded-xl border border-gray-300 text-gray-700 font-semibold hover:bg-gray-50 transition-all"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleDelete}
                    className="flex-1 px-4 py-3 rounded-xl bg-red-600 text-white font-semibold hover:bg-red-700 transition-all"
                  >
                    Delete
                  </button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </Layout>
  )
}

export default ProjectDetailPage
