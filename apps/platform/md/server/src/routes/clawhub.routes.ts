/**
 * Clawhub 路由
 * 处理 Clawhub 热门应用翻译相关路由
 */

import { Router } from 'express';
import * as clawhubController from '../controllers/clawhub.controller';
import { adminMiddleware } from '../middleware/auth';

const router = Router();

/**
 * @route   GET /api/v1/clawhub/hot-apps
 * @desc    获取热门应用列表（含翻译）
 * @access  Public
 * @param   locale - 可选，指定语言 (zh-CN, en, ja, ko)
 */
router.get('/hot-apps', clawhubController.getHotApps);

/**
 * @route   GET /api/v1/clawhub/search
 * @desc    搜索应用（含翻译）
 * @access  Public
 * @param   q - 搜索关键词
 * @param   locale - 可选，指定语言
 */
router.get('/search', clawhubController.searchApps);

/**
 * @route   GET /api/v1/clawhub/apps/:slug
 * @desc    获取应用详情（含翻译）
 * @access  Public
 * @param   slug - 应用标识
 * @param   locale - 可选，指定语言
 */
router.get('/apps/:slug', clawhubController.getAppDetails);

// 管理员路由
/**
 * @route   POST /api/v1/clawhub/cache/clear
 * @desc    清除缓存
 * @access  Admin
 */
router.post('/cache/clear', adminMiddleware, clawhubController.clearCache);

export default router;
