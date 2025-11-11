# Technical Design: Medium-Style Peer Review Payment Ecosystem

**Document Version**: 1.0
**Date**: November 11, 2025
**Architect**: Technical Solution Architect
**Project**: Meta-Analysis Tool - Payment Ecosystem Extension

---

## EXECUTIVE SUMMARY

### Feature Overview
Transform the existing peer review platform into a **Medium-style subscription payment ecosystem** where researchers pay $100/month, contribute $20 to a shared payout pool, and reviewers split the monthly pool proportionally based on completed approved reviews.

### Business Value
- **Revenue Model**: Sustainable $80/month profit per subscriber ($100 subscription - $20 payout contribution)
- **Reviewer Incentive**: Financial motivation for quality peer reviews ($20-40+ per review depending on participation)
- **Quality Assurance**: Editor approval gates ensure only quality reviews receive payment
- **Market Validation**: Proof-of-concept with 10 researchers, 2 papers demonstrates viability

### Recommended Technical Approach
- **Incremental Integration**: Extend existing FastAPI/PostgreSQL infrastructure
- **Stripe Standard Products**: Leverage Subscriptions API + Connect for payouts
- **Monthly Batch Processing**: Calculate and distribute payouts on first day of each month
- **Editor Quality Gate**: Manual approval workflow prevents gaming the system

### Key Architectural Decisions
1. **Database Extension**: Add 5 new tables to existing PostgreSQL schema (avoid separate payment DB)
2. **Stripe Integration**: Use Stripe Subscriptions + Connect (avoid PayPal complexity for MVP)
3. **Cron-Based Payouts**: Railway scheduled tasks trigger monthly payout calculations
4. **Existing Auth**: Leverage current User model and JWT authentication
5. **Role Enhancement**: Extend UserRole enum to include EDITOR, PAYING_MEMBER

---

## ARCHITECTURE DESIGN

### System Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js)                        │
├─────────────────────────────────────────────────────────────────┤
│  Researcher Dashboard  │  Editor Dashboard  │  Admin Dashboard   │
│  - Earnings Tracker    │  - Review Queue    │  - Pool Analytics  │
│  - Review Status       │  - Approval UI     │  - Researcher List │
│  - Payment History     │  - Paper Upload    │  - Payout Reports  │
└─────────────────────────────────────────────────────────────────┘
                              ↓ HTTPS/REST
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND API (FastAPI)                         │
├─────────────────────────────────────────────────────────────────┤
│  /api/v1/subscriptions  │  /api/v1/payouts  │  /api/v1/admin    │
│  - Subscribe/Cancel     │  - Calculate Pool │  - View Analytics  │
│  - Update Payment       │  - Distribute     │  - Export Reports  │
│  - Billing History      │  - Get Earnings   │  - Manage Users    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    POSTGRESQL DATABASE                           │
├─────────────────────────────────────────────────────────────────┤
│ EXISTING TABLES:                NEW PAYMENT TABLES:              │
│ - users                        - subscriptions                   │
│ - researchers                  - payout_pools                    │
│ - manuscripts                  - payout_contributions            │
│ - peer_reviews                 - review_completions              │
│ - reviewer_matches             - payout_distributions            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                             │
├─────────────────────────────────────────────────────────────────┤
│  Stripe API              │  Google Scholar   │  Railway Cron      │
│  - Subscriptions         │  - Profile Scrape │  - Monthly Payouts │
│  - Connect Payouts       │  - H-index Fetch  │  - Pool Calc       │
│  - Webhooks              │  - ORCID Verify   │  - Notifications   │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow Specifications

#### 1. Subscription Flow
```
User Signs Up
    ↓
POST /api/v1/subscriptions/create
    ↓
Create Stripe Subscription ($100/month)
    ↓
Save to `subscriptions` table
    ↓
Add $20 to `payout_pools` (current month)
    ↓
Return subscription_id + payment_url
```

#### 2. Review Completion Flow
```
Reviewer Submits Review
    ↓
POST /api/v1/peer-reviews (existing endpoint)
    ↓
Editor Approves Review
    ↓
POST /api/v1/peer-reviews/{id}/approve
    ↓
Create `review_completions` record
    ↓
Link to current `payout_pools` entry
    ↓
Increment reviewer's review count
```

#### 3. Monthly Payout Flow
```
Railway Cron (1st of month 00:00 UTC)
    ↓
POST /api/v1/payouts/calculate-monthly
    ↓
Query all approved reviews from previous month
    ↓
Calculate: payout_per_review = total_pool / approved_review_count
    ↓
For each reviewer:
    - Calculate: amount = payout_per_review × reviewer_review_count
    - Create Stripe Connect transfer
    - Save to `payout_distributions` table
    ↓
Send email notifications to reviewers
    ↓
Close previous month's pool
    ↓
Create new pool for current month
```

### Integration Points and Dependencies

#### Stripe Integration
- **Subscriptions API**: Recurring $100/month billing
- **Connect API**: Reviewer bank account connections + payouts
- **Webhooks**: Handle payment_succeeded, subscription_canceled events
- **Customer Portal**: Self-service subscription management

#### AI Profile Enrichment (Existing)
- **Google Scholar Scraper**: Extract h-index, publications, citations
- **ORCID API**: Verify researcher identity
- **Semantic Scholar API**: Additional publication metadata
- **Claude 3.5 Sonnet**: Profile completeness scoring

#### Existing System Integration
- **User Authentication**: JWT tokens (already implemented)
- **Researcher Model**: Extend with `stripe_connect_account_id`, `is_paying_member`
- **PeerReview Model**: Add `editor_approved`, `approved_by`, `approved_at`
- **ReviewerMatch Model**: Use existing expertise matching algorithm

### Technology Stack Rationale

#### Why Stripe Over PayPal?
- **Better Developer Experience**: Comprehensive APIs, webhooks, documentation
- **Connect Built-In**: Marketplace payouts without third-party integration
- **Compliance**: PCI-DSS compliant by default
- **Transparent Pricing**: 2.9% + 30¢ per transaction
- **Risk**: Requires US bank accounts for Connect (acceptable for US-based researchers)

#### Why PostgreSQL Over Separate Payment DB?
- **Data Integrity**: Foreign keys between payments and reviews
- **Transaction Safety**: ACID guarantees for financial operations
- **Simplicity**: Single database reduces operational complexity
- **Performance**: Join queries between payments and reviews are fast
- **Risk**: Single point of failure (mitigated by Railway backups)

#### Why Cron Over Real-Time Payouts?
- **Predictability**: Researchers know exactly when payouts occur
- **Fraud Prevention**: Time window to detect and reverse fraudulent reviews
- **Batch Efficiency**: Process all payouts in single Stripe API batch
- **Error Handling**: Manual intervention window for failed payouts
- **Risk**: Delayed gratification (mitigated by clear communication)

---

## DATABASE SCHEMA DESIGN

### New Tables (5 total)

