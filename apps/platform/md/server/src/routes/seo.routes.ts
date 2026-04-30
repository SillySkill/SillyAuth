import { Router } from 'express';
import * as seoController from '../controllers/seo.controller';
import { authMiddleware, editorMiddleware } from '../middleware/auth';
import { validate } from '../middleware/validation';
import { seoSchemas } from '../utils/validation';

const router = Router();

// 公开路由 - sitemap 和 robots
router.get('/sitemap.xml', seoController.generateSitemap);
router.get('/robots.txt', seoController.generateRobots);

// 其他路由需要认证
router.use(authMiddleware);

/**
 * @route   GET /api/v1/seo
 * @desc    获取所有SEO配置
 * @access  Private
 */
router.get('/', seoController.getSEOSettings);

/**
 * @route   GET /api/v1/seo/:page
 * @desc    获取页面SEO配置
 * @access  Private
 */
router.get('/:page', seoController.getSEOByPage);

/**
 * @route   PUT /api/v1/seo/:page
 * @desc    创建或更新SEO配置
 * @access  Editor
 */
router.put(
  '/:page',
  editorMiddleware,
  validate(seoSchemas.create),
  seoController.upsertSEO
);

/**
 * @route   DELETE /api/v1/seo/:page/:language
 * @desc    删除SEO配置
 * @access  Editor
 */
router.delete('/:page/:language', editorMiddleware, seoController.deleteSEO);

export default router;
