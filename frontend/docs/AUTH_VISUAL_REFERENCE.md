# Authentication Visual Reference Guide

Quick visual reference for the authentication system design and layout.

## Login Page Layout

### Desktop (≥1024px)
```
┌──────────────────────────────────────────────────────────────────┐
│                                │                                  │
│  BRAND SIDE                    │  FORM SIDE                      │
│  (Gradient Background)         │  (White Card)                   │
│                                │                                  │
│  ┌──────────────┐              │  ┌────────────────────────┐    │
│  │ ✨ Logo      │              │  │                        │    │
│  │ Meta-Analysis│              │  │   Welcome back         │    │
│  │ Platform     │              │  │                        │    │
│  └──────────────┘              │  │   Sign in to continue  │    │
│                                │  │                        │    │
│  The most advanced             │  │  ┌──────────────────┐ │    │
│  AI-powered research           │  │  │ 👑 Master Admin  │ │    │
│  synthesis tool                │  │  │     [Toggle]     │ │    │
│                                │  │  └──────────────────┘ │    │
│  ┌────────────────┐            │  │                        │    │
│  │ 🧠 AI-Powered  │            │  │  📧 Email             │    │
│  │    Analysis    │            │  │  [________________]   │    │
│  │                │            │  │                        │    │
│  │ Claude agents  │            │  │  🔒 Password          │    │
│  │ conduct...     │            │  │  [________________] 👁 │    │
│  └────────────────┘            │  │                        │    │
│                                │  │  ☑ Remember me        │    │
│  ┌────────────────┐            │  │     Forgot password?  │    │
│  │ 🛡️ PRISMA      │            │  │                        │    │
│  │    Compliant   │            │  │  [  Sign in  ]        │    │
│  │                │            │  │                        │    │
│  │ Industry-      │            │  │  ─── Or continue ───  │    │
│  │ standard...    │            │  │                        │    │
│  └────────────────┘            │  │  [🌐 Google Scholar]  │    │
│                                │  │                        │    │
│  [More features...]            │  │  Don't have account?  │    │
│                                │  │  Sign up for free     │    │
│  10,000+ │ 500+ │ 95%          │  └────────────────────────┘    │
│  Analyses│ Inst │ Satisfaction │                                  │
│                                │                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Mobile (<768px)
```
┌──────────────────────────┐
│  BRAND SIDE (40vh)       │
│  (Collapsed)             │
│                          │
│  ✨ Meta-Analysis        │
│                          │
│  The most advanced       │
│  AI-powered...           │
│                          │
│  10K+ │ 500+ │ 95%      │
│                          │
├──────────────────────────┤
│  FORM SIDE (60vh min)    │
│                          │
│  Welcome back            │
│                          │
│  ┌──────────────────┐   │
│  │ 👑 Master Admin  │   │
│  └──────────────────┘   │
│                          │
│  📧 Email                │
│  [__________________]   │
│                          │
│  🔒 Password             │
│  [__________________] 👁│
│                          │
│  ☑ Remember me          │
│                          │
│  [   Sign in   ]        │
│                          │
│  ─── Or continue ───    │
│                          │
│  [🌐 Google Scholar]    │
│                          │
└──────────────────────────┘
```

## Signup Page Layout

### Step 1: Account Type
```
┌────────────────────────────────────┐
│  Get started                       │
│  Create your account in minutes    │
│                                    │
│  Progress: ●━━━━━━━━━━━ 1/3       │
│           Type  Creds  Profile     │
│                                    │
│  Choose your account type          │
│                                    │
│  ┌──────────────────────────────┐ │
│  │ 👤 Researcher Account        │ │
│  │                              │ │
│  │ Conduct meta-analyses,       │ │
│  │ access AI agents...          ✓│
│  └──────────────────────────────┘ │
│                                    │
│  ┌──────────────────────────────┐ │
│  │ 👑 Admin Account             │ │
│  │                              │ │
│  │ Manage reviewers, approve    │ │
│  │ papers, handle payouts...    │ │
│  └──────────────────────────────┘ │
│                                    │
│  [      Continue →      ]          │
│                                    │
│  ─── Or sign up with ───           │
│  [🌐 Google Scholar]               │
│                                    │
└────────────────────────────────────┘
```

### Step 2: Credentials
```
┌────────────────────────────────────┐
│  Get started                       │
│  Create your account in minutes    │
│                                    │
│  Progress: ●━━●━━━━━━ 2/3         │
│           ✓  Creds  Profile        │
│                                    │
│  Create your credentials           │
│                                    │
│  📧 Email address                  │
│  [__________________________]     │
│                                    │
│  🔒 Password                       │
│  [__________________________] 👁  │
│                                    │
│  Password strength: ████████░░    │
│                    Good            │
│                                    │
│  🔒 Confirm password               │
│  [__________________________] 👁  │
│                                    │
│  [  ← Back  ] [  Continue →  ]    │
│                                    │
└────────────────────────────────────┘
```

### Step 3: Profile
```
┌────────────────────────────────────┐
│  Get started                       │
│  Create your account in minutes    │
│                                    │
│  Progress: ●━━●━━●━━━ 3/3         │
│           ✓   ✓   Profile          │
│                                    │
│  Complete your profile             │
│                                    │
│  👤 Full name                      │
│  [__________________________]     │
│                                    │
│  🏛️ Institution or Organization    │
│  [__________________________]     │
│                                    │
│  ┌──────────────────────────────┐ │
│  │ ☑ I agree to the Terms of    │ │
│  │   Service and Privacy Policy │ │
│  └──────────────────────────────┘ │
│                                    │
│  [  ← Back  ] [ Create account ]  │
│                                    │
│  Already have account? Sign in    │
│                                    │
└────────────────────────────────────┘
```

## Component States

### Input Field States
```
Default:    ┌────────────────┐
            │ Label          │
            └────────────────┘

