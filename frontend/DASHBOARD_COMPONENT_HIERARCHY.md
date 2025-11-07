# Dashboard Component Hierarchy

Visual guide to the dashboard component structure and relationships.

## Component Tree

```
┌─────────────────────────────────────────────────────────────────┐
│                        Layout (Existing)                         │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                 DashboardOverview Page                     │ │
│  │                                                             │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │              Hero Section (Animated)                 │  │ │
│  │  │  - Welcome message                                   │  │ │
│  │  │  - Date display                                      │  │ │
│  │  │  - New Project CTA                                   │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │                                                             │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │           Stats Grid (4 columns)                     │  │ │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │  │ │
│  │  │  │StatsCard │ │StatsCard │ │StatsCard │ │StatsCard│ │  │ │
│  │  │  │  Total   │ │In Progress│ │Completed │ │This Week│ │  │ │
│  │  │  └──────────┘ └──────────┘ └──────────┘ └────────┘ │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │                                                             │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │        View Tabs (Overview/Projects/Analytics)       │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │                                                             │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │            Conditional View Content                  │  │ │
│  │  │                                                       │  │ │
│  │  │  IF activeView === 'overview':                       │  │ │
│  │  │    ┌───────────────────────────────────────────┐    │  │ │
│  │  │    │         QuickActions Component            │    │  │ │
│  │  │    │  - New Meta-Analysis                      │    │  │ │
│  │  │    │  - Find Reviewers                         │    │  │ │
│  │  │    │  - Generate Review                        │    │  │ │
│  │  │    │  - Discover Gaps                          │    │  │ │
│  │  │    │  - Resume Recent                          │    │  │ │
│  │  │    │  - Clone Project                          │    │  │ │
│  │  │    └───────────────────────────────────────────┘    │  │ │
│  │  │                                                       │  │ │
│  │  │    ┌───────────────────────────────────────────┐    │  │ │
│  │  │    │      ProjectsList (Recent 6)              │    │  │ │
│  │  │    │  ┌──────────┐ ┌──────────┐ ┌──────────┐  │    │  │ │
│  │  │    │  │ProjectCard│ │ProjectCard│ │ProjectCard│  │    │  │ │
│  │  │    │  └──────────┘ └──────────┘ └──────────┘  │    │  │ │
│  │  │    │  ┌──────────┐ ┌──────────┐ ┌──────────┐  │    │  │ │
│  │  │    │  │ProjectCard│ │ProjectCard│ │ProjectCard│  │    │  │ │
│  │  │    │  └──────────┘ └──────────┘ └──────────┘  │    │  │ │
│  │  │    └───────────────────────────────────────────┘    │  │ │
│  │  │                                                       │  │ │
│  │  │  IF activeView === 'projects':                       │  │ │
│  │  │    ┌───────────────────────────────────────────┐    │  │ │
│  │  │    │      ProjectsList (All Projects)          │    │  │ │
│  │  │    │  - Search Bar                             │    │  │ │
│  │  │    │  - Filter Panel                           │    │  │ │
│  │  │    │  - Sort Dropdown                          │    │  │ │
│  │  │    │  - Refresh Button                         │    │  │ │
│  │  │    │  - Project Grid/List                      │    │  │ │
│  │  │    └───────────────────────────────────────────┘    │  │ │
│  │  │                                                       │  │ │
│  │  │  IF activeView === 'analytics':                      │  │ │
│  │  │    ┌───────────────────────────────────────────┐    │  │ │
│  │  │    │       AnalyticsDashboard Component        │    │  │ │
│  │  │    │  - Time Range Selector                    │    │  │ │
│  │  │    │  - Stats Summary                          │    │  │ │
│  │  │    │  - Chart Tabs                             │    │  │ │
│  │  │    │  - Multiple Chart Types                   │    │  │ │
│  │  │    └───────────────────────────────────────────┘    │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │                                                             │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │   NotificationCenter (Dropdown Mode - Fixed)         │  │ │
│  │  │   - Bell Icon with Badge                             │  │ │
│  │  │   - Dropdown Panel                                   │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Detailed Component Breakdown

### 1. DashboardOverview (Page)
```
DashboardOverview
├── Hero Section
│   ├── Date Badge (animated)
│   ├── Welcome Title
│   └── New Project Button
├── Stats Grid
│   ├── StatsCard (Total Projects)
│   ├── StatsCard (In Progress)
│   ├── StatsCard (Completed)
│   └── StatsCard (This Week)
├── View Tabs
│   ├── Overview Tab
│   ├── Projects Tab
│   └── Analytics Tab
├── Conditional Content
│   ├── QuickActions (if overview)
│   ├── ProjectsList (if overview/projects)
│   └── AnalyticsDashboard (if analytics)
└── NotificationCenter (dropdown, fixed)
```

### 2. ProjectsList Component
```
ProjectsList
├── Search Bar
│   ├── Search Input
│   └── Clear Button
├── Control Bar
│   ├── Filter Toggle Button
│   ├── Sort Dropdown
│   └── Refresh Button
├── Filter Panel (collapsible)
│   ├── Status Filters
│   ├── Tool Type Filters
│   └── Clear Filters Button
├── Results Summary
└── Projects Grid
    └── ProjectCard[] (mapped)
