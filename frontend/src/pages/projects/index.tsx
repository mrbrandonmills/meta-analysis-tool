import React, { useState, useEffect, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Layout from '@/components/layout/Layout'
import ProjectCard from '@/components/dashboard/ProjectCard'
import { useAppStore } from '@/stores/useAppStore'
import { projectsApi } from '@/lib/api'
import { ToolType, ProjectStatus, Project } from '@/lib/types'
import {
  Search,
  Filter,
  SlidersHorizontal,
  Grid3x3,
  List,
  ArrowUpDown,
  Microscope,
  Users,
  FileText,
  Lightbulb,
  Plus,
  X,
  Calendar,
  CheckCircle2,
  Clock,
  AlertCircle,
  Pause,
  Loader2
} from 'lucide-react'
import { useRouter } from 'next/router'
import toast from 'react-hot-toast'

// Tool configuration
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

const statusLabels = {
  [ProjectStatus.DRAFT]: 'Draft',
  [ProjectStatus.IN_PROGRESS]: 'In Progress',
  [ProjectStatus.PAUSED]: 'Paused',
  [ProjectStatus.COMPLETED]: 'Completed',
  [ProjectStatus.FAILED]: 'Failed',
  [ProjectStatus.CANCELLED]: 'Cancelled'
}

const statusIcons = {
  [ProjectStatus.DRAFT]: Clock,
  [ProjectStatus.IN_PROGRESS]: Clock,
  [ProjectStatus.PAUSED]: Pause,
  [ProjectStatus.COMPLETED]: CheckCircle2,
  [ProjectStatus.FAILED]: AlertCircle,
  [ProjectStatus.CANCELLED]: X
}

type ViewMode = 'grid' | 'list'
type SortOption = 'updated' | 'created' | 'title' | 'status'
type SortDirection = 'asc' | 'desc'

const ProjectsPage: React.FC = () => {
  const router = useRouter()
  const { projects, setProjects } = useAppStore()

  // UI State
  const [viewMode, setViewMode] = useState<ViewMode>('grid')
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState<SortOption>('updated')
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc')
  const [showFilters, setShowFilters] = useState(false)
  const [loading, setLoading] = useState(true)

  // Filter State
  const [selectedTools, setSelectedTools] = useState<ToolType[]>([])
  const [selectedStatuses, setSelectedStatuses] = useState<ProjectStatus[]>([])
  const [dateRange, setDateRange] = useState<'all' | 'today' | 'week' | 'month' | 'year'>('all')

  // Fetch projects on mount
  useEffect(() => {
    fetchProjects()
  }, [])

  const fetchProjects = async () => {
    try {
      setLoading(true)
      const data = await projectsApi.list()
      setProjects(data)
    } catch (error) {
      console.error('Failed to fetch projects:', error)
      toast.error('Failed to load projects')
    } finally {
      setLoading(false)
    }
  }

  // Filter and sort projects
  const filteredAndSortedProjects = useMemo(() => {
    let filtered = [...projects]

    // Apply search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(
        p =>
          p.title.toLowerCase().includes(query) ||
          p.description?.toLowerCase().includes(query)
      )
    }

    // Apply tool type filter
    if (selectedTools.length > 0) {
      filtered = filtered.filter(p => selectedTools.includes(p.toolType as ToolType))
    }

    // Apply status filter
    if (selectedStatuses.length > 0) {
      filtered = filtered.filter(p => selectedStatuses.includes(p.status))
    }

    // Apply date range filter
    if (dateRange !== 'all') {
      const now = new Date()
      const filterDate = new Date()

      switch (dateRange) {
        case 'today':
          filterDate.setHours(0, 0, 0, 0)
          break
        case 'week':
          filterDate.setDate(now.getDate() - 7)
          break
        case 'month':
          filterDate.setMonth(now.getMonth() - 1)
          break
        case 'year':
          filterDate.setFullYear(now.getFullYear() - 1)
          break
      }

      filtered = filtered.filter(p => new Date(p.updatedAt) >= filterDate)
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let comparison = 0

      switch (sortBy) {
        case 'updated':
          comparison = new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
          break
        case 'created':
          comparison = new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
          break
        case 'title':
          comparison = a.title.localeCompare(b.title)
          break
        case 'status':
          comparison = a.status.localeCompare(b.status)
          break
      }

      return sortDirection === 'asc' ? comparison : -comparison
    })

    return filtered
  }, [projects, searchQuery, selectedTools, selectedStatuses, dateRange, sortBy, sortDirection])

  // Toggle filter selections
  const toggleToolFilter = (tool: ToolType) => {
    setSelectedTools(prev =>
      prev.includes(tool) ? prev.filter(t => t !== tool) : [...prev, tool]
    )
  }

  const toggleStatusFilter = (status: ProjectStatus) => {
    setSelectedStatuses(prev =>
      prev.includes(status) ? prev.filter(s => s !== status) : [...prev, status]
    )
  }

  const clearFilters = () => {
    setSelectedTools([])
    setSelectedStatuses([])
    setDateRange('all')
    setSearchQuery('')
  }

  const activeFilterCount = selectedTools.length + selectedStatuses.length + (dateRange !== 'all' ? 1 : 0)

  // Calculate statistics
  const stats = {
    total: projects.length,
    active: projects.filter(p => p.status === ProjectStatus.IN_PROGRESS).length,
    completed: projects.filter(p => p.status === ProjectStatus.COMPLETED).length,
    filtered: filteredAndSortedProjects.length
  }

  return (
    <Layout title="Projects">
      <div className="space-y-6">
        {/* Header */}
        <motion.div
          className="flex items-center justify-between flex-wrap gap-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Projects</h1>
            <p className="text-gray-600">
              Manage and track all your research projects
              {stats.filtered !== stats.total && (
                <span className="ml-2 text-primary-600 font-medium">
                  ({stats.filtered} of {stats.total})
                </span>
              )}
            </p>
          </div>

          <motion.button
            className="px-6 py-3 bg-primary-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-glow-primary transition-all duration-300 flex items-center gap-2"
            whileHover={{ scale: 1.05, y: -2 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => router.push('/dashboard')} // TODO: Update when tool creation pages are ready
          >
            <Plus className="w-5 h-5" />
            New Project
          </motion.button>
        </motion.div>

        {/* Stats Bar */}
        <motion.div
          className="grid grid-cols-1 sm:grid-cols-3 gap-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <div className="p-4 rounded-xl bg-white/60 backdrop-blur-sm border border-gray-200">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-blue-100">
                <Grid3x3 className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Total Projects</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              </div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-white/60 backdrop-blur-sm border border-gray-200">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-yellow-100">
                <Clock className="w-5 h-5 text-yellow-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">In Progress</p>
                <p className="text-2xl font-bold text-gray-900">{stats.active}</p>
              </div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-white/60 backdrop-blur-sm border border-gray-200">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-green-100">
                <CheckCircle2 className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Completed</p>
                <p className="text-2xl font-bold text-gray-900">{stats.completed}</p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Search and Filters */}
        <motion.div
          className="space-y-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.2 }}
        >
          {/* Search Bar and Controls */}
          <div className="flex items-center gap-3 flex-wrap">
            {/* Search Input */}
            <div className="flex-1 min-w-[250px] relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search projects..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-4 py-3 rounded-xl border border-gray-200 bg-white/60 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  <X className="w-5 h-5" />
                </button>
              )}
            </div>

            {/* Filter Toggle */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`px-4 py-3 rounded-xl border font-medium transition-all flex items-center gap-2 ${
                showFilters
                  ? 'bg-primary-50 border-primary-300 text-primary-700'
                  : 'bg-white/60 backdrop-blur-sm border-gray-200 text-gray-700 hover:border-gray-300'
              }`}
            >
              <Filter className="w-5 h-5" />
              Filters
              {activeFilterCount > 0 && (
                <span className="px-2 py-0.5 rounded-full bg-primary-600 text-white text-xs font-semibold">
                  {activeFilterCount}
                </span>
              )}
            </button>

            {/* Sort */}
            <div className="flex items-center gap-2">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as SortOption)}
                className="px-4 py-3 rounded-xl border border-gray-200 bg-white/60 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all cursor-pointer"
              >
                <option value="updated">Last Updated</option>
                <option value="created">Date Created</option>
                <option value="title">Title</option>
                <option value="status">Status</option>
              </select>

              <button
                onClick={() => setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc')}
                className="p-3 rounded-xl border border-gray-200 bg-white/60 backdrop-blur-sm hover:border-gray-300 transition-all"
                title={sortDirection === 'asc' ? 'Ascending' : 'Descending'}
              >
                <ArrowUpDown className={`w-5 h-5 text-gray-700 transition-transform ${sortDirection === 'desc' ? 'rotate-180' : ''}`} />
              </button>
            </div>

            {/* View Mode Toggle */}
            <div className="flex items-center gap-1 p-1 rounded-xl border border-gray-200 bg-white/60 backdrop-blur-sm">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded-lg transition-all ${
                  viewMode === 'grid'
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
                title="Grid View"
              >
                <Grid3x3 className="w-5 h-5" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-lg transition-all ${
                  viewMode === 'list'
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
                title="List View"
              >
                <List className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Filter Panel */}
          <AnimatePresence>
            {showFilters && (
              <motion.div
                className="p-6 rounded-2xl bg-white/60 backdrop-blur-sm border border-gray-200"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.3 }}
              >
                <div className="space-y-6">
                  {/* Tool Type Filter */}
                  <div>
                    <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      <SlidersHorizontal className="w-4 h-4" />
                      Tool Type
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(toolLabels).map(([key, label]) => {
                        const tool = key as ToolType
                        const Icon = toolIcons[tool]
                        const color = toolColors[tool]
                        const isSelected = selectedTools.includes(tool)

                        return (
                          <button
                            key={tool}
                            onClick={() => toggleToolFilter(tool)}
                            className={`px-4 py-2 rounded-lg border font-medium transition-all flex items-center gap-2 ${
                              isSelected
                                ? `bg-${color}-100 border-${color}-300 text-${color}-700`
                                : 'bg-white border-gray-200 text-gray-700 hover:border-gray-300'
                            }`}
                          >
                            <Icon className="w-4 h-4" />
                            {label}
                          </button>
                        )
                      })}
                    </div>
                  </div>

                  {/* Status Filter */}
                  <div>
                    <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4" />
                      Status
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(statusLabels).map(([key, label]) => {
                        const status = key as ProjectStatus
                        const Icon = statusIcons[status]
                        const isSelected = selectedStatuses.includes(status)

                        return (
                          <button
                            key={status}
                            onClick={() => toggleStatusFilter(status)}
                            className={`px-4 py-2 rounded-lg border font-medium transition-all flex items-center gap-2 ${
                              isSelected
                                ? 'bg-primary-100 border-primary-300 text-primary-700'
                                : 'bg-white border-gray-200 text-gray-700 hover:border-gray-300'
                            }`}
                          >
                            <Icon className="w-4 h-4" />
                            {label}
                          </button>
                        )
                      })}
                    </div>
                  </div>

                  {/* Date Range Filter */}
                  <div>
                    <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      Date Range
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {[
                        { value: 'all', label: 'All Time' },
                        { value: 'today', label: 'Today' },
                        { value: 'week', label: 'This Week' },
                        { value: 'month', label: 'This Month' },
                        { value: 'year', label: 'This Year' }
                      ].map(option => (
                        <button
                          key={option.value}
                          onClick={() => setDateRange(option.value as typeof dateRange)}
                          className={`px-4 py-2 rounded-lg border font-medium transition-all ${
                            dateRange === option.value
                              ? 'bg-primary-100 border-primary-300 text-primary-700'
                              : 'bg-white border-gray-200 text-gray-700 hover:border-gray-300'
                          }`}
                        >
                          {option.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Clear Filters */}
                  {activeFilterCount > 0 && (
                    <div className="pt-4 border-t border-gray-200">
                      <button
                        onClick={clearFilters}
                        className="px-4 py-2 rounded-lg border border-gray-300 text-gray-700 font-medium hover:bg-gray-50 transition-all flex items-center gap-2"
                      >
                        <X className="w-4 h-4" />
                        Clear All Filters
                      </button>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Projects Grid/List */}
        {loading ? (
          <motion.div
            className="flex items-center justify-center py-20"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <Loader2 className="w-8 h-8 text-primary-600 animate-spin" />
          </motion.div>
        ) : filteredAndSortedProjects.length === 0 ? (
          <motion.div
            className="p-12 rounded-2xl bg-white/60 backdrop-blur-sm border border-gray-200 text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.3 }}
          >
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gray-100 text-gray-400 mb-4">
              <Microscope className="w-8 h-8" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {searchQuery || activeFilterCount > 0 ? 'No projects found' : 'No projects yet'}
            </h3>
            <p className="text-gray-600 mb-6">
              {searchQuery || activeFilterCount > 0
                ? 'Try adjusting your search or filters'
                : 'Get started by creating your first research project'}
            </p>
            {searchQuery || activeFilterCount > 0 ? (
              <button
                onClick={clearFilters}
                className="px-6 py-3 bg-white border border-gray-300 text-gray-700 rounded-xl font-semibold hover:bg-gray-50 transition-all"
              >
                Clear Filters
              </button>
            ) : (
              <motion.button
                className="px-6 py-3 bg-primary-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-glow-primary transition-all duration-300"
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => router.push('/dashboard')}
              >
                <span className="flex items-center gap-2">
                  <Plus className="w-5 h-5" />
                  Create Your First Project
                </span>
              </motion.button>
            )}
          </motion.div>
        ) : (
          <motion.div
            className={
              viewMode === 'grid'
                ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
                : 'space-y-4'
            }
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.4, delay: 0.3 }}
          >
            {filteredAndSortedProjects.map((project, index) => (
              <ProjectCard
                key={project.id}
                id={project.id}
                title={project.title}
                description={project.description}
                status={project.status}
                toolType={project.toolType}
                icon={toolIcons[project.toolType as ToolType]}
                color={toolColors[project.toolType as ToolType]}
                updatedAt={project.updatedAt.toString()}
                progress={project.status === ProjectStatus.IN_PROGRESS ? 45 : 0}
                index={index}
              />
            ))}
          </motion.div>
        )}
      </div>
    </Layout>
  )
}

export default ProjectsPage
