import api from './index';

export interface RevenueStats {
  total_orders: number;
  total_revenue: number;
  total_commission: number;
  total_earnings: number;
}

export interface RevenueStatsResponse {
  success: boolean;
  data: RevenueStats;
}

export const paymentApi = {
  getRevenueStats: (params?: any) => api.get('/payment/stats/revenue', { params }),
  getOrders: (params?: any) => api.get('/payment/orders', { params }),
  getOrder: (id: number) => api.get(`/payment/orders/${id}`),
};
