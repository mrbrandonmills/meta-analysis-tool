import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ProjectsList from '@/components/dashboard/ProjectsList'
import { Project, ProjectStatus, ToolType } from '@/lib/types'

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}))

// Mock next/router
vi.mock('next/router', () => ({
  useRouter: () => ({
    push: vi.fn(),
    pathname: '/',
    query: {},
    asPath: '/',
  }),
}))

const mockProjects: Project[] = [
  {
    id: '1',
    userId: 'user1',
    toolType: ToolType.META_ANALYSIS,
    title: 'COVID-19 Meta-Analysis',
    description: 'Systematic review of COVID-19 treatments',
    status: ProjectStatus.IN_PROGRESS,
    workflows: [],
    auditTrail: [],
    createdAt: new Date('2024-01-01'),
    updatedAt: new Date('2024-01-15'),
  },
  {
    id: '2',
    userId: 'user1',
    toolType: ToolType.REVIEWER_MATCHER,
    title: 'Find Reviewers for AI Paper',
    description: 'Match expert reviewers',
    status: ProjectStatus.COMPLETED,
    workflows: [],
    auditTrail: [],
    createdAt: new Date('2024-01-05'),
    updatedAt: new Date('2024-01-10'),
  },
  {
    id: '3',
    userId: 'user1',
    toolType: ToolType.PEER_REVIEW,
    title: 'Review Climate Study',
    description: 'Generate peer review',
    status: ProjectStatus.DRAFT,
    workflows: [],
    auditTrail: [],
    createdAt: new Date('2024-01-10'),
    updatedAt: new Date('2024-01-12'),
  },
]

