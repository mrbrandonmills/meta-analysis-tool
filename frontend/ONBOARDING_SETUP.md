# Researcher Onboarding System Setup Guide

## Overview

This document provides comprehensive setup instructions for the enhanced researcher onboarding system, which includes:

- **Multi-step form** with 5 comprehensive steps
- **AI-powered profile enrichment** from Google Scholar, ORCID
- **Stripe payment integration** for subscription management
- **Advanced UI components** with glassmorphism and smooth animations
- **Form validation** with real-time feedback
- **LocalStorage auto-save** for progress persistence

## Prerequisites

### Required Dependencies

The onboarding system uses the following existing dependencies:

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "next": "14.0.0",
    "framer-motion": "^10.16.16",
    "lucide-react": "^0.294.0",
    "react-hot-toast": "^2.4.1",
    "zustand": "^4.4.7"
  }
}
```

### Additional Dependencies Required

Install Stripe payment dependencies:

```bash
cd frontend
npm install @stripe/stripe-js @stripe/react-stripe-js
```

## File Structure

```
frontend/src/
├── components/onboarding/
│   ├── index.ts                        # Component exports
│   ├── OnboardingLayout.tsx            # Main layout wrapper
│   ├── StepIndicator.tsx               # Visual progress indicator
│   ├── ResearchDomainSelector.tsx      # Multi-select domain chips
│   ├── KeywordInput.tsx                # Tag input with autocomplete
│   └── StripePaymentForm.tsx           # Payment integration
├── hooks/
│   └── useOnboarding.ts                # State management hook
├── lib/validation/
│   └── onboarding.ts                   # Form validation utilities
├── pages/onboarding/
│   ├── researcher.tsx                  # Main 5-step onboarding page
│   └── success.tsx                     # Success page with enrichment animation
└── types/
    └── onboarding.ts                   # TypeScript type definitions
```

## Environment Variables

Add the following to your `.env.local` file:

```bash
# Stripe Configuration
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here

# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Backend API Requirements

The onboarding system expects the following API endpoints:

### 1. Create Subscription

```
POST /api/v1/subscriptions/create
Content-Type: application/json

{
  "payment_method_id": "pm_...",
  "billing_email": "researcher@edu"
}

Response:
{
  "subscription_id": "sub_...",
  "status": "active",
  "current_period_end": "2024-01-01T00:00:00Z"
}
```

### 2. Update Researcher Profile

```
PUT /api/v1/researchers/{id}
Content-Type: application/json

{
  "full_name": "Dr. Jane Smith",
  "email": "jane@stanford.edu",
  "institution": "Stanford University",
  "department": "Psychology",
  "position": "assistant_professor",
  "country": "United States",
  "orcid_id": "0000-0001-2345-6789",
  "google_scholar_url": "https://scholar.google.com/citations?user=...",
  "researchgate_url": "https://www.researchgate.net/profile/...",
  "personal_website": "https://jane-smith.com",
  "h_index": 15,
  "total_citations": 450,
  "primary_domains": ["psychology", "neuroscience"],
  "custom_domains": ["cognitive neuroscience"],
  "research_keywords": ["fMRI", "working memory", "attention"],
  "methodologies": ["experimental", "neuroimaging"],
  "review_experience_level": "6-10",
  "journals_reviewed_for": ["Nature Neuroscience", "Journal of Neuroscience"],
  "max_concurrent_reviews": 2,
  "preferred_review_time": 14,
  "availability_status": true,
  "languages": ["english", "spanish"],
  "subscription_id": "sub_..."
}

Response:
{
  "id": "researcher_123",
  "profile_completion": 95,
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 3. Trigger AI Enrichment

```
POST /api/v1/researchers/{id}/enrich
Content-Type: application/json

{
  "google_scholar_url": "https://scholar.google.com/citations?user=...",
  "orcid_id": "0000-0001-2345-6789"
}

Response:
{
  "status": "processing",
  "job_id": "enrich_job_123",
  "estimated_time": 45
}
```

## Integration Steps

### Step 1: Set Up Stripe

1. Create a Stripe account at https://stripe.com
2. Get your publishable key from the Stripe Dashboard
3. Add it to `.env.local` as `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`

### Step 2: Configure Backend Endpoints

Ensure your backend implements the three endpoints listed above:
- Subscription creation
- Researcher profile updates
- AI enrichment trigger

### Step 3: Add Navigation Link

Update your navigation/header to include a "Get Started" link:

```tsx
// In your Header or Landing page
import Link from 'next/link';

<Link href="/onboarding/researcher">
  <button className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-3 rounded-lg">
    Get Started as Reviewer
  </button>
