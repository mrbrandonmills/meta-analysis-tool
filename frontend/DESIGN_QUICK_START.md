# Design System Quick Start Guide

**Get up and running with the new design system in 5 minutes**

---

## Installation

No additional packages needed! Everything uses existing dependencies:
- Framer Motion (already installed)
- Tailwind CSS (already configured)
- Lucide React (already installed)

---

## Quick Examples

### 1. Animated Button

```tsx
import Button from '@/components/shared/Button'
import { Plus } from 'lucide-react'

<Button
  variant="primary"
  size="md"
  icon={<Plus />}
  onClick={handleClick}
>
  Create Project
</Button>
```

**Variants:** primary, secondary, outline, ghost, danger
**Sizes:** sm, md, lg

---

### 2. Stats Card

```tsx
import StatsCard from '@/components/dashboard/StatsCard'
import { TrendingUp } from 'lucide-react'

<StatsCard
  title="Total Projects"
  value={42}
  change="+12%"
  changeType="positive"
  icon={TrendingUp}
  color="blue"
/>
```

**Colors:** blue, green, purple, yellow, red

---

### 3. Project Card

```tsx
import ProjectCard from '@/components/dashboard/ProjectCard'
import { Microscope } from 'lucide-react'
import { ProjectStatus } from '@/lib/types'

<ProjectCard
  id="proj_123"
  title="My Meta-Analysis"
  description="Systematic review of 50 studies"
  status={ProjectStatus.IN_PROGRESS}
  icon={Microscope}
  color="blue"
  updatedAt={new Date().toISOString()}
  progress={67}
/>
```

---

### 4. Agent Workflow

```tsx
import AgentPipeline, { AgentState } from '@/components/workflow/AgentPipeline'
import { Search, Filter } from 'lucide-react'

const steps = [
  {
    id: 'search',
    name: 'Search Agent',
    description: 'Searching databases...',
    icon: Search,
    state: AgentState.COMPLETED,
    message: 'Found 234 papers'
  },
  {
    id: 'screening',
    name: 'Screening Agent',
    description: 'Filtering papers...',
    icon: Filter,
    state: AgentState.RUNNING,
    progress: 67,
    eta: 180,
    message: 'Processing...'
  }
]

<AgentPipeline steps={steps} currentStep={1} />
```

**States:** PENDING, RUNNING, COMPLETED, ERROR

---

### 5. Loading States

```tsx
import SkeletonCard from '@/components/loading/SkeletonCard'
import Spinner from '@/components/loading/Spinner'

// Skeleton placeholder
{loading ? (
  <SkeletonCard variant="project" />
) : (
  <ProjectCard {...project} />
)}

// Full screen spinner
<Spinner
  size="lg"
  color="primary"
  text="Loading your data..."
  fullScreen
/>
```

---

### 6. Animated Counter

```tsx
import AnimatedCounter from '@/components/visualizations/AnimatedCounter'

<AnimatedCounter
  value={1234}
  duration={1.5}
  decimals={0}
  prefix="$"
  suffix="M"
/>
```

---

### 7. Progress Ring

```tsx
import ProgressRing from '@/components/visualizations/ProgressRing'

<ProgressRing
  progress={75}
  size={120}
  strokeWidth={8}
  color="#2563eb"
  showPercentage
/>
```

---

### 8. Credibility Badge

```tsx
import CredibilityBadge, { CredibilityLevel } from '@/components/visualizations/CredibilityBadge'

<CredibilityBadge
  level={CredibilityLevel.HIGH}
  score={92}
  showScore
  size="md"
  animated
/>
```

**Levels:** VERY_LOW, LOW, MEDIUM, HIGH

---

### 9. Toast Notifications

```tsx
import { ToastContainer, ToastType } from '@/components/shared/Toast'
import { useState } from 'react'

const [toasts, setToasts] = useState([])

const showToast = () => {
  setToasts([...toasts, {
    id: Date.now().toString(),
    type: ToastType.SUCCESS,
    title: 'Success!',
    message: 'Your project was created',
    duration: 5000,
    onClose: (id) => setToasts(toasts.filter(t => t.id !== id))
  }])
}

// Render container
<ToastContainer toasts={toasts} />
```

