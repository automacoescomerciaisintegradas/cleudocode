'use client';

import { useState, useEffect } from 'react';
import { 
  Bot, 
  Plus, 
  Edit, 
  Trash2, 
  Copy, 
  Play, 
  Pause, 
  Settings,
  Search,
  Filter,
  MoreVertical,
  Clock,
  CheckCircle,
  AlertCircle,
  Zap
} from 'lucide-react';

interface Agent {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'inactive' | 'error';
  template: string;
  lastActivity: string;
  conversations: number;
  successRate: number;
  responseTime: number;
  createdAt: string;
  updated