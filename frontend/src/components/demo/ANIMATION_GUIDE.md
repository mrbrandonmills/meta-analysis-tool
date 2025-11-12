# Animation Variants Guide

## Overview

This document catalogs all animation variants used in the Highlight Demo component. These variants can be reused throughout the application for consistent, cinematic motion design.

## Core Animation Principles

### Timing
- **Fast** (200ms): Hover effects, button presses
- **Normal** (400-600ms): Card reveals, element transitions
- **Slow** (800-1000ms): Hero sections, page transitions

### Easing
- **Luxury Cubic**: `[0.22, 1, 0.36, 1]` - Primary easing for most animations
- **Spring**: For playful, energetic movements
- **Linear**: For continuous rotations and progress

### Performance
- Only animate `transform` and `opacity` (GPU-accelerated)
- Avoid animating `width`, `height`, `top`, `left`
- Use `will-change` sparingly

---

## Animation Variants Catalog

### 1. Fade In Up

**Use Case**: Main content reveals, cards entering viewport

```typescript
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
```

**Example Usage**:
```tsx
<motion.div
  variants={fadeInUp}
  initial="hidden"
  animate="visible"
  exit="exit"
>
  {content}
</motion.div>
```

---

### 2. Scale In (Pop)

**Use Case**: Buttons, badges, icons appearing

```typescript
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
```

**Example Usage**:
```tsx
<motion.button
  variants={scaleIn}
  initial="hidden"
  animate="visible"
  whileHover={{ scale: 1.1 }}
  whileTap={{ scale: 0.95 }}
>
  Click Me
</motion.button>
```

---

### 3. Slide In (Staggered)

**Use Case**: List items, menu items, grid items

```typescript
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
```

**Example Usage**:
```tsx
{items.map((item, i) => (
  <motion.div
    key={item.id}
    custom={i}
    variants={slideInLeft}
    initial="hidden"
    animate="visible"
  >
    {item.content}
  </motion.div>
))}
```

---

### 4. Stamp Animation

**Use Case**: Status badges, approval stamps, notifications

```typescript
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
```

**Example Usage**:
```tsx
<motion.div
  className="absolute top-4 right-4"
  variants={stampAnimation}
  initial="initial"
  animate="animate"
>
  <div className="px-4 py-2 bg-green-500 text-white font-bold rounded rotate-12">
    APPROVED
  </div>
</motion.div>
```

---

### 5. Confetti Particles

**Use Case**: Celebration moments, success states

```typescript
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
```

**Example Usage**:
```tsx
{[...Array(50)].map((_, i) => (
  <motion.div
    key={i}
    className="absolute w-4 h-4 rounded-full bg-yellow-400"
    custom={i}
    variants={confettiVariants}
    initial="hidden"
    animate="visible"
  />
))}
```

---

### 6. Pulse Glow

**Use Case**: Loading indicators, active states, attention grabbers

```typescript
const pulseGlow = {
  scale: [1, 1.05, 1],
  boxShadow: [
    '0 0 0 0 rgba(59, 130, 246, 0)',
    '0 0 0 20px rgba(59, 130, 246, 0.3)',
    '0 0 0 0 rgba(59, 130, 246, 0)'
  ],
  transition: {
    duration: 2,
    repeat: Infinity,
    ease: 'easeInOut'
  }
}
```

**Example Usage**:
```tsx
<motion.div
  className="w-12 h-12 bg-blue-500 rounded-full"
  animate={pulseGlow}
/>
```

---

### 7. Card Hover Lift

**Use Case**: Interactive cards, clickable elements

```typescript
const cardHoverLift = {
  rest: {
    y: 0,
    scale: 1,
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.12)'
  },
  hover: {
    y: -8,
    scale: 1.02,
    boxShadow: '0 20px 40px rgba(0, 0, 0, 0.2)',
    transition: {
      duration: 0.3,
      ease: [0.22, 1, 0.36, 1]
    }
  }
}
```

