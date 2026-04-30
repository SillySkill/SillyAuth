import { Request, Response } from 'express';
import { prisma } from '../config/database';
import { successResponse, errorResponse, notFoundResponse } from '../utils/response';
import { logger } from '../utils/logger';

/**
 * 获取所有SEO配置
 */
export async function getSEOSettings(req: Request, res: Response) {
  try {
    const language = (req.query.language as string) || 'zh';

    const settings = await prisma.sEOSettings.findMany({
      where: { language },
    });

    return res.json(successResponse(settings));
  } catch (error) {
    logger.error('获取SEO配置失败:', error);
    return res.status(500).json(errorResponse('获取SEO配置失败'));
  }
}

/**
 * 获取页面SEO配置
 */
export async function getSEOByPage(req: Request, res: Response) {
  try {
    const { page } = req.params;
    const language = (req.query.language as string) || 'zh';

    const setting = await prisma.sEOSettings.findUnique({
      where: {
        page_language: {
          page,
          language,
        },
      },
    });

    if (!setting) {
      return res.status(404).json(notFoundResponse('SEO配置'));
    }

    return res.json(successResponse(setting));
  } catch (error) {
    logger.error('获取SEO配置失败:', error);
    return res.status(500).json(errorResponse('获取SEO配置失败'));
  }
}

/**
 * 创建或更新SEO配置
 */
export async function upsertSEO(req: Request, res: Response) {
  try {
    const userId = req.user!.userId;
    const { page } = req.params;
    const data = req.body;

    const setting = await prisma.sEOSettings.upsert({
      where: {
        page_language: {
          page,
          language: data.language || 'zh',
        },
      },
      update: data,
      create: {
        page,
        ...data,
      },
    });

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'SEO_UPDATED',
        entity: 'SEO',
        entityId: setting.id,
        details: { page, title: setting.title },
      },
    });

    logger.info(`更新SEO配置: ${page}`);

    return res.json(successResponse(setting, 'SEO配置保存成功'));
  } catch (error) {
    logger.error('保存SEO配置失败:', error);
    return res.status(500).json(errorResponse('保存SEO配置失败'));
  }
}

/**
 * 删除SEO配置
 */
export async function deleteSEO(req: Request, res: Response) {
  try {
    const { page, language } = req.params;
    const userId = req.user!.userId;

    const setting = await prisma.sEOSettings.findUnique({
      where: {
        page_language: {
          page,
          language,
        },
      },
    });

    if (!setting) {
      return res.status(404).json(notFoundResponse('SEO配置'));
    }

    await prisma.sEOSettings.delete({
      where: {
        page_language: {
          page,
          language,
        },
      },
    });

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'SEO_DELETED',
        entity: 'SEO',
        entityId: setting.id,
        details: { page },
      },
    });

    logger.info(`删除SEO配置: ${page}`);

    return res.json(successResponse(null, 'SEO配置删除成功'));
  } catch (error) {
    logger.error('删除SEO配置失败:', error);
    return res.status(500).json(errorResponse('删除SEO配置失败'));
  }
}

/**
 * 生成sitemap.xml
 */
export async function generateSitemap(req: Request, res: Response) {
  try {
    const baseUrl = process.env.BASE_URL || 'https://example.com';

    // 获取所有已发布的内容
    const contents = await prisma.content.findMany({
      where: {
        status: 'PUBLISHED',
      },
      select: {
        key: true,
        updatedAt: true,
      },
    });

    // 生成XML
    const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>${baseUrl}/</loc>
    <lastmod>${new Date().toISOString()}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
${contents
  .map(
    (content) => `  <url>
    <loc>${baseUrl}/${content.key}</loc>
    <lastmod>${content.updatedAt.toISOString()}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>`
  )
  .join('\n')}
</urlset>`;

    res.set('Content-Type', 'application/xml');
    res.send(xml);
  } catch (error) {
    logger.error('生成sitemap失败:', error);
    return res.status(500).json(errorResponse('生成sitemap失败'));
  }
}

/**
 * 生成robots.txt
 */
export async function generateRobots(req: Request, res: Response) {
  try {
    const baseUrl = process.env.BASE_URL || 'https://example.com';

    const robots = `User-agent: *
Allow: /

Sitemap: ${baseUrl}/sitemap.xml

# 禁止爬取管理后台
Disallow: /admin/
Disallow: /api/`;

    res.set('Content-Type', 'text/plain');
    res.send(robots);
  } catch (error) {
    logger.error('生成robots.txt失败:', error);
    return res.status(500).json(errorResponse('生成robots.txt失败'));
  }
}
