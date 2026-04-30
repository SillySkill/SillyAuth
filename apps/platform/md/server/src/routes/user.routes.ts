import { Router } from 'express';
import * as userController from '../controllers/user.controller';
import { authMiddleware, adminMiddleware } from '../middleware/auth';
import { validate } from '../middleware/validation';
import { userSchemas } from '../utils/validation';

const router = Router();

// 所有路由都需要管理员权限
router.use(authMiddleware);

/**
 * @route   GET /api/v1/users
 * @desc    获取用户列表
 * @access  Admin
 */
router.get('/', adminMiddleware, userController.getUsers);

/**
 * @route   GET /api/v1/users/:id
 * @desc    获取单个用户
 * @access  Admin
 */
router.get('/:id', adminMiddleware, userController.getUserById);

/**
 * @route   POST /api/v1/users
 * @desc    创建用户
 * @access  Admin
 */
router.post(
  '/',
  adminMiddleware,
  validate(userSchemas.register),
  userController.createUser
);

/**
 * @route   PUT /api/v1/users/:id
 * @desc    更新用户
 * @access  Admin
 */
router.put(
  '/:id',
  adminMiddleware,
  validate(userSchemas.update),
  userController.updateUser
);

/**
 * @route   PUT /api/v1/users/:id/status
 * @desc    更新用户状态
 * @access  Admin
 */
router.put('/:id/status', adminMiddleware, userController.updateUserStatus);

/**
 * @route   DELETE /api/v1/users/:id
 * @desc    删除用户
 * @access  Admin
 */
router.delete('/:id', adminMiddleware, userController.deleteUser);

export default router;
