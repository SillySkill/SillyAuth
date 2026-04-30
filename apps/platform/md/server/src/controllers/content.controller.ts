import { Request, Response } from 'express';
import { prisma } from '../config/database';
import { successResponse, errorResponse, paginatedResponse, notFoundResponse } from '../utils/response';
import { logger } from '../utils/logger';
import { config } from '../config';

/**
 * 获取内容列表
 */
export async function getContents(req: Request, res: Response) {
  try {
    const page = parseInt(req.query.page as string) || config.pagination.defaultPage;
    const limit = parseInt(req.query.limit as string) || config.pagination.defaultLimit;
    const type = req.query.type as string;
    const language = req.query.language as string;
    const status = req.query.status as string;
    const search = req.query.search as string;

    const skip = (page - 1) * limit;

    // 构建查询条件
    const where: any = {};

    if (type) {
      where.type = type;
    }

    if (language) {
      where.language = language;
    }

    if (status) {
      where.status = status;
    }

    if (search) {
      where.OR = [
        { title: { contains: search } },
        { key: { contains: search } },
      ];
    }

    // 获取总数
    const total = await prisma.content.count({ where });

    // 获取数据
    const contents = await prisma.content.findMany({
      where,
      skip,
      take: limit,
      orderBy: { updatedAt: 'desc' },
      select: {
        id: true,
        key: true,
        type: true,
        title: true,
        content: true,
        language: true,
        status: true,
        createdAt: true,
        updatedAt: true,
      },
    });

    return res.json(paginatedResponse(contents, page, limit, total));
  } catch (error) {
    logger.error('获取内容列表失败:', error);
    return res.status(500).json(errorResponse('获取内容列表失败'));
  }
}

/**
 * 获取单个内容
 */
export async function getContentById(req: Request, res: Response) {
  try {
    const { id } = req.params;

    const content = await prisma.content.findUnique({
      where: { id },
      include: {
        versions: {
          take: 10,
          orderBy: { version: 'desc' },
          select: {
            id: true,
            version: true,
            createdAt: true,
            createdBy: true,
            changeLog: true,
          },
        },
      },
    });

    if (!content) {
      return res.status(404).json(notFoundResponse('内容'));
    }

    return res.json(successResponse(content));
  } catch (error) {
    logger.error('获取内容失败:', error);
    return res.status(500).json(errorResponse('获取内容失败'));
  }
}

/**
 * 根据key获取内容
 */
export async function getContentByKey(req: Request, res: Response) {
  try {
    const { key } = req.params;
    const language = (req.query.language as string) || 'zh';

    const content = await prisma.content.findFirst({
      where: {
        key,
        language,
      },
    });

    if (!content) {
      return res.status(404).json(notFoundResponse('内容'));
    }

    return res.json(successResponse(content));
  } catch (error) {
    logger.error('获取内容失败:', error);
    return res.status(500).json(errorResponse('获取内容失败'));
  }
}

/**
 * 创建内容
 */
export async function createContent(req: Request, res: Response) {
  try {
    const userId = req.user!.userId;
    const data = req.body;

    const content = await prisma.content.create({
      data: {
        ...data,
        createdBy: userId,
      },
    });

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'CONTENT_CREATED',
        entity: 'Content',
        entityId: content.id,
        details: { key: content.key, title: content.title },
      },
    });

    logger.info(`创建内容: ${content.key}`);

    return res.status(201).json(successResponse(content, '内容创建成功'));
  } catch (error) {
    logger.error('创建内容失败:', error);
    return res.status(500).json(errorResponse('创建内容失败'));
  }
}

/**
 * 更新内容
 */
export async function updateContent(req: Request, res: Response) {
  try {
    const { id } = req.params;
    const userId = req.user!.userId;
    const data = req.body;

    // 检查内容是否存在
    const existingContent = await prisma.content.findUnique({
      where: { id },
    });

    if (!existingContent) {
      return res.status(404).json(notFoundResponse('内容'));
    }

    // 更新内容
    const content = await prisma.content.update({
      where: { id },
      data: {
        ...data,
        updatedBy: userId,
      },
    });

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'CONTENT_UPDATED',
        entity: 'Content',
        entityId: content.id,
        details: { key: content.key, title: content.title },
      },
    });

    logger.info(`更新内容: ${content.key}`);

    return res.json(successResponse(content, '内容更新成功'));
  } catch (error) {
    logger.error('更新内容失败:', error);
    return res.status(500).json(errorResponse('更新内容失败'));
  }
}

/**
 * 删除内容
 */
export async function deleteContent(req: Request, res: Response) {
  try {
    const { id } = req.params;
    const userId = req.user!.userId;

    const content = await prisma.content.findUnique({
      where: { id },
    });

    if (!content) {
      return res.status(404).json(notFoundResponse('内容'));
    }

    await prisma.content.delete({
      where: { id },
    });

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'CONTENT_DELETED',
        entity: 'Content',
        entityId: id,
        details: { key: content.key, title: content.title },
      },
    });

    logger.info(`删除内容: ${content.key}`);

    return res.json(successResponse(null, '内容删除成功'));
  } catch (error) {
    logger.error('删除内容失败:', error);
    return res.status(500).json(errorResponse('删除内容失败'));
  }
}

/**
 * 获取内容版本历史
 */
export async function getContentVersions(req: Request, res: Response) {
  try {
    const { id } = req.params;
    const page = parseInt(req.query.page as string) || 1;
    const limit = parseInt(req.query.limit as string) || 20;

    const skip = (page - 1) * limit;

    const [versions, total] = await Promise.all([
      prisma.contentVersion.findMany({
        where: { contentId: id },
        skip,
        take: limit,
        orderBy: { version: 'desc' },
        include: {
          creator: {
            select: {
              id: true,
              username: true,
              email: true,
            },
          },
        },
      }),
      prisma.contentVersion.count({ where: { contentId: id } }),
    ]);

    return res.json(paginatedResponse(versions, page, limit, total));
  } catch (error) {
    logger.error('获取版本历史失败:', error);
    return res.status(500).json(errorResponse('获取版本历史失败'));
  }
}

/**
 * 发布内容
 */
export async function publishContent(req: Request, res: Response) {
  try {
    const { id } = req.params;
    const userId = req.user!.userId;

    const content = await prisma.content.update({
      where: { id },
      data: {
        status: 'PUBLISHED',
        updatedBy: userId,
      },
    });

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'CONTENT_PUBLISHED',
        entity: 'Content',
        entityId: content.id,
        details: { key: content.key, title: content.title },
      },
    });

    logger.info(`发布内容: ${content.key}`);

    return res.json(successResponse(content, '内容发布成功'));
  } catch (error) {
    logger.error('发布内容失败:', error);
    return res.status(500).json(errorResponse('发布内容失败'));
  }
}
