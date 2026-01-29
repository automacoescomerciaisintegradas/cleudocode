'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import AuthForm from '@/components/auth/AuthForm';
import Layout from '@/components/layout/Layout';

export default function LoginPage() {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const router = useRouter();
  const { login, register } = useAuth();

  const handleSuccess = () => {
    router.push('/');
  };

  const handleSubmit = async (email: string, password: string, name?: string) => {
    try {
      if (mode === 'login') {
        await login(email, password);
      } else {
        if (name) {
          await register(name, email, password);
        }
      }
      handleSuccess();
    } catch (error) {
      console.error('Authentication error:', error);
    }
  };

  return (
    <Layout>
      <div className="flex items-center justify-center min-h-[calc(100vh-8rem)] py-12">
        <AuthForm 
          mode={mode} 
          onToggleMode={() => setMode(mode === 'login' ? 'register' : 'login')} 
          onSuccess={handleSuccess}
        />
      </div>
    </Layout>
  );
}