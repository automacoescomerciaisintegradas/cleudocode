"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
// api/client.ts
const axios_1 = __importDefault(require("axios"));
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:11434';
const apiClient = axios_1.default.create({
    baseURL: `${API_BASE_URL}/v1`,
    headers: {
        'Content-Type': 'application/json',
    },
});
// Request interceptor to add auth token if available
apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('cleudocode_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});
// Response interceptor to handle common errors
apiClient.interceptors.response.use((response) => response, (error) => {
    if (error.response?.status === 401) {
        // Clear auth data and redirect to login
        localStorage.removeItem('cleudocode_token');
        localStorage.removeItem('cleudocode_user');
        window.location.href = '/login';
    }
    return Promise.reject(error);
});
exports.default = apiClient;
