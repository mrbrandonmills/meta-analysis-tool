'use client'

import React, { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useRouter } from 'next/router'
import {
  Search,
  Filter,
  SlidersHorizontal,
  X,
  ChevronDown,
  Calendar,
  RefreshCw,
  Download,
  Trash2,
  Copy,
  Play,
  Pause,
  MoreVertical,
} from 'lucide-react'
import { Project, ProjectStatus, ToolType } from '@/lib/types'
import ProjectCard from './ProjectCard'
import { formatDate } from '@/lib/utils'

interface ProjectsListProps {
  projects: Project[]
  loading?: boolean
  onRefresh?: () => void
  onDelete?: (projectId: string) => void
  onClone?: (projectId: string) => void
  onPause?: (projectId: string) => void
  onResume?: (projectId: string) => void
  onExport?: (projectId: string) => void
}

interface FilterState {
  status: ProjectStatus[]
  toolType: ToolType[]
  dateFrom?: Date
  dateTo?: Date
}

const statusOptions = [
  { value: ProjectStatus.DRAFT, label: 'Draft', color: 'gray' },
  { value: ProjectStatus.IN_PROGRESS, label: 'In Progress', color: 'blue' },
  { value: ProjectStatus.PAUSED, label: 'Paused', color: 'yellow' },
  { value: ProjectStatus.COMPLETED, label: 'Completed', color: 'green' },
  { value: ProjectStatus.FAILED, label: 'Failed', color: 'red' },
  { value: ProjectStatus.CANCELLED, label: 'Cancelled', color: 'gray' },
]

const toolTypeOptions = [
  { value: ToolType.META_ANALYSIS, label: 'Meta-Analysis', color: 'blue' },
  { value: ToolType.REVIEWER_MATCHER, label: 'Reviewer Matcher', color: 'green' },
  { value: ToolType.PEER_REVIEW, label: 'Peer Review', color: 'purple' },
  { value: ToolType.RESEARCH_DIRECTION, label: 'Research Direction', color: 'yellow' },
]

const sortOptions = [
  { value: 'updatedAt-desc', label: 'Recently Updated' },
  { value: 'updatedAt-asc', label: 'Oldest Updated' },
  { value: 'createdAt-desc', label: 'Recently Created' },
  { value: 'createdAt-asc', label: 'Oldest Created' },
  { value: 'title-asc', label: 'Title (A-Z)' },
  { value: 'title-desc', label: 'Title (Z-A)' },
]

