import api from './index';

export interface Download {
  id: number;
  download_key: string;
  slug: string;
  title_zh_CN: string;
  title_en: string;
  description_zh_CN: string;
  category: string;
  subcategory: string;
  version: string;
  platform: string;
  file_name: string;
  file_url: string;
  file_size: number;
  file_type: string;
  download_count: number;
  view_count: number;
  featured: boolean;
  is_official: boolean;
  is_published: boolean;
  created_at: string;
}

export interface DownloadListResponse {
  success: boolean;
  data: Download[];
  total: number;
  page: number;
  page_size: number;
}

export const downloadApi = {
  list: (params?: any) => api.get('/content/downloads/', { params }),
  get: (id: number) => api.get(`/content/downloads/${id}`),
  create: (data: Partial<Download>) => api.post('/content/downloads/', data),
  update: (id: number, data: Partial<Download>) => api.put(`/content/downloads/${id}`, data),
  delete: (id: number) => api.delete(`/content/downloads/${id}`),
};
