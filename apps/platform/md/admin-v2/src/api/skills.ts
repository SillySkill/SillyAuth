import apiClient from './client';
import type {
  ApiResponse,
  PaginatedResponse,
  Skill,
  SkillCreateRequest,
  SkillUpdateRequest,
  SkillListParams,
} from '@/types';

export const getSkills = async (
  params: SkillListParams = {}
): Promise<PaginatedResponse<Skill>> => {
  const response = await apiClient.get<PaginatedResponse<Skill>>('/skills', {
    params,
  });
  return response.data;
};

export const getSkill = async (id: number): Promise<ApiResponse<Skill>> => {
  const response = await apiClient.get<ApiResponse<Skill>>(`/skills/${id}`);
  return response.data;
};

export const createSkill = async (
  data: SkillCreateRequest
): Promise<ApiResponse<Skill>> => {
  const response = await apiClient.post<ApiResponse<Skill>>('/skills', data);
  return response.data;
};

export const updateSkill = async (
  id: number,
  data: SkillUpdateRequest
): Promise<ApiResponse<Skill>> => {
  const response = await apiClient.put<ApiResponse<Skill>>(
    `/skills/${id}`,
    data
  );
  return response.data;
};

export const deleteSkill = async (id: number): Promise<ApiResponse<null>> => {
  const response = await apiClient.delete<ApiResponse<null>>(`/skills/${id}`);
  return response.data;
};