const ProjectsList: React.FC<ProjectsListProps> = ({
  projects,
  loading = false,
  onRefresh,
  onDelete,
  onClone,
  onPause,
  onResume,
  onExport,
}) => {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const [sortBy, setSortBy] = useState('updatedAt-desc')
  const [filters, setFilters] = useState<FilterState>({
    status: [],
    toolType: [],
  })

  // Filter and sort projects
  const filteredProjects = useMemo(() => {
    let filtered = [...projects]

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(
        (project) =>
          project.title.toLowerCase().includes(query) ||
          project.description?.toLowerCase().includes(query)
      )
    }

    // Status filter
    if (filters.status.length > 0) {
      filtered = filtered.filter((project) => filters.status.includes(project.status))
    }

    // Tool type filter
    if (filters.toolType.length > 0) {
      filtered = filtered.filter((project) => filters.toolType.includes(project.toolType as ToolType))
    }

    // Date range filter
    if (filters.dateFrom) {
      filtered = filtered.filter(
        (project) => new Date(project.createdAt) >= filters.dateFrom!
      )
    }
    if (filters.dateTo) {
      filtered = filtered.filter(
        (project) => new Date(project.createdAt) <= filters.dateTo!
      )
    }

    // Sort
    const [sortField, sortOrder] = sortBy.split('-')
    filtered.sort((a, b) => {
      let aVal: any = a[sortField as keyof Project]
      let bVal: any = b[sortField as keyof Project]

      if (sortField === 'updatedAt' || sortField === 'createdAt') {
        aVal = new Date(aVal).getTime()
        bVal = new Date(bVal).getTime()
      } else if (sortField === 'title') {
        aVal = aVal.toLowerCase()
        bVal = bVal.toLowerCase()
      }

      if (sortOrder === 'asc') {
        return aVal > bVal ? 1 : -1
      } else {
        return aVal < bVal ? 1 : -1
      }
    })

    return filtered
  }, [projects, searchQuery, filters, sortBy])

  const toggleStatusFilter = (status: ProjectStatus) => {
    setFilters((prev) => ({
      ...prev,
      status: prev.status.includes(status)
        ? prev.status.filter((s) => s !== status)
        : [...prev.status, status],
    }))
  }

  const toggleToolTypeFilter = (toolType: ToolType) => {
    setFilters((prev) => ({
      ...prev,
      toolType: prev.toolType.includes(toolType)
        ? prev.toolType.filter((t) => t !== toolType)
        : [...prev.toolType, toolType],
    }))
  }

  const clearFilters = () => {
    setFilters({
      status: [],
      toolType: [],
    })
    setSearchQuery('')
  }

  const activeFilterCount =
    filters.status.length +
    filters.toolType.length +
    (filters.dateFrom ? 1 : 0) +
    (filters.dateTo ? 1 : 0)

  const toolIcons = {
    [ToolType.META_ANALYSIS]: '🔬',
    [ToolType.REVIEWER_MATCHER]: '👥',
    [ToolType.PEER_REVIEW]: '📄',
    [ToolType.RESEARCH_DIRECTION]: '💡',
  }

  return (
    <div className="space-y-6">
      {/* Search and Filter Bar */}
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Search */}
        <div className="flex-1 relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search projects..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-12 pr-4 py-3 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              aria-label="Clear search"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Filter Toggle */}
        <motion.button
          onClick={() => setShowFilters(!showFilters)}
          className={`
            relative px-6 py-3 rounded-xl font-medium transition-all duration-300
            ${
              showFilters
                ? 'bg-primary-600 text-white shadow-lg'
                : 'bg-white/60 backdrop-blur-sm border border-gray-200 text-gray-700 hover:bg-white'
            }
          `}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <span className="flex items-center gap-2">
            <SlidersHorizontal className="w-5 h-5" />
            Filters
            {activeFilterCount > 0 && (
              <span className="ml-1 px-2 py-0.5 bg-white/20 rounded-full text-xs font-bold">
                {activeFilterCount}
              </span>
            )}
          </span>
        </motion.button>

        {/* Sort Dropdown */}
        <div className="relative">
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="appearance-none px-6 py-3 pr-10 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-xl text-gray-700 font-medium focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all cursor-pointer"
          >
            {sortOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
        </div>

        {/* Refresh Button */}
        {onRefresh && (
          <motion.button
            onClick={onRefresh}
            className="px-6 py-3 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-xl text-gray-700 font-medium hover:bg-white transition-all"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98, rotate: 180 }}
            disabled={loading}
          >
            <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
          </motion.button>
        )}
      </div>

      {/* Filter Panel */}
      <AnimatePresence>
        {showFilters && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="p-6 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-xl space-y-6">
              {/* Status Filters */}
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Status</h3>
                <div className="flex flex-wrap gap-2">
                  {statusOptions.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => toggleStatusFilter(option.value)}
                      className={`
                        px-4 py-2 rounded-lg text-sm font-medium transition-all
                        ${
                          filters.status.includes(option.value)
                            ? `bg-${option.color}-100 text-${option.color}-700 border-2 border-${option.color}-300`
                            : 'bg-gray-50 text-gray-600 border border-gray-200 hover:bg-gray-100'
                        }
                      `}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Tool Type Filters */}
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Tool Type</h3>
                <div className="flex flex-wrap gap-2">
                  {toolTypeOptions.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => toggleToolTypeFilter(option.value)}
                      role="button"
                      aria-label={option.label}
                      className={`
                        px-4 py-2 rounded-lg text-sm font-medium transition-all
                        ${
                          filters.toolType.includes(option.value)
                            ? `bg-${option.color}-100 text-${option.color}-700 border-2 border-${option.color}-300`
                            : 'bg-gray-50 text-gray-600 border border-gray-200 hover:bg-gray-100'
                        }
                      `}
                    >
                      {toolIcons[option.value]} {option.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Clear Filters */}
              {activeFilterCount > 0 && (
                <div className="flex justify-end">
                  <button
                    onClick={clearFilters}
                    className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
                  >
                    Clear all filters
                  </button>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Results Summary */}
      <div className="flex items-center justify-between text-sm text-gray-600">
        <span>
          Showing {filteredProjects.length} of {projects.length} projects
        </span>
        {activeFilterCount > 0 && (
          <span className="text-primary-600 font-medium">
            {activeFilterCount} filter{activeFilterCount !== 1 ? 's' : ''} active
          </span>
        )}
      </div>

      {/* Projects Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              className="h-64 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-2xl animate-pulse"
            />
          ))}
        </div>
      ) : filteredProjects.length === 0 ? (
        <motion.div
          className="p-12 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-2xl text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gray-100 text-gray-400 mb-4">
            <Search className="w-8 h-8" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No projects found</h3>
          <p className="text-gray-600 mb-6">
            {searchQuery || activeFilterCount > 0
              ? 'Try adjusting your search or filters'
              : 'Get started by creating your first project'}
          </p>
          {(searchQuery || activeFilterCount > 0) && (
            <button
              onClick={clearFilters}
              className="px-6 py-3 bg-primary-600 text-white rounded-xl font-semibold hover:bg-primary-700 transition-colors"
            >
              Clear filters
            </button>
          )}
        </motion.div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map((project, index) => (
            <ProjectCard
              key={project.id}
              id={project.id}
              title={project.title}
              description={project.description}
              status={project.status}
              toolType={project.toolType}
              icon={toolIcons[project.toolType as ToolType] as any}
              color={toolTypeOptions.find((t) => t.value === project.toolType)?.color || 'gray'}
              updatedAt={project.updatedAt.toString()}
              progress={project.workflows?.[0]?.progress || 0}
              index={index}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default ProjectsList
