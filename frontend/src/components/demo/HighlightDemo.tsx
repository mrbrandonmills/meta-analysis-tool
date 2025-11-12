'use client'

import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence, useAnimation } from 'framer-motion'
import {
  Play,
  Pause,
  RotateCcw,
  FastForward,
  Sparkles,
  Database,
  FileText,
  CheckCircle2,
  XCircle,
  BarChart3,
  FileCheck,
  Zap,
  Clock,
  Trophy,
  Rocket,
  Target,
  Search,
  Brain,
  TrendingUp
} from 'lucide-react'

// ============================================================================
// ANIMATION VARIANTS - ESPN-STYLE CINEMATICS
// ============================================================================

const fadeInUp = {
  hidden: { opacity: 0, y: 60, scale: 0.9 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1] }
  },
  exit: {
    opacity: 0,
    y: -60,
    scale: 0.9,
    transition: { duration: 0.3 }
  }
}

const scaleIn = {
  hidden: { scale: 0, opacity: 0 },
  visible: {
    scale: 1,
    opacity: 1,
    transition: {
      type: 'spring',
      stiffness: 200,
      damping: 20
    }
  }
}

const slideInLeft = {
  hidden: { x: -100, opacity: 0 },
  visible: (i: number) => ({
    x: 0,
    opacity: 1,
    transition: {
      delay: i * 0.1,
      duration: 0.4,
      ease: [0.22, 1, 0.36, 1]
    }
  })
}

const stampAnimation = {
  initial: { scale: 0, rotate: -30, opacity: 0 },
  animate: {
    scale: [0, 1.2, 1],
    rotate: [30, -10, 0],
    opacity: 1,
    transition: {
      duration: 0.5,
      ease: [0.22, 1, 0.36, 1]
    }
  }
}

const confettiVariants = {
  hidden: { opacity: 0, scale: 0 },
  visible: (i: number) => ({
    opacity: [0, 1, 1, 0],
    scale: [0, 1, 1, 0.5],
    x: [0, Math.random() * 200 - 100],
    y: [0, -Math.random() * 300 - 100],
    rotate: [0, Math.random() * 360],
    transition: {
      duration: 1.5,
      delay: i * 0.05,
      ease: 'easeOut'
    }
  })
}

// ============================================================================
// DEMO STAGES - THE HIGHLIGHT REEL
// ============================================================================

type DemoStage =
  | 'intro'
  | 'create'
  | 'search'
  | 'papers-flow'
  | 'screening'
  | 'extraction'
  | 'analysis'
  | 'report'
  | 'celebration'
  | 'stats'

interface DemoStageConfig {
  id: DemoStage
  duration: number // milliseconds
  title: string
  subtitle: string
  icon: React.ReactNode
  color: string
  soundEffect?: string
}