```

### 3. ProjectDetailView Component
```
ProjectDetailView
├── Header
│   ├── Back Button
│   ├── Title & Description
│   ├── Status Badge
│   └── Action Buttons
│       ├── Edit Button
│       ├── Pause/Resume Button
│       └── More Menu
│           ├── Clone
│           ├── Export (JSON/CSV/PDF)
│           └── Delete
├── Stats Cards Grid
│   ├── Total Workflows
│   ├── Completed
│   ├── In Progress
│   └── Decisions Made
├── Tab Navigation
│   ├── Overview Tab
│   ├── Workflows Tab
│   ├── Decisions Tab
│   └── Results Tab
└── Tab Content
    ├── Overview: WorkflowVisualizer + Project Info
    ├── Workflows: AgentStatusCard[] + Decision Lists
    ├── Decisions: AgentDecision[] Timeline
    └── Results: Coming Soon Placeholder
```

### 4. AnalyticsDashboard Component
```
AnalyticsDashboard
├── Header
│   ├── Title & Description
│   └── Time Range Selector
├── Stats Summary Grid
│   ├── Total Projects Stat
│   ├── Success Rate Stat
│   ├── Studies Screened Stat
│   └── Avg Completion Time Stat
├── Chart Tab Navigation
│   ├── Overview Tab
│   ├── Trends Tab
│   └── Performance Tab
└── Charts Grid
    ├── Overview: Area + Pie + Bar Charts
    ├── Trends: Line Chart
    ├── Performance: Bar Chart
    └── Success Rate Card
```

### 5. NotificationCenter Component
```
NotificationCenter
├── IF showAsDropdown === true:
│   ├── Bell Button (with badge)
│   └── Dropdown Panel (when open)
│       ├── Header (with close button)
│       ├── Filter Tabs (All/Unread)
│       ├── Notifications List
│       │   └── NotificationItem[]
│       └── Footer Actions
│           ├── Mark All Read
│           └── Clear All
└── IF showAsDropdown === false:
    ├── Page Header
    ├── Filter & Action Bar
    └── Notifications List (full page)
        └── NotificationItem[]
```

### 6. ProfileSettings Component
```
ProfileSettings
├── Header
├── Tab Navigation
│   ├── Profile Tab
│   ├── Notifications Tab
│   ├── Preferences Tab
│   └── Billing Tab
└── Tab Content
    ├── Profile: Form Fields + Save Button
    ├── Notifications: Toggle Switches
    ├── Preferences: Export Settings
    └── Billing: Usage Stats + Plan Info
```

### 7. QuickActions Component
```
QuickActions
├── Header
├── Primary Actions Grid (4 columns)
│   ├── New Meta-Analysis Card
│   ├── Find Reviewers Card
│   ├── Generate Review Card
│   └── Discover Gaps Card
├── Secondary Actions Row (2 columns)
│   ├── Resume Recent Project
│   └── Clone Project
└── Help CTA Banner
    ├── Documentation Link
    └── Tutorials Link
