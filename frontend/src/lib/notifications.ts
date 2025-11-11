/**
 * Notification System
 * Browser notifications, sound alerts, and vibration for task completion
 */

export interface NotificationOptions {
  title: string
  body: string
  icon?: string
  badge?: string
  tag?: string
  requireInteraction?: boolean
  silent?: boolean
  data?: any
}

/**
 * Request notification permission from the user
 */
export async function requestNotificationPermission(): Promise<boolean> {
  if (!('Notification' in window)) {
    console.warn('This browser does not support desktop notifications')
    return false
  }

  if (Notification.permission === 'granted') {
    return true
  }

  if (Notification.permission !== 'denied') {
    const permission = await Notification.requestPermission()
    return permission === 'granted'
  }

  return false
}

/**
 * Check if notifications are supported and permitted
 */
export function canShowNotifications(): boolean {
  return (
    'Notification' in window &&
    Notification.permission === 'granted'
  )
}

/**
 * Show a browser notification
 */
export async function showNotification(options: NotificationOptions): Promise<Notification | null> {
  // Check if we have permission
  const hasPermission = await requestNotificationPermission()
  if (!hasPermission) {
    console.warn('Notification permission not granted')
    return null
  }

  try {
    const notification = new Notification(options.title, {
      body: options.body,
      icon: options.icon || '/icon-192x192.png',
      badge: options.badge || '/icon-96x96.png',
      tag: options.tag || 'default',
      requireInteraction: options.requireInteraction || false,
      silent: options.silent || false,
      data: options.data,
    })

    // Auto-close after 10 seconds if not requiring interaction
    if (!options.requireInteraction) {
      setTimeout(() => {
        notification.close()
      }, 10000)
    }

    return notification
  } catch (error) {
    console.error('Failed to show notification:', error)
    return null
  }
}

/**
 * Play a notification sound
 */
export function playNotificationSound(soundType: 'success' | 'error' | 'info' = 'success'): void {
  try {
    // Create audio element
    const audio = new Audio()

    // Set sound based on type
    switch (soundType) {
      case 'success':
        // Success sound (pleasant chime)
        audio.src = 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTKI0fPTgjMHHmm98OilUhQNUKnk7bllHgU2j9b0z3kpBSl+zPLaizsKEmaw7emnUBQPRp/g8r1sIwU3jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7emnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7emnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7emnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7emnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7emnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7emnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7emnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7emnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7emnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7emnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7emnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7emnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7emnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7emnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7emnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7emnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7emnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7emnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7emnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7emnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7emnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7emnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7emnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7emnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7emnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7emnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7emnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7emnUBQP'
        break
      case 'error':
        // Error sound (gentle alert)
        audio.src = 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTKI0fPTgjMHHmm98OilUhQNUKnk7bllHgU2j9b0z3kpBSl+zPLaizsKEmaw7emnUBQPRp/g8r1sIwU3jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQP'
        break
      default:
        // Info sound (gentle beep)
        audio.src = 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTKI0fPTgjMHHmm98OilUhQNUKnk7bllHgU2j9b0z3kpBSl+zPLaizsKEmaw7emnUBQPRp/g8r1sIwU3jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQPRp/g8r1sIwU4jtbzzngrBSl+zPLajDsKEmaw7umnUBQP'
    }

    audio.volume = 0.5
    audio.play().catch(error => {
      console.warn('Failed to play notification sound:', error)
    })
  } catch (error) {
    console.error('Error playing notification sound:', error)
  }
}

/**
 * Vibrate the device (mobile only)
 */
export function vibrate(pattern: number | number[] = 200): void {
  if ('vibrate' in navigator) {
    try {
      navigator.vibrate(pattern)
    } catch (error) {
      console.warn('Failed to vibrate device:', error)
    }
  }
}

/**
 * Notify user of task completion with all available methods
 */
export async function notifyComplete(
  title: string,
  body?: string,
  options?: {
    playSound?: boolean
    vibrate?: boolean
    soundType?: 'success' | 'error' | 'info'
    vibrationPattern?: number | number[]
    onClick?: () => void
  }
): Promise<void> {
  const {
    playSound = true,
    vibrate: shouldVibrate = true,
    soundType = 'success',
    vibrationPattern = [200, 100, 200],
    onClick,
  } = options || {}

  // Show browser notification
  const notification = await showNotification({
    title,
    body: body || 'Your research analysis is complete!',
    icon: '/icon-192x192.png',
    requireInteraction: false,
  })

  // Add click handler
  if (notification && onClick) {
    notification.onclick = () => {
      onClick()
      notification.close()
      window.focus()
    }
  }

  // Play sound
  if (playSound) {
    playNotificationSound(soundType)
  }

  // Vibrate
  if (shouldVibrate) {
    vibrate(vibrationPattern)
  }
}

/**
 * Notify user of task error
 */
export async function notifyError(
  title: string,
  body?: string,
  onClick?: () => void
): Promise<void> {
  await notifyComplete(title, body || 'Your task encountered an error', {
    soundType: 'error',
    vibrationPattern: [100, 50, 100, 50, 100],
    onClick,
  })
}

/**
 * Notify user of task progress milestone
 */
export async function notifyProgress(
  title: string,
  body: string,
  onClick?: () => void
): Promise<void> {
  await notifyComplete(title, body, {
    soundType: 'info',
    vibrate: false, // Don't vibrate for progress updates
    playSound: false, // Don't play sound for progress updates
    onClick,
  })
}

/**
 * Initialize notification system
 * Should be called once when the app loads
 */
export async function initializeNotifications(): Promise<void> {
  // Request permission on first load
  if ('Notification' in window && Notification.permission === 'default') {
    await requestNotificationPermission()
  }
}

export default {
  requestNotificationPermission,
  canShowNotifications,
  showNotification,
  playNotificationSound,
  vibrate,
  notifyComplete,
  notifyError,
  notifyProgress,
  initializeNotifications,
}