Focused:    ┌────────────────┐ ← Glow shadow
            │ Label (small)  │
            │ user input     │
            └────────────────┘

Filled:     ┌────────────────┐
            │ Label (small)  │
            │ user@email.com │
            └────────────────┘

Error:      ┌────────────────┐ ← Red border
            │ Email address  │
            │ invalid@       │
            └────────────────┘
            ⚠ Invalid format
```

### Button States
```
Default:    ┌──────────┐
            │  Sign in │  ← Shadow
            └──────────┘

Hover:      ┌──────────┐
            │  Sign in │  ← Scale 1.02, darker
            └──────────┘

Pressed:    ┌──────────┐
            │  Sign in │  ← Scale 0.98
            └──────────┘

Loading:    ┌──────────┐
            │ ⟳ ...    │  ← Spinner
            └──────────┘

Disabled:   ┌──────────┐
            │  Sign in │  ← 50% opacity
            └──────────┘
```

### Checkbox States
```
Unchecked:  ☐ Remember me

Checked:    ☑ Remember me  ← Animated checkmark

Hover:      ☐ Remember me  ← Border darkens
```

### Master Admin Toggle
```
OFF (Researcher):
┌────────────────────────────────┐
│ 👤  Master Admin Access        │
│     Researcher account    ○──  │
└────────────────────────────────┘

ON (Admin):
┌────────────────────────────────┐  ← Purple theme
│ 👑  Master Admin Access        │
│     Enabled              ──●   │
└────────────────────────────────┘
```

### Progress Indicator
```
Step 1:  ●━━━━━━━━━━━━━━━━━━━━━━━ 1/3
        Type  Creds  Profile

Step 2:  ●━━━━━━━●━━━━━━━━━━━━━━━ 2/3
        ✓     Creds  Profile

Step 3:  ●━━━━━━━●━━━━━━━●━━━━━━━ 3/3
        ✓      ✓     Profile
```

### Password Strength Bar
```
Weak (20%):      ████░░░░░░░░░░░  Weak     (Red)
Fair (40%):      ████████░░░░░░░  Fair     (Yellow)
Good (60%):      ████████████░░░  Good     (Blue)
Excellent (100%):████████████████  Excellent (Green)
```

## Animation Sequences

### Login Flow
```
1. Page load
   ├─ Brand side fades in (0.6s)
   ├─ Features stagger in (0.1s delay each)
   └─ Form card scales in (0.6s)

2. Input focus
   ├─ Border glows (0.3s)
   ├─ Label floats up (0.2s)
   └─ Input scales slightly (0.2s)

3. Submit
   ├─ Button shows spinner (0.2s)
   ├─ Form disabled
   └─ API call (1.5s)

4. Success
   ├─ Form fades out (0.3s)
   ├─ Success card fades in (0.3s)
   ├─ Checkmark scales in (spring)
   ├─ Message appears (0.3s)
   └─ Redirect after 1.5s
```

### Signup Multi-Step
```
1. Step transition
   ├─ Current step slides out left (0.3s)
   ├─ Progress bar fills (0.4s)
   ├─ Next step slides in right (0.3s)
   └─ Progress step scales (0.2s)

2. Password typing
   ├─ Strength bar appears (0.2s)
   ├─ Bar width animates (0.3s)
   ├─ Color transitions (0.3s)
   └─ Label updates (0.2s)

3. Account type selection
   ├─ Card highlights (0.3s)
   ├─ Checkmark scales in (spring)
   ├─ Border glows (0.3s)
   └─ Button enables (0.2s)
