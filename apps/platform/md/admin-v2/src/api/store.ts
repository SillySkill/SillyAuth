import apiClient from './client';
import type { ApiResponse, PaginatedResponse, PaginationParams } from '@/types';

// ---- Collection Types ----

export interface Collection {
  id: number;
  collection_key: string;
  name_zh: string;
  name_en?: string;
  description?: string;
  logo_url?: string;
  image_url?: string;
  theme_config?: Record<string, unknown>;
  sort_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CollectionCreateRequest {
  name_zh: string;
  name_en?: string;
  collection_key?: string;
  description?: string;
  logo_url?: string;
  image_url?: string;
  theme_config?: Record<string, unknown>;
  sort_order?: number;
  is_active?: boolean;
}

export interface CollectionUpdateRequest
  extends Partial<CollectionCreateRequest> {}

// ---- Product Types ----

export interface Product {
  id: number;
  collection_id: number;
  product_key: string;
  name_zh: string;
  name_en?: string;
  description_zh?: string;
  description_en?: string;
  image_url?: string;
  gallery?: string[];
  price: number;
  original_price?: number;
  stock_count: number;
  sold_count: number;
  specifications?: string;
  is_active: boolean;
  sort_order: number;
  created_at: string;
  updated_at: string;
  collection_name?: string;
}

export interface ProductCreateRequest {
  collection_id?: number;
  name_zh: string;
  name_en?: string;
  product_key?: string;
  description_zh?: string;
  description_en?: string;
  image_url?: string;
  gallery?: string[];
  price: number;
  original_price?: number;
  stock_count?: number;
  specifications?: string;
  is_active?: boolean;
  sort_order?: number;
}

export interface ProductUpdateRequest
  extends Partial<ProductCreateRequest> {}

// ---- Order Types ----

export interface StoreOrder {
  id: number;
  order_no: string;
  user_id: number;
  collection_id: number;
  total_amount: number;
  status: string;
  payment_method?: string;
  payment_no?: string;
  shipping_name?: string;
  shipping_phone?: string;
  shipping_address?: string;
  created_at: string;
  updated_at?: string;
}

export interface StoreOrderItem {
  id: number;
  order_id: number;
  product_id: number;
  product_name: string;
  quantity: number;
  unit_price: number;
  subtotal: number;
}

export interface OrderDetail {
  order: StoreOrder;
  items: StoreOrderItem[];
}

export interface OrderStatusUpdateRequest {
  status: string;
  reason?: string;
}

// ---- Inventory Types ----

export interface InventoryItem {
  id: number;
  product_key: string;
  name_zh: string;
  name_en?: string;
  stock_count: number;
  sold_count: number;
  price: number;
  original_price?: number;
  is_active: boolean;
  collection_name?: string;
  collection_key?: string;
}

export interface StockLog {
  id: number;
  product_id: number;
  change_type: string;
  change_quantity: number;
  stock_before: number;
  stock_after: number;
  reference_no?: string;
  external_ref?: string;
  source: string;
  note?: string;
  operator_id?: number;
  operator_name?: string;
  sync_status: string;
  created_at: string;
}

export interface StockAdjustRequest {
  change_type: string;
  quantity: number;
  note?: string;
  reference_no?: string;
  operator_id?: number;
}

// ---- Stats Types ----

export interface StoreStats {
  total_collections: number;
  active_collections: number;
  total_products: number;
  active_products: number;
  total_orders: number;
  pending_orders: number;
  total_revenue: number;
}

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

// ---- Orders ----

export const getOrders = async (
  params: PaginationParams & { status?: string; order_no?: string; collection_id?: number }
): Promise<PaginatedResponse<StoreOrder>> => {
  const response = await apiClient.get<PaginatedResponse<StoreOrder>>(
    '/store/admin/orders',
    { params }
  );
  return response.data;
};

export const getOrderDetail = async (
  orderNo: string
): Promise<ApiResponse<OrderDetail>> => {
  const response = await apiClient.get<ApiResponse<OrderDetail>>(
    `/store/admin/orders/${orderNo}/detail`
  );
  return response.data;
};

export const updateOrderStatus = async (
  orderNo: string,
  data: OrderStatusUpdateRequest
): Promise<ApiResponse<StoreOrder>> => {
  const response = await apiClient.put<ApiResponse<StoreOrder>>(
    `/store/admin/orders/${orderNo}/status`,
    data
  );
  return response.data;
};

// ---- Inventory ----

export const getInventory = async (
  params: PaginationParams & { search?: string; low_stock_only?: boolean; collection_key?: string }
): Promise<PaginatedResponse<InventoryItem>> => {
  const response = await apiClient.get<PaginatedResponse<InventoryItem>>(
    '/store/admin/inventory',
    { params }
  );
  return response.data;
};

export const adjustStock = async (
  productId: number,
  data: StockAdjustRequest
): Promise<ApiResponse<Record<string, unknown>>> => {
  const response = await apiClient.post<ApiResponse<Record<string, unknown>>>(
    `/store/admin/products/${productId}/stock-adjust`,
    data
  );
  return response.data;
};

export const getStockLogs = async (
  productId: number,
  params: PaginationParams = {}
): Promise<PaginatedResponse<StockLog>> => {
  const response = await apiClient.get<PaginatedResponse<StockLog>>(
    `/store/admin/products/${productId}/stock-logs`,
    { params }
  );
  return response.data;
};

// ---- Stats ----

export const getStoreStats = async (): Promise<ApiResponse<StoreStats>> => {
  const response = await apiClient.get<ApiResponse<StoreStats>>(
    '/store/admin/stats'
  );
  return response.data;
};
