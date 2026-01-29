'use client';

import { useState } from 'react';
import { Settings, Key, Shield, Globe, Palette, Bell, Database, Zap, Save, Check } from 'lucide-react';

interface SettingSection {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
}

export default function SettingsPage() {
  const [activeSection, setActiveSection] = useState('account');
  const [saved, setSaved] = useState(false);
  const [formData, setFormData] = useState({
    email: 'user@example.com',
    notifications: true,
    theme: 'dark',
    autoSave: true,
    apiEndpoint: 'http://localhost:11434',
    model: 'qwen2.5-coder:7b',
    temperature: 0.7,
    maxTokens: 2048,
  });

  const sections: SettingSection[] = [
    { 
      id: 'account', 
      title: 'Account', 
      description: 'Manage your account settings', 
      icon: <Settings className="h-5 w-5" /> 
    },
    { 
      id: 'security', 
      title: 'Security', 
      description: 'Password, 2FA, and privacy', 
      icon: <Shield className="h-5 w-5" /> 
    },
    { 
      id: 'api', 
      title: 'API Integration', 
      description: 'Connect external services', 
      icon: <Globe className="h-5 w-5" /> 
    },
    { 
      id: 'appearance', 
      title: 'Appearance', 
      description: 'Customize the interface', 
      icon: <Palette className="h-5 w-5" /> 
    },
    { 
      id: 'notifications', 
      title: 'Notifications', 
      description: 'Manage alerts and notifications', 
      icon: <Bell className="h-5 w-5" /> 
    },
    { 
      id: 'advanced', 
      title: 'Advanced', 
      description: 'Advanced configuration options', 
      icon: <Zap className="h-5 w-5" /> 
    },
  ];

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    const checked = type === 'checkbox' ? (e.target as HTMLInputElement).checked : undefined;
    
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // In a real app, this would save to backend
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const renderSection = () => {
    switch (activeSection) {
      case 'account':
        return (
          <div className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Email Address
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Profile Picture
              </label>
              <div className="flex items-center space-x-4">
                <div className="bg-gray-200 dark:bg-gray-700 border-2 border-dashed rounded-xl w-16 h-16" />
                <button className="text-sm text-primary-600 dark:text-primary-400 hover:underline">
                  Change
                </button>
              </div>
            </div>
          </div>
        );
      
      case 'security':
        return (
          <div className="space-y-6">
            <div>
              <label htmlFor="currentPassword" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Current Password
              </label>
              <input
                type="password"
                id="currentPassword"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              />
            </div>
            
            <div>
              <label htmlFor="newPassword" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                New Password
              </label>
              <input
                type="password"
                id="newPassword"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              />
            </div>
            
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Confirm New Password
              </label>
              <input
                type="password"
                id="confirmPassword"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              />
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="twoFactor"
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="twoFactor" className="ml-2 block text-sm text-gray-900 dark:text-white">
                Enable Two-Factor Authentication
              </label>
            </div>
          </div>
        );
      
      case 'api':
        return (
          <div className="space-y-6">
            <div>
              <label htmlFor="apiEndpoint" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                API Endpoint
              </label>
              <input
                type="text"
                id="apiEndpoint"
                name="apiEndpoint"
                value={formData.apiEndpoint}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              />
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                The URL of your Ollama server
              </p>
            </div>
            
            <div>
              <label htmlFor="model" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Default Model
              </label>
              <select
                id="model"
                name="model"
                value={formData.model}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              >
                <option value="qwen2.5-coder:7b">Qwen2.5-Coder 7B</option>
                <option value="llama3:8b">Llama 3 8B</option>
                <option value="mistral:7b">Mistral 7B</option>
                <option value="phi3:3.8b">Phi-3 3.8B</option>
              </select>
            </div>
            
            <div>
              <label htmlFor="temperature" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Temperature: {formData.temperature}
              </label>
              <input
                type="range"
                id="temperature"
                name="temperature"
                min="0"
                max="1"
                step="0.1"
                value={formData.temperature}
                onChange={handleChange}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
                <span>Precise</span>
                <span>Balanced</span>
                <span>Creative</span>
              </div>
            </div>
          </div>
        );
      
      case 'appearance':
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Theme
              </label>
              <div className="grid grid-cols-3 gap-4">
                {['light', 'dark', 'auto'].map((theme) => (
                  <div 
                    key={theme}
                    className={`border-2 rounded-lg p-4 cursor-pointer ${
                      formData.theme === theme 
                        ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' 
                        : 'border-gray-300 dark:border-gray-700'
                    }`}
                    onClick={() => setFormData({...formData, theme})}
                  >
                    <div className="flex items-center">
                      <div className={`w-4 h-4 rounded-full mr-2 ${
                        theme === 'light' ? 'bg-gray-200' : 
                        theme === 'dark' ? 'bg-gray-800' : 'bg-gradient-to-r from-gray-200 to-gray-800'
                      }`}></div>
                      <span className="capitalize text-gray-900 dark:text-white">{theme}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="autoSave"
                name="autoSave"
                checked={formData.autoSave}
                onChange={handleChange}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="autoSave" className="ml-2 block text-sm text-gray-900 dark:text-white">
                Auto-save conversations
              </label>
            </div>
          </div>
        );
      
      case 'notifications':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">Email Notifications</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Receive updates via email</p>
              </div>
              <button
                onClick={() => setFormData({...formData, notifications: !formData.notifications})}
                className={`relative inline-flex h-6 w-11 items-center rounded-full ${
                  formData.notifications ? 'bg-primary-500' : 'bg-gray-200 dark:bg-gray-700'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                    formData.notifications ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
            
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white mb-2">Notification Preferences</p>
              <div className="space-y-2">
                {['New messages', 'Agent status', 'System updates', 'Weekly digest'].map((item) => (
                  <div key={item} className="flex items-center">
                    <input
                      type="checkbox"
                      defaultChecked
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                    />
                    <label className="ml-2 block text-sm text-gray-900 dark:text-white">
                      {item}
                    </label>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );
      
      case 'advanced':
        return (
          <div className="space-y-6">
            <div>
              <label htmlFor="maxTokens" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Max Tokens: {formData.maxTokens}
              </label>
              <input
                type="range"
                id="maxTokens"
                name="maxTokens"
                min="1024"
                max="4096"
                step="256"
                value={formData.maxTokens}
                onChange={handleChange}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
                <span>1024</span>
                <span>2048</span>
                <span>4096</span>
              </div>
            </div>
            
            <div>
              <label htmlFor="customPrompt" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Custom System Prompt
              </label>
              <textarea
                id="customPrompt"
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                placeholder="Enter a custom system prompt that will be used for all conversations..."
              ></textarea>
            </div>
            
            <div className="pt-4">
              <button className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 font-medium">
                Reset to defaults
              </button>
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Settings</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">Manage your Cleudocode preferences</p>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Sidebar */}
        <div className="lg:w-1/4">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Settings</h2>
            </div>
            <nav className="p-2">
              <ul className="space-y-1">
                {sections.map((section) => (
                  <li key={section.id}>
                    <button
                      onClick={() => setActiveSection(section.id)}
                      className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left ${
                        activeSection === section.id
                          ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300'
                          : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                      }`}
                    >
                      <span className="text-gray-500 dark:text-gray-400">{section.icon}</span>
                      <span className="font-medium">{section.title}</span>
                    </button>
                  </li>
                ))}
              </ul>
            </nav>
          </div>
        </div>

        {/* Main content */}
        <div className="lg:w-3/4">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                {sections.find(s => s.id === activeSection)?.title}
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                {sections.find(s => s.id === activeSection)?.description}
              </p>
            </div>

            <form onSubmit={handleSubmit}>
              {renderSection()}

              <div className="mt-8 flex justify-end">
                <button
                  type="submit"
                  className="flex items-center space-x-2 bg-primary-500 hover:bg-primary-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                >
                  {saved ? (
                    <>
                      <Check className="h-5 w-5" />
                      <span>Saved!</span>
                    </>
                  ) : (
                    <>
                      <Save className="h-5 w-5" />
                      <span>Save Changes</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}