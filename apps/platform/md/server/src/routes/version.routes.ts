/**
 * 版本更新路由
 */

import { Router } from 'express';
import * as versionController from '../controllers/version.controller';
import { authMiddleware, adminMiddleware } from '../middleware/auth';

const router = Router();

// 公开路由

/**
 * @route   GET /api/v1/versions/latest
 * @desc    获取最新版本信息
 * @access  Public
 */
router.get('/latest', versionController.getLatestVersion);

/**
 * @route   GET /api/v1/versions/check
 * @desc    检查更新
 * @access  Public
 */
router.get('/check', versionController.checkUpdate);

/**
 * @route   GET /api/v1/versions/:appKey/history
 * @desc    获取版本历史
 * @access  Public
 */
router.get('/:appKey/history', versionController.getVersionHistory);

// 需要管理员权限的路由

/**
 * @route   GET /api/v1/versions
 * @desc    获取所有版本列表
 * @access  Admin
 */
router.get('/', adminMiddleware, versionController.getAllAppVersions);

/**
 * @route   POST /api/v1/versions
 * @desc    创建新版本
 * @access  Admin
 */
router.post('/', adminMiddleware, versionController.createVersion);

/**
 * @route   PUT /api/v1/versions/:id
 * @desc    更新版本信息
 * @access  Admin
 */
router.put('/:id', adminMiddleware, versionController.updateVersion);

/**
 * @route   DELETE /api/v1/versions/:id
 * @desc    删除版本
 * @access  Admin
 */
router.delete('/:id', adminMiddleware, versionController.deleteVersion);

export default router;
