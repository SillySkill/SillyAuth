import apiClient from './client';
import type { ApiResponse, LoginResponse, User } from '@/types';

export const login = async (
  email: string,
  password: string
): Promise<LoginResponse> => {
  const response = await apiClient.post<LoginResponse>('/auth/dev-login', {
    email,
    password,
  });
  return response.data;
};

export const getCurrentUser = async (): Promise<ApiResponse<User>> => {
  const response = await apiClient.get<ApiResponse<User>>('/auth/me');
  return response.data;
};
