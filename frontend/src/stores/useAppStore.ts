// Global Application Store
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { User, Project, NotificationMessage } from '@/lib/types';

interface AppState {
  // User & Auth
  user: User | null;
  isAuthenticated: boolean;

  // Projects
  projects: Project[];
  currentProject: Project | null;

  // UI State
  sidebarOpen: boolean;
  darkMode: boolean;
  notifications: NotificationMessage[];

  // Loading & Errors
  loading: boolean;
  error: string | null;

  // Actions
  setUser: (user: User | null) => void;
  logout: () => void;

  setProjects: (projects: Project[]) => void;
  addProject: (project: Project) => void;
  updateProject: (projectId: string, updates: Partial<Project>) => void;
  deleteProject: (projectId: string) => void;
  setCurrentProject: (project: Project | null) => void;

  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  toggleDarkMode: () => void;

  addNotification: (notification: Omit<NotificationMessage, 'id' | 'timestamp' | 'read'>) => void;
  markNotificationRead: (id: string) => void;
  clearNotifications: () => void;

  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial State
        user: null,
        isAuthenticated: false,
        projects: [],
        currentProject: null,
        sidebarOpen: true,
        darkMode: false,
        notifications: [],
        loading: false,
        error: null,

        // User Actions
        setUser: (user) => set({
          user,
          isAuthenticated: !!user
        }),

        logout: () => set({
          user: null,
          isAuthenticated: false,
          projects: [],
          currentProject: null
        }),

        // Project Actions
        setProjects: (projects) => set({ projects }),

        addProject: (project) => set((state) => ({
          projects: [project, ...state.projects]
        })),

        updateProject: (projectId, updates) => set((state) => ({
          projects: state.projects.map(p =>
            p.id === projectId ? { ...p, ...updates } : p
          ),
          currentProject: state.currentProject?.id === projectId
            ? { ...state.currentProject, ...updates }
            : state.currentProject
        })),

        deleteProject: (projectId) => set((state) => ({
          projects: state.projects.filter(p => p.id !== projectId),
          currentProject: state.currentProject?.id === projectId
            ? null
            : state.currentProject
        })),

        setCurrentProject: (project) => set({ currentProject: project }),

        // UI Actions
        toggleSidebar: () => set((state) => ({
          sidebarOpen: !state.sidebarOpen
        })),

        setSidebarOpen: (open) => set({ sidebarOpen: open }),

        toggleDarkMode: () => set((state) => ({
          darkMode: !state.darkMode
        })),

        // Notification Actions
        addNotification: (notification) => set((state) => ({
          notifications: [
            {
              ...notification,
              id: Math.random().toString(36).substr(2, 9),
              timestamp: new Date(),
              read: false
            },
            ...state.notifications
          ]
        })),

        markNotificationRead: (id) => set((state) => ({
          notifications: state.notifications.map(n =>
            n.id === id ? { ...n, read: true } : n
          )
        })),

        clearNotifications: () => set({ notifications: [] }),

        // Loading & Error Actions
        setLoading: (loading) => set({ loading }),
        setError: (error) => set({ error })
      }),
      {
        name: 'app-storage',
        partialize: (state) => ({
          user: state.user,
          isAuthenticated: state.isAuthenticated,
          darkMode: state.darkMode,
          sidebarOpen: state.sidebarOpen
        })
      }
    ),
    { name: 'AppStore' }
  )
);
