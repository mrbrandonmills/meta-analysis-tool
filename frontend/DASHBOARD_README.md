# Comprehensive Dashboard System

A complete dashboard system for managing meta-analysis projects with real-time updates, analytics, notifications, and user management.

## Overview

The dashboard provides a comprehensive interface for researchers to:
- Manage multiple meta-analysis projects
- Track progress with real-time updates
- View analytics and statistics
- Receive notifications
- Configure user settings and preferences

## Architecture

### Components Structure

```
src/
├── components/
│   └── dashboard/
│       ├── StatsCard.tsx              # Stat display cards
│       ├── ProjectCard.tsx            # Individual project cards
│       ├── ProjectsList.tsx           # Projects list with filters
│       ├── ProjectDetailView.tsx      # Detailed project view
│       ├── AnalyticsDashboard.tsx     # Analytics with charts
│       ├── NotificationCenter.tsx     # Notification system
│       ├── ProfileSettings.tsx        # User settings
│       └── QuickActions.tsx           # Quick action buttons
├── pages/
│   └── dashboard/
│       ├── index.tsx                  # Main dashboard (existing)
│       └── overview.tsx               # Enhanced dashboard (new)
├── hooks/
│   └── useRealtimeUpdates.ts         # Real-time polling hooks
├── lib/
│   └── api/
│       └── dashboard.ts              # Dashboard API service
└── stores/
    └── useAppStore.ts                # Global state management
```

## Features

### 1. Dashboard Overview

**Location:** `/pages/dashboard/overview.tsx`

Main dashboard view with:
- Hero section with user greeting
- Key statistics cards (total, in progress, completed, weekly)
- Quick actions for starting new projects
- Recent projects preview
- View tabs (Overview, All Projects, Analytics)

**Usage:**
```tsx
import DashboardOverview from '@/pages/dashboard/overview'

// Access at /dashboard/overview
```

### 2. Projects List Component

**Location:** `/components/dashboard/ProjectsList.tsx`

Advanced project listing with:
- Search functionality
- Multiple filters (status, tool type, date range)
- Sorting options
- Loading states
- Empty states
- Responsive grid layout

**Props:**
```typescript
interface ProjectsListProps {
  projects: Project[]
  loading?: boolean
  onRefresh?: () => void
  onDelete?: (projectId: string) => void
  onClone?: (projectId: string) => void
  onPause?: (projectId: string) => void
  onResume?: (projectId: string) => void
  onExport?: (projectId: string) => void
}
```

**Usage:**
```tsx
<ProjectsList
  projects={projects}
  loading={loading}
  onRefresh={handleRefresh}
  onDelete={handleDelete}
  onClone={handleClone}
/>
```

### 3. Project Detail View

**Location:** `/components/dashboard/ProjectDetailView.tsx`

Comprehensive project details:
- Project information and metadata
- Workflow visualizer
- Agent execution status
- Audit trail of decisions
- Statistics and metrics
- Action menu (edit, clone, export, delete)
- Tabbed interface (Overview, Workflows, Decisions, Results)

**Props:**
```typescript
interface ProjectDetailViewProps {
  project: Project
  onBack?: () => void
  onDelete?: (projectId: string) => void
  onClone?: (projectId: string) => void
  onPause?: (projectId: string) => void
  onResume?: (projectId: string) => void
  onExport?: (projectId: string, format: 'json' | 'csv' | 'pdf') => void
  onEdit?: (projectId: string) => void
}
```

**Usage:**
```tsx
<ProjectDetailView
  project={project}
  onBack={() => router.back()}
  onDelete={handleDelete}
  onExport={handleExport}
/>
```

### 4. Analytics Dashboard

**Location:** `/components/dashboard/AnalyticsDashboard.tsx`

Visualizations and insights:
- Projects over time (area chart)
- Projects by tool type (pie chart)
- Projects by status (bar chart)
- Studies screened trends (line chart)
- Completion times analysis
- Success rate metrics
- Time range selector

