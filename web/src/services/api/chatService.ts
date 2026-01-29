// api/chatService.ts
import apiClient from './client';

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
}

export interface Conversation {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  messages: Message[];
}

export interface ChatRequest {
  message: string;
  conversationId?: string;
  model?: string;
}

export interface ChatResponse {
  conversationId: string;
  response: string;
  timestamp: string;
}

export const chatService = {
  // Get all conversations
  getConversations: async (): Promise<Conversation[]> => {
    try {
      const response = await apiClient.get('/conversations');
      return response.data;
    } catch (error) {
      console.error('Error fetching conversations:', error);
      throw error;
    }
  },

  // Get a specific conversation
  getConversation: async (id: string): Promise<Conversation> => {
    try {
      const response = await apiClient.get(`/conversations/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching conversation ${id}:`, error);
      throw error;
    }
  },

  // Create a new conversation
  createConversation: async (title: string): Promise<Conversation> => {
    try {
      const response = await apiClient.post('/conversations', { title });
      return response.data;
    } catch (error) {
      console.error('Error creating conversation:', error);
      throw error;
    }
  },

  // Send a message
  sendMessage: async (data: ChatRequest): Promise<ChatResponse> => {
    try {
      const response = await apiClient.post('/chat', data);
      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  },

  // Delete a conversation
  deleteConversation: async (id: string): Promise<void> => {
    try {
      await apiClient.delete(`/conversations/${id}`);
    } catch (error) {
      console.error(`Error deleting conversation ${id}:`, error);
      throw error;
    }
  },

  // Update conversation title
  updateConversationTitle: async (id: string, title: string): Promise<Conversation> => {
    try {
      const response = await apiClient.patch(`/conversations/${id}`, { title });
      return response.data;
    } catch (error) {
      console.error(`Error updating conversation ${id}:`, error);
      throw error;
    }
  }
};