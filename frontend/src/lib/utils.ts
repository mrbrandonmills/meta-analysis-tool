import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { CredibilityLevel, AgentStatus, ProjectStatus } from './types';

/**
 * Utility to merge Tailwind CSS classes
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Get color classes for credibility levels
 */
export function getCredibilityColor(level: CredibilityLevel): string {
  switch (level) {
    case CredibilityLevel.HIGH:
      return 'bg-green-50 border-green-300 text-green-900';
    case CredibilityLevel.MEDIUM:
      return 'bg-yellow-50 border-yellow-300 text-yellow-900';
    case CredibilityLevel.LOW:
      return 'bg-orange-50 border-orange-300 text-orange-900';
    case CredibilityLevel.VERY_LOW:
      return 'bg-red-50 border-red-300 text-red-900';
    default:
      return 'bg-gray-50 border-gray-300 text-gray-900';
  }
}

/**
 * Get badge color for credibility level
 */
export function getCredibilityBadgeColor(level: CredibilityLevel): string {
  switch (level) {
    case CredibilityLevel.HIGH:
      return 'bg-green-100 text-green-800 border-green-300';
    case CredibilityLevel.MEDIUM:
      return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    case CredibilityLevel.LOW:
      return 'bg-orange-100 text-orange-800 border-orange-300';
    case CredibilityLevel.VERY_LOW:
      return 'bg-red-100 text-red-800 border-red-300';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-300';
  }
}

/**
 * Get icon for credibility level
 */
export function getCredibilityIcon(level: CredibilityLevel): string {
  switch (level) {
    case CredibilityLevel.HIGH:
      return '🟢';
    case CredibilityLevel.MEDIUM:
      return '🟡';
    case CredibilityLevel.LOW:
      return '🟠';
    case CredibilityLevel.VERY_LOW:
      return '🔴';
    default:
      return '⚪';
  }
}

/**
 * Get color for agent status
 */
export function getAgentStatusColor(status: AgentStatus): string {
  switch (status) {
    case AgentStatus.IDLE:
      return 'text-gray-500 bg-gray-100';
    case AgentStatus.THINKING:
      return 'text-blue-500 bg-blue-100 animate-pulse';
    case AgentStatus.PROCESSING:
      return 'text-purple-500 bg-purple-100';
    case AgentStatus.COMPLETE:
      return 'text-green-500 bg-green-100';
    case AgentStatus.ERROR:
      return 'text-red-500 bg-red-100';
    default:
      return 'text-gray-500 bg-gray-100';
  }
}

/**
 * Get color for project status
 */
export function getProjectStatusColor(status: ProjectStatus): string {
  switch (status) {
    case ProjectStatus.DRAFT:
      return 'bg-gray-100 text-gray-800';
    case ProjectStatus.IN_PROGRESS:
      return 'bg-blue-100 text-blue-800 animate-pulse';
    case ProjectStatus.PAUSED:
      return 'bg-yellow-100 text-yellow-800';
    case ProjectStatus.COMPLETED:
      return 'bg-green-100 text-green-800';
    case ProjectStatus.FAILED:
      return 'bg-red-100 text-red-800';
    case ProjectStatus.CANCELLED:
      return 'bg-gray-100 text-gray-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
}

/**
 * Format date to readable string
 */
export function formatDate(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Format date to relative time
 */
export function formatRelativeTime(date: Date | string): string {
  const now = new Date();
  const then = typeof date === 'string' ? new Date(date) : date;
  const diffInSeconds = Math.floor((now.getTime() - then.getTime()) / 1000);

  if (diffInSeconds < 60) return 'just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)}d ago`;
  if (diffInSeconds < 31536000) return `${Math.floor(diffInSeconds / 2592000)}mo ago`;
  return `${Math.floor(diffInSeconds / 31536000)}y ago`;
}

/**
 * Format duration in seconds to human readable
 */
export function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  return `${hours}h ${minutes}m`;
}

/**
 * Format number with commas
 */
export function formatNumber(num: number): string {
  return num.toLocaleString('en-US');
}

/**
 * Calculate percentage
 */
export function calculatePercentage(value: number, total: number): number {
  if (total === 0) return 0;
  return Math.round((value / total) * 100);
}

/**
 * Truncate text
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

/**
 * Estimate time remaining
 */
export function estimateTimeRemaining(
  completed: number,
  total: number,
  elapsedSeconds: number
): number {
  if (completed === 0) return 0;
  const rate = completed / elapsedSeconds;
  const remaining = total - completed;
  return Math.ceil(remaining / rate);
}

/**
 * Get initials from name
 */
export function getInitials(name: string): string {
  return name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .substring(0, 2);
}

/**
 * Validate email
 */
export function isValidEmail(email: string): boolean {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

/**
 * Generate random color
 */
export function generateColor(seed: string): string {
  let hash = 0;
  for (let i = 0; i < seed.length; i++) {
    hash = seed.charCodeAt(i) + ((hash << 5) - hash);
  }
  const color = Math.floor(Math.abs((Math.sin(hash) * 16777215) % 1) * 16777215).toString(16);
  return '#' + '0'.repeat(6 - color.length) + color;
}

/**
 * Deep clone object
 */
export function deepClone<T>(obj: T): T {
  return JSON.parse(JSON.stringify(obj));
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Download file from blob
 */
export function downloadBlob(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

/**
 * Copy to clipboard
 */
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    console.error('Failed to copy:', err);
    return false;
  }
}