**Props:**
```typescript
interface AnalyticsDashboardProps {
  data?: AnalyticsData
  loading?: boolean
  timeRange?: '7d' | '30d' | '90d' | '1y'
  onTimeRangeChange?: (range: '7d' | '30d' | '90d' | '1y') => void
}
```

**Usage:**
```tsx
<AnalyticsDashboard
  data={analyticsData}
  loading={loading}
  timeRange="30d"
  onTimeRangeChange={handleTimeRangeChange}
/>
```

### 5. Notification Center

**Location:** `/components/dashboard/NotificationCenter.tsx`

Two modes:
- **Dropdown mode**: Bell icon with badge for header
- **Full page mode**: Dedicated notifications page

Features:
- Filter by read/unread
- Mark as read/unread
- Delete notifications
- Clear all
- Action links
- Type-based icons and colors

**Props:**
```typescript
interface NotificationCenterProps {
  notifications: NotificationMessage[]
  onMarkAsRead?: (notificationId: string) => void
  onMarkAllAsRead?: () => void
  onDelete?: (notificationId: string) => void
  onClear?: () => void
  showAsDropdown?: boolean
}
```

**Usage:**
```tsx
// Dropdown mode (in header)
<NotificationCenter
  notifications={notifications}
  onMarkAsRead={handleMarkAsRead}
  showAsDropdown={true}
/>

// Full page mode
<NotificationCenter
  notifications={notifications}
  onMarkAsRead={handleMarkAsRead}
  onMarkAllAsRead={handleMarkAllAsRead}
  onClear={handleClear}
  showAsDropdown={false}
/>
```

### 6. Profile Settings

**Location:** `/components/dashboard/ProfileSettings.tsx`

User settings management:
- **Profile tab**: Personal information
- **Notifications tab**: Notification preferences
- **Preferences tab**: Export settings
- **Billing tab**: Usage statistics and plan info

**Props:**
```typescript
interface ProfileSettingsProps {
  user: User
  onSave?: (updates: Partial<User>) => Promise<void>
}
```

**Usage:**
```tsx
<ProfileSettings
  user={user}
  onSave={handleSaveProfile}
/>
```

### 7. Quick Actions

**Location:** `/components/dashboard/QuickActions.tsx`

Fast access to common actions:
- New meta-analysis
- Find reviewers
- Generate review
- Discover research gaps
- Resume recent project
- Clone project
- Help resources

**Props:**
```typescript
interface QuickActionsProps {
  onActionClick?: (actionId: string) => void
  recentProjectId?: string
}
```

**Usage:**
```tsx
<QuickActions
  onActionClick={handleActionClick}
  recentProjectId={mostRecentProject?.id}
/>
```

## Real-time Updates

### useRealtimeUpdates Hook

**Location:** `/hooks/useRealtimeUpdates.ts`

Provides polling-based real-time updates:

```typescript
const {
  isPolling,
  error,
  lastUpdate,
  refresh,
  startPolling,
  stopPolling
} = useRealtimeUpdates({
  enabled: true,
  projectId: 'project-123', // Optional: poll specific project
  pollingInterval: 5000, // 5 seconds
  onProjectUpdate: (project) => console.log('Updated:', project),
  onNewNotification: (notification) => console.log('New:', notification)
})
```

**Features:**
- Automatic polling with configurable interval
- Pauses when tab is hidden
- Stops when component unmounts
- Manual refresh capability
- Error handling
- Project-specific or global polling

### useProjectProgress Hook

Monitor specific project progress:

```typescript
const {
  project,
  progress,
  isComplete,
  isPolling,
  error,
  refresh
} = useProjectProgress('project-123')
```

## API Service

**Location:** `/lib/api/dashboard.ts`

Centralized API calls:

