import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Badge } from '@/components/shared/Badge';

describe('Badge Component', () => {
  describe('Rendering', () => {
    it('renders with text content', () => {
      render(<Badge>Badge Text</Badge>);
      expect(screen.getByText('Badge Text')).toBeInTheDocument();
    });

    it('applies default variant', () => {
      render(<Badge data-testid="badge">Default</Badge>);
      const badge = screen.getByTestId('badge');
      expect(badge).toHaveClass('bg-gray-100', 'text-gray-800');
    });

    it('applies default size', () => {
      render(<Badge data-testid="badge">Medium</Badge>);
      const badge = screen.getByTestId('badge');
      expect(badge).toHaveClass('px-2.5', 'py-1', 'text-sm');
    });
  });

  describe('Variants', () => {
    it('renders default variant', () => {
      render(<Badge variant="default" data-testid="badge">Default</Badge>);
      const badge = screen.getByTestId('badge');
      expect(badge).toHaveClass('bg-gray-100', 'text-gray-800', 'border-gray-300');
    });

    it('renders success variant', () => {
      render(<Badge variant="success" data-testid="badge">Success</Badge>);
      const badge = screen.getByTestId('badge');
      expect(badge).toHaveClass('bg-green-100', 'text-green-800', 'border-green-300');
    });

    it('renders warning variant', () => {
      render(<Badge variant="warning" data-testid="badge">Warning</Badge>);
      const badge = screen.getByTestId('badge');
      expect(badge).toHaveClass('bg-yellow-100', 'text-yellow-800', 'border-yellow-300');
    });

    it('renders danger variant', () => {
      render(<Badge variant="danger" data-testid="badge">Danger</Badge>);
      const badge = screen.getByTestId('badge');
      expect(badge).toHaveClass('bg-red-100', 'text-red-800', 'border-red-300');
    });

    it('renders info variant', () => {
      render(<Badge variant="info" data-testid="badge">Info</Badge>);
      const badge = screen.getByTestId('badge');
      expect(badge).toHaveClass('bg-blue-100', 'text-blue-800', 'border-blue-300');
    });

    it('renders purple variant', () => {
      render(<Badge variant="purple" data-testid="badge">Purple</Badge>);
      const badge = screen.getByTestId('badge');
      expect(badge).toHaveClass('bg-purple-100', 'text-purple-800', 'border-purple-300');
    });
  });

  describe('Sizes', () => {
    it('renders small size', () => {
      render(<Badge size="sm" data-testid="badge">Small</Badge>);
      const badge = screen.getByTestId('badge');
      expect(badge).toHaveClass('px-2', 'py-0.5', 'text-xs');
    });

    it('renders medium size', () => {
      render(<Badge size="md" data-testid="badge">Medium</Badge>);
      const badge = screen.getByTestId('badge');
      expect(badge).toHaveClass('px-2.5', 'py-1', 'text-sm');
    });

    it('renders large size', () => {
      render(<Badge size="lg" data-testid="badge">Large</Badge>);
      const badge = screen.getByTestId('badge');
      expect(badge).toHaveClass('px-3', 'py-1.5', 'text-base');
    });
  });

  describe('Dot Indicator', () => {
    it('does not render dot by default', () => {
      const { container } = render(<Badge>No Dot</Badge>);
      const dots = container.querySelectorAll('.w-2.h-2');
      expect(dots.length).toBe(0);
    });

    it('renders dot when dot prop is true', () => {
      const { container } = render(<Badge dot>With Dot</Badge>);
      const dots = container.querySelectorAll('.w-2');
      expect(dots.length).toBeGreaterThan(0);
    });

    it('renders dot with correct color for success variant', () => {
      const { container } = render(
        <Badge variant="success" dot>Success</Badge>
      );
      const dot = container.querySelector('.bg-green-500');
      expect(dot).toBeInTheDocument();
    });

    it('renders dot with correct color for danger variant', () => {
      const { container } = render(
        <Badge variant="danger" dot>Danger</Badge>
      );
      const dot = container.querySelector('.bg-red-500');
      expect(dot).toBeInTheDocument();
    });

    it('renders dot with correct color for warning variant', () => {
      const { container } = render(
        <Badge variant="warning" dot>Warning</Badge>
      );
      const dot = container.querySelector('.bg-yellow-500');
      expect(dot).toBeInTheDocument();
    });

    it('renders dot with correct color for info variant', () => {
      const { container } = render(
        <Badge variant="info" dot>Info</Badge>
      );
      const dot = container.querySelector('.bg-blue-500');
      expect(dot).toBeInTheDocument();
    });

    it('renders dot with correct color for purple variant', () => {
      const { container } = render(
        <Badge variant="purple" dot>Purple</Badge>
      );
      const dot = container.querySelector('.bg-purple-500');
      expect(dot).toBeInTheDocument();
    });
  });

  describe('Styling', () => {
    it('has rounded corners', () => {
      render(<Badge data-testid="badge">Rounded</Badge>);
      const badge = screen.getByTestId('badge');
      expect(badge).toHaveClass('rounded-full');
    });

    it('has border', () => {
      render(<Badge data-testid="badge">Bordered</Badge>);
      const badge = screen.getByTestId('badge');
      expect(badge).toHaveClass('border');
    });

    it('applies custom className', () => {
      render(<Badge className="custom-badge" data-testid="badge">Custom</Badge>);
      const badge = screen.getByTestId('badge');
      expect(badge).toHaveClass('custom-badge');
    });

    it('uses inline-flex display', () => {
      render(<Badge data-testid="badge">Flex</Badge>);
      const badge = screen.getByTestId('badge');
      expect(badge).toHaveClass('inline-flex', 'items-center');
    });
  });

  describe('Status Badge Use Cases', () => {
    it('renders completed status badge', () => {
      render(<Badge variant="success" dot>Completed</Badge>);
      expect(screen.getByText('Completed')).toBeInTheDocument();
    });

    it('renders in-progress status badge', () => {
      render(<Badge variant="info" dot>In Progress</Badge>);
      expect(screen.getByText('In Progress')).toBeInTheDocument();
    });

    it('renders failed status badge', () => {
      render(<Badge variant="danger" dot>Failed</Badge>);
      expect(screen.getByText('Failed')).toBeInTheDocument();
    });

    it('renders pending status badge', () => {
      render(<Badge variant="warning" dot>Pending</Badge>);
      expect(screen.getByText('Pending')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('renders as span element', () => {
      const { container } = render(<Badge>Badge</Badge>);
      const span = container.querySelector('span');
      expect(span).toBeInTheDocument();
    });

    it('supports custom attributes', () => {
      render(<Badge data-testid="badge" aria-label="Status badge">Active</Badge>);
      const badge = screen.getByTestId('badge');
      expect(badge).toHaveAttribute('aria-label', 'Status badge');
    });
  });
});
