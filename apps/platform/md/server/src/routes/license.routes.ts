/**
 * 许可证路由（付费技能防盗版）
 */

import { Router } from 'express';
import * as licenseController from '../controllers/license.controller';
import { authMiddleware } from '../middleware/auth';

const router = Router();

// 需要登录的路由

/**
 * @route   GET /api/v1/licenses
 * @desc    获取用户的许可证列表
 * @access  Private
 */
router.get('/', authMiddleware, licenseController.getUserLicenses);

/**
 * @route   POST /api/v1/licenses
 * @desc    创建许可证（购买技能后）
 * @access  Private (通常由支付回调触发)
 */
router.post('/', authMiddleware, licenseController.createLicense);

/**
 * @route   POST /api/v1/licenses/activate
 * @desc    激活设备
 * @access  Private
 */
router.post('/activate', authMiddleware, licenseController.activateDevice);

/**
 * @route   POST /api/v1/licenses/verify
 * @desc    验证设备许可证
 * @access  Private
 */
router.post('/verify', authMiddleware, licenseController.verifyLicense);

/**
 * @route   DELETE /api/v1/licenses/:licenseId/devices/:deviceId
 * @desc    移除设备
 * @access  Private
 */
router.delete('/:licenseId/devices/:deviceId', authMiddleware, licenseController.removeDevice);

/**
 * @route   DELETE /api/v1/licenses/:licenseKey
 * @desc    停用许可证
 * @access  Private
 */
router.delete('/:licenseKey', authMiddleware, licenseController.deactivateLicense);

export default router;
