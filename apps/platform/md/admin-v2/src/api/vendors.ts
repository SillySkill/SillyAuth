import apiClient from './client';
import type {
  ApiResponse,
  PaginatedResponse,
  Vendor,
  VendorCreateRequest,
  VendorUpdateRequest,
  VendorListParams,
} from '@/types';

export const getVendors = async (
  params: VendorListParams = {}
): Promise<PaginatedResponse<Vendor>> => {
  const response = await apiClient.get<PaginatedResponse<Vendor>>('/vendors', {
    params,
  });
  return response.data;
};

export const getVendor = async (id: number): Promise<ApiResponse<Vendor>> => {
  const response = await apiClient.get<ApiResponse<Vendor>>(`/vendors/${id}`);
  return response.data;
};

export const createVendor = async (
  data: VendorCreateRequest
): Promise<ApiResponse<Vendor>> => {
  const response = await apiClient.post<ApiResponse<Vendor>>('/vendors', data);
  return response.data;
};

export const updateVendor = async (
  id: number,
  data: VendorUpdateRequest
): Promise<ApiResponse<Vendor>> => {
  const response = await apiClient.put<ApiResponse<Vendor>>(
    `/vendors/${id}`,
    data
  );
  return response.data;
};

export const deleteVendor = async (
  id: number
): Promise<ApiResponse<null>> => {
  const response = await apiClient.delete<ApiResponse<null>>(
    `/vendors/${id}`
  );
  return response.data;
};