const DEMO_STAGES: DemoStageConfig[] = [
  {
    id: 'intro',
    duration: 2000,
    title: 'The Challenge',
    subtitle: 'Traditional meta-analysis takes 6-12 months',
    icon: <Clock className="w-16 h-16" />,
    color: 'from-gray-600 to-gray-800',
    soundEffect: 'dramatic-intro'
  },
  {
    id: 'create',
    duration: 1500,
    title: 'Create Project',
    subtitle: 'Dr. Smith starts a new meta-analysis',
    icon: <Rocket className="w-16 h-16" />,
    color: 'from-blue-600 to-blue-800',
    soundEffect: 'project-start'
  },
  {
    id: 'search',
    duration: 3000,
    title: 'AI Database Search',
    subtitle: 'Searching 47 databases simultaneously...',
    icon: <Database className="w-16 h-16" />,
    color: 'from-purple-600 to-purple-800',
    soundEffect: 'search-whoosh'
  },
  {
    id: 'papers-flow',
    duration: 2500,
    title: 'Papers Discovered',
    subtitle: 'Found 2,847 relevant papers!',
    icon: <FileText className="w-16 h-16" />,
    color: 'from-indigo-600 to-indigo-800',
    soundEffect: 'papers-cascade'
  },
  {
    id: 'screening',
    duration: 4000,
    title: 'AI Screening',
    subtitle: 'Intelligent filtering with 99.2% accuracy',
    icon: <Target className="w-16 h-16" />,
    color: 'from-cyan-600 to-cyan-800',
    soundEffect: 'screening-stamps'
  },
  {
    id: 'extraction',
    duration: 2500,
    title: 'Data Extraction',
    subtitle: 'Extracting key findings and statistics',
    icon: <Brain className="w-16 h-16" />,
    color: 'from-teal-600 to-teal-800',
    soundEffect: 'data-extraction'
  },
  {
    id: 'analysis',
    duration: 3000,
    title: 'Statistical Analysis',
    subtitle: 'Running meta-regression and subgroup analysis',
    icon: <BarChart3 className="w-16 h-16" />,
    color: 'from-green-600 to-green-800',
    soundEffect: 'chart-build'
  },
  {
    id: 'report',
    duration: 2000,
    title: 'Report Generation',
    subtitle: 'Publication-ready manuscript complete',
    icon: <FileCheck className="w-16 h-16" />,
    color: 'from-emerald-600 to-emerald-800',
    soundEffect: 'report-complete'
  },
  {
    id: 'celebration',
    duration: 2500,
    title: 'Mission Complete!',
    subtitle: '6 months of work done in 3 hours',
    icon: <Trophy className="w-16 h-16" />,
    color: 'from-yellow-500 to-orange-600',
    soundEffect: 'victory-fanfare'
  },
  {
    id: 'stats',
    duration: 4000,
    title: 'Impact',
    subtitle: 'Join thousands of researchers saving time',
    icon: <TrendingUp className="w-16 h-16" />,
    color: 'from-pink-600 to-rose-600',
    soundEffect: 'stats-reveal'
  }
]

// ============================================================================
// MAIN COMPONENT
// ============================================================================

interface HighlightDemoProps {
  onComplete?: () => void
  autoPlay?: boolean
  className?: string
}

