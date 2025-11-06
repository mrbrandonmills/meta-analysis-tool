import React from 'react'
import { motion } from 'framer-motion'
import Layout from '@/components/layout/Layout'
import ProjectCard from '@/components/dashboard/ProjectCard'
import { useAppStore } from '@/stores/useAppStore'
import { ToolType, ProjectStatus } from '../../../lib/types'
import {
  Lightbulb,
  Plus,
  ArrowRight,
  Compass,
  TrendingUp,
  Target,
  Sparkles,
  Clock,
  Award,
  Zap,
  Search,
  Brain,
  BarChart3
} from 'lucide-react'
import { useRouter } from 'next/router'

const ResearchDirectionIndexPage: React.FC = () => {
  const router = useRouter()
  const { projects } = useAppStore()

  // Filter projects for this tool type
  const researchDirectionProjects = projects.filter(
    p => p.toolType === ToolType.RESEARCH_DIRECTION
  )

  const recentProjects = researchDirectionProjects
    .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
    .slice(0, 6)

  const stats = {
    total: researchDirectionProjects.length,
    active: researchDirectionProjects.filter(p => p.status === ProjectStatus.IN_PROGRESS).length,
    completed: researchDirectionProjects.filter(p => p.status === ProjectStatus.COMPLETED).length
  }

  const features = [
    {
      icon: Search,
      title: 'Gap Discovery',
      description: 'AI-powered identification of unexplored research opportunities in your field'
    },
    {
      icon: TrendingUp,
      title: 'Trend Analysis',
      description: 'Track emerging topics, methodologies, and research trajectories in real-time'
    },
    {
      icon: Brain,
      title: 'Cross-Domain Insights',
      description: 'Discover methodological innovations from adjacent fields applicable to your work'
    },
    {
      icon: Target,
      title: 'Impact Prediction',
      description: 'Forecast potential impact and citation metrics for proposed research directions'
    },
    {
      icon: Zap,
      title: 'Novel Proposals',
      description: 'AI-generated research proposals combining gap analysis with methodological innovation'
    },
    {
      icon: BarChart3,
      title: 'Feasibility Analysis',
      description: 'Comprehensive evaluation of research feasibility, resources, and timeline'
    }
  ]

  return (
    <Layout title="Research Direction">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Hero Section */}
        <motion.div
          className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-yellow-500 via-amber-600 to-orange-700 p-8 md:p-12 text-white"
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
            className="absolute bottom-0 left-0 w-96 h-96 bg-orange-400/20 rounded-full blur-3xl"
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
                    <Lightbulb className="w-8 h-8" />
                  </div>
                  <div>
                    <h1 className="text-4xl md:text-5xl font-bold">
                      Research Direction
                    </h1>
                    <div className="flex items-center gap-2 mt-1">
                      <Sparkles className="w-4 h-4 text-yellow-200" />
                      <span className="text-sm text-yellow-100 font-medium">
                        AI-Powered Research Discovery
                      </span>
                    </div>
                  </div>
                </motion.div>

                <motion.p
                  className="text-lg text-yellow-100 max-w-2xl leading-relaxed mb-6"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.4 }}
                >
                  Discover your next breakthrough research direction. Our AI analyzes your publication
                  history, identifies gaps in the literature, tracks emerging trends, and generates
                  novel research proposals with predicted impact scores.
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
                      <Compass className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-2xl font-bold">{stats.total}</div>
                      <div className="text-xs text-yellow-200">Total Analyses</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="p-2 rounded-lg bg-white/20 backdrop-blur-sm">
                      <Clock className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-2xl font-bold">{stats.active}</div>
                      <div className="text-xs text-yellow-200">In Progress</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="p-2 rounded-lg bg-white/20 backdrop-blur-sm">
                      <Award className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-2xl font-bold">{stats.completed}</div>
                      <div className="text-xs text-yellow-200">Completed</div>
                    </div>
                  </div>
                </motion.div>
              </div>

              {/* CTA Button */}
              <motion.button
                className="group px-8 py-4 bg-white text-amber-600 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-300"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: 0.6 }}
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => router.push('/tools/research-direction/new')}
              >
                <span className="flex items-center gap-2">
                  <Plus className="w-5 h-5" />
                  Discover Directions
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
              AI-driven analysis to identify high-impact research opportunities and directions
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                className="group p-6 rounded-2xl bg-white/60 backdrop-blur-sm border border-gray-200 hover:border-yellow-300 shadow-soft hover:shadow-lg transition-all duration-300"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.3 + index * 0.1 }}
                whileHover={{ y: -4 }}
              >
                <div className="flex items-start gap-4">
                  <motion.div
                    className="p-3 rounded-xl bg-yellow-100 text-yellow-600 shadow-sm flex-shrink-0"
                    whileHover={{ scale: 1.1, rotate: 5 }}
                    transition={{ type: 'spring', stiffness: 400, damping: 10 }}
                  >
                    <feature.icon className="w-6 h-6" />
                  </motion.div>

                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-yellow-600 transition-colors">
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
                Recent Analyses
              </h2>
              <p className="text-gray-600">
                Your latest research direction discoveries
              </p>
            </div>
            {recentProjects.length > 0 && (
              <button
                className="group flex items-center gap-2 text-sm font-medium text-primary-600 hover:text-primary-700 transition-colors"
                onClick={() => router.push('/projects?tool=research-direction')}
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
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-yellow-100 text-yellow-600 mb-4">
                <Lightbulb className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                No research direction analyses yet
              </h3>
              <p className="text-gray-600 mb-6 max-w-md mx-auto">
                Discover high-impact research gaps and emerging trends with AI-powered analysis
              </p>
              <motion.button
                className="px-6 py-3 bg-amber-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-glow-accent transition-all duration-300"
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => router.push('/tools/research-direction/new')}
              >
                <span className="flex items-center gap-2">
                  <Plus className="w-5 h-5" />
                  Start Your First Analysis
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
                  icon={Lightbulb}
                  color="yellow"
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

export default ResearchDirectionIndexPage
