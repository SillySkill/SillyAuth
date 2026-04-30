import api from './index';

export interface UserPoint {
  id: number;
  user_id: number;
  username: string;
  email: string;
  avatar_url: string;
  balance: number;
  total_earned: number;
  total_spent: number;
  level: number;
  experience: number;
}

export interface PointTransaction {
  id: number;
  user_id: number;
  username: string;
  transaction_type: string;
  transaction_source: string;
  amount: number;
  balance_before: number;
  balance_after: number;
  description: string;
  created_at: string;
}

export interface PointProduct {
  id: number;
  product_name: string;
  product_type: string;
  description: string;
  points_price: number;
  original_price: number;
  stock: number;
  sold_count: number;
  is_featured: boolean;
  is_active: boolean;
}

export const pointsApi = {
  // User Points
  getUsers: (params?: any) => api.get('/points/users', { params }),
  listUsers: (params?: any) => api.get('/points/users', { params }),
  updateUserPoints: (userId: number, data: any) => api.put(`/points/users/${userId}`, data),
  adjustPoints: (userId: number, data: any) => api.post(`/points/users/${userId}/adjust`, data),

  // Transactions
  getTransactions: (params?: any) => api.get('/points/transactions', { params }),
  listTransactions: (params?: any) => api.get('/points/transactions', { params }),

  // Products
  getProducts: (params?: any) => api.get('/points/mall/products', { params }),
  listProducts: (params?: any) => api.get('/points/mall/products', { params }),
  createProduct: (data: Partial<PointProduct>) => api.post('/points/mall/products', data),
  updateProduct: (id: number, data: Partial<PointProduct>) => api.put(`/points/mall/products/${id}`, data),
  deleteProduct: (id: number) => api.delete(`/points/mall/products/${id}`),

  // Stats
  getStats: () => api.get('/points/stats'),
};
