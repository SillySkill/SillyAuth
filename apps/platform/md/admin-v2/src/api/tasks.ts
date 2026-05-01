import apiClient from './client';
import type { ApiResponse, PaginatedResponse, PaginationParams } from '@/types';

// ---- Task Definition Types ----

export interface TaskDefinition {
  id: number;
  name: string;
  description: string;
  points_reward: number;
  action_type: string;
  action_config?: Record<string, unknown>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskDefinitionCreateRequest {
  name: string;
  description: string;
  points_reward: number;
  action_type: string;
  action_config?: Record<string, unknown>;
  is_active?: boolean;
}

export interface TaskDefinitionUpdateRequest
  extends Partial<TaskDefinitionCreateRequest> {}

// ---- Achievement Types ----

export interface Achievement {
  id: number;
  name: string;
  description: string;
  icon?: string;
  badge_image?: string;
  criteria_type: string;
  criteria_value: number;
  points_reward: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AchievementCreateRequest {
  name: string;
  description: string;
  icon?: string;
  badge_image?: string;
  criteria_type: string;
  criteria_value: number;
  points_reward: number;
  is_active?: boolean;
}

export interface AchievementUpdateRequest
  extends Partial<AchievementCreateRequest> {}

// ---- Task Definitions CRUD ----

export const getTaskDefinitions = async (
  params: PaginationParams = {}
): Promise<PaginatedResponse<TaskDefinition>> => {
  const response = await apiClient.get<PaginatedResponse<TaskDefinition>>(
    '/tasks/definitions',
    { params }
  );
  return response.data;
};

export const createTaskDefinition = async (
  data: TaskDefinitionCreateRequest
): Promise<ApiResponse<TaskDefinition>> => {
  const response = await apiClient.post<ApiResponse<TaskDefinition>>(
    '/tasks/definitions',
    data
  );
  return response.data;
};

export const updateTaskDefinition = async (
  id: number,
  data: TaskDefinitionUpdateRequest
): Promise<ApiResponse<TaskDefinition>> => {
  const response = await apiClient.put<ApiResponse<TaskDefinition>>(
    `/tasks/definitions/${id}`,
    data
  );
  return response.data;
};

export const deleteTaskDefinition = async (
  id: number
): Promise<ApiResponse<null>> => {
  const response = await apiClient.delete<ApiResponse<null>>(
    `/tasks/definitions/${id}`
  );
  return response.data;
};

// ---- Achievements CRUD ----

export const getAchievements = async (
  params: PaginationParams = {}
): Promise<PaginatedResponse<Achievement>> => {
  const response = await apiClient.get<PaginatedResponse<Achievement>>(
    '/tasks/achievements',
    { params }
  );
  return response.data;
};

export const createAchievement = async (
  data: AchievementCreateRequest
): Promise<ApiResponse<Achievement>> => {
  const response = await apiClient.post<ApiResponse<Achievement>>(
    '/tasks/achievements',
    data
  );
  return response.data;
};

export const updateAchievement = async (
  id: number,
  data: AchievementUpdateRequest
): Promise<ApiResponse<Achievement>> => {
  const response = await apiClient.put<ApiResponse<Achievement>>(
    `/tasks/achievements/${id}`,
    data
  );
  return response.data;
};

export const deleteAchievement = async (
  id: number
): Promise<ApiResponse<null>> => {
  const response = await apiClient.delete<ApiResponse<null>>(
    `/tasks/achievements/${id}`
  );
  return response.data;
};
