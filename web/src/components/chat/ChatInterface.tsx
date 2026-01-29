'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Copy, ThumbsUp, ThumbsDown, Paperclip } from 'lucide-react';
import { chatService, ChatRequest } from '@/services/api/chatService';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize with a welcome message
  useEffect(() => {
    if (messages.length === 0) {
      const welcomeMessage: Message = {
        id: 'welcome',
        content: 'Hello! I\'m your Cleudocode assistant. How can I help you today?',
        role: 'assistant',
        timestamp: new Date(),
      };
      setMessages([welcomeMessage]);
    }
  }, [messages.length]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      role: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Prepare the chat request
      const chatRequest: ChatRequest = {
        message: inputValue,
        conversationId: conversationId || undefined,
      };

      // Send message to backend
      const response = await chatService.sendMessage(chatRequest);

      // Update conversation ID if new conversation was created
      if (!conversationId) {
        setConversationId(response.conversationId);
      }

      // Add assistant response
      const assistantMessage: Message = {
        id: Date.now().toString(),
        content: response.response,
        role: 'assistant',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: Date.now().toString(),
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        role: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] max-w-4xl mx-auto bg-white dark:bg-gray-900 rounded-lg shadow-lg overflow-hidden">
      {/* Chat header */}
      <div className="bg-gray-50 dark:bg-gray-800 px-4 py-3 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-2">
          <div className="bg-primary-500 p-2 rounded-lg">
            <Bot className="h-5 w-5 text-white" />
          </div>
          <h2 className="font-semibold text-gray-900 dark:text-white">Cleudocode Assistant</h2>
        </div>
      </div>

      {/* Messages container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-900">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                message.role === 'user'
                  ? 'bg-primary-500 text-white rounded-br-none'
                  : 'bg-gray-200 dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-bl-none'
              }`}
            >
              <div className="flex items-start space-x-2">
                {message.role === 'assistant' && (
                  <div className="flex-shrink-0 pt-0.5">
                    <Bot className="h-4 w-4" />
                  </div>
                )}
                <div className="flex-1">
                  <p className="whitespace-pre-wrap">{message.content}</p>
                  <div className="flex items-center mt-2 space-x-2">
                    <button
                      onClick={() => copyToClipboard(message.content)}
                      className={`p-1 rounded hover:bg-opacity-20 ${
                        message.role === 'user' ? 'hover:bg-white' : 'hover:bg-gray-500'
                      }`}
                      title="Copy to clipboard"
                    >
                      <Copy className="h-3 w-3" />
                    </button>
                    {message.role === 'assistant' && (
                      <>
                        <button className="p-1 rounded hover:bg-gray-500 hover:bg-opacity-20">
                          <ThumbsUp className="h-3 w-3" />
                        </button>
                        <button className="p-1 rounded hover:bg-gray-500 hover:bg-opacity-20">
                          <ThumbsDown className="h-3 w-3" />
                        </button>
                      </>
                    )}
                  </div>
                </div>
                {message.role === 'user' && (
                  <div className="flex-shrink-0 pt-0.5">
                    <User className="h-4 w-4" />
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="max-w-[80%] rounded-2xl rounded-bl-none bg-gray-200 dark:bg-gray-800 text-gray-800 dark:text-gray-200 px-4 py-3">
              <div className="flex items-center space-x-2">
                <Bot className="h-4 w-4" />
                <div className="flex space-x-1">
                  <div className="h-2 w-2 bg-gray-500 rounded-full animate-bounce"></div>
                  <div className="h-2 w-2 bg-gray-500 rounded-full animate-bounce delay-75"></div>
                  <div className="h-2 w-2 bg-gray-500 rounded-full animate-bounce delay-150"></div>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-gray-200 dark:border-gray-700 p-4 bg-white dark:bg-gray-900">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <button
            type="button"
            className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-500 dark:text-gray-400"
            title="Attach file"
          >
            <Paperclip className="h-5 w-5" />
          </button>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 border border-gray-300 dark:border-gray-700 rounded-full px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || isLoading}
            className="bg-primary-500 hover:bg-primary-600 text-white rounded-full p-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="h-5 w-5" />
          </button>
        </form>
        <p className="text-xs text-center text-gray-500 dark:text-gray-400 mt-2">
          Cleudocode Assistant can make mistakes. Verify important information.
        </p>
      </div>
    </div>
  );
}