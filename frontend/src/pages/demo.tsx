import React, { useState } from 'react'
import { motion } from 'framer-motion'
import Layout from '@/components/layout/Layout'
import {
  Play,
  Pause,
  RotateCcw,
  ChevronRight,
  Microscope,
  Users,
  FileText,
  Lightbulb,
  CheckCircle2,
  ArrowRight
} from 'lucide-react'
import { useRouter } from 'next/router'

interface DemoStep {
  id: number
  tool: string
  title: string
  description: string
  icon: any
  color: string
  gradient: string
  duration: string
  example: string
}

const demoSteps: DemoStep[] = [
  {
    id: 1,
    tool: 'Meta-Analysis',
    title: 'Create Systematic Review',
    description: 'Define your research question, inclusion/exclusion criteria, and let AI agents search, screen, and analyze hundreds of papers automatically.',
    icon: Microscope,
    color: 'blue',
    gradient: 'from-blue-500/10 to-blue-600/10',
    duration: '15-30 min',
    example: 'Effect of cognitive behavioral therapy on depression'
  },
  {
    id: 2,
    tool: 'Reviewer Matcher',
    title: 'Find Expert Reviewers',
    description: 'Upload your manuscript and our AI analyzes publication history to match you with the most qualified reviewers in your field.',
    icon: Users,
    color: 'green',
    gradient: 'from-green-500/10 to-green-600/10',
    duration: '5-10 min',
    example: 'Machine learning in medical imaging'
  },
  {
    id: 3,
    tool: 'Peer Review',
    title: 'Generate Peer Reviews',
    description: 'Get constructive, comprehensive peer reviews that evaluate methodology, significance, and writing quality with actionable feedback.',
    icon: FileText,
    color: 'purple',
    gradient: 'from-purple-500/10 to-purple-600/10',
    duration: '10-15 min',
    example: 'Clinical trial manuscript review'
  },
  {
    id: 4,
    tool: 'Research Direction',
    title: 'Discover Research Gaps',
    description: 'Explore emerging trends, identify unexplored areas, and get AI-generated research proposals with novelty and feasibility scores.',
    icon: Lightbulb,
    color: 'yellow',
    gradient: 'from-yellow-500/10 to-yellow-600/10',
    duration: '10-20 min',
    example: 'Novel approaches to cancer immunotherapy'
  }
]

