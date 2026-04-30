import { Router } from 'express';
import * as authController from '../controllers/auth.controller';
import { authMiddleware } from '../middleware/auth';
import { validate } from '../middleware/validation';
import { userSchemas } from '../utils/validation';

const router = Router();

/**
 * @route   POST /api/v1/auth/register
 * @desc    用户注册
 * @access  Public
 */
router.post(
  '/register',
  validate(userSchemas.register),
  authController.register
);

/**
 * @route   POST /api/v1/auth/login
 * @desc    用户登录
 * @access  Public
 */
router.post(
  '/login',
  validate(userSchemas.login),
  authController.login
);

/**
 * @route   GET /api/v1/auth/me
 * @desc    获取当前用户信息
 * @access  Private
 */
router.get('/me', authMiddleware, authController.getCurrentUser);

/**
 * @route   PUT /api/v1/auth/change-password
 * @desc    修改密码
 * @access  Private
 */
router.put('/change-password', authMiddleware, authController.changePassword);

export default router;
