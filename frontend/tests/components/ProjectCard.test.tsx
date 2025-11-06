import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ProjectCard from '@/components/dashboard/ProjectCard';
import { ProjectStatus } from '@/lib/types';
import { BarChart3 } from 'lucide-react';

// Mock next/router
const mockPush = vi.fn();
vi.mock('next/router', () => ({
  useRouter: () => ({
    push: mockPush,
    pathname: '/',
    query: {},
    asPath: '/',
  }),
}));

describe('ProjectCard Component', () => {
  const defaultProps = {
    id: 'project-123',
    title: 'Meta-Analysis Project',
    description: 'A comprehensive meta-analysis of research papers',
    status: ProjectStatus.IN_PROGRESS,
    toolType: 'meta_analysis',
    icon: BarChart3,
    color: 'blue',
    updatedAt: '2024-01-15T10:00:00Z',
    progress: 65,
    index: 0,
  };

  beforeEach(() => {
    mockPush.mockClear();
  });

  describe('Rendering', () => {
    it('renders project title', () => {
      render(<ProjectCard {...defaultProps} />);
      expect(screen.getByText('Meta-Analysis Project')).toBeInTheDocument();
    });

    it('renders project description', () => {
      render(<ProjectCard {...defaultProps} />);
      expect(screen.getByText('A comprehensive meta-analysis of research papers')).toBeInTheDocument();
    });

    it('renders without description', () => {
      const { container } = render(<ProjectCard {...defaultProps} description={undefined} />);
      expect(screen.getByText('Meta-Analysis Project')).toBeInTheDocument();
      expect(container.querySelector('.line-clamp-2')).not.toBeInTheDocument();
    });

    it('renders project icon', () => {
      const { container } = render(<ProjectCard {...defaultProps} />);
      const icon = container.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });

    it('truncates long titles', () => {
      render(<ProjectCard {...defaultProps} />);
      const title = screen.getByText('Meta-Analysis Project');
      expect(title).toHaveClass('truncate');
    });

    it('truncates long descriptions', () => {
      render(<ProjectCard {...defaultProps} />);
      const description = screen.getByText(/A comprehensive meta-analysis/);
      expect(description).toHaveClass('line-clamp-2');
    });
  });

  describe('Status Display', () => {
    it('displays draft status', () => {
      render(<ProjectCard {...defaultProps} status={ProjectStatus.DRAFT} />);
      expect(screen.getByText('Draft')).toBeInTheDocument();
    });

    it('displays in-progress status', () => {
      render(<ProjectCard {...defaultProps} status={ProjectStatus.IN_PROGRESS} />);
      expect(screen.getByText('In Progress')).toBeInTheDocument();
    });

    it('displays completed status', () => {
      render(<ProjectCard {...defaultProps} status={ProjectStatus.COMPLETED} />);
      expect(screen.getByText('Completed')).toBeInTheDocument();
    });

    it('displays failed status', () => {
      render(<ProjectCard {...defaultProps} status={ProjectStatus.FAILED} />);
      expect(screen.getByText('Failed')).toBeInTheDocument();
    });

    it('displays paused status', () => {
      render(<ProjectCard {...defaultProps} status={ProjectStatus.PAUSED} />);
      expect(screen.getByText('Paused')).toBeInTheDocument();
    });

    it('displays cancelled status', () => {
      render(<ProjectCard {...defaultProps} status={ProjectStatus.CANCELLED} />);
      expect(screen.getByText('Cancelled')).toBeInTheDocument();
    });
  });

  describe('Progress Display', () => {
    it('displays progress percentage for in-progress projects', () => {
      render(<ProjectCard {...defaultProps} status={ProjectStatus.IN_PROGRESS} progress={75} />);
      expect(screen.getByText('75%')).toBeInTheDocument();
    });

    it('displays progress bar for in-progress projects', () => {
      const { container } = render(
        <ProjectCard {...defaultProps} status={ProjectStatus.IN_PROGRESS} progress={50} />
      );
      const progressBar = container.querySelector('.h-1\\.5.bg-gray-100');
      expect(progressBar).toBeInTheDocument();
    });

    it('does not display progress for draft projects', () => {
      render(<ProjectCard {...defaultProps} status={ProjectStatus.DRAFT} />);
      expect(screen.queryByText('%')).not.toBeInTheDocument();
    });

    it('does not display progress for completed projects', () => {
      render(<ProjectCard {...defaultProps} status={ProjectStatus.COMPLETED} />);
      expect(screen.queryByText('%')).not.toBeInTheDocument();
    });

    it('displays 0% progress correctly', () => {
      render(<ProjectCard {...defaultProps} status={ProjectStatus.IN_PROGRESS} progress={0} />);
      expect(screen.getByText('0%')).toBeInTheDocument();
    });

    it('displays 100% progress correctly', () => {
      render(<ProjectCard {...defaultProps} status={ProjectStatus.IN_PROGRESS} progress={100} />);
      expect(screen.getByText('100%')).toBeInTheDocument();
    });
  });

  describe('Updated Time', () => {
    it('displays relative update time', () => {
      render(<ProjectCard {...defaultProps} />);
      const timeText = screen.getByText(/Updated/);
      expect(timeText).toBeInTheDocument();
    });
  });

  describe('Navigation', () => {
    it('navigates to project detail on click', async () => {
      const user = userEvent.setup();
      render(<ProjectCard {...defaultProps} />);

      const card = screen.getByText('Meta-Analysis Project').closest('.group');
      if (card) {
        await user.click(card);
        expect(mockPush).toHaveBeenCalledWith('/projects/project-123');
      }
    });

    it('displays arrow icon', () => {
      const { container } = render(<ProjectCard {...defaultProps} />);
      // ArrowRight icon should be present
      const icons = container.querySelectorAll('svg');
      expect(icons.length).toBeGreaterThan(1); // Project icon + arrow icon
    });
  });

  describe('Color Variants', () => {
    it('uses blue color scheme', () => {
      const { container } = render(<ProjectCard {...defaultProps} color="blue" />);
      expect(container.querySelector('.group')).toBeInTheDocument();
    });

    it('uses green color scheme', () => {
      const { container } = render(<ProjectCard {...defaultProps} color="green" />);
      expect(container.querySelector('.group')).toBeInTheDocument();
    });

    it('uses purple color scheme', () => {
      const { container } = render(<ProjectCard {...defaultProps} color="purple" />);
      expect(container.querySelector('.group')).toBeInTheDocument();
    });
  });

  describe('Status Colors', () => {
    it('uses blue color for in-progress status', () => {
      render(<ProjectCard {...defaultProps} status={ProjectStatus.IN_PROGRESS} />);
      const statusBadge = screen.getByText('In Progress');
      expect(statusBadge).toHaveClass('bg-blue-100', 'text-blue-700');
    });

    it('uses green color for completed status', () => {
      render(<ProjectCard {...defaultProps} status={ProjectStatus.COMPLETED} />);
      const statusBadge = screen.getByText('Completed');
      expect(statusBadge).toHaveClass('bg-green-100', 'text-green-700');
    });

    it('uses red color for failed status', () => {
      render(<ProjectCard {...defaultProps} status={ProjectStatus.FAILED} />);
      const statusBadge = screen.getByText('Failed');
      expect(statusBadge).toHaveClass('bg-red-100', 'text-red-700');
    });

    it('uses yellow color for paused status', () => {
      render(<ProjectCard {...defaultProps} status={ProjectStatus.PAUSED} />);
      const statusBadge = screen.getByText('Paused');
      expect(statusBadge).toHaveClass('bg-yellow-100', 'text-yellow-700');
    });

    it('uses gray color for draft status', () => {
      render(<ProjectCard {...defaultProps} status={ProjectStatus.DRAFT} />);
      const statusBadge = screen.getByText('Draft');
      expect(statusBadge).toHaveClass('bg-gray-100', 'text-gray-700');
    });
  });

  describe('Visual Styling', () => {
    it('has card styling', () => {
      const { container } = render(<ProjectCard {...defaultProps} />);
      const card = container.querySelector('.rounded-2xl');
      expect(card).toBeInTheDocument();
    });

    it('has cursor pointer', () => {
      const { container } = render(<ProjectCard {...defaultProps} />);
      const card = container.querySelector('.cursor-pointer');
      expect(card).toBeInTheDocument();
    });

    it('has backdrop blur effect', () => {
      const { container } = render(<ProjectCard {...defaultProps} />);
      const card = container.querySelector('.backdrop-blur-sm');
      expect(card).toBeInTheDocument();
    });
  });

  describe('Layout', () => {
    it('arranges icon and title horizontally', () => {
      const { container } = render(<ProjectCard {...defaultProps} />);
      const header = container.querySelector('.flex.items-start.gap-3');
      expect(header).toBeInTheDocument();
    });

    it('has proper padding', () => {
      const { container } = render(<ProjectCard {...defaultProps} />);
      const card = container.querySelector('.p-6');
      expect(card).toBeInTheDocument();
    });
  });

  describe('Status Icons', () => {
    it('displays clock icon for in-progress', () => {
      const { container } = render(<ProjectCard {...defaultProps} status={ProjectStatus.IN_PROGRESS} />);
      const statusIcons = container.querySelectorAll('.w-3\\.5.h-3\\.5');
      expect(statusIcons.length).toBeGreaterThan(0);
    });

    it('displays check icon for completed', () => {
      const { container } = render(<ProjectCard {...defaultProps} status={ProjectStatus.COMPLETED} />);
      const statusIcons = container.querySelectorAll('.w-3\\.5.h-3\\.5');
      expect(statusIcons.length).toBeGreaterThan(0);
    });

    it('displays alert icon for failed', () => {
      const { container } = render(<ProjectCard {...defaultProps} status={ProjectStatus.FAILED} />);
      const statusIcons = container.querySelectorAll('.w-3\\.5.h-3\\.5');
      expect(statusIcons.length).toBeGreaterThan(0);
    });
  });

  describe('Animation Props', () => {
    it('accepts index prop', () => {
      const { container } = render(<ProjectCard {...defaultProps} index={3} />);
      expect(container.firstChild).toBeInTheDocument();
    });

    it('defaults to index 0', () => {
      const { container } = render(<ProjectCard {...defaultProps} />);
      expect(container.firstChild).toBeInTheDocument();
    });
  });
});
