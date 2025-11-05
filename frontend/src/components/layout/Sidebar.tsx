import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import {
  LayoutDashboard,
  FlaskConical,
  Folder,
  Settings,
  Menu,
  X,
  Microscope,
  Users,
  FileText,
  Lightbulb
} from 'lucide-react';
import { useAppStore } from '@/stores/useAppStore';
import { cn } from '@/lib/utils';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Projects', href: '/projects', icon: Folder },
  {
    name: 'Tools',
    icon: FlaskConical,
    children: [
      { name: 'Meta-Analysis', href: '/tools/meta-analysis', icon: Microscope },
      { name: 'Reviewer Matcher', href: '/tools/reviewer-matcher', icon: Users },
      { name: 'Peer Review', href: '/tools/peer-review', icon: FileText },
      { name: 'Research Direction', href: '/tools/research-direction', icon: Lightbulb }
    ]
  },
  { name: 'Settings', href: '/settings', icon: Settings }
];

export const Sidebar: React.FC = () => {
  const router = useRouter();
  const { sidebarOpen, setSidebarOpen } = useAppStore();

  const isActive = (href: string) => {
    return router.pathname === href || router.pathname.startsWith(href + '/');
  };

  return (
    <>
      {/* Mobile backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-gray-900 bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed top-0 left-0 z-50 h-screen bg-white border-r border-gray-200 transition-transform duration-300 ease-in-out',
          'lg:translate-x-0 lg:static lg:z-0',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full',
          'w-64'
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
          <Link href="/dashboard" className="flex items-center space-x-2">
            <FlaskConical className="w-8 h-8 text-blue-600" />
            <span className="text-xl font-bold text-gray-900">ResearchAI</span>
          </Link>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden text-gray-500 hover:text-gray-700"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4 px-3">
          <ul className="space-y-1">
            {navigation.map((item) => (
              <li key={item.name}>
                {item.children ? (
                  <div className="space-y-1">
                    <div className="flex items-center px-3 py-2 text-sm font-medium text-gray-700">
                      <item.icon className="w-5 h-5 mr-3" />
                      {item.name}
                    </div>
                    <ul className="ml-8 space-y-1">
                      {item.children.map((child) => (
                        <li key={child.name}>
                          <Link
                            href={child.href}
                            className={cn(
                              'flex items-center px-3 py-2 text-sm rounded-lg transition-colors',
                              isActive(child.href)
                                ? 'bg-blue-50 text-blue-700 font-medium'
                                : 'text-gray-700 hover:bg-gray-100'
                            )}
                          >
                            <child.icon className="w-4 h-4 mr-3" />
                            {child.name}
                          </Link>
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : (
                  <Link
                    href={item.href}
                    className={cn(
                      'flex items-center px-3 py-2 text-sm rounded-lg transition-colors',
                      isActive(item.href)
                        ? 'bg-blue-50 text-blue-700 font-medium'
                        : 'text-gray-700 hover:bg-gray-100'
                    )}
                  >
                    <item.icon className="w-5 h-5 mr-3" />
                    {item.name}
                  </Link>
                )}
              </li>
            ))}
          </ul>
        </nav>

        {/* Footer */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-semibold">
              U
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">User Name</p>
              <p className="text-xs text-gray-500 truncate">user@example.com</p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
