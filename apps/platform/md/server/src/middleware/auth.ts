import { Request, Response, NextFunction } from 'express';
import { verifyToken, JwtPayload } from '../utils/jwt';
import { unauthorizedResponse, forbiddenResponse } from '../utils/response';
import { logger } from '../utils/logger';
import { UserRole } from '@prisma/client';

// 扩展 Express Request 类型
declare global {
  namespace Express {
    interface Request {
      user?: JwtPayload;
    }
  }
}

/**
 * 认证中间件 - 验证 JWT Token
 */
export function authMiddleware(req: Request, res: Response, next: NextFunction) {
  try {
    // 从请求头获取 token
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json(unauthorizedResponse('未提供认证令牌'));
    }

    // 提取 token
    const token = authHeader.substring(7);

    // 验证 token
    const decoded = verifyToken(token);

    // 将用户信息添加到请求对象
    req.user = decoded;

    next();
  } catch (error) {
    logger.error('认证失败:', error);
    return res.status(401).json(unauthorizedResponse('认证令牌无效或已过期'));
  }
}

/**
 * 角色权限中间件 - 验证用户角色
 */
export function roleMiddleware(...allowedRoles: UserRole[]) {
  return (req: Request, res: Response, next: NextFunction) => {
    try {
      const user = req.user;

      if (!user) {
        return res.status(401).json(unauthorizedResponse('未认证'));
      }

      if (!allowedRoles.includes(user.role as UserRole)) {
        return res.status(403).json(
          forbiddenResponse('权限不足')
        );
      }

      next();
    } catch (error) {
      logger.error('权限验证失败:', error);
      return res.status(403).json(forbiddenResponse('权限验证失败'));
    }
  };
}

/**
 * 管理员权限中间件
 */
export const adminMiddleware = roleMiddleware(UserRole.ADMIN);

/**
 * 编辑或管理员权限中间件
 */
export const editorMiddleware = roleMiddleware(UserRole.ADMIN, UserRole.EDITOR);
