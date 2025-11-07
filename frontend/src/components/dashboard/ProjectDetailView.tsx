'use client'

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useRouter } from 'next/router'
import {
  ArrowLeft,
  Download,
  Trash2,
  Copy,
  Play,
  Pause,
  MoreVertical,
  Calendar,
  Clock,
  CheckCircle2,
  AlertCircle,
  Users,
  FileText,
  BarChart3,
  Activity,
  Eye,
  EyeOff,
  ExternalLink,
  Share2,
  Edit,
} from 'lucide-react'
import { Project, Workflow, WorkflowStatus, ProjectStatus, AgentDecision } from '@/lib/types'
import { formatDate, formatRelativeTime, formatDuration } from '@/lib/utils'
import WorkflowVisualizer from '@/components/shared/WorkflowVisualizer'
import AgentStatusCard from '@/components/shared/AgentStatusCard'
import Badge from '@/components/shared/Badge'

interface ProjectDetailViewProps {
  project: Project
  onBack?: () => void
  onDelete?: (projectId: string) => void
  onClone?: (projectId: string) => void
  onPause?: (projectId: string) => void
  onResume?: (projectId: string) => void
  onExport?: (projectId: string, format: 'json' | 'csv' | 'pdf') => void
  onEdit?: (projectId: string) => void
}

