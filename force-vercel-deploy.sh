#!/bin/bash

echo "🚀 Force Clean Vercel Deployment"
echo "================================"
echo ""

cd /Users/brandon/meta-analysis-tool/frontend

echo "Step 1: Clean local build..."
rm -rf .next
rm -rf node_modules/.cache
echo "✅ Local cache cleared"
echo ""

echo "Step 2: Verify build works locally..."
npm run build
if [ $? -eq 0 ]; then
    echo "✅ Local build SUCCEEDED"
else
    echo "❌ Local build FAILED - fix issues first"
    exit 1
fi
echo ""

echo "Step 3: Deploy to Vercel with --force..."
npx vercel --prod --force
echo ""

echo "✅ Deployment initiated!"
echo ""
echo "Check status at: https://vercel.com/brandons-projects/meta-analysis-tool"
