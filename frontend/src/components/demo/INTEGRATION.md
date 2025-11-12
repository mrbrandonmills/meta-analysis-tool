# Highlight Demo - Integration Guide

## Quick Start

### 1. Basic Page Integration

Create a dedicated demo page:

```tsx
// app/demo/page.tsx
'use client'

import { HighlightDemo } from '@/components/demo/HighlightDemo'

export default function DemoPage() {
  return (
    <main className="w-full h-screen bg-black">
      <HighlightDemo autoPlay={true} />
    </main>
  )
}
```

### 2. Homepage Hero Integration

Add to homepage after the hero section:

```tsx
// app/page.tsx
'use client'

import Hero from '@/components/landing/Hero'
import { HighlightDemo } from '@/components/demo/HighlightDemo'

export default function Home() {
  return (
    <>
      {/* Existing hero */}
      <Hero />

      {/* Demo section */}
      <section id="demo" className="relative h-screen">
        <HighlightDemo autoPlay={false} />
      </section>

      {/* Rest of homepage... */}
    </>
  )
}
```

### 3. Modal/Overlay Integration

Show demo in a full-screen overlay:

```tsx
// components/landing/DemoModal.tsx
'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X } from 'lucide-react'
import { HighlightDemo } from '@/components/demo/HighlightDemo'

export function DemoModal() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      {/* Trigger button */}
      <button
        onClick={() => setIsOpen(true)}
        className="px-8 py-4 bg-primary-600 text-white rounded-xl font-semibold"
      >
        Watch Demo
      </button>

      {/* Modal */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              className="fixed inset-0 bg-black/90 backdrop-blur-sm z-50"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
            />

            {/* Demo container */}
            <motion.div
              className="fixed inset-0 z-50 p-4 md:p-8"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.3 }}
            >
              {/* Close button */}
              <button
                onClick={() => setIsOpen(false)}
                className="absolute top-8 right-8 z-10 p-3 bg-white/10 backdrop-blur-md border border-white/20 rounded-full hover:bg-white/20 transition-colors"
              >
                <X className="w-6 h-6 text-white" />
              </button>

              {/* Demo */}
              <div className="w-full h-full rounded-3xl overflow-hidden shadow-2xl">
                <HighlightDemo
                  autoPlay={true}
                  onComplete={() => {
                    setTimeout(() => setIsOpen(false), 2000)
                  }}
                />
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  )
}
```

---

## Homepage Integration Options

### Option A: Inline Section (Recommended)

Best for maximum visibility and engagement.

```tsx
// app/page.tsx
import Hero from '@/components/landing/Hero'
import { HighlightDemo } from '@/components/demo/HighlightDemo'
import Features from '@/components/landing/Features'

export default function Home() {
  return (
    <>
      <Hero />

      {/* Demo section with context */}
      <section className="relative">
        {/* Intro text */}
        <div className="max-w-7xl mx-auto px-4 py-16 text-center">
          <h2 className="text-5xl font-bold text-gray-900 mb-4">
            See It In Action
          </h2>
          <p className="text-xl text-gray-600">
            Watch how AI transforms months of work into hours
          </p>
        </div>

        {/* Full-width demo */}
        <div className="h-screen">
          <HighlightDemo />
        </div>
      </section>

      <Features />
    </>
  )
}
```

### Option B: Click-to-Reveal Section

Lower commitment, user-initiated.

```tsx
// app/page.tsx
'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Play } from 'lucide-react'

export default function Home() {
  const [showDemo, setShowDemo] = useState(false)

  return (
    <>
      <Hero />

      <section className="relative min-h-screen flex items-center justify-center">
        {!showDemo ? (
          <motion.div
            className="text-center"
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-6xl font-bold text-gray-900 mb-6">
              Experience the Future
            </h2>
            <p className="text-2xl text-gray-600 mb-12 max-w-2xl mx-auto">
              See how AI agents complete a full meta-analysis in real-time
            </p>
            <motion.button
              onClick={() => setShowDemo(true)}
              className="group px-12 py-6 bg-gradient-to-r from-blue-600 to-purple-600 text-white text-xl font-bold rounded-2xl shadow-2xl"
              whileHover={{ scale: 1.05, boxShadow: '0 20px 60px rgba(0,0,0,0.3)' }}
              whileTap={{ scale: 0.95 }}
            >
              <span className="flex items-center gap-3">
                <Play className="w-8 h-8" />
                Watch the Highlight Reel
              </span>
            </motion.button>
          </motion.div>
        ) : (
          <div className="w-full h-screen">
            <HighlightDemo autoPlay={true} />
          </div>
        )}
      </section>
    </>
  )
}
```

