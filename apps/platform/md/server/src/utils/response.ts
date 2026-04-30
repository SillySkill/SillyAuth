/**
 * 统一响应格式工具类
 */

export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
  meta?: {
    page?: number;
    limit?: number;
    total?: number;
    totalPages?: number;
  };
}

export type PaginationParams = {
  page?: number;
  limit?: number;
};

/**
 * 成功响应
 */
export function successResponse<T>(data: T, message = '操作成功'): ApiResponse<T> {
  return {
    success: true,
    message,
    data,
  };
}

/**
 * 分页响应
 */
export function paginatedResponse<T>(
  data: T[],
  page: number,
  limit: number,
  total: number,
  message = '获取成功'
): ApiResponse<T[]> {
  return {
    success: true,
    message,
    data,
    meta: {
      page,
      limit,
      total,
      totalPages: Math.ceil(total / limit),
    },
  };
}

/**
 * 错误响应
 */
export function errorResponse(message: string, error?: string): ApiResponse {
  return {
    success: false,
    message,
    error,
  };
}

/**
 * 验证错误响应
 */
export function validationErrorResponse(errors: Record<string, string[]>): ApiResponse {
  return {
    success: false,
    message: '数据验证失败',
    error: JSON.stringify(errors),
  };
}

/**
 * 未授权响应
 */
export function unauthorizedResponse(message = '未授权访问'): ApiResponse {
  return {
    success: false,
    message,
    error: 'UNAUTHORIZED',
  };
}

/**
 * 禁止访问响应
 */
export function forbiddenResponse(message = '无权访问'): ApiResponse {
  return {
    success: false,
    message,
    error: 'FORBIDDEN',
  };
}

/**
 * 未找到响应
 */
export function notFoundResponse(resource = '资源'): ApiResponse {
  return {
    success: false,
    message: `${resource}不存在`,
    error: 'NOT_FOUND',
  };
}
