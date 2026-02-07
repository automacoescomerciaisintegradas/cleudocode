"use strict";
'use client';
Object.defineProperty(exports, "__esModule", { value: true });
exports.AuthProvider = AuthProvider;
exports.useAuth = useAuth;
const react_1 = require("react");
const AuthContext = (0, react_1.createContext)(undefined);
function AuthProvider({ children }) {
    const [user, setUser] = (0, react_1.useState)(null);
    const [loading, setLoading] = (0, react_1.useState)(true);
    (0, react_1.useEffect)(() => {
        // Check if user is logged in from localStorage or cookie
        const storedUser = localStorage.getItem('cleudocode_user');
        if (storedUser) {
            try {
                setUser(JSON.parse(storedUser));
            }
            catch (e) {
                console.error('Failed to parse user from localStorage', e);
            }
        }
        setLoading(false);
    }, []);
    const login = async (email, password) => {
        setLoading(true);
        try {
            // Simulate API call to backend
            await new Promise(resolve => setTimeout(resolve, 1000));
            // In a real app, this would be an API call to your backend
            // const response = await fetch('/api/login', { ... });
            // const userData = await response.json();
            // Mock user data
            const mockUser = {
                id: '1',
                name: 'John Doe',
                email: email,
                avatar: 'https://via.placeholder.com/40x40'
            };
            setUser(mockUser);
            localStorage.setItem('cleudocode_user', JSON.stringify(mockUser));
        }
        catch (error) {
            throw new Error('Login failed');
        }
        finally {
            setLoading(false);
        }
    };
    const register = async (name, email, password) => {
        setLoading(true);
        try {
            // Simulate API call to backend
            await new Promise(resolve => setTimeout(resolve, 1000));
            // Mock user data
            const mockUser = {
                id: '1',
                name: name,
                email: email,
                avatar: 'https://via.placeholder.com/40x40'
            };
            setUser(mockUser);
            localStorage.setItem('cleudocode_user', JSON.stringify(mockUser));
        }
        catch (error) {
            throw new Error('Registration failed');
        }
        finally {
            setLoading(false);
        }
    };
    const logout = () => {
        setUser(null);
        localStorage.removeItem('cleudocode_user');
    };
    const forgotPassword = async (email) => {
        // Simulate API call to backend
        await new Promise(resolve => setTimeout(resolve, 1000));
        // In a real app, this would send a reset link to the user's email
    };
    const value = {
        user,
        isAuthenticated: !!user,
        loading,
        login,
        register,
        logout,
        forgotPassword
    };
    return (<AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>);
}
function useAuth() {
    const context = (0, react_1.useContext)(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
