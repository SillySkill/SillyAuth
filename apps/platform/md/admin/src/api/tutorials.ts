import api from './index';

export interface Tutorial {
  id: number;
  tutorial_key: string;
  slug: string;
  title_zh_CN: string;
  title_en: string;
  description_zh_CN: string;
  category: string;
  subcategory: string;
  difficulty: string;
  thumbnail: string;
  video_url: string;
  video_type: string;
  video_duration: number;
  view_count: number;
  like_count: number;
  featured: boolean;
  is_published: boolean;
  created_at: string;
}

export interface TutorialListResponse {
  success: boolean;
  data: Tutorial[];
  total: number;
  page: number;
  page_size: number;
}

export const tutorialApi = {
  list: (params?: any) => api.get('/content/tutorials/', { params }),
  get: (id: number) => api.get(`/content/tutorials/${id}`),
  create: (data: Partial<Tutorial>) => api.post('/content/tutorials/', data),
  update: (id: number, data: Partial<Tutorial>) => api.put(`/content/tutorials/${id}`, data),
  delete: (id: number) => api.delete(`/content/tutorials/${id}`),
};
