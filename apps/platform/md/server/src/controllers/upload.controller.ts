import { Request, Response } from 'express';
import { prisma } from '../config/database';
import { successResponse, errorResponse } from '../utils/response';
import { logger } from '../utils/logger';
import path from 'path';
import fs from 'fs';

/**
 * 上传单个文件
 */
export async function uploadFile(req: Request, res: Response) {
  try {
    const userId = req.user!.userId;
    const file = req.file;

    if (!file) {
      return res.status(400).json(errorResponse('没有上传文件'));
    }

    // 构建相对URL路径
    const relativePath = path.relative(path.join(process.cwd(), 'uploads'), file.path);
    const url = `/uploads/${relativePath.replace(/\\/g, '/')}`;

    // 获取图片尺寸
    let width: number | undefined;
    let height: number | undefined;

    if (file.mimetype.startsWith('image/')) {
      try {
        // 这里可以使用 sharp 等库获取图片尺寸
        // 暂时跳过
      } catch (error) {
        logger.warn('无法获取图片尺寸');
      }
    }

    // 保存到数据库
    const media = await prisma.media.create({
      data: {
        filename: file.filename,
        originalName: file.originalname,
        mimeType: file.mimetype,
        size: file.size,
        url,
        path: file.path,
        width,
        height,
        category: req.body.category,
      },
    });

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'FILE_UPLOADED',
        entity: 'Media',
        entityId: media.id,
        details: {
          filename: file.originalname,
          size: file.size,
          mimeType: file.mimetype,
        },
      },
    });

    logger.info(`文件上传成功: ${file.originalname}`);

    return res.json(successResponse(media, '文件上传成功'));
  } catch (error) {
    logger.error('文件上传失败:', error);
    return res.status(500).json(errorResponse('文件上传失败'));
  }
}

/**
 * 上传多个文件
 */
export async function uploadFiles(req: Request, res: Response) {
  try {
    const userId = req.user!.userId;
    const files = req.files as Express.Multer.File[];

    if (!files || files.length === 0) {
      return res.status(400).json(errorResponse('没有上传文件'));
    }

    const mediaList = await Promise.all(
      files.map(async (file) => {
        const relativePath = path.relative(path.join(process.cwd(), 'uploads'), file.path);
        const url = `/uploads/${relativePath.replace(/\\/g, '/')}`;

        return prisma.media.create({
          data: {
            filename: file.filename,
            originalName: file.originalname,
            mimeType: file.mimetype,
            size: file.size,
            url,
            path: file.path,
            category: req.body.category,
          },
        });
      })
    );

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'FILES_UPLOADED',
        entity: 'Media',
        details: {
          count: files.length,
        },
      },
    });

    logger.info(`批量上传文件成功: ${files.length} 个`);

    return res.json(successResponse(mediaList, '文件上传成功'));
  } catch (error) {
    logger.error('批量上传文件失败:', error);
    return res.status(500).json(errorResponse('文件上传失败'));
  }
}

/**
 * 获取媒体文件列表
 */
export async function getMediaList(req: Request, res: Response) {
  try {
    const page = parseInt(req.query.page as string) || 1;
    const limit = parseInt(req.query.limit as string) || 20;
    const category = req.query.category as string;
    const mimeType = req.query.mimeType as string;

    const skip = (page - 1) * limit;

    const where: any = {};

    if (category) {
      where.category = category;
    }

    if (mimeType) {
      where.mimeType = { startsWith: mimeType };
    }

    const [mediaList, total] = await Promise.all([
      prisma.media.findMany({
        where,
        skip,
        take: limit,
        orderBy: { createdAt: 'desc' },
      }),
      prisma.media.count({ where }),
    ]);

    return res.json({
      success: true,
      data: mediaList,
      meta: {
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit),
      },
    });
  } catch (error) {
    logger.error('获取媒体列表失败:', error);
    return res.status(500).json(errorResponse('获取媒体列表失败'));
  }
}

/**
 * 删除媒体文件
 */
export async function deleteMedia(req: Request, res: Response) {
  try {
    const { id } = req.params;
    const userId = req.user!.userId;

    const media = await prisma.media.findUnique({
      where: { id },
    });

    if (!media) {
      return res.status(404).json({
        success: false,
        message: '文件不存在',
      });
    }

    // 删除物理文件
    try {
      if (fs.existsSync(media.path)) {
        fs.unlinkSync(media.path);
        logger.info(`删除物理文件: ${media.path}`);
      }
    } catch (error) {
      logger.warn(`删除物理文件失败: ${media.path}`, error);
    }

    // 删除数据库记录
    await prisma.media.delete({
      where: { id },
    });

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'FILE_DELETED',
        entity: 'Media',
        entityId: id,
        details: {
          filename: media.originalName,
        },
      },
    });

    logger.info(`删除媒体文件: ${media.originalName}`);

    return res.json(successResponse(null, '文件删除成功'));
  } catch (error) {
    logger.error('删除媒体文件失败:', error);
    return res.status(500).json(errorResponse('删除文件失败'));
  }
}