```

## Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                    Backend API                          │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│              dashboard.ts API Service                   │
│  - getDashboardStats()                                  │
│  - getProjects()                                        │
│  - getProject(id)                                       │
│  - getNotifications()                                   │
│  - getAnalytics()                                       │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│            useRealtimeUpdates Hook                      │
│  - Polling logic                                        │
│  - State updates                                        │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│               Zustand Store (useAppStore)               │
│  - projects: Project[]                                  │
│  - notifications: NotificationMessage[]                 │
│  - user: User                                           │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│              Dashboard Components                       │
│  - Read from store                                      │
│  - Dispatch actions                                     │
│  - Render UI                                            │
└─────────────────────────────────────────────────────────┘
```

## State Management Flow

```
User Action
    ↓
Component Event Handler
    ↓
API Call (dashboard.ts)
    ↓
Backend Processing
    ↓
Response Data
    ↓
Store Update (useAppStore)
    ↓
Component Re-render
    ↓
Updated UI
```

## Real-time Update Flow

```
useRealtimeUpdates Hook
    ↓
Polling Timer (every 5s)
    ↓
API Calls (parallel)
    ├── getProjects() or getProject(id)
    └── getNotifications()
    ↓
Store Updates
    ├── setProjects(projects)
    ├── updateProject(id, data)
    └── addNotification(notification)
    ↓
Component Re-renders
    ↓
UI Updates Automatically
```

## Navigation Flow

```
/dashboard/overview (Main Dashboard)
    │
    ├─→ Click Project Card ──→ /projects/[id] (ProjectDetailView)
    │
    ├─→ Click Quick Action ──→ /tools/[tool]/new
    │
    ├─→ Click Analytics Tab ──→ In-page view (AnalyticsDashboard)
    │
    ├─→ Click Notification ──→ notification.actionUrl
    │
    └─→ Click Settings ──→ /settings (ProfileSettings)
```

## Component Dependencies

```
DashboardOverview
    ├── StatsCard (existing)
    ├── ProjectsList (new)
    │   └── ProjectCard (existing)
    ├── AnalyticsDashboard (new)
    ├── QuickActions (new)
    └── NotificationCenter (new)

ProjectDetailView
    ├── WorkflowVisualizer (existing)
    ├── AgentStatusCard (existing)
    └── Badge (existing)

All Components
    ├── framer-motion
    ├── lucide-react (icons)
    ├── next/router
    └── @/lib/utils
```

## Integration Points

### With Existing Components
- **Layout**: Wraps all dashboard pages
- **StatsCard**: Used for metrics display
- **ProjectCard**: Used in projects grid
- **WorkflowVisualizer**: Shows workflow progress
- **AgentStatusCard**: Displays agent status
- **Badge**: Status indicators

### With Existing Hooks
- **useAppStore**: Global state management
- **useRouter**: Navigation

### With Existing Utils
- **formatRelativeTime**: Time formatting
- **formatDate**: Date formatting
- **formatDuration**: Duration formatting
- **formatNumber**: Number formatting

## Responsive Behavior

```
Mobile (< 640px)
├── Single column layouts
├── Stacked components
├── Simplified navigation
└── Touch-optimized buttons

Tablet (640px - 1024px)
├── 2-column grids
├── Collapsible sidebars
└── Optimized spacing

Desktop (> 1024px)
├── Multi-column layouts
├── Full feature set
└── Hover interactions
```

## Performance Considerations

1. **Lazy Loading**: Components loaded on-demand
2. **Memoization**: Expensive calculations cached
3. **Virtualization**: Large lists virtualized
4. **Debouncing**: Search inputs debounced
5. **Polling**: Pauses when tab hidden
6. **Code Splitting**: Dynamic imports for routes

## Accessibility Features

1. **Keyboard Navigation**: All interactive elements
2. **Screen Readers**: ARIA labels and roles
3. **Focus Management**: Logical focus order
4. **Color Contrast**: WCAG AA compliance
5. **Error Messages**: Clear, actionable feedback
