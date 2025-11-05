import React from 'react'
import { motion } from 'framer-motion'
import Layout from '@/components/layout/Layout'
import ProjectCard from '@/components/dashboard/ProjectCard'
import { useAppStore } from '@/stores/useAppStore'
import { ToolType, ProjectStatus } from '@/lib/types'
import {
  FileText,
  Plus,
  ArrowRight,
  Eye,
  MessageSquare,
  TrendingUp,
  CheckCircle2,
  AlertCircle,
  Clock,
  Award,
  Sparkles,
  Brain,
  Shield
} from 'lucide-react'
import { useRouter } from 'next/router'

const PeerReviewIndexPage: React.FC = () => {
  const router = useRouter()
  const { projects } = useAppStore()

  // Filter projects for this tool type
  const peerReviewProjects = projects.filter(
    p => p.toolType === ToolType.PEER_REVIEW
  )

  const recentProjects = peerReviewProjects
    .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
    .slice(0, 6)

  const stats = {
    total: peerReviewProjects.length,
    active: peerReviewProjects.filter(p => p.status === ProjectStatus.IN_PROGRESS).length,
    completed: peerReviewProjects.filter(p => p.status === ProjectStatus.COMPLETED).length
  }

  const features = [
    {
      icon: Eye,
      title: 'Deep Analysis',
      description: 'Comprehensive evaluation of manuscript structure, methodology, and results'
    },
    {
      icon: Brain,
      title: 'Multi-Perspective Review',
      description: 'AI agents simulate multiple expert reviewers with different specializations'
    },
    {
      icon: Shield,
      title: 'Bias Detection',
      description: 'Automated identification of potential biases and methodological flaws'
    },
    {
      icon: MessageSquare,
      title: 'Constructive Feedback',
      description: 'Detailed, actionable suggestions for improving the manuscript'
    },
    {
      icon: CheckCircle2,
      title: 'Quality Metrics',
      description: 'Objective scoring of technical accuracy, novelty, and clarity'
    },
    {
      icon: FileText,
      title: 'Review Report',
      description: 'Publication-ready peer review report with recommendations'
    }
  ]

  return (
    <Layout title="Peer Review">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Hero Section */}
        <motion.div
          className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-purple-600 via-purple-700 to-violet-800 p-8 md:p-12 text-white"
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
            className="absolute bottom-0 left-0 w-96 h-96 bg-violet-400/20 rounded-full blur-3xl"
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
                    <FileText className="w-8 h-8" />
                  </div>
                  <div>
                    <h1 className="text-4xl md:text-5xl font-bold">
                      Peer Review
                    </h1>
                    <div className="flex items-center gap-2 mt-1">
                      <Sparkles className="w-4 h-4 text-purple-200" />
                      <span className="text-sm text-purple-100 font-medium">
                        AI-Powered Manuscript Review
                      </span>
                    </div>
                  </div>
                </motion.div>

                <motion.p
                  className="text-lg text-purple-100 max-w-2xl leading-relaxed mb-6"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.4 }}
                >
                  Generate comprehensive, publication-quality peer reviews in minutes. Our AI agents
                  analyze manuscripts from multiple expert perspectives, providing constructive feedback,
                  bias detection, and actionable recommendations.
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
                      <div className="text-xs text-purple-200">Total Reviews</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="p-2 rounded-lg bg-white/20 backdrop-blur-sm">
                      <Clock className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-2xl font-bold">{stats.active}</div>
                      <div className="text-xs text-purple-200">In Progress</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="p-2 rounded-lg bg-white/20 backdrop-blur-sm">
                      <Award className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-2xl font-bold">{stats.completed}</div>
                      <div className="text-xs text-purple-200">Completed</div>
                    </div>
                  </div>
                </motion.div>
              </div>

              {/* CTA Button */}
              <motion.button
                className="group px-8 py-4 bg-white text-purple-600 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-300"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: 0.6 }}
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => router.push('/tools/peer-review/new')}
              >
                <span className="flex items-center gap-2">
                  <Plus className="w-5 h-5" />
                  Generate Review
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
              AI-powered multi-perspective analysis for comprehensive manuscript reviews
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                className="group p-6 rounded-2xl bg-white/60 backdrop-blur-sm border border-gray-200 hover:border-purple-300 shadow-soft hover:shadow-lg transition-all duration-300"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.3 + index * 0.1 }}
                whileHover={{ y: -4 }}
              >
                <div className="flex items-start gap-4">
                  <motion.div
                    className="p-3 rounded-xl bg-purple-100 text-purple-600 shadow-sm flex-shrink-0"
                    whileHover={{ scale: 1.1, rotate: 5 }}
                    transition={{ type: 'spring', stiffness: 400, damping: 10 }}
                  >
                    <feature.icon className="w-6 h-6" />
                  </motion.div>

                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-purple-600 transition-colors">
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
                Recent Reviews
              </h2>
              <p className="text-gray-600">
                Your latest peer review projects
              </p>
            </div>
            {recentProjects.length > 0 && (
              <button
                className="group flex items-center gap-2 text-sm font-medium text-primary-600 hover:text-primary-700 transition-colors"
                onClick={() => router.push('/projects?tool=peer-review')}
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
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-purple-100 text-purple-600 mb-4">
                <FileText className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                No peer reviews yet
              </h3>
              <p className="text-gray-600 mb-6 max-w-md mx-auto">
                Generate comprehensive AI-powered peer reviews with multi-perspective analysis
              </p>
              <motion.button
                className="px-6 py-3 bg-purple-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-glow-purple transition-all duration-300"
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => router.push('/tools/peer-review/new')}
              >
                <span className="flex items-center gap-2">
                  <Plus className="w-5 h-5" />
                  Create Your First Review
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
                  icon={FileText}
                  color="purple"
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

export default PeerReviewIndexPage
