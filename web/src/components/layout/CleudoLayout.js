"use strict";
'use client';
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = CleudoLayout;
const react_1 = require("react");
const lucide_react_1 = require("lucide-react");
const link_1 = __importDefault(require("next/link"));
const navigation_1 = require("next/navigation");
const NOMES_MASC = ['José', 'João', 'Raimundo', 'Severino', 'Francisco', 'Pedro', 'Lucas', 'Mateus', 'Ronaldo', 'Cícero'];
const NOMES_FEM = ['Maria', 'Ana', 'Raimunda', 'Francisca', 'Juliana', 'Patrícia', 'Larissa', 'Renata', 'Camila', 'Fernanda'];
const ACOES = [
    'acabou de se conectar ao',
    'criou um novo agente no',
    'executou uma tarefa no',
    'fez upload de arquivos no',
    'ativou a memória RAG no',
    'iniciou uma automação no'
];
const EMOJIS = ['🤠', '🚀', '⚡', '🎯', '💡', '🔥'];
function CleudoLayout({ children }) {
    const [isSidebarOpen, setIsSidebarOpen] = (0, react_1.useState)(false);
    const [activities, setActivities] = (0, react_1.useState)([]);
    const pathname = (0, navigation_1.usePathname)();
    const navigation = [
        { name: 'Dashboard', href: '/dashboard', icon: lucide_react_1.TrendingUp },
        { name: 'Chat', href: '/chat', icon: lucide_react_1.MessageSquare },
        { name: 'Agentes', href: '/agents', icon: lucide_react_1.Bot },
        { name: 'Usuários', href: '/users', icon: lucide_react_1.Users },
        { name: 'Configurações', href: '/settings', icon: lucide_react_1.Settings },
    ];
    // Activity Carousel Logic
    const getRandomName = () => {
        const list = Math.random() > 0.5 ? NOMES_MASC : NOMES_FEM;
        return list[Math.floor(Math.random() * list.length)];
    };
    const getRandomAction = () => ACOES[Math.floor(Math.random() * ACOES.length)];
    const getRandomEmoji = () => EMOJIS[Math.floor(Math.random() * EMOJIS.length)];
    const createActivity = () => ({
        id: Date.now().toString() + Math.random(),
        user: getRandomName(),
        action: getRandomAction(),
        time: 'Agora mesmo',
        emoji: getRandomEmoji(),
    });
    (0, react_1.useEffect)(() => {
        const addActivity = () => {
            const newActivity = createActivity();
            setActivities(prev => {
                const updated = [newActivity, ...prev.slice(0, 4)]; // Keep max 5 items
                return updated;
            });
            // Remove activity after 8 seconds
            setTimeout(() => {
                setActivities(prev => prev.filter(activity => activity.id !== newActivity.id));
            }, 8000);
        };
        // Add initial activity
        addActivity();
        // Schedule random activities
        const scheduleNext = () => {
            const interval = Math.floor(Math.random() * (14000 - 6000) + 6000); // 6-14 seconds
            setTimeout(() => {
                addActivity();
                scheduleNext();
            }, interval);
        };
        scheduleNext();
    }, []);
    return (<div className="min-h-screen bg-gradient-bg text-text-primary">
      {/* Background Effects */}
      <div className="bg-stars bg-stars--animated"></div>
      <div className="vignette"></div>

      {/* Header */}
      <header className="fixed top-0 left-0 right-0 h-16 flex items-center justify-between px-6 bg-bg-dark/80 backdrop-blur-glass border-b border-surface-border z-50">
        <div className="flex items-center gap-4">
          <button onClick={() => setIsSidebarOpen(!isSidebarOpen)} className="lg:hidden p-2 rounded-lg hover:bg-surface-glass transition-colors">
            {isSidebarOpen ? <lucide_react_1.X className="h-5 w-5"/> : <lucide_react_1.Menu className="h-5 w-5"/>}
          </button>
          
          <div className="flex items-center gap-3">
            <div className="cleudo-avatar">
              🤖
            </div>
            <div>
              <h1 className="font-display font-bold text-lg">CleudoCode</h1>
              <p className="slogan text-xs">THE AI THAT ACTUALLY DOES THINGS</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-cleudo-accent-green/15 border border-cleudo-accent-green/30 rounded-full">
            <div className="w-2 h-2 bg-cleudo-accent-green rounded-full animate-pulse"></div>
            <span className="text-xs font-medium text-cleudo-accent-green">SISTEMA ATIVO</span>
          </div>
          
          <button className="cleudo-avatar">
            <lucide_react_1.User className="h-5 w-5"/>
          </button>
        </div>
      </header>

      {/* Sidebar */}
      <aside className={`fixed top-16 left-0 h-[calc(100vh-4rem)] w-64 bg-bg-card/90 backdrop-blur-glass border-r border-surface-border transform transition-transform duration-300 z-40 ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0`}>
        <nav className="p-4 space-y-2">
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            return (<link_1.default key={item.name} href={item.href} className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${isActive
                    ? 'bg-cleudo-accent-blue/20 text-cleudo-accent-blue border border-cleudo-accent-blue/30'
                    : 'hover:bg-surface-glass text-text-secondary hover:text-text-primary'}`} onClick={() => setIsSidebarOpen(false)}>
                <item.icon className="h-5 w-5"/>
                <span className="font-medium">{item.name}</span>
              </link_1.default>);
        })}
        </nav>
      </aside>

      {/* Main Content */}
      <main className={`pt-16 transition-all duration-300 ${isSidebarOpen ? 'lg:ml-64' : 'lg:ml-64'}`}>
        <div className="p-6 relative z-10">
          {children}
        </div>
      </main>

      {/* Activity Carousel */}
      <div className="cleudo-activity-carousel">
        <div className="cleudo-activity-track">
          {activities.map((activity) => (<div key={activity.id} className="cleudo-activity-card animate-slide-in">
              <div className="cleudo-activity-avatar">
                {activity.emoji}
              </div>
              <div>
                <div className="cleudo-activity-text">
                  <strong>{activity.user}</strong> {activity.action} <span className="brand">CleudoCode</span>
                </div>
                <div className="cleudo-activity-time">{activity.time}</div>
              </div>
            </div>))}
        </div>
      </div>

      {/* Mobile Sidebar Overlay */}
      {isSidebarOpen && (<div className="fixed inset-0 bg-black/50 z-30 lg:hidden" onClick={() => setIsSidebarOpen(false)}/>)}
    </div>);
}
