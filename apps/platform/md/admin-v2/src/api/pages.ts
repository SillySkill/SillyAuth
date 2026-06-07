import apiClient from './client';
import type { ApiResponse, PaginatedResponse } from '@/types';

// ---- Page Types ----

export interface Page {
  id: number;
  slug: string;
  title: string;
  content: string;
  status: 'draft' | 'published';
  meta_title?: string;
  meta_description?: string;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface PageCreateRequest {
  slug: string;
  title: string;
  content?: string;
  status?: 'draft' | 'published';
  meta_title?: string;
  meta_description?: string;
  sort_order?: number;
}

export interface PageUpdateRequest {
  slug?: string;
  title?: string;
  content?: string;
  status?: 'draft' | 'published';
  meta_title?: string;
  meta_description?: string;
  sort_order?: number;
}

// ---- API Functions ----

export const getPages = async (params: {
  status?: string;
  search?: string;
  page?: number;
  page_size?: number;
} = {}): Promise<PaginatedResponse<Page>> => {
  const response = await apiClient.get<PaginatedResponse<Page>>('/pages', { params });
  return response.data;
};

export const getPage = async (id: number): Promise<ApiResponse<Page>> => {
  const response = await apiClient.get<ApiResponse<Page>>(`/pages/${id}`);
  return response.data;
};

export const createPage = async (data: PageCreateRequest): Promise<ApiResponse<Page>> => {
  const response = await apiClient.post<ApiResponse<Page>>('/pages', data);
  return response.data;
};

export const updatePage = async (id: number, data: PageUpdateRequest): Promise<ApiResponse<Page>> => {
  const response = await apiClient.put<ApiResponse<Page>>(`/pages/${id}`, data);
  return response.data;
};

export const deletePage = async (id: number): Promise<ApiResponse<null>> => {
  const response = await apiClient.delete<ApiResponse<null>>(`/pages/${id}`);
  return response.data;
};
