import apiClient from './client';
import type {
  ApiResponse,
  PaginatedResponse,
  Download,
  DownloadCreateRequest,
  DownloadUpdateRequest,
  DownloadListParams,
} from '@/types';

export const getDownloads = async (
  params: DownloadListParams = {}
): Promise<PaginatedResponse<Download>> => {
  const response = await apiClient.get<PaginatedResponse<Download>>(
    '/downloads',
    { params }
  );
  return response.data;
};

export const getDownload = async (
  id: number
): Promise<ApiResponse<Download>> => {
  const response = await apiClient.get<ApiResponse<Download>>(
    `/downloads/${id}`
  );
  return response.data;
};

export const createDownload = async (
  data: DownloadCreateRequest
): Promise<ApiResponse<Download>> => {
  const response = await apiClient.post<ApiResponse<Download>>(
    '/downloads',
    data
  );
  return response.data;
};

export const updateDownload = async (
  id: number,
  data: DownloadUpdateRequest
): Promise<ApiResponse<Download>> => {
  const response = await apiClient.put<ApiResponse<Download>>(
    `/downloads/${id}`,
    data
  );
  return response.data;
};

export const deleteDownload = async (
  id: number
): Promise<ApiResponse<null>> => {
  const response = await apiClient.delete<ApiResponse<null>>(
    `/downloads/${id}`
  );
  return response.data;
};
