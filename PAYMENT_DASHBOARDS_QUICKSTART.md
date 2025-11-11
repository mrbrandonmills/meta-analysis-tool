# Payment Dashboards - Quick Start Guide

## 🚀 Getting Started (5 minutes)

### 1. View the Dashboards

Navigate to any of the three dashboards:

```bash
# Admin Dashboard (requires admin role)
http://localhost:3000/admin

# Editor Dashboard (requires editor or admin role)
http://localhost:3000/editor

# Earnings Dashboard (all authenticated users)
http://localhost:3000/earnings
```

### 2. Set Your User Role

Update the mock user in your store to test different roles:

```typescript
// In your useAppStore or mock data
const user = {
  id: '123',
  name: 'John Doe',
  email: 'john@example.com',
  role: 'admin' // Change to 'editor' or 'researcher'
};
```

### 3. Test with Mock Data

The dashboards work with mock data out of the box. No backend required for UI testing!

---

## 📦 Import Components

### Using Individual Components

```typescript
import { PayoutPoolCard } from '@/components/payment/PayoutPoolCard';
import { SubscriptionCard } from '@/components/payment/SubscriptionCard';
import { ReviewerTable } from '@/components/payment/ReviewerTable';
import { PaperQueueCard } from '@/components/payment/PaperQueueCard';
import { ReviewApprovalCard } from '@/components/payment/ReviewApprovalCard';
```

Or use the barrel export:

```typescript
import {
  PayoutPoolCard,
  SubscriptionCard,
  ReviewerTable,
  PaperQueueCard,
  ReviewApprovalCard
} from '@/components/payment';
```

### Using API Hooks

```typescript
import { useSubscription } from '@/hooks/useSubscription';
import { usePayouts } from '@/hooks/usePayouts';
import { useAdminDashboard } from '@/hooks/useAdminDashboard';
import { useReviewApproval } from '@/hooks/useReviewApproval';
```

Or use the barrel export:

```typescript
import {
  useSubscription,
  usePayouts,
  useAdminDashboard,
  useReviewApproval
} from '@/hooks';
```

---

## 🎨 Component Examples

### PayoutPoolCard

```typescript
import { PayoutPoolCard } from '@/components/payment';

const pool = {
  id: 'pool_123',
  poolMonth: '2025-11-01',
  totalContributions: 200,
  totalReviewsApproved: 10,
  payoutPerReview: 20,
  status: 'open'
  // ... other fields
};

<PayoutPoolCard
  pool={pool}
  showActions={true}
  onDistribute={() => console.log('Distribute payouts')}
/>
```

### SubscriptionCard

```typescript
import { SubscriptionCard } from '@/components/payment';

const subscription = {
  id: 'sub_123',
  status: 'active',
  monthlyAmount: 100,
  payoutContribution: 20,
  currentPeriodEnd: '2025-12-01T00:00:00Z'
  // ... other fields
};

<SubscriptionCard
  subscription={subscription}
  onCancel={(reason) => console.log('Cancel:', reason)}
  onUpdatePayment={() => console.log('Update payment')}
/>
```

### ReviewerTable

```typescript
import { ReviewerTable } from '@/components/payment';

const researchers = [
  {
    id: '1',
    name: 'Dr. Jane Smith',
    email: 'jane@university.edu',
    institution: 'Stanford University',
    hIndex: 35,
    lifetimeEarnings: 240,
    lifetimeReviews: 12,
    isPayingMember: true
    // ... other fields
  }
];

<ReviewerTable
  researchers={researchers}
  onResearcherClick={(researcher) => console.log(researcher)}
  itemsPerPage={10}
/>
```

### PaperQueueCard

```typescript
import { PaperQueueCard } from '@/components/payment';

const paper = {
  id: 'paper_123',
  title: 'The Role of Dopamine in Learning',
  uploadDate: '2025-11-05T10:30:00Z',
  uploadedBy: 'Dr. Sarah Johnson',
  status: 'under_review',
  assignedReviewers: [
    { id: '1', name: 'Dr. Michael Chen', status: 'completed' }
  ],
  reviewsCompleted: 1,
  reviewsNeeded: 3
};

<PaperQueueCard
  paper={paper}
  onView={() => console.log('View paper')}
  onAssignReviewers={() => console.log('Assign reviewers')}
/>
```

### ReviewApprovalCard

```typescript
import { ReviewApprovalCard } from '@/components/payment';

const review = {
  reviewId: 'review_123',
  manuscriptId: 'paper_123',
  manuscriptTitle: 'The Role of Dopamine...',
  reviewerName: 'Dr. Anonymous',
  submittedAt: '2025-11-10T14:30:00Z',
  reviewQualityPreview: {
    overallScore: 8.5,
    strengthsCount: 4,
    weaknessesCount: 3,
    wordCount: 1250
  }
};

<ReviewApprovalCard
  review={review}
  onApprove={(notes, score) => console.log('Approved', notes, score)}
  onReject={(reason) => console.log('Rejected', reason)}
  onViewFull={() => console.log('View full review')}
  estimatedPayout={20}
/>
```

