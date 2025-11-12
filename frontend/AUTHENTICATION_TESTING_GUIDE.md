# Authentication System Testing Guide

## Quick Start

```bash
# Install dependencies (if not already done)
npm install

# Start development server
npm run dev

# Open browser to test pages
# Login: http://localhost:3000/login
# Signup: http://localhost:3000/signup
```

## Test Pages

### Login Page (`/login`)
**URL:** `http://localhost:3000/login`

**Test Scenarios:**

1. **Visual Layout**
   - [ ] Split-screen layout displays correctly (50/50 on desktop)
   - [ ] Brand side shows gradient background with animated orbs
   - [ ] Form side shows white card with login form
   - [ ] Logo and tagline visible on brand side
   - [ ] Features list displays with icons

2. **Master Admin Toggle**
   - [ ] Toggle defaults to OFF (researcher mode)
   - [ ] Click toggles between Researcher/Admin modes
   - [ ] Colors change from blue (researcher) to purple (admin)
   - [ ] Toggle animation is smooth (300ms)
   - [ ] Crown icon displays for admin mode

3. **Email Input**
   - [ ] Click focuses input with blue glow
   - [ ] Label floats to top when focused/filled
   - [ ] Typing updates value correctly
   - [ ] Icon stays left-aligned
   - [ ] Validation runs on blur

4. **Password Input**
   - [ ] Click focuses with blue glow
   - [ ] Show/hide icon toggles visibility
   - [ ] Label floats to top
   - [ ] Password masked by default
   - [ ] Toggle reveals plain text

5. **Remember Me Checkbox**
   - [ ] Click checks/unchecks
   - [ ] Checkmark animates in (spring)
   - [ ] Background fills with primary color
   - [ ] Hover state works

6. **Submit Button**
   - [ ] Hover scales to 1.02
   - [ ] Press scales to 0.98
   - [ ] Click shows loading spinner
   - [ ] Text changes to "Signing in..."
   - [ ] Button disabled during loading

7. **Error States**
   - [ ] Test with email: `error@test.com`
   - [ ] Error banner slides down from top
   - [ ] Red alert icon displayed
   - [ ] Error message readable
   - [ ] Banner dismisses on retry

8. **Success Flow**
   - [ ] Test with any valid email (except error@test.com)
   - [ ] Success screen fades in
   - [ ] Green checkmark scales in (spring)
   - [ ] "Welcome back!" message displays
   - [ ] Auto-redirect after 1.5 seconds
   - [ ] Redirects to `/dashboard`

9. **Google OAuth Button**
   - [ ] Hover changes background
   - [ ] Click triggers OAuth flow
   - [ ] Chrome icon visible

10. **Sign Up Link**
    - [ ] Link navigates to `/signup`
    - [ ] Hover underlines text

### Signup Page (`/signup`)
**URL:** `http://localhost:3000/signup`

**Test Scenarios:**

1. **Progress Indicator**
   - [ ] Shows 1/3 on Step 1 (Account Type)
   - [ ] Shows 2/3 on Step 2 (Credentials)
   - [ ] Shows 3/3 on Step 3 (Profile)
   - [ ] Progress bar fills between steps
   - [ ] Active step scales to 1.1
   - [ ] Completed steps show checkmark

2. **Step 1: Account Type**
   - [ ] Two cards displayed (Researcher, Admin)
   - [ ] Click selects card
   - [ ] Selected card highlights (blue or purple)
   - [ ] Checkmark appears on selection
   - [ ] "Continue" button enabled
   - [ ] Click Continue advances to Step 2

3. **Step 2: Credentials**
   - [ ] Email input focuses with glow
   - [ ] Password input shows strength indicator
   - [ ] Strength bar animates (red → yellow → blue → green)
   - [ ] Strength label updates (Weak → Fair → Good → Excellent)
   - [ ] Confirm password validates match
   - [ ] Error message shows if passwords don't match
   - [ ] "Back" button returns to Step 1
   - [ ] "Continue" validates and advances to Step 3

4. **Password Strength Indicator**
   - Test different passwords:
     - [ ] "test" → Weak (red, 20%)
     - [ ] "testing123" → Fair (yellow, 40%)
     - [ ] "Testing123" → Good (blue, 60%)
     - [ ] "Testing123!" → Excellent (green, 100%)

5. **Step 3: Profile**
   - [ ] Full name input works
   - [ ] Institution input works
   - [ ] Terms checkbox required
   - [ ] Checkbox animates on check
   - [ ] "Back" returns to Step 2
   - [ ] "Create account" submits form

6. **Validation Errors**
   - [ ] Empty email shows error
   - [ ] Invalid email format shows error
   - [ ] Short password (< 8 chars) shows error
   - [ ] Mismatched passwords show error
   - [ ] Empty full name shows error
   - [ ] Empty institution shows error
   - [ ] Unchecked terms prevents submission

7. **Success Flow**
   - [ ] Fill all fields correctly
   - [ ] Click "Create account"
   - [ ] Loading spinner appears
   - [ ] Success screen fades in
   - [ ] Green checkmark scales in
   - [ ] "Welcome!" message displays
   - [ ] Auto-redirect after 1.5 seconds
   - [ ] Redirects to `/onboarding`

8. **Multi-Step Navigation**
   - [ ] Steps slide out left on next
   - [ ] Steps slide in from right on next
   - [ ] Steps slide out right on back
   - [ ] Steps slide in from left on back
   - [ ] Animations smooth (300ms)

