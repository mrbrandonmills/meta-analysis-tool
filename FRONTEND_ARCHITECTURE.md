# Frontend Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE LAYER                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐         │
│  │   Dashboard   │  │  Tool Pages   │  │Design System  │         │
│  │               │  │               │  │   Showcase    │         │
│  │ - Tool Cards  │  │ - Tool 1 (MA) │  │               │         │
│  │ - Stats       │  │ - Tool 2 (RD) │  │ - Components  │         │
│  │ - Projects    │  │ - Tool 3 (PR) │  │ - Examples    │         │
│  │ - Activity    │  │ - Tool 4 (RM) │  │ - Docs        │         │
│  └───────────────┘  └───────────────┘  └───────────────┘         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       LAYOUT COMPONENTS                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                        │
│  │ Sidebar  │  │  Header  │  │  Layout  │                        │
│  │          │  │          │  │          │                        │
│  │ - Nav    │  │ - Search │  │ - Wrapper│                        │
│  │ - Tools  │  │ - Notify │  │ - Main   │                        │
│  │ - Profile│  │ - Bread  │  │ - Content│                        │
│  └──────────┘  └──────────┘  └──────────┘                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     SHARED COMPONENTS LIBRARY                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Core UI:                    Agent System:                         │
│  ┌─────────────┐            ┌──────────────────┐                 │
│  │ Button      │            │ AgentStatusCard  │                 │
│  │ Card        │            │ WorkflowVisualizer│                 │
│  │ Badge       │            │ ProgressIndicator│                 │
│  │ DataTable   │            └──────────────────┘                 │
│  └─────────────┘                                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    TOOL-SPECIFIC COMPONENTS                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Tool 1:           Tool 2:           Tool 3:         Tool 4:       │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐   ┌──────────┐  │
│  │SearchForm│     │GapMatrix │     │ReviewForm│   │MatchList │  │
│  │PrismaFlow│     │TrendChart│     │QualityBar│   │ProfileCrd│  │
│  │ForestPlot│     │ProposalUI│     │EditorView│   │ConflictUI│  │
│  └──────────┘     └──────────┘     └──────────┘   └──────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       STATE MANAGEMENT                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Global State:                Tool-Specific State:                 │
│  ┌──────────────────┐        ┌──────────────────────────┐        │
│  │ useAppStore      │        │ useMetaAnalysisStore     │        │
│  │                  │        │ useReviewerMatcherStore  │        │
│  │ - User/Auth      │        │ usePeerReviewStore       │        │
│  │ - Projects       │        │ useResearchDirectionStore│        │
│  │ - UI State       │        │                          │        │
│  │ - Notifications  │        │ - Agent Progress         │        │
│  │ - Loading/Errors │        │ - Results Cache          │        │
│  └──────────────────┘        │ - Selections             │        │
│                               └──────────────────────────┘        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      TYPE SYSTEM & UTILITIES                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────────────────────────────────────────────────┐       │
│  │ types.ts (400+ lines)                                   │       │
│  │                                                          │       │
│  │ - Core Types (User, Project, Workflow, Agent)           │       │
│  │ - Shared Entities (Paper, Researcher)                   │       │
│  │ - Tool-Specific Types (MetaAnalysisProject, etc.)       │       │
│  │ - UI State Types (DashboardStats, ActivityItem)         │       │
│  │ - API Response Types                                     │       │
│  └────────────────────────────────────────────────────────┘       │
│                                                                     │
│  ┌────────────────────────────────────────────────────────┐       │
│  │ utils.ts                                                 │       │
│  │                                                          │       │
│  │ - Color Mapping (credibility, status)                   │       │
│  │ - Date/Time Formatting                                   │       │
│  │ - Number Formatting                                      │       │
│  │ - Clipboard, Downloads, Debounce                        │       │
│  └────────────────────────────────────────────────────────┘       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      BACKEND INTEGRATION                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  API Layer (Future):                                               │
│  ┌────────────────────────────────────────┐                       │
│  │ React Query / Axios                     │                       │
│  │                                          │                       │
│  │ - FastAPI Backend (localhost:8000)      │                       │
│  │ - WebSocket for real-time updates       │                       │
│  │ - Authentication (JWT)                   │                       │
│  │ - File uploads                           │                       │
│  └────────────────────────────────────────┘                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Hierarchy

