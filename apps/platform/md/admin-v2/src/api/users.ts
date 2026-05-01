import apiClient from './client';
import type {
  ApiResponse,
  PaginatedResponse,
  PaginationParams,
  User,
} from '@/types';

export interface UserUpdateData {
  role?: string;
  is_active?: boolean;
  email?: string;
}

export const getUsers = async (
  params: PaginationParams = {}
): Promise<PaginatedResponse<User>> => {
  const response = await apiClient.get<PaginatedResponse<User>>('/admin/users', {
    params,
  });
  return response.data;
};

export const getUser = async (id: number): Promise<ApiResponse<User>> => {
  const response = await apiClient.get<ApiResponse<User>>(`/admin/users/${id}`);
  return response.data;
};

export const updateUser = async (
  id: number,
  data: UserUpdateData
): Promise<ApiResponse<User>> => {
  const response = await apiClient.put<ApiResponse<User>>(
    `/admin/users/${id}/status`,
    data
  );
  return response.data;
};
