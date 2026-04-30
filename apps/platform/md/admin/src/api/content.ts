import api from './index';

export interface Content {
  id: string;
  key: string;
  type: string;
  title: string;
  content: string;
  metadata?: any;
  language: string;
  status: string;
  seo?: any;
  createdAt: string;
  updatedAt: string;
}

export interface ContentListResponse {
  success: boolean;
  data: Content[];
  meta?: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// 获取内容列表
export const getContents = (params?: any) => {
  return api.get<any, ContentListResponse>('/content', { params });
};

// 获取单个内容
export const getContentById = (id: string) => {
  return api.get<any, { success: boolean; data: Content }>(`/content/${id}`);
};

// 根据key获取内容
export const getContentByKey = (key: string, language?: string) => {
  return api.get<any, { success: boolean; data: Content }>(`/content/key/${key}`, {
    params: { language },
  });
};

// 创建内容
export const createContent = (data: Partial<Content>) => {
  return api.post<any, { success: boolean; data: Content; message: string }>('/content', data);
};

// 更新内容
export const updateContent = (id: string, data: Partial<Content>) => {
  return api.put<any, { success: boolean; data: Content; message: string }>(`/content/${id}`, data);
};

// 删除内容
export const deleteContent = (id: string) => {
  return api.delete<any, { success: boolean; message: string }>(`/content/${id}`);
};

// 发布内容
export const publishContent = (id: string) => {
  return api.put<any, { success: boolean; data: Content; message: string }>(
    `/content/${id}/publish`
  );
};

// 获取内容版本历史
export const getContentVersions = (id: string, params?: any) => {
  return api.get<any, ContentListResponse>(`/content/${id}/versions`, { params });
};
