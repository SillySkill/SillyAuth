/**
 * 二维码登录路由
 */

import { Router } from 'express';
import * as qrcodeController from '../controllers/qrcode.controller';
import { authMiddleware } from '../middleware/auth';

const router = Router();

/**
 * @route   POST /api/v1/qrcode/generate
 * @desc    生成二维码
 * @access  Public (但需要图形验证码防止滥用)
 */
router.post('/generate', qrcodeController.generateQRCode);

/**
 * @route   GET /api/v1/qrcode/:code/status
 * @desc    检查二维码状态（PC端轮询）
 * @access  Public
 */
router.get('/:code/status', qrcodeController.checkQRStatus);

/**
 * @route   POST /api/v1/qrcode/:code/scan
 * @desc    扫码（移动端操作）
 * @access  Private
 */
router.post('/:code/scan', authMiddleware, qrcodeController.scanQRCode);

/**
 * @route   POST /api/v1/qrcode/:code/confirm
 * @desc    确认登录（移动端操作）
 * @access  Private
 */
router.post('/:code/confirm', authMiddleware, qrcodeController.confirmLogin);

/**
 * @route   POST /api/v1/qrcode/:code/cancel
 * @desc    取消登录
 * @access  Private
 */
router.post('/:code/cancel', authMiddleware, qrcodeController.cancelLogin);

export default router;
