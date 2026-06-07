import apiClient from './client';
import type { ApiResponse } from '@/types';

/** A marketplace skill awaiting review */
export interface ReviewSkill {
  id: number;
  skill_id: string;
  name: string;
  description: string | null;
  author_id: number;
  author_username: string;
  category: string;
  type: string;
  version: string;
  status: string;
  price: number;
  tags: string;
  code_content: string | null;
  theme_description: string | null;
  repo_url: string | null;
  source_path: string | null;
  cover_image: string | null;
  package_url: string | null;
  view_count: number;
  download_count: number;
  initial_downloads: number;
  is_featured: boolean;
  published_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface SkillListResponse {
  success: boolean;
  data: {
    items: ReviewSkill[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
  };
}

/** List skills for review with optional status filter */
export const getSkillsForReview = async (
  params: {
    status?: string;
    page?: number;
    limit?: number;
    search?: string;
  } = {}
): Promise<SkillListResponse> => {
  const response = await apiClient.get<SkillListResponse>('/skills/admin/list', {
    params: {
      status: params.status || 'reviewing',
      page: params.page || 1,
      limit: params.limit || 20,
      search: params.search || undefined,
    },
  });
  return response.data;
};

/** Approve a skill */
export const approveSkill = async (
  skillId: number
): Promise<ApiResponse<null>> => {
  const response = await apiClient.post<ApiResponse<null>>(
    `/skills/${skillId}/approve`
  );
  return response.data;
};

/** Skill2 processing status */
export interface Skill2Status {
  skill_id: number;
  status: string;
  total_sensitive: number;
  sensitive_items: Array<{
    marker_type: string;
    content_preview: string;
    line_number: number;
    confidence: number;
    suggested_action: string;
  }>;
  package_url: string | null;
  manifest_url: string | null;
  platform_signature: string | null;
  error_message: string | null;
}

/** Get Skill2 processing status for a skill */
export const getSkill2Status = async (
  skillId: number
): Promise<{ success: boolean; data: Skill2Status }> => {
  const response = await apiClient.get(`/skill2/status/${skillId}`);
  return response.data;
};

/** Update initial download count for a skill */
export const updateInitialDownloads = async (
  skillId: number,
  initialDownloads: number
): Promise<ApiResponse<null>> => {
  const response = await apiClient.put<ApiResponse<null>>(
    `/skills/${skillId}/initial-downloads`,
    { initial_downloads: initialDownloads }
  );
  return response.data;
};

/** Reject a skill */
export const rejectSkill = async (
  skillId: number,
  reason?: string
): Promise<ApiResponse<null>> => {
  const response = await apiClient.post<ApiResponse<null>>(
    `/skills/${skillId}/reject`,
    null,
    { params: { reason: reason || undefined } }
  );
  return response.data;
};
