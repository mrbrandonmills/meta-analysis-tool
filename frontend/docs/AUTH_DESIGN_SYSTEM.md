# Authentication Design System

Museum-quality authentication experience for the Meta-Analysis Research Platform.

## Overview

This authentication system is designed to rival luxury SaaS platforms like Stripe, Linear, and Notion. Every interaction is carefully crafted to delight users while maintaining accessibility and performance standards.

## Visual Hierarchy

### Split-Screen Layout

```
┌─────────────────────────────────────────────┐
│                     │                       │
│                     │                       │
│   Brand Side        │    Form Side          │
│   (Animated)        │    (White Card)       │
│                     │                       │
│                     │                       │
└─────────────────────────────────────────────┘
```

**Desktop (≥1024px):**
- 50/50 split between brand and form
- Brand side: Full-height gradient with animated orbs
- Form side: Centered card with max-width 448px

**Mobile (<768px):**
- Stacked vertical layout
- Brand side collapses to 40vh
- Form side takes remaining space

## Color System

### Primary Theme (Researcher)
```css
Primary Blue:
- 50:  #eff6ff (backgrounds)
- 100: #dbeafe (hover states)
- 600: #2563eb (main actions)
- 700: #1d4ed8 (hover)
- Glow: rgba(37, 99, 235, 0.3)
```

### Accent Theme (Admin)
```css
Accent Purple:
- 50:  #faf5ff (backgrounds)
- 100: #f3e8ff (hover states)
- 600: #9333ea (main actions)
- 700: #7e22ce (hover)
- Glow: rgba(147, 51, 234, 0.3)
```

### Semantic Colors
```css
Success: #16a34a (green-600)
Warning: #ca8a04 (yellow-600)
Error:   #dc2626 (red-600)
Info:    #2563eb (blue-600)
```

## Typography

### Font Stack
```css
Sans-serif: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial
Monospace:  "JetBrains Mono", "Fira Code", Consolas
```

### Type Scale
```
Page Title:     36px / 2.25rem (font-bold)
Section Title:  24px / 1.5rem  (font-semibold)
Card Title:     20px / 1.25rem (font-semibold)
Body:           16px / 1rem    (font-normal)
Caption:        14px / 0.875rem (font-normal)
Fine Print:     12px / 0.75rem (font-normal)
```

### Usage Example
```tsx
<h1 className="text-4xl font-bold text-gray-900">Welcome back</h1>
<p className="text-lg text-gray-600">Sign in to continue</p>
<label className="text-sm font-medium text-gray-700">Email</label>
<span className="text-xs text-gray-500">Optional field</span>
```

## Spacing System

### Base Scale (Tailwind)
```
xs:  4px   (0.25rem)
sm:  8px   (0.5rem)
md:  16px  (1rem)
lg:  24px  (1.5rem)
xl:  32px  (2rem)
2xl: 48px  (3rem)
3xl: 64px  (4rem)
4xl: 96px  (6rem)
```

### Component Spacing
```
Form fields:      20px vertical gap (space-y-5)
Card padding:     32px (p-8)
Button padding:   16px horizontal, 12px vertical (px-4 py-3)
Input padding:    16px horizontal, 16px vertical (px-4 py-4)
Section margins:  32px (mb-8)
```

## Animation System

### Timing Functions
```css
Luxury Easing: cubic-bezier(0.22, 1, 0.36, 1)
Ease Out:      cubic-bezier(0, 0, 0.2, 1)
Spring:        cubic-bezier(0.68, -0.55, 0.265, 1.55)
```

### Duration Scale
```
Fast:    200ms (hover, focus)
Normal:  300ms (transitions)
Slow:    400ms (step changes)
Slower:  600ms (layout shifts)
Slowest: 800ms (page transitions)
```

### Animation Catalog

**1. Floating Label**
```tsx
// Label moves up and shrinks when input is focused or filled
<motion.label
  className={cn(
    formData.email || focusedField === 'email'
      ? "top-2 text-xs"
      : "top-1/2 -translate-y-1/2 text-base"
  )}
/>
```

**2. Glow on Focus**
```tsx
// Input gets themed glow shadow on focus
<div className={cn(
  focusedField === 'email'
    ? "border-primary-600 shadow-glow-primary"
    : "border-gray-200"
)}>
```

**3. Scale on Hover**
```tsx
// Button scales up slightly on hover
<motion.div
  whileHover={{ scale: 1.02 }}
  whileTap={{ scale: 0.98 }}
>
```

**4. Progress Step Transitions**
```tsx
// Multi-step form with slide animation
<motion.div
  initial={{ opacity: 0, x: 20 }}
  animate={{ opacity: 1, x: 0 }}
  exit={{ opacity: 0, x: -20 }}
  transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
>
```

