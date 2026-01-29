'use client';

import { useState, useEffect } from 'react';
import Head from 'next/head';
import Layout from '@/components/layout/Layout';
import ChatInterface from '@/components/chat/ChatInterface';
import { MessageCircle, Settings, User, Moon, Sun, Menu, X } from 'lucide-react';
import '@/styles/globals.css';

export default function Home() {
  return (
    <div className="min-h-screen bg-background-light dark:bg-background-dark transition-colors duration-300">
      <Head>
        <title>Cleudocodebot - Your AI Assistant</title>
        <meta name="description" content="Advanced AI assistant for developers" />
        <link rel="icon" href="/favicon.ico" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet" />
      </Head>

      <div className="container mx-auto px-4 py-8">
        <section className="text-center max-w-3xl mx-auto">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-6">
            Your <span className="text-primary-500">AI Assistant</span> for Development
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
            Cleudocode helps you build, debug, and deploy with intelligent automation and expert guidance.
          </p>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-center space-x-4 mb-4">
              <div className="bg-primary-100 dark:bg-primary-900/30 p-3 rounded-lg">
                <Settings className="h-6 w-6 text-primary-500" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Quick Start</h2>
            </div>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              Get started with Cleudocode in seconds. Connect your tools, configure your preferences, and start building.
            </p>
            <button className="bg-primary-500 hover:bg-primary-600 text-white font-medium py-2 px-6 rounded-lg transition-colors">
              Begin Setup
            </button>
          </div>
        </section>

        <section className="mt-12">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 text-center">Try the Chat Interface</h2>
          <div className="max-w-2xl mx-auto">
            <ChatInterface />
          </div>
        </section>
      </div>
    </div>
  );
}