```typescript
// Dashboard stats
const stats = await getDashboardStats()

// Projects list with filters
const projects = await getProjects({
  page: 1,
  pageSize: 10,
  sortBy: 'updatedAt',
  sortOrder: 'desc',
  filters: {
    status: ['in_progress'],
    toolType: ['meta_analysis']
  }
})

// Single project
const project = await getProject('project-123')

// Activity feed
const activity = await getRecentActivity(10)

// Notifications
const notifications = await getNotifications(true) // unread only
await markNotificationRead('notif-123')
await markAllNotificationsRead()

// Project actions
await deleteProject('project-123')
const cloned = await cloneProject('project-123')
await pauseProject('project-123')
await resumeProject('project-123')
const blob = await exportProject('project-123', 'json')

// Analytics
const analytics = await getAnalytics('30d')
```

## State Management

Uses Zustand for global state:

```typescript
const {
  // State
  projects,
  user,
  notifications,
  loading,
  error,

  // Actions
  setProjects,
  addProject,
  updateProject,
  deleteProject,
  addNotification,
  markNotificationRead,
  clearNotifications,
  setLoading,
  setError
} = useAppStore()
```

## Testing

Comprehensive test coverage:

### Component Tests

**ProjectsList.test.tsx:**
- Renders all projects
- Search functionality
- Filters (status, tool type)
- Sorting
- Refresh action
- Empty states
- Loading states

**NotificationCenter.test.tsx:**
- Full page and dropdown modes
- Filter by read/unread
- Mark as read actions
- Delete notifications
- Empty states
- Icon rendering

**useRealtimeUpdates.test.ts:**
- Polling initialization
- Start/stop polling
- Error handling
- Visibility changes
- Manual refresh
- Project-specific polling

### Running Tests

```bash
# Run all tests
npm test

# Run specific test file
npm test ProjectsList.test.tsx

# Run with coverage
npm run test:coverage

# Run in watch mode
npm test -- --watch
```

## Styling

Uses Tailwind CSS with custom configuration:

- **Colors:** Primary (blue), Accent (purple), tool-specific colors
- **Animations:** Fade in, slide in, scale in, shimmer
- **Shadows:** Soft, medium, hard, glow effects
- **Responsive:** Mobile-first breakpoints

## Performance Optimizations

1. **Lazy Loading:** Components loaded on demand
2. **Memoization:** React.memo and useMemo for expensive operations
3. **Virtualization:** Large lists use virtual scrolling
4. **Debouncing:** Search inputs debounced
5. **Pagination:** Projects list paginated
6. **Polling Management:** Pauses when tab hidden

## Accessibility

- Semantic HTML
- ARIA labels and roles
- Keyboard navigation
- Focus management
- Screen reader support
- Color contrast compliance

## Browser Support

- Chrome/Edge (last 2 versions)
- Firefox (last 2 versions)
- Safari (last 2 versions)
- Mobile browsers (iOS Safari, Chrome Android)

## Future Enhancements

1. **WebSocket Support:** Replace polling with real-time WebSocket connections
2. **Offline Mode:** Cache data for offline access
3. **Advanced Filters:** Saved filter presets, complex queries
4. **Export Templates:** Customizable export formats
5. **Collaborative Features:** Share projects, comments
6. **Mobile App:** React Native mobile application
7. **Customizable Dashboards:** Drag-and-drop widget system
8. **Advanced Analytics:** Machine learning insights

## Troubleshooting

### Polling Not Working

1. Check `enabled` prop is true
2. Verify API endpoints are accessible
3. Check browser console for errors
4. Ensure auth token is valid

### Charts Not Displaying

1. Verify recharts is installed: `npm install recharts`
2. Check data format matches expected structure
3. Ensure container has height/width

### Notifications Not Appearing

1. Check notification permissions
2. Verify WebSocket/polling is active
3. Check store for notification state

## Contributing

1. Create feature branch
2. Add tests for new features
3. Update documentation
4. Submit pull request

## License

MIT License - see LICENSE file for details