export const HighlightDemo: React.FC<HighlightDemoProps> = ({
  onComplete,
  autoPlay = false,
  className = ''
}) => {
  const [isPlaying, setIsPlaying] = useState(autoPlay)
  const [currentStageIndex, setCurrentStageIndex] = useState(0)
  const [playbackSpeed, setPlaybackSpeed] = useState(1)
  const [hasStarted, setHasStarted] = useState(false)
  const timeoutRef = useRef<NodeJS.Timeout>()

  const currentStage = DEMO_STAGES[currentStageIndex]
  const progress = ((currentStageIndex + 1) / DEMO_STAGES.length) * 100

  // ============================================================================
  // PLAYBACK CONTROL
  // ============================================================================

  useEffect(() => {
    if (isPlaying && currentStageIndex < DEMO_STAGES.length) {
      const duration = currentStage.duration / playbackSpeed

      timeoutRef.current = setTimeout(() => {
        if (currentStageIndex < DEMO_STAGES.length - 1) {
          setCurrentStageIndex((prev) => prev + 1)
        } else {
          setIsPlaying(false)
          onComplete?.()
        }
      }, duration)
    }

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [isPlaying, currentStageIndex, playbackSpeed, currentStage, onComplete])

  const handlePlayPause = () => {
    if (!hasStarted) {
      setHasStarted(true)
    }
    setIsPlaying(!isPlaying)
  }

  const handleRestart = () => {
    setCurrentStageIndex(0)
    setIsPlaying(true)
    setHasStarted(true)
  }

  const handleSpeedChange = () => {
    const speeds = [0.5, 1, 2, 4]
    const currentIndex = speeds.indexOf(playbackSpeed)
    const nextIndex = (currentIndex + 1) % speeds.length
    setPlaybackSpeed(speeds[nextIndex])
  }

  const jumpToStage = (index: number) => {
    setCurrentStageIndex(index)
    setIsPlaying(true)
    setHasStarted(true)
  }

  // ============================================================================
  // RENDER STAGE CONTENT
  // ============================================================================

  const renderStageContent = () => {
    switch (currentStage.id) {
      case 'intro':
        return <IntroStage />
      case 'create':
        return <CreateProjectStage />
      case 'search':
        return <SearchStage />
      case 'papers-flow':
        return <PapersFlowStage />
      case 'screening':
        return <ScreeningStage playbackSpeed={playbackSpeed} />
      case 'extraction':
        return <ExtractionStage />
      case 'analysis':
        return <AnalysisStage />
      case 'report':
        return <ReportStage />
      case 'celebration':
        return <CelebrationStage />
      case 'stats':
        return <StatsStage />
      default:
        return null
    }
  }

  // ============================================================================
  // MAIN RENDER
  // ============================================================================

  return (
    <div className={`relative w-full h-screen bg-black overflow-hidden ${className}`}>
      {/* Animated background gradient */}
      <motion.div
        className={`absolute inset-0 bg-gradient-to-br ${currentStage.color} opacity-80`}
        animate={{
          background: [
            `linear-gradient(to bottom right, var(--tw-gradient-stops))`,
            `linear-gradient(135deg, var(--tw-gradient-stops))`,
            `linear-gradient(to bottom right, var(--tw-gradient-stops))`
          ]
        }}
        transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
      />

      {/* Radial glow */}
      <motion.div
        className="absolute top-1/2 left-1/2 w-[800px] h-[800px] -translate-x-1/2 -translate-y-1/2 rounded-full blur-3xl opacity-30"
        style={{ background: 'radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%)' }}
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.2, 0.4, 0.2]
        }}
        transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
      />

      {/* Main content area */}
      <div className="relative z-10 h-full flex flex-col">
        {/* Progress bar */}
        <div className="absolute top-0 left-0 right-0 h-2 bg-black/30">
          <motion.div
            className="h-full bg-gradient-to-r from-yellow-400 via-orange-500 to-red-500"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
          />
        </div>

        {/* Stage title overlay */}
        <motion.div
          className="absolute top-8 left-0 right-0 text-center z-20"
          key={currentStage.id}
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 20 }}
          transition={{ duration: 0.4 }}
        >
          <motion.div
            className="inline-flex items-center gap-3 px-6 py-3 bg-white/10 backdrop-blur-md border border-white/20 rounded-full"
            animate={{ scale: [1, 1.05, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <div className="text-white">{currentStage.icon}</div>
            <div className="text-left">
              <div className="text-2xl font-bold text-white">{currentStage.title}</div>
              <div className="text-sm text-white/80">{currentStage.subtitle}</div>
            </div>
          </motion.div>
        </motion.div>

        {/* Main stage content */}
        <div className="flex-1 flex items-center justify-center p-8">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStage.id}
              className="w-full max-w-6xl"
              initial="hidden"
              animate="visible"
              exit="exit"
              variants={fadeInUp}
            >
              {renderStageContent()}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Control panel */}
        <div className="absolute bottom-8 left-0 right-0 flex items-center justify-center gap-4 z-20">
          {/* Restart */}
          <motion.button
            onClick={handleRestart}
            className="p-4 bg-white/10 backdrop-blur-md border border-white/20 rounded-full hover:bg-white/20 transition-colors"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
          >
            <RotateCcw className="w-6 h-6 text-white" />
          </motion.button>

          {/* Play/Pause */}
          <motion.button
            onClick={handlePlayPause}
            className="p-6 bg-white/20 backdrop-blur-md border-2 border-white/40 rounded-full hover:bg-white/30 transition-colors shadow-lg"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
          >
            {isPlaying ? (
              <Pause className="w-8 h-8 text-white fill-white" />
            ) : (
              <Play className="w-8 h-8 text-white fill-white ml-1" />
            )}
          </motion.button>

          {/* Speed control */}
          <motion.button
            onClick={handleSpeedChange}
            className="px-6 py-4 bg-white/10 backdrop-blur-md border border-white/20 rounded-full hover:bg-white/20 transition-colors"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
          >
            <div className="flex items-center gap-2">
              <FastForward className="w-5 h-5 text-white" />
              <span className="text-white font-bold">{playbackSpeed}x</span>
            </div>
          </motion.button>
        </div>

        {/* Stage navigation dots */}
        <div className="absolute bottom-32 left-0 right-0 flex items-center justify-center gap-2 z-20">
          {DEMO_STAGES.map((stage, index) => (
            <motion.button
              key={stage.id}
              onClick={() => jumpToStage(index)}
              className={`h-2 rounded-full transition-all ${
                index === currentStageIndex
                  ? 'w-8 bg-white'
                  : index < currentStageIndex
                  ? 'w-2 bg-white/60'
                  : 'w-2 bg-white/30'
              }`}
              whileHover={{ scale: 1.5 }}
              whileTap={{ scale: 0.9 }}
            />
          ))}
        </div>

        {/* Sound effect markers (for audio integration) */}
        <div className="hidden" data-sound-effect={currentStage.soundEffect} />
      </div>
    </div>
  )
}

