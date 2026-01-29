'use client';

import { useState } from 'react';
import { Activity, MessageSquare, Bot, Users, TrendingUp, Clock, CheckCircle, AlertCircle } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string;
  icon: React.ReactNode;
  change?: string;
  positive?: boolean;
}

const StatCard = ({ title, value, icon, change, positive }: StatCardProps) => (
  <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</p>
        <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{value}</p>
        {change && (
          <p className={`text-sm mt-1 flex items-center ${positive ? 'text-green-600' : 'text-red-600'}`}>
            {positive ? <TrendingUp className="h-4 w-4 mr-1" /> : <TrendingUp className="h-4 w-4 mr-1 rotate-180" />}
            {change}
          </p>
        )}
      </div>
      <div className="p-3 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
        {icon}
      </div>
    </div>
  </div>
);

interface RecentActivity {
  id: number;
  user: string;
  action: string;
  time: string;
  status: 'success' | 'warning' | 'error';
}

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview');

  const recentActivities: RecentActivity[] = [
    { id: 1, user: 'John Doe', action: 'Created new agent', time: '2 min ago', status: 'success' },
    { id: 2, user: 'Jane Smith', action: 'Updated settings', time: '15 min ago', status: 'success' },
    { id: 3, user: 'System', action: 'Model update completed', time: '1 hour ago', status: 'success' },
    { id: 4, user: 'Alex Johnson', action: 'Agent failed to execute', time: '2 hours ago', status: 'error' },
    { id: 5, user: 'Sarah Williams', action: 'New conversation started', time: '3 hours ago', status: 'success' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Overview of your Cleudocode activity</p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button className="bg-primary-500 hover:bg-primary-600 text-white font-medium py-2 px-4 rounded-lg transition-colors">
            New Agent
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          title="Total Conversations" 
          value="1,248" 
          change="+12%" 
          positive={true}
          icon={<MessageSquare className="h-6 w-6 text-primary-500" />} 
        />
        <StatCard 
          title="Active Agents" 
          value="24" 
          change="+3" 
          positive={true}
          icon={<Bot className="h-6 w-6 text-primary-500" />} 
        />
        <StatCard 
          title="Users" 
          value="142" 
          change="+5%" 
          positive={true}
          icon={<Users className="h-6 w-6 text-primary-500" />} 
        />
        <StatCard 
          title="Uptime" 
          value="99.9%" 
          change="+0.1%" 
          positive={true}
          icon={<Activity className="h-6 w-6 text-primary-500" />} 
        />
      </div>

      {/* Tabs */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('overview')}
              className={`py-4 px-6 text-center border-b-2 font-medium text-sm ${
                activeTab === 'overview'
                  ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('activity')}
              className={`py-4 px-6 text-center border-b-2 font-medium text-sm ${
                activeTab === 'activity'
                  ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              Recent Activity
            </button>
            <button
              onClick={() => setActiveTab('performance')}
              className={`py-4 px-6 text-center border-b-2 font-medium text-sm ${
                activeTab === 'performance'
                  ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              Performance
            </button>
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Conversation Trends</h3>
                <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 h-64 flex items-center justify-center">
                  <p className="text-gray-500 dark:text-gray-400">Chart visualization would appear here</p>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Top Performing Agents</h3>
                <div className="space-y-4">
                  {[1, 2, 3].map((item) => (
                    <div key={item} className="flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                      <div className="flex items-center space-x-4">
                        <div className="bg-primary-100 dark:bg-primary-900/30 p-2 rounded-lg">
                          <Bot className="h-5 w-5 text-primary-500" />
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900 dark:text-white">Agent {item}</h4>
                          <p className="text-sm text-gray-500 dark:text-gray-400">Last active: 2 hours ago</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-gray-900 dark:text-white">98%</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Success rate</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'activity' && (
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Recent Activity</h3>
              <div className="space-y-4">
                {recentActivities.map((activity) => (
                  <div key={activity.id} className="flex items-start p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
                    <div className={`p-2 rounded-full mr-3 ${
                      activity.status === 'success' 
                        ? 'bg-green-100 dark:bg-green-900/30' 
                        : activity.status === 'warning'
                          ? 'bg-yellow-100 dark:bg-yellow-900/30'
                          : 'bg-red-100 dark:bg-red-900/30'
                    }`}>
                      {activity.status === 'success' ? (
                        <CheckCircle className="h-5 w-5 text-green-500" />
                      ) : activity.status === 'warning' ? (
                        <AlertCircle className="h-5 w-5 text-yellow-500" />
                      ) : (
                        <AlertCircle className="h-5 w-5 text-red-500" />
                      )}
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900 dark:text-white">
                        <span className="font-semibold">{activity.user}</span> {activity.action}
                      </p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">{activity.time}</p>
                    </div>
                    <Clock className="h-5 w-5 text-gray-400" />
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'performance' && (
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Performance Metrics</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">Response Time</h4>
                  <div className="h-40 flex items-center justify-center">
                    <p className="text-gray-500 dark:text-gray-400">Response time chart</p>
                  </div>
                </div>
                <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">Success Rate</h4>
                  <div className="h-40 flex items-center justify-center">
                    <p className="text-gray-500 dark:text-gray-400">Success rate chart</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}