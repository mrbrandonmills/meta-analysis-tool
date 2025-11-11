# Onboarding Quick Start Guide

## Install Dependencies

```bash
cd frontend
npm install @stripe/stripe-js @stripe/react-stripe-js
```

## Configure Environment

```bash
# .env.local
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_key
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Add Navigation Link

```tsx
// In your header/landing page
import Link from 'next/link';

<Link href="/onboarding/researcher">
  <button className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-3 rounded-lg">
    Get Started as Reviewer
  </button>
</Link>
```

## Required Backend Endpoints

```
POST   /api/v1/subscriptions/create      # Create Stripe subscription
PUT    /api/v1/researchers/{id}          # Update researcher profile
POST   /api/v1/researchers/{id}/enrich   # Trigger AI enrichment
```

## Test the Flow

1. Navigate to `/onboarding/researcher`
2. Fill out 5 steps:
   - Basic Information
   - Academic Profile (optional)
   - Research Expertise
   - Review Experience
   - Payment & Subscription
3. Use Stripe test card: `4242 4242 4242 4242`
4. Verify redirect to `/onboarding/success`
5. Check dashboard for new researcher profile

## Key Features

✅ **Multi-step form** with visual progress indicator
✅ **Auto-save** to localStorage (survives page refresh)
✅ **Real-time validation** with helpful error messages
✅ **Stripe integration** for subscription payments
✅ **AI enrichment** trigger for Google Scholar/ORCID
✅ **Success animation** with profile enrichment progress
✅ **Mobile responsive** design with glassmorphism

## Files Created

```
frontend/src/
├── components/onboarding/         # 5 onboarding components
├── hooks/useOnboarding.ts         # State management hook
├── lib/validation/onboarding.ts   # Validation utilities
├── pages/onboarding/              # Main page + success page
└── types/onboarding.ts            # TypeScript types
```

## Customization

### Change Subscription Price

Edit `pages/onboarding/researcher.tsx` - Step 5 component

### Modify Research Domains

Edit `types/onboarding.ts` - `RESEARCH_DOMAINS` constant

### Add Keywords

Edit `types/onboarding.ts` - `COMMON_RESEARCH_KEYWORDS` constant

## Troubleshooting

**Stripe not loading?**
```bash
npm install @stripe/stripe-js @stripe/react-stripe-js
```

**Validation errors?**
Check `lib/validation/onboarding.ts` for validation rules

**Auto-save not working?**
Check browser console for localStorage errors

**Backend errors?**
Verify API endpoints match expected format (see `ONBOARDING_SETUP.md`)

## Next Steps

1. Set up Stripe account and get publishable key
2. Implement backend endpoints
3. Configure AI enrichment service
4. Test with real user flow
5. Deploy to production

## Support

Questions? Check `ONBOARDING_SETUP.md` for detailed documentation.
