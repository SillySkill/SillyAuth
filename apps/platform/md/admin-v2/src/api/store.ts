import apiClient from './client';
import type { ApiResponse, PaginatedResponse, PaginationParams } from '@/types';

// ---- Collection Types ----

export interface Collection {
  id: number;
  name: string;
  slug: string;
  description?: string;
  image_url?: string;
  sort_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CollectionCreateRequest {
  name: string;
  slug?: string;
  description?: string;
  image_url?: string;
  sort_order?: number;
  is_active?: boolean;
}

export interface CollectionUpdateRequest
  extends Partial<CollectionCreateRequest> {}

// ---- Product Types ----

export interface Product {
  id: number;
  name: string;
  slug: string;
  description: string;
  price: number;
  currency: string;
  images?: string[];
  collection_id?: number;
  collection?: Collection;
  stock: number;
  is_active: boolean;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface ProductCreateRequest {
  name: string;
  slug?: string;
  description: string;
  price: number;
  currency?: string;
  images?: string[];
  collection_id?: number;
  stock?: number;
  is_active?: boolean;
  sort_order?: number;
}

export interface ProductUpdateRequest
  extends Partial<ProductCreateRequest> {}

// ---- Collections CRUD ----

export const getCollections = async (
  params: PaginationParams = {}
): Promise<PaginatedResponse<Collection>> => {
  const response = await apiClient.get<PaginatedResponse<Collection>>(
    '/store/admin/collections',
    { params }
  );
  return response.data;
};

export const createCollection = async (
  data: CollectionCreateRequest
): Promise<ApiResponse<Collection>> => {
  const response = await apiClient.post<ApiResponse<Collection>>(
    '/store/admin/collections',
    data
  );
  return response.data;
};

export const updateCollection = async (
  id: number,
  data: CollectionUpdateRequest
): Promise<ApiResponse<Collection>> => {
  const response = await apiClient.put<ApiResponse<Collection>>(
    `/store/admin/collections/${id}`,
    data
  );
  return response.data;
};

export const deleteCollection = async (
  id: number
): Promise<ApiResponse<null>> => {
  const response = await apiClient.delete<ApiResponse<null>>(
    `/store/admin/collections/${id}`
  );
  return response.data;
};

// ---- Products CRUD ----

export const getProducts = async (
  params: PaginationParams = {}
): Promise<PaginatedResponse<Product>> => {
  const response = await apiClient.get<PaginatedResponse<Product>>(
    '/store/admin/products',
    { params }
  );
  return response.data;
};

export const createProduct = async (
  data: ProductCreateRequest
): Promise<ApiResponse<Product>> => {
  const response = await apiClient.post<ApiResponse<Product>>(
    '/store/admin/products',
    data
  );
  return response.data;
};

export const updateProduct = async (
  id: number,
  data: ProductUpdateRequest
): Promise<ApiResponse<Product>> => {
  const response = await apiClient.put<ApiResponse<Product>>(
    `/store/admin/products/${id}`,
    data
  );
  return response.data;
};

export const deleteProduct = async (
  id: number
): Promise<ApiResponse<null>> => {
  const response = await apiClient.delete<ApiResponse<null>>(
    `/store/admin/products/${id}`
  );
  return response.data;
};
