/**
 * Role-Based Access Control (RBAC) Utilities
 *
 * This module provides functions to check user permissions based on their role.
 * Used to protect routes and conditional UI rendering.
 */

import { User } from './types';

export type UserRole = 'researcher' | 'editor' | 'admin';

/**
 * Check if user can access admin dashboard
 */
export function canAccessAdmin(user: User | null): boolean {
  if (!user) return false;
  return user.role === 'admin';
}

/**
 * Check if user can access editor dashboard
 */
export function canAccessEditor(user: User | null): boolean {
  if (!user) return false;
  return user.role === 'editor' || user.role === 'admin';
}

/**
 * Check if user can approve peer reviews
 */
export function canApproveReviews(user: User | null): boolean {
  return canAccessEditor(user);
}

/**
 * Check if user can manage subscriptions
 */
export function canManageSubscriptions(user: User | null): boolean {
  if (!user) return false;
  return user.role === 'admin';
}

/**
 * Check if user can view earnings (paying members only)
 */
export function canViewEarnings(user: User | null): boolean {
  if (!user) return false;
  // All researchers can potentially view earnings if they're paying members
  return true; // Will check is_paying_member in the component
}

/**
 * Check if user can upload papers
 */
export function canUploadPapers(user: User | null): boolean {
  if (!user) return false;
  // Editors and paying researchers can upload papers
  return user.role === 'editor' || user.role === 'admin' || user.role === 'researcher';
}

/**
 * Get user role display name
 */
export function getRoleDisplayName(role: UserRole): string {
  const roleNames: Record<UserRole, string> = {
    researcher: 'Researcher',
    editor: 'Editor',
    admin: 'Administrator'
  };
  return roleNames[role];
}

/**
 * Get user role badge color
 */
export function getRoleBadgeColor(role: UserRole): string {
  const roleColors: Record<UserRole, string> = {
    researcher: 'bg-green-100 text-green-700',
    editor: 'bg-purple-100 text-purple-700',
    admin: 'bg-red-100 text-red-700'
  };
  return roleColors[role];
}