---

## 🔌 Hook Examples

### useSubscription

```typescript
import { useSubscription } from '@/hooks';

function SubscriptionManager() {
  const {
    subscription,
    loading,
    error,
    fetchSubscription,
    cancelSubscription
  } = useSubscription();

  useEffect(() => {
    fetchSubscription();
  }, []);

  const handleCancel = async () => {
    await cancelSubscription('Too expensive');
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return <SubscriptionCard subscription={subscription} onCancel={handleCancel} />;
}
```

### usePayouts

```typescript
import { usePayouts } from '@/hooks';

function EarningsDashboard() {
  const { earnings, currentPool, loading, fetchEarnings, fetchCurrentPool } = usePayouts();

  useEffect(() => {
    fetchEarnings();
    fetchCurrentPool();
  }, []);

  return (
    <div>
      <div>Lifetime Earnings: ${earnings?.lifetimeEarnings}</div>
      <PayoutPoolCard pool={currentPool} />
    </div>
  );
}
```

### useAdminDashboard

```typescript
import { useAdminDashboard } from '@/hooks';

function AdminPanel() {
  const {
    dashboardData,
    researchers,
    loading,
    fetchDashboard,
    fetchResearchers
  } = useAdminDashboard();

  useEffect(() => {
    fetchDashboard();
    fetchResearchers({ pageSize: 50 });
  }, []);

  return (
    <div>
      <div>MRR: ${dashboardData?.platformMetrics.monthlyRecurringRevenue}</div>
      <ReviewerTable researchers={researchers} />
    </div>
  );
}
```

### useReviewApproval

```typescript
import { useReviewApproval } from '@/hooks';

function ReviewApprovalQueue() {
  const {
    pendingReviews,
    loading,
    fetchPendingReviews,
    approveReview,
    rejectReview
  } = useReviewApproval();

  useEffect(() => {
    fetchPendingReviews();
  }, []);

  const handleApprove = async (reviewId: string) => {
    await approveReview(reviewId, {
      approved: true,
      qualityScore: 4,
      eligibleForPayout: true
    });
  };

  return (
    <div>
      {pendingReviews.map(review => (
        <ReviewApprovalCard
          key={review.reviewId}
          review={review}
          onApprove={(notes, score) => handleApprove(review.reviewId)}
        />
      ))}
    </div>
  );
}
```

---

## 🔒 Role-Based Access Control

### Protecting Routes

```typescript
import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { canAccessAdmin } from '@/lib/rbac';
import { useAppStore } from '@/stores/useAppStore';

function AdminPage() {
  const router = useRouter();
  const { user } = useAppStore();

  useEffect(() => {
    if (!canAccessAdmin(user)) {
      router.push('/dashboard-new');
    }
  }, [user, router]);

  if (!canAccessAdmin(user)) {
    return null;
  }

  return <div>Admin Content</div>;
}
```

### Conditional Rendering

```typescript
import { canAccessEditor, canAccessAdmin } from '@/lib/rbac';
import { useAppStore } from '@/stores/useAppStore';

function Navigation() {
  const { user } = useAppStore();

  return (
    <nav>
      <Link href="/dashboard">Dashboard</Link>

      {canAccessEditor(user) && (
        <Link href="/editor">Editor</Link>
      )}

      {canAccessAdmin(user) && (
        <Link href="/admin">Admin</Link>
      )}
    </nav>
  );
}
```

---

## 🎭 Mock Data for Testing

Create a file `/frontend/src/mocks/paymentData.ts`:

