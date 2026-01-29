'use client';

import { useState, useEffect } from 'react';
import { Bot, Plus, Play, Pause, Trash2, Settings, Eye, Edit, Copy, MoreHorizontal, Loader2 } from 'lucide-react';
import { agentService, Agent, CreateAgentData } from '@/services/api/agentService';

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newAgent, setNewAgent] = useState({
    name: '',
    description: ''
  });
  const [error, setError] = useState<string | null>(null);

  // Load agents on component mount
  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    try {
      setLoading(true);
      const data = await agentService.getAgents();
      setAgents(data);
    } catch (err) {
      setError('Failed to load agents. Please try again later.');
      console.error('Error loading agents:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleAgentStatus = async (id: string) => {
    try {
      const agent = agents.find(a => a.id === id);
      if (!agent) return;

      if (agent.status === 'running') {
        await agentService.stopAgent(id);
      } else {
        await agentService.startAgent(id);
      }

      // Refresh the agent list
      loadAgents();
    } catch (err) {
      setError('Failed to update agent status. Please try again.');
      console.error('Error toggling agent status:', err);
    }
  };

  const deleteAgent = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this agent?')) {
      return;
    }

    try {
      await agentService.deleteAgent(id);
      setAgents(agents.filter(agent => agent.id !== id));
    } catch (err) {
      setError('Failed to delete agent. Please try again.');
      console.error('Error deleting agent:', err);
    }
  };

  const createAgent = async () => {
    if (!newAgent.name.trim() || !newAgent.description.trim()) {
      setError('Please fill in all fields');
      return;
    }

    try {
      const agentData: CreateAgentData = {
        name: newAgent.name,
        description: newAgent.description,
        config: {}
      };

      await agentService.createAgent(agentData);
      setNewAgent({ name: '', description: '' });
      setShowCreateModal(false);
      loadAgents(); // Refresh the list
    } catch (err) {
      setError('Failed to create agent. Please try again.');
      console.error('Error creating agent:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Agents</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Manage your automated assistants</p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center space-x-2 bg-primary-500 hover:bg-primary-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
          >
            <Plus className="h-5 w-5" />
            <span>New Agent</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 rounded-lg">
          {error}
        </div>
      )}

      {/* Agent Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {agents.map((agent) => (
          <div key={agent.id} className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
            <div className="p-5">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg ${
                    agent.status === 'running' ? 'bg-green-100 dark:bg-green-900/30' :
                    agent.status === 'stopped' ? 'bg-gray-100 dark:bg-gray-700' :
                    'bg-red-100 dark:bg-red-900/30'
                  }`}>
                    <Bot className={`h-5 w-5 ${
                      agent.status === 'running' ? 'text-green-500' :
                      agent.status === 'stopped' ? 'text-gray-500' :
                      'text-red-500'
                    }`} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white">{agent.name}</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">{agent.owner}</p>
                  </div>
                </div>
                <div className="relative">
                  <button className="p-1 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700">
                    <MoreHorizontal className="h-5 w-5 text-gray-500 dark:text-gray-400" />
                  </button>
                </div>
              </div>

              <p className="mt-3 text-sm text-gray-600 dark:text-gray-300">
                {agent.description}
              </p>

              <div className="mt-4 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    agent.status === 'running' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                    agent.status === 'stopped' ? 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300' :
                    'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
                  }`}>
                    {agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">{agent.lastRun}</span>
                </div>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {agent.tasksCompleted} tasks
                </span>
              </div>
            </div>

            <div className="bg-gray-50 dark:bg-gray-700/50 px-5 py-3 border-t border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <div className="flex space-x-2">
                  <button
                    onClick={() => toggleAgentStatus(agent.id)}
                    className={`p-2 rounded-md ${
                      agent.status === 'running'
                        ? 'bg-red-100 hover:bg-red-200 text-red-600 dark:bg-red-900/30 dark:hover:bg-red-800/50 dark:text-red-400'
                        : 'bg-green-100 hover:bg-green-200 text-green-600 dark:bg-green-900/30 dark:hover:bg-green-800/50 dark:text-green-400'
                    }`}
                  >
                    {agent.status === 'running' ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                  </button>
                  <button className="p-2 rounded-md bg-blue-100 hover:bg-blue-200 text-blue-600 dark:bg-blue-900/30 dark:hover:bg-blue-800/50 dark:text-blue-400">
                    <Edit className="h-4 w-4" />
                  </button>
                  <button className="p-2 rounded-md bg-gray-100 hover:bg-gray-200 text-gray-600 dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-gray-400">
                    <Settings className="h-4 w-4" />
                  </button>
                </div>
                <button
                  onClick={() => deleteAgent(agent.id)}
                  className="p-2 rounded-md bg-red-100 hover:bg-red-200 text-red-600 dark:bg-red-900/30 dark:hover:bg-red-800/50 dark:text-red-400"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Create Agent Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg w-full max-w-md">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Create New Agent</h3>

              <div className="space-y-4">
                <div>
                  <label htmlFor="agentName" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Name
                  </label>
                  <input
                    type="text"
                    id="agentName"
                    value={newAgent.name}
                    onChange={(e) => setNewAgent({...newAgent, name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    placeholder="Enter agent name"
                  />
                </div>

                <div>
                  <label htmlFor="agentDescription" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Description
                  </label>
                  <textarea
                    id="agentDescription"
                    value={newAgent.description}
                    onChange={(e) => setNewAgent({...newAgent, description: e.target.value})}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    placeholder="Describe what this agent does"
                  ></textarea>
                </div>
              </div>

              <div className="mt-6 flex justify-end space-x-3">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  Cancel
                </button>
                <button
                  onClick={createAgent}
                  className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg"
                >
                  Create Agent
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}