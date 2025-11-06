import React from 'react'
import { motion } from 'framer-motion'
import Layout from '@/components/layout/Layout'
import ProjectCard from '@/components/dashboard/ProjectCard'
import { useAppStore } from '@/stores/useAppStore'
import { ToolType, ProjectStatus } from '../../../lib/types'
import {
  Microscope,
  Plus,
  ArrowRight,
  Search,
  Filter,
  Award,
  FileText,
  BarChart3,
  FileDown,
  Sparkles,
  TrendingUp,
  Clock
} from 'lucide-react'
import { useRouter } from 'next/router'

const MetaAnalysisIndexPage: React.FC = () => {
  const router = useRouter()
  const { projects } = useAppStore()

  // Filter projects for this tool type
  const metaAnalysisProjects = projects.filter(
    p => p.toolType === ToolType.META_ANALYSIS
  )

  const recentProjects = metaAnalysisProjects
    .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
    .slice(0, 6)

  const stats = {
    total: metaAnalysisProjects.length,
    active: metaAnalysisProjects.filter(p => p.status === ProjectStatus.IN_PROGRESS).length,
    completed: metaAnalysisProjects.filter(p => p.status === ProjectStatus.COMPLETED).length
  }

  const features = [
    {
      icon: Search,
      title: 'Intelligent Search',
      description: 'AI-powered multi-database search across PubMed, Scopus, Web of Science, and more'
    },
    {
      icon: Filter,
      title: 'Smart Screening',
      description: 'Automated screening with inclusion/exclusion criteria and confidence scoring'
    },
    {
      icon: Award,
      title: 'Quality Assessment',
      description: 'Comprehensive quality and credibility evaluation of each study'
    },
    {
      icon: FileText,
      title: 'Data Extraction',
      description: 'Automated extraction of effect sizes, statistics, and key findings'
    },
    {
      icon: BarChart3,
      title: 'Statistical Analysis',
      description: 'Publication-ready meta-analysis with forest plots and funnel plots'
    },
    {
      icon: FileDown,
      title: 'PRISMA Report',
      description: 'Complete PRISMA-compliant systematic review report generation'
    }
  ]

  return (
    <Layout title="Meta-Analysis">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Hero Section */}
        <motion.div
          className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-blue-600 via-blue-700 to-primary-800 p-8 md:p-12 text-white"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        >
          {/* Animated background elements */}
          <motion.div
            className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl"
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.3, 0.5, 0.3]
            }}
            transition={{
              duration: 8,
              repeat: Infinity,
              ease: 'easeInOut'
            }}
          />
          <motion.div
            className="absolute bottom-0 left-0 w-96 h-96 bg-primary-400/20 rounded-full blur-3xl"
            animate={{
              scale: [1, 1.3, 1],
              opacity: [0.2, 0.4, 0.2]
            }}
            transition={{
              duration: 10,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: 1
            }}
          />

          <div className="relative z-10">
            <div className="flex items-start justify-between flex-wrap gap-6">
              <div className="flex-1 min-w-0">
                <motion.div
                  className="inline-flex items-center gap-3 mb-4"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.6, delay: 0.2 }}
                >
                  <div className="p-3 rounded-2xl bg-white/20 backdrop-blur-sm">
                    <Microscope className="w-8 h-8" />
                  </div>
                  <div>
                    <h1 className="text-4xl md:text-5xl font-bold">
                      Meta-Analysis
                    </h1>
                    <div className="flex items-center gap-2 mt-1">
                      <Sparkles className="w-4 h-4 text-blue-200" />
                      <span className="text-sm text-blue-100 font-medium">
                        AI-Powered Systematic Reviews
                      </span>
                    </div>
                  </div>
                </motion.div>

                <motion.p
                  className="text-lg text-blue-100 max-w-2xl leading-relaxed mb-6"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.4 }}
                >
                  Transform months of systematic review work into hours with 9 specialized AI agents.
                  From literature search to publication-ready PRISMA reports, complete your meta-analysis
                  with unprecedented speed and rigor.
                </motion.p>

                {/* Stats */}
                <motion.div
                  className="flex flex-wrap gap-6"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.5 }}
                >
                  <div className="flex items-center gap-2">
                    <div className="p-2 rounded-lg bg-white/20 backdrop-blur-sm">
                      <TrendingUp className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-2xl font-bold">{stats.total}</div>
                      <div className="text-xs text-blue-200">Total Projects</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="p-2 rounded-lg bg-white/20 backdrop-blur-sm">
                      <Clock className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-2xl font-bold">{stats.active}</div>
                      <div className="text-xs text-blue-200">In Progress</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="p-2 rounded-lg bg-white/20 backdrop-blur-sm">
                      <Award className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-2xl font-bold">{stats.completed}</div>
                      <div className="text-xs text-blue-200">Completed</div>
                    </div>
                  </div>
                </motion.div>
              </div>

              {/* CTA Button */}
              <motion.button
                className="group px-8 py-4 bg-white text-primary-600 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-300"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: 0.6 }}
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => router.push('/tools/meta-analysis/new')}
              >
                <span className="flex items-center gap-2">
                  <Plus className="w-5 h-5" />
                  Start New Meta-Analysis
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </span>
              </motion.button>
            </div>
          </div>
        </motion.div>

        {/* Features Grid */}
        <div>
          <motion.div
            className="mb-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.2 }}
          >
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              How It Works
            </h2>
            <p className="text-gray-600">
              6 specialized AI agents working in sequence to deliver comprehensive systematic reviews
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                className="group p-6 rounded-2xl bg-white/60 backdrop-blur-sm border border-gray-200 hover:border-blue-300 shadow-soft hover:shadow-lg transition-all duration-300"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.3 + index * 0.1 }}
                whileHover={{ y: -4 }}
              >
                <div className="flex items-start gap-4">
                  <motion.div
                    className="p-3 rounded-xl bg-blue-100 text-blue-600 shadow-sm flex-shrink-0"
                    whileHover={{ scale: 1.1, rotate: 5 }}
                    transition={{ type: 'spring', stiffness: 400, damping: 10 }}
                  >
                    <feature.icon className="w-6 h-6" />
                  </motion.div>

                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
                      {feature.title}
                    </h3>
                    <p className="text-sm text-gray-600 leading-relaxed">
                      {feature.description}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Recent Projects */}
        <div>
          <motion.div
            className="flex items-center justify-between mb-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.8 }}
          >
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-1">
                Recent Projects
              </h2>
              <p className="text-gray-600">
                Your latest meta-analysis systematic reviews
              </p>
            </div>
            {recentProjects.length > 0 && (
              <button
                className="group flex items-center gap-2 text-sm font-medium text-primary-600 hover:text-primary-700 transition-colors"
                onClick={() => router.push('/projects?tool=meta-analysis')}
              >
                View All
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </button>
            )}
          </motion.div>

          {recentProjects.length === 0 ? (
            <motion.div
              className="p-12 rounded-2xl bg-white/60 backdrop-blur-sm border border-gray-200 text-center"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.9 }}
            >
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-blue-100 text-blue-600 mb-4">
                <Microscope className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                No meta-analysis projects yet
              </h3>
              <p className="text-gray-600 mb-6 max-w-md mx-auto">
                Start your first AI-powered systematic review and transform months of work into hours
              </p>
              <motion.button
                className="px-6 py-3 bg-primary-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-glow-primary transition-all duration-300"
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => router.push('/tools/meta-analysis/new')}
              >
                <span className="flex items-center gap-2">
                  <Plus className="w-5 h-5" />
                  Create Your First Meta-Analysis
                </span>
              </motion.button>
            </motion.div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {recentProjects.map((project, index) => (
                <ProjectCard
                  key={project.id}
                  id={project.id}
                  title={project.title}
                  description={project.description}
                  status={project.status}
                  toolType={project.toolType}
                  icon={Microscope}
                  color="blue"
                  updatedAt={project.updatedAt.toString()}
                  progress={45}
                  index={index}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}

export default MetaAnalysisIndexPage
