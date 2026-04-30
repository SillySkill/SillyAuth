import { Router } from 'express';
import * as dashboardController from '../controllers/dashboard.controller';
import { authMiddleware } from '../middleware/auth';

const router = Router();

// 所有路由都需要认证
router.use(authMiddleware);

/**
 * @route   GET /api/v1/dashboard/stats
 * @desc    获取仪表盘统计数据
 * @access  Private
 */
router.get('/stats', dashboardController.getDashboardStats);

/**
 * @route   GET /api/v1/dashboard/trend
 * @desc    获取内容趋势
 * @access  Private
 */
router.get('/trend', dashboardController.getContentTrend);

/**
 * @route   GET /api/v1/dashboard/recent
 * @desc    获取最近修改的内容
 * @access  Private
 */
router.get('/recent', dashboardController.getRecentContent);

/**
 * @route   GET /api/v1/dashboard/logs
 * @desc    获取操作日志
 * @access  Private
 */
router.get('/logs', dashboardController.getActivityLogs);

export default router;
