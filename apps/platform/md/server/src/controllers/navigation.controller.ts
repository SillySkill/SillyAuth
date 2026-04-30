import { Request, Response } from 'express';
import { prisma } from '../config/database';
import { successResponse, errorResponse, notFoundResponse } from '../utils/response';
import { logger } from '../utils/logger';

/**
 * 获取导航树结构
 */
export async function getNavigationTree(req: Request, res: Response) {
  try {
    const language = (req.query.language as string) || 'zh';

    // 获取所有顶级导航
    const rootNavigations = await prisma.navigation.findMany({
      where: {
        parentId: null,
        language,
      },
      orderBy: { order: 'asc' },
      include: {
        children: {
          orderBy: { order: 'asc' },
          include: {
            children: true,
          },
        },
      },
    });

    return res.json(successResponse(rootNavigations));
  } catch (error) {
    logger.error('获取导航树失败:', error);
    return res.status(500).json(errorResponse('获取导航树失败'));
  }
}

/**
 * 获取所有导航（扁平结构）
 */
export async function getNavigations(req: Request, res: Response) {
  try {
    const language = (req.query.language as string) || 'zh';

    const navigations = await prisma.navigation.findMany({
      where: { language },
      orderBy: { order: 'asc' },
    });

    return res.json(successResponse(navigations));
  } catch (error) {
    logger.error('获取导航列表失败:', error);
    return res.status(500).json(errorResponse('获取导航列表失败'));
  }
}

/**
 * 获取单个导航
 */
export async function getNavigationById(req: Request, res: Response) {
  try {
    const { id } = req.params;

    const navigation = await prisma.navigation.findUnique({
      where: { id },
      include: {
        parent: true,
        children: true,
      },
    });

    if (!navigation) {
      return res.status(404).json(notFoundResponse('导航'));
    }

    return res.json(successResponse(navigation));
  } catch (error) {
    logger.error('获取导航失败:', error);
    return res.status(500).json(errorResponse('获取导航失败'));
  }
}

/**
 * 创建导航
 */
export async function createNavigation(req: Request, res: Response) {
  try {
    const userId = req.user!.userId;
    const data = req.body;

    const navigation = await prisma.navigation.create({
      data,
    });

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'NAVIGATION_CREATED',
        entity: 'Navigation',
        entityId: navigation.id,
        details: { title: navigation.title, key: navigation.key },
      },
    });

    logger.info(`创建导航: ${navigation.title}`);

    return res.status(201).json(successResponse(navigation, '导航创建成功'));
  } catch (error) {
    logger.error('创建导航失败:', error);
    return res.status(500).json(errorResponse('创建导航失败'));
  }
}

/**
 * 更新导航
 */
export async function updateNavigation(req: Request, res: Response) {
  try {
    const { id } = req.params;
    const userId = req.user!.userId;
    const data = req.body;

    const navigation = await prisma.navigation.update({
      where: { id },
      data,
    });

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'NAVIGATION_UPDATED',
        entity: 'Navigation',
        entityId: navigation.id,
        details: { title: navigation.title, key: navigation.key },
      },
    });

    logger.info(`更新导航: ${navigation.title}`);

    return res.json(successResponse(navigation, '导航更新成功'));
  } catch (error) {
    logger.error('更新导航失败:', error);
    return res.status(500).json(errorResponse('更新导航失败'));
  }
}

/**
 * 删除导航
 */
export async function deleteNavigation(req: Request, res: Response) {
  try {
    const { id } = req.params;
    const userId = req.user!.userId;

    const navigation = await prisma.navigation.findUnique({
      where: { id },
    });

    if (!navigation) {
      return res.status(404).json(notFoundResponse('导航'));
    }

    await prisma.navigation.delete({
      where: { id },
    });

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'NAVIGATION_DELETED',
        entity: 'Navigation',
        entityId: id,
        details: { title: navigation.title, key: navigation.key },
      },
    });

    logger.info(`删除导航: ${navigation.title}`);

    return res.json(successResponse(null, '导航删除成功'));
  } catch (error) {
    logger.error('删除导航失败:', error);
    return res.status(500).json(errorResponse('删除导航失败'));
  }
}

/**
 * 批量更新导航排序
 */
export async function updateNavigationOrder(req: Request, res: Response) {
  try {
    const userId = req.user!.userId;
    const { orders } = req.body; // [{id, order}, ...]

    // 使用事务批量更新
    await prisma.$transaction(
      orders.map((item: { id: string; order: number }) =>
        prisma.navigation.update({
          where: { id: item.id },
          data: { order: item.order },
        })
      )
    );

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'NAVIGATION_ORDER_UPDATED',
        entity: 'Navigation',
        details: { count: orders.length },
      },
    });

    logger.info(`批量更新导航排序: ${orders.length} 项`);

    return res.json(successResponse(null, '导航排序更新成功'));
  } catch (error) {
    logger.error('更新导航排序失败:', error);
    return res.status(500).json(errorResponse('更新导航排序失败'));
  }
}
