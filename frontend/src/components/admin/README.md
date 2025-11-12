# Admin Dashboard Components

Comprehensive admin dashboard components for controlling the Meta-Analysis Research Platform.

## Components Overview

### 1. MasterDashboardOverview
Main overview component displaying key platform metrics.

**Features:**
- Platform metrics cards (subscriptions, revenue, payouts, profit)
- Current month activity statistics
- Researcher pool composition
- Animated metric cards with hover effects
- Real-time data updates

**Props:**
```typescript
interface MasterDashboardOverviewProps {
  data: AdminDashboardData;
}
```

**Usage:**
```tsx
import { MasterDashboardOverview } from '@/components/admin';

<MasterDashboardOverview data={dashboardData} />
```

---

### 2. PayoutPoolManager
Complete payout pool management interface with distribution controls.

**Features:**
- Current pool status display
- Pool history table
- Distribution preview (dry run)
- Confirmation modals for payouts
- Progress tracking (completion rate, approval rate)
- Status indicators (open, calculating, distributed, closed)
- Pool statistics grid

**Props:**
```typescript
interface PayoutPoolManagerProps {
  currentPool: PayoutPool | null;
  poolHistory?: PayoutPool[];
  onDistribute: (poolId: string, dryRun: boolean) => Promise<any>;
  onCreatePool?: () => void;
  loading?: boolean;
}
```

**Usage:**
```tsx
import { PayoutPoolManager } from '@/components/admin';

<PayoutPoolManager
  currentPool={currentPool}
  poolHistory={poolHistory}
  onDistribute={handleDistribute}
  loading={loading}
/>
```

**Key Functions:**
- `Preview Distribution`: Dry-run calculation before actual distribution
- `Distribute Payouts`: Execute payout distribution with confirmation
- `View History`: Browse past payout pools

---

### 3. RevenueChart
Interactive charts for revenue, profit, and user growth analytics.

**Features:**
- Multiple chart types (line, area, bar)
- Revenue over time visualization
- Payout tracking
- Profit analysis
- User signup trends
- Summary statistics cards
- Custom tooltips with formatted data
- Responsive design

**Props:**
```typescript
interface RevenueChartProps {
  data?: RevenueData[];
  signupData?: SignupData[];
  type?: 'line' | 'area' | 'bar';
}
```

**Usage:**
```tsx
import { RevenueChart } from '@/components/admin';

// Area chart (default)
<RevenueChart type="area" />

// Bar chart
<RevenueChart type="bar" data={customRevenueData} />

// Line chart
<RevenueChart type="line" signupData={customSignupData} />
```

**Data Formats:**
```typescript
interface RevenueData {
  month: string;
  revenue: number;
  subscriptions: number;
  payouts: number;
  profit: number;
}

interface SignupData {
  month: string;
  signups: number;
  activeUsers: number;
}
```

---

### 4. ActivityFeed
Real-time activity feed with filtering and auto-refresh capabilities.

**Features:**
- Real-time activity updates
- Activity type filtering (signups, reviews, payouts, subscriptions)
- Auto-refresh with configurable interval
- Manual refresh button
- Activity type indicators with colors
- Relative timestamps
- Empty state handling
- Activity statistics summary

**Props:**
```typescript
interface ActivityFeedProps {
  activities?: ActivityItem[];
  onRefresh?: () => void;
  refreshing?: boolean;
  autoRefresh?: boolean;
  autoRefreshInterval?: number; // in seconds
}
```

**Usage:**
```tsx
import { ActivityFeed } from '@/components/admin';

<ActivityFeed
  activities={recentActivities}
  onRefresh={handleRefresh}
  autoRefresh={true}
  autoRefreshInterval={30}
/>
```

**Activity Types:**
- `signup`: New user registration
- `review_submitted`: Review submission
- `payout_processed`: Payout execution
- `subscription`: Subscription changes
- `paper_uploaded`: New paper upload
- `review_approved`: Review approval
- `system`: System events

---

### 5. EnhancedResearcherTable
Advanced researcher management table with search, filters, and bulk operations.

**Features:**
- Advanced search (name, email, institution)
- Multiple filters (status, expertise domain)
- Column sorting (name, H-index, earnings, reviews)
- Row selection (individual and bulk)
- CSV export functionality
- Action dropdown menu (view, suspend, activity)
- Pagination with page navigation
- Summary statistics
- Responsive design

**Props:**
```typescript
interface EnhancedResearcherTableProps {
  researchers: ResearcherListItem[];
  onResearcherClick?: (researcher: ResearcherListItem) => void;
  onSuspend?: (researcherId: string) => void;
  onViewActivity?: (researcherId: string) => void;
  itemsPerPage?: number;
}
```

**Usage:**
```tsx
import { EnhancedResearcherTable } from '@/components/admin';

<EnhancedResearcherTable
  researchers={researchers}
  onResearcherClick={handleViewProfile}
  onSuspend={handleSuspend}
  onViewActivity={handleViewActivity}
  itemsPerPage={10}
/>
```

**Available Actions:**
- View Profile: Navigate to researcher detail page
- View Activity: See researcher's platform activity
- Suspend Account: Disable researcher account
- Export CSV: Download selected/all researchers

---

## Master Dashboard Page

Location: `/src/pages/admin/master-dashboard.tsx`

### Features

1. **Overview Tab**
   - Platform metrics overview
   - Current month activity
   - Researcher pool stats

2. **Researchers Tab**
   - Complete researcher management
   - Search and filter capabilities
   - Bulk operations

