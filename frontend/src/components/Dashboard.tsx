import React, { useState } from 'react';

interface RecentActivity {
    id: number;
    user: string;
    action: string;
    time: string;
    status: 'success' | 'warning' | 'error';
}

export default function Dashboard() {
    const [activeTab, setActiveTab] = useState('overview');

    const recentActivities: RecentActivity[] = [
        { id: 1, user: 'John Doe', action: 'Created new agent', time: '2 min ago', status: 'success' },
        { id: 2, user: 'Jane Smith', action: 'Updated settings', time: '15 min ago', status: 'success' },
        { id: 3, user: 'System', action: 'Model update completed', time: '1 hour ago', status: 'success' },
        { id: 4, user: 'Alex Johnson', action: 'Agent failed to execute', time: '2 hours ago', status: 'error' },
        { id: 5, user: 'Sarah Williams', action: 'New conversation started', time: '3 hours ago', status: 'success' },
    ];

    return (
        <div style={{ display: 'flex', minHeight: '100vh' }}>
            {/* Sidebar */}
            <aside style={{ width: '240px', backgroundColor: 'var(--bg-sidebar)', padding: '24px', borderRight: '1px solid var(--border-color)' }}>
                <h2 style={{ color: 'var(--primary-main)', fontWeight: 800, margin: '0 0 24px 0' }}>Cleudocode</h2>
                <nav style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <button
                        className={`btn-ghost ${activeTab === 'overview' ? 'active' : ''}`}
                        onClick={() => setActiveTab('overview')}
                        style={{ textAlign: 'left', width: '100%' }}
                    >
                        Overview
                    </button>
                    <button
                        className={`btn-ghost ${activeTab === 'activity' ? 'active' : ''}`}
                        onClick={() => setActiveTab('activity')}
                        style={{ textAlign: 'left', width: '100%' }}
                    >
                        Activity
                    </button>
                    <button
                        className="btn-ghost"
                        style={{ textAlign: 'left', width: '100%' }}
                    >
                        Settings
                    </button>
                </nav>
            </aside>

            {/* Main Content */}
            <main style={{ flex: 1, padding: '24px' }}>
                <header style={{ marginBottom: '32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                        <h1 style={{ fontSize: '24px', margin: 0 }}>Dashboard</h1>
                        <p style={{ color: 'var(--text-secondary)', marginTop: '4px' }}>Welcome back, Operator.</p>
                    </div>
                    <button className="btn-primary">+ New Agent</button>
                </header>

                {activeTab === 'overview' && (
                    <div className="card" style={{ padding: '24px', marginBottom: '24px' }}>
                        <h3>System Status</h3>
                        <p style={{ color: 'var(--status-success)', fontWeight: 600 }}>All Systems Operational</p>
                    </div>
                )}

                <div className="card">
                    <div style={{ padding: '16px 24px', borderBottom: '1px solid var(--border-color)' }}>
                        <h3 style={{ margin: 0, fontSize: '16px' }}>Recent Activity</h3>
                    </div>
                    <div>
                        {recentActivities.map((activity, index) => (
                            <div key={activity.id} style={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                padding: '16px 24px',
                                borderBottom: index < recentActivities.length - 1 ? '1px solid var(--border-color)' : 'none',
                                alignItems: 'center'
                            }}>
                                <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                                    <span style={{
                                        width: '8px', height: '8px', borderRadius: '50%',
                                        backgroundColor: activity.status === 'success' ? 'var(--status-success)' : activity.status === 'error' ? 'var(--status-error-text)' : 'orange'
                                    }}></span>
                                    <div>
                                        <strong style={{ display: 'block', color: 'var(--text-primary)' }}>{activity.user}</strong>
                                        <span style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>{activity.action}</span>
                                    </div>
                                </div>
                                <span style={{ color: 'var(--text-disabled)', fontSize: '13px', fontFamily: 'var(--font-mono)' }}>{activity.time}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </main>
        </div>
    );
}
