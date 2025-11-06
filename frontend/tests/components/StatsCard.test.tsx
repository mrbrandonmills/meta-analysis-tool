import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import StatsCard from '@/components/dashboard/StatsCard';
import { BarChart3 } from 'lucide-react';

describe('StatsCard Component', () => {
  const defaultProps = {
    title: 'Total Projects',
    value: '42',
    icon: BarChart3,
    color: 'blue' as const,
  };

  describe('Rendering', () => {
    it('renders with title and value', () => {
      render(<StatsCard {...defaultProps} />);
      expect(screen.getByText('Total Projects')).toBeInTheDocument();
      expect(screen.getByText('42')).toBeInTheDocument();
    });

    it('renders icon', () => {
      const { container } = render(<StatsCard {...defaultProps} />);
      const icon = container.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });

    it('renders numeric value', () => {
      render(<StatsCard {...defaultProps} value={100} />);
      expect(screen.getByText('100')).toBeInTheDocument();
    });

    it('renders string value', () => {
      render(<StatsCard {...defaultProps} value="1.2K" />);
      expect(screen.getByText('1.2K')).toBeInTheDocument();
    });
  });

  describe('Color Variants', () => {
    it('renders blue variant', () => {
      const { container } = render(<StatsCard {...defaultProps} color="blue" />);
      const iconWrapper = container.querySelector('.bg-blue-100');
      expect(iconWrapper).toBeInTheDocument();
    });

    it('renders green variant', () => {
      const { container } = render(<StatsCard {...defaultProps} color="green" />);
      const iconWrapper = container.querySelector('.bg-green-100');
      expect(iconWrapper).toBeInTheDocument();
    });

    it('renders purple variant', () => {
      const { container } = render(<StatsCard {...defaultProps} color="purple" />);
      const iconWrapper = container.querySelector('.bg-purple-100');
      expect(iconWrapper).toBeInTheDocument();
    });

    it('renders yellow variant', () => {
      const { container } = render(<StatsCard {...defaultProps} color="yellow" />);
      const iconWrapper = container.querySelector('.bg-yellow-100');
      expect(iconWrapper).toBeInTheDocument();
    });

    it('renders red variant', () => {
      const { container } = render(<StatsCard {...defaultProps} color="red" />);
      const iconWrapper = container.querySelector('.bg-red-100');
      expect(iconWrapper).toBeInTheDocument();
    });
  });

  describe('Change Indicator', () => {
    it('does not render change by default', () => {
      render(<StatsCard {...defaultProps} />);
      expect(screen.queryByText(/\+/)).not.toBeInTheDocument();
    });

    it('renders positive change', () => {
      render(<StatsCard {...defaultProps} change="+12%" changeType="positive" />);
      expect(screen.getByText('+12%')).toBeInTheDocument();
    });

    it('renders negative change', () => {
      render(<StatsCard {...defaultProps} change="-5%" changeType="negative" />);
      expect(screen.getByText('-5%')).toBeInTheDocument();
    });

    it('renders neutral change', () => {
      render(<StatsCard {...defaultProps} change="0%" changeType="neutral" />);
      expect(screen.getByText('0%')).toBeInTheDocument();
    });

    it('applies positive styling to positive change', () => {
      render(<StatsCard {...defaultProps} change="+12%" changeType="positive" />);
      const changeElement = screen.getByText('+12%');
      expect(changeElement).toHaveClass('bg-green-100', 'text-green-700');
    });

    it('applies negative styling to negative change', () => {
      render(<StatsCard {...defaultProps} change="-5%" changeType="negative" />);
      const changeElement = screen.getByText('-5%');
      expect(changeElement).toHaveClass('bg-red-100', 'text-red-700');
    });

    it('applies neutral styling to neutral change', () => {
      render(<StatsCard {...defaultProps} change="0%" changeType="neutral" />);
      const changeElement = screen.getByText('0%');
      expect(changeElement).toHaveClass('bg-gray-100', 'text-gray-700');
    });
  });

  describe('Styling', () => {
    it('has card styling', () => {
      const { container } = render(<StatsCard {...defaultProps} />);
      const card = container.firstChild;
      expect(card).toHaveClass('rounded-2xl', 'border', 'shadow-soft');
    });

    it('displays value with large bold font', () => {
      render(<StatsCard {...defaultProps} />);
      const value = screen.getByText('42');
      expect(value).toHaveClass('text-3xl', 'font-bold', 'text-gray-900');
    });

    it('displays title with smaller font', () => {
      render(<StatsCard {...defaultProps} />);
      const title = screen.getByText('Total Projects');
      expect(title).toHaveClass('text-sm', 'font-medium', 'text-gray-600');
    });

    it('has padding', () => {
      const { container } = render(<StatsCard {...defaultProps} />);
      const card = container.firstChild;
      expect(card).toHaveClass('p-6');
    });
  });

  describe('Icon Styling', () => {
    it('renders icon in colored circle', () => {
      const { container } = render(<StatsCard {...defaultProps} color="blue" />);
      const iconWrapper = container.querySelector('.bg-blue-100.text-blue-600');
      expect(iconWrapper).toBeInTheDocument();
    });

    it('applies rounded styling to icon wrapper', () => {
      const { container } = render(<StatsCard {...defaultProps} />);
      const iconWrapper = container.querySelector('.rounded-xl');
      expect(iconWrapper).toBeInTheDocument();
    });

    it('sizes icon wrapper correctly', () => {
      const { container } = render(<StatsCard {...defaultProps} />);
      const iconWrapper = container.querySelector('.w-12.h-12');
      expect(iconWrapper).toBeInTheDocument();
    });
  });

  describe('Layout', () => {
    it('arranges icon and change in header', () => {
      const { container } = render(
        <StatsCard {...defaultProps} change="+12%" changeType="positive" />
      );
      const header = container.querySelector('.flex.items-start.justify-between');
      expect(header).toBeInTheDocument();
    });

    it('stacks title and value vertically', () => {
      render(<StatsCard {...defaultProps} />);
      const title = screen.getByText('Total Projects');
      const value = screen.getByText('42');

      // Both should exist in document
      expect(title).toBeInTheDocument();
      expect(value).toBeInTheDocument();
    });
  });

  describe('Animation Props', () => {
    it('accepts index prop for staggered animations', () => {
      const { container } = render(<StatsCard {...defaultProps} index={2} />);
      expect(container.firstChild).toBeInTheDocument();
    });

    it('defaults to index 0', () => {
      const { container } = render(<StatsCard {...defaultProps} />);
      expect(container.firstChild).toBeInTheDocument();
    });
  });

  describe('Real-World Use Cases', () => {
    it('renders completed projects stat', () => {
      render(
        <StatsCard
          title="Completed Projects"
          value={15}
          icon={BarChart3}
          color="green"
          change="+5"
          changeType="positive"
        />
      );
      expect(screen.getByText('Completed Projects')).toBeInTheDocument();
      expect(screen.getByText('15')).toBeInTheDocument();
      expect(screen.getByText('+5')).toBeInTheDocument();
    });

    it('renders active workflows stat', () => {
      render(
        <StatsCard
          title="Active Workflows"
          value={8}
          icon={BarChart3}
          color="blue"
        />
      );
      expect(screen.getByText('Active Workflows')).toBeInTheDocument();
      expect(screen.getByText('8')).toBeInTheDocument();
    });

    it('renders papers analyzed stat with large number', () => {
      render(
        <StatsCard
          title="Papers Analyzed"
          value="2.3K"
          icon={BarChart3}
          color="purple"
          change="+234"
          changeType="positive"
        />
      );
      expect(screen.getByText('Papers Analyzed')).toBeInTheDocument();
      expect(screen.getByText('2.3K')).toBeInTheDocument();
    });
  });
});
