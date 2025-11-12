/**
 * Design Tokens for Authentication System
 *
 * Museum-quality design system tokens for luxury authentication experience.
 * These tokens ensure consistency across all auth components.
 */

export const authTokens = {
  /**
   * Color Palette
   */
  colors: {
    // Primary theme (Researcher accounts)
    primary: {
      50: '#eff6ff',
      100: '#dbeafe',
      200: '#bfdbfe',
      300: '#93c5fd',
      400: '#60a5fa',
      500: '#3b82f6',
      600: '#2563eb', // Main
      700: '#1d4ed8',
      800: '#1e40af',
      900: '#1e3a8a',
    },

    // Accent theme (Admin accounts)
    accent: {
      50: '#faf5ff',
      100: '#f3e8ff',
      200: '#e9d5ff',
      300: '#d8b4fe',
      400: '#c084fc',
      500: '#a855f7',
      600: '#9333ea', // Main
      700: '#7e22ce',
      800: '#6b21a8',
      900: '#581c87',
    },

    // Neutral grays
    gray: {
      50: '#f9fafb',
      100: '#f3f4f6',
      200: '#e5e7eb',
      300: '#d1d5db',
      400: '#9ca3af',
      500: '#6b7280',
      600: '#4b5563',
      700: '#374151',
      800: '#1f2937',
      900: '#111827',
    },

    // Semantic colors
    semantic: {
      success: '#16a34a',
      warning: '#ca8a04',
      error: '#dc2626',
      info: '#2563eb',
    }
  },

  /**
   * Typography Scale
   */
  typography: {
    fontFamily: {
      sans: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
      mono: '"JetBrains Mono", "Fira Code", monospace',
    },
    fontSize: {
      xs: '0.75rem',    // 12px
      sm: '0.875rem',   // 14px
      base: '1rem',     // 16px
      lg: '1.125rem',   // 18px
      xl: '1.25rem',    // 20px
      '2xl': '1.5rem',  // 24px
      '3xl': '1.875rem',// 30px
      '4xl': '2.25rem', // 36px
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: {
      tight: 1.25,
      normal: 1.5,
      relaxed: 1.75,
    },
  },

  /**
   * Spacing Scale
   */
  spacing: {
    xs: '0.25rem',   // 4px
    sm: '0.5rem',    // 8px
    md: '1rem',      // 16px
    lg: '1.5rem',    // 24px
    xl: '2rem',      // 32px
    '2xl': '3rem',   // 48px
    '3xl': '4rem',   // 64px
    '4xl': '6rem',   // 96px
  },

  /**
   * Border Radius
   */
  borderRadius: {
    sm: '0.375rem',  // 6px
    md: '0.5rem',    // 8px
    lg: '0.75rem',   // 12px
    xl: '1rem',      // 16px
    '2xl': '1.5rem', // 24px
    full: '9999px',
  },

  /**
   * Shadows
   */
  shadows: {
    soft: '0 2px 15px rgba(0, 0, 0, 0.08)',
    medium: '0 4px 20px rgba(0, 0, 0, 0.12)',
    hard: '0 10px 40px rgba(0, 0, 0, 0.2)',
    glowPrimary: '0 0 20px rgba(37, 99, 235, 0.3)',
    glowAccent: '0 0 20px rgba(147, 51, 234, 0.3)',
  },

  /**
   * Animation Timing
   */
  animation: {
    duration: {
      fast: '200ms',
      normal: '300ms',
      slow: '400ms',
      slower: '600ms',
      slowest: '800ms',
    },
    easing: {
      // Luxury easing for smooth, premium feel
      luxury: 'cubic-bezier(0.22, 1, 0.36, 1)',
      easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
      easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
      spring: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
    },
  },

  /**
   * Breakpoints
   */
  breakpoints: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  },

  /**
   * Z-index Scale
   */
  zIndex: {
    base: 0,
    dropdown: 1000,
    sticky: 1100,
    overlay: 1200,
    modal: 1300,
    toast: 1400,
  },

  /**
   * Component-Specific Tokens
   */
  components: {
    input: {
      height: {
        sm: '2.5rem',   // 40px
        md: '3rem',     // 48px
        lg: '3.5rem',   // 56px
      },
      padding: {
        horizontal: '1rem',
        vertical: '0.75rem',
      },
      borderWidth: '2px',
      focusRingWidth: '2px',
      focusRingOffset: '2px',
    },

    button: {
      height: {
        sm: '2.25rem',  // 36px
        md: '2.75rem',  // 44px
        lg: '3rem',     // 48px
      },
      padding: {
        sm: '0.75rem 1rem',
        md: '1rem 1.5rem',
        lg: '1rem 2rem',
      },
      minTouchTarget: '44px', // WCAG AA minimum
    },

    card: {
      padding: {
        sm: '1rem',     // 16px
        md: '1.5rem',   // 24px
        lg: '2rem',     // 32px
      },
      maxWidth: '28rem', // 448px
    },

    progress: {
      height: '0.5rem',       // 8px
      indicatorHeight: '2.5rem', // 40px
    },
  },

  /**
   * Accessibility
   */
  accessibility: {
    minContrastRatio: 4.5,        // WCAG AA for normal text
    minLargeTextRatio: 3,         // WCAG AA for large text
    minTouchTarget: '44px',       // Minimum touch target size
    focusRingColor: '#2563eb',
    focusRingWidth: '2px',
    focusRingOffset: '2px',
  },
} as const;

/**
 * Helper function to get theme colors based on account type
 */
export function getThemeColors(accountType: 'researcher' | 'admin') {
  return accountType === 'admin' ? authTokens.colors.accent : authTokens.colors.primary;
}

/**
 * Helper function to generate focus ring classes
 */
export function getFocusRingClasses(accountType: 'researcher' | 'admin') {
  const baseClasses = 'focus-visible:ring-2 focus-visible:ring-offset-2';
  const colorClass = accountType === 'admin'
    ? 'focus-visible:ring-accent-600'
    : 'focus-visible:ring-primary-600';
  return `${baseClasses} ${colorClass}`;
}

/**
 * Helper function to generate shadow glow classes
 */
export function getGlowClasses(accountType: 'researcher' | 'admin') {
  return accountType === 'admin' ? 'shadow-glow-accent' : 'shadow-glow-primary';
}

/**
 * Helper function to generate gradient background
 */
export function getGradientBackground(accountType: 'researcher' | 'admin') {
  if (accountType === 'admin') {
    return 'bg-gradient-to-br from-accent-600 via-accent-700 to-purple-600';
  }
  return 'bg-gradient-to-br from-primary-600 via-primary-700 to-accent-600';
}

/**
 * Password strength thresholds and colors
 */
export const passwordStrength = {
  thresholds: {
    weak: 40,
    fair: 60,
    good: 80,
    excellent: 100,
  },
  colors: {
    weak: '#dc2626',    // red-600
    fair: '#ca8a04',    // yellow-600
    good: '#2563eb',    // blue-600
    excellent: '#16a34a', // green-600
  },
  labels: {
    weak: 'Weak',
    fair: 'Fair',
    good: 'Good',
    excellent: 'Excellent',
  },
} as const;

export type AuthTokens = typeof authTokens;
export type ThemeColors = typeof authTokens.colors.primary;
export type AccountType = 'researcher' | 'admin';
