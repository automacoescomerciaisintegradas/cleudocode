'use client';

import { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  MessageSquare, 
  Clock, 
  Zap, 
  Download, 
  Calendar,
  BarChart3,
  PieChart,
  Activity,
  Users
} from 'lucide-react';

interface MetricData {
  label: string;
  value: number;
  change: number;
  positive: boolean;
}

interface ChartData {
  date: string;
  conversations: number;
  tokens: number;
  responseTime: number;
}

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState('30d');
  const [metrics, setMetrics] = useState<MetricData[]>([]);
  const [chartData, setChartData] = useState<ChartData[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Simulate real-time data updates
  useEffect(() => {
    const updateMetrics = () => {
      setMetrics([
        {
          label: 'Conversas Totais',
          value: Math.floor(Math.random() * 1000) + 1200,
          change: Math.floor(Math.random() * 20) + 5,
          positive: true
        },
        {
          label: 'Tokens Processados',
          value: Math.floor(Math.random() * 50000) + 125000,
          change: Math.floor(Math.random() * 15) + 8,
          positive: true
        },
        {
          label: 'Tempo Médio de Resposta',
          value: Math.floor(Math.random() * 500) + 850,
          change: Math.floor(Math.random() * 10) + 2,
          positive: false
        },
        {
          label: 'Taxa de Sucesso',
          value: Math.floor(Math.random() * 5) + 95,
          change: Math.floor(Math.random() * 3) + 1,
          positive: true
        }
      ]);

      // Generate chart data
      const data: ChartData[] = [];
      for (let i = 29; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        data.push({
          date: date.toISOString().split('T')[0],
          conversations: Math.floor(Math.random() * 50) + 20,
          tokens: Math.floor(Math.random() * 2000) + 1000,
          responseTime: Math.floor(Math.random() * 200) + 800
        });
      }
      setChartData(data);
      setIsLoading(false);
    };

    updateMetrics();
    const interval = setInterval(updateMetrics, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, [timeRange]);

  const exportData = (format: 'pdf' | 'csv') => {
    // Simulate export functionality
    const data = {
      metrics,
      chartData,
      exportDate: new Date().toISOString(),
      format
    };
    
    console.log(`Exportando dados em formato ${format.toUpperCase()}:`, data);
    
    // In a real implementation, this would trigger a download
    alert(`Dados exportados em formato ${format.toUpperCase()}! (Simulação)`);
  };

  const MetricCard = ({ metric }: { metric: MetricData }) => (
    <div className="cleudo-card animate-fade-in">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-text-secondary">{metric.label}</h3>
        <div className="p-2 bg-cleudo-accent-blue/20 rounded-lg">
          {metric.label.includes('Conversas') && <MessageSquare className="h-4 w-4 text-cleudo-accent-blue" />}
          {metric.label.includes('Tokens') && <Zap className="h-4 w-4 text-cleudo-accent-blue" />}
          {metric.label.includes('Tempo') && <Clock className="h-4 w-4 text-cleudo-accent-blue" />}
          {metric.label.includes('Taxa') && <TrendingUp className="h-4 w-4 text-cleudo-accent-blue" />}
        </div>
      </div>
      
      <div className="space-y-2">
        <p className="text-2xl font-bold text-text-primary">
          {metric.label.includes('Tokens') 
            ? metric.value.toLocaleString() 
            : metric.label.includes('Tempo')
              ? `${metric.value}ms`
              : metric.label.includes('Taxa')
                ? `${metric.value}%`
                : metric.value.toLocaleString()
          }
        </p>
        
        <div className={`flex items-center gap-1 text-sm ${
          metric.positive ? 'text-cleudo-accent-green' : 'text-cleudo-primary'
        }`}>
          <TrendingUp className={`h-4 w-4 ${!metric.positive ? 'rotate-180' : ''}`} />
          <span>{metric.positive ? '+' : '-'}{metric.change}%</span>
          <span className="text-text-muted ml-1">vs período anterior</span>
        </div>
      </div>
    </div>
  );

  const SimpleChart = ({ data, title, dataKey, color }: { 
    data: ChartData[], 
    title: string, 
    dataKey: keyof ChartData,
    color: string 
  }) => (
    <div className="cleudo-card">
      <h3 className="text-lg font-semibold text-text-primary mb-4">{title}</h3>
      <div className="h-64 flex items-end justify-between gap-1 p-4 bg-bg-dark/50 rounded-lg">
        {data.slice(-14).map((item, index) => {
          const value = item[dataKey] as number;
          const maxValue = Math.max(...data.map(d => d[dataKey] as number));
          const height = (value / maxValue) * 200;
          
          return (
            <div
              key={index}
              className="flex-1 flex flex-col items-center gap-2"
            >
              <div
                className={`w-full rounded-t transition-all duration-500 delay-${index * 50}`}
                style={{ 
                  height: `${height}px`,
                  background: `linear-gradient(to top, ${color}, ${color}80)`
                }}
              />
              <span className="text-xs text-text-muted transform -rotate-45 origin-center">
                {new Date(item.date).getDate()}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-center h-64">
          <div className="cleudo-avatar animate-spin">
            <Activity className="h-6 w-6" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-text-primary glow-title">Analytics</h1>
          <p className="text-text-secondary mt-1">Métricas detalhadas e relatórios interativos</p>
        </div>
        
        <div className="flex items-center gap-3">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-4 py-2 bg-bg-card border border-surface-border rounded-lg text-text-primary focus:outline-none focus:border-cleudo-accent-blue"
          >
            <option value="7d">Últimos 7 dias</option>
            <option value="30d">Últimos 30 dias</option>
            <option value="90d">Últimos 90 dias</option>
            <option value="1y">Último ano</option>
          </select>
          
          <div className="flex gap-2">
            <button
              onClick={() => exportData('csv')}
              className="cleudo-btn cleudo-btn--outline"
            >
              <Download className="h-4 w-4" />
              CSV
            </button>
            <button
              onClick={() => exportData('pdf')}
              className="cleudo-btn cleudo-btn--primary"
            >
              <Download className="h-4 w-4" />
              PDF
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => (
          <div key={metric.label} className={`delay-${index * 100}`}>
            <MetricCard metric={metric} />
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SimpleChart
          data={chartData}
          title="Conversas por Dia"
          dataKey="conversations"
          color="#5B7CFF"
        />
        <SimpleChart
          data={chartData}
          title="Tokens Processados"
          dataKey="tokens"
          color="#10b981"
        />
      </div>

      <div className="grid grid-cols-1 gap-6">
        <SimpleChart
          data={chartData}
          title="Tempo de Resposta (ms)"
          dataKey="responseTime"
          color="#ef4444"
        />
      </div>

      {/* Real-time Status */}
      <div className="cleudo-card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-text-primary">Status em Tempo Real</h3>
          <div className="flex items-center gap-2 text-cleudo-accent-green">
            <div className="w-2 h-2 bg-cleudo-accent-green rounded-full animate-pulse"></div>
            <span className="text-sm">Atualizando automaticamente</span>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-bg-dark/50 rounded-lg">
            <div className="flex items-center gap-3">
              <Users className="h-5 w-5 text-cleudo-accent-blue" />
              <div>
                <p className="text-sm text-text-secondary">Usuários Ativos</p>
                <p className="text-xl font-bold text-text-primary">
                  {Math.floor(Math.random() * 50) + 25}
                </p>
              </div>
            </div>
          </div>
          
          <div className="p-4 bg-bg-dark/50 rounded-lg">
            <div className="flex items-center gap-3">
              <MessageSquare className="h-5 w-5 text-cleudo-accent-green" />
              <div>
                <p className="text-sm text-text-secondary">Conversas Ativas</p>
                <p className="text-xl font-bold text-text-primary">
                  {Math.floor(Math.random() * 20) + 10}
                </p>
              </div>
            </div>
          </div>
          
          <div className="p-4 bg-bg-dark/50 rounded-lg">
            <div className="flex items-center gap-3">
              <Activity className="h-5 w-5 text-cleudo-accent-orange" />
              <div>
                <p className="text-sm text-text-secondary">CPU Usage</p>
                <p className="text-xl font-bold text-text-primary">
                  {Math.floor(Math.random() * 30) + 45}%
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}