**5. Success Celebration**
```tsx
// Checkmark scales in with spring physics
<motion.div
  initial={{ scale: 0 }}
  animate={{ scale: 1 }}
  transition={{ type: "spring", stiffness: 200 }}
>
  <CheckCircle2 />
</motion.div>
```

**6. Error Shake**
```tsx
// Error message slides down and fades in
<motion.div
  initial={{ opacity: 0, y: -10, height: 0 }}
  animate={{ opacity: 1, y: 0, height: "auto" }}
  exit={{ opacity: 0, y: -10, height: 0 }}
>
```

## Shadows & Depth

### Shadow Scale
```css
soft:   0 2px 15px rgba(0, 0, 0, 0.08)   /* Subtle cards */
medium: 0 4px 20px rgba(0, 0, 0, 0.12)   /* Hover states */
hard:   0 10px 40px rgba(0, 0, 0, 0.2)   /* Modals, auth cards */
```

### Glow Effects
```css
primary-glow: 0 0 20px rgba(37, 99, 235, 0.3)
accent-glow:  0 0 20px rgba(147, 51, 234, 0.3)
```

### Usage
```tsx
// Base card
<div className="bg-white rounded-2xl shadow-hard p-8">

// Hover effect
<div className="shadow-soft hover:shadow-medium transition-shadow">

// Focus glow
<div className="focus-within:shadow-glow-primary">
```

## Interactive States

### Input Field States

**1. Default**
```css
border: 2px solid #e5e7eb (gray-200)
background: white
```

**2. Hover**
```css
border: 2px solid #d1d5db (gray-300)
cursor: text
```

**3. Focus**
```css
border: 2px solid #2563eb (primary-600)
shadow: 0 0 20px rgba(37, 99, 235, 0.3)
outline: none
```

**4. Filled**
```css
label: moves to top-2, text-xs
border: 2px solid #d1d5db (gray-300)
```

**5. Error**
```css
border: 2px solid #dc2626 (red-600)
background: #fef2f2 (red-50)
text: #dc2626 (red-600)
```

**6. Disabled**
```css
opacity: 0.5
cursor: not-allowed
background: #f3f4f6 (gray-100)
```

### Button States

**1. Default**
```css
background: #2563eb (primary-600)
color: white
shadow: 0 2px 15px rgba(0, 0, 0, 0.08)
```

**2. Hover**
```css
background: #1d4ed8 (primary-700)
scale: 1.02
shadow: 0 4px 20px rgba(0, 0, 0, 0.12)
```

**3. Active/Pressed**
```css
scale: 0.98
```

**4. Focus**
```css
ring: 2px solid #2563eb
ring-offset: 2px
```

**5. Loading**
```css
opacity: 0.7
cursor: not-allowed
Spinner animation: 360deg rotation, 1s linear infinite
```

**6. Disabled**
```css
opacity: 0.5
cursor: not-allowed
background: #9ca3af (gray-400)
```

## Micro-Interactions

### 1. Master Admin Toggle
- Background color transition (200ms)
- Switch ball slides left/right (300ms cubic-bezier)
- Icon color fades (200ms)
- Border color animates to accent (300ms)
- Shadow glow appears (300ms)

### 2. Checkbox
- Checkmark scales from 0 to 1 (200ms spring)
- Border color transitions to primary (200ms)
- Background fills with color (200ms)
- Slight bounce on check (spring physics)

### 3. Password Strength Bar
- Width animates from 0% to score% (300ms ease-out)
- Color transitions through red → yellow → blue → green
- Label updates with fade transition (200ms)

### 4. Progress Steps
- Active step scales to 1.1 (200ms)
- Checkmark appears when complete (spring)
- Progress bar fills (400ms cubic-bezier)
- Step number replaced with checkmark icon

### 5. Form Step Transitions
- Current step slides out left (300ms)
- Next step slides in from right (300ms)
- Stagger delay of 50ms between elements
- Opacity fades 0 → 1

## Responsive Behavior

### Breakpoints
```
Mobile:  < 768px   (sm)
Tablet:  768-1024px (md/lg)
Desktop: > 1024px  (xl)
```

### Mobile Adaptations (< 768px)

**Layout:**
- Split-screen becomes stacked vertical
- Brand side: 40vh height, collapsed features
- Form side: 60vh minimum, full width
- Card padding reduced: 24px (p-6)

**Typography:**
- Page title: 30px (down from 36px)
- Section title: 20px (down from 24px)
- Body: 16px (same)

**Inputs:**
- Height: 48px (same - maintains touch target)
- Font size: 16px (prevents iOS zoom)
- Padding: 12px (down from 16px)

