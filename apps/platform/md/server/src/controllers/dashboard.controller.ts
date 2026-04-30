import { Request, Response } from 'express';
import { prisma } from '../config/database';
import { successResponse, errorResponse } from '../utils/response';
import { logger } from '../utils/logger';

/**
 * 获取仪表盘统计数据
 */
export async function getDashboardStats(req: Request, res: Response) {
  try {
    const language = (req.query.language as string) || 'zh';

    // 并行获取各种统计数据
    const [
      totalContent,
      publishedContent,
      totalNavigation,
      totalCarousel,
      activeCarousel,
      totalSkill,
      totalVendor,
      totalUser,
      activeUser,
      recentActivity,
    ] = await Promise.all([
      // 内容统计
      prisma.content.count({ where: { language } }),
      prisma.content.count({ where: { language, status: 'PUBLISHED' } }),

      // 导航和轮播统计
      prisma.navigation.count({ where: { language } }),
      prisma.carousel.count({ where: { language } }),
      prisma.carousel.count({ where: { language, isActive: true } }),

      // 技能和供应商统计
      prisma.skill.count({ where: { language } }),
      prisma.vendor.count({ where: { language } }),

      // 用户统计
      prisma.user.count(),
      prisma.user.count({ where: { status: 'ACTIVE' } }),

      // 最近活动
      prisma.activityLog.findMany({
        take: 10,
        orderBy: { createdAt: 'desc' },
        include: {
          user: {
            select: {
              username: true,
              email: true,
            },
          },
        },
      }),
    ]);

    const stats = {
      content: {
        total: totalContent,
        published: publishedContent,
        draft: totalContent - publishedContent,
      },
      navigation: {
        total: totalNavigation,
      },
      carousel: {
        total: totalCarousel,
        active: activeCarousel,
      },
      skill: {
        total: totalSkill,
      },
      vendor: {
        total: totalVendor,
      },
      user: {
        total: totalUser,
        active: activeUser,
      },
      recentActivity,
    };

    return res.json(successResponse(stats));
  } catch (error) {
    logger.error('获取仪表盘统计失败:', error);
    return res.status(500).json(errorResponse('获取仪表盘统计失败'));
  }
}

/**
 * 获取内容趋势（最近7天）
 */
export async function getContentTrend(req: Request, res: Response) {
  try {
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

    const content = await prisma.content.findMany({
      where: {
        createdAt: {
          gte: sevenDaysAgo,
        },
      },
      select: {
        createdAt: true,
        status: true,
      },
    });

    // 按日期分组统计
    const trend = Array.from({ length: 7 }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - (6 - i));
      date.setHours(0, 0, 0, 0);

      const nextDate = new Date(date);
      nextDate.setDate(nextDate.getDate() + 1);

      const dayContent = content.filter((c) => {
        const createdAt = new Date(c.createdAt);
        return createdAt >= date && createdAt < nextDate;
      });

      return {
        date: date.toISOString().split('T')[0],
        total: dayContent.length,
        published: dayContent.filter((c) => c.status === 'PUBLISHED').length,
        draft: dayContent.filter((c) => c.status === 'DRAFT').length,
      };
    });

    return res.json(successResponse(trend));
  } catch (error) {
    logger.error('获取内容趋势失败:', error);
    return res.status(500).json(errorResponse('获取内容趋势失败'));
  }
}

/**
 * 获取最近修改的内容
 */
export async function getRecentContent(req: Request, res: Response) {
  try {
    const language = (req.query.language as string) || 'zh';
    const limit = parseInt(req.query.limit as string) || 10;

    const contents = await prisma.content.findMany({
      where: { language },
      take: limit,
      orderBy: { updatedAt: 'desc' },
      select: {
        id: true,
        key: true,
        title: true,
        type: true,
        status: true,
        updatedAt: true,
      },
    });

    return res.json(successResponse(contents));
  } catch (error) {
    logger.error('获取最近内容失败:', error);
    return res.status(500).json(errorResponse('获取最近内容失败'));
  }
}

/**
 * 获取操作日志
 */
export async function getActivityLogs(req: Request, res: Response) {
  try {
    const page = parseInt(req.query.page as string) || 1;
    const limit = parseInt(req.query.limit as string) || 20;
    const userId = req.query.userId as string;
    const action = req.query.action as string;

    const skip = (page - 1) * limit;

    const where: any = {};

    if (userId) {
      where.userId = userId;
    }

    if (action) {
      where.action = action;
    }

    const [logs, total] = await Promise.all([
      prisma.activityLog.findMany({
        where,
        skip,
        take: limit,
        orderBy: { createdAt: 'desc' },
        include: {
          user: {
            select: {
              username: true,
              email: true,
            },
          },
        },
      }),
      prisma.activityLog.count({ where }),
    ]);

    return res.json({
      success: true,
      data: logs,
      meta: {
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit),
      },
    });
  } catch (error) {
    logger.error('获取操作日志失败:', error);
    return res.status(500).json(errorResponse('获取操作日志失败'));
  }
}