**Example Usage**:
```tsx
<motion.div
  className="p-6 bg-white rounded-xl"
  variants={cardHoverLift}
  initial="rest"
  whileHover="hover"
>
  {content}
</motion.div>
```

---

### 8. Cascade (Flying Papers)

**Use Case**: Document flows, item discoveries

```typescript
const cascade = {
  hidden: {
    opacity: 0,
    y: -100,
    rotate: -20,
    scale: 0.8
  },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    rotate: 0,
    scale: 1,
    transition: {
      delay: i * 0.05,
      duration: 0.4,
      ease: [0.22, 1, 0.36, 1]
    }
  })
}
```

**Example Usage**:
```tsx
<div className="grid grid-cols-8 gap-3">
  {papers.map((paper, i) => (
    <motion.div
      key={paper.id}
      custom={i}
      variants={cascade}
      initial="hidden"
      animate="visible"
      whileHover={{ scale: 1.1, zIndex: 10 }}
    >
      <PaperCard paper={paper} />
    </motion.div>
  ))}
</div>
```

---

### 9. Progress Bar Fill

**Use Case**: Loading states, completion tracking

```typescript
const progressFill = (targetWidth: number) => ({
  initial: { width: 0, opacity: 0 },
  animate: {
    width: `${targetWidth}%`,
    opacity: 1,
    transition: {
      duration: 0.8,
      ease: [0.22, 1, 0.36, 1]
    }
  }
})
```

**Example Usage**:
```tsx
<div className="h-8 bg-gray-200 rounded-full overflow-hidden">
  <motion.div
    className="h-full bg-blue-500 rounded-full"
    variants={progressFill(85)}
    initial="initial"
    animate="animate"
  />
</div>
```

---

### 10. Rotating Loader

**Use Case**: Loading spinners, processing indicators

```typescript
const rotatingLoader = {
  animate: {
    rotate: 360
  },
  transition: {
    duration: 2,
    repeat: Infinity,
    ease: 'linear'
  }
}
```

**Example Usage**:
```tsx
<motion.div
  className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full"
  animate={{ rotate: 360 }}
  transition={{
    duration: 1,
    repeat: Infinity,
    ease: 'linear'
  }}
/>
```

---

### 11. Number Counter

**Use Case**: Statistics, metrics, achievements

```tsx
import { useEffect, useState } from 'react'
import { motion, useSpring, useTransform } from 'framer-motion'

function Counter({ value, duration = 2000 }: { value: number; duration?: number }) {
  const [count, setCount] = useState(0)

  useEffect(() => {
    let startTime: number
    let animationFrame: number

    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime
      const progress = Math.min((currentTime - startTime) / duration, 1)

      setCount(Math.floor(progress * value))

      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate)
      }
    }

    animationFrame = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(animationFrame)
  }, [value, duration])

  return (
    <motion.span
      initial={{ opacity: 0, scale: 0.5 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      {count.toLocaleString()}
    </motion.span>
  )
}
```

---

### 12. Typewriter Effect

**Use Case**: Dynamic text reveals, announcements

```tsx
import { motion } from 'framer-motion'

const sentence = "Your meta-analysis is complete!"

const containerVariants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.03
    }
  }
}

const letterVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.2 }
  }
}

function Typewriter({ text }: { text: string }) {
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {text.split('').map((char, i) => (
        <motion.span key={i} variants={letterVariants}>
          {char}
        </motion.span>
      ))}
    </motion.div>
  )
}
```

---

### 13. Parallax Scroll

**Use Case**: Hero sections, immersive backgrounds

```tsx
import { useScroll, useTransform, useSpring } from 'framer-motion'

function ParallaxSection() {
  const { scrollYProgress } = useScroll()
  const y = useSpring(
    useTransform(scrollYProgress, [0, 1], ['0%', '50%']),
    { stiffness: 100, damping: 30 }
  )

  return (
    <motion.div style={{ y }}>
      {/* Background content */}
    </motion.div>
  )
}
```

---

### 14. Magnetic Button

