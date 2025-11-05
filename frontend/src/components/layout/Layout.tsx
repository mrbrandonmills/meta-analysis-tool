import React, { ReactNode } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';

interface LayoutProps {
  children: ReactNode;
  title?: string;
  breadcrumbs?: Array<{ label: string; href?: string }>;
}

export const Layout: React.FC<LayoutProps> = ({ children, title, breadcrumbs }) => {
  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar />

      <div className="flex-1 flex flex-col min-w-0">
        <Header title={title} breadcrumbs={breadcrumbs} />

        <main className="flex-1 overflow-auto">
          <div className="max-w-7xl mx-auto px-4 lg:px-6 py-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
