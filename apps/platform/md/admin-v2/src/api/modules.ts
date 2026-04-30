import apiClient from './client';
import type { ApiResponse, ModuleInfo } from '@/types';

export const getModules = async (): Promise<ApiResponse<ModuleInfo[]>> => {
  const response = await apiClient.get<ApiResponse<ModuleInfo[]>>('/modules');
  return response.data;
};

export const enableModule = async (
  id: number
): Promise<ApiResponse<ModuleInfo>> => {
  const response = await apiClient.post<ApiResponse<ModuleInfo>>(
    `/modules/${id}/enable`
  );
  return response.data;
};

export const disableModule = async (
  id: number
): Promise<ApiResponse<ModuleInfo>> => {
  const response = await apiClient.post<ApiResponse<ModuleInfo>>(
    `/modules/${id}/disable`
  );
  return response.data;
};
