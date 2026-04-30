import apiClient from './client';
import type {
  ApiResponse,
  PaginatedResponse,
  PaymentAccount,
  PaymentAccountCreateRequest,
  PaymentAccountUpdateRequest,
  CreatorEarning,
  CreatorEarningListParams,
  RevenueStats,
  SettleRequest,
} from '@/types';

// ---- Payment Accounts ----

export const getPaymentAccounts = async (): Promise<
  ApiResponse<PaymentAccount[]>
> => {
  const response = await apiClient.get<ApiResponse<PaymentAccount[]>>(
    '/payment/accounts'
  );
  return response.data;
};

export const createPaymentAccount = async (
  data: PaymentAccountCreateRequest
): Promise<ApiResponse<PaymentAccount>> => {
  const response = await apiClient.post<ApiResponse<PaymentAccount>>(
    '/payment/accounts',
    data
  );
  return response.data;
};

export const updatePaymentAccount = async (
  id: number,
  data: PaymentAccountUpdateRequest
): Promise<ApiResponse<PaymentAccount>> => {
  const response = await apiClient.put<ApiResponse<PaymentAccount>>(
    `/payment/accounts/${id}`,
    data
  );
  return response.data;
};

export const deletePaymentAccount = async (
  id: number
): Promise<ApiResponse<null>> => {
  const response = await apiClient.delete<ApiResponse<null>>(
    `/payment/accounts/${id}`
  );
  return response.data;
};

// ---- Creator Earnings ----

export const getCreatorEarnings = async (
  params: CreatorEarningListParams = {}
): Promise<PaginatedResponse<CreatorEarning>> => {
  const response = await apiClient.get<PaginatedResponse<CreatorEarning>>(
    '/payment/earnings',
    { params }
  );
  return response.data;
};

export const getRevenueStats = async (
  days: number = 30
): Promise<ApiResponse<RevenueStats>> => {
  const response = await apiClient.get<ApiResponse<RevenueStats>>(
    '/payment/revenue-stats',
    { params: { days } }
  );
  return response.data;
};

export const getPendingSettlements =
  async (): Promise<PaginatedResponse<CreatorEarning>> => {
    const response = await apiClient.get<PaginatedResponse<CreatorEarning>>(
      '/payment/pending-settlements'
    );
    return response.data;
  };

export const settleCreator = async (
  userId: number,
  data: SettleRequest
): Promise<ApiResponse<CreatorEarning>> => {
  const response = await apiClient.post<ApiResponse<CreatorEarning>>(
    `/payment/settle/${userId}`,
    data
  );
  return response.data;
};
