/**
 * Payment Ecosystem Types
 *
 * Type definitions for the Medium-style peer review payment system
 */

// ===========================
// SUBSCRIPTION TYPES
// ===========================

export interface Subscription {
  id: string;
  userId: string;
  stripeSubscriptionId: string;
  stripeCustomerId: string;
  stripePaymentMethodId?: string;
  status: 'active' | 'past_due' | 'canceled' | 'unpaid';
  planType: string;
  monthlyAmount: number; // in dollars
  payoutContribution: number; // in dollars
  currentPeriodStart: string;
  currentPeriodEnd: string;
  cancelAtPeriodEnd: boolean;
  canceledAt?: string;
  cancellationReason?: string;
  createdAt: string;
  updatedAt: string;
}

export interface SubscriptionCreateRequest {
  paymentMethodId: string;
  billingEmail: string;
  researcherProfile?: {
    orcid?: string;
    expertiseDomains?: string[];
    hIndex?: number;
    institution?: string;
  };
}

export interface SubscriptionResponse {
  subscriptionId: string;
  status: string;
  currentPeriodEnd: string;
  monthlyAmount: number;
  payoutContribution: number;
  nextBillingDate: string;
  stripeCustomerId: string;
}

// ===========================
// PAYOUT TYPES
// ===========================

export interface PayoutPool {
  id: string;
  poolMonth: string; // YYYY-MM-DD format
  totalContributions: number; // in dollars
  totalDistributed: number;
  remaining: number;
  totalReviewsAssigned: number;
  totalReviewsCompleted: number;
  totalReviewsApproved: number;
  payoutPerReview?: number;
  status: 'open' | 'calculating' | 'distributed' | 'closed';
  calculatedAt?: string;
  distributedAt?: string;
  closedAt?: string;
  poolMetadata?: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

export interface PayoutDistribution {
  id: string;
  poolId: string;
  reviewerId: string;
  reviewerName: string;
  approvedReviewsCount: number;
  payoutPerReview: number;
  totalPayout: number;
  stripeTransferId?: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'reversed';
  transferInitiatedAt?: string;
  transferCompletedAt?: string;
  failureReason?: string;
  destinationBankLast4?: string;
  estimatedArrivalDate?: string;
  createdAt: string;
}

export interface EarningsSummary {
  lifetimeEarnings: number;
  currentMonthPending: number;
  lastPayout?: {
    amount: number;
    date: string;
    reviewsCount: number;
    transferStatus: string;
  };
  earningsHistory: Array<{
    month: string;
    reviewsCompleted: number;
    reviewsApproved: number;
    payoutAmount: number;
    payoutDate: string;
    status: string;
  }>;
  currentMonthReviews: {
    assigned: number;
    completed: number;
    approved: number;
    pendingApproval: number;
    estimatedPayout: number;
  };
}

// ===========================
// REVIEW APPROVAL TYPES
// ===========================

export interface PendingReview {
  reviewId: string;
  manuscriptId: string;
  manuscriptTitle: string;
  reviewerName: string;
  submittedAt: string;
  reviewQualityPreview: {
    overallScore: number;
    strengthsCount: number;
    weaknessesCount: number;
    wordCount: number;
  };
}

export interface ReviewApprovalRequest {
  approved: boolean;
  qualityScore?: number;
  approvalNotes?: string;
  eligibleForPayout: boolean;
}

export interface ReviewApprovalResponse {
  reviewId: string;
  editorApproved: boolean;
  approvedBy: string;
  approvedAt: string;
  eligibleForPayout: boolean;
  addedToPool: string;
  estimatedPayout: number;
}

// ===========================
// ADMIN DASHBOARD TYPES
// ===========================

export interface AdminDashboardData {
  platformMetrics: {
    totalActiveSubscriptions: number;
    totalPayingMembers: number;
    monthlyRecurringRevenue: number;
    monthlyPayoutObligations: number;
    netMonthlyProfit: number;
  };
  currentMonthPool: {
    poolAmount: number;
    papersSubmitted: number;
    reviewsAssigned: number;
    reviewsCompleted: number;
    reviewsApproved: number;
    estimatedPayoutPerReview: number;
  };
  researcherPool: {
    totalResearchers: number;
    activeReviewers: number;
    averageHIndex: number;
    averageReviewsPerMonth: number;
  };
  recentActivity: Array<{
    timestamp: string;
    type: string;
    description: string;
  }>;
}

export interface ResearcherListItem {
  id: string;
  name: string;
  email: string;
  institution: string;
  hIndex?: number;
  expertiseDomains: string[];
  subscriptionStatus: string;
  isPayingMember: boolean;
  memberSince?: string;
  lifetimeReviews: number;
  lifetimeEarnings: number;
  averageReviewQuality: number;
  stripeConnectStatus: string;
}

export interface PayoutHistoryItem {
  month: string;
  totalPool: number;
  totalDistributed: number;
  reviewsApproved: number;
  payoutPerReview: number;
  uniqueReviewers: number;
  distributionDate: string;
  status: string;
}

// ===========================
// PAPER QUEUE TYPES
// ===========================

export interface PaperQueueItem {
  id: string;
  title: string;
  uploadDate: string;
  uploadedBy: string;
  status: 'pending_assignment' | 'under_review' | 'reviews_complete' | 'published';
  assignedReviewers: Array<{
    id: string;
    name: string;
    status: 'invited' | 'accepted' | 'declined' | 'completed';
  }>;
  reviewsCompleted: number;
  reviewsNeeded: number;
}

// ===========================
// STRIPE TYPES
// ===========================

export interface StripeConnectStatus {
  connected: boolean;
  accountId?: string;
  bankAccountLast4?: string;
  bankAccountName?: string;
  verified: boolean;
  status: 'not_connected' | 'pending' | 'verified' | 'restricted';
}

export interface PaymentMethod {
  id: string;
  brand: string; // 'visa', 'mastercard', etc.
  last4: string;
  expiryMonth: number;
  expiryYear: number;
}

// ===========================
// EDITOR DASHBOARD TYPES
// ===========================

export interface PaperUploadRequest {
  title: string;
  abstract: string;
  keywords: string[];
  methodology?: string;
  reviewCriteria?: string[];
  file?: File;
}

export interface ReviewerRecommendation {
  researcher: ResearcherListItem;
  matchScore: number;
  expertiseScore: number;
  availabilityScore: number;
  conflictRisk: number;
  reasoning: string;
  expertiseOverlap: string[];
}
