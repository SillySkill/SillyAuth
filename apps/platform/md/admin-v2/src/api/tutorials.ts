import apiClient from './client';
import type {
  ApiResponse,
  PaginatedResponse,
  Tutorial,
  TutorialCreateRequest,
  TutorialUpdateRequest,
  TutorialListParams,
} from '@/types';

// ---- Chapter Types ----

export interface TutorialChapter {
  id: number;
  tutorial_id: number;
  title: string;
  content: string;
  order: number;
  video_url?: string;
  duration?: number;
  created_at: string;
  updated_at: string;
}

export interface ChapterCreateRequest {
  title: string;
  content: string;
  order: number;
  video_url?: string;
  duration?: number;
}

export interface ChapterUpdateRequest extends Partial<ChapterCreateRequest> {}

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

// ---- Chapter API ----

export const getChapters = async (
  tutorialId: number
): Promise<ApiResponse<TutorialChapter[]>> => {
  const response = await apiClient.get<ApiResponse<TutorialChapter[]>>(
    `/tutorials/${tutorialId}/chapters`
  );
  return response.data;
};

export const createChapter = async (
  tutorialId: number,
  data: ChapterCreateRequest
): Promise<ApiResponse<TutorialChapter>> => {
  const response = await apiClient.post<ApiResponse<TutorialChapter>>(
    `/tutorials/${tutorialId}/chapters`,
    data
  );
  return response.data;
};

export const updateChapter = async (
  tutorialId: number,
  chapterId: number,
  data: ChapterUpdateRequest
): Promise<ApiResponse<TutorialChapter>> => {
  const response = await apiClient.put<ApiResponse<TutorialChapter>>(
    `/tutorials/${tutorialId}/chapters/${chapterId}`,
    data
  );
  return response.data;
};

export const deleteChapter = async (
  tutorialId: number,
  chapterId: number
): Promise<ApiResponse<null>> => {
  const response = await apiClient.delete<ApiResponse<null>>(
    `/tutorials/${tutorialId}/chapters/${chapterId}`
  );
  return response.data;
};