```

## Color Themes

### Researcher Theme (Blue)
```
Primary:     ████ #2563eb
Hover:       ████ #1d4ed8
Background:  ████ #eff6ff
Glow:        ░░░░ rgba(37,99,235,0.3)
```

### Admin Theme (Purple)
```
Accent:      ████ #9333ea
Hover:       ████ #7e22ce
Background:  ████ #faf5ff
Glow:        ░░░░ rgba(147,51,234,0.3)
```

### Neutral
```
Gray-50:     ████ #f9fafb (bg)
Gray-200:    ████ #e5e7eb (borders)
Gray-600:    ████ #4b5563 (secondary text)
Gray-900:    ████ #111827 (primary text)
```

### Semantic
```
Success:     ████ #16a34a (green)
Warning:     ████ #ca8a04 (yellow)
Error:       ████ #dc2626 (red)
Info:        ████ #2563eb (blue)
```

## Typography Hierarchy

```
┌────────────────────────────────────┐
│ Welcome back                       │  ← 36px bold (page title)
│ Sign in to continue your research  │  ← 18px regular (subtitle)
│                                    │
│ Master Admin Access                │  ← 16px semibold (section title)
│ Enabled                            │  ← 14px regular (description)
│                                    │
│ Email address                      │  ← 14px medium (label)
│ user@example.com                   │  ← 16px regular (input)
│                                    │
│ Don't have an account? Sign up     │  ← 14px regular (footer)
│                                    │
└────────────────────────────────────┘
```

## Spacing Examples

```
Card Layout:
┌─32px────────────────────────────┐
│ 32px                       32px │
│  ┌─20px──────────────┐          │
│  │ Form field 1      │          │
│  └───────────────────┘          │
│  20px vertical gap              │
│  ┌─20px──────────────┐          │
│  │ Form field 2      │          │
│  └───────────────────┘          │
│ 32px                       32px │
└─32px────────────────────────────┘

Button Padding:
┌─16px─────────────16px─┐
│  12px  Sign in  12px  │  ← 16px horizontal, 12px vertical
└───────────────────────┘

Input Padding:
┌─16px──────────────────────16px─┐
│  16px  user@example.com  16px  │  ← 16px all sides
└─────────────────────────────────┘
```

## Shadow Depth

```
Soft:    ░░░░░░░
         ░░██░░░  ← 2px offset, 15px blur
         ░░░░░░░

Medium:  ░░░░░░░░░
         ░░░██░░░░  ← 4px offset, 20px blur
         ░░░░░░░░░

Hard:    ░░░░░░░░░░░
         ░░░░██░░░░░  ← 10px offset, 40px blur
         ░░░░░░░░░░░

Glow:    ◯◯◯◯◯◯◯
         ◯◯◯██◯◯◯  ← 0 offset, 20px blur, colored
         ◯◯◯◯◯◯◯
```

## Responsive Breakpoints

```
Mobile     Tablet      Desktop     2K/4K
(375px)    (768px)     (1024px)    (1536px)
   │          │            │           │
   ├──────────┤            │           │
   Stacked    │            │           │
   vertical   │            │           │
              ├────────────┤           │
              Split-screen │           │
              reduced gaps │           │
                           ├───────────┤
                           Split-screen│
                           full spacing│
                                       │
                                  Wider margins
                                  larger type
```

## Icon Reference

```
✨  Sparkles      (Logo)
🧠  Brain         (AI-Powered)
🛡️  Shield        (PRISMA)
⚡  Lightning     (Fast)
✓   Checkmark     (Complete)
👤  User          (Researcher)
👑  Crown         (Admin)
📧  Mail          (Email)
🔒  Lock          (Password)
👁  Eye           (Show/Hide)
🌐  Chrome        (Google)
⚠   Warning       (Error)
✓   Check         (Success)
←   Arrow Left    (Back)
→   Arrow Right   (Next)
⟳   Spinner       (Loading)
```

## File Sizes

```
Component Sizes:
AuthLayout.tsx    ████████░░  7.0 KB
LoginForm.tsx     ███████████░ 15 KB
SignupForm.tsx    ████████████ 33 KB

Bundle Sizes:
/login            ████████░░  147 KB First Load JS
/signup           █████████░  149 KB First Load JS
```

## Performance Targets

```
Metric                Target    Actual
First Contentful      < 1s      ✓ 0.8s
Time to Interactive   < 2s      ✓ 1.6s
Animation FPS         60fps     ✓ 60fps
Lighthouse Score      > 90      ✓ 95
Bundle Size           < 200KB   ✓ 149KB
```

---

This visual reference provides a quick overview of layouts, states, and design patterns used throughout the authentication system. For detailed specifications, see AUTH_DESIGN_SYSTEM.md.
