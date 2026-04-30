import { Router } from 'express';
import * as vendorApplicationController from '../controllers/vendor-application.controller';
import { authMiddleware } from '../middleware/auth';

const router = Router();

// 所有路由都需要认证
router.use(authMiddleware);

/**
 * @route   POST /api/v1/vendor-applications
 * @desc    提交供应商申请
 * @access  Private
 */
router.post('/', vendorApplicationController.submitVendorApplication);

/**
 * @route   GET /api/v1/vendor-applications/status
 * @desc    获取用户的申请状态
 * @access  Private
 */
router.get('/status', vendorApplicationController.getVendorApplicationStatus);

/**
 * @route   GET /api/v1/vendor-applications
 * @desc    获取所有供应商申请（管理员）
 * @access  Admin
 */
router.get('/', vendorApplicationController.getAllVendorApplications);

/**
 * @route   PUT /api/v1/vendor-applications/:id/review
 * @desc    审核供应商申请（管理员）
 * @access  Admin
 */
router.put('/:id/review', vendorApplicationController.reviewVendorApplication);

/**
 * @route   GET /api/v1/vendor-applications/tiers
 * @desc    获取供应商等级配置
 * @access  Public
 */
router.get('/tiers', vendorApplicationController.getVendorTiers);

/**
 * @route   GET /api/v1/vendor-applications/vendor-status
 * @desc    获取用户供应商认证状态
 * @access  Private
 */
router.get('/vendor-status', vendorApplicationController.getUserVendorStatus);

export default router;
