import { Request, Response, NextFunction } from 'express';
import { logger } from '../utils/logger';
import { Prisma } from '@prisma/client';

/**
 * 全局错误处理中间件
 */
export function errorHandler(
  error: Error,
  req: Request,
  res: Response,
  next: NextFunction
) {
  logger.error('错误:', {
    message: error.message,
    stack: error.stack,
    url: req.url,
    method: req.method,
  });

  // Prisma 错误处理
  if (error instanceof Prisma.PrismaClientKnownRequestError) {
    // 唯一约束冲突
    if (error.code === 'P2002') {
      return res.status(400).json({
        success: false,
        message: '数据已存在',
        error: 'UNIQUE_CONSTRAINT',
      });
    }

    // 记录不存在
    if (error.code === 'P2025') {
      return res.status(404).json({
        success: false,
        message: '记录不存在',
        error: 'NOT_FOUND',
      });
    }

    // 外键约束
    if (error.code === 'P2003') {
      return res.status(400).json({
        success: false,
        message: '关联数据不存在',
        error: 'FOREIGN_KEY_CONSTRAINT',
      });
    }
  }

  // 验证错误
  if (error.name === 'ValidationError') {
    return res.status(400).json({
      success: false,
      message: '数据验证失败',
      error: error.message,
    });
  }

  // JWT 错误
  if (error.name === 'JsonWebTokenError') {
    return res.status(401).json({
      success: false,
      message: '认证令牌无效',
      error: 'INVALID_TOKEN',
    });
  }

  if (error.name === 'TokenExpiredError') {
    return res.status(401).json({
      success: false,
      message: '认证令牌已过期',
      error: 'TOKEN_EXPIRED',
    });
  }

  // 默认错误响应
  return res.status(500).json({
    success: false,
    message: process.env.NODE_ENV === 'development' ? error.message : '服务器内部错误',
    error: 'INTERNAL_SERVER_ERROR',
  });
}

/**
 * 404 处理中间件
 */
export function notFoundHandler(req: Request, res: Response) {
  res.status(404).json({
    success: false,
    message: '请求的资源不存在',
    error: 'NOT_FOUND',
    path: req.url,
  });
}
