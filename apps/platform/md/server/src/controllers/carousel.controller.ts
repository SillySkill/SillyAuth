import { Request, Response } from 'express';
import { prisma } from '../config/database';
import { successResponse, errorResponse, notFoundResponse } from '../utils/response';
import { logger } from '../utils/logger';

/**
 * 获取轮播图列表
 */
export async function getCarousels(req: Request, res: Response) {
  try {
    const language = (req.query.language as string) || 'zh';
    const isActive = req.query.isActive;

    const where: any = { language };

    if (isActive !== undefined) {
      where.isActive = isActive === 'true';
    }

    const carousels = await prisma.carousel.findMany({
      where,
      orderBy: { order: 'asc' },
    });

    return res.json(successResponse(carousels));
  } catch (error) {
    logger.error('获取轮播图列表失败:', error);
    return res.status(500).json(errorResponse('获取轮播图列表失败'));
  }
}

/**
 * 获取单个轮播图
 */
export async function getCarouselById(req: Request, res: Response) {
  try {
    const { id } = req.params;

    const carousel = await prisma.carousel.findUnique({
      where: { id },
    });

    if (!carousel) {
      return res.status(404).json(notFoundResponse('轮播图'));
    }

    return res.json(successResponse(carousel));
  } catch (error) {
    logger.error('获取轮播图失败:', error);
    return res.status(500).json(errorResponse('获取轮播图失败'));
  }
}

/**
 * 创建轮播图
 */
export async function createCarousel(req: Request, res: Response) {
  try {
    const userId = req.user!.userId;
    const data = req.body;

    const carousel = await prisma.carousel.create({
      data,
    });

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'CAROUSEL_CREATED',
        entity: 'Carousel',
        entityId: carousel.id,
        details: { title: carousel.title },
      },
    });

    logger.info(`创建轮播图: ${carousel.title}`);

    return res.status(201).json(successResponse(carousel, '轮播图创建成功'));
  } catch (error) {
    logger.error('创建轮播图失败:', error);
    return res.status(500).json(errorResponse('创建轮播图失败'));
  }
}

/**
 * 更新轮播图
 */
export async function updateCarousel(req: Request, res: Response) {
  try {
    const { id } = req.params;
    const userId = req.user!.userId;
    const data = req.body;

    const carousel = await prisma.carousel.update({
      where: { id },
      data,
    });

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'CAROUSEL_UPDATED',
        entity: 'Carousel',
        entityId: carousel.id,
        details: { title: carousel.title },
      },
    });

    logger.info(`更新轮播图: ${carousel.title}`);

    return res.json(successResponse(carousel, '轮播图更新成功'));
  } catch (error) {
    logger.error('更新轮播图失败:', error);
    return res.status(500).json(errorResponse('更新轮播图失败'));
  }
}

/**
 * 删除轮播图
 */
export async function deleteCarousel(req: Request, res: Response) {
  try {
    const { id } = req.params;
    const userId = req.user!.userId;

    const carousel = await prisma.carousel.findUnique({
      where: { id },
    });

    if (!carousel) {
      return res.status(404).json(notFoundResponse('轮播图'));
    }

    await prisma.carousel.delete({
      where: { id },
    });

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'CAROUSEL_DELETED',
        entity: 'Carousel',
        entityId: id,
        details: { title: carousel.title },
      },
    });

    logger.info(`删除轮播图: ${carousel.title}`);

    return res.json(successResponse(null, '轮播图删除成功'));
  } catch (error) {
    logger.error('删除轮播图失败:', error);
    return res.status(500).json(errorResponse('删除轮播图失败'));
  }
}

/**
 * 切换轮播图启用状态
 */
export async function toggleCarousel(req: Request, res: Response) {
  try {
    const { id } = req.params;
    const userId = req.user!.userId;

    const carousel = await prisma.carousel.findUnique({
      where: { id },
    });

    if (!carousel) {
      return res.status(404).json(notFoundResponse('轮播图'));
    }

    const updated = await prisma.carousel.update({
      where: { id },
      data: { isActive: !carousel.isActive },
    });

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'CAROUSEL_TOGGLED',
        entity: 'Carousel',
        entityId: id,
        details: {
          title: carousel.title,
          isActive: updated.isActive,
        },
      },
    });

    logger.info(`切换轮播图状态: ${carousel.title}`);

    return res.json(successResponse(updated, '状态更新成功'));
  } catch (error) {
    logger.error('切换轮播图状态失败:', error);
    return res.status(500).json(errorResponse('切换状态失败'));
  }
}

/**
 * 批量更新轮播图排序
 */
export async function updateCarouselOrder(req: Request, res: Response) {
  try {
    const userId = req.user!.userId;
    const { orders } = req.body; // [{id, order}, ...]

    await prisma.$transaction(
      orders.map((item: { id: string; order: number }) =>
        prisma.carousel.update({
          where: { id: item.id },
          data: { order: item.order },
        })
      )
    );

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'CAROUSEL_ORDER_UPDATED',
        entity: 'Carousel',
        details: { count: orders.length },
      },
    });

    logger.info(`批量更新轮播图排序: ${orders.length} 项`);

    return res.json(successResponse(null, '轮播图排序更新成功'));
  } catch (error) {
    logger.error('更新轮播图排序失败:', error);
    return res.status(500).json(errorResponse('更新排序失败'));
  }
}