### Option C: Sticky Navigation Link

Demo accessible from anywhere on homepage.

```tsx
// components/navigation/Navbar.tsx
'use client'

import { useState } from 'react'
import { Video } from 'lucide-react'
import { DemoModal } from '@/components/landing/DemoModal'

export function Navbar() {
  const [showDemo, setShowDemo] = useState(false)

  return (
    <>
      <nav className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <Logo />

          <div className="flex items-center gap-6">
            <NavLinks />

            {/* Demo button in nav */}
            <button
              onClick={() => setShowDemo(true)}
              className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              <Video className="w-4 h-4" />
              <span>Demo</span>
            </button>
          </div>
        </div>
      </nav>

      {/* Demo modal */}
      {showDemo && (
        <DemoModal onClose={() => setShowDemo(false)} />
      )}
    </>
  )
}
```

---

## Advanced Integrations

### Auto-play on Scroll (Intersection Observer)

Demo starts when user scrolls to it:

```tsx
'use client'

import { useEffect, useRef, useState } from 'react'
import { HighlightDemo } from '@/components/demo/HighlightDemo'

export function AutoPlayDemoSection() {
  const [shouldPlay, setShouldPlay] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !shouldPlay) {
          setShouldPlay(true)
        }
      },
      { threshold: 0.5 }
    )

    if (ref.current) {
      observer.observe(ref.current)
    }

    return () => observer.disconnect()
  }, [shouldPlay])

  return (
    <section ref={ref} className="h-screen">
      {shouldPlay && <HighlightDemo autoPlay={true} />}
    </section>
  )
}
```

### With Analytics Tracking

Track demo engagement:

```tsx
'use client'

import { HighlightDemo } from '@/components/demo/HighlightDemo'

export function TrackedDemo() {
  const handleComplete = () => {
    // Track completion
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'demo_completed', {
        event_category: 'engagement',
        event_label: 'highlight_demo'
      })
    }

    // Redirect to signup
    window.location.href = '/onboarding/researcher'
  }

  const handlePlay = () => {
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'demo_started', {
        event_category: 'engagement',
        event_label: 'highlight_demo'
      })
    }
  }

  return (
    <HighlightDemo
      onComplete={handleComplete}
      // Track play via custom hook or context
    />
  )
}
```

### With Personalization

Show different versions to different users:

```tsx
'use client'

import { useUser } from '@/hooks/useUser'
import { HighlightDemo } from '@/components/demo/HighlightDemo'

export function PersonalizedDemo() {
  const { user, userType } = useUser()

  return (
    <section className="h-screen">
      <div className="absolute top-8 left-8 z-20 bg-white/10 backdrop-blur-md border border-white/20 rounded-xl px-6 py-3">
        <p className="text-white text-lg">
          {user ? `Welcome back, ${user.name}!` : 'Welcome!'}
        </p>
        <p className="text-white/70 text-sm">
          {userType === 'researcher'
            ? 'See how we help researchers like you'
            : 'Discover the power of AI research tools'
          }
        </p>
      </div>

      <HighlightDemo autoPlay={true} />
    </section>
  )
}
```

---

## CTA Integration Patterns

### End-of-Demo CTA Overlay

Show call-to-action after completion:

