import apiClient from './client';
import type {
  ApiResponse,
  PaginatedResponse,
  I18nTranslation,
  TranslationCreateRequest,
  TranslationUpdateRequest,
  TranslationListParams,
} from '@/types';

export const getTranslations = async (
  params: TranslationListParams = {}
): Promise<PaginatedResponse<I18nTranslation>> => {
  const response = await apiClient.get<PaginatedResponse<I18nTranslation>>(
    '/i18n/translations',
    { params }
  );
  return response.data;
};

export const createTranslation = async (
  data: TranslationCreateRequest
): Promise<ApiResponse<I18nTranslation>> => {
  const response = await apiClient.post<ApiResponse<I18nTranslation>>(
    '/i18n/translations',
    data
  );
  return response.data;
};

export const updateTranslation = async (
  id: number,
  data: TranslationUpdateRequest
): Promise<ApiResponse<I18nTranslation>> => {
  const response = await apiClient.put<ApiResponse<I18nTranslation>>(
    `/i18n/translations/${id}`,
    data
  );
  return response.data;
};

export const deleteTranslation = async (
  id: number
): Promise<ApiResponse<null>> => {
  const response = await apiClient.delete<ApiResponse<null>>(
    `/i18n/translations/${id}`
  );
  return response.data;
};
