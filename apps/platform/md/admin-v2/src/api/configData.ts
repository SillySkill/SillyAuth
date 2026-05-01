import apiClient from './client';
import type { ApiResponse, PaginatedResponse } from '@/types';

// ---- ConfigData Types ----

export interface ConfigDataItem {
  category: string;
  name: string;
  data: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
}

export interface ConfigDataCreateRequest {
  category: string;
  name: string;
  data: Record<string, unknown>;
}

export interface ConfigDataUpdateRequest {
  data: Record<string, unknown>;
}

// ---- ConfigData API Functions ----

export const getConfigList = async (
  category: string
): Promise<PaginatedResponse<ConfigDataItem>> => {
  const response = await apiClient.get<PaginatedResponse<ConfigDataItem>>(
    `/config-data/list/${category}`
  );
  return response.data;
};

export const getConfigItem = async (
  category: string,
  name: string
): Promise<ApiResponse<ConfigDataItem>> => {
  const response = await apiClient.get<ApiResponse<ConfigDataItem>>(
    `/config-data/item/${category}/${name}`
  );
  return response.data;
};

export const createConfig = async (
  data: ConfigDataCreateRequest
): Promise<ApiResponse<ConfigDataItem>> => {
  const response = await apiClient.post<ApiResponse<ConfigDataItem>>(
    '/config-data',
    data
  );
  return response.data;
};

export const updateConfig = async (
  category: string,
  name: string,
  data: ConfigDataUpdateRequest
): Promise<ApiResponse<ConfigDataItem>> => {
  const response = await apiClient.put<ApiResponse<ConfigDataItem>>(
    `/config-data/item/${category}/${name}`,
    data
  );
  return response.data;
};

export const deleteConfig = async (
  category: string,
  name: string
): Promise<ApiResponse<null>> => {
  const response = await apiClient.delete<ApiResponse<null>>(
    `/config-data/item/${category}/${name}`
  );
  return response.data;
};