3. **Payouts Tab**
   - Current pool management
   - Distribution controls
   - Pool history

4. **Analytics Tab**
   - Revenue charts
   - Growth metrics
   - Trend analysis

5. **Activity Feed Tab**
   - Real-time activity stream
   - Activity filtering
   - Auto-refresh

6. **Financial Tab**
   - Revenue breakdown
   - Payout obligations
   - Profit margins
   - Historical data

### Navigation

```
/admin/master-dashboard
```

### Access Control

Protected by RBAC - requires admin role:
```typescript
canAccessAdmin(user)
```

### Data Fetching

Uses custom hooks:
- `useAdminDashboard()`: Dashboard data and actions
- `usePayouts()`: Payout pool management

### State Management

- Tab selection state
- Refresh triggers
- Loading states
- Error handling

---

## Installation & Dependencies

### Required Packages

```json
{
  "framer-motion": "^10.16.16",
  "recharts": "^2.10.3",
  "lucide-react": "^0.294.0",
  "react-hot-toast": "^2.4.1"
}
```

### File Structure

```
src/components/admin/
├── README.md
├── index.ts
├── MasterDashboardOverview.tsx
├── PayoutPoolManager.tsx
├── RevenueChart.tsx
├── ActivityFeed.tsx
└── EnhancedResearcherTable.tsx

src/pages/admin/
└── master-dashboard.tsx
```

---

## Styling

All components use:
- Tailwind CSS for styling
- Framer Motion for animations
- Consistent design system
- Responsive breakpoints
- Accessible color contrasts

### Color Scheme

- Primary: Red/Orange gradient
- Success: Green
- Warning: Orange
- Info: Blue
- Danger: Red
- Neutral: Gray

---

## Best Practices

### 1. Data Fetching
```tsx
// Fetch on mount and refresh
useEffect(() => {
  if (canAccessAdmin(user)) {
    fetchDashboard();
    fetchResearchers();
    fetchCurrentPool();
  }
}, [user, refreshKey]);
```

### 2. Error Handling
```tsx
try {
  const result = await distributePayouts(poolId);
  toast.success('Success message');
} catch (err) {
  toast.error(err.message);
  throw err;
}
```

### 3. Confirmation Modals
```tsx
// Always confirm destructive actions
<Button onClick={() => setShowConfirmation(true)}>
  Distribute Payouts
</Button>
```

### 4. CSV Export
```tsx
// Export selected or all rows
const dataToExport = selectedRows.size > 0
  ? data.filter(item => selectedRows.has(item.id))
  : data;
```

### 5. Real-time Updates
```tsx
// Auto-refresh with interval
useEffect(() => {
  if (autoRefresh) {
    const interval = setInterval(onRefresh, autoRefreshInterval * 1000);
    return () => clearInterval(interval);
  }
}, [autoRefresh, autoRefreshInterval]);
```

---

## API Integration

### Expected Endpoints

```typescript
// Dashboard data
GET /api/v1/admin/dashboard

// Researchers
GET /api/v1/admin/researchers?page=1&page_size=100

// Payout history
GET /api/v1/admin/payouts/history

// Current pool
GET /api/v1/payouts/current-pool

// Distribute payouts
POST /api/v1/payouts/calculate-monthly
{
  "poolMonth": "2025-11",
  "dryRun": false
}
```

### Response Types

All types defined in `/src/lib/payment-types.ts`:
- `AdminDashboardData`
- `ResearcherListItem`
- `PayoutPool`
- `PayoutHistoryItem`

---

## Accessibility

- Semantic HTML structure
- ARIA labels on interactive elements
- Keyboard navigation support
- Focus management
- Screen reader friendly
- Color contrast compliance

---

## Performance

### Optimizations

1. **Memoization**
   - Use `useMemo` for computed values
   - Memoize expensive calculations

2. **Pagination**
   - Limit displayed rows
   - Lazy loading for large datasets

3. **Debouncing**
   - Search input debouncing
   - Filter application delays

4. **Animation Performance**
   - GPU-accelerated animations
   - Reduced motion support

---

## Testing

### Component Testing

```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { EnhancedResearcherTable } from '@/components/admin';

test('filters researchers by search query', () => {
  render(<EnhancedResearcherTable researchers={mockData} />);

  const searchInput = screen.getByPlaceholderText(/search/i);
  fireEvent.change(searchInput, { target: { value: 'John' } });

  expect(screen.getByText('John Doe')).toBeInTheDocument();
});
```

### Integration Testing

Test complete workflows:
- Dashboard data loading
- Payout distribution flow
- Researcher management actions
- CSV export functionality

---

## Future Enhancements

### Planned Features

1. **Advanced Analytics**
   - Cohort analysis
   - Retention metrics
   - Revenue forecasting

2. **Bulk Operations**
   - Bulk researcher actions
   - Batch email notifications
   - Mass updates

3. **Reporting**
   - PDF report generation
   - Scheduled reports
   - Custom report builder

4. **Notifications**
   - Real-time WebSocket updates
   - Email alerts for critical events
   - Push notifications

5. **Permissions**
   - Role-based feature access
   - Action logging
   - Audit trails

---

## Support

For questions or issues:
1. Check this documentation
2. Review component source code
3. Check `/src/lib/payment-types.ts` for type definitions
4. Review `/src/hooks/useAdminDashboard.ts` for data hooks

---

## Version History

### v1.0.0 (Current)
- Initial release
- All 5 core components
- Master dashboard page
- Complete feature set
- Full documentation
