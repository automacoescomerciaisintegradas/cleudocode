"use strict";
'use client';
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = LoginPage;
const react_1 = require("react");
const navigation_1 = require("next/navigation");
const AuthContext_1 = require("@/contexts/AuthContext");
const AuthForm_1 = __importDefault(require("@/components/auth/AuthForm"));
const Layout_1 = __importDefault(require("@/components/layout/Layout"));
function LoginPage() {
    const [mode, setMode] = (0, react_1.useState)('login');
    const router = (0, navigation_1.useRouter)();
    const { login, register } = (0, AuthContext_1.useAuth)();
    const handleSuccess = () => {
        router.push('/');
    };
    const handleSubmit = async (email, password, name) => {
        try {
            if (mode === 'login') {
                await login(email, password);
            }
            else {
                if (name) {
                    await register(name, email, password);
                }
            }
            handleSuccess();
        }
        catch (error) {
            console.error('Authentication error:', error);
        }
    };
    return (<Layout_1.default>
      <div className="flex items-center justify-center min-h-[calc(100vh-8rem)] py-12">
        <AuthForm_1.default mode={mode} onToggleMode={() => setMode(mode === 'login' ? 'register' : 'login')} onSuccess={handleSuccess}/>
      </div>
    </Layout_1.default>);
}