**Buttons:**
- Height: 48px (maintains 44px minimum)
- Font size: 16px
- Full width on mobile

**Spacing:**
- Form field gaps: 16px (down from 20px)
- Card padding: 24px (down from 32px)
- Section margins: 24px (down from 32px)

### Touch Interactions

**Minimum Touch Targets:**
- All interactive elements: 44x44px minimum
- Buttons: 48x48px
- Checkboxes: 44x44px (invisible padding)
- Input fields: 48px height

**Touch Feedback:**
- Active state scale: 0.98
- Fast transition: 100ms
- No hover states on touch devices

## Accessibility Features

### Keyboard Navigation
- Tab order follows visual hierarchy
- Focus visible states (ring-2 ring-primary-600)
- Skip to main content link
- Escape key closes modals/alerts

### Screen Readers
- ARIA labels on all form fields
- ARIA descriptions for errors
- ARIA live regions for dynamic content
- Loading states announced

### Color Contrast
- All text meets WCAG AA (4.5:1)
- Large text meets WCAG AA (3:1)
- Focus indicators highly visible
- Error states use both color and icon

### Motion
- Respects prefers-reduced-motion
- Essential animations only
- No motion for users with vestibular disorders

## Performance Optimizations

### CSS
- Use transform and opacity (GPU-accelerated)
- Avoid layout thrashing
- Will-change hints for animations
- Hardware acceleration for smooth 60fps

### JavaScript
- Debounced validation (300ms)
- Throttled scroll handlers (16ms)
- Code splitting for auth pages
- Lazy loaded icons

### Images
- SVG icons for crisp rendering
- Optimized gradients (CSS, not images)
- No background images
- Reduced motion variants

## Component Examples

### Login Form Flow
```
1. User lands on /login
2. Split screen appears (brand + form)
3. Master Admin toggle defaults to OFF
4. User clicks email field
   → Field scales up (1.02)
   → Border glows primary blue
   → Label floats to top
5. User types email
   → Label stays at top
   → Border stays blue while focused
6. User clicks password field
   → Email field border returns to gray
   → Password field glows blue
   → Show/hide icon appears
7. User checks "Remember me"
   → Checkbox animates with spring
   → Checkmark appears
8. User clicks "Sign in"
   → Button shows loading spinner
   → Submit disabled during API call
9a. Success path:
   → Success screen fades in
   → Green checkmark scales in (spring)
   → "Welcome back!" message
   → 1.5s delay
   → Redirect to /dashboard
9b. Error path:
   → Error banner slides down from top
   → Red alert icon
   → Error message displayed
   → Form re-enabled for retry
```

### Signup Form Flow
```
1. User lands on /signup
2. Step 1: Account Type
   → Progress indicator shows 1/3
   → Two large cards (Researcher vs Admin)
   → User clicks "Researcher"
   → Card highlights blue, checkmark appears
   → "Continue" button enabled
   → User clicks Continue
   → Step slides out left, Step 2 slides in right
   → Progress bar fills to 33%

3. Step 2: Credentials
   → Progress indicator shows 2/3
   → Email field appears
   → Password field appears
   → Password strength bar appears
   → User types password
   → Strength bar animates (red → yellow → green)
   → User types confirm password
   → Real-time validation checks match
   → User clicks Continue
   → Validation runs
   → If valid: Step slides to Step 3
   → If invalid: Inline errors appear

4. Step 3: Profile
   → Progress indicator shows 3/3
   → Full name field
   → Institution field
   → Terms checkbox
   → User fills fields
   → User checks Terms
   → Checkbox background fills with color
   → User clicks "Create account"
   → Button shows loading spinner
   → API call made

5a. Success:
   → Success screen fades in
   → Green checkmark scales in
   → "Welcome!" message
   → Redirect to /onboarding

5b. Error:
   → Error banner appears
   → Form stays on Step 3
   → User can fix and retry
```

## File Structure
```
src/
├── components/
│   └── auth/
│       ├── AuthLayout.tsx      # Split-screen container
│       ├── LoginForm.tsx       # Login component
│       ├── SignupForm.tsx      # Multi-step signup
│       └── README.md           # Component docs
├── pages/
│   ├── login.tsx               # Login page
│   └── signup.tsx              # Signup page
├── lib/
│   ├── auth-tokens.ts          # Design tokens
│   └── utils.ts                # Shared utilities
└── docs/
    └── AUTH_DESIGN_SYSTEM.md   # This file
```

## Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- iOS Safari 14+
- Chrome Mobile 90+

## Credits
Design inspired by:
- Stripe Dashboard
- Linear App
- Notion Authentication
- Vercel Dashboard
- Arc Browser

Built with love by Agent 3 - Visual Designer.