9. **Color Themes**
   - [ ] Researcher: Blue theme (#2563eb)
   - [ ] Admin: Purple theme (#9333ea)
   - [ ] Theme persists across steps
   - [ ] Buttons, borders, glows match theme

## Mobile Testing

### iPhone (375px width)
- [ ] Visit on iPhone or use Chrome DevTools
- [ ] Split-screen becomes stacked vertical
- [ ] Brand side: 40vh height
- [ ] Form side: Full width, 60vh minimum
- [ ] All touch targets ≥ 44px
- [ ] Inputs don't trigger zoom (16px font)
- [ ] Buttons full width
- [ ] Cards stack vertically
- [ ] Progress indicator responsive
- [ ] Animations still smooth

### iPad (768px width)
- [ ] Split-screen maintains
- [ ] Spacing adjusts
- [ ] Typography scales appropriately
- [ ] Touch targets remain adequate

## Accessibility Testing

### Keyboard Navigation
- [ ] Tab through all fields in order
- [ ] Shift+Tab reverses order
- [ ] Enter submits form
- [ ] Space toggles checkboxes
- [ ] Escape closes modals (if any)
- [ ] Focus visible on all elements

### Screen Reader Testing
- [ ] All inputs have labels
- [ ] Error messages announced
- [ ] Loading states announced
- [ ] Success messages announced
- [ ] Button purposes clear
- [ ] Form structure semantic

### Color Contrast
- [ ] All text meets WCAG AA (4.5:1)
- [ ] Large text meets WCAG AA (3:1)
- [ ] Focus indicators visible
- [ ] Error states use icon + color

### Motion Preferences
- [ ] Test with `prefers-reduced-motion`
- [ ] Animations reduce or disable
- [ ] Essential motion only

## Performance Testing

### Animation Smoothness
- [ ] Open Chrome DevTools Performance
- [ ] Record during interactions
- [ ] Check for 60fps (16ms per frame)
- [ ] No jank or dropped frames
- [ ] GPU-accelerated properties only

### Load Time
- [ ] First Contentful Paint < 1s
- [ ] Time to Interactive < 2s
- [ ] Lighthouse Performance > 90

### Bundle Size
- [ ] Login page: ~147 KB First Load JS
- [ ] Signup page: ~149 KB First Load JS
- [ ] Check Network tab for large assets

## Browser Compatibility

Test in:
- [ ] Chrome 90+ (Desktop & Mobile)
- [ ] Firefox 88+
- [ ] Safari 14+ (Mac & iOS)
- [ ] Edge 90+

## API Integration Testing

### Mock Success
```javascript
// In LoginForm or SignupForm onSubmit
await new Promise(resolve => setTimeout(resolve, 1500));
// Success - redirects
```

### Mock Error
```javascript
// Use email: error@test.com
// OR use email: exists@test.com for signup
// Error banner should appear
```

### Real API (when available)
Replace mock functions with:
```typescript
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password, isMasterAdmin })
});
```

## Design System Verification

### Colors
- [ ] Primary blue: #2563eb (researcher)
- [ ] Accent purple: #9333ea (admin)
- [ ] Gray-50 background: #f9fafb
- [ ] Gray-900 text: #111827

### Typography
- [ ] Page title: 36px bold
- [ ] Section title: 24px semibold
- [ ] Body: 16px regular
- [ ] Caption: 14px regular

### Spacing
- [ ] Form fields: 20px gap
- [ ] Card padding: 32px
- [ ] Button padding: 16px horizontal
- [ ] Input padding: 16px all sides

### Shadows
- [ ] Soft: 0 2px 15px rgba(0,0,0,0.08)
- [ ] Hard: 0 10px 40px rgba(0,0,0,0.2)
- [ ] Glow (primary): 0 0 20px rgba(37,99,235,0.3)

## Known Demo Behaviors

1. **Login page** redirects to `/dashboard` on success
2. **Signup page** redirects to `/onboarding` on success
3. Email `error@test.com` triggers error on login
4. Email `exists@test.com` triggers error on signup
5. All other emails succeed (demo mode)
6. No actual authentication - for visual testing only

## Screenshots to Capture

1. Login page - default state
2. Login page - Master Admin toggle ON
3. Login page - focused email input
4. Login page - error state
5. Login page - success screen
6. Signup page - Step 1 (Account Type)
7. Signup page - Step 2 (Credentials)
8. Signup page - Step 3 (Profile)
9. Signup page - password strength indicator
10. Signup page - success screen
11. Mobile: Login stacked layout
12. Mobile: Signup multi-step
13. Accessibility: Keyboard focus visible
14. Animation: Progress indicator transition

## Deployment Checklist

Before deploying to production:
- [ ] All tests pass
- [ ] Build succeeds (`npm run build`)
- [ ] No console errors
- [ ] No TypeScript errors
- [ ] Environment variables set
- [ ] API endpoints configured
- [ ] OAuth credentials added
- [ ] HTTPS enabled
- [ ] Analytics tracking added
- [ ] Error monitoring setup
- [ ] Performance benchmarks met

## Troubleshooting

### Build Fails
```bash
# Clear cache and rebuild
rm -rf .next
npm run build
```

### Animations Choppy
- Check for large images
- Disable CPU throttling in DevTools
- Reduce motion complexity
- Use will-change CSS hints

### TypeScript Errors
```bash
# Regenerate types
npm run build
```

### Styles Not Applied
- Check Tailwind config
- Verify globals.css imported
- Clear browser cache
- Restart dev server

## Support

For issues or questions:
- Check `/docs/AUTH_DESIGN_SYSTEM.md`
- Check `/src/components/auth/README.md`
- Review component source code
- Contact Agent 3 - Visual Designer

---

Built with pixel-perfect precision by Agent 3.
Last updated: November 12, 2025
