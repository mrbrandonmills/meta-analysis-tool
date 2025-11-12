# Authentication Components

Museum-quality authentication system for the Meta-Analysis Research Platform.

## Components

### AuthLayout
Split-screen authentication layout with animated brand side and form side.

**Features:**
- Animated gradient background with floating orbs
- Feature showcase with icons and descriptions
- Social proof statistics (10,000+ analyses, 500+ institutions)
- Responsive design (stacks vertically on mobile)
- Configurable side placement (left/right)

**Usage:**
```tsx
<AuthLayout
  title="Welcome back"
  subtitle="Sign in to continue your research"
  side="right"
>
  <LoginForm />
</AuthLayout>
```

### LoginForm
Elegant login form with floating labels and smooth animations.

**Features:**
- Master Admin toggle with crown icon
- Floating label animations on focus
- Password visibility toggle
- Remember me checkbox with custom styling
- Error state animations
- Success screen with confetti-style celebration
- Google Scholar OAuth button
- Color themes based on account type (primary for researcher, accent for admin)

**Props:**
```tsx
interface LoginFormProps {
  onSubmit?: (data: LoginFormData) => Promise<void>;
  onGoogleLogin?: () => void;
}

interface LoginFormData {
  email: string;
  password: string;
  rememberMe: boolean;
  isMasterAdmin: boolean;
}
```

**Usage:**
```tsx
<LoginForm
  onSubmit={async (data) => {
    await loginUser(data);
  }}
  onGoogleLogin={() => {
    window.location.href = '/api/auth/google';
  }}
/>
```

### SignupForm
Multi-step signup flow with visual progress indicator.

**Features:**
- 3-step wizard (Account Type → Credentials → Profile)
- Visual progress indicator with checkmarks
- Account type selection (Researcher vs Admin)
- Real-time password strength indicator
- Inline validation with helpful error messages
- Password confirmation matching
- Terms & conditions checkbox
- Success animation on completion
- Color themes based on account type

**Props:**
```tsx
interface SignupFormProps {
  onSubmit?: (data: SignupFormData) => Promise<void>;
  onGoogleSignup?: () => void;
}

interface SignupFormData {
  accountType: 'researcher' | 'admin';
  email: string;
  password: string;
  confirmPassword: string;
  fullName: string;
  institution: string;
  agreeToTerms: boolean;
}
```

**Usage:**
```tsx
<SignupForm
  onSubmit={async (data) => {
    await createUser(data);
  }}
  onGoogleSignup={() => {
    window.location.href = '/api/auth/google?signup=true';
  }}
/>
```

## Pages

### /login
Login page with split-screen layout (form on left, brand on right).

### /signup
Signup page with split-screen layout (form on right, brand on left).

## Design Specifications

### Colors
- **Researcher theme:** Primary blue (#2563eb)
- **Admin theme:** Accent purple (#9333ea)
- **Background:** Gray-50 (#f9fafb)
- **Text:** Gray-900 (#111827)

### Typography
- **Headings:** System sans-serif, bold
- **Body:** System sans-serif, regular
- **Size scale:** xs (12px), sm (14px), base (16px), lg (18px), xl (20px), 2xl (24px), 4xl (36px)

### Spacing
- **Form fields:** 20px (5 Tailwind units) vertical spacing
- **Sections:** 32px (8 Tailwind units) vertical spacing
- **Cards:** 32px (8 Tailwind units) padding
- **Buttons:** 16px (4 Tailwind units) horizontal, 12px (3 Tailwind units) vertical

### Animation Timing
- **Fast (200ms):** Hover effects, focus states
- **Normal (300ms):** Step transitions, form field animations
- **Slow (400ms):** Layout shifts, success animations
- **Easing:** cubic-bezier(0.22, 1, 0.36, 1) for luxury feel

### Shadows
- **Soft:** 0 2px 15px rgba(0,0,0,0.08)
- **Medium:** 0 4px 20px rgba(0,0,0,0.12)
- **Hard:** 0 10px 40px rgba(0,0,0,0.2)
- **Glow (primary):** 0 0 20px rgba(37,99,235,0.3)
- **Glow (accent):** 0 0 20px rgba(147,51,234,0.3)

### Responsive Breakpoints
- **Mobile:** < 768px (sm)
- **Tablet:** 768px - 1024px (md/lg)
- **Desktop:** > 1024px (xl)

### Accessibility
- WCAG AA compliant contrast ratios
- Keyboard navigation support
- Screen reader labels (aria-label, aria-hidden)
- Focus visible states with ring-2
- Touch targets minimum 44px x 44px
- Loading states announced to screen readers

## Implementation Notes

### State Management
- Local component state using React useState
- Form validation on blur and submit
- Error messages cleared on input change
- Loading states prevent multiple submissions

### Error Handling
- API errors displayed in dismissible alerts
- Validation errors shown inline below fields
- Network errors fallback to generic message
- Success states automatically redirect after 1.5s

### Performance
- Framer Motion animations optimized for 60fps
- Images and icons lazy loaded
- Form components code split
- CSS transitions use GPU-accelerated properties (transform, opacity)

### Browser Support
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Chrome Mobile)
- Progressive enhancement for older browsers
- Graceful degradation of animations

## Testing Checklist

- [ ] Login form validates email format
- [ ] Login form validates password length
- [ ] Master Admin toggle changes theme colors
- [ ] Password visibility toggle works
- [ ] Remember me checkbox persists
- [ ] Error messages display and dismiss correctly
- [ ] Success animation plays before redirect
- [ ] Google OAuth button triggers flow
- [ ] Signup multi-step navigation works
- [ ] Password strength indicator updates
- [ ] Password confirmation validates match
- [ ] Terms checkbox prevents submission if unchecked
- [ ] All forms are keyboard navigable
- [ ] All forms work on mobile (tested on iPhone/Android)
- [ ] Animations are smooth at 60fps
- [ ] Loading states prevent double submission
- [ ] Forms work with screen readers
- [ ] Focus states are clearly visible

## Future Enhancements

- [ ] Add biometric authentication (Face ID, Touch ID)
- [ ] Implement magic link email login
- [ ] Add 2FA with QR code
- [ ] Support for SSO (SAML, OIDC)
- [ ] Password strength requirements customizable by admin
- [ ] Account recovery flow
- [ ] Email verification step
- [ ] Captcha for bot prevention
- [ ] Session management (remember devices)
- [ ] Login history and activity log