// ============================================================================
// STAGE COMPONENTS
// ============================================================================

const IntroStage: React.FC = () => (
  <motion.div className="text-center space-y-8">
    <motion.div
      initial={{ scale: 0, rotate: -180 }}
      animate={{ scale: 1, rotate: 0 }}
      transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
    >
      <Clock className="w-32 h-32 text-white mx-auto mb-6" />
    </motion.div>
    <motion.h2
      className="text-6xl font-bold text-white leading-tight"
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3, duration: 0.6 }}
    >
      Traditional meta-analysis takes
      <br />
      <span className="text-red-400">6-12 months</span>
    </motion.h2>
    <motion.p
      className="text-2xl text-white/80"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.6, duration: 0.6 }}
    >
      Let's change that...
    </motion.p>
  </motion.div>
)

const CreateProjectStage: React.FC = () => (
  <motion.div className="space-y-8">
    <motion.div
      className="max-w-2xl mx-auto p-8 bg-white/10 backdrop-blur-md border border-white/20 rounded-3xl"
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="space-y-4">
        <motion.div
          className="flex items-center gap-3 text-white text-xl"
          initial={{ x: -50, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <div className="w-3 h-3 rounded-full bg-green-400 animate-pulse" />
          <span>Project: "Efficacy of Cognitive Behavioral Therapy"</span>
        </motion.div>
        <motion.div
          className="flex items-center gap-3 text-white/80 text-lg"
          initial={{ x: -50, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          <div className="w-3 h-3 rounded-full bg-blue-400 animate-pulse" />
          <span>Researcher: Dr. Sarah Smith</span>
        </motion.div>
        <motion.div
          className="flex items-center gap-3 text-white/80 text-lg"
          initial={{ x: -50, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.6 }}
        >
          <div className="w-3 h-3 rounded-full bg-purple-400 animate-pulse" />
          <span>AI Agents: Activated</span>
        </motion.div>
      </div>
    </motion.div>
    <motion.div
      className="text-center"
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.8 }}
    >
      <Rocket className="w-20 h-20 text-yellow-300 mx-auto animate-bounce" />
    </motion.div>
  </motion.div>
)

const SearchStage: React.FC = () => {
  const databases = [
    'PubMed', 'Scopus', 'Web of Science', 'PsycINFO', 'CINAHL',
    'Embase', 'Cochrane', 'IEEE Xplore', 'ACM Digital', 'ArXiv'
  ]

  return (
    <div className="space-y-8">
      <motion.div
        className="relative w-32 h-32 mx-auto"
        animate={{ rotate: 360 }}
        transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
      >
        <Database className="w-32 h-32 text-white" />
        <motion.div
          className="absolute inset-0 border-8 border-white/30 border-t-white rounded-full"
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        />
      </motion.div>

      <div className="grid grid-cols-5 gap-4 max-w-4xl mx-auto">
        {databases.map((db, i) => (
          <motion.div
            key={db}
            className="p-4 bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl text-center"
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.15, duration: 0.3 }}
          >
            <Search className="w-6 h-6 text-white mx-auto mb-2" />
            <div className="text-white text-sm font-medium">{db}</div>
            <motion.div
              className="mt-2 text-green-400 text-xs"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: i * 0.15 + 0.5 }}
            >
              ✓ Searching
            </motion.div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

const PapersFlowStage: React.FC = () => {
  const paperCount = 24

  return (
    <div className="relative h-[600px]">
      <motion.div
        className="text-center mb-8"
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ duration: 0.5, type: 'spring' }}
      >
        <div className="text-8xl font-bold text-white">2,847</div>
        <div className="text-3xl text-white/80">Papers Found!</div>
      </motion.div>

      <div className="grid grid-cols-8 gap-3">
        {[...Array(paperCount)].map((_, i) => (
          <motion.div
            key={i}
            className="aspect-[3/4] bg-white/20 backdrop-blur-sm border border-white/40 rounded-lg p-2"
            initial={{ opacity: 0, y: -100, rotate: -20 }}
            animate={{
              opacity: 1,
              y: 0,
              rotate: 0
            }}
            transition={{
              delay: i * 0.05,
              duration: 0.4,
              ease: [0.22, 1, 0.36, 1]
            }}
            whileHover={{ scale: 1.1, zIndex: 10 }}
          >
            <FileText className="w-full h-full text-white/60" />
          </motion.div>
        ))}
      </div>
    </div>
  )
}

interface ScreeningStageProps {
  playbackSpeed: number
}

const ScreeningStage: React.FC<ScreeningStageProps> = ({ playbackSpeed }) => {
  const [acceptedCount, setAcceptedCount] = useState(0)
  const [rejectedCount, setRejectedCount] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      if (Math.random() > 0.4) {
        setAcceptedCount((prev) => prev + 1)
      } else {
        setRejectedCount((prev) => prev + 1)
      }
    }, 200 / playbackSpeed)

    return () => clearInterval(interval)
  }, [playbackSpeed])

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-2 gap-8 max-w-4xl mx-auto">
        {/* Accepted */}
        <motion.div
          className="p-8 bg-green-500/20 backdrop-blur-sm border-2 border-green-400/40 rounded-3xl text-center"
          animate={{ scale: [1, 1.05, 1] }}
          transition={{ duration: 0.5, repeat: Infinity }}
        >
          <CheckCircle2 className="w-20 h-20 text-green-400 mx-auto mb-4" />
          <div className="text-6xl font-bold text-white mb-2">{acceptedCount}</div>
          <div className="text-2xl text-white/80">Accepted</div>
        </motion.div>

        {/* Rejected */}
        <motion.div
          className="p-8 bg-red-500/20 backdrop-blur-sm border-2 border-red-400/40 rounded-3xl text-center"
          animate={{ scale: [1, 1.05, 1] }}
          transition={{ duration: 0.5, repeat: Infinity, delay: 0.25 }}
        >
          <XCircle className="w-20 h-20 text-red-400 mx-auto mb-4" />
          <div className="text-6xl font-bold text-white mb-2">{rejectedCount}</div>
          <div className="text-2xl text-white/80">Rejected</div>
        </motion.div>
      </div>

      {/* Stamps animation */}
      <div className="flex justify-center gap-8">
        <motion.div
          className="relative"
          variants={stampAnimation}
          initial="initial"
          animate="animate"
        >
          <div className="text-6xl font-bold text-green-400 border-8 border-green-400 rounded-xl px-8 py-4 rotate-12 opacity-80">
            ACCEPTED
          </div>
        </motion.div>
        <motion.div
          className="relative"
          variants={stampAnimation}
          initial="initial"
          animate="animate"
          transition={{ delay: 0.3 }}
        >
          <div className="text-6xl font-bold text-red-400 border-8 border-red-400 rounded-xl px-8 py-4 -rotate-12 opacity-80">
            REJECTED
          </div>
        </motion.div>
      </div>

      {/* Accuracy indicator */}
      <motion.div
        className="text-center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1 }}
      >
        <div className="inline-flex items-center gap-3 px-6 py-3 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full">
          <Target className="w-6 h-6 text-yellow-400" />
          <span className="text-xl font-bold text-white">99.2% Accuracy</span>
        </div>
      </motion.div>
    </div>
  )
}

