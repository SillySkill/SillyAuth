import { Router } from 'express';
import * as publicController from '../controllers/public.controller';
import { validate } from '../middleware/validation';

const router = Router();

/**
 * 公共 API 路由
 * 无需认证的公开接口
 * 用于前端首页、市场页面等公开访问场景
 */

// ============================================
// 市场统计
// ============================================

/**
 * @route   GET /api/v1/public/market/stats
 * @desc    获取平台统计数据（Skills、供应商、团队等）
 * @access  Public
 */
router.get('/market/stats', publicController.getMarketStats);

// ============================================
// Skills 相关
// ============================================

/**
 * @route   GET /api/v1/public/skills
 * @desc    获取 Skills 列表（支持筛选、排序、分页）
 * @query   type - Skills 类型 (free/commercial)
 * @query   category - 分类 (tech/product/design/marketing/operations)
 * @query   status - 状态 (默认: approved)
 * @query   is_featured - 是否精选
 * @query   limit - 返回数量 (默认: 10, 最大: 50)
 * @query   sort - 排序字段 (默认: download_count)
 * @query   page - 页码 (默认: 1)
 * @access  Public
 */
router.get('/skills', publicController.getPublicSkills);

/**
 * @route   GET /api/v1/public/skills/categories
 * @desc    获取所有分类及其数量
 * @access  Public
 */
router.get('/skills/categories', publicController.getSkillCategories);

/**
 * @route   GET /api/v1/public/skills/:skillId
 * @desc    获取单个 Skill 详情
 * @access  Public
 */
router.get('/skills/:skillId', publicController.getPublicSkillById);

// ============================================
// 供应商相关
// ============================================

/**
 * @route   GET /api/v1/public/vendors
 * @desc    获取供应商列表（支持筛选、排序、分页）
 * @query   is_verified - 是否认证 (true/false)
 * @query   limit - 返回数量 (默认: 10, 最大: 50)
 * @query   sort - 排序字段 (rating/download_count)
 * @query   page - 页码 (默认: 1)
 * @access  Public
 */
router.get('/vendors', publicController.getPublicVendors);

export default router;
