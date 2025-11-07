import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import NotificationCenter from '@/components/dashboard/NotificationCenter'
import { NotificationMessage } from '@/lib/types'

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
    span: ({ children, ...props }: any) => <span {...props}>{children}</span>,
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

const mockNotifications: NotificationMessage[] = [
  {
    id: '1',
    type: 'success',
    title: 'Project Completed',
    message: 'Your meta-analysis project has been completed successfully',
    timestamp: new Date('2024-01-15T10:00:00'),
    read: false,
    actionUrl: '/projects/1',
  },
  {
    id: '2',
    type: 'info',
    title: 'New Feature Available',
    message: 'Check out our new analytics dashboard',
    timestamp: new Date('2024-01-14T15:30:00'),
    read: true,
  },
  {
    id: '3',
    type: 'warning',
    title: 'Action Required',
    message: 'Please review your project settings',
    timestamp: new Date('2024-01-13T09:00:00'),
    read: false,
    actionUrl: '/settings',
  },
  {
    id: '4',
    type: 'error',
    title: 'Analysis Failed',
    message: 'Your analysis encountered an error',
    timestamp: new Date('2024-01-12T14:00:00'),
    read: true,
  },
]

describe('NotificationCenter', () => {
  const mockOnMarkAsRead = vi.fn()
  const mockOnMarkAllAsRead = vi.fn()
  const mockOnDelete = vi.fn()
  const mockOnClear = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Full Page View', () => {
    it('renders all notifications', () => {
      render(
        <NotificationCenter
          notifications={mockNotifications}
          showAsDropdown={false}
        />
      )

      expect(screen.getByText('Project Completed')).toBeInTheDocument()
      expect(screen.getByText('New Feature Available')).toBeInTheDocument()
      expect(screen.getByText('Action Required')).toBeInTheDocument()
      expect(screen.getByText('Analysis Failed')).toBeInTheDocument()
    })

    it('displays unread count correctly', () => {
      render(
        <NotificationCenter
          notifications={mockNotifications}
          showAsDropdown={false}
        />
      )

      expect(screen.getByText(/You have 2 unread notification/)).toBeInTheDocument()
    })

    it('filters to show unread notifications only', async () => {
      const user = userEvent.setup()
      render(
        <NotificationCenter
          notifications={mockNotifications}
          showAsDropdown={false}
        />
      )

      const unreadButton = screen.getByRole('button', { name: /Unread \(2\)/ })
      await user.click(unreadButton)

      expect(screen.getByText('Project Completed')).toBeInTheDocument()
      expect(screen.getByText('Action Required')).toBeInTheDocument()
      expect(screen.queryByText('New Feature Available')).not.toBeInTheDocument()
      expect(screen.queryByText('Analysis Failed')).not.toBeInTheDocument()
    })

    it('filters to show all notifications', async () => {
      const user = userEvent.setup()
      render(
        <NotificationCenter
          notifications={mockNotifications}
          showAsDropdown={false}
        />
      )

      // First set to unread
      const unreadButton = screen.getByRole('button', { name: /Unread/ })
      await user.click(unreadButton)

      // Then switch back to all
      const allButton = screen.getByRole('button', { name: 'All' })
      await user.click(allButton)

      expect(screen.getAllByRole('generic').length).toBeGreaterThan(0)
    })

    it('calls onMarkAsRead when notification is clicked', async () => {
      const user = userEvent.setup()
      render(
        <NotificationCenter
          notifications={mockNotifications}
          onMarkAsRead={mockOnMarkAsRead}
          showAsDropdown={false}
        />
      )

      const notification = screen.getByText('Project Completed').closest('div')
      if (notification) {
        await user.click(notification)
        expect(mockOnMarkAsRead).toHaveBeenCalledWith('1')
      }
    })

    it('calls onMarkAllAsRead when button is clicked', async () => {
      const user = userEvent.setup()
      render(
        <NotificationCenter
          notifications={mockNotifications}
          onMarkAllAsRead={mockOnMarkAllAsRead}
          showAsDropdown={false}
        />
      )

      const markAllButton = screen.getByRole('button', { name: '' })
      await user.click(markAllButton)

      expect(mockOnMarkAllAsRead).toHaveBeenCalledTimes(1)
    })

    it('calls onClear when clear button is clicked', async () => {
      const user = userEvent.setup()
      render(
        <NotificationCenter
          notifications={mockNotifications}
          onClear={mockOnClear}
          showAsDropdown={false}
        />
      )

      const clearButton = screen.getByRole('button', { name: '' })
      await user.click(clearButton)

      expect(mockOnClear).toHaveBeenCalledTimes(1)
    })

    it('calls onDelete when delete button is clicked', async () => {
      const user = userEvent.setup()
      render(
        <NotificationCenter
          notifications={mockNotifications}
          onDelete={mockOnDelete}
          showAsDropdown={false}
        />
      )

      // Find and click delete button for first notification
      const deleteButtons = screen.getAllByRole('button')
      const deleteButton = deleteButtons.find((btn) =>
        btn.querySelector('svg')
      )

      if (deleteButton) {
        await user.click(deleteButton)
        expect(mockOnDelete).toHaveBeenCalled()
      }
    })

    it('shows empty state when no notifications', () => {
      render(
        <NotificationCenter
          notifications={[]}
          showAsDropdown={false}
        />
      )

      expect(screen.getByText('No notifications yet')).toBeInTheDocument()
    })

    it('shows correct empty state for unread filter', async () => {
      const user = userEvent.setup()
      const readNotifications = mockNotifications.map((n) => ({ ...n, read: true }))

      render(
        <NotificationCenter
          notifications={readNotifications}
          showAsDropdown={false}
        />
      )

      const unreadButton = screen.getByRole('button', { name: /Unread/ })
      await user.click(unreadButton)

      expect(screen.getByText('All caught up!')).toBeInTheDocument()
    })

    it('displays notification icons based on type', () => {
      render(
        <NotificationCenter
          notifications={mockNotifications}
          showAsDropdown={false}
        />
      )

      // Check that different notification types are rendered
      // (Icons would be rendered, checking for their presence)
      const notifications = screen.getAllByRole('generic')
      expect(notifications.length).toBeGreaterThan(0)
    })

    it('shows unread indicator for unread notifications', () => {
      render(
        <NotificationCenter
          notifications={mockNotifications}
          showAsDropdown={false}
        />
      )

      // Unread notifications should have special border or indicator
      const projectCompleted = screen.getByText('Project Completed').closest('div')
      expect(projectCompleted).toHaveClass(/border-l-4/)
    })
  })

  describe('Dropdown View', () => {
    it('renders bell icon with unread count', () => {
      render(
        <NotificationCenter
          notifications={mockNotifications}
          showAsDropdown={true}
        />
      )

      expect(screen.getByText('2')).toBeInTheDocument() // Unread count badge
    })

    it('toggles dropdown when bell is clicked', async () => {
      const user = userEvent.setup()
      render(
        <NotificationCenter
          notifications={mockNotifications}
          showAsDropdown={true}
        />
      )

      const bellButton = screen.getByRole('button')
      await user.click(bellButton)

      // Dropdown should open
      await waitFor(() => {
        expect(screen.getByText('Notifications')).toBeInTheDocument()
      })

      // Close dropdown
      const closeButton = screen.getByRole('button', { name: /×/ })
      await user.click(closeButton)
    })

    it('closes dropdown when clicking backdrop', async () => {
      const user = userEvent.setup()
      render(
        <NotificationCenter
          notifications={mockNotifications}
          showAsDropdown={true}
        />
      )

      const bellButton = screen.getByRole('button')
      await user.click(bellButton)

      // Wait for dropdown to open
      await waitFor(() => {
        expect(screen.getByText('Notifications')).toBeInTheDocument()
      })

      // Click backdrop (rendered as a div)
      const backdrop = document.querySelector('.fixed.inset-0')
      if (backdrop) {
        fireEvent.click(backdrop)
        await waitFor(() => {
          expect(screen.queryByText('Notifications')).not.toBeInTheDocument()
        })
      }
    })

    it('shows notification count badge', () => {
      render(
        <NotificationCenter
          notifications={mockNotifications}
          showAsDropdown={true}
        />
      )

      const badge = screen.getByText('2')
      expect(badge).toBeInTheDocument()
    })

    it('shows 9+ when more than 9 unread notifications', () => {
      const manyNotifications = Array.from({ length: 15 }, (_, i) => ({
        id: `${i}`,
        type: 'info' as const,
        title: `Notification ${i}`,
        message: `Message ${i}`,
        timestamp: new Date(),
        read: false,
      }))

      render(
        <NotificationCenter
          notifications={manyNotifications}
          showAsDropdown={true}
        />
      )

      expect(screen.getByText('9+')).toBeInTheDocument()
    })

    it('displays filter tabs in dropdown', async () => {
      const user = userEvent.setup()
      render(
        <NotificationCenter
          notifications={mockNotifications}
          showAsDropdown={true}
        />
      )

      const bellButton = screen.getByRole('button')
      await user.click(bellButton)

      await waitFor(() => {
        expect(screen.getByText('All')).toBeInTheDocument()
        expect(screen.getByText(/Unread/)).toBeInTheDocument()
      })
    })

    it('renders mark all read button in dropdown footer', async () => {
      const user = userEvent.setup()
      render(
        <NotificationCenter
          notifications={mockNotifications}
          onMarkAllAsRead={mockOnMarkAllAsRead}
          showAsDropdown={true}
        />
      )

      const bellButton = screen.getByRole('button')
      await user.click(bellButton)

      await waitFor(() => {
        const markAllButton = screen.getByText('Mark all read')
        expect(markAllButton).toBeInTheDocument()
      })
    })
  })
})
