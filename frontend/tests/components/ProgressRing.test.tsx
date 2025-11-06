import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import ProgressRing from '@/components/visualizations/ProgressRing';

describe('ProgressRing Component', () => {
  describe('Rendering', () => {
    it('renders with progress value', () => {
      const { container } = render(<ProgressRing progress={50} />);
      expect(container.querySelector('svg')).toBeInTheDocument();
    });

    it('displays percentage by default', () => {
      render(<ProgressRing progress={75} />);
      expect(screen.getByText('75%')).toBeInTheDocument();
    });

    it('rounds percentage to nearest integer', () => {
      render(<ProgressRing progress={66.7} />);
      expect(screen.getByText('67%')).toBeInTheDocument();
    });

    it('hides percentage when showPercentage is false', () => {
      render(<ProgressRing progress={50} showPercentage={false} />);
      expect(screen.queryByText('50%')).not.toBeInTheDocument();
    });
  });

  describe('SVG Structure', () => {
    it('renders SVG with correct dimensions', () => {
      const { container } = render(<ProgressRing progress={50} size={100} />);
      const svg = container.querySelector('svg');
      expect(svg).toHaveAttribute('width', '100');
      expect(svg).toHaveAttribute('height', '100');
    });

    it('uses default size of 120', () => {
      const { container } = render(<ProgressRing progress={50} />);
      const svg = container.querySelector('svg');
      expect(svg).toHaveAttribute('width', '120');
      expect(svg).toHaveAttribute('height', '120');
    });

    it('renders background circle', () => {
      const { container } = render(<ProgressRing progress={50} />);
      const circles = container.querySelectorAll('circle');
      expect(circles.length).toBe(2); // Background + progress circle
    });

    it('applies custom background color', () => {
      const { container } = render(
        <ProgressRing progress={50} backgroundColor="#ff0000" />
      );
      const circles = container.querySelectorAll('circle');
      const bgCircle = circles[0];
      expect(bgCircle).toHaveAttribute('stroke', '#ff0000');
    });

    it('applies custom progress color', () => {
      const { container } = render(
        <ProgressRing progress={50} color="#00ff00" />
      );
      const circles = container.querySelectorAll('circle');
      const progressCircle = circles[1];
      expect(progressCircle).toHaveAttribute('stroke', '#00ff00');
    });
  });

  describe('Progress Values', () => {
    it('renders 0% progress', () => {
      render(<ProgressRing progress={0} />);
      expect(screen.getByText('0%')).toBeInTheDocument();
    });

    it('renders 100% progress', () => {
      render(<ProgressRing progress={100} />);
      expect(screen.getByText('100%')).toBeInTheDocument();
    });

    it('renders partial progress correctly', () => {
      render(<ProgressRing progress={33} />);
      expect(screen.getByText('33%')).toBeInTheDocument();
    });

    it('handles decimal progress values', () => {
      render(<ProgressRing progress={45.8} />);
      expect(screen.getByText('46%')).toBeInTheDocument();
    });
  });

  describe('Customization', () => {
    it('applies custom stroke width', () => {
      const { container } = render(
        <ProgressRing progress={50} strokeWidth={12} />
      );
      const circles = container.querySelectorAll('circle');
      circles.forEach(circle => {
        expect(circle).toHaveAttribute('stroke-width', '12');
      });
    });

    it('uses default stroke width of 8', () => {
      const { container } = render(<ProgressRing progress={50} />);
      const circles = container.querySelectorAll('circle');
      circles.forEach(circle => {
        expect(circle).toHaveAttribute('stroke-width', '8');
      });
    });

    it('applies custom className', () => {
      const { container } = render(
        <ProgressRing progress={50} className="custom-ring" />
      );
      const wrapper = container.querySelector('.custom-ring');
      expect(wrapper).toBeInTheDocument();
    });

    it('uses custom size for all calculations', () => {
      const { container } = render(
        <ProgressRing progress={50} size={200} strokeWidth={10} />
      );
      const svg = container.querySelector('svg');
      expect(svg).toHaveAttribute('width', '200');
      expect(svg).toHaveAttribute('height', '200');
    });
  });

  describe('Circle Calculations', () => {
    it('calculates circle radius correctly', () => {
      const size = 120;
      const strokeWidth = 8;
      const expectedRadius = (size - strokeWidth) / 2;

      const { container } = render(
        <ProgressRing progress={50} size={size} strokeWidth={strokeWidth} />
      );
      const circles = container.querySelectorAll('circle');

      circles.forEach(circle => {
        expect(circle).toHaveAttribute('r', expectedRadius.toString());
      });
    });

    it('centers circles in SVG', () => {
      const size = 120;
      const center = size / 2;

      const { container } = render(
        <ProgressRing progress={50} size={size} />
      );
      const circles = container.querySelectorAll('circle');

      circles.forEach(circle => {
        expect(circle).toHaveAttribute('cx', center.toString());
        expect(circle).toHaveAttribute('cy', center.toString());
      });
    });
  });

  describe('Styling', () => {
    it('applies transform rotation to SVG', () => {
      const { container } = render(<ProgressRing progress={50} />);
      const svg = container.querySelector('svg');
      expect(svg).toHaveClass('transform', '-rotate-90');
    });

    it('has rounded line caps on progress circle', () => {
      const { container } = render(<ProgressRing progress={50} />);
      const circles = container.querySelectorAll('circle');
      const progressCircle = circles[1];
      expect(progressCircle).toHaveAttribute('stroke-linecap', 'round');
    });

    it('sets fill to none on circles', () => {
      const { container } = render(<ProgressRing progress={50} />);
      const circles = container.querySelectorAll('circle');
      circles.forEach(circle => {
        expect(circle).toHaveAttribute('fill', 'none');
      });
    });
  });

  describe('Percentage Display', () => {
    it('renders percentage with correct styling', () => {
      render(<ProgressRing progress={50} />);
      const percentage = screen.getByText('50%');
      expect(percentage).toHaveClass('text-2xl', 'font-bold', 'text-gray-900');
    });

    it('positions percentage text absolutely', () => {
      const { container } = render(<ProgressRing progress={50} />);
      const textWrapper = container.querySelector('.absolute');
      expect(textWrapper).toHaveClass('inset-0', 'flex', 'items-center', 'justify-center');
    });
  });

  describe('Use Cases', () => {
    it('renders project completion progress', () => {
      render(<ProgressRing progress={67} color="#10b981" />);
      expect(screen.getByText('67%')).toBeInTheDocument();
    });

    it('renders workflow progress', () => {
      render(<ProgressRing progress={25} color="#3b82f6" />);
      expect(screen.getByText('25%')).toBeInTheDocument();
    });

    it('renders small progress ring', () => {
      const { container } = render(
        <ProgressRing progress={90} size={80} strokeWidth={6} />
      );
      const svg = container.querySelector('svg');
      expect(svg).toHaveAttribute('width', '80');
    });

    it('renders large progress ring', () => {
      const { container } = render(
        <ProgressRing progress={90} size={200} strokeWidth={12} />
      );
      const svg = container.querySelector('svg');
      expect(svg).toHaveAttribute('width', '200');
    });
  });
});
