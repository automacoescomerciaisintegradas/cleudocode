"use strict";
'use client';
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = Layout;
const link_1 = __importDefault(require("next/link"));
const react_1 = require("react");
const lucide_react_1 = require("lucide-react");
const AuthContext_1 = require("@/contexts/AuthContext");
function Layout({ children }) {
    const [sidebarOpen, setSidebarOpen] = (0, react_1.useState)(false);
    const [darkMode, setDarkMode] = (0, react_1.useState)(false);
    const { user, logout } = (0, AuthContext_1.useAuth)();
    const sidebarItems = [
        { icon: <lucide_react_1.LayoutDashboard className="h-5 w-5"/>, label: 'Dashboard', href: '/' },
        { icon: <lucide_react_1.MessageCircle className="h-5 w-5"/>, label: 'Chat', href: '/chat' },
        { icon: <lucide_react_1.Bot className="h-5 w-5"/>, label: 'Agents', href: '/agents' },
        { icon: <lucide_react_1.Settings className="h-5 w-5"/>, label: 'Settings', href: '/settings' },
    ];
    const toggleDarkMode = () => {
        const newDarkMode = !darkMode;
        setDarkMode(newDarkMode);
        localStorage.setItem('darkMode', String(newDarkMode));
        if (newDarkMode) {
            document.documentElement.classList.add('dark');
        }
        else {
            document.documentElement.classList.remove('dark');
        }
    };
    return (<div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      {/* Mobile sidebar toggle */}
      <div className="md:hidden fixed top-4 left-4 z-50">
        <button onClick={() => setSidebarOpen(true)} className="p-2 rounded-md bg-white dark:bg-gray-800 shadow-md">
          <lucide_react_1.Menu className="h-6 w-6 text-gray-700 dark:text-gray-300"/>
        </button>
      </div>

      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-40 w-64 bg-white dark:bg-gray-800 shadow-lg transform transition-transform duration-300 ease-in-out md:translate-x-0 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-2">
            <div className="bg-primary-500 p-2 rounded-lg">
              <lucide_react_1.MessageCircle className="h-6 w-6 text-white"/>
            </div>
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">Cleudocode</h1>
          </div>
          <button className="md:hidden p-1 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700" onClick={() => setSidebarOpen(false)}>
            <lucide_react_1.X className="h-6 w-6"/>
          </button>
        </div>

        <nav className="p-4">
          <ul className="space-y-2">
            {sidebarItems.map((item, index) => (<li key={index}>
                <link_1.default href={item.href} className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 transition-colors">
                  {item.icon}
                  <span>{item.label}</span>
                </link_1.default>
              </li>))}
          </ul>

          <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
            <button onClick={toggleDarkMode} className="flex items-center space-x-3 w-full p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 transition-colors">
              {darkMode ? <lucide_react_1.Sun className="h-5 w-5"/> : <lucide_react_1.Moon className="h-5 w-5"/>}
              <span>{darkMode ? 'Light Mode' : 'Dark Mode'}</span>
            </button>

            <div className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 transition-colors mt-2">
              <div className="flex items-center space-x-3">
                <lucide_react_1.User className="h-5 w-5"/>
                <span>{user?.name || 'Guest'}</span>
              </div>
              <button onClick={logout} className="p-1 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700" title="Logout">
                <lucide_react_1.LogOut className="h-4 w-4"/>
              </button>
            </div>
          </div>
        </nav>
      </aside>

      {/* Overlay for mobile */}
      {sidebarOpen && (<div className="fixed inset-0 z-30 bg-black bg-opacity-50 md:hidden" onClick={() => setSidebarOpen(false)}></div>)}

      {/* Main content */}
      <main className="flex-1 md:ml-64 transition-all duration-300">
        <div className="p-4 md:p-6">
          {children}
        </div>
      </main>
    </div>);
}
