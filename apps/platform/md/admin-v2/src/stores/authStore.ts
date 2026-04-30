import { create } from 'zustand';
import type { User } from '@/types';
import apiClient from '@/api/client';

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('sillymd_admin_token'),
  user: null,
  isAuthenticated: !!localStorage.getItem('sillymd_admin_token'),
  isLoading: false,

  login: async (username: string, password: string) => {
    set({ isLoading: true });
    try {
      const response = await apiClient.post('/auth/login', {
        username,
        password,
      });

      const { token, user } = response.data.data;

      localStorage.setItem('sillymd_admin_token', token);
      localStorage.setItem('sillymd_admin_user', JSON.stringify(user));

      set({
        token,
        user,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem('sillymd_admin_token');
    localStorage.removeItem('sillymd_admin_user');
    set({
      token: null,
      user: null,
      isAuthenticated: false,
    });
  },

  checkAuth: async () => {
    const token = localStorage.getItem('sillymd_admin_token');
    if (!token) {
      set({ isAuthenticated: false, isLoading: false });
      return;
    }

    set({ isLoading: true, token });
    try {
      const response = await apiClient.get('/auth/me');
      const user = response.data.data;

      localStorage.setItem('sillymd_admin_user', JSON.stringify(user));

      set({
        user,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch {
      localStorage.removeItem('sillymd_admin_token');
      localStorage.removeItem('sillymd_admin_user');
      set({
        token: null,
        user: null,
        isAuthenticated: false,
        isLoading: false,
      });
    }
  },
}));
