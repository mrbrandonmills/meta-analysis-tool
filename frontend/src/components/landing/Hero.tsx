'use client'

import React, { useEffect, useRef } from 'react'
import { motion, useScroll, useTransform, useSpring } from 'framer-motion'
import { useRouter } from 'next/router'
import {
  Sparkles,
  Brain,
  Zap,
  ArrowRight,
  CheckCircle2,
  Users,
  Microscope,
  FileText,
  Lightbulb
} from 'lucide-react'

const Hero: React.FC = () => {
  const router = useRouter()
  const containerRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start start', 'end start']
  })

  // Smooth parallax effects
  const y = useSpring(useTransform(scrollYProgress, [0, 1], ['0%', '50%']), {
    stiffness: 100,
    damping: 30,
    restDelta: 0.001
  })

  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0])

  return (
    <div ref={containerRef} className="relative min-h-screen overflow-hidden bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/30">
      {/* Animated mesh gradient background */}
      <div className="absolute inset-0 bg-gradient-mesh opacity-30 animate-pulse-slow" />

      {/* Floating orbs */}
      <motion.div
        className="absolute top-20 left-1/4 w-64 h-64 bg-primary-400/20 rounded-full blur-3xl"
        animate={{
          y: [0, 30, 0],
          scale: [1, 1.1, 1],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: 'easeInOut'
        }}
      />
      <motion.div
        className="absolute bottom-20 right-1/4 w-96 h-96 bg-accent-400/20 rounded-full blur-3xl"
        animate={{
          y: [0, -40, 0],
          scale: [1, 1.2, 1],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: 'easeInOut'
        }}
      />

      <motion.div
        className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-32 pb-20"
        style={{ y, opacity }}
      >
        {/* Badge */}
        <motion.div
          className="flex justify-center mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/80 backdrop-blur-sm border border-gray-200 shadow-soft">
            <Sparkles className="w-4 h-4 text-primary-600" />
            <span className="text-sm font-medium text-gray-700">
              AI-Powered Research Platform
            </span>
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          </div>
        </motion.div>

        {/* Main heading */}
        <motion.h1
          className="text-center text-6xl sm:text-7xl lg:text-8xl font-bold tracking-tight mb-8 leading-tight"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
        >
          <span className="block text-gray-900 pb-2">Transform Research</span>
          <span className="block bg-gradient-to-r from-primary-600 via-accent-600 to-primary-600 bg-clip-text text-transparent animate-shimmer bg-[length:200%_100%] pb-2">
            with AI Agents
          </span>
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          className="text-center text-xl sm:text-2xl text-gray-600 max-w-3xl mx-auto mb-12 leading-relaxed"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
        >
          Meta-analysis, peer review, and research discovery powered by specialized AI agents.
          Complete in hours what used to take weeks.
        </motion.p>

        {/* CTA Buttons */}
        <motion.div
          className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3, ease: [0.22, 1, 0.36, 1] }}
        >
          <motion.button
            className="group relative px-8 py-4 bg-primary-600 text-white rounded-xl font-semibold text-lg shadow-lg hover:shadow-glow-primary transition-all duration-300"
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => router.push('/dashboard')}
          >
            <span className="flex items-center gap-2">
              Get Started Free
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </span>
          </motion.button>

          <motion.button
            className="group px-8 py-4 bg-white/80 backdrop-blur-sm text-gray-900 rounded-xl font-semibold text-lg border border-gray-200 hover:border-gray-300 shadow-soft hover:shadow-medium transition-all duration-300"
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => router.push('/dashboard')} // TODO: Create /demo page
          >
            <span className="flex items-center gap-2">
              Watch Demo
              <Zap className="w-5 h-5 group-hover:rotate-12 transition-transform" />
            </span>
          </motion.button>
        </motion.div>

        {/* Stats */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto mb-20"
          initial={{ opacity: 0, y: 60 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4, ease: [0.22, 1, 0.36, 1] }}
        >
          {[
            { value: '10x', label: 'Faster Research', icon: Zap },
            { value: '95%', label: 'Accuracy Rate', icon: CheckCircle2 },
            { value: '50K+', label: 'Papers Analyzed', icon: Brain }
          ].map((stat, index) => (
            <motion.div
              key={stat.label}
              className="text-center p-6 rounded-2xl bg-white/60 backdrop-blur-sm border border-gray-200 shadow-soft hover:shadow-medium transition-shadow duration-300"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.5 + index * 0.1 }}
              whileHover={{ y: -4 }}
            >
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-primary-100 text-primary-600 mb-3">
                <stat.icon className="w-6 h-6" />
              </div>
              <div className="text-4xl font-bold text-gray-900 mb-1">{stat.value}</div>
              <div className="text-sm font-medium text-gray-600">{stat.label}</div>
            </motion.div>
          ))}
        </motion.div>

        {/* Tool Cards Grid */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
          initial={{ opacity: 0, y: 80 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6, ease: [0.22, 1, 0.36, 1] }}
        >
          {[
            {
              icon: Microscope,
              title: 'Meta-Analysis',
              description: 'Systematic literature synthesis with AI-powered screening',
              color: 'blue',
              gradient: 'from-blue-500/10 to-blue-600/10'
            },
            {
              icon: Users,
              title: 'Reviewer Matcher',
              description: 'Find expert reviewers in minutes with smart matching',
              color: 'green',
              gradient: 'from-green-500/10 to-green-600/10'
            },
            {
              icon: FileText,
              title: 'Peer Review',
              description: 'Generate comprehensive, constructive peer reviews',
              color: 'purple',
              gradient: 'from-purple-500/10 to-purple-600/10'
            },
            {
              icon: Lightbulb,
              title: 'Research Direction',
              description: 'Discover gaps and generate novel research proposals',
              color: 'yellow',
              gradient: 'from-yellow-500/10 to-yellow-600/10'
            }
          ].map((tool, index) => (
            <motion.div
              key={tool.title}
              className={`group relative p-6 rounded-2xl bg-gradient-to-br ${tool.gradient} backdrop-blur-sm border border-gray-200 hover:border-${tool.color}-300 shadow-soft hover:shadow-lg transition-all duration-300 cursor-pointer overflow-hidden`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.7 + index * 0.1 }}
              whileHover={{ y: -8, scale: 1.02 }}
              onClick={() => router.push('/dashboard')} // TODO: Create /tools/[toolname] pages
            >
              {/* Hover glow effect */}
              <div className={`absolute inset-0 bg-gradient-to-br from-${tool.color}-500/0 to-${tool.color}-600/0 group-hover:from-${tool.color}-500/5 group-hover:to-${tool.color}-600/10 transition-all duration-300`} />

              <div className="relative z-10">
                <div className={`inline-flex items-center justify-center w-12 h-12 rounded-xl bg-${tool.color}-100 text-${tool.color}-600 mb-4 group-hover:scale-110 transition-transform duration-300`}>
                  <tool.icon className="w-6 h-6" />
                </div>

                <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors">
                  {tool.title}
                </h3>

                <p className="text-sm text-gray-600 leading-relaxed">
                  {tool.description}
                </p>

                <div className="mt-4 flex items-center text-sm font-medium text-primary-600 opacity-0 group-hover:opacity-100 transition-opacity">
                  Learn more
                  <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </motion.div>

      {/* Scroll indicator */}
      <motion.div
        className="absolute bottom-8 left-1/2 -translate-x-1/2"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.5 }}
      >
        <motion.div
          className="w-6 h-10 rounded-full border-2 border-gray-400 p-1"
          animate={{ y: [0, 8, 0] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        >
          <div className="w-1 h-2 bg-gray-400 rounded-full mx-auto" />
        </motion.div>
      </motion.div>
    </div>
  )
}

export default Hero
