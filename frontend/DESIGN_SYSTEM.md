# Design System - Academic Research Platform v2.0

**Museum-quality visual system inspired by Linear, Notion, and Vercel**

Last Updated: November 4, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Design Principles](#design-principles)
3. [Design Tokens](#design-tokens)
4. [Components Library](#components-library)
5. [Animation System](#animation-system)
6. [Glassmorphism & Visual Effects](#glassmorphism--visual-effects)
7. [Responsive Design](#responsive-design)
8. [Accessibility](#accessibility)
9. [Best Practices](#best-practices)

---

## Overview

This design system creates a **jaw-dropping, buttery-smooth interface** that rivals the best modern SaaS products while maintaining academic credibility. Every pixel matters. Every animation delights.

### Technology Stack

- **Framework:** Next.js 14 + React 18 + TypeScript
- **Styling:** Tailwind CSS 3.3 with custom design tokens
- **Animation:** Framer Motion 10 with Linear's signature easing
- **Icons:** Lucide React
- **State:** Zustand
- **Charts:** Recharts

### Key Features

- 60fps animations everywhere
- Glassmorphism with backdrop blur
- Smooth micro-interactions
- Progressive loading states
- Museum-quality aesthetics
- WCAG AA accessibility compliant

---

## Design Principles

### 1. Cinematic Delight

Every interaction feels like a luxury brand experience:
- Smooth 60fps animations
- Signature cubic-bezier easing: `cubic-bezier(0.22, 1, 0.36, 1)`
- Gentle hover states with scale and glow effects
- Staggered animations for visual interest
- Parallax scrolling effects

### 2. Performance-First

Fast is beautiful:
- Optimized bundle size (< 200KB initial JS)
- Skeleton screens for perceived performance
- Optimistic UI updates
- Progressive image loading
- Code splitting by route

### 3. Data-Dense Yet Beautiful

Academic content with visual hierarchy:
- Generous white space (24px baseline grid)
- Clear typography scale
- Color-coded information
- Progressive disclosure
- Scannable layouts

### 4. Trustworthy & Professional

Credibility through design:
- Subtle shadows and borders
- Professional color palette
- Clear visual hierarchy
- Complete transparency (audit trails)
- Explainable AI decisions

### 5. Accessible by Default

Design for everyone:
- WCAG 2.1 AA compliant
- Keyboard navigation
- Screen reader support
- High contrast ratios (4.5:1 minimum)
- Clear focus indicators

---

## Design Tokens

All design tokens are defined in `/frontend/src/lib/design-tokens.ts`

### Color Palette

#### Primary (Academic Blue)
```typescript
primary-50:  #eff6ff  // Lightest tint
primary-600: #2563eb  // Main brand color
primary-950: #172554  // Darkest shade
```

#### Accent (Research Purple)
```typescript
accent-500: #a855f7  // AI/Agent features
accent-600: #9333ea  // Interactive elements
```

#### Tool Colors
```typescript
meta-analysis:      #2563eb (blue)
reviewer-matcher:   #22c55e (green)
peer-review:        #a855f7 (purple)
research-direction: #eab308 (yellow)
```

#### Semantic Colors
```typescript
success: #22c55e  // High credibility, completed
warning: #eab308  // Medium credibility, caution
danger:  #ef4444  // Low credibility, errors
```

### Typography

#### Font Stack
- **Sans:** System font stack for speed and native feel
- **Mono:** JetBrains Mono for code, DOIs, IDs
- **Serif:** Cormorant Garamond for elegant headings (optional)

#### Type Scale
```typescript
text-xs:   12px / 16px  // Labels, captions
text-sm:   14px / 20px  // Secondary text
text-base: 16px / 24px  // Body text
text-lg:   18px / 28px  // Lead text
text-xl:   20px / 28px  // Subheadings
text-2xl:  24px / 32px  // Card titles
text-4xl:  36px / 40px  // Page titles
text-8xl:  96px / 1     // Hero titles
```

#### Font Weights
- **Light (300):** Hero headings
- **Normal (400):** Body text
- **Medium (500):** Emphasized text
- **Semibold (600):** Subheadings
- **Bold (700):** Headings

### Spacing System

4px base grid:
```typescript
1:  4px    6:  24px   14: 56px
2:  8px    8:  32px   16: 64px
3:  12px   10: 40px   20: 80px
4:  16px   12: 48px   24: 96px
```

### Border Radius
```typescript
sm:   4px   // Buttons, badges
base: 8px   // Inputs, small cards
lg:   12px  // Cards
xl:   16px  // Large cards
2xl:  20px  // Hero sections
```

### Shadows
```typescript
soft:   0 2px 15px rgba(0, 0, 0, 0.08)
medium: 0 4px 20px rgba(0, 0, 0, 0.12)
hard:   0 10px 40px rgba(0, 0, 0, 0.2)

// Glow effects (for hover)
glow-primary: 0 0 20px rgba(37, 99, 235, 0.3)
glow-accent:  0 0 20px rgba(168, 85, 247, 0.3)
glow-success: 0 0 20px rgba(34, 197, 94, 0.3)
```

---

## Components Library

### Navigation Components

#### Hero Section
**Location:** `/components/landing/Hero.tsx`

Stunning animated hero with:
- Animated mesh gradient background
- Floating orbs with physics
- Parallax scroll effects
- Animated text reveals
- Smooth CTAs with glow effects

```tsx
import Hero from '@/components/landing/Hero'

<Hero />
```

#### Features Showcase
**Location:** `/components/landing/FeaturesShowcase.tsx`

Feature grid with:
- Staggered card animations
- Hover scale effects
- Icon animations
- Gradient overlays

```tsx
import FeaturesShowcase from '@/components/landing/FeaturesShowcase'

<FeaturesShowcase />
```

### Dashboard Components

#### Stats Card
**Location:** `/components/dashboard/StatsCard.tsx`

Animated metrics card:
```tsx
<StatsCard
  title="Total Projects"
  value={42}
  change="+12%"
  changeType="positive"
  icon={TrendingUp}
  color="blue"
  index={0}
/>
```

Features:
- Smooth entrance animations
- Hover lift effect
- Color-coded variants
- Animated counters
- Change indicators

#### Project Card
**Location:** `/components/dashboard/ProjectCard.tsx`

Interactive project card:
```tsx
<ProjectCard
  id="proj_123"
  title="Meta-Analysis of Mindfulness Studies"
  description="Systematic review of 50+ RCTs"
  status={ProjectStatus.IN_PROGRESS}
  icon={Microscope}
  color="blue"
  updatedAt="2025-11-04T10:00:00Z"
  progress={67}
  index={0}
/>
```

Features:
- Status badges with icons
- Animated progress bars
- Hover reveal effects
- Color-coded by tool type

### Workflow Components

#### Agent Pipeline
**Location:** `/components/workflow/AgentPipeline.tsx`

Animated multi-agent workflow:
```tsx
<AgentPipeline
  steps={[
    {
      id: 'search',
      name: 'Search Agent',
      description: 'Searching databases...',
      icon: Search,
      state: AgentState.RUNNING,
      progress: 67,
      eta: 180,
      message: 'Found 234 papers'
    },
    // ... more steps
  ]}
  currentStep={0}
/>
```

Features:
- Real-time progress tracking
- Animated state transitions
- Pulsing active indicators
- Connector lines with progress
- ETA countdown
- Error/success messages

### Visualization Components

#### Animated Counter
**Location:** `/components/visualizations/AnimatedCounter.tsx`

Spring-animated number transitions:
```tsx
<AnimatedCounter
  value={1234}
  duration={1.5}
  decimals={0}
  prefix="$"
  suffix="M"
/>
```

#### Progress Ring
**Location:** `/components/visualizations/ProgressRing.tsx`

Circular progress indicator:
```tsx
<ProgressRing
  progress={75}
  size={120}
  strokeWidth={8}
  color="#2563eb"
  showPercentage={true}
/>
```

#### Credibility Badge
**Location:** `/components/visualizations/CredibilityBadge.tsx`

Color-coded credibility indicators:
```tsx
<CredibilityBadge
  level={CredibilityLevel.HIGH}
  score={92}
  showScore={true}
  size="md"
  animated={true}
/>
```

### Loading States

#### Skeleton Card
**Location:** `/components/loading/SkeletonCard.tsx`

Shimmer loading placeholders:
```tsx
<SkeletonCard variant="project" />
<SkeletonCard variant="stats" />
<SkeletonCard variant="tool" />
```

Features:
- Shimmer animation
- Multiple variants
- Smooth fade-in

#### Spinner
**Location:** `/components/loading/Spinner.tsx`

Animated loading spinner:
```tsx
<Spinner
  size="md"
  color="primary"
  text="Loading your data..."
  fullScreen={false}
/>
```

### Shared Components

#### Button
**Location:** `/components/shared/Button.tsx`

Fully animated button:
```tsx
<Button
  variant="primary"
  size="md"
  loading={false}
  icon={<Plus />}
  onClick={handleClick}
>
  Create Project
</Button>
```

Variants:
- `primary` - Main actions (blue)
- `secondary` - Secondary actions (gray)
- `outline` - Tertiary actions (border)
- `ghost` - Subtle actions (no bg)
- `danger` - Destructive actions (red)

Features:
- Hover scale (1.02)
- Tap scale (0.98)
- Loading spinner
- Icon support
- Keyboard accessible

#### Toast Notifications
**Location:** `/components/shared/Toast.tsx`

Animated toast messages:
```tsx
<Toast
  id="toast_1"
  type={ToastType.SUCCESS}
  title="Project created!"
  message="Your meta-analysis has been started."
  duration={5000}
  onClose={handleClose}
/>
```

Features:
- 4 types (success, error, warning, info)
- Auto-dismiss with progress bar
- Smooth entrance/exit
- Stacking support

---

## Animation System

### Timing Functions

#### Linear's Signature Easing
```typescript
cubic-bezier(0.22, 1, 0.36, 1)
```
Use for: All transitions, feels buttery smooth

#### Spring Easing
```typescript
cubic-bezier(0.68, -0.55, 0.265, 1.55)
```
Use for: Playful interactions, icon bounces

### Duration Scale

```typescript
fast:    150ms  // Hover states, quick feedback
normal:  200ms  // Standard transitions
base:    300ms  // Card reveals, modals
slow:    400ms  // Hero sections
slower:  600ms  // Page transitions
slowest: 800ms  // Large animations
```

### Framer Motion Presets

#### Fade In
```tsx
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  transition={{ duration: 0.3 }}
/>
```

#### Slide Up
```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
/>
```

#### Scale In
```tsx
<motion.div
  initial={{ opacity: 0, scale: 0.95 }}
  animate={{ opacity: 1, scale: 1 }}
  transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
/>
```

#### Hover Lift
```tsx
<motion.div
  whileHover={{ y: -4, scale: 1.02 }}
  whileTap={{ scale: 0.98 }}
/>
```

#### Stagger Children
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
    />
  ))}
</motion.div>
```

---

## Glassmorphism & Visual Effects

### Glassmorphism

```css
background: rgba(255, 255, 255, 0.7);
backdrop-filter: blur(12px) saturate(180%);
border: 1px solid rgba(255, 255, 255, 0.18);
```

Tailwind classes:
```tsx
className="bg-white/70 backdrop-blur-sm border border-white/20"
```

### Gradient Meshes

Animated background gradients:
```tsx
<div className="bg-gradient-mesh opacity-30 animate-pulse-slow" />
```

Custom gradient:
```typescript
background: radial-gradient(
  at 40% 20%, hsla(216,100%,80%,1) 0px, transparent 50%
),
radial-gradient(
  at 80% 0%, hsla(189,100%,70%,1) 0px, transparent 50%
)
```

### Floating Orbs

Physics-based floating orbs:
```tsx
<motion.div
  className="absolute w-64 h-64 bg-primary-400/20 rounded-full blur-3xl"
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
```

### Shimmer Effect

Loading shimmer:
```tsx
<motion.div
  className="bg-gradient-to-r from-transparent via-white/50 to-transparent"
  animate={{ x: ['-100%', '100%'] }}
  transition={{ duration: 1.5, repeat: Infinity }}
/>
```

Or use Tailwind:
```tsx
className="animate-shimmer bg-[length:200%_100%]"
```

---

## Responsive Design

### Breakpoints

```typescript
sm:  640px   // Small tablets
md:  768px   // Tablets
lg:  1024px  // Small desktops
xl:  1280px  // Desktops
2xl: 1536px  // Large desktops
```

### Mobile-First Approach

```tsx
// Mobile: Full width, stacked
<div className="w-full">

// Tablet: 2 columns
<div className="w-full md:w-1/2">

// Desktop: 3 columns
<div className="w-full md:w-1/2 lg:w-1/3">
```

### Touch Targets

Minimum 44px for touch:
```tsx
<button className="h-11 px-4">
  {/* 44px height */}
</button>
```

---

## Accessibility

### Keyboard Navigation

All interactive elements must be:
- Focusable (tab order)
- Have visible focus rings
- Operable with Enter/Space
- Escapable (modals/dropdowns)

```tsx
className="focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2"
```

### Screen Readers

```tsx
// Add aria-labels
<button aria-label="Close modal">
  <X className="w-4 h-4" />
</button>

// Hide decorative icons
<Icon className="w-5 h-5" aria-hidden="true" />

// Use semantic HTML
<main>
  <h1>Page Title</h1>
  <section>
    <h2>Section Title</h2>
  </section>
</main>
```

### Color Contrast

- Text: 4.5:1 minimum
- Large text: 3:1 minimum
- UI components: 3:1 minimum

Test with: Chrome DevTools Lighthouse

---

## Best Practices

### Component Checklist

Before shipping a component:

- [ ] TypeScript types exported
- [ ] Props documented with JSDoc
- [ ] Responsive on all breakpoints
- [ ] Keyboard accessible
- [ ] Screen reader friendly
- [ ] Color contrast sufficient
- [ ] Hover states defined
- [ ] Loading states included
- [ ] Error states handled
- [ ] Animations at 60fps
- [ ] No layout shift

### Performance Optimization

1. **Use Next.js Image**
   ```tsx
   <Image src="/hero.jpg" alt="Hero" width={1200} height={630} />
   ```

2. **Lazy load heavy components**
   ```tsx
   const Chart = dynamic(() => import('./Chart'), {
     loading: () => <SkeletonCard variant="stats" />
   })
   ```

3. **Optimize animations**
   ```tsx
   // Good: transform and opacity (GPU accelerated)
   animate={{ opacity: 1, y: 0 }}

   // Bad: width, height, top, left (CPU)
   animate={{ width: '100%' }}
   ```

4. **Use will-change sparingly**
   ```css
   .hover-card:hover {
     will-change: transform;
   }
   ```

### Code Style

```tsx
// Good component structure
export const ComponentName: React.FC<Props> = ({
  prop1,
  prop2,
  ...props
}) => {
  // 1. Hooks
  const [state, setState] = useState()

  // 2. Event handlers
  const handleClick = () => {}

  // 3. Render
  return (
    <motion.div
      className="..."
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      {/* Content */}
    </motion.div>
  )
}
```

---

## Resources

### Internal Files

- `/frontend/src/lib/design-tokens.ts` - All design tokens
- `/frontend/tailwind.config.js` - Tailwind configuration
- `/frontend/src/components/**` - Component library
- `/frontend/src/styles/globals.css` - Global styles

### External References

- [Tailwind CSS Docs](https://tailwindcss.com)
- [Framer Motion Docs](https://www.framer.com/motion/)
- [Linear Design](https://linear.app/design) - Inspiration
- [Vercel Design](https://vercel.com/design) - Inspiration
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

---

**Design with excellence. Build with precision. Delight with every pixel.**

Maintained by: Visual Designer Agent
Last Updated: November 4, 2025
