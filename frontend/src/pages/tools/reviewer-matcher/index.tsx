import React from 'react'
import { motion } from 'framer-motion'
import Layout from '@/components/layout/Layout'
import ProjectCard from '@/components/dashboard/ProjectCard'
import { useAppStore } from '@/stores/useAppStore'
import { ToolType, ProjectStatus } from '../../../lib/types'
import {
  Users,
  Plus,
  ArrowRight,
  Search,
  Target,
  AlertTriangle,
  Clock,
  TrendingUp,
  Award,
  Sparkles,
  Brain,
  Shield
} from 'lucide-react'
import { useRouter } from 'next/router'

const ReviewerMatcherIndexPage: React.FC = () => {
  const router = useRouter()
  const { projects } = useAppStore()

  // Filter projects for this tool type
  const reviewerMatcherProjects = projects.filter(
    p => p.toolType === ToolType.REVIEWER_MATCHER
  )

  const recentProjects = reviewerMatcherProjects
    .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
    .slice(0, 6)

  const stats = {
    total: reviewerMatcherProjects.length,
    active: reviewerMatcherProjects.filter(p => p.status === ProjectStatus.IN_PROGRESS).length,
    completed: reviewerMatcherProjects.filter(p => p.status === ProjectStatus.COMPLETED).length
  }

  const features = [
    {
      icon: Search,
      title: 'Expert Discovery',
      description: 'AI-powered search across global researcher databases to find domain experts'
    },
    {
      icon: Target,
      title: 'Expertise Matching',
      description: 'Deep semantic matching between manuscript content and reviewer expertise'
    },
    {
      icon: Shield,
      title: 'Conflict Detection',
      description: 'Automated identification of potential conflicts of interest and collaborations'
    },
    {
      icon: Clock,
      title: 'Availability Analysis',
      description: 'Intelligent prediction of reviewer availability and workload'
    },
    {
      icon: Brain,
      title: 'Quality Metrics',
      description: 'Comprehensive evaluation of reviewer quality, h-index, and review history'
    },
    {
      icon: Award,
      title: 'Ranked Results',
      description: 'Prioritized list of best-fit reviewers with detailed reasoning and scores'
    }
  ]

  return (
    <Layout title="Reviewer Matcher">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Hero Section */}
        <motion.div
          className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-green-600 via-green-700 to-emerald-800 p-8 md:p-12 text-white"
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
            className="absolute bottom-0 left-0 w-96 h-96 bg-emerald-400/20 rounded-full blur-3xl"
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
                    <Users className="w-8 h-8" />
                  </div>
                  <div>
                    <h1 className="text-4xl md:text-5xl font-bold">
                      Reviewer Matcher
                    </h1>
                    <div className="flex items-center gap-2 mt-1">
                      <Sparkles className="w-4 h-4 text-green-200" />
                      <span className="text-sm text-green-100 font-medium">
                        AI-Powered Expert Discovery
                      </span>
                    </div>
                  </div>
                </motion.div>

                <motion.p
                  className="text-lg text-green-100 max-w-2xl leading-relaxed mb-6"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.4 }}
                >
                  Find the perfect peer reviewers for your manuscript in minutes. Our AI analyzes
                  expertise, availability, and conflicts to recommend the most qualified reviewers
                  from a global database of researchers.
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
                      <div className="text-xs text-green-200">Total Searches</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="p-2 rounded-lg bg-white/20 backdrop-blur-sm">
                      <Clock className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-2xl font-bold">{stats.active}</div>
                      <div className="text-xs text-green-200">In Progress</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="p-2 rounded-lg bg-white/20 backdrop-blur-sm">
                      <Award className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-2xl font-bold">{stats.completed}</div>
                      <div className="text-xs text-green-200">Completed</div>
                    </div>
                  </div>
                </motion.div>
              </div>

              {/* CTA Button */}
              <motion.button
                className="group px-8 py-4 bg-white text-green-600 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-300"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: 0.6 }}
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => router.push('/tools/reviewer-matcher/new')}
              >
                <span className="flex items-center gap-2">
                  <Plus className="w-5 h-5" />
                  Find Reviewers
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
              AI-driven matching process to identify the best-fit reviewers for your manuscript
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                className="group p-6 rounded-2xl bg-white/60 backdrop-blur-sm border border-gray-200 hover:border-green-300 shadow-soft hover:shadow-lg transition-all duration-300"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.3 + index * 0.1 }}
                whileHover={{ y: -4 }}
              >
                <div className="flex items-start gap-4">
                  <motion.div
                    className="p-3 rounded-xl bg-green-100 text-green-600 shadow-sm flex-shrink-0"
                    whileHover={{ scale: 1.1, rotate: 5 }}
                    transition={{ type: 'spring', stiffness: 400, damping: 10 }}
                  >
                    <feature.icon className="w-6 h-6" />
                  </motion.div>

                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-green-600 transition-colors">
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
                Recent Searches
              </h2>
              <p className="text-gray-600">
                Your latest reviewer matching projects
              </p>
            </div>
            {recentProjects.length > 0 && (
              <button
                className="group flex items-center gap-2 text-sm font-medium text-primary-600 hover:text-primary-700 transition-colors"
                onClick={() => router.push('/projects?tool=reviewer-matcher')}
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
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-green-100 text-green-600 mb-4">
                <Users className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                No reviewer searches yet
              </h3>
              <p className="text-gray-600 mb-6 max-w-md mx-auto">
                Find the perfect peer reviewers for your manuscript with AI-powered expert matching
              </p>
              <motion.button
                className="px-6 py-3 bg-green-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-glow-success transition-all duration-300"
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => router.push('/tools/reviewer-matcher/new')}
              >
                <span className="flex items-center gap-2">
                  <Plus className="w-5 h-5" />
                  Start Your First Search
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
                  icon={Users}
                  color="green"
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

export default ReviewerMatcherIndexPage