```
App
├── Layout
│   ├── Sidebar
│   │   ├── Navigation Links
│   │   ├── Tool Submenu
│   │   └── User Profile
│   │
│   ├── Header
│   │   ├── Hamburger Menu (mobile)
│   │   ├── Breadcrumbs
│   │   ├── Search Bar
│   │   └── Notifications
│   │
│   └── Main Content
│       └── {Page Content}
│
├── Dashboard Page
│   ├── Welcome Banner
│   ├── Stats Cards (3x)
│   ├── Tool Cards (4x)
│   │   ├── Meta-Analysis Card
│   │   ├── Reviewer Matcher Card
│   │   ├── Peer Review Card
│   │   └── Research Direction Card
│   └── Recent Projects List
│
├── Tool Pages
│   ├── Meta-Analysis
│   │   ├── SearchForm
│   │   ├── AgentStatusCards
│   │   ├── WorkflowVisualizer
│   │   ├── Results Dashboard
│   │   └── PRISMA Flow Diagram
│   │
│   ├── Reviewer Matcher
│   │   ├── Manuscript Upload
│   │   ├── Match Progress
│   │   ├── Reviewer List
│   │   └── Profile Cards
│   │
│   ├── Peer Review
│   │   ├── Manuscript Screen
│   │   ├── Review Generator
│   │   └── Editor Summary
│   │
│   └── Research Direction
│       ├── Publication Import
│       ├── Gap Analysis
│       ├── Trend Visualization
│       └── Proposal Generator
│
└── Design System Page
    ├── Color Swatches
    ├── Typography Examples
    ├── Button Showcase
    ├── Badge Variants
    ├── Agent Status Demos
    ├── Workflow Examples
    └── Data Table Demo
```

---

## Data Flow

```
┌────────────┐
│   User     │
│  Action    │
└────┬───────┘
     │
     ▼
┌────────────────┐
│   Component    │ ──── reads ───▶ ┌──────────────┐
│   (UI Event)   │                 │ Zustand Store│
└────┬───────────┘ ◀─── updates ── └──────────────┘
     │                                     │
     │                                     │
     ▼                                     │
┌────────────────┐                        │
│  API Call      │                        │
│  (React Query) │                        │
└────┬───────────┘                        │
     │                                     │
     ▼                                     │
┌────────────────┐                        │
│   Backend      │                        │
│   (FastAPI)    │                        │
└────┬───────────┘                        │
     │                                     │
     ▼                                     │
┌────────────────┐                        │
│   Response     │ ────────────────────────┘
│   (Updates     │
│    Store)      │
└────────────────┘
```

---

## State Management Flow

```
┌─────────────────────────────────────────┐
│         Global App Store                │
│                                         │
│ ┌─────────────────────────────────────┐│
│ │ User State                          ││
│ │ - user: User | null                 ││
│ │ - isAuthenticated: boolean          ││
│ └─────────────────────────────────────┘│
│                                         │
│ ┌─────────────────────────────────────┐│
│ │ Projects State                      ││
│ │ - projects: Project[]               ││
│ │ - currentProject: Project | null    ││
│ └─────────────────────────────────────┘│
│                                         │
│ ┌─────────────────────────────────────┐│
│ │ UI State                            ││
│ │ - sidebarOpen: boolean              ││
│ │ - darkMode: boolean                 ││
│ │ - notifications: Notification[]     ││
│ └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
              │
              ├──────────────────────┐
              │                      │
              ▼                      ▼
┌──────────────────────┐  ┌──────────────────────┐
│ Meta-Analysis Store  │  │ Reviewer Match Store │
│                      │  │                      │
│ - currentAnalysis    │  │ - currentProject     │
│ - agentProgress      │  │ - matches            │
│ - searchResults      │  │ - selectedReviewers  │
│ - screeningResults   │  │ - agentProgress      │
│ - credibilityResults │  │ - filters            │
│ - statisticalResults │  │ - sortBy             │
└──────────────────────┘  └──────────────────────┘
```

