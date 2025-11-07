'use client'

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useRouter } from 'next/router'
import {
  Bell,
  X,
  CheckCheck,
  Trash2,
  Info,
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
  ExternalLink,
  Filter,
} from 'lucide-react'
import { NotificationMessage } from '@/lib/types'
import { formatRelativeTime } from '@/lib/utils'

interface NotificationCenterProps {
  notifications: NotificationMessage[]
  onMarkAsRead?: (notificationId: string) => void
  onMarkAllAsRead?: () => void
  onDelete?: (notificationId: string) => void
  onClear?: () => void
  showAsDropdown?: boolean
}

const NotificationCenter: React.FC<NotificationCenterProps> = ({
  notifications,
  onMarkAsRead,
  onMarkAllAsRead,
  onDelete,
  onClear,
  showAsDropdown = false,
}) => {
  const router = useRouter()
  const [filter, setFilter] = useState<'all' | 'unread'>('all')
  const [isOpen, setIsOpen] = useState(false)

  const unreadCount = notifications.filter((n) => !n.read).length

  const filteredNotifications =
    filter === 'unread' ? notifications.filter((n) => !n.read) : notifications

  const getNotificationIcon = (type: NotificationMessage['type']) => {
    switch (type) {
      case 'success':
        return CheckCircle2
      case 'warning':
        return AlertTriangle
      case 'error':
        return AlertCircle
      case 'info':
      default:
        return Info
    }
  }

  const getNotificationColor = (type: NotificationMessage['type']) => {
    switch (type) {
      case 'success':
        return 'text-green-600 bg-green-100'
      case 'warning':
        return 'text-yellow-600 bg-yellow-100'
      case 'error':
        return 'text-red-600 bg-red-100'
      case 'info':
      default:
        return 'text-blue-600 bg-blue-100'
    }
  }

  const handleNotificationClick = (notification: NotificationMessage) => {
    if (!notification.read && onMarkAsRead) {
      onMarkAsRead(notification.id)
    }
    if (notification.actionUrl) {
      router.push(notification.actionUrl)
      if (showAsDropdown) {
        setIsOpen(false)
      }
    }
  }

  // Dropdown version (for header bell icon)
  if (showAsDropdown) {
    return (
      <div className="relative">
        <motion.button
          onClick={() => setIsOpen(!isOpen)}
          className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-xl transition-all"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Bell className="w-6 h-6" />
          {unreadCount > 0 && (
            <motion.span
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center"
            >
              {unreadCount > 9 ? '9+' : unreadCount}
            </motion.span>
          )}
        </motion.button>

        <AnimatePresence>
          {isOpen && (
            <>
              {/* Backdrop */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={() => setIsOpen(false)}
                className="fixed inset-0 z-40"
              />

              {/* Dropdown */}
              <motion.div
                initial={{ opacity: 0, y: -10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -10, scale: 0.95 }}
                transition={{ duration: 0.2 }}
                className="absolute right-0 top-full mt-2 w-96 max-h-[600px] bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden z-50"
              >
                {/* Header */}
                <div className="p-4 border-b border-gray-200 bg-gray-50">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-lg font-semibold text-gray-900">Notifications</h3>
                    <button
                      onClick={() => setIsOpen(false)}
                      className="p-1 text-gray-400 hover:text-gray-600 rounded-lg transition-colors"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setFilter('all')}
                      className={`
                        flex-1 px-3 py-1.5 rounded-lg text-sm font-medium transition-all
                        ${
                          filter === 'all'
                            ? 'bg-primary-600 text-white'
                            : 'bg-white text-gray-600 hover:bg-gray-100'
                        }
                      `}
                    >
                      All
                    </button>
                    <button
                      onClick={() => setFilter('unread')}
                      className={`
                        flex-1 px-3 py-1.5 rounded-lg text-sm font-medium transition-all
                        ${
                          filter === 'unread'
                            ? 'bg-primary-600 text-white'
                            : 'bg-white text-gray-600 hover:bg-gray-100'
                        }
                      `}
                    >
                      Unread ({unreadCount})
                    </button>
                  </div>
                </div>

                {/* Notifications List */}
                <div className="max-h-[400px] overflow-y-auto">
                  {filteredNotifications.length === 0 ? (
                    <div className="p-8 text-center">
                      <Bell className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                      <p className="text-sm text-gray-500">
                        {filter === 'unread' ? 'No unread notifications' : 'No notifications yet'}
                      </p>
                    </div>
                  ) : (
                    filteredNotifications.map((notification, index) => {
                      const Icon = getNotificationIcon(notification.type)
                      const colorClass = getNotificationColor(notification.type)

                      return (
                        <motion.div
                          key={notification.id}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.05 }}
                          onClick={() => handleNotificationClick(notification)}
                          className={`
                            relative p-4 border-b border-gray-100 hover:bg-gray-50 transition-colors cursor-pointer
                            ${!notification.read ? 'bg-blue-50/30' : ''}
                          `}
                        >
                          <div className="flex gap-3">
                            <div className={`flex-shrink-0 w-10 h-10 rounded-xl ${colorClass} flex items-center justify-center`}>
                              <Icon className="w-5 h-5" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-start justify-between gap-2 mb-1">
                                <h4 className="text-sm font-semibold text-gray-900">
                                  {notification.title}
                                </h4>
                                {!notification.read && (
                                  <div className="flex-shrink-0 w-2 h-2 bg-blue-500 rounded-full" />
                                )}
                              </div>
                              <p className="text-sm text-gray-600 line-clamp-2 mb-2">
                                {notification.message}
                              </p>
                              <div className="flex items-center justify-between">
                                <span className="text-xs text-gray-500">
                                  {formatRelativeTime(notification.timestamp)}
                                </span>
                                {notification.actionUrl && (
                                  <ExternalLink className="w-3 h-3 text-gray-400" />
                                )}
                              </div>
                            </div>
                          </div>
                        </motion.div>
                      )
                    })
                  )}
                </div>

                {/* Footer */}
                {filteredNotifications.length > 0 && (
                  <div className="p-3 border-t border-gray-200 bg-gray-50 flex gap-2">
                    {onMarkAllAsRead && unreadCount > 0 && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          onMarkAllAsRead()
                        }}
                        className="flex-1 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors flex items-center justify-center gap-2"
                      >
                        <CheckCheck className="w-4 h-4" />
                        Mark all read
                      </button>
                    )}
                    {onClear && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          onClear()
                        }}
                        className="flex-1 px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-lg transition-colors flex items-center justify-center gap-2"
                      >
                        <Trash2 className="w-4 h-4" />
                        Clear all
                      </button>
                    )}
                  </div>
                )}
              </motion.div>
            </>
          )}
        </AnimatePresence>
      </div>
    )
  }

  // Full page version (for dedicated notifications page)
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Notifications</h2>
          <p className="text-gray-600 mt-1">
            {unreadCount > 0 ? `You have ${unreadCount} unread notification${unreadCount !== 1 ? 's' : ''}` : 'All caught up!'}
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Filter Buttons */}
          <div className="flex items-center gap-2 p-1 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-xl">
            <button
              onClick={() => setFilter('all')}
              className={`
                px-4 py-2 rounded-lg text-sm font-medium transition-all
                ${
                  filter === 'all'
                    ? 'bg-primary-600 text-white shadow-sm'
                    : 'text-gray-600 hover:bg-gray-50'
                }
              `}
            >
              All
            </button>
            <button
              onClick={() => setFilter('unread')}
              className={`
                px-4 py-2 rounded-lg text-sm font-medium transition-all
                ${
                  filter === 'unread'
                    ? 'bg-primary-600 text-white shadow-sm'
                    : 'text-gray-600 hover:bg-gray-50'
                }
              `}
            >
              Unread ({unreadCount})
            </button>
          </div>

          {/* Action Buttons */}
          {onMarkAllAsRead && unreadCount > 0 && (
            <motion.button
              onClick={onMarkAllAsRead}
              className="px-4 py-2 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-xl text-gray-700 font-medium hover:bg-white transition-all"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <CheckCheck className="w-5 h-5" />
            </motion.button>
          )}

          {onClear && (
            <motion.button
              onClick={onClear}
              className="px-4 py-2 bg-red-50 text-red-600 rounded-xl font-medium hover:bg-red-100 transition-all"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Trash2 className="w-5 h-5" />
            </motion.button>
          )}
        </div>
      </div>

      {/* Notifications List */}
      {filteredNotifications.length === 0 ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-12 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-2xl text-center"
        >
          <Bell className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2" data-testid="empty-state-title">
            {filter === 'unread' ? 'All caught up!' : 'No notifications yet'}
          </h3>
          <p className="text-gray-600">
            {filter === 'unread'
              ? 'You have no unread notifications'
              : 'Notifications will appear here when you have new activity'}
          </p>
        </motion.div>
      ) : (
        <div className="space-y-3">
          {filteredNotifications.map((notification, index) => {
            const Icon = getNotificationIcon(notification.type)
            const colorClass = getNotificationColor(notification.type)

            return (
              <motion.div
                key={notification.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className={`
                  relative p-6 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-2xl
                  hover:shadow-md transition-all cursor-pointer group
                  ${!notification.read ? 'border-l-4 border-l-blue-500' : ''}
                `}
                onClick={() => handleNotificationClick(notification)}
              >
                <div className="flex gap-4">
                  <div className={`flex-shrink-0 w-12 h-12 rounded-xl ${colorClass} flex items-center justify-center`}>
                    <Icon className="w-6 h-6" />
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-4 mb-2">
                      <div>
                        <h4 className="text-base font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
                          {notification.title}
                        </h4>
                        <p className="text-sm text-gray-600 mt-1">{notification.message}</p>
                      </div>
                      {!notification.read && (
                        <div className="flex-shrink-0 w-3 h-3 bg-blue-500 rounded-full" />
                      )}
                    </div>

                    <div className="flex items-center justify-between mt-3">
                      <span className="text-sm text-gray-500">
                        {formatRelativeTime(notification.timestamp)}
                      </span>

                      <div className="flex items-center gap-2">
                        {notification.actionUrl && (
                          <span className="text-xs text-primary-600 font-medium flex items-center gap-1">
                            View details
                            <ExternalLink className="w-3 h-3" />
                          </span>
                        )}
                        {onDelete && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              onDelete(notification.id)
                            }}
                            className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>
      )}
    </div>
  )
}

export default NotificationCenter
