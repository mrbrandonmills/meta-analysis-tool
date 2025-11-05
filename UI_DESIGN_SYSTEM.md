# Academic Research Platform - UI Design System

**Version:** 1.0
**Last Updated:** November 4, 2025
**Status:** Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Design Principles](#design-principles)
3. [Color System](#color-system)
4. [Typography](#typography)
5. [Component Library](#component-library)
6. [Layout Patterns](#layout-patterns)
7. [Tool-Specific Components](#tool-specific-components)
8. [Accessibility](#accessibility)
9. [Responsive Design](#responsive-design)
10. [Dark Mode](#dark-mode)

---

## Overview

The Academic Research Platform UI is designed for researchers, editors, and academics who need powerful tools for literature synthesis, peer review, and research direction. The design emphasizes:

- **Data density** without overwhelming users
- **Professional aesthetics** suitable for academic contexts
- **Fast perceived performance** with optimistic UI updates
- **Clarity and hierarchy** for complex information
- **Accessible** to all users (WCAG 2.1 AA compliant)

### Technology Stack

- **Framework:** Next.js 14 + React 18
- **Language:** TypeScript (strict mode)
- **Styling:** Tailwind CSS 3.3
- **State Management:** Zustand 4.4
- **Animation:** Framer Motion 10
- **Charts:** Recharts 2.10
- **Icons:** Lucide React

---

## Design Principles

### 1. Academic Aesthetic
- Clean, professional appearance
- Subtle shadows and borders
- Generous white space
- Clear visual hierarchy
- Conservative color palette

### 2. Data-Dense but Readable
- Information-rich interfaces
- Scannable layouts
- Progressive disclosure
- Smart defaults
- Collapsible sections for advanced features

### 3. Fast & Responsive
- Skeleton screens during load
- Optimistic UI updates
- Instant feedback
- < 100ms interaction response
- < 2s initial page load

### 4. Trust & Transparency
- Clear agent status indicators
- Complete audit trails
- Confidence scores visible
- Reasoning explanations available
- No hidden "magic"

### 5. Accessible by Default
- Keyboard navigation
- Screen reader support
- High contrast ratios
- Focus indicators
- ARIA labels

---

## Color System

### Primary Palette

```css
/* Blue - Primary Actions, Links */
blue-50:  #eff6ff
blue-100: #dbeafe
blue-500: #3b82f6
blue-600: #2563eb (primary)
blue-700: #1d4ed8

/* Gray - Text, Borders, Backgrounds */
gray-50:  #f9fafb
gray-100: #f3f4f6
gray-300: #d1d5db
gray-500: #6b7280
gray-700: #374151
gray-900: #111827

/* Green - Success, Credibility High */
green-50:  #f0fdf4
green-100: #dcfce7
green-500: #22c55e
green-600: #16a34a

/* Red - Error, Danger, Credibility Very Low */
red-50:  #fef2f2
red-100: #fee2e2
red-500: #ef4444
red-600: #dc2626

/* Yellow - Warning, Credibility Medium */
yellow-50:  #fefce8
yellow-100: #fef9c3
yellow-500: #eab308
yellow-600: #ca8a04

/* Orange - Credibility Low */
orange-50:  #fff7ed
orange-100: #ffedd5
orange-500: #f97316
orange-600: #ea580c
```

### Tool-Specific Colors

```css
/* Tool 1: Meta-Analysis */
tool-meta: blue-600

/* Tool 2: Research Direction */
tool-research: yellow-600

/* Tool 3: Peer Review */
tool-review: purple-600

/* Tool 4: Reviewer Matcher */
tool-matcher: green-600
```

### Semantic Colors

```css
/* Status Colors */
status-draft: gray-500
status-progress: blue-600
status-paused: yellow-600
status-complete: green-600
status-failed: red-600

/* Agent Status */
agent-idle: gray-400
agent-thinking: blue-500 + pulse animation
agent-processing: purple-500
agent-complete: green-500
agent-error: red-500
```

---

## Typography

### Font Stack

```css
/* Primary Font */
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto',
             'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans',
             'Helvetica Neue', sans-serif;

/* Monospace (for code, DOIs, IDs) */
font-family: 'Courier New', Courier, monospace;
```

### Type Scale

```css
/* Headings */
text-4xl: 36px / 40px  /* Page titles */
text-3xl: 30px / 36px  /* Section headers */
text-2xl: 24px / 32px  /* Card titles */
text-xl:  20px / 28px  /* Sub-headers */
text-lg:  18px / 28px  /* Lead text */

/* Body */
text-base: 16px / 24px /* Default body */
text-sm:   14px / 20px /* Secondary text */
text-xs:   12px / 16px /* Labels, captions */
```

### Font Weights

```css
font-normal:    400  /* Body text */
font-medium:    500  /* Emphasized text */
font-semibold:  600  /* Subheadings */
font-bold:      700  /* Headings */
```

### Usage Guidelines

- **Page Titles:** text-4xl, font-bold, text-gray-900
- **Section Headers:** text-2xl, font-semibold, text-gray-900
- **Card Titles:** text-xl, font-semibold, text-gray-900
- **Body Text:** text-base, font-normal, text-gray-700
- **Secondary Text:** text-sm, font-normal, text-gray-600
- **Labels:** text-sm, font-medium, text-gray-700
- **Captions:** text-xs, font-normal, text-gray-500

---

## Component Library

### Buttons

**Location:** `/frontend/src/components/shared/Button.tsx`

**Variants:**
- `primary` - Main actions (blue background)
- `secondary` - Secondary actions (gray background)
- `outline` - Tertiary actions (border only)
- `ghost` - Subtle actions (no background)
- `danger` - Destructive actions (red background)

**Sizes:**
- `sm` - 32px height, text-sm
- `md` - 40px height, text-base (default)
- `lg` - 48px height, text-lg

**States:**
- Default
- Hover (darker shade)
- Focus (ring outline)
- Disabled (50% opacity, no pointer)
- Loading (spinner icon, disabled)

**Usage:**

```tsx
import Button from '@/components/shared/Button';

<Button variant="primary" size="md" loading={false}>
  Click Me
</Button>

<Button
  variant="outline"
  icon={<Plus className="w-4 h-4" />}
>
  Add Item
</Button>
```

---

### Cards

**Location:** `/frontend/src/components/shared/Card.tsx`

**Variants:**
- `default` - White background, rounded
- `bordered` - + border
- `elevated` - + shadow

**Padding:**
- `none` - 0px
- `sm` - 12px
- `md` - 16px (default)
- `lg` - 24px

**Sub-components:**
- `CardHeader` - Title, subtitle, optional action button
- `CardContent` - Main content area
- `CardFooter` - Actions, bottom border

**Usage:**

```tsx
import { Card, CardHeader, CardContent, CardFooter } from '@/components/shared/Card';

<Card variant="bordered" padding="lg" hover>
  <CardHeader
    title="Title"
    subtitle="Subtitle"
    action={<Button>Action</Button>}
  />
  <CardContent>
    <p>Content goes here...</p>
  </CardContent>
  <CardFooter>
    <Button>Save</Button>
  </CardFooter>
</Card>
```

---

### Badges

**Location:** `/frontend/src/components/shared/Badge.tsx`

**Variants:**
- `default` - Gray
- `success` - Green
- `warning` - Yellow
- `danger` - Red
- `info` - Blue
- `purple` - Purple

**Sizes:**
- `sm` - text-xs, compact
- `md` - text-sm (default)
- `lg` - text-base

**Features:**
- Optional dot indicator
- Rounded corners
- Bordered

**Usage:**

```tsx
import Badge from '@/components/shared/Badge';

<Badge variant="success" dot>High Credibility</Badge>
<Badge variant="info" size="sm">3 items</Badge>
```

---

### Agent Status Card

**Location:** `/frontend/src/components/shared/AgentStatusCard.tsx`

**Purpose:** Display real-time agent activity, progress, and status.

**Variants:**
- `compact` - Single line with icon and name
- `expanded` - Full card with progress bar and details

**Features:**
- Status icon (animated when active)
- Progress bar (0-100%)
- ETA display
- Current task description
- Status message

**Usage:**

```tsx
import AgentStatusCard from '@/components/shared/AgentStatusCard';

const progress: AgentProgress = {
  agentName: 'Search Agent',
  status: AgentStatus.PROCESSING,
  currentTask: 'Searching PubMed database...',
  progress: 45,
  eta: 120,
  message: 'Found 234 papers so far'
};

<AgentStatusCard progress={progress} variant="expanded" />
```

---

### Workflow Visualizer

**Location:** `/frontend/src/components/shared/WorkflowVisualizer.tsx`

**Purpose:** Show multi-agent pipeline with step-by-step progress.

**Features:**
- Vertical timeline layout
- Step status icons (pending, in progress, complete, error)
- Progress bars for active steps
- Duration display
- Error messages
- Connector lines between steps

**Usage:**

```tsx
import WorkflowVisualizer from '@/components/shared/WorkflowVisualizer';

<WorkflowVisualizer
  workflows={projectWorkflows}
  currentStep={2}
/>
```

---

### Progress Indicator

**Location:** `/frontend/src/components/shared/ProgressIndicator.tsx`

**Variants:**
- `bar` - Horizontal progress bar
- `circular` - Circular progress ring
- `dots` - Animated loading dots

**Features:**
- Label text
- Percentage display
- ETA countdown
- Color customization
- Size options (sm, md, lg)

**Usage:**

```tsx
import ProgressIndicator from '@/components/shared/ProgressIndicator';

<ProgressIndicator
  progress={67}
  label="Processing studies"
  eta={45}
  variant="bar"
  color="blue"
/>
```

---

### Data Table

**Location:** `/frontend/src/components/shared/DataTable.tsx`

**Purpose:** Display tabular data with sorting, filtering, and search.

**Features:**
- Sortable columns (click header to sort)
- Search/filter functionality
- Pagination (optional)
- Row selection
- Custom cell rendering
- Click handlers for rows
- Empty state message
- Responsive (scrolls horizontally on mobile)

**Usage:**

```tsx
import DataTable from '@/components/shared/DataTable';

const columns = [
  { key: 'title', title: 'Title', sortable: true },
  { key: 'year', title: 'Year', sortable: true, width: '100px' },
  {
    key: 'credibility',
    title: 'Credibility',
    render: (value) => <Badge variant="success">{value}</Badge>
  }
];

<DataTable
  data={papers}
  columns={columns}
  searchable
  searchPlaceholder="Search papers..."
  onRowClick={(paper) => console.log(paper)}
/>
```

---

## Layout Patterns

### Main Layout

**Location:** `/frontend/src/components/layout/Layout.tsx`

**Structure:**
```
┌─────────────────────────────────────┐
│ Sidebar  │  Header                  │
│          ├──────────────────────────┤
│          │                          │
│          │  Main Content            │
│          │                          │
│          │                          │
└──────────┴──────────────────────────┘
```

**Features:**
- Responsive sidebar (drawer on mobile)
- Sticky header
- Breadcrumb navigation
- User profile in sidebar footer
- Tool navigation in sidebar
- Global search in header
- Notifications bell

---

### Sidebar

**Location:** `/frontend/src/components/layout/Sidebar.tsx`

**Navigation Structure:**
- Dashboard
- Projects
- Tools
  - Meta-Analysis
  - Reviewer Matcher
  - Peer Review
  - Research Direction
- Settings

**Features:**
- Active route highlighting
- Icon + text labels
- Collapsible on mobile
- User profile at bottom
- Smooth transitions

---

### Header

**Location:** `/frontend/src/components/layout/Header.tsx`

**Elements:**
- Hamburger menu (mobile)
- Breadcrumbs / Page title
- Global search
- Notifications icon (with count badge)
- User avatar dropdown

**Responsive:**
- Full search bar on desktop
- Collapsed to icon on mobile
- Breadcrumbs hidden on small screens

---

## Tool-Specific Components

### Tool 1: Meta-Analysis

#### Search Form
**Location:** `/frontend/src/components/tools/meta-analysis/SearchForm.tsx`

**Features:**
- Research question input
- Topic input
- Dynamic inclusion/exclusion criteria
- Database selection (checkboxes with descriptions)
- Peer-review-only toggle

#### Study Screening Table
**Features:**
- Paper title, authors, year, journal
- Include/Exclude/Uncertain buttons
- Bulk actions
- Credibility scores
- Export to CSV

#### PRISMA Flow Diagram
**Features:**
- Interactive SVG diagram
- Click sections to drill down
- Exclusion reasons breakdown
- Export as PNG/PDF

#### Statistical Results Dashboard
**Features:**
- Forest plot visualization
- Funnel plot for publication bias
- Heterogeneity metrics (I², τ²)
- Effect size with confidence intervals
- Subgroup analysis tables

---

### Tool 4: Reviewer Matcher

#### Manuscript Upload
**Features:**
- Drag-and-drop PDF upload
- Title, abstract, keywords input
- Auto-extract metadata

#### Reviewer Recommendation List
**Features:**
- Ranked list with scores
- Expertise match visualization (tags)
- Availability indicator (traffic light)
- Conflict warnings (if any)
- Profile cards with H-index, publications

#### Match Score Visualization
**Features:**
- Radar chart showing expertise, availability, diversity
- Breakdown of score components
- Explanation text for each score

#### Outreach Tracking
**Features:**
- Invitation status (sent, accepted, declined)
- Response time tracking
- Follow-up reminders
- Email templates

---

### Tool 3: Peer Review

#### Manuscript Quality Screener
**Features:**
- Upload manuscript
- Auto-generated quality score
- Strengths/weaknesses list
- Desk-reject recommendation

#### Review Draft Editor
**Features:**
- Section-by-section comments
- Overall assessment
- Recommendation dropdown (accept, minor, major, reject)
- Constructive feedback suggestions
- Bias detection warnings

#### Editor Summary View
**Features:**
- All reviews side-by-side
- Consensus/disagreement highlighting
- Recommendation aggregation
- Decision support

---

### Tool 2: Research Direction

#### Publication Import
**Features:**
- ORCID login
- Manual publication entry
- CSV import
- Auto-populate from ORCID

#### Gap Matrix Display
**Features:**
- 2D matrix (populations × interventions)
- Color-coded cells (studied, understudied, unstudied)
- Click cell to see related papers
- Export matrix

#### Research Proposal Generator
**Features:**
- Step-by-step wizard
- Auto-populated sections (background, significance)
- Editable text areas
- Format selection (NIH, NSF, general)
- Export to Word/PDF

---

## Accessibility

### WCAG 2.1 AA Compliance

**Color Contrast:**
- Text: minimum 4.5:1 contrast ratio
- Large text: minimum 3:1 contrast ratio
- UI elements: minimum 3:1 contrast ratio

**Keyboard Navigation:**
- All interactive elements focusable
- Tab order follows visual order
- Escape key closes modals/dropdowns
- Enter/Space activates buttons
- Arrow keys navigate lists/menus

**Screen Readers:**
- All images have alt text
- Icons have aria-labels
- Form inputs have labels
- Tables have proper headers
- ARIA landmarks used

**Focus Indicators:**
- 2px blue ring on focus
- Visible on all interactive elements
- Never removed with CSS

**Semantic HTML:**
- Proper heading hierarchy (h1, h2, h3...)
- Landmarks (header, nav, main, footer)
- Lists for navigation
- Buttons (not divs) for actions

---

## Responsive Design

### Breakpoints

```css
sm:  640px   /* Small tablets */
md:  768px   /* Tablets */
lg:  1024px  /* Small desktops */
xl:  1280px  /* Desktops */
2xl: 1536px  /* Large desktops */
```

### Layout Behavior

**Mobile (< 768px):**
- Sidebar becomes drawer (overlay)
- Single column layouts
- Stacked cards
- Compact headers
- Bottom action buttons

**Tablet (768px - 1024px):**
- 2-column grids
- Sidebar visible but narrow
- Compact data tables

**Desktop (> 1024px):**
- Full sidebar (256px)
- 3-4 column grids
- Generous spacing
- Full-featured tables

### Component Responsiveness

- **Buttons:** Full-width on mobile, auto on desktop
- **Cards:** Stack on mobile, grid on desktop
- **Tables:** Scroll horizontally on mobile
- **Modals:** Full-screen on mobile, centered on desktop
- **Sidebar:** Drawer on mobile, fixed on desktop

---

## Dark Mode

**Status:** Planned for v1.1

**Approach:**
- Tailwind dark mode with `class` strategy
- Toggle in user settings
- Saved to localStorage
- System preference detection

**Color Adjustments:**
- Invert grayscale
- Reduce saturation slightly
- Maintain contrast ratios
- Adjust shadows

---

## Performance Budget

### Metrics

- **First Contentful Paint (FCP):** < 1.5s
- **Largest Contentful Paint (LCP):** < 2.0s
- **Time to Interactive (TTI):** < 3.0s
- **Cumulative Layout Shift (CLS):** < 0.1
- **Total Blocking Time (TBT):** < 200ms

### Optimization Strategies

1. **Code Splitting:**
   - Tool-specific components lazy-loaded
   - Route-based splitting
   - Dynamic imports for heavy components

2. **Image Optimization:**
   - Next.js Image component
   - WebP format with fallbacks
   - Lazy loading below the fold
   - Responsive srcsets

3. **Bundle Size:**
   - Tree-shaking unused code
   - Analyze bundle with webpack-bundle-analyzer
   - Target: < 200KB initial JS

4. **Caching:**
   - Static assets cached for 1 year
   - API responses cached in React Query
   - Service worker for offline support

5. **Rendering:**
   - Server-side rendering (SSR) for initial page
   - Static generation (SSG) for docs
   - Incremental static regeneration (ISR) for data

---

## Component Development Checklist

When creating a new component, ensure:

- [ ] TypeScript interfaces exported
- [ ] Props documented with JSDoc
- [ ] Variants/sizes supported
- [ ] Responsive behavior defined
- [ ] Accessibility tested
  - [ ] Keyboard navigation works
  - [ ] Screen reader friendly
  - [ ] Color contrast sufficient
  - [ ] Focus indicators visible
- [ ] Loading states handled
- [ ] Error states handled
- [ ] Empty states designed
- [ ] Hover states defined
- [ ] Dark mode colors (if enabled)
- [ ] Storybook story created
- [ ] Unit tests written
- [ ] E2E tests for critical flows

---

## Design Tokens

For consistency, use these design tokens throughout the app:

```typescript
// Spacing
spacing = {
  xs: '0.25rem',   // 4px
  sm: '0.5rem',    // 8px
  md: '1rem',      // 16px
  lg: '1.5rem',    // 24px
  xl: '2rem',      // 32px
  '2xl': '3rem',   // 48px
}

// Border Radius
borderRadius = {
  sm: '0.25rem',   // 4px
  md: '0.5rem',    // 8px
  lg: '0.75rem',   // 12px
  xl: '1rem',      // 16px
  full: '9999px',  // circular
}

// Shadows
shadows = {
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
}

// Transitions
transitions = {
  fast: '150ms ease-in-out',
  base: '200ms ease-in-out',
  slow: '300ms ease-in-out',
}
```

---

## Resources

### Internal Files

- `/frontend/src/lib/types.ts` - TypeScript type definitions
- `/frontend/src/lib/utils.ts` - Utility functions
- `/frontend/src/stores/` - Zustand state stores
- `/frontend/src/components/shared/` - Reusable components
- `/frontend/src/components/layout/` - Layout components
- `/frontend/src/components/tools/` - Tool-specific components

### External Resources

- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Lucide Icons](https://lucide.dev/)
- [Recharts Examples](https://recharts.org/en-US/examples)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Framer Motion Docs](https://www.framer.com/motion/)

---

## Changelog

### Version 1.0 (November 4, 2025)
- Initial design system documentation
- Complete component library
- All 4 tools' UI components
- Accessibility guidelines
- Responsive design patterns

---

**Maintained by:** Frontend Team
**Questions?** Contact the development team or consult the component showcase at `/design-system`.
