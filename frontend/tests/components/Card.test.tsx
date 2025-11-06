import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Card, CardHeader, CardContent, CardFooter } from '@/components/shared/Card';

describe('Card Component', () => {
  describe('Card', () => {
    it('renders children correctly', () => {
      render(<Card>Card Content</Card>);
      expect(screen.getByText('Card Content')).toBeInTheDocument();
    });

    it('applies default variant', () => {
      render(<Card data-testid="card">Content</Card>);
      const card = screen.getByTestId('card');
      expect(card).toHaveClass('bg-white', 'rounded-lg');
    });

    it('applies bordered variant', () => {
      render(<Card variant="bordered" data-testid="card">Content</Card>);
      const card = screen.getByTestId('card');
      expect(card).toHaveClass('border', 'border-gray-200');
    });

    it('applies elevated variant with shadow', () => {
      render(<Card variant="elevated" data-testid="card">Content</Card>);
      const card = screen.getByTestId('card');
      expect(card).toHaveClass('shadow-md');
    });

    it('applies padding none', () => {
      render(<Card padding="none" data-testid="card">Content</Card>);
      const card = screen.getByTestId('card');
      expect(card).not.toHaveClass('p-3', 'p-4', 'p-6');
    });

    it('applies padding small', () => {
      render(<Card padding="sm" data-testid="card">Content</Card>);
      const card = screen.getByTestId('card');
      expect(card).toHaveClass('p-3');
    });

    it('applies padding medium (default)', () => {
      render(<Card padding="md" data-testid="card">Content</Card>);
      const card = screen.getByTestId('card');
      expect(card).toHaveClass('p-4');
    });

    it('applies padding large', () => {
      render(<Card padding="lg" data-testid="card">Content</Card>);
      const card = screen.getByTestId('card');
      expect(card).toHaveClass('p-6');
    });

    it('applies hover effect when hover prop is true', () => {
      render(<Card hover data-testid="card">Content</Card>);
      const card = screen.getByTestId('card');
      expect(card).toHaveClass('hover:shadow-lg', 'transition-shadow', 'cursor-pointer');
    });

    it('applies custom className', () => {
      render(<Card className="custom-class" data-testid="card">Content</Card>);
      const card = screen.getByTestId('card');
      expect(card).toHaveClass('custom-class');
    });
  });

  describe('CardHeader', () => {
    it('renders title', () => {
      render(<CardHeader title="Card Title" />);
      expect(screen.getByText('Card Title')).toBeInTheDocument();
    });

    it('renders subtitle when provided', () => {
      render(<CardHeader title="Title" subtitle="Subtitle" />);
      expect(screen.getByText('Subtitle')).toBeInTheDocument();
    });

    it('does not render subtitle when not provided', () => {
      render(<CardHeader title="Title" />);
      expect(screen.queryByText('Subtitle')).not.toBeInTheDocument();
    });

    it('renders action element when provided', () => {
      render(
        <CardHeader
          title="Title"
          action={<button>Action</button>}
        />
      );
      expect(screen.getByRole('button', { name: /action/i })).toBeInTheDocument();
    });

    it('applies custom className', () => {
      render(
        <CardHeader
          title="Title"
          className="custom-header"
          data-testid="header"
        />
      );
      const header = screen.getByTestId('header');
      expect(header).toHaveClass('custom-header');
    });

    it('has proper layout classes', () => {
      render(<CardHeader title="Title" data-testid="header" />);
      const header = screen.getByTestId('header');
      expect(header).toHaveClass('mb-4');
    });

    it('renders title with correct styling', () => {
      render(<CardHeader title="Test Title" />);
      const title = screen.getByText('Test Title');
      expect(title).toHaveClass('text-lg', 'font-semibold', 'text-gray-900');
    });

    it('renders subtitle with correct styling', () => {
      render(<CardHeader title="Title" subtitle="Test Subtitle" />);
      const subtitle = screen.getByText('Test Subtitle');
      expect(subtitle).toHaveClass('text-sm', 'text-gray-600', 'mt-1');
    });
  });

  describe('CardContent', () => {
    it('renders children', () => {
      render(<CardContent>Card content goes here</CardContent>);
      expect(screen.getByText('Card content goes here')).toBeInTheDocument();
    });

    it('applies default styling', () => {
      render(<CardContent data-testid="content">Content</CardContent>);
      const content = screen.getByTestId('content');
      expect(content).toHaveClass('text-gray-700');
    });

    it('applies custom className', () => {
      render(
        <CardContent className="custom-content" data-testid="content">
          Content
        </CardContent>
      );
      const content = screen.getByTestId('content');
      expect(content).toHaveClass('custom-content');
    });

    it('renders complex content', () => {
      render(
        <CardContent>
          <p>Paragraph 1</p>
          <p>Paragraph 2</p>
        </CardContent>
      );
      expect(screen.getByText('Paragraph 1')).toBeInTheDocument();
      expect(screen.getByText('Paragraph 2')).toBeInTheDocument();
    });
  });

  describe('CardFooter', () => {
    it('renders children', () => {
      render(<CardFooter>Footer content</CardFooter>);
      expect(screen.getByText('Footer content')).toBeInTheDocument();
    });

    it('applies default styling with border', () => {
      render(<CardFooter data-testid="footer">Footer</CardFooter>);
      const footer = screen.getByTestId('footer');
      expect(footer).toHaveClass('mt-4', 'pt-4', 'border-t', 'border-gray-200');
    });

    it('applies custom className', () => {
      render(
        <CardFooter className="custom-footer" data-testid="footer">
          Footer
        </CardFooter>
      );
      const footer = screen.getByTestId('footer');
      expect(footer).toHaveClass('custom-footer');
    });

    it('renders action buttons', () => {
      render(
        <CardFooter>
          <button>Cancel</button>
          <button>Submit</button>
        </CardFooter>
      );
      expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument();
    });
  });

  describe('Composite Card', () => {
    it('renders complete card with all components', () => {
      render(
        <Card>
          <CardHeader title="Test Card" subtitle="Test Subtitle" />
          <CardContent>Test Content</CardContent>
          <CardFooter>Test Footer</CardFooter>
        </Card>
      );

      expect(screen.getByText('Test Card')).toBeInTheDocument();
      expect(screen.getByText('Test Subtitle')).toBeInTheDocument();
      expect(screen.getByText('Test Content')).toBeInTheDocument();
      expect(screen.getByText('Test Footer')).toBeInTheDocument();
    });

    it('works with minimal configuration', () => {
      render(
        <Card>
          <CardHeader title="Simple Card" />
          <CardContent>Simple content</CardContent>
        </Card>
      );

      expect(screen.getByText('Simple Card')).toBeInTheDocument();
      expect(screen.getByText('Simple content')).toBeInTheDocument();
    });
  });
});
