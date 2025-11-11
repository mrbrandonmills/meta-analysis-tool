#!/bin/bash

# Researcher Onboarding System - Setup Script
# This script installs dependencies and configures the onboarding system

set -e

echo "════════════════════════════════════════════════════════════════"
echo "  Researcher Onboarding System - Setup Script"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check if we're in the frontend directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this script from the frontend directory."
    exit 1
fi

echo "✅ Found package.json"
echo ""

# Step 1: Install Stripe dependencies
echo "📦 Step 1: Installing Stripe dependencies..."
echo "   - @stripe/stripe-js"
echo "   - @stripe/react-stripe-js"
echo ""

npm install @stripe/stripe-js @stripe/react-stripe-js

if [ $? -eq 0 ]; then
    echo "✅ Stripe dependencies installed successfully"
else
    echo "❌ Failed to install Stripe dependencies"
    exit 1
fi
echo ""

# Step 2: Check for .env.local file
echo "🔧 Step 2: Checking environment configuration..."

if [ -f ".env.local" ]; then
    echo "✅ Found .env.local"

    # Check if Stripe key exists
    if grep -q "NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY" .env.local; then
        echo "✅ Stripe publishable key configured"
    else
        echo "⚠️  Warning: NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY not found in .env.local"
        echo ""
        echo "   Add the following to your .env.local file:"
        echo "   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here"
        echo ""
    fi

    # Check if API URL exists
    if grep -q "NEXT_PUBLIC_API_URL" .env.local; then
        echo "✅ API URL configured"
    else
        echo "⚠️  Warning: NEXT_PUBLIC_API_URL not found in .env.local"
        echo ""
        echo "   Add the following to your .env.local file:"
        echo "   NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1"
        echo ""
    fi
else
    echo "⚠️  Warning: .env.local not found"
    echo ""
    echo "   Creating .env.local with template..."

    cat > .env.local << 'EOF'
# Stripe Configuration
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here

# Backend API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
EOF

    echo "✅ Created .env.local"
    echo ""
    echo "   ⚠️  IMPORTANT: Update the Stripe publishable key in .env.local"
    echo ""
fi
echo ""

# Step 3: Verify file structure
echo "📁 Step 3: Verifying file structure..."

REQUIRED_FILES=(
    "src/components/onboarding/index.ts"
    "src/components/onboarding/StepIndicator.tsx"
    "src/components/onboarding/ResearchDomainSelector.tsx"
    "src/components/onboarding/KeywordInput.tsx"
    "src/components/onboarding/StripePaymentForm.tsx"
    "src/components/onboarding/OnboardingLayout.tsx"
    "src/hooks/useOnboarding.ts"
    "src/pages/onboarding/researcher.tsx"
    "src/pages/onboarding/success.tsx"
    "src/types/onboarding.ts"
    "src/lib/validation/onboarding.ts"
)

ALL_FILES_EXIST=true

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ Missing: $file"
        ALL_FILES_EXIST=false
    fi
done
echo ""

if [ "$ALL_FILES_EXIST" = true ]; then
    echo "✅ All required files are present"
else
    echo "❌ Some files are missing. Please ensure all onboarding files are created."
    exit 1
fi
echo ""

# Step 4: Display next steps
echo "════════════════════════════════════════════════════════════════"
echo "  ✅ Setup Complete!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📋 Next Steps:"
echo ""
echo "   1. Update .env.local with your Stripe publishable key"
echo "      Get it from: https://dashboard.stripe.com/test/apikeys"
echo ""
echo "   2. Ensure backend API is running at http://localhost:8000"
echo "      Required endpoints:"
echo "      - POST /api/v1/subscriptions/create"
echo "      - PUT  /api/v1/researchers/{id}"
echo "      - POST /api/v1/researchers/{id}/enrich"
echo ""
echo "   3. Start the development server:"
echo "      npm run dev"
echo ""
echo "   4. Test the onboarding flow:"
echo "      http://localhost:3000/onboarding/researcher"
echo ""
echo "   5. Use Stripe test card for payment:"
echo "      Card: 4242 4242 4242 4242"
echo "      Exp:  Any future date"
echo "      CVC:  Any 3 digits"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  📚 Documentation"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "   ONBOARDING_SETUP.md              - Complete setup guide"
echo "   ONBOARDING_QUICK_START.md        - Quick reference"
echo "   ONBOARDING_IMPLEMENTATION_SUMMARY.md - Technical details"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""

exit 0