#### 1. `subscriptions` - Track Researcher Subscriptions
```sql
CREATE TABLE subscriptions (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Stripe Integration
    stripe_subscription_id VARCHAR(255) UNIQUE NOT NULL,
    stripe_customer_id VARCHAR(255) NOT NULL,
    stripe_payment_method_id VARCHAR(255),

    -- Subscription Details
    status VARCHAR(50) NOT NULL DEFAULT 'active',
        -- active, past_due, canceled, unpaid
    plan_type VARCHAR(50) NOT NULL DEFAULT 'researcher_monthly',
    monthly_amount_cents INTEGER NOT NULL DEFAULT 10000, -- $100.00
    payout_contribution_cents INTEGER NOT NULL DEFAULT 2000, -- $20.00

    -- Billing Cycle
    current_period_start TIMESTAMP NOT NULL,
    current_period_end TIMESTAMP NOT NULL,
    trial_end TIMESTAMP,

    -- Cancellation
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    canceled_at TIMESTAMP,
    cancellation_reason TEXT,

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Indexes
    CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
    CREATE INDEX idx_subscriptions_status ON subscriptions(status);
    CREATE INDEX idx_subscriptions_stripe_customer ON subscriptions(stripe_customer_id);
);

-- Audit trigger for updates
CREATE TRIGGER update_subscriptions_updated_at
    BEFORE UPDATE ON subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

#### 2. `payout_pools` - Monthly Payout Pool Tracking
```sql
CREATE TABLE payout_pools (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Time Period
    pool_month DATE NOT NULL UNIQUE, -- First day of month (e.g., 2025-11-01)

    -- Pool Amounts (in cents)
    total_contributions_cents INTEGER NOT NULL DEFAULT 0,
    total_distributed_cents INTEGER NOT NULL DEFAULT 0,
    remaining_cents INTEGER NOT NULL DEFAULT 0,

    -- Review Counts
    total_reviews_assigned INTEGER NOT NULL DEFAULT 0,
    total_reviews_completed INTEGER NOT NULL DEFAULT 0,
    total_reviews_approved INTEGER NOT NULL DEFAULT 0,

    -- Payout Calculation
    payout_per_review_cents INTEGER, -- Calculated on pool close

    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'open',
        -- open, calculating, distributed, closed
    calculated_at TIMESTAMP,
    distributed_at TIMESTAMP,
    closed_at TIMESTAMP,

    -- Metadata
    pool_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Indexes
    CREATE INDEX idx_payout_pools_month ON payout_pools(pool_month);
    CREATE INDEX idx_payout_pools_status ON payout_pools(status);
);
```

#### 3. `payout_contributions` - Track Individual Subscription Contributions
```sql
CREATE TABLE payout_contributions (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys
    pool_id UUID NOT NULL REFERENCES payout_pools(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subscription_id UUID NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,

    -- Contribution Details
    contribution_amount_cents INTEGER NOT NULL DEFAULT 2000, -- $20.00
    billing_date TIMESTAMP NOT NULL,

    -- Stripe Details
    stripe_payment_intent_id VARCHAR(255),
    stripe_invoice_id VARCHAR(255),

    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
        -- pending, completed, failed, refunded

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Indexes
    CREATE INDEX idx_payout_contributions_pool ON payout_contributions(pool_id);
    CREATE INDEX idx_payout_contributions_user ON payout_contributions(user_id);
    CREATE INDEX idx_payout_contributions_subscription ON payout_contributions(subscription_id);

    -- Constraints
    UNIQUE(pool_id, subscription_id, billing_date)
);
```

#### 4. `review_completions` - Track Approved Reviews for Payout
```sql
CREATE TABLE review_completions (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys
    pool_id UUID NOT NULL REFERENCES payout_pools(id) ON DELETE CASCADE,
    peer_review_id UUID NOT NULL REFERENCES peer_reviews(id) ON DELETE CASCADE,
    reviewer_id UUID NOT NULL REFERENCES researchers(id) ON DELETE CASCADE,
    manuscript_id UUID NOT NULL REFERENCES manuscripts(id) ON DELETE CASCADE,

    -- Approval Details
    editor_id UUID REFERENCES users(id), -- Who approved the review
    approved_at TIMESTAMP NOT NULL DEFAULT NOW(),
    approval_notes TEXT,

    -- Review Quality Metrics
    quality_score FLOAT, -- 0.0 to 1.0
    completeness_score FLOAT,
    constructiveness_score FLOAT,

    -- Payout Eligibility
    eligible_for_payout BOOLEAN NOT NULL DEFAULT TRUE,
    ineligibility_reason TEXT,

    -- Payout Status
    payout_status VARCHAR(50) NOT NULL DEFAULT 'pending',
        -- pending, calculated, distributed, failed
    payout_amount_cents INTEGER,
    distributed_at TIMESTAMP,

    -- Metadata
    completion_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Indexes
    CREATE INDEX idx_review_completions_pool ON review_completions(pool_id);
    CREATE INDEX idx_review_completions_reviewer ON review_completions(reviewer_id);
    CREATE INDEX idx_review_completions_payout_status ON review_completions(payout_status);
    CREATE INDEX idx_review_completions_approved_at ON review_completions(approved_at);

    -- Constraints
    UNIQUE(peer_review_id) -- Each review can only be counted once
);
```

#### 5. `payout_distributions` - Track Individual Reviewer Payouts
```sql
CREATE TABLE payout_distributions (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys
    pool_id UUID NOT NULL REFERENCES payout_pools(id) ON DELETE CASCADE,
    reviewer_id UUID NOT NULL REFERENCES researchers(id) ON DELETE CASCADE,

    -- Payout Calculation
    approved_reviews_count INTEGER NOT NULL DEFAULT 0,
    payout_per_review_cents INTEGER NOT NULL,
    total_payout_cents INTEGER NOT NULL,

    -- Stripe Connect Details
    stripe_connect_account_id VARCHAR(255) NOT NULL,
    stripe_transfer_id VARCHAR(255) UNIQUE,
    stripe_payout_id VARCHAR(255),

    -- Transfer Status
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
        -- pending, processing, completed, failed, reversed
    transfer_initiated_at TIMESTAMP,
    transfer_completed_at TIMESTAMP,
    failure_reason TEXT,

    -- Banking Details
    destination_bank_last4 VARCHAR(4),
    destination_bank_name VARCHAR(255),
    estimated_arrival_date DATE,

    -- Notifications
    notification_sent BOOLEAN DEFAULT FALSE,
    notification_sent_at TIMESTAMP,

    -- Metadata
    distribution_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Indexes
    CREATE INDEX idx_payout_distributions_pool ON payout_distributions(pool_id);
    CREATE INDEX idx_payout_distributions_reviewer ON payout_distributions(reviewer_id);
    CREATE INDEX idx_payout_distributions_status ON payout_distributions(status);
    CREATE INDEX idx_payout_distributions_transfer_id ON payout_distributions(stripe_transfer_id);

    -- Constraints
    UNIQUE(pool_id, reviewer_id), -- One payout per reviewer per month
    CHECK (total_payout_cents >= 0),
    CHECK (approved_reviews_count >= 0)
);
```

### Existing Table Modifications

#### `users` - Add Payment Fields
```sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR(255) UNIQUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS stripe_connect_account_id VARCHAR(255) UNIQUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_paying_member BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS member_since TIMESTAMP;
ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_status VARCHAR(50) DEFAULT 'inactive';

CREATE INDEX idx_users_stripe_customer ON users(stripe_customer_id);
CREATE INDEX idx_users_stripe_connect ON users(stripe_connect_account_id);
CREATE INDEX idx_users_is_paying_member ON users(is_paying_member);
```

#### `researchers` - Add Payout Fields
```sql
ALTER TABLE researchers ADD COLUMN IF NOT EXISTS stripe_connect_account_id VARCHAR(255) UNIQUE;
ALTER TABLE researchers ADD COLUMN IF NOT EXISTS connect_account_status VARCHAR(50) DEFAULT 'not_connected';
ALTER TABLE researchers ADD COLUMN IF NOT EXISTS bank_account_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE researchers ADD COLUMN IF NOT EXISTS total_earnings_cents INTEGER DEFAULT 0;
ALTER TABLE researchers ADD COLUMN IF NOT EXISTS lifetime_reviews_paid INTEGER DEFAULT 0;
ALTER TABLE researchers ADD COLUMN IF NOT EXISTS last_payout_date TIMESTAMP;

CREATE INDEX idx_researchers_connect_account ON researchers(stripe_connect_account_id);
CREATE INDEX idx_researchers_connect_status ON researchers(connect_account_status);
```

#### `peer_reviews` - Add Approval Fields
```sql
ALTER TABLE peer_reviews ADD COLUMN IF NOT EXISTS editor_approved BOOLEAN DEFAULT FALSE;
ALTER TABLE peer_reviews ADD COLUMN IF NOT EXISTS approved_by UUID REFERENCES users(id);
ALTER TABLE peer_reviews ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP;
ALTER TABLE peer_reviews ADD COLUMN IF NOT EXISTS approval_notes TEXT;
ALTER TABLE peer_reviews ADD COLUMN IF NOT EXISTS eligible_for_payout BOOLEAN DEFAULT TRUE;

CREATE INDEX idx_peer_reviews_editor_approved ON peer_reviews(editor_approved);
CREATE INDEX idx_peer_reviews_approved_at ON peer_reviews(approved_at);
```

### Database Migration Strategy
```sql
-- Migration file: 0010_add_payment_ecosystem.sql

BEGIN;

-- Step 1: Create new tables (in dependency order)
CREATE TABLE subscriptions (...);
CREATE TABLE payout_pools (...);
CREATE TABLE payout_contributions (...);
CREATE TABLE review_completions (...);
CREATE TABLE payout_distributions (...);

-- Step 2: Modify existing tables
ALTER TABLE users ...;
ALTER TABLE researchers ...;
ALTER TABLE peer_reviews ...;

-- Step 3: Create helper functions
CREATE OR REPLACE FUNCTION get_current_payout_pool()
RETURNS UUID AS $$
    SELECT id FROM payout_pools
    WHERE pool_month = date_trunc('month', CURRENT_DATE)::DATE
    AND status = 'open'
    LIMIT 1;
$$ LANGUAGE SQL STABLE;

CREATE OR REPLACE FUNCTION calculate_reviewer_earnings(reviewer_uuid UUID)
RETURNS INTEGER AS $$
    SELECT COALESCE(SUM(total_payout_cents), 0)
    FROM payout_distributions
    WHERE reviewer_id = reviewer_uuid AND status = 'completed';
$$ LANGUAGE SQL STABLE;

-- Step 4: Seed initial data
INSERT INTO payout_pools (pool_month, status)
VALUES (date_trunc('month', CURRENT_DATE)::DATE, 'open');

COMMIT;
```

---

## API ENDPOINT SPECIFICATIONS

### Subscription Management

#### POST /api/v1/subscriptions/create
**Purpose**: Create new researcher subscription

**Request Body**:
```json
{
  "payment_method_id": "pm_1234567890",
  "billing_email": "researcher@university.edu",
  "researcher_profile": {
    "orcid": "0000-0001-2345-6789",
    "expertise_domains": ["cognitive psychology", "neuroscience"],
    "h_index": 25,
    "institution": "Stanford University"
  }
}
```

**Response** (201 Created):
```json
{
  "subscription_id": "sub_abc123",
  "status": "active",
  "current_period_end": "2025-12-11T00:00:00Z",
  "monthly_amount": 100.00,
  "payout_contribution": 20.00,
  "next_billing_date": "2025-12-11",
  "stripe_customer_id": "cus_xyz789"
}
```

**Business Logic**:
1. Validate payment method with Stripe
2. Create Stripe subscription ($100/month)
3. Create `subscriptions` record
4. Update `users.is_paying_member = TRUE`
5. Add $20 to current month's `payout_pools`
6. Trigger AI profile enrichment job
7. Send welcome email

**Error Handling**:
- 400: Payment method declined
- 409: User already has active subscription
- 500: Stripe API error (retry with exponential backoff)

---

#### POST /api/v1/subscriptions/{subscription_id}/cancel
**Purpose**: Cancel subscription at period end

**Request Body**:
```json
{
  "cancellation_reason": "Too expensive",
  "immediate": false
}
```

**Response** (200 OK):
```json
{
  "subscription_id": "sub_abc123",
  "status": "active",
  "cancel_at_period_end": true,
  "cancellation_effective_date": "2025-12-11T00:00:00Z",
  "final_billing_date": "2025-12-11"
}
```

**Business Logic**:
1. Call Stripe: `subscription.cancel(at_period_end=True)`
2. Update `subscriptions.cancel_at_period_end = TRUE`
3. Stop contributing to future payout pools
4. Preserve access until period end
5. Send cancellation confirmation email

---

#### GET /api/v1/subscriptions/me
**Purpose**: Get current user's subscription details

**Response** (200 OK):
```json
{
  "subscription": {
    "id": "sub_abc123",
    "status": "active",
    "plan_type": "researcher_monthly",
    "monthly_amount": 100.00,
    "current_period_start": "2025-11-11T00:00:00Z",
    "current_period_end": "2025-12-11T00:00:00Z",
    "cancel_at_period_end": false
  },
  "billing_history": [
    {
      "date": "2025-11-11",
      "amount": 100.00,
      "status": "paid",
      "invoice_url": "https://invoice.stripe.com/i/..."
    }
  ],
  "contribution_summary": {
    "total_contributed": 60.00,
    "months_active": 3,
    "next_contribution_date": "2025-12-11"
  }
}
```

---

### Payout Management

#### POST /api/v1/payouts/calculate-monthly
**Purpose**: Calculate and distribute monthly payouts (CRON trigger)

**Request Body**:
```json
{
  "pool_month": "2025-11-01",
  "dry_run": false
}
```

**Response** (200 OK):
```json
{
  "pool_month": "2025-11-01",
  "calculation_status": "completed",
  "summary": {
    "total_pool_amount": 200.00,
    "approved_reviews_count": 10,
    "payout_per_review": 20.00,
    "unique_reviewers": 8,
    "total_distributed": 200.00
  },
  "distributions": [
    {
      "reviewer_id": "researcher-uuid-1",
      "reviewer_name": "Dr. Sarah Johnson",
      "approved_reviews": 3,
      "payout_amount": 60.00,
      "stripe_transfer_id": "tr_1234",
      "status": "processing"
    }
  ],
  "failed_distributions": [],
  "next_pool_created": true
}
```

**Algorithm** (see detailed pseudocode below):
1. Close previous month's pool
2. Query all approved reviews from previous month
3. Calculate: `payout_per_review = total_pool / approved_reviews_count`
4. Group reviews by reviewer
5. For each reviewer:
   - Calculate: `amount = payout_per_review × reviewer_reviews`
   - Create Stripe Connect transfer
   - Save `payout_distributions` record
6. Update pool status to 'distributed'
7. Create new pool for current month
8. Send notification emails

---

#### GET /api/v1/payouts/earnings
**Purpose**: Get current user's earnings summary

**Response** (200 OK):
```json
{
  "lifetime_earnings": 180.00,
  "current_month_pending": 40.00,
  "last_payout": {
    "amount": 60.00,
    "date": "2025-11-01",
    "reviews_count": 3,
    "transfer_status": "completed"
  },
  "earnings_history": [
    {
      "month": "2025-11",
      "reviews_completed": 3,
      "reviews_approved": 3,
      "payout_amount": 60.00,
      "payout_date": "2025-12-01",
      "status": "completed"
    }
  ],
  "current_month_reviews": {
    "assigned": 5,
    "completed": 2,
    "approved": 2,
    "pending_approval": 0,
    "estimated_payout": 40.00
  }
}
```

---

#### GET /api/v1/payouts/pool/{pool_month}
**Purpose**: Get payout pool details for specific month

**Response** (200 OK):
```json
{
  "pool_month": "2025-11-01",
  "status": "distributed",
  "total_contributions": 200.00,
  "total_distributed": 200.00,
  "remaining": 0.00,
  "statistics": {
    "contributing_members": 10,
    "papers_reviewed": 2,
    "total_reviews_assigned": 10,
    "total_reviews_completed": 10,
    "total_reviews_approved": 10,
    "payout_per_review": 20.00,
    "unique_reviewers_paid": 8
  },
  "calculated_at": "2025-12-01T00:00:00Z",
  "distributed_at": "2025-12-01T00:05:00Z"
}
```

---

### Review Approval Workflow

#### POST /api/v1/peer-reviews/{review_id}/approve
**Purpose**: Editor approves review for payout eligibility

**Request Body**:
```json
{
  "approved": true,
  "quality_score": 0.85,
  "approval_notes": "Comprehensive review with actionable feedback",
  "eligible_for_payout": true
}
```

**Response** (200 OK):
```json
{
  "review_id": "review-uuid-1",
  "editor_approved": true,
  "approved_by": "editor-uuid",
  "approved_at": "2025-11-15T14:30:00Z",
  "eligible_for_payout": true,
  "added_to_pool": "2025-11-01",
  "estimated_payout": 20.00
}
```

**Business Logic**:
1. Verify current user has EDITOR role
2. Update `peer_reviews` record
3. Create `review_completions` record
4. Link to current month's `payout_pools`
5. Increment pool's `total_reviews_approved`
6. Notify reviewer of approval

---

#### GET /api/v1/peer-reviews/pending-approval
**Purpose**: Get reviews awaiting editor approval

**Response** (200 OK):
```json
{
  "total": 5,
  "pending_reviews": [
    {
      "review_id": "review-uuid-1",
      "manuscript_id": "manuscript-uuid",
      "manuscript_title": "The Role of Dopamine in Learning",
      "reviewer_name": "Dr. Sarah Johnson (Anonymous)",
      "submitted_at": "2025-11-14T10:00:00Z",
      "review_quality_preview": {
        "overall_score": 8.5,
        "strengths_count": 4,
        "weaknesses_count": 3,
        "word_count": 1250
      }
    }
  ]
}
```

---

### Admin Dashboard

#### GET /api/v1/admin/dashboard
**Purpose**: Master admin overview (REQUIRES ADMIN ROLE)

**Response** (200 OK):
```json
{
  "platform_metrics": {
    "total_active_subscriptions": 10,
    "total_paying_members": 10,
    "monthly_recurring_revenue": 1000.00,
    "monthly_payout_obligations": 200.00,
    "net_monthly_profit": 800.00
  },
  "current_month_pool": {
    "pool_amount": 200.00,
    "papers_submitted": 2,
    "reviews_assigned": 10,
    "reviews_completed": 8,
    "reviews_approved": 6,
    "estimated_payout_per_review": 33.33
  },
  "researcher_pool": {
    "total_researchers": 50,
    "active_reviewers": 25,
    "average_h_index": 22,
    "average_reviews_per_month": 2.5
  },
  "recent_activity": [
    {
      "timestamp": "2025-11-15T14:30:00Z",
      "type": "review_approved",
      "description": "Editor approved review by Dr. Sarah Johnson"
    }
  ]
}
```

---

#### GET /api/v1/admin/researchers
**Purpose**: View all researchers in the pool

**Query Parameters**:
- `page`: int (default 1)
- `page_size`: int (default 50)
- `is_paying_member`: bool (filter)
- `min_h_index`: int (filter)
- `sort_by`: string (h_index, earnings, reviews_count)

**Response** (200 OK):
```json
{
  "total": 50,
  "page": 1,
  "page_size": 50,
  "researchers": [
    {
      "id": "researcher-uuid-1",
      "name": "Dr. Sarah Johnson",
      "email": "sjohnson@stanford.edu",
      "institution": "Stanford University",
      "h_index": 35,
      "expertise_domains": ["cognitive psychology", "neuroscience"],
      "subscription_status": "active",
      "is_paying_member": true,
      "member_since": "2025-09-01T00:00:00Z",
      "lifetime_reviews": 12,
      "lifetime_earnings": 240.00,
      "average_review_quality": 0.88,
      "stripe_connect_status": "verified"
    }
  ]
}
```

---

#### GET /api/v1/admin/payouts/history
**Purpose**: View historical payout data

**Query Parameters**:
- `start_month`: date (e.g., "2025-09-01")
- `end_month`: date
- `export_format`: string (json, csv)

**Response** (200 OK):
```json
{
  "total_months": 3,
  "total_distributed": 600.00,
  "payout_history": [
    {
      "month": "2025-11-01",
      "total_pool": 200.00,
      "total_distributed": 200.00,
      "reviews_approved": 10,
      "payout_per_review": 20.00,
      "unique_reviewers": 8,
      "distribution_date": "2025-12-01",
      "status": "completed"
    }
  ]
}
```

---

## PAYOUT CALCULATION ALGORITHM

### Detailed Pseudocode

```python
def calculate_and_distribute_monthly_payouts(pool_month: date, dry_run: bool = False):
    """
    Calculate and distribute payouts for a specific month.

    Args:
        pool_month: First day of the month to process (e.g., 2025-11-01)
        dry_run: If True, calculate but don't execute transfers

    Returns:
        PayoutCalculationResult with summary and individual distributions
    """

    # Step 1: Retrieve the payout pool
    pool = PayoutPool.query.filter_by(
        pool_month=pool_month,
        status='open'
    ).first()

    if not pool:
        raise PayoutPoolNotFoundError(f"No open pool for {pool_month}")

    # Step 2: Validate pool has contributions
    if pool.total_contributions_cents == 0:
        log.warning(f"Pool {pool_month} has zero contributions")
        pool.status = 'closed'
        db.session.commit()
        return PayoutCalculationResult(
            pool_month=pool_month,
            status='skipped',
            reason='no_contributions'
        )

    # Step 3: Query all approved reviews for this month
    approved_reviews = ReviewCompletion.query.filter(
        ReviewCompletion.pool_id == pool.id,
        ReviewCompletion.eligible_for_payout == True,
        ReviewCompletion.payout_status == 'pending'
    ).all()

    total_approved_reviews = len(approved_reviews)

    # Step 4: Handle edge case - no approved reviews
    if total_approved_reviews == 0:
        log.warning(f"Pool {pool_month} has no approved reviews")
        pool.status = 'closed'
        pool.remaining_cents = pool.total_contributions_cents
        db.session.commit()

        # Roll over contributions to next month
        rollover_contributions_to_next_month(pool)

        return PayoutCalculationResult(
            pool_month=pool_month,
            status='rolled_over',
            reason='no_approved_reviews'
        )

    # Step 5: Calculate payout per review
    payout_per_review_cents = pool.total_contributions_cents // total_approved_reviews
    pool.payout_per_review_cents = payout_per_review_cents

    # Step 6: Group reviews by reviewer
    reviews_by_reviewer = defaultdict(list)
    for review_completion in approved_reviews:
        reviews_by_reviewer[review_completion.reviewer_id].append(review_completion)

    # Step 7: Calculate individual payouts
    distributions = []
    failed_distributions = []

    for reviewer_id, reviews in reviews_by_reviewer.items():
        reviewer = Researcher.query.get(reviewer_id)

        if not reviewer:
            log.error(f"Reviewer {reviewer_id} not found")
            continue

        # Calculate total payout for this reviewer
        review_count = len(reviews)
        total_payout_cents = payout_per_review_cents * review_count

        # Validate Stripe Connect account
        if not reviewer.stripe_connect_account_id:
            log.error(f"Reviewer {reviewer.name} has no Connect account")
            failed_distributions.append({
                'reviewer_id': reviewer_id,
                'reason': 'no_connect_account',
                'amount': total_payout_cents
            })
            continue

        # Create distribution record
        distribution = PayoutDistribution(
            pool_id=pool.id,
            reviewer_id=reviewer_id,
            approved_reviews_count=review_count,
            payout_per_review_cents=payout_per_review_cents,
            total_payout_cents=total_payout_cents,
            stripe_connect_account_id=reviewer.stripe_connect_account_id,
            status='pending'
        )

        if not dry_run:
            # Step 8: Execute Stripe Connect transfer
            try:
                transfer = stripe.Transfer.create(
                    amount=total_payout_cents,
                    currency='usd',
                    destination=reviewer.stripe_connect_account_id,
                    description=f"Peer review payouts for {pool_month.strftime('%B %Y')}",
                    metadata={
                        'pool_month': str(pool_month),
                        'review_count': review_count,
                        'payout_per_review': payout_per_review_cents / 100
                    }
                )

                distribution.stripe_transfer_id = transfer.id
                distribution.status = 'processing'
                distribution.transfer_initiated_at = datetime.utcnow()

                # Update review completions
                for review_completion in reviews:
                    review_completion.payout_status = 'distributed'
                    review_completion.payout_amount_cents = payout_per_review_cents
                    review_completion.distributed_at = datetime.utcnow()

                # Update researcher lifetime earnings
                reviewer.total_earnings_cents += total_payout_cents
                reviewer.lifetime_reviews_paid += review_count
                reviewer.last_payout_date = datetime.utcnow()

                distributions.append(distribution)

            except stripe.error.StripeError as e:
                log.error(f"Stripe transfer failed for reviewer {reviewer_id}: {e}")
                distribution.status = 'failed'
                distribution.failure_reason = str(e)
                failed_distributions.append({
                    'reviewer_id': reviewer_id,
                    'reason': str(e),
                    'amount': total_payout_cents
                })

        else:
            # Dry run - just record the calculation
            distributions.append(distribution)

        db.session.add(distribution)

    # Step 9: Update pool status
    pool.total_distributed_cents = sum(d.total_payout_cents for d in distributions)
    pool.remaining_cents = pool.total_contributions_cents - pool.total_distributed_cents
    pool.calculated_at = datetime.utcnow()

    if not dry_run:
        pool.status = 'distributed'
        pool.distributed_at = datetime.utcnow()

    db.session.commit()

    # Step 10: Send notification emails
    if not dry_run:
        for distribution in distributions:
            if distribution.status != 'failed':
                send_payout_notification_email(distribution)

    # Step 11: Close current pool and create next month's pool
    if not dry_run:
        close_payout_pool(pool)
        create_next_month_pool(pool_month)

    return PayoutCalculationResult(
        pool_month=pool_month,
        status='completed' if not dry_run else 'dry_run',
        total_pool_cents=pool.total_contributions_cents,
        total_distributed_cents=pool.total_distributed_cents,
        payout_per_review_cents=payout_per_review_cents,
        approved_reviews_count=total_approved_reviews,
        unique_reviewers_count=len(distributions),
        distributions=distributions,
        failed_distributions=failed_distributions
    )


def handle_edge_cases():
    """Handle special edge cases in payout calculation."""

    # Case 1: No reviews completed this month
    if approved_reviews_count == 0:
        # Roll over pool to next month
        next_month_pool = get_or_create_pool(next_month)
        next_month_pool.total_contributions_cents += current_pool.total_contributions_cents
        current_pool.status = 'rolled_over'
        return

    # Case 2: Partial month subscription
    # User subscribed mid-month → still contributes full $20
    # This is simpler than pro-rating and acceptable for MVP

    # Case 3: Reviewer has no Stripe Connect account
    # Mark distribution as failed, send email to set up account
    # Payout held in escrow (pool.remaining_cents)

    # Case 4: Stripe transfer fails (insufficient funds, frozen account)
    # Retry 3 times with exponential backoff
    # If still fails, mark as failed and alert admin

    # Case 5: Reviewer completed reviews but subscription canceled
    # Still eligible for payout for reviews done during active period

    # Case 6: Pool amount doesn't divide evenly
    # Remaining cents stay in pool.remaining_cents
    # Carry forward to next month as "bonus pool"
```

### Edge Case Handling Matrix

| Edge Case | Scenario | Solution | Impact |
|-----------|----------|----------|--------|
| **No Reviews Completed** | Pool has $200, but 0 approved reviews | Roll over entire pool to next month | Next month's reviewers get larger payouts |
| **Partial Month Subscription** | User subscribes on Nov 15 | Still contributes full $20 to Nov pool | Simplified billing, acceptable for MVP |
| **Uneven Division** | $200 pool ÷ 9 reviews = $22.22 per review | Round down to $22, keep $2 in `remaining_cents` | Carry forward to next month |
| **No Connect Account** | Reviewer has no bank account linked | Mark distribution as `failed`, hold funds in escrow | Email reviewer to set up Connect |
| **Stripe Transfer Fails** | Bank rejects transfer | Retry 3x with exponential backoff, then mark failed | Manual intervention required |
| **Subscription Canceled Mid-Month** | User cancels on Nov 15 after contributing | Contribution stays in pool, reviews still eligible | Fair for other reviewers |
| **Review Approved After Month End** | Editor approves review on Dec 2 for Nov paper | Count toward December pool instead | Encourages timely editor approvals |

---

## ENHANCED ONBOARDING FLOW

### Researcher Onboarding Process

#### Phase 1: Account Creation (3 minutes)
```
User visits /signup
    ↓
POST /api/v1/auth/register
    - email, password, full_name, institution
    ↓
Create User account (is_paying_member = FALSE)
    ↓
Send email verification link
    ↓
User verifies email
    ↓
Redirect to /onboarding/profile
```

#### Phase 2: Profile Enrichment (5 minutes)
```
Display profile form with fields:
    - ORCID (optional but recommended)
    - Google Scholar ID (optional)
    - Semantic Scholar ID (optional)
    - Expertise domains (multi-select: cognitive, clinical, social, etc.)
    - Primary research areas (free text, AI suggests based on keywords)
    - H-index (auto-filled if ORCID provided)
    - Publication count (auto-filled)
    - Career stage (PhD student, postdoc, assistant prof, etc.)
    - Willing to review? (yes/no)
    - Review capacity (1-3 papers/month, 4-6, 7+)
    ↓
User clicks "Auto-Fill from ORCID"
    ↓
AI Agent scrapes ORCID profile:
    - Parse publication list
    - Extract research keywords from paper titles
    - Calculate h-index if not provided
    - Extract collaborator network
    - Detect primary research domains
    ↓
AI Agent scrapes Google Scholar (if ID provided):
    - Verify h-index
    - Get total citations
    - Extract co-author list
    ↓
AI Claude analyzes profile:
    - Generate expertise summary
    - Suggest additional research domains
    - Calculate profile completeness score (0-100%)
    ↓
Display enriched profile for user review
    ↓
User confirms/edits profile
    ↓
POST /api/v1/researchers/create-profile
    ↓
Create Researcher record linked to User
```

#### Phase 3: Payment Setup (2 minutes)
```
Display subscription options:
    - Researcher Monthly: $100/month
        • Upload unlimited papers
        • Get matched with 5 expert reviewers per paper
        • Earn $20-40+ per review completed
        • Access AI review assistant
    ↓
User clicks "Subscribe"
    ↓
Redirect to Stripe Checkout:
    - Collect payment method
    - Show clear breakdown: $80 platform fee, $20 payout pool
    ↓
Stripe webhook: payment_intent.succeeded
    ↓
POST /api/v1/subscriptions/create (internal)
    ↓
Update User: is_paying_member = TRUE
    ↓
Add $20 to current payout_pools
    ↓
Send welcome email with next steps
```

#### Phase 4: Reviewer Setup (Optional, 3 minutes)
```
If user selected "willing to review":
    ↓
Display Stripe Connect onboarding:
    - "Set up your bank account to receive review payouts"
    - Show estimated earnings: "Average reviewer earns $60-120/month"
    ↓
User clicks "Connect Bank Account"
    ↓
Redirect to Stripe Connect onboarding flow:
    - Collect bank account details
    - Verify identity (SSN for US, equivalent for other countries)
    - Accept Connect terms
    ↓
Stripe webhook: account.updated
    ↓
Update Researcher: stripe_connect_account_id, connect_account_status = 'verified'
    ↓
Add researcher to reviewer matching pool
    ↓
Send confirmation email: "You're ready to earn!"
```

### Data Collected from Researchers

#### Required Fields (Manual Entry)
- Email address
- Password
- Full name
- Institution
- Consent to terms

#### Highly Recommended Fields (Manual Entry)
- ORCID ID
- Google Scholar ID
- Expertise domains (checkboxes)
- Primary research areas (keywords)
- Career stage
- Review capacity

#### Auto-Enriched Fields (AI Agent)
- H-index (from ORCID or Google Scholar)
- i10-index
- Total citations
- Publication count
- Co-author network (list of researcher IDs)
- Research keywords (extracted from paper titles)
- Trending research areas (detected from recent publications)
- Profile completeness score (0-100%)

#### Financial Fields (Stripe)
- Stripe customer ID (subscriptions)
- Stripe Connect account ID (payouts)
- Bank account last 4 digits
- Payment method brand (Visa, Mastercard, etc.)

### AI Profile Enrichment Logic

```python
async def enrich_researcher_profile(orcid: str, google_scholar_id: Optional[str] = None):
    """
    Use AI to automatically enrich researcher profile from external sources.

    Steps:
    1. Scrape ORCID API for publication list
    2. Scrape Google Scholar for h-index and citations
    3. Use Claude to analyze publications and extract expertise
    4. Generate profile completeness score
    """

    # Step 1: Fetch ORCID data
    orcid_data = await fetch_orcid_profile(orcid)
    publications = orcid_data.get('works', [])

    # Step 2: Fetch Google Scholar data (if available)
    if google_scholar_id:
        scholar_data = await scrape_google_scholar(google_scholar_id)
        h_index = scholar_data.get('h_index')
        total_citations = scholar_data.get('total_citations')
        coauthors = scholar_data.get('coauthors', [])
    else:
        h_index = calculate_h_index_from_orcid(publications)
        total_citations = sum(p.get('citation_count', 0) for p in publications)
        coauthors = []

    # Step 3: Extract research keywords using Claude
    publication_titles = [p['title'] for p in publications[:50]]  # Most recent 50

    prompt = f"""Analyze these publication titles from a researcher's profile:

{json.dumps(publication_titles, indent=2)}

Extract:
1. Primary research domains (cognitive psychology, neuroscience, etc.)
2. Specific expertise areas (working memory, decision-making, etc.)
3. Research methodologies (fMRI, behavioral experiments, meta-analysis, etc.)
4. Trending topics (recent research directions)

Return JSON:
{{
    "domains": ["domain1", "domain2"],
    "expertise_keywords": ["keyword1", "keyword2"],
    "methodologies": ["method1", "method2"],
    "trending_areas": ["trend1", "trend2"]
}}
"""

    claude_response = await claude_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    expertise_data = json.loads(claude_response.content[0].text)

    # Step 4: Calculate profile completeness
    completeness_score = calculate_completeness_score({
        'has_orcid': bool(orcid),
        'has_google_scholar': bool(google_scholar_id),
        'has_h_index': h_index is not None,
        'has_publications': len(publications) > 0,
        'has_expertise_keywords': len(expertise_data['expertise_keywords']) > 0,
        'has_coauthors': len(coauthors) > 0
    })

    return {
        'h_index': h_index,
        'total_citations': total_citations,
        'publication_count': len(publications),
        'expertise_domains': expertise_data['domains'],
        'expertise_keywords': expertise_data['expertise_keywords'],
        'research_methodologies': expertise_data['methodologies'],
        'trending_areas': expertise_data['trending_areas'],
        'coauthor_ids': coauthors,
        'profile_completeness': completeness_score
    }


def calculate_completeness_score(profile_data: dict) -> float:
    """
    Calculate profile completeness score (0-100%).

    Scoring:
    - ORCID: 20 points
    - Google Scholar: 15 points
    - H-index: 15 points
    - Publications: 15 points
    - Expertise keywords: 15 points
    - Co-authors: 10 points
    - Institution: 10 points
    """
    score = 0

    if profile_data.get('has_orcid'):
        score += 20
    if profile_data.get('has_google_scholar'):
        score += 15
    if profile_data.get('has_h_index'):
        score += 15
    if profile_data.get('has_publications'):
        score += 15
    if profile_data.get('has_expertise_keywords'):
        score += 15
    if profile_data.get('has_coauthors'):
        score += 10
    if profile_data.get('has_institution'):
        score += 10

    return min(score, 100)
```

---

## DASHBOARD DESIGNS

### Master Admin Dashboard

#### Layout Structure
```
┌─────────────────────────────────────────────────────────────┐
│  Admin Dashboard                                  [Logout]  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Platform Overview                                           │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │ Active Subs  │ │ Monthly MRR  │ │ Net Profit   │        │
│  │    10        │ │   $1,000     │ │    $800      │        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
│                                                               │
│  Current Month Payout Pool (November 2025)                   │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Total Pool: $200.00                                      ││
│  │ Reviews Assigned: 10  |  Completed: 8  |  Approved: 6   ││
│  │ Estimated Payout/Review: $33.33                          ││
│  │ [Close Pool & Distribute Payouts]                        ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│  Researcher Pool                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Name              | H-Index | Reviews | Earnings | Status││
│  │ Dr. Sarah Johnson |   35    |    12   | $240.00  | Active││
│  │ Dr. Michael Chen  |   28    |     8   | $160.00  | Active││
│  │ [View All Researchers] [Export CSV]                      ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│  Paper Queue                                                 │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Title                        | Status      | Reviews     ││
│  │ The Role of Dopamine...      | In Review   | 3/5 Done   ││
│  │ Cognitive Load and Memory... | Submitted   | 0/5 Done   ││
│  │ [View All Papers]                                        ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│  Payout History                                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Month      | Pool    | Distributed | Reviews | Status   ││
│  │ Nov 2025   | $200.00 | $0.00       |    6    | Open     ││
│  │ Oct 2025   | $200.00 | $200.00     |   10    | Closed   ││
│  │ [View All History] [Export CSV]                          ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

#### Key Features
- **Real-time Metrics**: Live updates via WebSocket
- **One-Click Actions**: Distribute payouts, export reports
- **Drill-Down**: Click any metric to see detailed breakdown
- **Alerts**: Highlight issues (failed payouts, low review completion rate)

---

### Editor Dashboard

#### Layout Structure
```
┌─────────────────────────────────────────────────────────────┐
│  Editor Dashboard - Dr. Jane Smith                [Logout]  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Paper Queue (2 papers awaiting action)                      │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ [+ Upload New Paper]                                     ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│  Active Papers                                               │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Title: The Role of Dopamine in Learning                 ││
│  │ Submitted: Nov 10, 2025  |  Status: In Review           ││
│  │ Reviews: 3/5 Completed                                   ││
│  │                                                           ││
│  │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        ││
│  │ │ Review #1   │ │ Review #2   │ │ Review #3   │        ││
│  │ │ Submitted   │ │ Submitted   │ │ In Progress │        ││
│  │ │ [Approve]   │ │ [Approve]   │ │ Waiting...  │        ││
│  │ └─────────────┘ └─────────────┘ └─────────────┘        ││
│  │                                                           ││
│  │ [Assign Additional Reviewers] [View Full Paper]         ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│  Review Approval Queue (3 reviews pending)                   │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Review by Dr. Sarah Johnson (Anonymous)                 ││
│  │ Manuscript: The Role of Dopamine...                      ││
│  │ Submitted: Nov 14, 2025                                  ││
│  │ Overall Score: 8.5 | Recommendation: Minor Revision     ││
│  │                                                           ││
│  │ [View Full Review]                                       ││
│  │ Quality Assessment:                                      ││
│  │ ☑ Comprehensive feedback                                 ││
│  │ ☑ Specific citations to manuscript sections              ││
│  │ ☑ Actionable improvement suggestions                     ││
│  │ ☐ Tone is constructive and professional                  ││
│  │                                                           ││
│  │ [✓ Approve for Payout] [✗ Reject (No Payout)]           ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

#### Key Features
- **Upload Paper**: Drag-and-drop PDF + auto-extract title/abstract
- **Review Approval**: Side-by-side view of manuscript + review
- **Quality Checklist**: Guided criteria for approval decisions
- **Reviewer Management**: Manually assign reviewers from pool
- **Email Templates**: Send feedback to authors

---

### Researcher Dashboard

#### Layout Structure
```
┌─────────────────────────────────────────────────────────────┐
│  Researcher Dashboard - Dr. Sarah Johnson         [Logout]  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Earnings Overview                                           │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────┐│
│  │ Lifetime Earnings│ │ This Month Pending│ │ Next Payout  ││
│  │    $240.00       │ │     $60.00        │ │  Dec 1       ││
│  └──────────────────┘ └──────────────────┘ └──────────────┘│
│                                                               │
│  Review Activity (November 2025)                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Assigned: 5  |  Completed: 3  |  Approved: 3  |  Paid: 0││
│  │ Estimated Payout: $60.00 (based on 3 approved reviews)  ││
│  │ [View All Reviews]                                       ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│  Current Review Assignments                                  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Title: Cognitive Load and Working Memory                ││
│  │ Assigned: Nov 12  |  Due: Nov 26  |  Days Left: 11      ││
│  │ [Start Review] [Decline]                                 ││
│  │                                                           ││
│  │ Title: The Impact of Sleep on Consolidation             ││
│  │ Assigned: Nov 15  |  Due: Nov 29  |  Days Left: 14      ││
│  │ [Start Review] [Decline]                                 ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│  Payment History                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Month    | Reviews | Amount  | Status    | Transfer ID  ││
│  │ Oct 2025 |    3    | $60.00  | Completed | tr_1234...   ││
│  │ Sep 2025 |    5    | $100.00 | Completed | tr_5678...   ││
│  │ [View All] [Download Statements]                         ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│  Subscription Management                                     │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Plan: Researcher Monthly ($100/month)                    ││
│  │ Next Billing: Dec 11, 2025                               ││
│  │ Payment Method: Visa •••• 4242                           ││
│  │ [Update Payment Method] [Cancel Subscription]            ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

#### Key Features
- **Earnings Tracker**: Real-time pending earnings estimate
- **Review Queue**: All assigned reviews with deadlines
- **Payment History**: Downloadable transaction statements
- **Self-Service**: Update payment method, cancel subscription
- **Notifications**: Email alerts for new assignments, approvals, payouts

---

## IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Week 1-2) - 2 weeks
**Goal**: Core payment infrastructure + database schema

#### Tasks
1. **Database Schema Implementation** (3 days)
   - Task ID: PAY-101
   - Scope: Create 5 new tables (subscriptions, payout_pools, etc.)
   - Dependencies: Existing PostgreSQL database
   - Acceptance: Migration runs successfully, all foreign keys valid
   - Effort: 1 developer-day

2. **Stripe Account Setup** (2 days)
   - Task ID: PAY-102
   - Scope: Create Stripe account, configure webhooks, test API keys
   - Dependencies: Business bank account
   - Acceptance: Successfully create test subscription and transfer
   - Effort: 0.5 developer-days

3. **Subscription API Endpoints** (5 days)
   - Task ID: PAY-103
   - Scope: Implement /api/v1/subscriptions/* endpoints
   - Dependencies: Stripe setup, database schema
   - Acceptance: Create, cancel, update subscription via API
   - Effort: 3 developer-days

4. **Payout Pool Management** (3 days)
   - Task ID: PAY-104
   - Scope: Auto-create monthly pools, track contributions
   - Dependencies: Subscription endpoints
   - Acceptance: Pool auto-creates on first subscription, tracks $20 contributions
   - Effort: 2 developer-days

**Phase 1 Deliverables**:
- Database migrations complete
- Stripe integration working
- Users can subscribe and contribute to pool
- Monthly pools auto-create

---

### Phase 2: Review Approval Workflow (Week 3) - 1 week
**Goal**: Editor approval gates for review quality

#### Tasks
1. **Extend PeerReview Model** (1 day)
   - Task ID: PAY-201
   - Scope: Add editor_approved, approved_by, approved_at fields
   - Dependencies: Phase 1 database
   - Acceptance: Reviews can be marked as approved/rejected
   - Effort: 0.5 developer-days

2. **Editor Approval API** (3 days)
   - Task ID: PAY-202
   - Scope: POST /api/v1/peer-reviews/{id}/approve
   - Dependencies: Extended PeerReview model
   - Acceptance: Editor can approve/reject review, creates review_completions record
   - Effort: 2 developer-days

3. **Editor Dashboard Backend** (2 days)
   - Task ID: PAY-203
   - Scope: GET /api/v1/peer-reviews/pending-approval
   - Dependencies: Editor approval API
   - Acceptance: Returns list of reviews awaiting approval
   - Effort: 1 developer-day

**Phase 2 Deliverables**:
- Editors can approve/reject reviews
- Approved reviews linked to payout pools
- Review completions tracked

---

### Phase 3: Payout Calculation (Week 4) - 1 week
**Goal**: Automated monthly payout calculation and distribution

#### Tasks
1. **Payout Algorithm Implementation** (4 days)
   - Task ID: PAY-301
   - Scope: POST /api/v1/payouts/calculate-monthly
   - Dependencies: Phase 2 complete
   - Acceptance: Correctly calculates payout_per_review, groups by reviewer
   - Effort: 3 developer-days

2. **Stripe Connect Integration** (3 days)
   - Task ID: PAY-302
   - Scope: Create transfers to reviewer Connect accounts
   - Dependencies: Payout algorithm
   - Acceptance: Successfully transfers $20 to test Connect account
   - Effort: 2 developer-days

3. **Edge Case Handling** (2 days)
   - Task ID: PAY-303
   - Scope: Handle no reviews, failed transfers, rollover logic
   - Dependencies: Payout algorithm
   - Acceptance: All edge cases from matrix handled gracefully
   - Effort: 2 developer-days

4. **Cron Job Setup** (1 day)
   - Task ID: PAY-304
   - Scope: Railway scheduled task to trigger payouts on 1st of month
   - Dependencies: Payout algorithm complete
   - Acceptance: Cron triggers at 00:00 UTC on 1st of month
   - Effort: 0.5 developer-days

**Phase 3 Deliverables**:
- Monthly payouts calculated automatically
- Funds transferred to reviewers via Stripe Connect
- Edge cases handled robustly
- Cron job runs reliably

---

### Phase 4: Enhanced Onboarding (Week 5) - 1 week
**Goal**: AI-powered researcher profile enrichment

#### Tasks
1. **Profile Form Frontend** (2 days)
   - Task ID: PAY-401
   - Scope: Multi-step form (account → profile → payment → reviewer setup)
   - Dependencies: None (can start in parallel)
   - Acceptance: User can complete all 4 onboarding steps
   - Effort: 2 developer-days

2. **AI Profile Enrichment Service** (4 days)
   - Task ID: PAY-402
   - Scope: Scrape ORCID, Google Scholar, use Claude for analysis
   - Dependencies: None
   - Acceptance: Auto-fills h-index, keywords, publications from ORCID
   - Effort: 3 developer-days

3. **Stripe Connect Onboarding** (2 days)
   - Task ID: PAY-403
   - Scope: Redirect to Stripe Connect, handle webhooks
   - Dependencies: Phase 3 Connect integration
   - Acceptance: Reviewer can link bank account, status updates correctly
   - Effort: 1 developer-day

**Phase 4 Deliverables**:
- Smooth onboarding experience
- AI auto-enriches profiles from ORCID/Scholar
- Reviewers can set up payouts during onboarding

---

### Phase 5: Dashboards (Week 6-7) - 2 weeks
**Goal**: Admin, Editor, and Researcher dashboards

#### Tasks
1. **Admin Dashboard Backend** (3 days)
   - Task ID: PAY-501
   - Scope: GET /api/v1/admin/dashboard, /admin/researchers, /admin/payouts/history
   - Dependencies: All previous phases
   - Acceptance: Returns all metrics from design spec
   - Effort: 2 developer-days

2. **Admin Dashboard Frontend** (4 days)
   - Task ID: PAY-502
   - Scope: Next.js pages with charts, tables, export buttons
   - Dependencies: Admin backend API
   - Acceptance: Matches design wireframe
   - Effort: 3 developer-days

3. **Editor Dashboard Frontend** (4 days)
   - Task ID: PAY-503
   - Scope: Paper queue, review approval UI
   - Dependencies: Phase 2 complete
   - Acceptance: Editor can approve reviews via UI
   - Effort: 3 developer-days

4. **Researcher Dashboard Frontend** (3 days)
   - Task ID: PAY-504
   - Scope: Earnings tracker, payment history, subscription management
   - Dependencies: Phase 1-3 complete
   - Acceptance: Researcher sees real-time earnings estimate
   - Effort: 2 developer-days

**Phase 5 Deliverables**:
- Fully functional admin dashboard
- Editor can manage reviews via UI
- Researchers can track earnings and payments

---

### Phase 6: Testing & Polish (Week 8) - 1 week
**Goal**: End-to-end testing with 10 researchers, 2 papers

#### Tasks
1. **Integration Testing** (3 days)
   - Task ID: PAY-601
   - Scope: Test full flow: subscribe → review → approve → payout
   - Dependencies: All phases complete
   - Acceptance: All 10 test users can complete workflow
   - Effort: 2 developer-days

2. **Stripe Webhook Testing** (2 days)
   - Task ID: PAY-602
   - Scope: Test all webhook events (payment_succeeded, transfer_failed, etc.)
   - Dependencies: Stripe integration
   - Acceptance: Webhooks trigger correct database updates
   - Effort: 1 developer-day

3. **Email Notifications** (2 days)
   - Task ID: PAY-603
   - Scope: Welcome email, payout notification, approval notification
   - Dependencies: All phases
   - Acceptance: Users receive emails at key milestones
   - Effort: 1 developer-day

4. **Bug Fixes & Polish** (2 days)
   - Task ID: PAY-604
   - Scope: Fix issues found during testing
   - Dependencies: Testing phase
   - Acceptance: All critical bugs resolved
   - Effort: 2 developer-days

**Phase 6 Deliverables**:
- Proof-of-concept tested with 10 real researchers
- All critical bugs fixed
- Email notifications working
- Ready for production launch

---

### Timeline Summary

| Phase | Duration | Start | End | Key Milestone |
|-------|----------|-------|-----|---------------|
| Phase 1: Foundation | 2 weeks | Week 1 | Week 2 | Subscriptions working |
| Phase 2: Review Approval | 1 week | Week 3 | Week 3 | Editor approval flow |
| Phase 3: Payout Calculation | 1 week | Week 4 | Week 4 | Automated payouts |
| Phase 4: Onboarding | 1 week | Week 5 | Week 5 | AI profile enrichment |
| Phase 5: Dashboards | 2 weeks | Week 6 | Week 7 | All UIs complete |
| Phase 6: Testing | 1 week | Week 8 | Week 8 | Production ready |

**Total Duration**: 8 weeks (2 months)

**Critical Path**: Phase 1 → Phase 2 → Phase 3 (Core payment flow must be sequential)

**Parallelizable**: Phase 4 (Onboarding) can start during Phase 3

---

## RISK ANALYSIS

### Technical Risks

#### Risk 1: Stripe Connect Complexity
**Impact**: High
**Probability**: Medium
**Description**: Stripe Connect onboarding requires identity verification, which can fail or take days for some reviewers.

**Mitigation**:
- Use Stripe Connect Express accounts (simplified onboarding)
- Provide clear documentation with screenshots
- Hold failed payouts in escrow, retry next month
- Support email for Connect issues

**Fallback**: Allow manual payout via PayPal as backup

---

#### Risk 2: Monthly Payout Timing
**Impact**: Medium
**Probability**: Low
**Description**: Cron job fails to run on 1st of month, delaying payouts.

**Mitigation**:
- Use Railway's built-in cron scheduler (99.9% uptime)
- Add monitoring: alert if cron doesn't run by 01:00 UTC
- Manual trigger endpoint: POST /api/v1/payouts/calculate-monthly
- Test cron extensively in staging

**Fallback**: Admin can manually trigger payouts from dashboard

---

#### Risk 3: Database Transaction Failures
**Impact**: High
**Probability**: Low
**Description**: Payout distribution partially fails, leaving inconsistent state (some reviewers paid, some not).

**Mitigation**:
- Wrap payout calculation in PostgreSQL transaction
- Use two-phase commit: calculate first, then distribute
- Mark distributions as 'pending' before Stripe transfer
- Retry failed transfers with exponential backoff
- Admin dashboard shows failed distributions for manual review

**Fallback**: Manual intervention to complete failed payouts

---

#### Risk 4: Fraudulent Reviews
**Impact**: High
**Probability**: Medium
**Description**: Reviewers submit low-quality reviews to game the payout system.

**Mitigation**:
- **Editor Approval Gate**: Only approved reviews count toward payout
- **Quality Metrics**: Track review quality score, constructiveness
- **Pattern Detection**: Flag reviewers with unusually high submission rate
- **Blacklist**: Remove bad actors from reviewer pool
- **Reputation System**: Future enhancement to weight payouts by quality

**Fallback**: Admin can manually reverse payouts for fraudulent reviews

---

#### Risk 5: Insufficient Reviewer Pool
**Impact**: Medium
**Probability**: Medium
**Description**: Not enough qualified reviewers for all papers, leading to slow turnaround.

**Mitigation**:
- **Aggressive Recruiting**: Incentivize researchers to invite colleagues
- **Referral Bonuses**: $20 bonus for referring paying member
- **Lower Barriers**: Allow non-paying members to review (no payout)
- **Fallback Matching**: If <5 reviewers found, assign fewer (3 minimum)

**Fallback**: Editor manually recruits external reviewers

---

#### Risk 6: Stripe Rate Limits
**Impact**: Low
**Probability**: Low
**Description**: Monthly payout distribution hits Stripe API rate limit (100 transfers/second).

**Mitigation**:
- Batch transfers in groups of 50
- Add 1-second delay between batches
- Use Stripe's bulk transfer API (planned for future)
- Monitor rate limit headers, exponential backoff

**Fallback**: Payout calculation takes 5-10 minutes instead of 1 minute

---

### Business Risks

#### Risk 7: Low Review Completion Rate
**Impact**: High
**Probability**: Medium
**Description**: Reviewers accept assignments but don't complete, leading to large pool with $0 payout.

**Mitigation**:
- **Deadline Enforcement**: Remove non-responsive reviewers from pool
- **Reminders**: Email reminders 3 days before deadline
- **Reputation Score**: Track completion rate, prioritize reliable reviewers
- **Pool Rollover**: If no completions, roll pool to next month (no loss)

**Fallback**: Editor assigns backup reviewers from waiting list

---

#### Risk 8: Regulatory Compliance (1099 Tax Reporting)
**Impact**: High
**Probability**: High
**Description**: US reviewers earning >$600/year require 1099 tax forms, adding compliance burden.

**Mitigation**:
- **Stripe Tax**: Use Stripe Tax product to auto-generate 1099s
- **W-9 Collection**: Collect W-9 forms during Connect onboarding
- **Accountant Review**: Hire tax professional to review setup
- **Geographic Restriction**: MVP limited to US reviewers (simplifies compliance)

**Fallback**: Manual 1099 generation via accountant

---

#### Risk 9: Subscription Churn
**Impact**: Medium
**Probability**: Medium
**Description**: Researchers cancel subscriptions after papers are reviewed, reducing MRR.

**Mitigation**:
- **Annual Plans**: Offer 20% discount for annual subscriptions
- **Usage Analytics**: Track which features drive retention
- **Exit Surveys**: Understand why users cancel
- **Improved Value**: Add features (AI review assistant, analytics)

**Fallback**: Acceptable churn rate <10% is sustainable

---

### Security Risks

#### Risk 10: Payment Fraud
**Impact**: High
**Probability**: Low
**Description**: Stolen credit cards used to create subscriptions, leading to chargebacks.

**Mitigation**:
- **Stripe Radar**: Enable fraud detection (blocks risky cards)
- **3D Secure**: Require SCA (Strong Customer Authentication) for EU cards
- **Email Verification**: Require verified email before subscription
- **Manual Review**: Flag subscriptions from high-risk countries

**Fallback**: Refund fraudulent charges, ban accounts

---

#### Risk 11: Data Privacy (GDPR/CCPA)
**Impact**: High
**Probability**: Medium
**Description**: Storing payment data violates privacy regulations.

**Mitigation**:
- **Stripe PCI Compliance**: Never store raw card numbers
- **Data Minimization**: Only store Stripe customer IDs, not payment details
- **Privacy Policy**: Clearly disclose data usage
- **GDPR Compliance**: Right to erasure, data export

**Fallback**: Legal review before EU launch

---

## SUCCESS METRICS

### Proof-of-Concept Success Criteria (10 researchers, 2 papers)

#### Metric 1: Subscription Conversion
- **Target**: 10 out of 10 researchers complete subscription
- **Measurement**: `COUNT(subscriptions WHERE status = 'active')`
- **Success Threshold**: 100%

#### Metric 2: Review Completion Rate
- **Target**: 8 out of 10 assigned reviews completed
- **Measurement**: `completed_reviews / assigned_reviews`
- **Success Threshold**: ≥80%

#### Metric 3: Editor Approval Rate
- **Target**: 8 out of 8 completed reviews approved
- **Measurement**: `approved_reviews / submitted_reviews`
- **Success Threshold**: ≥90%

#### Metric 4: Payout Success Rate
- **Target**: All approved reviews successfully paid
- **Measurement**: `successful_distributions / total_distributions`
- **Success Threshold**: 100%

#### Metric 5: Average Payout per Review
- **Target**: $20-25 per review (validates business model)
- **Measurement**: `total_pool / approved_reviews`
- **Success Threshold**: ≥$20

#### Metric 6: Time to First Payout
- **Target**: Payouts distributed within 24 hours of month end
- **Measurement**: `distributed_at - pool_month_end`
- **Success Threshold**: <24 hours

#### Metric 7: User Satisfaction
- **Target**: Researchers and reviewers report positive experience
- **Measurement**: Post-POC survey (1-5 scale)
- **Success Threshold**: ≥4.0 average rating

---

## DEPLOYMENT PLAN

### Step 1: Database Migration (Week 8, Day 1)
```bash
# Connect to Railway PostgreSQL
railway connect

# Run migration
cd /Users/brandon/meta-analysis-tool/backend
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt payout*"
# Should show: payout_pools, payout_contributions, payout_distributions, review_completions

# Seed initial payout pool
psql $DATABASE_URL -c "INSERT INTO payout_pools (pool_month, status) VALUES (CURRENT_DATE, 'open');"
```

### Step 2: Environment Variables (Week 8, Day 1)
```bash
# Railway dashboard → Environment variables
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
ENABLE_PAYOUTS=true
PAYOUT_CRON_SCHEDULE="0 0 1 * *"  # First day of month, 00:00 UTC
```

### Step 3: Deploy Backend (Week 8, Day 1)
```bash
cd /Users/brandon/meta-analysis-tool/backend
git add .
git commit -m "Add payment ecosystem: subscriptions, payouts, approval workflow"
git push origin main

# Railway auto-deploys from GitHub
# Monitor: https://railway.app/project/your-project/deployments
```

### Step 4: Deploy Frontend (Week 8, Day 1)
```bash
cd /Users/brandon/meta-analysis-tool/frontend
git add .
git commit -m "Add payment dashboards: admin, editor, researcher"
git push origin main

# Vercel auto-deploys from GitHub
# Monitor: https://vercel.com/dashboard
```

### Step 5: Configure Stripe Webhooks (Week 8, Day 2)
```bash
# Stripe Dashboard → Webhooks
# Add endpoint: https://meta-analysis-tool-production.up.railway.app/api/v1/webhooks/stripe

# Select events:
- payment_intent.succeeded
- payment_intent.payment_failed
- customer.subscription.created
- customer.subscription.updated
- customer.subscription.deleted
- account.updated (Connect)
- transfer.created
- transfer.failed
```

### Step 6: Test End-to-End (Week 8, Day 2-3)
```bash
# Create test subscription
curl -X POST "https://meta-analysis-tool-production.up.railway.app/api/v1/subscriptions/create" \
  -H "Authorization: Bearer $TEST_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_method_id": "pm_card_visa",
    "billing_email": "test@example.com"
  }'

# Verify pool contribution
curl "https://meta-analysis-tool-production.up.railway.app/api/v1/payouts/pool/2025-11-01" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Submit and approve test review
# ... (detailed test script in QA docs)

# Manually trigger payout calculation (dry run)
curl -X POST "https://meta-analysis-tool-production.up.railway.app/api/v1/payouts/calculate-monthly" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"pool_month": "2025-11-01", "dry_run": true}'
```

### Step 7: Recruit 10 Test Researchers (Week 8, Day 3-7)
```bash
# Send invitation emails with promo code
# Onboard researchers through full flow
# Upload 2 real papers for review
# Monitor onboarding completion rate
```

### Step 8: Monitor First Month (Week 9-12)
```bash
# Daily checks:
- Review completion rate
- Editor approval backlog
- Subscription churn
- Stripe webhook success rate

# Weekly checks:
- Researcher satisfaction surveys
- Review quality metrics
- Payout accuracy

# End of month:
- Verify automatic payout distribution
- Confirm all reviewers received funds
- Collect feedback for iteration
```

---

## APPENDIX A: SQL QUERIES

### Query 1: Get Current Month Payout Pool Status
```sql
SELECT
    pool_month,
    total_contributions_cents / 100.0 AS total_pool,
    total_reviews_assigned,
    total_reviews_completed,
    total_reviews_approved,
    CASE
        WHEN total_reviews_approved > 0
        THEN total_contributions_cents / total_reviews_approved / 100.0
        ELSE 0
    END AS estimated_payout_per_review,
    status
FROM payout_pools
WHERE pool_month = DATE_TRUNC('month', CURRENT_DATE)::DATE;
```

### Query 2: Get Reviewer Earnings for Specific Month
```sql
SELECT
    r.name AS reviewer_name,
    pd.approved_reviews_count,
    pd.total_payout_cents / 100.0 AS payout_amount,
    pd.status,
    pd.transfer_completed_at
FROM payout_distributions pd
JOIN researchers r ON pd.reviewer_id = r.id
WHERE pd.pool_id = (
    SELECT id FROM payout_pools WHERE pool_month = '2025-11-01'
)
ORDER BY pd.total_payout_cents DESC;
```

### Query 3: Get All Pending Review Approvals
```sql
SELECT
    pr.id AS review_id,
    m.title AS manuscript_title,
    r.name AS reviewer_name,
    pr.submission_date,
    pr.overall_score,
    pr.recommendation
FROM peer_reviews pr
JOIN manuscripts m ON pr.manuscript_id = m.id
LEFT JOIN researchers r ON pr.reviewer_id = r.id
WHERE pr.status = 'submitted'
  AND pr.editor_approved = FALSE
ORDER BY pr.submission_date ASC;
```

### Query 4: Calculate Platform Revenue Metrics
```sql
SELECT
    DATE_TRUNC('month', s.created_at)::DATE AS month,
    COUNT(DISTINCT s.id) AS active_subscriptions,
    SUM(s.monthly_amount_cents) / 100.0 AS gross_revenue,
    SUM(s.payout_contribution_cents) / 100.0 AS payout_obligations,
    SUM(s.monthly_amount_cents - s.payout_contribution_cents) / 100.0 AS net_revenue
FROM subscriptions s
WHERE s.status = 'active'
GROUP BY month
ORDER BY month DESC;
```

---

## APPENDIX B: PYDANTIC MODELS

### Subscription Models
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SubscriptionCreate(BaseModel):
    """Request schema for creating a subscription."""
    payment_method_id: str = Field(..., description="Stripe payment method ID")
    billing_email: str = Field(..., description="Email for billing receipts")
    researcher_profile: Optional[dict] = Field(None, description="Researcher profile data")

class SubscriptionResponse(BaseModel):
    """Response schema for subscription."""
    id: str
    user_id: str
    stripe_subscription_id: str
    status: str
    monthly_amount: float
    payout_contribution: float
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    created_at: datetime

    class Config:
        from_attributes = True

class PayoutPoolResponse(BaseModel):
    """Response schema for payout pool."""
    id: str
    pool_month: str
    total_contributions: float
    total_distributed: float
    remaining: float
    total_reviews_assigned: int
    total_reviews_completed: int
    total_reviews_approved: int
    payout_per_review: Optional[float]
    status: str

    class Config:
        from_attributes = True
```

---

## APPENDIX C: STRIPE INTEGRATION CODE

### Subscription Creation
```python
import stripe
from app.core.config import get_settings

settings = get_settings()
stripe.api_key = settings.stripe_secret_key

async def create_subscription(
    user_id: UUID,
    payment_method_id: str,
    db: AsyncSession
) -> dict:
    """
    Create a Stripe subscription for a researcher.

    Returns subscription details and Stripe customer ID.
    """

    # Get user
    user = await db.get(User, user_id)

    # Create Stripe customer if doesn't exist
    if not user.stripe_customer_id:
        customer = stripe.Customer.create(
            email=user.email,
            name=user.full_name,
            payment_method=payment_method_id,
            invoice_settings={
                'default_payment_method': payment_method_id
            },
            metadata={
                'user_id': str(user_id)
            }
        )
        user.stripe_customer_id = customer.id
    else:
        # Attach payment method to existing customer
        stripe.PaymentMethod.attach(
            payment_method_id,
            customer=user.stripe_customer_id
        )
        stripe.Customer.modify(
            user.stripe_customer_id,
            invoice_settings={
                'default_payment_method': payment_method_id
            }
        )

    # Create subscription
    subscription = stripe.Subscription.create(
        customer=user.stripe_customer_id,
        items=[
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Researcher Monthly Subscription',
                        'description': 'Access to peer review platform ($80 platform + $20 reviewer pool)'
                    },
                    'unit_amount': 10000,  # $100.00
                    'recurring': {
                        'interval': 'month'
                    }
                }
            }
        ],
        expand=['latest_invoice.payment_intent'],
        metadata={
            'user_id': str(user_id),
            'payout_contribution_cents': 2000
        }
    )

    # Save subscription to database
    db_subscription = Subscription(
        user_id=user_id,
        stripe_subscription_id=subscription.id,
        stripe_customer_id=user.stripe_customer_id,
        stripe_payment_method_id=payment_method_id,
        status=subscription.status,
        monthly_amount_cents=10000,
        payout_contribution_cents=2000,
        current_period_start=datetime.fromtimestamp(subscription.current_period_start),
        current_period_end=datetime.fromtimestamp(subscription.current_period_end)
    )

    db.add(db_subscription)

    # Add contribution to current payout pool
    current_pool = await get_or_create_current_pool(db)
    current_pool.total_contributions_cents += 2000

    contribution = PayoutContribution(
        pool_id=current_pool.id,
        user_id=user_id,
        subscription_id=db_subscription.id,
        contribution_amount_cents=2000,
        billing_date=datetime.utcnow(),
        status='completed'
    )

    db.add(contribution)

    # Update user
    user.is_paying_member = True
    user.member_since = datetime.utcnow()
    user.subscription_status = 'active'

    await db.commit()

    return {
        'subscription_id': subscription.id,
        'status': subscription.status,
        'current_period_end': subscription.current_period_end,
        'client_secret': subscription.latest_invoice.payment_intent.client_secret
    }
```

---

**END OF TECHNICAL DESIGN DOCUMENT**

**Next Steps for Development Team**:
1. Review this document with stakeholders
2. Set up development environment (Stripe test mode)
3. Begin Phase 1: Foundation (database schema)
4. Weekly progress reviews with product manager
5. Iterate based on POC feedback

**Questions? Contact**: Technical Solution Architect
