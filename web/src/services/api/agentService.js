"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.agentService = void 0;
// api/agentService.ts
const client_1 = __importDefault(require("./client"));
exports.agentService = {
    // Get all agents
    getAgents: async () => {
        try {
            const response = await client_1.default.get('/agents');
            return response.data;
        }
        catch (error) {
            console.error('Error fetching agents:', error);
            throw error;
        }
    },
    // Get a specific agent
    getAgent: async (id) => {
        try {
            const response = await client_1.default.get(`/agents/${id}`);
            return response.data;
        }
        catch (error) {
            console.error(`Error fetching agent ${id}:`, error);
            throw error;
        }
    },
    // Create a new agent
    createAgent: async (data) => {
        try {
            const response = await client_1.default.post('/agents', data);
            return response.data;
        }
        catch (error) {
            console.error('Error creating agent:', error);
            throw error;
        }
    },
    // Update an agent
    updateAgent: async (id, data) => {
        try {
            const response = await client_1.default.put(`/agents/${id}`, data);
            return response.data;
        }
        catch (error) {
            console.error(`Error updating agent ${id}:`, error);
            throw error;
        }
    },
    // Delete an agent
    deleteAgent: async (id) => {
        try {
            await client_1.default.delete(`/agents/${id}`);
        }
        catch (error) {
            console.error(`Error deleting agent ${id}:`, error);
            throw error;
        }
    },
    // Start an agent
    startAgent: async (id) => {
        try {
            const response = await client_1.default.post(`/agents/${id}/start`);
            return response.data;
        }
        catch (error) {
            console.error(`Error starting agent ${id}:`, error);
            throw error;
        }
    },
    // Stop an agent
    stopAgent: async (id) => {
        try {
            const response = await client_1.default.post(`/agents/${id}/stop`);
            return response.data;
        }
        catch (error) {
            console.error(`Error stopping agent ${id}:`, error);
            throw error;
        }
    }
};
