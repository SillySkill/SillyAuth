import apiClient from './client';
import type {
  ApiResponse,
  PaginatedResponse,
  CommissionRecord,
  CommissionListParams,
  CommissionStats,
} from '@/types';

export const getCommissionRecords = async (
  params: CommissionListParams = {}
): Promise<PaginatedResponse<CommissionRecord>> => {
  const response = await apiClient.get<PaginatedResponse<CommissionRecord>>(
    '/commission/records',
    { params }
  );
  return response.data;
};

export const getCommissionStats = async (): Promise<
  ApiResponse<CommissionStats>
> => {
  const response = await apiClient.get<ApiResponse<CommissionStats>>(
    '/commission/stats'
  );
  return response.data;
};
