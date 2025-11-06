# Frontend Test Suite Documentation

## Overview

This directory contains comprehensive tests for the Meta-Analysis Tool frontend application. The test suite is built with **Vitest**, **React Testing Library**, and follows industry best practices for modern React applications.

## Table of Contents

- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Writing Tests](#writing-tests)
- [Test Patterns](#test-patterns)
- [Mock Strategy](#mock-strategy)
- [Accessibility Testing](#accessibility-testing)

## Test Structure

```
tests/
├── setup.ts                  # Global test configuration
├── components/              # Component tests
│   ├── Button.test.tsx
│   ├── Card.test.tsx
│   ├── Badge.test.tsx
│   ├── ProgressRing.test.tsx
│   ├── StatsCard.test.tsx
│   ├── AgentPipeline.test.tsx
│   └── ProjectCard.test.tsx
├── hooks/                   # Custom hook tests
│   ├── useAuth.test.ts
│   └── useProjects.test.ts
├── integration/             # Integration tests
│   └── apiClient.test.ts
├── e2e/                    # End-to-end tests
├── fixtures/               # Test data and fixtures
├── accessibility/          # A11y specific tests
└── unit/                   # Pure utility function tests
```

## Running Tests

### Basic Commands

```bash
# Run tests in watch mode
npm test

# Run tests once
npm run test:run

# Run tests with coverage
npm run test:coverage

# Run tests with UI
npm run test:ui
```

### Running Specific Tests

```bash
# Run specific test file
npm test Button.test.tsx

# Run tests matching pattern
npm test -- --grep="Button"

# Run tests in specific directory
npm test tests/components
```

## Test Coverage

### Coverage Goals

- **Overall Coverage**: 80%+ (Lines, Functions, Branches, Statements)
- **Components**: 85%+ coverage
- **Hooks**: 90%+ coverage
- **Utils**: 80%+ coverage

### Coverage Reports

Coverage reports are generated in multiple formats:

- **Terminal**: Text summary in console
- **HTML**: `coverage/index.html` - Interactive browser report
- **JSON**: `coverage/coverage-final.json` - For CI/CD integration
- **LCOV**: `coverage/lcov.info` - For code coverage services

### Viewing Coverage

```bash
# Generate and open HTML coverage report
npm run test:coverage
open coverage/index.html
```

## Writing Tests

### Component Test Template

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ComponentName } from '@/components/path/to/Component';

describe('ComponentName', () => {
  describe('Rendering', () => {
    it('renders with required props', () => {
      render(<ComponentName prop="value" />);
      expect(screen.getByText('expected text')).toBeInTheDocument();
    });
  });

  describe('Interactions', () => {
    it('handles user interactions', async () => {
      const user = userEvent.setup();
      const handleClick = vi.fn();

      render(<ComponentName onClick={handleClick} />);
      await user.click(screen.getByRole('button'));

      expect(handleClick).toHaveBeenCalledTimes(1);
    });
  });

  describe('Accessibility', () => {
    it('is keyboard navigable', () => {
      render(<ComponentName />);
      const element = screen.getByRole('button');
      expect(element).toHaveClass('focus-visible:ring-2');
    });
  });
});
```

### Hook Test Template

```typescript
import { describe, it, expect, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useCustomHook } from '@/hooks/useCustomHook';

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } }
  });

  return ({ children }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('useCustomHook', () => {
  it('returns expected initial state', () => {
    const { result } = renderHook(() => useCustomHook(), {
      wrapper: createWrapper(),
    });

    expect(result.current.data).toBeUndefined();
    expect(result.current.isLoading).toBe(true);
  });

  it('handles async operations', async () => {
    const { result } = renderHook(() => useCustomHook(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      await result.current.mutate(data);
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
  });
});
```

## Test Patterns

### 1. Arrange-Act-Assert (AAA)

```typescript
it('follows AAA pattern', async () => {
  // Arrange
  const user = userEvent.setup();
  const handleSubmit = vi.fn();
  render(<Form onSubmit={handleSubmit} />);

  // Act
  await user.type(screen.getByLabelText('Email'), 'test@example.com');
  await user.click(screen.getByRole('button', { name: /submit/i }));

  // Assert
  expect(handleSubmit).toHaveBeenCalledWith({
    email: 'test@example.com'
  });
});
```

### 2. Test Variants Systematically

```typescript
describe('Button variants', () => {
  const variants = ['primary', 'secondary', 'outline', 'ghost', 'danger'];

  variants.forEach(variant => {
    it(`renders ${variant} variant correctly`, () => {
      render(<Button variant={variant}>Click me</Button>);
      const button = screen.getByRole('button');
      expect(button).toMatchSnapshot();
    });
  });
});
```

### 3. Test Edge Cases

```typescript
describe('Edge cases', () => {
  it('handles empty data', () => {
    render(<List items={[]} />);
    expect(screen.getByText('No items')).toBeInTheDocument();
  });

  it('handles very long strings', () => {
    const longString = 'a'.repeat(1000);
    render(<Text>{longString}</Text>);
    expect(screen.getByText(longString, { exact: false })).toBeInTheDocument();
  });

  it('handles null values gracefully', () => {
    render(<Component value={null} />);
    expect(screen.queryByText('undefined')).not.toBeInTheDocument();
  });
});
```

## Mock Strategy

### Mocking External Dependencies

```typescript
// Mock Next.js router
vi.mock('next/router', () => ({
  useRouter: () => ({
    push: vi.fn(),
    pathname: '/',
    query: {},
    asPath: '/',
  }),
}));

// Mock react-hot-toast
vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

// Mock API calls
vi.mock('@/lib/api', () => ({
  authApi: {
    login: vi.fn(),
    logout: vi.fn(),
    getCurrentUser: vi.fn(),
  },
}));
```

### Mocking localStorage

```typescript
beforeEach(() => {
  const mockStorage = {};

  Object.defineProperty(window, 'localStorage', {
    value: {
      getItem: vi.fn((key) => mockStorage[key] || null),
      setItem: vi.fn((key, value) => { mockStorage[key] = value }),
      removeItem: vi.fn((key) => { delete mockStorage[key] }),
      clear: vi.fn(() => { mockStorage = {} }),
    },
    writable: true,
  });
});
```

## Accessibility Testing

### Keyboard Navigation

```typescript
it('is keyboard navigable', async () => {
  const user = userEvent.setup();
  render(<Navigation />);

  // Tab through elements
  await user.tab();
  expect(screen.getByRole('link', { name: 'Home' })).toHaveFocus();

  // Enter key activates
  await user.keyboard('{Enter}');
  expect(mockNavigate).toHaveBeenCalled();
});
```

### Screen Reader Support

```typescript
it('provides screen reader labels', () => {
  render(<IconButton icon={<CloseIcon />} />);

  const button = screen.getByRole('button');
  expect(button).toHaveAttribute('aria-label');
});

it('announces loading state', () => {
  render(<Button loading>Submit</Button>);

  const button = screen.getByRole('button');
  expect(button).toHaveAttribute('aria-busy', 'true');
});
```

### Focus Management

```typescript
it('manages focus correctly', async () => {
  const user = userEvent.setup();
  render(<Dialog />);

  // Open dialog
  await user.click(screen.getByRole('button', { name: 'Open' }));

  // Focus traps in dialog
  const dialog = screen.getByRole('dialog');
  expect(dialog).toContainFocus();

  // Close returns focus
  await user.keyboard('{Escape}');
  expect(screen.getByRole('button', { name: 'Open' })).toHaveFocus();
});
```

## Best Practices

### 1. Test User Behavior, Not Implementation

```typescript
// Good - tests user behavior
it('allows user to submit form', async () => {
  const user = userEvent.setup();
  render(<LoginForm />);

  await user.type(screen.getByLabelText('Email'), 'user@example.com');
  await user.type(screen.getByLabelText('Password'), 'password123');
  await user.click(screen.getByRole('button', { name: /log in/i }));

  expect(await screen.findByText('Welcome back!')).toBeInTheDocument();
});

// Bad - tests implementation details
it('calls handleSubmit with form data', () => {
  const handleSubmit = vi.fn();
  render(<LoginForm onSubmit={handleSubmit} />);
  // Testing internal function calls
});
```

### 2. Use Semantic Queries

```typescript
// Priority order (best to worst):
// 1. getByRole (best for accessibility)
screen.getByRole('button', { name: /submit/i })

// 2. getByLabelText (good for forms)
screen.getByLabelText('Email address')

// 3. getByPlaceholderText (fallback)
screen.getByPlaceholderText('Enter email')

// 4. getByText (content)
screen.getByText('Welcome!')

// 5. getByTestId (last resort)
screen.getByTestId('custom-element')
```

### 3. Wait for Async Operations

```typescript
// Good - waits for element
await waitFor(() => {
  expect(screen.getByText('Data loaded')).toBeInTheDocument();
});

// Good - finds element when it appears
const element = await screen.findByText('Data loaded');

// Bad - may cause race conditions
expect(screen.getByText('Data loaded')).toBeInTheDocument();
```

### 4. Clean Up After Tests

```typescript
afterEach(() => {
  vi.clearAllMocks();
  cleanup(); // Automatically called by setup.ts
});

afterAll(() => {
  vi.restoreAllMocks();
});
```

## Debugging Tests

### Using debug()

```typescript
import { render, screen } from '@testing-library/react';

it('debugs component output', () => {
  const { debug } = render(<MyComponent />);

  // Print entire document
  debug();

  // Print specific element
  debug(screen.getByRole('button'));
});
```

### Using logTestingPlaygroundURL()

```typescript
import { render, screen, logTestingPlaygroundURL } from '@testing-library/react';

it('gets query suggestions', () => {
  render(<MyComponent />);

  // Opens Testing Playground with current DOM
  logTestingPlaygroundURL();
});
```

### Verbose Test Output

```bash
# Run with verbose output
npm test -- --reporter=verbose

# Run with debugging
DEBUG=* npm test
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm test -- --coverage
      - uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info
```

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Testing Library Queries](https://testing-library.com/docs/queries/about)
- [Jest-DOM Matchers](https://github.com/testing-library/jest-dom)
- [userEvent API](https://testing-library.com/docs/user-event/intro)
- [Common Mistakes](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)

## Support

For questions or issues:
1. Check existing test examples in this directory
2. Review Testing Library documentation
3. Open an issue on the project repository

---

**Last Updated**: November 2025
**Maintained by**: Meta-Analysis Tool Development Team
