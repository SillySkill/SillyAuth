import apiClient from './client';
import type { ApiResponse, Navigation, NavigationUpdateRequest } from '@/types';

export const getNavigation = async (): Promise<ApiResponse<Navigation>> => {
  const response = await apiClient.get<ApiResponse<Navigation>>('/navigation');
  return response.data;
};

export const updateNavigation = async (
  data: NavigationUpdateRequest
): Promise<ApiResponse<Navigation>> => {
  const response = await apiClient.put<ApiResponse<Navigation>>(
    '/navigation',
    data
  );
  return response.data;
};