---

## Responsive Behavior

```
Mobile (< 640px)           Tablet (640-1024px)        Desktop (> 1024px)
┌─────────────────┐        ┌──────┬────────────┐      ┌──────┬─────────────┐
│                 │        │      │            │      │      │             │
│  [≡] Header     │        │ Side │  Header    │      │ Side │   Header    │
│─────────────────│        │ bar  │────────────│      │ bar  │─────────────│
│                 │        │      │            │      │      │             │
│   Single        │        │      │  2-Column  │      │      │  3-4 Column │
│   Column        │        │      │   Grid     │      │      │    Grid     │
│   Layout        │        │      │            │      │      │             │
│                 │        │      │            │      │      │             │
│   [Drawer]      │        │      │            │      │      │             │
│   Sidebar       │        └──────┴────────────┘      └──────┴─────────────┘
│   (Overlay)     │
│                 │
│   Full-width    │
│   Buttons       │
│                 │
└─────────────────┘

Behavior:
- Sidebar: Drawer     - Sidebar: Visible     - Sidebar: Fixed
- Cards: Stack        - Cards: 2-col grid    - Cards: 3-4 col grid
- Tables: H-scroll    - Tables: Scroll       - Tables: Full width
- Buttons: Full       - Buttons: Auto        - Buttons: Auto
```

---

## Tool Navigation Flow

```
Dashboard
   │
   ├─► Meta-Analysis
   │      │
   │      ├─► New Project
   │      │      └─► Search Form ──► Execute ──► Results
   │      │
   │      └─► View Project
   │             ├─► PRISMA Flow
   │             ├─► Forest Plot
   │             └─► Export Report
   │
   ├─► Reviewer Matcher
   │      │
   │      ├─► New Match
   │      │      └─► Upload ──► Analyze ──► Match List
   │      │
   │      └─► View Match
   │             ├─► Reviewer Profiles
   │             ├─► Send Invitations
   │             └─► Track Responses
   │
   ├─► Peer Review
   │      │
   │      ├─► New Review
   │      │      └─► Upload ──► Screen ──► Generate
   │      │
   │      └─► View Review
   │             ├─► Edit Comments
   │             ├─► Editor Summary
   │             └─► Submit Review
   │
   └─► Research Direction
          │
          ├─► New Analysis
          │      └─► Import ──► Analyze ──► Proposals
          │
          └─► View Analysis
                 ├─► Gap Matrix
                 ├─► Trend Charts
                 └─► Generate Proposal
```

---

## Agent Workflow Visualization

```
Meta-Analysis Workflow:

1. [●] Coordinator      ✅ Complete (5s)
       │
       ▼
2. [◐] Search           🔄 In Progress (67%)
       │                   ETA: 2m 00s
       │                   "Searching PubMed..."
       ▼
3. [ ] Screening        ⏳ Queued
       │
       ▼
4. [ ] Credibility      ⏳ Queued
       │
       ▼
5. [ ] Data Extract     ⏳ Queued
       │
       ▼
6. [ ] Statistical      ⏳ Queued
       │
       ▼
7. [ ] Report           ⏳ Queued


Reviewer Match Workflow:

1. [●] Coordinator      ✅ Complete
       │
       ▼
2. [●] Expertise        ✅ Complete
       │
       ▼
3. [◐] Conflict Check   🔄 In Progress
       │
       ▼
4. [ ] Availability     ⏳ Queued
       │
       ▼
5. [ ] Matcher          ⏳ Queued
```

---

## Component Relationships

