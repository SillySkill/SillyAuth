import api from './index';

export interface DashboardStats {
  content: {
    total: number;
    published: number;
    draft: number;
  };
  navigation: {
    total: number;
  };
  carousel: {
    total: number;
    active: number;
  };
  skill: {
    total: number;
  };
  vendor: {
    total: number;
  };
  user: {
    total: number;
    active: number;
  };
  recentActivity: any[];
}

// 获取仪表盘统计
export const getDashboardStats = (params?: any) => {
  return api.get<any, { success: boolean; data: DashboardStats }>('/dashboard/stats', { params });
};

// 获取内容趋势
export const getContentTrend = () => {
  return api.get<any, { success: boolean; data: any[] }>('/dashboard/trend');
};

// 获取最近修改的内容
export const getRecentContent = (params?: any) => {
  return api.get<any, { success: boolean; data: any[] }>('/dashboard/recent', { params });
};

// 获取操作日志
export const getActivityLogs = (params?: any) => {
  return api.get<any, { success: boolean; data: any[]; meta?: any }>('/dashboard/logs', { params });
};
