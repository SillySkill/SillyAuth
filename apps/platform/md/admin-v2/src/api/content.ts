import apiClient from './client';
import type {
  ApiResponse,
  PaginatedResponse,
  Article,
  ArticleCreateRequest,
  ArticleUpdateRequest,
  ArticleListParams,
  Category,
} from '@/types';

export const getArticles = async (
  params: ArticleListParams = {}
): Promise<PaginatedResponse<Article>> => {
  const response = await apiClient.get<PaginatedResponse<Article>>(
    '/cms/articles',
    { params }
  );
  return response.data;
};

export const getArticle = async (
  id: number
): Promise<ApiResponse<Article>> => {
  const response = await apiClient.get<ApiResponse<Article>>(
    `/cms/articles/${id}`
  );
  return response.data;
};

export const createArticle = async (
  data: ArticleCreateRequest
): Promise<ApiResponse<Article>> => {
  const response = await apiClient.post<ApiResponse<Article>>(
    '/cms/articles',
    data
  );
  return response.data;
};

export const updateArticle = async (
  id: number,
  data: ArticleUpdateRequest
): Promise<ApiResponse<Article>> => {
  const response = await apiClient.put<ApiResponse<Article>>(
    `/cms/articles/${id}`,
    data
  );
  return response.data;
};

export const deleteArticle = async (
  id: number
): Promise<ApiResponse<null>> => {
  const response = await apiClient.delete<ApiResponse<null>>(
    `/cms/articles/${id}`
  );
  return response.data;
};

export const getCategories = async (): Promise<ApiResponse<Category[]>> => {
  const response = await apiClient.get<ApiResponse<Category[]>>(
    '/cms/categories'
  );
  return response.data;
};
