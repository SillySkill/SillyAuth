import apiClient from './client';
import type {
  ApiResponse,
  DashboardOverview,
  DashboardStats,
  RecentActivity,
} from '@/types';

export const getStats = async (
  days: number = 30
): Promise<ApiResponse<DashboardStats>> => {
  const response = await apiClient.get<ApiResponse<DashboardStats>>(
    '/dashboard/stats',
    { params: { days } }
  );
  return response.data;
};

export const getOverview = async (): Promise<
  ApiResponse<DashboardOverview>
> => {
  const response = await apiClient.get<ApiResponse<DashboardOverview>>(
    '/dashboard/overview'
  );
  return response.data;
};

export const getRecentActivity = async (
  limit: number = 20
): Promise<ApiResponse<RecentActivity[]>> => {
  const response = await apiClient.get<ApiResponse<RecentActivity[]>>(
    '/dashboard/activity',
    { params: { limit } }
  );
  return response.data;
};
