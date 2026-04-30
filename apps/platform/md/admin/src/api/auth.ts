import api from './index';

export interface LoginParams {
  email: string;
  password: string;
}

export interface RegisterParams {
  email: string;
  username: string;
  password: string;
}

export interface User {
  id: string;
  email: string;
  username: string;
  role: string;
  avatar?: string;
  status: string;
  createdAt: string;
}

export interface AuthResponse {
  token: string;
  user: User;
}

// 登录
export const login = (params: LoginParams) => {
  return api.post<any, AuthResponse>('/auth/login', params);
};

// 注册
export const register = (params: RegisterParams) => {
  return api.post<any, AuthResponse>('/auth/register', params);
};

// 获取当前用户信息
export const getCurrentUser = () => {
  return api.get<any, User>('/auth/me');
};

// 修改密码
export const changePassword = (params: { oldPassword: string; newPassword: string }) => {
  return api.put('/auth/change-password', params);
};
