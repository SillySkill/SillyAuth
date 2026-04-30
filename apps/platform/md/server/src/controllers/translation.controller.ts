import { Request, Response } from 'express';
import { prisma } from '../config/database';
import { successResponse, errorResponse, notFoundResponse } from '../utils/response';
import { logger } from '../utils/logger';

/**
 * 获取所有翻译
 */
export async function getTranslations(req: Request, res: Response) {
  try {
    const language = (req.query.language as string) || 'zh';
    const namespace = req.query.namespace as string;
    const key = req.query.key as string;

    const where: any = {};

    if (language) {
      where.language = language;
    }

    if (namespace) {
      where.namespace = namespace;
    }

    if (key) {
      where.key = { contains: key };
    }

    const translations = await prisma.translation.findMany({
      where,
      orderBy: [{ key: 'asc' }, { language: 'asc' }],
    });

    // 按语言分组
    const grouped = translations.reduce((acc: any, translation) => {
      if (!acc[translation.language]) {
        acc[translation.language] = {};
      }
      acc[translation.language][translation.key] = translation.value;
      return acc;
    }, {});

    return res.json(successResponse(grouped));
  } catch (error) {
    logger.error('获取翻译列表失败:', error);
    return res.status(500).json(errorResponse('获取翻译列表失败'));
  }
}

/**
 * 获取单个翻译
 */
export async function getTranslationByKey(req: Request, res: Response) {
  try {
    const { key, language } = req.params;

    const translation = await prisma.translation.findUnique({
      where: {
        key_language: {
          key,
          language,
        },
      },
    });

    if (!translation) {
      return res.status(404).json(notFoundResponse('翻译'));
    }

    return res.json(successResponse(translation));
  } catch (error) {
    logger.error('获取翻译失败:', error);
    return res.status(500).json(errorResponse('获取翻译失败'));
  }
}

/**
 * 创建或更新翻译
 */
export async function upsertTranslation(req: Request, res: Response) {
  try {
    const userId = req.user!.userId;
    const { key, language } = req.params;
    const { value, namespace, context } = req.body;

    const translation = await prisma.translation.upsert({
      where: {
        key_language: {
          key,
          language,
        },
      },
      update: {
        value,
        namespace,
        context,
      },
      create: {
        key,
        language,
        value,
        namespace,
        context,
      },
    });

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'TRANSLATION_UPDATED',
        entity: 'Translation',
        entityId: translation.id,
        details: { key, language },
      },
    });

    logger.info(`更新翻译: ${key} (${language})`);

    return res.json(successResponse(translation, '翻译保存成功'));
  } catch (error) {
    logger.error('保存翻译失败:', error);
    return res.status(500).json(errorResponse('保存翻译失败'));
  }
}

/**
 * 批量创建或更新翻译
 */
export async function batchUpsertTranslations(req: Request, res: Response) {
  try {
    const userId = req.user!.userId;
    const { translations } = req.body; // [{key, language, value, namespace, context}, ...]

    const results = await Promise.all(
      translations.map((item: any) =>
        prisma.translation.upsert({
          where: {
            key_language: {
              key: item.key,
              language: item.language,
            },
          },
          update: {
            value: item.value,
            namespace: item.namespace,
            context: item.context,
          },
          create: item,
        })
      )
    );

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'TRANSLATIONS_BATCH_UPDATED',
        entity: 'Translation',
        details: { count: translations.length },
      },
    });

    logger.info(`批量更新翻译: ${translations.length} 项`);

    return res.json(successResponse(results, '批量保存翻译成功'));
  } catch (error) {
    logger.error('批量保存翻译失败:', error);
    return res.status(500).json(errorResponse('批量保存翻译失败'));
  }
}

/**
 * 删除翻译
 */
export async function deleteTranslation(req: Request, res: Response) {
  try {
    const { key, language } = req.params;
    const userId = req.user!.userId;

    const translation = await prisma.translation.findUnique({
      where: {
        key_language: {
          key,
          language,
        },
      },
    });

    if (!translation) {
      return res.status(404).json(notFoundResponse('翻译'));
    }

    await prisma.translation.delete({
      where: {
        key_language: {
          key,
          language,
        },
      },
    });

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'TRANSLATION_DELETED',
        entity: 'Translation',
        entityId: translation.id,
        details: { key, language },
      },
    });

    logger.info(`删除翻译: ${key} (${language})`);

    return res.json(successResponse(null, '翻译删除成功'));
  } catch (error) {
    logger.error('删除翻译失败:', error);
    return res.status(500).json(errorResponse('删除翻译失败'));
  }
}

/**
 * 导出翻译
 */
export async function exportTranslations(req: Request, res: Response) {
  try {
    const language = (req.query.language as string) || 'zh';

    const translations = await prisma.translation.findMany({
      where: { language },
    });

    // 转换为简单的键值对格式
    const data = translations.reduce((acc: any, t) => {
      acc[t.key] = t.value;
      return acc;
    }, {});

    return res.json(successResponse(data));
  } catch (error) {
    logger.error('导出翻译失败:', error);
    return res.status(500).json(errorResponse('导出翻译失败'));
  }
}

/**
 * 获取缺失的翻译
 */
export async function getMissingTranslations(req: Request, res: Response) {
  try {
    // 获取所有唯一的键
    const allKeys = await prisma.translation.findMany({
      select: { key: true },
      distinct: ['key'],
    });

    // 获取所有语言
    const allLanguages = await prisma.translation.findMany({
      select: { language: true },
      distinct: ['language'],
    });

    const missing: Array<{ key: string; language: string }> = [];

    // 检查每个键在每种语言下是否存在
    for (const { key } of allKeys) {
      for (const { language } of allLanguages) {
        const exists = await prisma.translation.findUnique({
          where: {
            key_language: { key, language },
          },
        });

        if (!exists) {
          missing.push({ key, language });
        }
      }
    }

    return res.json(successResponse(missing));
  } catch (error) {
    logger.error('获取缺失翻译失败:', error);
    return res.status(500).json(errorResponse('获取缺失翻译失败'));
  }
}