</Link>
```

### Step 4: Test the Flow

1. Navigate to `/onboarding/researcher`
2. Fill out all 5 steps
3. Complete test payment (use Stripe test card: 4242 4242 4242 4242)
4. Verify redirect to success page
5. Check backend for created subscription and profile

## Features by Step

### Step 1: Basic Information
- Full name validation
- Email format validation
- Institution autocomplete (top 20 universities)
- Department text input
- Position dropdown
- Country selection

### Step 2: Academic Profile (Optional)
- ORCID ID with format validation
- Google Scholar URL validation
- ResearchGate URL validation
- Personal website URL
- H-index input
- Total citations input
- All fields optional but recommended

### Step 3: Research Expertise
- Multi-select research domains (max 5)
- Custom domain input
- Keyword tag input (min 5, max 20)
- Keyword autocomplete from common psychology keywords
- Research methodology multi-select
- All required for matching algorithm

### Step 4: Peer Review Experience
- Experience level dropdown
- Journals reviewed for (dynamic list)
- Max concurrent reviews selection
- Preferred review timeframe
- Availability toggle
- Language multi-select (required)

### Step 5: Subscription & Payment
- Pricing breakdown display
- Payout system explanation
- Stripe payment form
- Terms of Service checkbox
- Privacy Policy checkbox
- Payout terms checkbox
- All checkboxes required

## Form Validation

The system includes comprehensive validation:

```typescript
import {
  validateBasicInfo,
  validateAcademicProfile,
  validateResearchExpertise,
  validateReviewExperience,
  validatePaymentInfo,
  validateOnboardingForm,
} from '@/lib/validation/onboarding';

// Validate individual step
const { isValid, errors } = validateBasicInfo(formData.basicInfo);

// Validate entire form
const validation = validateOnboardingForm(formData);
console.log(validation.summary); // ["Step 1: Basic Information has errors"]
```

## Auto-Save Feature

Form progress is automatically saved to `localStorage`:

```typescript
// Saved on every change
localStorage.setItem('researcher_onboarding_data', JSON.stringify({
  formData,
  currentStep
}));

// Restored on page load
const savedData = localStorage.getItem('researcher_onboarding_data');

// Cleared on successful submission
localStorage.removeItem('researcher_onboarding_data');
```

## Success Page

The success page includes:

1. **Enrichment Animation**
   - 4-step progress indicator
   - Animated loading states
   - Confetti celebration on completion

2. **Next Steps Cards**
   - Complete profile (link to settings)
   - Browse papers (link to paper queue)
   - Get matched (link to dashboard)

3. **Auto-redirect** to dashboard after enrichment

## Customization

### Modify Research Domains

Edit `/frontend/src/types/onboarding.ts`:

```typescript
export const RESEARCH_DOMAINS = [
  { value: 'your_domain', label: 'Your Domain' },
  // Add more domains
];
```

### Change Subscription Price

Update in `/frontend/src/pages/onboarding/researcher.tsx`:

```typescript
// Step 5: Payment component
<div className="flex justify-between text-sm">
  <span className="text-gray-600">Monthly Subscription</span>
  <span className="font-semibold text-gray-900">$150.00</span> {/* Change here */}
</div>
```

### Modify Keyword Suggestions

Edit `/frontend/src/types/onboarding.ts`:

```typescript
export const COMMON_RESEARCH_KEYWORDS = [
  'your_keyword',
  // Add more keywords
];
```

## Troubleshooting

### Issue: Stripe payment form not showing

**Solution:** Install Stripe dependencies:
```bash
npm install @stripe/stripe-js @stripe/react-stripe-js
```

Then update `StripePaymentForm.tsx` to use actual Stripe Elements.

### Issue: Form validation not working

**Solution:** Check that all required fields are properly connected to the `useOnboarding` hook:

```typescript
const {
  updateBasicInfo,
  updateAcademicProfile,
  // ... etc
} = useOnboarding();
```

### Issue: Auto-save not persisting

**Solution:** Ensure localStorage is available (not in SSR context):

```typescript
useEffect(() => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('key', 'value');
  }
}, []);
```

### Issue: Success page not showing enrichment

**Solution:** The animation is time-based. Check browser console for any errors during the animation sequence.

## Security Considerations

1. **Never store payment information in localStorage**
   - Only store Stripe payment method IDs
   - Let Stripe handle sensitive card data

2. **Validate on backend**
   - Frontend validation is UX only
   - Always validate on backend before processing

3. **Sanitize user input**
   - Especially for custom domains and keywords
   - Prevent XSS attacks

4. **Use HTTPS**
   - Required for Stripe integration
   - Protects user data in transit

## Testing

### Manual Testing Checklist

- [ ] Navigate through all 5 steps
- [ ] Verify back button works
- [ ] Test form validation on each step
- [ ] Test auto-save by refreshing page
- [ ] Complete payment with test card
- [ ] Verify success page loads
- [ ] Check backend for created data

### Stripe Test Cards

```
Success: 4242 4242 4242 4242
Decline: 4000 0000 0000 0002
Auth Required: 4000 0025 0000 3155
```

## Support

For issues or questions:
- Email: support@metaanalysis.ai
- Documentation: /docs/onboarding
- Slack: #onboarding-help

## Version History

- **v1.0.0** - Initial release with 5-step onboarding
- Multi-step form with validation
- Stripe payment integration
- AI enrichment preparation
- Success page with animations
