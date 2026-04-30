import { Router } from 'express';
import * as navigationController from '../controllers/navigation.controller';
import { authMiddleware, editorMiddleware } from '../middleware/auth';
import { validate } from '../middleware/validation';
import { navigationSchemas } from '../utils/validation';

const router = Router();

// 所有路由都需要认证
router.use(authMiddleware);

/**
 * @route   GET /api/v1/navigation/tree
 * @desc    获取导航树结构
 * @access  Private
 */
router.get('/tree', navigationController.getNavigationTree);

/**
 * @route   GET /api/v1/navigation
 * @desc    获取所有导航（扁平）
 * @access  Private
 */
router.get('/', navigationController.getNavigations);

/**
 * @route   GET /api/v1/navigation/:id
 * @desc    获取单个导航
 * @access  Private
 */
router.get('/:id', navigationController.getNavigationById);

/**
 * @route   POST /api/v1/navigation
 * @desc    创建导航
 * @access  Editor
 */
router.post(
  '/',
  editorMiddleware,
  validate(navigationSchemas.create),
  navigationController.createNavigation
);

/**
 * @route   PUT /api/v1/navigation/:id
 * @desc    更新导航
 * @access  Editor
 */
router.put(
  '/:id',
  editorMiddleware,
  validate(navigationSchemas.update),
  navigationController.updateNavigation
);

/**
 * @route   PUT /api/v1/navigation/order
 * @desc    批量更新导航排序
 * @access  Editor
 */
router.put('/order', editorMiddleware, navigationController.updateNavigationOrder);

/**
 * @route   DELETE /api/v1/navigation/:id
 * @desc    删除导航
 * @access  Editor
 */
router.delete('/:id', editorMiddleware, navigationController.deleteNavigation);

export default router;
