'use client'

import React from 'react'
import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'
import {
  Sparkles,
  TrendingUp,
  Shield,
  Zap,
  Brain,
  Target,
  Activity,
  Lock,
  Globe
} from 'lucide-react'

const FeatureCard = ({ feature, index }: { feature: any; index: number }) => {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <motion.div
      ref={ref}
      className="group relative"
      initial={{ opacity: 0, y: 60 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 60 }}
      transition={{ duration: 0.6, delay: index * 0.1, ease: [0.22, 1, 0.36, 1] }}
    >
      <div className="relative p-8 rounded-2xl bg-white/60 backdrop-blur-sm border border-gray-200 hover:border-primary-300 shadow-soft hover:shadow-lg transition-all duration-300 h-full overflow-hidden">
        {/* Gradient overlay on hover */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary-500/0 to-accent-500/0 group-hover:from-primary-500/5 group-hover:to-accent-500/5 transition-all duration-300" />

        <div className="relative z-10">
          {/* Icon */}
          <motion.div
            className="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 text-white mb-5 shadow-lg"
            whileHover={{ scale: 1.1, rotate: 5 }}
            transition={{ type: 'spring', stiffness: 400, damping: 10 }}
          >
            <feature.icon className="w-7 h-7" />
          </motion.div>

          {/* Title */}
          <h3 className="text-xl font-semibold text-gray-900 mb-3 group-hover:text-primary-600 transition-colors">
            {feature.title}
          </h3>

          {/* Description */}
          <p className="text-gray-600 leading-relaxed mb-4">
            {feature.description}
          </p>

          {/* Benefits list */}
          <ul className="space-y-2">
            {feature.benefits.map((benefit: string, idx: number) => (
              <motion.li
                key={idx}
                className="flex items-start gap-2 text-sm text-gray-600"
                initial={{ opacity: 0, x: -10 }}
                animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: -10 }}
                transition={{ duration: 0.4, delay: 0.3 + idx * 0.1 }}
              >
                <Sparkles className="w-4 h-4 text-primary-500 mt-0.5 flex-shrink-0" />
                <span>{benefit}</span>
              </motion.li>
            ))}
          </ul>
        </div>
      </div>
    </motion.div>
  )
}

const FeaturesShowcase: React.FC = () => {
  const features = [
    {
      icon: Brain,
      title: 'Multi-Agent Architecture',
      description: 'Specialized AI agents work together to deliver comprehensive research insights.',
      benefits: [
        'Search agent finds relevant papers',
        'Screening agent filters by criteria',
        'Analysis agent extracts insights',
        'Report agent synthesizes findings'
      ]
    },
    {
      icon: Zap,
      title: 'Lightning Fast',
      description: 'Complete meta-analyses in hours instead of months with automated workflows.',
      benefits: [
        '10x faster than manual methods',
        'Real-time progress tracking',
        'Parallel processing of papers',
        'Instant report generation'
      ]
    },
    {
      icon: Shield,
      title: 'Research-Grade Quality',
      description: 'Built on rigorous academic standards with transparency at every step.',
      benefits: [
        'PRISMA-compliant reporting',
        'Credibility scoring system',
        'Complete audit trails',
        'Explainable AI decisions'
      ]
    },
    {
      icon: Target,
      title: 'Precision Matching',
      description: 'Find the perfect reviewers with expertise-based AI matching algorithms.',
      benefits: [
        'Analyze expertise from publications',
        'Detect conflicts of interest',
        'Predict reviewer availability',
        'Match quality scoring'
      ]
    },
    {
      icon: Activity,
      title: 'Real-Time Collaboration',
      description: 'Work together with your team in real-time with shared workspaces.',
      benefits: [
        'Live project updates',
        'Comment and discussion threads',
        'Role-based permissions',
        'Export to common formats'
      ]
    },
    {
      icon: Globe,
      title: 'Multi-Database Search',
      description: 'Search across PubMed, arXiv, Europe PMC, and CORE simultaneously.',
      benefits: [
        'Unified search interface',
        'Automatic deduplication',
        'Citation extraction',
        'Full-text access where available'
      ]
    },
    {
      icon: TrendingUp,
      title: 'Gap Analysis',
      description: 'Discover understudied research areas and generate novel proposals.',
      benefits: [
        'Visual gap matrices',
        'Trend detection',
        'Method innovation suggestions',
        'Auto-generated proposals'
      ]
    },
    {
      icon: Lock,
      title: 'Secure & Compliant',
      description: 'Enterprise-grade security with GDPR and HIPAA compliance.',
      benefits: [
        'End-to-end encryption',
        'SOC 2 Type II certified',
        'Data residency options',
        'Regular security audits'
      ]
    }
  ]

  const titleRef = useRef(null)
  const isTitleInView = useInView(titleRef, { once: true })

  return (
    <section className="relative py-32 bg-gradient-to-b from-gray-50 to-white overflow-hidden">
      {/* Background decorations */}
      <div className="absolute top-20 left-10 w-72 h-72 bg-primary-200/20 rounded-full blur-3xl" />
      <div className="absolute bottom-20 right-10 w-96 h-96 bg-accent-200/20 rounded-full blur-3xl" />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <motion.div
          ref={titleRef}
          className="text-center mb-16"
          initial={{ opacity: 0, y: 40 }}
          animate={isTitleInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 40 }}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-100 text-primary-700 font-medium text-sm mb-6">
            <Sparkles className="w-4 h-4" />
            Why Researchers Love Us
          </div>

          <h2 className="text-5xl sm:text-6xl font-bold text-gray-900 mb-6">
            Everything you need to
            <span className="block bg-gradient-to-r from-primary-600 to-accent-600 bg-clip-text text-transparent">
              accelerate research
            </span>
          </h2>

          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Powerful features designed for the modern researcher. From literature search to publication, we have you covered.
          </p>
        </motion.div>

        {/* Features grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <FeatureCard key={feature.title} feature={feature} index={index} />
          ))}
        </div>

        {/* Bottom CTA */}
        <motion.div
          className="mt-20 text-center"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
        >
          <div className="inline-flex flex-col sm:flex-row items-center gap-4">
            <motion.button
              className="px-8 py-4 bg-primary-600 text-white rounded-xl font-semibold text-lg shadow-lg hover:shadow-glow-primary transition-all duration-300"
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.98 }}
            >
              Start Your Free Trial
            </motion.button>
            <motion.button
              className="px-8 py-4 bg-white text-gray-900 rounded-xl font-semibold text-lg border border-gray-200 hover:border-gray-300 shadow-soft hover:shadow-medium transition-all duration-300"
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.98 }}
            >
              Book a Demo
            </motion.button>
          </div>
          <p className="mt-4 text-sm text-gray-500">
            No credit card required. 14-day free trial.
          </p>
        </motion.div>
      </div>
    </section>
  )
}

export default FeaturesShowcase