const ProjectDetailView: React.FC<ProjectDetailViewProps> = ({
  project,
  onBack,
  onDelete,
  onClone,
  onPause,
  onResume,
  onExport,
  onEdit,
}) => {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState<'overview' | 'workflows' | 'decisions' | 'results'>('overview')
  const [showActions, setShowActions] = useState(false)
  const [expandedWorkflow, setExpandedWorkflow] = useState<string | null>(null)

  const statusConfig = {
    [ProjectStatus.DRAFT]: { icon: Clock, color: 'gray', label: 'Draft' },
    [ProjectStatus.IN_PROGRESS]: { icon: Activity, color: 'blue', label: 'In Progress' },
    [ProjectStatus.PAUSED]: { icon: Pause, color: 'yellow', label: 'Paused' },
    [ProjectStatus.COMPLETED]: { icon: CheckCircle2, color: 'green', label: 'Completed' },
    [ProjectStatus.FAILED]: { icon: AlertCircle, color: 'red', label: 'Failed' },
    [ProjectStatus.CANCELLED]: { icon: AlertCircle, color: 'gray', label: 'Cancelled' },
  }

  const status = statusConfig[project.status]
  const StatusIcon = status.icon

  const handleExport = (format: 'json' | 'csv' | 'pdf') => {
    onExport?.(project.id, format)
    setShowActions(false)
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Eye },
    { id: 'workflows', label: 'Workflows', icon: Activity },
    { id: 'decisions', label: 'Audit Trail', icon: FileText },
    { id: 'results', label: 'Results', icon: BarChart3 },
  ]

  const workflowStats = {
    total: project.workflows?.length || 0,
    completed: project.workflows?.filter((w) => w.status === WorkflowStatus.COMPLETED).length || 0,
    inProgress: project.workflows?.filter((w) => w.status === WorkflowStatus.IN_PROGRESS).length || 0,
    failed: project.workflows?.filter((w) => w.status === WorkflowStatus.FAILED).length || 0,
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <motion.button
            onClick={onBack || (() => router.back())}
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4 transition-colors"
            whileHover={{ x: -4 }}
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Projects
          </motion.button>

          <div className="flex items-start gap-4">
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{project.title}</h1>
              {project.description && (
                <p className="text-gray-600 leading-relaxed">{project.description}</p>
              )}
            </div>

            <div className={`
              inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium
              bg-${status.color}-100 text-${status.color}-700
            `}>
              <StatusIcon className="w-4 h-4" />
              {status.label}
            </div>
          </div>

          <div className="flex items-center gap-6 mt-4 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              Created {formatDate(project.createdAt)}
            </div>
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4" />
              Updated {formatRelativeTime(project.updatedAt)}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          {onEdit && (
            <motion.button
              onClick={() => onEdit(project.id)}
              className="px-4 py-2 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-xl text-gray-700 font-medium hover:bg-white transition-all"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Edit className="w-5 h-5" />
            </motion.button>
          )}

          {project.status === ProjectStatus.IN_PROGRESS && onPause && (
            <motion.button
              onClick={() => onPause(project.id)}
              className="px-4 py-2 bg-yellow-100 text-yellow-700 rounded-xl font-medium hover:bg-yellow-200 transition-all"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Pause className="w-5 h-5" />
            </motion.button>
          )}

          {project.status === ProjectStatus.PAUSED && onResume && (
            <motion.button
              onClick={() => onResume(project.id)}
              className="px-4 py-2 bg-green-100 text-green-700 rounded-xl font-medium hover:bg-green-200 transition-all"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Play className="w-5 h-5" />
            </motion.button>
          )}

          <div className="relative">
            <motion.button
              onClick={() => setShowActions(!showActions)}
              className="px-4 py-2 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-xl text-gray-700 font-medium hover:bg-white transition-all"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <MoreVertical className="w-5 h-5" />
            </motion.button>

            <AnimatePresence>
              {showActions && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="absolute right-0 top-full mt-2 w-48 bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden z-50"
                >
                  {onClone && (
                    <button
                      onClick={() => {
                        onClone(project.id)
                        setShowActions(false)
                      }}
                      className="w-full px-4 py-3 text-left text-sm text-gray-700 hover:bg-gray-50 transition-colors flex items-center gap-3"
                    >
                      <Copy className="w-4 h-4" />
                      Clone Project
                    </button>
                  )}
                  <button
                    onClick={() => handleExport('json')}
                    className="w-full px-4 py-3 text-left text-sm text-gray-700 hover:bg-gray-50 transition-colors flex items-center gap-3"
                  >
                    <Download className="w-4 h-4" />
                    Export JSON
                  </button>
                  <button
                    onClick={() => handleExport('csv')}
                    className="w-full px-4 py-3 text-left text-sm text-gray-700 hover:bg-gray-50 transition-colors flex items-center gap-3"
                  >
                    <Download className="w-4 h-4" />
                    Export CSV
                  </button>
                  <button
                    onClick={() => handleExport('pdf')}
                    className="w-full px-4 py-3 text-left text-sm text-gray-700 hover:bg-gray-50 transition-colors flex items-center gap-3"
                  >
                    <Download className="w-4 h-4" />
                    Export PDF
                  </button>
                  {onDelete && (
                    <button
                      onClick={() => {
                        if (window.confirm('Are you sure you want to delete this project?')) {
                          onDelete(project.id)
                        }
                        setShowActions(false)
                      }}
                      className="w-full px-4 py-3 text-left text-sm text-red-600 hover:bg-red-50 transition-colors flex items-center gap-3 border-t border-gray-100"
                    >
                      <Trash2 className="w-4 h-4" />
                      Delete Project
                    </button>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-6 bg-gradient-to-br from-blue-500/10 to-blue-600/10 rounded-2xl border border-blue-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">Total Workflows</span>
            <Activity className="w-5 h-5 text-blue-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{workflowStats.total}</p>
        </div>

        <div className="p-6 bg-gradient-to-br from-green-500/10 to-green-600/10 rounded-2xl border border-green-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">Completed</span>
            <CheckCircle2 className="w-5 h-5 text-green-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{workflowStats.completed}</p>
        </div>

        <div className="p-6 bg-gradient-to-br from-yellow-500/10 to-yellow-600/10 rounded-2xl border border-yellow-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">In Progress</span>
            <Clock className="w-5 h-5 text-yellow-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{workflowStats.inProgress}</p>
        </div>

        <div className="p-6 bg-gradient-to-br from-purple-500/10 to-purple-600/10 rounded-2xl border border-purple-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">Decisions Made</span>
            <FileText className="w-5 h-5 text-purple-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{project.auditTrail?.length || 0}</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex gap-2">
          {tabs.map((tab) => {
            const TabIcon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`
                  relative px-6 py-3 font-medium transition-all
                  ${
                    activeTab === tab.id
                      ? 'text-primary-600'
                      : 'text-gray-600 hover:text-gray-900'
                  }
                `}
              >
                <span className="flex items-center gap-2">
                  <TabIcon className="w-4 h-4" />
                  {tab.label}
                </span>
                {activeTab === tab.id && (
                  <motion.div
                    layoutId="activeTab"
                    className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-600"
                    transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                  />
                )}
              </button>
            )
          })}
        </div>
      </div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
        >
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Workflow Visualizer */}
              <div className="p-6 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-2xl">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Workflow Progress</h3>
                <WorkflowVisualizer workflows={project.workflows || []} />
              </div>

              {/* Project Details */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="p-6 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-2xl">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Project Information</h3>
                  <dl className="space-y-3">
                    <div>
                      <dt className="text-sm font-medium text-gray-600">Tool Type</dt>
                      <dd className="text-base text-gray-900 mt-1">{project.toolType}</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-600">Created At</dt>
                      <dd className="text-base text-gray-900 mt-1">{formatDate(project.createdAt)}</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-600">Last Updated</dt>
                      <dd className="text-base text-gray-900 mt-1">{formatDate(project.updatedAt)}</dd>
                    </div>
                  </dl>
                </div>

                <div className="p-6 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-2xl">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Activity Summary</h3>
                  <dl className="space-y-3">
                    <div className="flex items-center justify-between">
                      <dt className="text-sm font-medium text-gray-600">Total Runtime</dt>
                      <dd className="text-base font-semibold text-gray-900">
                        {formatDuration(
                          project.workflows?.reduce((acc, w) => acc + (w.durationSeconds || 0), 0) || 0
                        )}
                      </dd>
                    </div>
                    <div className="flex items-center justify-between">
                      <dt className="text-sm font-medium text-gray-600">Success Rate</dt>
                      <dd className="text-base font-semibold text-gray-900">
                        {workflowStats.total > 0
                          ? Math.round((workflowStats.completed / workflowStats.total) * 100)
                          : 0}
                        %
                      </dd>
                    </div>
                    <div className="flex items-center justify-between">
                      <dt className="text-sm font-medium text-gray-600">Agent Decisions</dt>
                      <dd className="text-base font-semibold text-gray-900">
                        {project.auditTrail?.length || 0}
                      </dd>
                    </div>
                  </dl>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'workflows' && (
            <div className="space-y-4">
              {project.workflows && project.workflows.length > 0 ? (
                project.workflows.map((workflow, index) => (
                  <div
                    key={workflow.id}
                    className="p-6 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-2xl"
                  >
                    <AgentStatusCard
                      agentName={workflow.agentName}
                      agentRole={workflow.agentRole}
                      status={workflow.status as any}
                      currentTask={workflow.status === WorkflowStatus.IN_PROGRESS ? 'Processing...' : undefined}
                      progress={workflow.progress || 0}
                      message={workflow.errorMessage}
                    />
                    {workflow.decisions && workflow.decisions.length > 0 && (
                      <div className="mt-4 pt-4 border-t border-gray-200">
                        <button
                          onClick={() =>
                            setExpandedWorkflow(expandedWorkflow === workflow.id ? null : workflow.id)
                          }
                          className="text-sm font-medium text-primary-600 hover:text-primary-700"
                        >
                          {expandedWorkflow === workflow.id ? 'Hide' : 'Show'} {workflow.decisions.length}{' '}
                          decisions
                        </button>
                        {expandedWorkflow === workflow.id && (
                          <div className="mt-4 space-y-3">
                            {workflow.decisions.map((decision, idx) => (
                              <div
                                key={idx}
                                className="p-4 bg-gray-50 rounded-lg text-sm"
                              >
                                <div className="font-medium text-gray-900 mb-1">{decision.decision}</div>
                                <div className="text-gray-600">{decision.reasoning}</div>
                                <div className="mt-2 text-xs text-gray-500">
                                  Confidence: {Math.round(decision.confidence * 100)}%
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="p-12 text-center text-gray-600">
                  <Activity className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                  <p>No workflows available</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'decisions' && (
            <div className="space-y-4">
              {project.auditTrail && project.auditTrail.length > 0 ? (
                project.auditTrail.map((decision, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="p-6 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-2xl"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h4 className="font-semibold text-gray-900">{decision.agentName}</h4>
                        <p className="text-sm text-gray-600">{decision.agentRole}</p>
                      </div>
                      <Badge variant="default" size="sm">
                        {Math.round(decision.confidence * 100)}% confidence
                      </Badge>
                    </div>
                    <div className="mb-3">
                      <div className="font-medium text-gray-900 mb-1">Decision</div>
                      <div className="text-gray-700">{decision.decision}</div>
                    </div>
                    <div className="mb-3">
                      <div className="font-medium text-gray-900 mb-1">Reasoning</div>
                      <div className="text-gray-700 leading-relaxed">{decision.reasoning}</div>
                    </div>
                    <div className="text-xs text-gray-500">
                      {formatDate(decision.timestamp)}
                    </div>
                  </motion.div>
                ))
              ) : (
                <div className="p-12 text-center text-gray-600">
                  <FileText className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                  <p>No decisions recorded yet</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'results' && (
            <div className="p-12 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-2xl text-center">
              <BarChart3 className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Results Available Soon</h3>
              <p className="text-gray-600">
                Results will be displayed here once the project is completed
              </p>
            </div>
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  )
}

export default ProjectDetailView