const ExtractionStage: React.FC = () => {
  const dataFields = [
    'Sample Size',
    'Effect Size',
    'P-Value',
    'Confidence Interval',
    'Study Design',
    'Population',
    'Intervention',
    'Outcome Measures'
  ]

  return (
    <div className="space-y-8">
      <motion.div
        className="relative w-32 h-32 mx-auto"
        animate={{ rotate: [0, 360] }}
        transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
      >
        <Brain className="w-32 h-32 text-white" />
        <motion.div
          className="absolute inset-0 border-4 border-dashed border-white/40 rounded-full"
          animate={{ rotate: [360, 0] }}
          transition={{ duration: 4, repeat: Infinity, ease: 'linear' }}
        />
      </motion.div>

      <div className="grid grid-cols-2 gap-4 max-w-3xl mx-auto">
        {dataFields.map((field, i) => (
          <motion.div
            key={field}
            className="flex items-center gap-3 p-4 bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl"
            initial={{ opacity: 0, x: i % 2 === 0 ? -50 : 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.2, duration: 0.4 }}
          >
            <motion.div
              className="flex-shrink-0 w-6 h-6 rounded-full border-2 border-white/40"
              animate={{
                borderColor: ['rgba(255,255,255,0.4)', 'rgba(34,197,94,1)'],
                backgroundColor: ['transparent', 'rgba(34,197,94,0.5)']
              }}
              transition={{ delay: i * 0.2 + 0.5, duration: 0.3 }}
            >
              <motion.div
                className="w-full h-full rounded-full bg-green-400"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: i * 0.2 + 0.7, duration: 0.2 }}
              />
            </motion.div>
            <span className="text-white font-medium">{field}</span>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

const AnalysisStage: React.FC = () => {
  return (
    <div className="space-y-8">
      <motion.div
        className="max-w-4xl mx-auto p-8 bg-white/10 backdrop-blur-sm border border-white/20 rounded-3xl"
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
      >
        {/* Animated chart bars */}
        <div className="space-y-6">
          {[
            { label: 'Forest Plot', value: 85, color: 'bg-blue-400' },
            { label: 'Funnel Plot', value: 72, color: 'bg-green-400' },
            { label: 'Meta-Regression', value: 93, color: 'bg-purple-400' },
            { label: 'Subgroup Analysis', value: 67, color: 'bg-yellow-400' }
          ].map((item, i) => (
            <motion.div key={item.label} className="space-y-2">
              <div className="flex items-center justify-between text-white">
                <span className="font-medium">{item.label}</span>
                <span className="text-white/60">{item.value}%</span>
              </div>
              <div className="h-8 bg-white/10 rounded-full overflow-hidden">
                <motion.div
                  className={`h-full ${item.color} rounded-full`}
                  initial={{ width: 0 }}
                  animate={{ width: `${item.value}%` }}
                  transition={{ delay: i * 0.3, duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
                />
              </div>
            </motion.div>
          ))}
        </div>

        {/* Chart icon */}
        <motion.div
          className="mt-8 text-center"
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 1.5, duration: 0.5 }}
        >
          <BarChart3 className="w-24 h-24 text-white mx-auto" />
        </motion.div>
      </motion.div>
    </div>
  )
}

const ReportStage: React.FC = () => {
  return (
    <motion.div
      className="max-w-3xl mx-auto"
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <motion.div
        className="p-12 bg-white/10 backdrop-blur-sm border border-white/20 rounded-3xl space-y-6"
        animate={{
          boxShadow: [
            '0 0 0 0 rgba(255,255,255,0)',
            '0 0 0 20px rgba(255,255,255,0.1)',
            '0 0 0 0 rgba(255,255,255,0)'
          ]
        }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        <motion.div
          className="flex items-center justify-center"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', duration: 0.6 }}
        >
          <FileCheck className="w-32 h-32 text-green-400" />
        </motion.div>

        <div className="space-y-4 text-white">
          <motion.div
            className="flex items-center gap-3"
            initial={{ x: -50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            <CheckCircle2 className="w-6 h-6 text-green-400" />
            <span className="text-xl">Abstract & Introduction</span>
          </motion.div>
          <motion.div
            className="flex items-center gap-3"
            initial={{ x: -50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            <CheckCircle2 className="w-6 h-6 text-green-400" />
            <span className="text-xl">Methods & Analysis</span>
          </motion.div>
          <motion.div
            className="flex items-center gap-3"
            initial={{ x: -50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.7 }}
          >
            <CheckCircle2 className="w-6 h-6 text-green-400" />
            <span className="text-xl">Results & Discussion</span>
          </motion.div>
          <motion.div
            className="flex items-center gap-3"
            initial={{ x: -50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.9 }}
          >
            <CheckCircle2 className="w-6 h-6 text-green-400" />
            <span className="text-xl">References & Appendices</span>
          </motion.div>
        </div>

        <motion.div
          className="pt-6 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
        >
          <div className="inline-flex items-center gap-2 px-6 py-3 bg-green-500/20 border border-green-400/40 rounded-full">
            <Sparkles className="w-5 h-5 text-green-400" />
            <span className="text-xl font-bold text-white">Publication Ready!</span>
          </div>
        </motion.div>
      </motion.div>
    </motion.div>
  )
}

const CelebrationStage: React.FC = () => {
  return (
    <div className="relative">
      {/* Confetti */}
      <div className="absolute inset-0 pointer-events-none">
        {[...Array(50)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute top-1/2 left-1/2 w-4 h-4 rounded-full"
            style={{
              backgroundColor: ['#FFD700', '#FF6B6B', '#4ECDC4', '#95E1D3', '#F38181'][i % 5]
            }}
            custom={i}
            variants={confettiVariants}
            initial="hidden"
            animate="visible"
          />
        ))}
      </div>

      {/* Main content */}
      <motion.div
        className="relative z-10 text-center space-y-8"
        initial={{ scale: 0, rotate: -180 }}
        animate={{ scale: 1, rotate: 0 }}
        transition={{ type: 'spring', duration: 1 }}
      >
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 10, -10, 0]
          }}
          transition={{ duration: 0.6, repeat: Infinity, repeatDelay: 1 }}
        >
          <Trophy className="w-40 h-40 text-yellow-300 mx-auto drop-shadow-2xl" />
        </motion.div>

        <motion.h2
          className="text-7xl font-bold text-white"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          Mission Complete!
        </motion.h2>

        <motion.div
          className="text-5xl text-white/90 space-y-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          <div>
            <span className="line-through text-white/40">6 months</span>
            {' → '}
            <span className="text-green-400 font-bold">3 hours</span>
          </div>
        </motion.div>

        <motion.div
          className="flex items-center justify-center gap-4 text-3xl text-white"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2 }}
        >
          <Zap className="w-10 h-10 text-yellow-400" />
          <span className="font-bold">99.7% Time Saved</span>
          <Zap className="w-10 h-10 text-yellow-400" />
        </motion.div>
      </motion.div>
    </div>
  )
}

const StatsStage: React.FC = () => {
  const stats = [
    { value: '10,000+', label: 'Researchers', icon: Users, color: 'text-blue-400' },
    { value: '50,000+', label: 'Papers Analyzed', icon: FileText, color: 'text-purple-400' },
    { value: '2.5M', label: 'Hours Saved', icon: Clock, color: 'text-green-400' },
    { value: '99.2%', label: 'Accuracy Rate', icon: Target, color: 'text-yellow-400' }
  ]

  return (
    <div className="space-y-12">
      <motion.h2
        className="text-6xl font-bold text-white text-center"
        initial={{ opacity: 0, y: -40 }}
        animate={{ opacity: 1, y: 0 }}
      >
        Join the Revolution
      </motion.h2>

      <div className="grid grid-cols-2 gap-8 max-w-5xl mx-auto">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.label}
            className="p-8 bg-white/10 backdrop-blur-sm border border-white/20 rounded-3xl text-center"
            initial={{ opacity: 0, scale: 0.5, rotate: -20 }}
            animate={{ opacity: 1, scale: 1, rotate: 0 }}
            transition={{ delay: i * 0.2, duration: 0.6, type: 'spring' }}
            whileHover={{ scale: 1.05, y: -10 }}
          >
            <stat.icon className={`w-16 h-16 mx-auto mb-4 ${stat.color}`} />
            <div className="text-6xl font-bold text-white mb-2">{stat.value}</div>
            <div className="text-2xl text-white/80">{stat.label}</div>
          </motion.div>
        ))}
      </div>

      <motion.div
        className="text-center"
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1 }}
      >
        <motion.button
          className="px-12 py-6 bg-gradient-to-r from-blue-600 to-purple-600 text-white text-2xl font-bold rounded-2xl shadow-2xl"
          whileHover={{ scale: 1.1, boxShadow: '0 20px 60px rgba(0,0,0,0.3)' }}
          whileTap={{ scale: 0.95 }}
        >
          <span className="flex items-center gap-3">
            Start Your Free Trial
            <Rocket className="w-8 h-8" />
          </span>
        </motion.button>
      </motion.div>
    </div>
  )
}

export default HighlightDemo
