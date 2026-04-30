/**
 * 傻福虾群组控制器
 * 处理群组相关的业务逻辑
 */

import { Request, Response } from 'express';
import { PrismaClient, Prisma } from '@prisma/client';

const prisma = new PrismaClient();

// 获取所有活跃群组
export const getGroups = async (req: Request, res: Response): Promise<void> => {
  try {
    const groups = await prisma.shrimpGroup.findMany({
      where: { isActive: true },
      orderBy: { sortOrder: 'asc' },
      include: {
        _count: {
          select: { members: true }
        }
      }
    });

    // 格式化返回数据
    const formattedGroups = groups.map(group => ({
      id: group.id,
      name: group.name,
      groupKey: group.groupKey,
      description: group.description,
      maxMembers: group.maxMembers,
      currentMembers: group._count.members,
      icon: group.icon,
      color: group.color,
      isActive: group.isActive
    }));

    res.json({
      success: true,
      data: formattedGroups
    });
  } catch (error) {
    console.error('获取群组列表失败:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'GET_GROUPS_FAILED',
        message: '获取群组列表失败'
      }
    });
  }
};

// 获取用户所在的群组
export const getUserGroups = async (req: Request, res: Response): Promise<void> => {
  try {
    const userId = (req as any).user?.id;
    if (!userId) {
      res.status(401).json({
        success: false,
        error: { code: 'UNAUTHORIZED', message: '请先登录' }
      });
      return;
    }

    const memberships = await prisma.shrimpGroupMember.findMany({
      where: {
        userId,
        isActive: true,
        group: { isActive: true }
      },
      include: {
        group: true
      }
    });

    const groups = memberships.map(m => ({
      id: m.group.id,
      name: m.group.name,
      groupKey: m.group.groupKey,
      description: m.group.description,
      nickname: m.nickname,
      joinTime: m.joinTime,
      icon: m.group.icon,
      color: m.group.color
    }));

    res.json({
      success: true,
      data: groups
    });
  } catch (error) {
    console.error('获取用户群组失败:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'GET_USER_GROUPS_FAILED',
        message: '获取用户群组失败'
      }
    });
  }
};

// 随机加入一个群组
export const joinRandomGroup = async (req: Request, res: Response): Promise<void> => {
  try {
    const userId = (req as any).user?.id;
    if (!userId) {
      res.status(401).json({
        success: false,
        error: { code: 'UNAUTHORIZED', message: '请先登录' }
      });
      return;
    }

    // 检查用户是否已在某个群组
    const existingMembership = await prisma.shrimpGroupMember.findFirst({
      where: { userId, isActive: true }
    });

    if (existingMembership) {
      res.status(400).json({
        success: false,
        error: { code: 'ALREADY_IN_GROUP', message: '您已经在某个群组中' }
      });
      return;
    }

    // 获取还有名额的群组
    const availableGroups = await prisma.shrimpGroup.findMany({
      where: {
        isActive: true,
        // 使用原生查询来过滤还有名额的群组
      },
      orderBy: { sortOrder: 'asc' }
    });

    if (availableGroups.length === 0) {
      res.status(400).json({
        success: false,
        error: { code: 'NO_AVAILABLE_GROUPS', message: '暂无可加入的群组' }
      });
      return;
    }

    // 随机选择一个群组
    const randomIndex = Math.floor(Math.random() * availableGroups.length);
    const selectedGroup = availableGroups[randomIndex];

    // 创建群组成员关系
    const membership = await prisma.shrimpGroupMember.create({
      data: {
        userId,
        groupId: selectedGroup.id,
        nickname: (req as any).user?.username || '新虾友'
      },
      include: {
        group: true
      }
    });

    res.json({
      success: true,
      data: {
        id: membership.group.id,
        name: membership.group.name,
        groupKey: membership.group.groupKey,
        description: membership.group.description,
        icon: membership.group.icon,
        color: membership.group.color,
        joinTime: membership.joinTime
      }
    });
  } catch (error) {
    console.error('加入群组失败:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'JOIN_GROUP_FAILED',
        message: '加入群组失败'
      }
    });
  }
};

// 获取群组成员列表
export const getGroupMembers = async (req: Request, res: Response): Promise<void> => {
  try {
    const { groupKey } = req.params;

    const group = await prisma.shrimpGroup.findUnique({
      where: { groupKey }
    });

    if (!group) {
      res.status(404).json({
        success: false,
        error: { code: 'GROUP_NOT_FOUND', message: '群组不存在' }
      });
      return;
    }

    const members = await prisma.shrimpGroupMember.findMany({
      where: {
        groupId: group.id,
        isActive: true
      },
      include: {
        user: {
          select: {
            id: true,
            username: true,
            avatar: true
          }
        }
      },
      orderBy: { joinTime: 'asc' }
    });

    res.json({
      success: true,
      data: {
        group: {
          id: group.id,
          name: group.name,
          groupKey: group.groupKey,
          description: group.description,
          currentMembers: members.length,
          maxMembers: group.maxMembers,
          icon: group.icon,
          color: group.color
        },
        members: members.map(m => ({
          id: m.user.id,
          username: m.user.username,
          avatar: m.user.avatar,
          nickname: m.nickname,
          joinTime: m.joinTime
        }))
      }
    });
  } catch (error) {
    console.error('获取群组成员失败:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'GET_MEMBERS_FAILED',
        message: '获取群组成员失败'
      }
    });
  }
};

// 管理员：创建群组
export const createGroup = async (req: Request, res: Response): Promise<void> => {
  try {
    const { name, groupKey, description, maxMembers, icon, color, sortOrder } = req.body;

    // 检查群组标识是否已存在
    const existing = await prisma.shrimpGroup.findUnique({
      where: { groupKey }
    });

    if (existing) {
      res.status(400).json({
        success: false,
        error: { code: 'KEY_EXISTS', message: '群组标识已存在' }
      });
      return;
    }

    const group = await prisma.shrimpGroup.create({
      data: {
        name,
        groupKey,
        description,
        maxMembers: maxMembers || 100,
        icon,
        color,
        sortOrder: sortOrder || 0
      }
    });

    res.status(201).json({
      success: true,
      data: group
    });
  } catch (error) {
    console.error('创建群组失败:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'CREATE_GROUP_FAILED',
        message: '创建群组失败'
      }
    });
  }
};

// 管理员：更新群组
export const updateGroup = async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    const { name, description, maxMembers, icon, color, sortOrder, isActive } = req.body;

    const group = await prisma.shrimpGroup.update({
      where: { id },
      data: {
        name,
        description,
        maxMembers,
        icon,
        color,
        sortOrder,
        isActive
      }
    });

    res.json({
      success: true,
      data: group
    });
  } catch (error) {
    console.error('更新群组失败:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'UPDATE_GROUP_FAILED',
        message: '更新群组失败'
      }
    });
  }
};

// 管理员：删除群组
export const deleteGroup = async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;

    // 软删除 - 只更新 isActive 状态
    await prisma.shrimpGroup.update({
      where: { id },
      data: { isActive: false }
    });

    res.json({
      success: true,
      message: '群组已删除'
    });
  } catch (error) {
    console.error('删除群组失败:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'DELETE_GROUP_FAILED',
        message: '删除群组失败'
      }
    });
  }
};
