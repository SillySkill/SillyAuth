import apiClient from './client';
import type {
  ApiResponse,
  PaginatedResponse,
  PointsProduct,
  PointsProductCreateRequest,
  PointsProductUpdateRequest,
  PointsCategory,
  PointsExchange,
  ExchangeListParams,
  PaginationParams,
} from '@/types';

// ---- Products ----

export const getPointsProducts = async (
  params: PaginationParams = {}
): Promise<PaginatedResponse<PointsProduct>> => {
  const response = await apiClient.get<PaginatedResponse<PointsProduct>>(
    '/points/mall/items',
    { params }
  );
  return response.data;
};

export const createPointsProduct = async (
  data: PointsProductCreateRequest
): Promise<ApiResponse<PointsProduct>> => {
  const response = await apiClient.post<ApiResponse<PointsProduct>>(
    '/points/mall/items',
    data
  );
  return response.data;
};

export const updatePointsProduct = async (
  id: number,
  data: PointsProductUpdateRequest
): Promise<ApiResponse<PointsProduct>> => {
  const response = await apiClient.put<ApiResponse<PointsProduct>>(
    `/points/mall/items/${id}`,
    data
  );
  return response.data;
};

export const deletePointsProduct = async (
  id: number
): Promise<ApiResponse<null>> => {
  const response = await apiClient.delete<ApiResponse<null>>(
    `/points/products/${id}`
  );
  return response.data;
};

// ---- Categories ----

export const getPointsCategories = async (): Promise<
  ApiResponse<PointsCategory[]>
> => {
  const response = await apiClient.get<ApiResponse<PointsCategory[]>>(
    '/points/categories'
  );
  return response.data;
};

// ---- Exchanges ----

export const getAllExchanges = async (
  params: ExchangeListParams = {}
): Promise<PaginatedResponse<PointsExchange>> => {
  const response = await apiClient.get<PaginatedResponse<PointsExchange>>(
    '/points/mall/all-exchanges',
    { params }
  );
  return response.data;
};

export const updateExchangeStatus = async (
  id: number,
  data: { status: string; tracking_number?: string }
): Promise<ApiResponse<PointsExchange>> => {
  const response = await apiClient.put<ApiResponse<PointsExchange>>(
    `/points/mall/exchanges/${id}/status`,
    data
  );
  return response.data;
};