const DemoPage: React.FC = () => {
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying)
    if (!isPlaying && currentStep >= demoSteps.length - 1) {
      setCurrentStep(0)
    }
  }

  const handleReset = () => {
    setCurrentStep(0)
    setIsPlaying(false)
  }

  const handleNext = () => {
    if (currentStep < demoSteps.length - 1) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleTryTool = (tool: string) => {
    const routes: { [key: string]: string } = {
      'Meta-Analysis': '/tools/meta-analysis/new',
      'Reviewer Matcher': '/tools/reviewer-matcher/new',
      'Peer Review': '/tools/peer-review/new',
      'Research Direction': '/tools/research-direction/new'
    }
    router.push(routes[tool] || '/dashboard')
  }

  React.useEffect(() => {
    let interval: NodeJS.Timeout
    if (isPlaying && currentStep < demoSteps.length - 1) {
      interval = setInterval(() => {
        setCurrentStep(prev => {
          if (prev >= demoSteps.length - 1) {
            setIsPlaying(false)
            return prev
          }
          return prev + 1
        })
      }, 5000) // 5 seconds per step
    }
    return () => clearInterval(interval)
  }, [isPlaying, currentStep])

  const currentStepData = demoSteps[currentStep]

  return (
    <Layout title="Platform Demo">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <motion.div
          className="text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Platform Walkthrough
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            See how our AI-powered research tools can accelerate your academic workflow
          </p>
        </motion.div>

        {/* Main Demo Area */}
        <motion.div
          className="bg-white/60 backdrop-blur-sm rounded-3xl p-8 md:p-12 border border-gray-200 shadow-soft"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          {/* Current Step Display */}
          <div className="mb-8">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.4 }}
              className={`relative overflow-hidden rounded-2xl bg-gradient-to-br ${currentStepData.gradient} p-8 border border-gray-200`}
            >
              <div className="flex items-start gap-6">
                <div className={`flex-shrink-0 p-4 rounded-xl bg-${currentStepData.color}-100 text-${currentStepData.color}-600`}>
                  <currentStepData.icon className="w-8 h-8" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-3">
                    <span className={`text-sm font-semibold px-3 py-1 rounded-full bg-${currentStepData.color}-100 text-${currentStepData.color}-600`}>
                      {currentStepData.tool}
                    </span>
                    <span className="text-sm text-gray-500">
                      {currentStepData.duration}
                    </span>
                  </div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-3">
                    {currentStepData.title}
                  </h2>
                  <p className="text-gray-600 mb-4">
                    {currentStepData.description}
                  </p>
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <span className="font-medium">Example:</span>
                    <span className="italic">{currentStepData.example}</span>
                  </div>
                  <motion.button
                    onClick={() => handleTryTool(currentStepData.tool)}
                    className={`mt-6 px-6 py-3 bg-${currentStepData.color}-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-glow-${currentStepData.color} transition-all duration-300`}
                    whileHover={{ scale: 1.05, y: -2 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <span className="flex items-center gap-2">
                      Try This Tool
                      <ArrowRight className="w-5 h-5" />
                    </span>
                  </motion.button>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Controls */}
          <div className="flex items-center justify-center gap-4 mb-8">
            <motion.button
              onClick={handleReset}
              className="p-3 rounded-xl bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <RotateCcw className="w-5 h-5" />
            </motion.button>
            <motion.button
              onClick={handlePrevious}
              disabled={currentStep === 0}
              className="p-3 rounded-xl bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
              whileHover={{ scale: currentStep === 0 ? 1 : 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <ChevronRight className="w-5 h-5 rotate-180" />
            </motion.button>
            <motion.button
              onClick={handlePlayPause}
              className="px-8 py-4 rounded-xl bg-primary-600 text-white font-semibold shadow-lg hover:shadow-glow-primary transition-all duration-300"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <span className="flex items-center gap-2">
                {isPlaying ? (
                  <>
                    <Pause className="w-5 h-5" />
                    Pause
                  </>
                ) : (
                  <>
                    <Play className="w-5 h-5" />
                    {currentStep >= demoSteps.length - 1 ? 'Replay' : 'Play'}
                  </>
                )}
              </span>
            </motion.button>
            <motion.button
              onClick={handleNext}
              disabled={currentStep === demoSteps.length - 1}
              className="p-3 rounded-xl bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
              whileHover={{ scale: currentStep === demoSteps.length - 1 ? 1 : 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <ChevronRight className="w-5 h-5" />
            </motion.button>
          </div>

          {/* Progress Dots */}
          <div className="flex items-center justify-center gap-2">
            {demoSteps.map((step, index) => (
              <motion.button
                key={step.id}
                onClick={() => setCurrentStep(index)}
                className={`h-2 rounded-full transition-all duration-300 ${
                  index === currentStep
                    ? 'w-8 bg-primary-600'
                    : 'w-2 bg-gray-300 hover:bg-gray-400'
                }`}
                whileHover={{ scale: 1.2 }}
              />
            ))}
          </div>
        </motion.div>

        {/* All Tools Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Explore All Tools
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {demoSteps.map((step, index) => (
              <motion.div
                key={step.id}
                className={`group relative p-6 rounded-2xl bg-gradient-to-br ${step.gradient} backdrop-blur-sm border border-gray-200 hover:border-${step.color}-300 shadow-soft hover:shadow-lg transition-all duration-300 cursor-pointer`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.3 + index * 0.1 }}
                whileHover={{ y: -4 }}
                onClick={() => handleTryTool(step.tool)}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className={`p-3 rounded-xl bg-${step.color}-100 text-${step.color}-600`}>
                    <step.icon className="w-6 h-6" />
                  </div>
                  {currentStep === index && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="flex items-center gap-1 text-sm font-semibold text-primary-600"
                    >
                      <CheckCircle2 className="w-4 h-4" />
                      Viewing
                    </motion.div>
                  )}
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {step.title}
                </h3>
                <p className="text-sm text-gray-600 mb-3">
                  {step.description}
                </p>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">{step.duration}</span>
                  <span className="text-primary-600 font-medium group-hover:translate-x-1 transition-transform">
                    Try Now →
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* CTA */}
        <motion.div
          className="text-center bg-gradient-to-br from-primary-600 via-primary-700 to-accent-600 rounded-2xl p-8 text-white"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <h2 className="text-2xl font-bold mb-4">
            Ready to Transform Your Research?
          </h2>
          <p className="text-primary-100 mb-6 max-w-2xl mx-auto">
            Join researchers worldwide who are accelerating their work with AI-powered tools
          </p>
          <motion.button
            onClick={() => router.push('/dashboard')}
            className="px-8 py-4 bg-white text-primary-600 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-300"
            whileHover={{ scale: 1.05, y: -2 }}
            whileTap={{ scale: 0.98 }}
          >
            <span className="flex items-center gap-2">
              Get Started Free
              <ArrowRight className="w-5 h-5" />
            </span>
          </motion.button>
        </motion.div>
      </div>
    </Layout>
  )
}

export default DemoPage
