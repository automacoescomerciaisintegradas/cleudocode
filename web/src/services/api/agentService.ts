// api/agentService.ts
import apiClient from './client';

export interface Agent {
  id: string;
  name: string;
  description: string;
  status: 'running' | 'stopped' | 'error';
  lastRun: string;
  tasksCompleted: number;
  owner: string;
  config: Record<string, any>;
}

export interface CreateAgentData {
  name: string;
  description: string;
  config: Record<string, any>;
}

export const agentService = {
  // Get all agents
  getAgents: async (): Promise<Agent[]> => {
    try {
      const response = await apiClient.get('/agents');
      return response.data;
    } catch (error) {
      console.error('Error fetching agents:', error);
      throw error;
    }
  },

  // Get a specific agent
  getAgent: async (id: string): Promise<Agent> => {
    try {
      const response = await apiClient.get(`/agents/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching agent ${id}:`, error);
      throw error;
    }
  },

  // Create a new agent
  createAgent: async (data: CreateAgentData): Promise<Agent> => {
    try {
      const response = await apiClient.post('/agents', data);
      return response.data;
    } catch (error) {
      console.error('Error creating agent:', error);
      throw error;
    }
  },

  // Update an agent
  updateAgent: async (id: string, data: Partial<CreateAgentData>): Promise<Agent> => {
    try {
      const response = await apiClient.put(`/agents/${id}`, data);
      return response.data;
    } catch (error) {
      console.error(`Error updating agent ${id}:`, error);
      throw error;
    }
  },

  // Delete an agent
  deleteAgent: async (id: string): Promise<void> => {
    try {
      await apiClient.delete(`/agents/${id}`);
    } catch (error) {
      console.error(`Error deleting agent ${id}:`, error);
      throw error;
    }
  },

  // Start an agent
  startAgent: async (id: string): Promise<Agent> => {
    try {
      const response = await apiClient.post(`/agents/${id}/start`);
      return response.data;
    } catch (error) {
      console.error(`Error starting agent ${id}:`, error);
      throw error;
    }
  },

  // Stop an agent
  stopAgent: async (id: string): Promise<Agent> => {
    try {
      const response = await apiClient.post(`/agents/${id}/stop`);
      return response.data;
    } catch (error) {
      console.error(`Error stopping agent ${id}:`, error);
      throw error;
    }
  }
};