```typescript
import {
  Subscription,
  PayoutPool,
  EarningsSummary,
  ResearcherListItem,
  PendingReview
} from '@/lib/payment-types';

export const mockSubscription: Subscription = {
  id: 'sub_123',
  userId: 'user_123',
  stripeSubscriptionId: 'sub_stripe_123',
  stripeCustomerId: 'cus_stripe_123',
  status: 'active',
  planType: 'researcher_monthly',
  monthlyAmount: 100,
  payoutContribution: 20,
  currentPeriodStart: '2025-11-01T00:00:00Z',
  currentPeriodEnd: '2025-12-01T00:00:00Z',
  cancelAtPeriodEnd: false,
  createdAt: '2025-09-01T00:00:00Z',
  updatedAt: '2025-11-11T00:00:00Z'
};

export const mockPool: PayoutPool = {
  id: 'pool_123',
  poolMonth: '2025-11-01',
  totalContributions: 200,
  totalDistributed: 0,
  remaining: 200,
  totalReviewsAssigned: 10,
  totalReviewsCompleted: 8,
  totalReviewsApproved: 6,
  payoutPerReview: 33.33,
  status: 'open',
  createdAt: '2025-11-01T00:00:00Z',
  updatedAt: '2025-11-11T00:00:00Z'
};

export const mockEarnings: EarningsSummary = {
  lifetimeEarnings: 240,
  currentMonthPending: 60,
  lastPayout: {
    amount: 60,
    date: '2025-11-01T00:00:00Z',
    reviewsCount: 3,
    transferStatus: 'completed'
  },
  earningsHistory: [
    {
      month: '2025-11-01',
      reviewsCompleted: 3,
      reviewsApproved: 3,
      payoutAmount: 60,
      payoutDate: '2025-12-01',
      status: 'completed'
    }
  ],
  currentMonthReviews: {
    assigned: 5,
    completed: 3,
    approved: 3,
    pendingApproval: 0,
    estimatedPayout: 60
  }
};

export const mockResearchers: ResearcherListItem[] = [
  {
    id: 'res_1',
    name: 'Dr. Sarah Johnson',
    email: 'sjohnson@stanford.edu',
    institution: 'Stanford University',
    hIndex: 35,
    expertiseDomains: ['cognitive psychology', 'neuroscience'],
    subscriptionStatus: 'active',
    isPayingMember: true,
    memberSince: '2025-09-01T00:00:00Z',
    lifetimeReviews: 12,
    lifetimeEarnings: 240,
    averageReviewQuality: 0.88,
    stripeConnectStatus: 'verified'
  }
];

export const mockPendingReviews: PendingReview[] = [
  {
    reviewId: 'review_1',
    manuscriptId: 'paper_1',
    manuscriptTitle: 'The Role of Dopamine in Learning',
    reviewerName: 'Dr. Sarah Johnson (Anonymous)',
    submittedAt: '2025-11-10T14:30:00Z',
    reviewQualityPreview: {
      overallScore: 8.5,
      strengthsCount: 4,
      weaknessesCount: 3,
      wordCount: 1250
    }
  }
];
```

Then use in your components:

```typescript
import { mockPool, mockEarnings } from '@/mocks/paymentData';

function TestComponent() {
  return (
    <>
      <PayoutPoolCard pool={mockPool} />
      <div>Earnings: ${mockEarnings.lifetimeEarnings}</div>
    </>
  );
}
```

---

## 🐛 Debugging Tips

### Check User Role

```typescript
console.log('Current user:', user);
console.log('Has admin access:', canAccessAdmin(user));
console.log('Has editor access:', canAccessEditor(user));
```

### Monitor API Calls

```typescript
// In hooks, add logging
const fetchData = async () => {
  console.log('Fetching data from:', endpoint);
  const response = await fetch(endpoint);
  console.log('Response:', response);
};
```

### Inspect Component Props

```typescript
// Add to component
console.log('Props received:', { pool, showActions, onDistribute });
```

### Check Loading States

```typescript
if (loading) {
  console.log('Loading...');
  return <LoadingSpinner />;
}

if (error) {
  console.error('Error:', error);
  return <ErrorMessage error={error} />;
}
```

---

## 🎬 Demo Mode

To run the dashboards in demo mode with fake data:

1. **Set demo user**:
```typescript
const demoUser = {
  id: 'demo_123',
  name: 'Demo User',
  email: 'demo@example.com',
  role: 'admin' // Change to test different roles
};
```

2. **Mock API responses**:
```typescript
// Override fetch in hooks
const fetchDashboard = async () => {
  // Instead of real API call
  setDashboardData(mockDashboardData);
};
```

3. **Disable authentication**:
```typescript
// In route protection
useEffect(() => {
  // Comment out redirect for demo
  // if (!canAccessAdmin(user)) {
  //   router.push('/dashboard-new');
  // }
}, []);
```

---

## 📚 Additional Resources

- **Technical Design**: See `/TECHNICAL_DESIGN_PAYMENT_ECOSYSTEM.md`
- **Implementation Details**: See `/PAYMENT_DASHBOARDS_IMPLEMENTATION.md`
- **Type Definitions**: See `/frontend/src/lib/payment-types.ts`
- **RBAC Functions**: See `/frontend/src/lib/rbac.ts`

---

## 🆘 Common Issues

### "Cannot find module '@/components/payment'"
**Solution**: Check your tsconfig.json has the `@` alias configured:
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### "User is null or undefined"
**Solution**: Make sure your auth system is setting the user in useAppStore

### "Hook called outside function component"
**Solution**: Make sure you're calling hooks at the top level of your component

### Components not styling correctly
**Solution**: Verify Tailwind CSS is properly configured and your globals.css imports Tailwind

---

## ✅ Verification Checklist

Before deploying to production:

- [ ] All API endpoints implemented and tested
- [ ] User authentication working correctly
- [ ] Role-based access control functioning
- [ ] Stripe integration connected (test mode)
- [ ] All components render without errors
- [ ] Mobile responsive design tested
- [ ] Loading states display properly
- [ ] Error handling works for failed requests
- [ ] Animations smooth on all devices
- [ ] Accessibility standards met (ARIA labels, keyboard nav)
- [ ] TypeScript compiles without errors
- [ ] No console errors in browser
- [ ] Cross-browser testing completed

---

**Ready to start building?** Import a component and start customizing! 🚀
