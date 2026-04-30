import apiClient from './client';
import type {
  ApiResponse,
  PaginatedResponse,
  Tutorial,
  TutorialCreateRequest,
  TutorialUpdateRequest,
  TutorialListParams,
} from '@/types';

export const getTutorials = async (
  params: TutorialListParams = {}
): Promise<PaginatedResponse<Tutorial>> => {
  const response = await apiClient.get<PaginatedResponse<Tutorial>>(
    '/tutorials',
    { params }
  );
  return response.data;
};

export const getTutorial = async (
  id: number
): Promise<ApiResponse<Tutorial>> => {
  const response = await apiClient.get<ApiResponse<Tutorial>>(
    `/tutorials/${id}`
  );
  return response.data;
};

export const createTutorial = async (
  data: TutorialCreateRequest
): Promise<ApiResponse<Tutorial>> => {
  const response = await apiClient.post<ApiResponse<Tutorial>>(
    '/tutorials',
    data
  );
  return response.data;
};

export const updateTutorial = async (
  id: number,
  data: TutorialUpdateRequest
): Promise<ApiResponse<Tutorial>> => {
  const response = await apiClient.put<ApiResponse<Tutorial>>(
    `/tutorials/${id}`,
    data
  );
  return response.data;
};

export const deleteTutorial = async (
  id: number
): Promise<ApiResponse<null>> => {
  const response = await apiClient.delete<ApiResponse<null>>(
    `/tutorials/${id}`
  );
  return response.data;
};
