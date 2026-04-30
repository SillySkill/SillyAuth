import { Request, Response } from 'express';
import bcrypt from 'bcrypt';
import { prisma } from '../config/database';
import { successResponse, errorResponse, notFoundResponse, paginatedResponse } from '../utils/response';
import { logger } from '../utils/logger';
import { config } from '../config';

/**
 * 获取用户列表
 */
export async function getUsers(req: Request, res: Response) {
  try {
    const page = parseInt(req.query.page as string) || config.pagination.defaultPage;
    const limit = parseInt(req.query.limit as string) || config.pagination.defaultLimit;
    const role = req.query.role as string;
    const status = req.query.status as string;
    const search = req.query.search as string;

    const skip = (page - 1) * limit;

    const where: any = {};

    if (role) {
      where.role = role;
    }

    if (status) {
      where.status = status;
    }

    if (search) {
      where.OR = [
        { email: { contains: search } },
        { username: { contains: search } },
      ];
    }

    const total = await prisma.user.count({ where });

    const users = await prisma.user.findMany({
      where,
      skip,
      take: limit,
      orderBy: { createdAt: 'desc' },
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

    return res.json(paginatedResponse(users, page, limit, total));
  } catch (error) {
    logger.error('获取用户列表失败:', error);
    return res.status(500).json(errorResponse('获取用户列表失败'));
  }
}

/**
 * 获取单个用户
 */
export async function getUserById(req: Request, res: Response) {
  try {
    const { id } = req.params;

    const user = await prisma.user.findUnique({
      where: { id },
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
      return res.status(404).json(notFoundResponse('用户'));
    }

    return res.json(successResponse(user));
  } catch (error) {
    logger.error('获取用户失败:', error);
    return res.status(500).json(errorResponse('获取用户失败'));
  }
}

/**
 * 创建用户
 */
export async function createUser(req: Request, res: Response) {
  try {
    const currentUserId = req.user!.userId;
    const { email, username, password, role, avatar } = req.body;

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

    const user = await prisma.user.create({
      data: {
        email,
        username,
        password: hashedPassword,
        role: role || 'EDITOR',
        avatar,
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

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId: currentUserId,
        action: 'USER_CREATED',
        entity: 'User',
        entityId: user.id,
        details: { email, username, role: user.role },
      },
    });

    logger.info(`创建用户: ${email}`);

    return res.status(201).json(successResponse(user, '用户创建成功'));
  } catch (error) {
    logger.error('创建用户失败:', error);
    return res.status(500).json(errorResponse('创建用户失败'));
  }
}

/**
 * 更新用户
 */
export async function updateUser(req: Request, res: Response) {
  try {
    const currentUserId = req.user!.userId;
    const { id } = req.params;
    const { email, username, password, role, avatar, status } = req.body;

    const data: any = {};

    if (email) data.email = email;
    if (username) data.username = username;
    if (password) data.password = await bcrypt.hash(password, 10);
    if (role) data.role = role;
    if (avatar !== undefined) data.avatar = avatar;
    if (status) data.status = status;

    const user = await prisma.user.update({
      where: { id },
      data,
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

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId: currentUserId,
        action: 'USER_UPDATED',
        entity: 'User',
        entityId: user.id,
        details: { email: user.email, role: user.role },
      },
    });

    logger.info(`更新用户: ${user.email}`);

    return res.json(successResponse(user, '用户更新成功'));
  } catch (error) {
    logger.error('更新用户失败:', error);
    return res.status(500).json(errorResponse('更新用户失败'));
  }
}

/**
 * 删除用户
 */
export async function deleteUser(req: Request, res: Response) {
  try {
    const currentUserId = req.user!.userId;
    const { id } = req.params;

    // 不能删除自己
    if (id === currentUserId) {
      return res.status(400).json(errorResponse('不能删除自己'));
    }

    const user = await prisma.user.findUnique({
      where: { id },
    });

    if (!user) {
      return res.status(404).json(notFoundResponse('用户'));
    }

    await prisma.user.delete({
      where: { id },
    });

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId: currentUserId,
        action: 'USER_DELETED',
        entity: 'User',
        entityId: id,
        details: { email: user.email },
      },
    });

    logger.info(`删除用户: ${user.email}`);

    return res.json(successResponse(null, '用户删除成功'));
  } catch (error) {
    logger.error('删除用户失败:', error);
    return res.status(500).json(errorResponse('删除用户失败'));
  }
}

/**
 * 更新用户状态
 */
export async function updateUserStatus(req: Request, res: Response) {
  try {
    const currentUserId = req.user!.userId;
    const { id } = req.params;
    const { status } = req.body;

    const user = await prisma.user.update({
      where: { id },
      data: { status },
      select: {
        id: true,
        email: true,
        username: true,
        status: true,
      },
    });

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId: currentUserId,
        action: 'USER_STATUS_UPDATED',
        entity: 'User',
        entityId: user.id,
        details: { email: user.email, status },
      },
    });

    logger.info(`更新用户状态: ${user.email} -> ${status}`);

    return res.json(successResponse(user, '用户状态更新成功'));
  } catch (error) {
    logger.error('更新用户状态失败:', error);
    return res.status(500).json(errorResponse('更新用户状态失败'));
  }
}
