import api from './index';

export interface CommissionSetting {
  id: number;
  scope: string;
  scope_id: number | null;
  commission_rate: number;
  min_commission_rate: number;
  max_commission_rate: number;
  creator_share_rate: number;
  is_custom: boolean;
  is_active: boolean;
  valid_from: string | null;
  valid_until: string | null;
  description: string;
  created_at: string;
}

export const commissionApi = {
  list: () => api.get('/payment/commission/settings'),
  get: (id: number) => api.get(`/payment/commission/settings/${id}`),
  create: (data: Partial<CommissionSetting>) => api.post('/payment/commission/settings', data),
  update: (id: number, data: Partial<CommissionSetting>) => api.put(`/payment/commission/settings/${id}`, data),
  delete: (id: number) => api.delete(`/payment/commission/settings/${id}`),
};