**Use Case**: CTAs, primary actions

```tsx
import { useMotionValue, useSpring, useTransform, motion } from 'framer-motion'
import { useRef } from 'react'

function MagneticButton({ children }: { children: React.ReactNode }) {
  const ref = useRef<HTMLButtonElement>(null)
  const x = useMotionValue(0)
  const y = useMotionValue(0)

  const springX = useSpring(x, { stiffness: 300, damping: 20 })
  const springY = useSpring(y, { stiffness: 300, damping: 20 })

  const handleMouseMove = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (!ref.current) return
    const rect = ref.current.getBoundingClientRect()
    const centerX = rect.left + rect.width / 2
    const centerY = rect.top + rect.height / 2
    x.set((e.clientX - centerX) * 0.3)
    y.set((e.clientY - centerY) * 0.3)
  }

  const handleMouseLeave = () => {
    x.set(0)
    y.set(0)
  }

  return (
    <motion.button
      ref={ref}
      style={{ x: springX, y: springY }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className="px-8 py-4 bg-blue-600 text-white rounded-xl"
    >
      {children}
    </motion.button>
  )
}
```

---

## Combining Animations

### Sequence

Run animations one after another:

```tsx
const sequence = async () => {
  await controls.start({ opacity: 1 })
  await controls.start({ scale: 1.2 })
  await controls.start({ rotate: 360 })
}
```

### Orchestration

Multiple elements, coordinated timing:

```tsx
const orchestration = {
  visible: {
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.3
    }
  }
}

<motion.div variants={orchestration} initial="hidden" animate="visible">
  {items.map(item => (
    <motion.div key={item.id} variants={childVariants}>
      {item.content}
    </motion.div>
  ))}
</motion.div>
```

---

## Performance Best Practices

### 1. Use Transform Instead of Position

```tsx
// ❌ Bad - causes layout recalculation
<motion.div animate={{ left: 100 }} />

// ✅ Good - GPU accelerated
<motion.div animate={{ x: 100 }} />
```

### 2. Batch Updates

```tsx
// ❌ Bad - multiple repaints
animate({ opacity: 1 })
animate({ scale: 1 })

// ✅ Good - single repaint
animate({ opacity: 1, scale: 1 })
```

### 3. Use will-change Sparingly

```tsx
// Only for animations you know will happen
<motion.div style={{ willChange: 'transform' }} />
```

### 4. Exit Animations

```tsx
<AnimatePresence mode="wait">
  <motion.div
    key={id}
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    exit={{ opacity: 0 }}
  />
</AnimatePresence>
```

---

## Testing Animations

### Visual Regression
```bash
npm run test:visual
```

### Performance Testing
```bash
# Use Chrome DevTools Performance panel
# Look for 60fps (16.67ms per frame)
# Check for layout thrashing
```

### Accessibility
```tsx
// Respect prefers-reduced-motion
const shouldAnimate = !window.matchMedia('(prefers-reduced-motion: reduce)').matches

<motion.div
  animate={shouldAnimate ? { opacity: 1 } : {}}
  transition={{ duration: shouldAnimate ? 0.5 : 0 }}
/>
```

---

## Quick Reference Card

| Animation | Use Case | Duration | Easing |
|-----------|----------|----------|--------|
| Fade In Up | Content reveals | 500ms | [0.22, 1, 0.36, 1] |
| Scale In | Popups, badges | 300ms | Spring |
| Slide In | Lists, menus | 400ms | [0.22, 1, 0.36, 1] |
| Stamp | Status changes | 500ms | [0.22, 1, 0.36, 1] |
| Confetti | Celebrations | 1500ms | easeOut |
| Pulse | Loading states | 2000ms | easeInOut |
| Card Hover | Interactive cards | 300ms | [0.22, 1, 0.36, 1] |
| Cascade | Document flows | 400ms | [0.22, 1, 0.36, 1] |

---

## Questions?

Contact Visual Designer (Agent 3) for animation guidance or customization needs.
