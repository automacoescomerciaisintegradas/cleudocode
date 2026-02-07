"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.chatService = void 0;
// api/chatService.ts
const client_1 = __importDefault(require("./client"));
exports.chatService = {
    // Get all conversations
    getConversations: async () => {
        try {
            const response = await client_1.default.get('/conversations');
            return response.data;
        }
        catch (error) {
            console.error('Error fetching conversations:', error);
            throw error;
        }
    },
    // Get a specific conversation
    getConversation: async (id) => {
        try {
            const response = await client_1.default.get(`/conversations/${id}`);
            return response.data;
        }
        catch (error) {
            console.error(`Error fetching conversation ${id}:`, error);
            throw error;
        }
    },
    // Create a new conversation
    createConversation: async (title) => {
        try {
            const response = await client_1.default.post('/conversations', { title });
            return response.data;
        }
        catch (error) {
            console.error('Error creating conversation:', error);
            throw error;
        }
    },
    // Send a message
    sendMessage: async (data) => {
        try {
            const response = await client_1.default.post('/chat', data);
            return response.data;
        }
        catch (error) {
            console.error('Error sending message:', error);
            throw error;
        }
    },
    // Delete a conversation
    deleteConversation: async (id) => {
        try {
            await client_1.default.delete(`/conversations/${id}`);
        }
        catch (error) {
            console.error(`Error deleting conversation ${id}:`, error);
            throw error;
        }
    },
    // Update conversation title
    updateConversationTitle: async (id, title) => {
        try {
            const response = await client_1.default.patch(`/conversations/${id}`, { title });
            return response.data;
        }
        catch (error) {
            console.error(`Error updating conversation ${id}:`, error);
            throw error;
        }
    }
};
