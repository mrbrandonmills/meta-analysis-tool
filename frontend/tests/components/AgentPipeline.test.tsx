import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import AgentPipeline, { AgentState, AgentStep } from '@/components/workflow/AgentPipeline';
import { Search, Filter } from 'lucide-react';

describe('AgentPipeline Component', () => {
  const mockSteps: AgentStep[] = [
    {
      id: 'step-1',
      name: 'Search Agent',
      description: 'Searching databases',
      icon: Search,
      state: AgentState.COMPLETED,
      message: 'Found 100 papers',
    },
    {
      id: 'step-2',
      name: 'Screening Agent',
      description: 'Screening papers',
      icon: Filter,
      state: AgentState.RUNNING,
      progress: 50,
      eta: 120,
      message: 'Processing papers',
    },
    {
      id: 'step-3',
      name: 'Analysis Agent',
      description: 'Analyzing results',
      icon: Search,
      state: AgentState.PENDING,
    },
  ];

  describe('Rendering', () => {
    it('renders all steps', () => {
      render(<AgentPipeline steps={mockSteps} />);
      expect(screen.getByText('Search Agent')).toBeInTheDocument();
      expect(screen.getByText('Screening Agent')).toBeInTheDocument();
      expect(screen.getByText('Analysis Agent')).toBeInTheDocument();
    });

    it('renders step descriptions', () => {
      render(<AgentPipeline steps={mockSteps} />);
      expect(screen.getByText('Searching databases')).toBeInTheDocument();
      expect(screen.getByText('Screening papers')).toBeInTheDocument();
      expect(screen.getByText('Analyzing results')).toBeInTheDocument();
    });

    it('handles empty steps array', () => {
      const { container } = render(<AgentPipeline steps={[]} />);
      expect(container.querySelector('.space-y-4')).toBeInTheDocument();
    });
  });

  describe('Agent States', () => {
    it('displays pending state', () => {
      const pendingSteps: AgentStep[] = [{
        id: '1',
        name: 'Test',
        description: 'Test desc',
        icon: Search,
        state: AgentState.PENDING,
      }];
      render(<AgentPipeline steps={pendingSteps} />);
      expect(screen.getByText('Pending')).toBeInTheDocument();
    });

    it('displays running state', () => {
      const runningSteps: AgentStep[] = [{
        id: '1',
        name: 'Test',
        description: 'Test desc',
        icon: Search,
        state: AgentState.RUNNING,
      }];
      render(<AgentPipeline steps={runningSteps} />);
      expect(screen.getByText('Running')).toBeInTheDocument();
    });

    it('displays completed state', () => {
      const completedSteps: AgentStep[] = [{
        id: '1',
        name: 'Test',
        description: 'Test desc',
        icon: Search,
        state: AgentState.COMPLETED,
      }];
      render(<AgentPipeline steps={completedSteps} />);
      expect(screen.getByText('Completed')).toBeInTheDocument();
    });

    it('displays error state', () => {
      const errorSteps: AgentStep[] = [{
        id: '1',
        name: 'Test',
        description: 'Test desc',
        icon: Search,
        state: AgentState.ERROR,
        message: 'Something went wrong',
      }];
      render(<AgentPipeline steps={errorSteps} />);
      expect(screen.getByText('Error')).toBeInTheDocument();
    });
  });

  describe('Progress Display', () => {
    it('displays progress bar for running steps', () => {
      const runningSteps: AgentStep[] = [{
        id: '1',
        name: 'Test',
        description: 'Test desc',
        icon: Search,
        state: AgentState.RUNNING,
        progress: 75,
      }];
      render(<AgentPipeline steps={runningSteps} />);
      expect(screen.getByText('75%')).toBeInTheDocument();
    });

    it('does not display progress for pending steps', () => {
      const pendingSteps: AgentStep[] = [{
        id: '1',
        name: 'Test',
        description: 'Test desc',
        icon: Search,
        state: AgentState.PENDING,
      }];
      render(<AgentPipeline steps={pendingSteps} />);
      expect(screen.queryByText('%')).not.toBeInTheDocument();
    });

    it('does not display progress for completed steps', () => {
      const completedSteps: AgentStep[] = [{
        id: '1',
        name: 'Test',
        description: 'Test desc',
        icon: Search,
        state: AgentState.COMPLETED,
        message: 'Done',
      }];
      render(<AgentPipeline steps={completedSteps} />);
      expect(screen.queryByText('%')).not.toBeInTheDocument();
    });

    it('displays progress message', () => {
      const runningSteps: AgentStep[] = [{
        id: '1',
        name: 'Test',
        description: 'Test desc',
        icon: Search,
        state: AgentState.RUNNING,
        progress: 50,
        message: 'Processing files',
      }];
      render(<AgentPipeline steps={runningSteps} />);
      expect(screen.getByText('Processing files')).toBeInTheDocument();
    });

    it('displays default message when no message provided', () => {
      const runningSteps: AgentStep[] = [{
        id: '1',
        name: 'Test',
        description: 'Test desc',
        icon: Search,
        state: AgentState.RUNNING,
        progress: 50,
      }];
      render(<AgentPipeline steps={runningSteps} />);
      expect(screen.getByText('Processing...')).toBeInTheDocument();
    });
  });

  describe('ETA Display', () => {
    it('displays ETA for running steps', () => {
      const runningSteps: AgentStep[] = [{
        id: '1',
        name: 'Test',
        description: 'Test desc',
        icon: Search,
        state: AgentState.RUNNING,
        progress: 50,
        eta: 180,
      }];
      render(<AgentPipeline steps={runningSteps} />);
      expect(screen.getByText(/Estimated time: 3 min/)).toBeInTheDocument();
    });

    it('rounds up ETA to minutes', () => {
      const runningSteps: AgentStep[] = [{
        id: '1',
        name: 'Test',
        description: 'Test desc',
        icon: Search,
        state: AgentState.RUNNING,
        progress: 50,
        eta: 65, // Should display as 2 min
      }];
      render(<AgentPipeline steps={runningSteps} />);
      expect(screen.getByText(/Estimated time: 2 min/)).toBeInTheDocument();
    });

    it('does not display ETA when not provided', () => {
      const runningSteps: AgentStep[] = [{
        id: '1',
        name: 'Test',
        description: 'Test desc',
        icon: Search,
        state: AgentState.RUNNING,
        progress: 50,
      }];
      render(<AgentPipeline steps={runningSteps} />);
      expect(screen.queryByText(/Estimated time/)).not.toBeInTheDocument();
    });

    it('does not display ETA when 0', () => {
      const runningSteps: AgentStep[] = [{
        id: '1',
        name: 'Test',
        description: 'Test desc',
        icon: Search,
        state: AgentState.RUNNING,
        progress: 50,
        eta: 0,
      }];
      render(<AgentPipeline steps={runningSteps} />);
      expect(screen.queryByText(/Estimated time/)).not.toBeInTheDocument();
    });
  });

  describe('Messages', () => {
    it('displays completion message', () => {
      const completedSteps: AgentStep[] = [{
        id: '1',
        name: 'Test',
        description: 'Test desc',
        icon: Search,
        state: AgentState.COMPLETED,
        message: 'Successfully processed 100 items',
      }];
      render(<AgentPipeline steps={completedSteps} />);
      expect(screen.getByText('Successfully processed 100 items')).toBeInTheDocument();
    });

    it('displays error message', () => {
      const errorSteps: AgentStep[] = [{
        id: '1',
        name: 'Test',
        description: 'Test desc',
        icon: Search,
        state: AgentState.ERROR,
        message: 'Failed to connect to database',
      }];
      render(<AgentPipeline steps={errorSteps} />);
      expect(screen.getByText('Failed to connect to database')).toBeInTheDocument();
    });

    it('does not display message for pending steps', () => {
      const pendingSteps: AgentStep[] = [{
        id: '1',
        name: 'Test',
        description: 'Test desc',
        icon: Search,
        state: AgentState.PENDING,
        message: 'This should not appear',
      }];
      render(<AgentPipeline steps={pendingSteps} />);
      expect(screen.queryByText('This should not appear')).not.toBeInTheDocument();
    });
  });

  describe('Current Step Highlighting', () => {
    it('accepts currentStep prop', () => {
      render(<AgentPipeline steps={mockSteps} currentStep={1} />);
      expect(screen.getByText('Screening Agent')).toBeInTheDocument();
    });

    it('defaults to currentStep 0', () => {
      render(<AgentPipeline steps={mockSteps} />);
      expect(screen.getByText('Search Agent')).toBeInTheDocument();
    });
  });

  describe('Multiple Steps Workflow', () => {
    it('renders complex multi-step workflow', () => {
      const complexSteps: AgentStep[] = [
        {
          id: '1',
          name: 'Step 1',
          description: 'First step',
          icon: Search,
          state: AgentState.COMPLETED,
          message: 'Done',
        },
        {
          id: '2',
          name: 'Step 2',
          description: 'Second step',
          icon: Filter,
          state: AgentState.COMPLETED,
          message: 'Done',
        },
        {
          id: '3',
          name: 'Step 3',
          description: 'Third step',
          icon: Search,
          state: AgentState.RUNNING,
          progress: 60,
        },
        {
          id: '4',
          name: 'Step 4',
          description: 'Fourth step',
          icon: Filter,
          state: AgentState.PENDING,
        },
        {
          id: '5',
          name: 'Step 5',
          description: 'Fifth step',
          icon: Search,
          state: AgentState.PENDING,
        },
      ];

      render(<AgentPipeline steps={complexSteps} />);

      expect(screen.getByText('Step 1')).toBeInTheDocument();
      expect(screen.getByText('Step 2')).toBeInTheDocument();
      expect(screen.getByText('Step 3')).toBeInTheDocument();
      expect(screen.getByText('Step 4')).toBeInTheDocument();
      expect(screen.getByText('Step 5')).toBeInTheDocument();
    });
  });

  describe('Visual Elements', () => {
    it('renders step icons', () => {
      const { container } = render(<AgentPipeline steps={mockSteps} />);
      const icons = container.querySelectorAll('svg');
      // Should have icons for each step plus state icons
      expect(icons.length).toBeGreaterThan(0);
    });

    it('has proper card styling', () => {
      const { container } = render(<AgentPipeline steps={mockSteps} />);
      const cards = container.querySelectorAll('.rounded-2xl');
      expect(cards.length).toBe(mockSteps.length);
    });
  });

  describe('State Colors', () => {
    it('uses blue color for running state', () => {
      const runningSteps: AgentStep[] = [{
        id: '1',
        name: 'Test',
        description: 'Test desc',
        icon: Search,
        state: AgentState.RUNNING,
      }];
      const { container } = render(<AgentPipeline steps={runningSteps} />);
      const runningBadge = container.querySelector('.bg-blue-100');
      expect(runningBadge).toBeInTheDocument();
    });

    it('uses green color for completed state', () => {
      const completedSteps: AgentStep[] = [{
        id: '1',
        name: 'Test',
        description: 'Test desc',
        icon: Search,
        state: AgentState.COMPLETED,
      }];
      const { container } = render(<AgentPipeline steps={completedSteps} />);
      const completedBadge = container.querySelector('.bg-green-100');
      expect(completedBadge).toBeInTheDocument();
    });

    it('uses red color for error state', () => {
      const errorSteps: AgentStep[] = [{
        id: '1',
        name: 'Test',
        description: 'Test desc',
        icon: Search,
        state: AgentState.ERROR,
      }];
      const { container } = render(<AgentPipeline steps={errorSteps} />);
      const errorBadge = container.querySelector('.bg-red-100');
      expect(errorBadge).toBeInTheDocument();
    });

    it('uses gray color for pending state', () => {
      const pendingSteps: AgentStep[] = [{
        id: '1',
        name: 'Test',
        description: 'Test desc',
        icon: Search,
        state: AgentState.PENDING,
      }];
      const { container } = render(<AgentPipeline steps={pendingSteps} />);
      const pendingBadge = container.querySelector('.bg-gray-100');
      expect(pendingBadge).toBeInTheDocument();
    });
  });
});
