import { Request, Response } from 'express';
import bcrypt from 'bcrypt';
import { prisma } from '../config/database';
import { generateToken } from '../utils/jwt';
import { successResponse, errorResponse } from '../utils/response';
import { logger } from '../utils/logger';

/**
 * 用户注册
 */
export async function register(req: Request, res: Response) {
  try {
    const { email, username, password, role } = req.body;

    // 检查邮箱是否已存在
    const existingUser = await prisma.user.findUnique({
      where: { email },
    });

    if (existingUser) {
      return res.status(400).json(errorResponse('邮箱已被注册'));
    }

    // 检查用户名是否已存在
    const existingUsername = await prisma.user.findUnique({
      where: { username },
    });

    if (existingUsername) {
      return res.status(400).json(errorResponse('用户名已存在'));
    }

    // 加密密码
    const hashedPassword = await bcrypt.hash(password, 10);

    // 创建用户
    const user = await prisma.user.create({
      data: {
        email,
        username,
        password: hashedPassword,
        role: role || 'EDITOR',
        status: 'ACTIVE',
      },
      select: {
        id: true,
        email: true,
        username: true,
        role: true,
        avatar: true,
        status: true,
        createdAt: true,
      },
    });

    // 记录日志
    await prisma.activityLog.create({
      data: {
        userId: user.id,
        action: 'USER_REGISTERED',
        entity: 'User',
        entityId: user.id,
        details: { email, username },
      },
    });

    logger.info(`新用户注册: ${email}`);

    return res.status(201).json(successResponse(user, '注册成功'));
  } catch (error) {
    logger.error('注册失败:', error);
    return res.status(500).json(errorResponse('注册失败'));
  }
}

/**
 * 用户登录
 */
export async function login(req: Request, res: Response) {
  try {
    const { email, password } = req.body;

    // 查找用户
    const user = await prisma.user.findUnique({
      where: { email },
    });

    if (!user) {
      return res.status(401).json(errorResponse('邮箱或密码错误'));
    }

    // 检查用户状态
    if (user.status === 'INACTIVE') {
      return res.status(403).json(errorResponse('账号未激活'));
    }

    if (user.status === 'BANNED') {
      return res.status(403).json(errorResponse('账号已被封禁'));
    }

    // 验证密码
    const isPasswordValid = await bcrypt.compare(password, user.password);

    if (!isPasswordValid) {
      return res.status(401).json(errorResponse('邮箱或密码错误'));
    }

    // 生成 JWT Token
    const token = generateToken({
      userId: user.id,
      email: user.email,
      role: user.role,
    });

    // 记录登录日志
    await prisma.activityLog.create({
      data: {
        userId: user.id,
        action: 'USER_LOGIN',
        entity: 'User',
        entityId: user.id,
        ipAddress: req.ip,
        userAgent: req.headers['user-agent'],
      },
    });

    logger.info(`用户登录: ${email}`);

    return res.json(successResponse({
      token,
      user: {
        id: user.id,
        email: user.email,
        username: user.username,
        role: user.role,
        avatar: user.avatar,
      },
    }, '登录成功'));
  } catch (error) {
    logger.error('登录失败:', error);
    return res.status(500).json(errorResponse('登录失败'));
  }
}

/**
 * 获取当前用户信息
 */
export async function getCurrentUser(req: Request, res: Response) {
  try {
    const userId = req.user!.userId;

    const user = await prisma.user.findUnique({
      where: { id: userId },
      select: {
        id: true,
        email: true,
        username: true,
        role: true,
        avatar: true,
        status: true,
        createdAt: true,
        updatedAt: true,
      },
    });

    if (!user) {
      return res.status(404).json(errorResponse('用户不存在'));
    }

    return res.json(successResponse(user));
  } catch (error) {
    logger.error('获取用户信息失败:', error);
    return res.status(500).json(errorResponse('获取用户信息失败'));
  }
}

/**
 * 修改密码
 */
export async function changePassword(req: Request, res: Response) {
  try {
    const userId = req.user!.userId;
    const { oldPassword, newPassword } = req.body;

    // 获取用户
    const user = await prisma.user.findUnique({
      where: { id: userId },
    });

    if (!user) {
      return res.status(404).json(errorResponse('用户不存在'));
    }

    // 验证旧密码
    const isPasswordValid = await bcrypt.compare(oldPassword, user.password);

    if (!isPasswordValid) {
      return res.status(400).json(errorResponse('旧密码错误'));
    }

    // 加密新密码
    const hashedPassword = await bcrypt.hash(newPassword, 10);

    // 更新密码
    await prisma.user.update({
      where: { id: userId },
      data: { password: hashedPassword },
    });

    // 记录日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'PASSWORD_CHANGED',
        entity: 'User',
        entityId: userId,
      },
    });

    logger.info(`用户修改密码: ${user.email}`);

    return res.json(successResponse(null, '密码修改成功'));
  } catch (error) {
    logger.error('修改密码失败:', error);
    return res.status(500).json(errorResponse('修改密码失败'));
  }
}