---

## Common Patterns

### Animated Card with Hover

```tsx
<motion.div
  className="p-6 rounded-2xl bg-white/60 backdrop-blur-sm border border-gray-200 hover:border-primary-300 shadow-soft hover:shadow-lg transition-all duration-300"
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
  whileHover={{ y: -4, scale: 1.02 }}
>
  {/* Content */}
</motion.div>
```

### Glassmorphism Background

```tsx
<div className="bg-white/70 backdrop-blur-sm border border-white/20">
  {/* Content */}
</div>
```

### Staggered List Animation

```tsx
<motion.div
  initial="hidden"
  animate="visible"
  variants={{
    visible: {
      transition: {
        staggerChildren: 0.1
      }
    }
  }}
>
  {items.map((item, i) => (
    <motion.div
      key={i}
      variants={{
        hidden: { opacity: 0, y: 20 },
        visible: { opacity: 1, y: 0 }
      }}
    >
      {item}
    </motion.div>
  ))}
</motion.div>
```

### Gradient Text

```tsx
<h1 className="bg-gradient-to-r from-primary-600 to-accent-600 bg-clip-text text-transparent">
  Gradient Heading
</h1>
```

---

## Design Tokens

### Colors

```tsx
// Tailwind classes
className="bg-primary-600 text-white"
className="text-accent-500"
className="bg-green-100 text-green-700"
```

### Animations

```tsx
// Built-in animations
className="animate-fade-in"
className="animate-slide-up"
className="animate-scale-in"
className="animate-shimmer"
className="animate-pulse-slow"
```

### Shadows

```tsx
className="shadow-soft"      // Subtle
className="shadow-medium"    // Medium
className="shadow-hard"      // Strong
className="shadow-glow-primary"  // Hover glow
```

### Spacing

```tsx
// 4px base grid
className="p-6"   // 24px padding
className="gap-4" // 16px gap
className="mb-8"  // 32px bottom margin
```

---

## Animation Presets

### Linear's Signature Easing

```tsx
transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
```

### Hover Effects

```tsx
whileHover={{ y: -4, scale: 1.02 }}
whileTap={{ scale: 0.98 }}
```

### Entrance Animation

```tsx
initial={{ opacity: 0, y: 20 }}
animate={{ opacity: 1, y: 0 }}
transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
```

---

## Responsive Breakpoints

```tsx
// Mobile first
className="w-full md:w-1/2 lg:w-1/3"

// Hide on mobile
className="hidden md:block"

// Different layouts
className="flex-col md:flex-row"
```

**Breakpoints:**
- sm: 640px
- md: 768px
- lg: 1024px
- xl: 1280px
- 2xl: 1536px

---

## Accessibility Tips

### Focus Rings

```tsx
className="focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2"
```

### ARIA Labels

```tsx
<button aria-label="Close modal">
  <X className="w-4 h-4" />
</button>
```

### Semantic HTML

```tsx
<main>
  <h1>Page Title</h1>
  <section>
    <h2>Section Title</h2>
  </section>
</main>
```

---

## Performance Tips

### Only Animate Transform & Opacity

```tsx
// Good (GPU accelerated)
animate={{ opacity: 1, y: 0, scale: 1 }}

// Bad (CPU intensive)
animate={{ width: '100%', height: '100%' }}
```

### Lazy Load Heavy Components

```tsx
import dynamic from 'next/dynamic'

const Chart = dynamic(() => import('./Chart'), {
  loading: () => <SkeletonCard variant="stats" />
})
```

### Use Next.js Image

```tsx
import Image from 'next/image'

<Image
  src="/hero.jpg"
  alt="Hero image"
  width={1200}
  height={630}
  priority
/>
```

---

## Need More Help?

- **Full Documentation:** `/frontend/DESIGN_SYSTEM.md`
- **Design Tokens:** `/frontend/src/lib/design-tokens.ts`
- **Example Pages:** `/frontend/src/pages/landing.tsx` and `dashboard-new.tsx`

---

**Happy designing!** 🎨