```
Layout
  └─► uses
       ├─► Sidebar
       │     └─► uses
       │          └─► Navigation data
       │
       ├─► Header
       │     └─► uses
       │          ├─► Search component
       │          └─► Notification badge
       │
       └─► Main
             └─► renders
                  └─► {children}


Dashboard
  └─► uses
       ├─► Card (4x Tool Cards)
       │     └─► contains
       │          ├─► Icon
       │          ├─► Badge (project count)
       │          └─► Button (CTA)
       │
       ├─► Card (3x Stats)
       │     └─► contains
       │          └─► Stat display
       │
       └─► Card (Recent Projects)
             └─► contains
                  └─► Project list


Meta-Analysis Page
  └─► uses
       ├─► SearchForm
       │     └─► uses
       │          ├─► Input fields
       │          ├─► Checkbox groups
       │          └─► Button (submit)
       │
       ├─► AgentStatusCard (5-7 agents)
       │     └─► uses
       │          ├─► Status icon
       │          ├─► ProgressIndicator
       │          └─► ETA display
       │
       └─► WorkflowVisualizer
             └─► uses
                  ├─► Timeline
                  ├─► Step cards
                  └─► Progress bars
```

---

## File Dependencies

```
pages/dashboard/index.tsx
  ├─► Layout
  ├─► Card
  ├─► Badge
  ├─► Button
  ├─► useAppStore
  └─► types (ToolType, ProjectStatus)

components/shared/AgentStatusCard.tsx
  ├─► AgentProgress (type)
  ├─► AgentStatus (type)
  ├─► utils (getAgentStatusColor, formatDuration)
  └─► lucide-react (icons)

components/shared/WorkflowVisualizer.tsx
  ├─► Workflow (type)
  ├─► lucide-react (icons)
  └─► None (self-contained)

stores/useAppStore.ts
  ├─► zustand
  ├─► User (type)
  ├─► Project (type)
  └─► NotificationMessage (type)

lib/utils.ts
  ├─► clsx
  ├─► tailwind-merge
  └─► types (CredibilityLevel, AgentStatus, ProjectStatus)
```

---

## Performance Optimization Strategy

```
Code Splitting:
┌────────────────────────────────────┐
│ Initial Bundle (< 200KB)           │
│ - Layout components                │
│ - Dashboard                        │
│ - Shared components                │
└────────────────────────────────────┘
         │
         ├─► Lazy Load
         │
┌────────┴───────────────────────────┐
│ Tool-Specific Bundles              │
│ - Meta-Analysis (~50KB)            │
│ - Reviewer Matcher (~50KB)         │
│ - Peer Review (~50KB)              │
│ - Research Direction (~50KB)       │
└────────────────────────────────────┘
         │
         ├─► Dynamic Import
         │
┌────────┴───────────────────────────┐
│ Heavy Components (on-demand)       │
│ - Chart libraries                  │
│ - PDF viewers                      │
│ - Advanced editors                 │
└────────────────────────────────────┘
```

---

## Accessibility Features

```
Keyboard Navigation:
Tab          → Focus next element
Shift+Tab    → Focus previous element
Enter/Space  → Activate button/link
Escape       → Close modal/dropdown
Arrow Keys   → Navigate lists/menus


Screen Reader Support:
- All images have alt text
- Icons have aria-labels
- Form inputs have labels
- Buttons have descriptive text
- ARIA landmarks used
- Live regions for updates


Color Contrast:
Text (regular)    4.5:1 ✅
Text (large)      3.0:1 ✅
UI components     3.0:1 ✅
Focus indicators  3.0:1 ✅


Focus Management:
- Visible focus rings
- Logical tab order
- Trap focus in modals
- Skip links for main content
```

---

## Future Architecture Enhancements

```
v1.1 (Planned):
├─► Dark Mode
│   └─► Theme context with localStorage
│
├─► Real-time Updates
│   └─► WebSocket integration
│
├─► Offline Support
│   └─► Service Worker + Cache API
│
└─► Advanced Search
    └─► Full-text search across projects

v1.2 (Planned):
├─► Collaboration
│   └─► Multi-user editing
│
├─► Export/Import
│   └─► Project backup/restore
│
├─► Advanced Analytics
│   └─► Usage tracking & insights
│
└─► Mobile Apps
    └─► React Native (iOS/Android)
```

---

This architecture provides a solid foundation for a scalable, maintainable, and performant academic research platform!
