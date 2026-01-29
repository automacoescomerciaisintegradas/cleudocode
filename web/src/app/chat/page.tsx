import Layout from '@/components/layout/Layout';
import ChatInterface from '@/components/chat/ChatInterface';

export default function Chat() {
  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Chat with Cleudocode</h1>
          <p className="text-gray-600 dark:text-gray-400">Have a conversation with your AI assistant</p>
        </div>
        <ChatInterface />
      </div>
    </Layout>
  );
}