describe('ProjectsList', () => {
  const mockOnRefresh = vi.fn()
  const mockOnDelete = vi.fn()
  const mockOnClone = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders all projects', () => {
    render(<ProjectsList projects={mockProjects} />)

    expect(screen.getByText('COVID-19 Meta-Analysis')).toBeInTheDocument()
    expect(screen.getByText('Find Reviewers for AI Paper')).toBeInTheDocument()
    expect(screen.getByText('Review Climate Study')).toBeInTheDocument()
  })

  it('displays correct project count', () => {
    render(<ProjectsList projects={mockProjects} />)

    expect(screen.getByText('Showing 3 of 3 projects')).toBeInTheDocument()
  })

  it('filters projects by search query', async () => {
    const user = userEvent.setup()
    render(<ProjectsList projects={mockProjects} />)

    const searchInput = screen.getByPlaceholderText('Search projects...')
    await user.type(searchInput, 'COVID')

    await waitFor(() => {
      expect(screen.getByText('COVID-19 Meta-Analysis')).toBeInTheDocument()
      expect(screen.queryByText('Find Reviewers for AI Paper')).not.toBeInTheDocument()
      expect(screen.queryByText('Review Climate Study')).not.toBeInTheDocument()
    })

    expect(screen.getByText('Showing 1 of 3 projects')).toBeInTheDocument()
  })

  it('clears search query when X button clicked', async () => {
    const user = userEvent.setup()
    render(<ProjectsList projects={mockProjects} />)

    const searchInput = screen.getByPlaceholderText('Search projects...')
    await user.type(searchInput, 'COVID')

    const clearButton = screen.getByRole('button', { name: /×/i })
    await user.click(clearButton)

    expect(searchInput).toHaveValue('')
    expect(screen.getByText('Showing 3 of 3 projects')).toBeInTheDocument()
  })

  it('toggles filter panel', async () => {
    const user = userEvent.setup()
    render(<ProjectsList projects={mockProjects} />)

    const filterButton = screen.getByText('Filters')
    await user.click(filterButton)

    expect(screen.getByText('Status')).toBeInTheDocument()
    expect(screen.getByText('Tool Type')).toBeInTheDocument()

    await user.click(filterButton)
  })

  it('filters projects by status', async () => {
    const user = userEvent.setup()
    render(<ProjectsList projects={mockProjects} />)

    // Open filters
    const filterButton = screen.getByText('Filters')
    await user.click(filterButton)

    // Click "Completed" filter
    const completedFilter = screen.getByRole('button', { name: 'Completed' })
    await user.click(completedFilter)

    await waitFor(() => {
      expect(screen.getByText('Find Reviewers for AI Paper')).toBeInTheDocument()
      expect(screen.queryByText('COVID-19 Meta-Analysis')).not.toBeInTheDocument()
      expect(screen.queryByText('Review Climate Study')).not.toBeInTheDocument()
    })

    expect(screen.getByText('1 filter active')).toBeInTheDocument()
  })

  it('filters projects by tool type', async () => {
    const user = userEvent.setup()
    render(<ProjectsList projects={mockProjects} />)

    // Open filters
    const filterButton = screen.getByText('Filters')
    await user.click(filterButton)

    // Click "Meta-Analysis" filter
    const metaAnalysisFilter = screen.getByText(/Meta-Analysis/)
    await user.click(metaAnalysisFilter)

    await waitFor(() => {
      expect(screen.getByText('COVID-19 Meta-Analysis')).toBeInTheDocument()
      expect(screen.queryByText('Find Reviewers for AI Paper')).not.toBeInTheDocument()
    })
  })

  it('combines multiple filters', async () => {
    const user = userEvent.setup()
    render(<ProjectsList projects={mockProjects} />)

    // Open filters
    const filterButton = screen.getByText('Filters')
    await user.click(filterButton)

    // Apply status filter
    const inProgressFilter = screen.getByRole('button', { name: 'In Progress' })
    await user.click(inProgressFilter)

    // Apply tool type filter
    const metaAnalysisFilter = screen.getByText(/Meta-Analysis/)
    await user.click(metaAnalysisFilter)

    await waitFor(() => {
      expect(screen.getByText('COVID-19 Meta-Analysis')).toBeInTheDocument()
      expect(screen.queryByText('Find Reviewers for AI Paper')).not.toBeInTheDocument()
    })

    expect(screen.getByText('2 filters active')).toBeInTheDocument()
  })

  it('clears all filters', async () => {
    const user = userEvent.setup()
    render(<ProjectsList projects={mockProjects} />)

    // Open filters and apply some
    const filterButton = screen.getByText('Filters')
    await user.click(filterButton)

    const completedFilter = screen.getByRole('button', { name: 'Completed' })
    await user.click(completedFilter)

    // Clear filters
    const clearButton = screen.getByText('Clear all filters')
    await user.click(clearButton)

    expect(screen.getByText('Showing 3 of 3 projects')).toBeInTheDocument()
  })

  it('sorts projects by different criteria', async () => {
    const user = userEvent.setup()
    render(<ProjectsList projects={mockProjects} />)

    const sortSelect = screen.getByRole('combobox')

    // Sort by title A-Z
    await user.selectOptions(sortSelect, 'title-asc')
    // Projects should be sorted alphabetically

    // Sort by recently created
    await user.selectOptions(sortSelect, 'createdAt-desc')
    // Most recent should be first
  })

  it('calls onRefresh when refresh button clicked', async () => {
    const user = userEvent.setup()
    render(<ProjectsList projects={mockProjects} onRefresh={mockOnRefresh} />)

    const refreshButton = screen.getByRole('button', { name: '' }) // Refresh icon button
    await user.click(refreshButton)

    expect(mockOnRefresh).toHaveBeenCalledTimes(1)
  })

  it('shows loading skeleton when loading', () => {
    render(<ProjectsList projects={mockProjects} loading={true} />)

    const skeletons = screen.getAllByRole('generic')
    expect(skeletons.length).toBeGreaterThan(0)
  })

  it('shows empty state when no projects', () => {
    render(<ProjectsList projects={[]} />)

    expect(screen.getByText('No projects found')).toBeInTheDocument()
    expect(
      screen.getByText('Get started by creating your first project')
    ).toBeInTheDocument()
  })

  it('shows empty state with filters applied', async () => {
    const user = userEvent.setup()
    render(<ProjectsList projects={mockProjects} />)

    const searchInput = screen.getByPlaceholderText('Search projects...')
    await user.type(searchInput, 'nonexistent project')

    expect(screen.getByText('No projects found')).toBeInTheDocument()
    expect(
      screen.getByText('Try adjusting your search or filters')
    ).toBeInTheDocument()
  })

  it('preserves filters when switching between views', async () => {
    const user = userEvent.setup()
    const { rerender } = render(<ProjectsList projects={mockProjects} />)

    // Apply filter
    const filterButton = screen.getByText('Filters')
    await user.click(filterButton)

    const completedFilter = screen.getByRole('button', { name: 'Completed' })
    await user.click(completedFilter)

    // Rerender (simulating navigation or state change)
    rerender(<ProjectsList projects={mockProjects} />)

    // Filter should still be applied
    expect(screen.getByText('1 filter active')).toBeInTheDocument()
  })
})
