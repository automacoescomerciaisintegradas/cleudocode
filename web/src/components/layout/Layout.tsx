'use client';

import Link from 'next/link';
import { ReactNode, useState } from 'react';
import { LayoutDashboard, MessageCircle, Bot, Settings, User, Moon, Sun, Menu, X, LogOut } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

interface SidebarItem {
  icon: React.ReactNode;
  label: string;
  href: string;
}

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const { user, logout } = useAuth();

  const sidebarItems: SidebarItem[] = [
    { icon: <LayoutDashboard className="h-5 w-5" />, label: 'Dashboard', href: '/' },
    { icon: <MessageCircle className="h-5 w-5" />, label: 'Chat', href: '/chat' },
    { icon: <Bot className="h-5 w-5" />, label: 'Agents', href: '/agents' },
    { icon: <Settings className="h-5 w-5" />, label: 'Settings', href: '/settings' },
  ];

  const toggleDarkMode = () => {
    const newDarkMode = !darkMode;
    setDarkMode(newDarkMode);
    localStorage.setItem('darkMode', String(newDarkMode));

    if (newDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      {/* Mobile sidebar toggle */}
      <div className="md:hidden fixed top-4 left-4 z-50">
        <button
          onClick={() => setSidebarOpen(true)}
          className="p-2 rounded-md bg-white dark:bg-gray-800 shadow-md"
        >
          <Menu className="h-6 w-6 text-gray-700 dark:text-gray-300" />
        </button>
      </div>

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-64 bg-white dark:bg-gray-800 shadow-lg transform transition-transform duration-300 ease-in-out md:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-2">
            <div className="bg-primary-500 p-2 rounded-lg">
              <MessageCircle className="h-6 w-6 text-white" />
            </div>
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">Cleudocode</h1>
          </div>
          <button
            className="md:hidden p-1 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <nav className="p-4">
          <ul className="space-y-2">
            {sidebarItems.map((item, index) => (
              <li key={index}>
                <Link
                  href={item.href}
                  className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 transition-colors"
                >
                  {item.icon}
                  <span>{item.label}</span>
                </Link>
              </li>
            ))}
          </ul>

          <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
            <button
              onClick={toggleDarkMode}
              className="flex items-center space-x-3 w-full p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 transition-colors"
            >
              {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
              <span>{darkMode ? 'Light Mode' : 'Dark Mode'}</span>
            </button>

            <div className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 transition-colors mt-2">
              <div className="flex items-center space-x-3">
                <User className="h-5 w-5" />
                <span>{user?.name || 'Guest'}</span>
              </div>
              <button
                onClick={logout}
                className="p-1 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700"
                title="Logout"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          </div>
        </nav>
      </aside>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black bg-opacity-50 md:hidden"
          onClick={() => setSidebarOpen(false)}
        ></div>
      )}

      {/* Main content */}
      <main className="flex-1 md:ml-64 transition-all duration-300">
        <div className="p-4 md:p-6">
          {children}
        </div>
      </main>
    </div>
  );
}