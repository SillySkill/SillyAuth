import apiClient from './client';
import type { ApiResponse, SEOConfig, SEOConfigUpdateRequest } from '@/types';

export const getSEOConfig = async (): Promise<ApiResponse<SEOConfig[]>> => {
  const response = await apiClient.get<ApiResponse<SEOConfig[]>>('/seo');
  return response.data;
};

export const updateSEOConfig = async (
  data: SEOConfigUpdateRequest
): Promise<ApiResponse<SEOConfig>> => {
  const response = await apiClient.put<ApiResponse<SEOConfig>>('/seo', data);
  return response.data;
};
