import React from 'react';
import { Menu, Bell, Search } from 'lucide-react';
import { useAppStore } from '@/stores/useAppStore';

interface HeaderProps {
  title?: string;
  breadcrumbs?: Array<{ label: string; href?: string }>;
}

export const Header: React.FC<HeaderProps> = ({ title, breadcrumbs }) => {
  const { toggleSidebar, notifications } = useAppStore();
  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <header className="sticky top-0 z-30 bg-white border-b border-gray-200">
      <div className="flex items-center justify-between h-16 px-4 lg:px-6">
        {/* Left section */}
        <div className="flex items-center space-x-4">
          <button
            onClick={toggleSidebar}
            className="lg:hidden text-gray-500 hover:text-gray-700"
          >
            <Menu className="w-6 h-6" />
          </button>

          {breadcrumbs ? (
            <nav className="flex items-center space-x-2 text-sm">
              {breadcrumbs.map((crumb, index) => (
                <React.Fragment key={index}>
                  {index > 0 && <span className="text-gray-400">/</span>}
                  {crumb.href ? (
                    <a href={crumb.href} className="text-gray-600 hover:text-gray-900">
                      {crumb.label}
                    </a>
                  ) : (
                    <span className="text-gray-900 font-medium">{crumb.label}</span>
                  )}
                </React.Fragment>
              ))}
            </nav>
          ) : title ? (
            <h1 className="text-xl font-semibold text-gray-900">{title}</h1>
          ) : null}
        </div>

        {/* Right section */}
        <div className="flex items-center space-x-4">
          {/* Search */}
          <div className="hidden md:block">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search projects..."
                className="w-64 pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Notifications */}
          <button className="relative p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg">
            <Bell className="w-6 h-6" />
            {unreadCount > 0 && (
              <span className="absolute top-1 right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                {unreadCount}
              </span>
            )}
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