```tsx
'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { HighlightDemo } from '@/components/demo/HighlightDemo'
import { Rocket, ArrowRight } from 'lucide-react'

export function DemoWithCTA() {
  const [showCTA, setShowCTA] = useState(false)

  return (
    <div className="relative h-screen">
      <HighlightDemo
        onComplete={() => {
          setTimeout(() => setShowCTA(true), 1000)
        }}
      />

      {/* CTA Overlay */}
      <AnimatePresence>
        {showCTA && (
          <motion.div
            className="absolute inset-0 bg-black/80 backdrop-blur-xl z-50 flex items-center justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              className="max-w-2xl mx-auto text-center p-12"
              initial={{ scale: 0.8, y: 40 }}
              animate={{ scale: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.5 }}
            >
              <motion.div
                className="mb-8"
                animate={{
                  scale: [1, 1.2, 1],
                  rotate: [0, 10, -10, 0]
                }}
                transition={{ duration: 0.6, repeat: Infinity, repeatDelay: 2 }}
              >
                <Rocket className="w-24 h-24 text-white mx-auto" />
              </motion.div>

              <h2 className="text-5xl font-bold text-white mb-6">
                Ready to Save Months?
              </h2>
              <p className="text-2xl text-white/80 mb-12">
                Join 10,000+ researchers using AI to accelerate their work
              </p>

              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <motion.button
                  className="px-12 py-6 bg-gradient-to-r from-blue-600 to-purple-600 text-white text-xl font-bold rounded-2xl shadow-2xl"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => window.location.href = '/onboarding/researcher'}
                >
                  <span className="flex items-center gap-3">
                    Start Free Trial
                    <ArrowRight className="w-6 h-6" />
                  </span>
                </motion.button>

                <motion.button
                  className="px-12 py-6 bg-white/10 border-2 border-white/40 text-white text-xl font-bold rounded-2xl"
                  whileHover={{ scale: 1.05, backgroundColor: 'rgba(255,255,255,0.2)' }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setShowCTA(false)}
                >
                  Watch Again
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
```

---

## Mobile Optimizations

### Responsive Demo Container

```tsx
'use client'

import { HighlightDemo } from '@/components/demo/HighlightDemo'

export function ResponsiveDemo() {
  return (
    <section className="relative w-full">
      {/* Mobile: Shorter height, simplified controls */}
      <div className="h-[80vh] md:h-screen">
        <HighlightDemo />
      </div>

      {/* Mobile-specific CTA below demo */}
      <div className="md:hidden p-8 bg-gradient-to-b from-black to-gray-900 text-center">
        <h3 className="text-2xl font-bold text-white mb-4">
          Ready to get started?
        </h3>
        <button className="w-full px-8 py-4 bg-blue-600 text-white rounded-xl font-semibold">
          Start Free Trial
        </button>
      </div>
    </section>
  )
}
```

---

## Testing Checklist

Before deploying the demo:

- [ ] Test on Chrome, Firefox, Safari
- [ ] Test on mobile (iOS, Android)
- [ ] Test on different screen sizes
- [ ] Verify all animations at 60fps
- [ ] Check accessibility (keyboard navigation, screen readers)
- [ ] Test with slow network (demo should still work)
- [ ] Verify analytics tracking works
- [ ] Test CTA conversions
- [ ] Check reduced motion preference
- [ ] Load testing (multiple simultaneous users)

---

## Performance Monitoring

Track demo performance:

```tsx
'use client'

import { useEffect } from 'react'
import { HighlightDemo } from '@/components/demo/HighlightDemo'

export function MonitoredDemo() {
  useEffect(() => {
    // Performance observer
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        console.log('Animation frame time:', entry.duration)

        if (entry.duration > 16.67) {
          console.warn('Frame drop detected:', entry)
        }
      }
    })

    observer.observe({ entryTypes: ['measure'] })

    return () => observer.disconnect()
  }, [])

  return <HighlightDemo />
}
```

---

## Troubleshooting

### Issue: Demo not loading

**Solution**: Ensure Framer Motion is installed and demo is client-side rendered:

```tsx
'use client' // Add this at top of file
```

### Issue: Choppy animations

**Solution**: Check for layout thrashing, use GPU-accelerated properties:

```tsx
// ❌ Bad
animate={{ left: 100 }}

// ✅ Good
animate={{ x: 100 }}
```

### Issue: Demo blocking page scroll

**Solution**: Use overflow control:

```tsx
<section className="relative h-screen overflow-hidden">
  <HighlightDemo />
</section>
```

---

## Next Steps

1. Choose integration pattern (inline, modal, or navigation)
2. Add analytics tracking
3. Test on multiple devices
4. Monitor performance metrics
5. A/B test CTA placement
6. Gather user feedback
7. Iterate and optimize

---

## Questions?

Contact:
- **Visual Designer** (Agent 3): Design and animation questions
- **Tech Builder** (Agent 2): Technical integration help
- **Growth Marketer** (Agent 4): Conversion optimization

---

## Quick Deploy Commands

```bash
# Install dependencies (if needed)
npm install framer-motion lucide-react

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run start
```

Enjoy your ESPN-style highlight demo!
