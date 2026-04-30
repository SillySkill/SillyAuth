import { Router } from 'express';
import * as vendorController from '../controllers/vendor.controller';
import { authMiddleware, editorMiddleware } from '../middleware/auth';
import { validate } from '../middleware/validation';
import { vendorSchemas } from '../utils/validation';

const router = Router();

// 所有路由都需要认证
router.use(authMiddleware);

/**
 * @route   GET /api/v1/vendors
 * @desc    获取供应商列表
 * @access  Private
 */
router.get('/', vendorController.getVendors);

/**
 * @route   GET /api/v1/vendors/:id
 * @desc    获取单个供应商
 * @access  Private
 */
router.get('/:id', vendorController.getVendorById);

/**
 * @route   POST /api/v1/vendors
 * @desc    创建供应商
 * @access  Editor
 */
router.post(
  '/',
  editorMiddleware,
  validate(vendorSchemas.create),
  vendorController.createVendor
);

/**
 * @route   PUT /api/v1/vendors/:id
 * @desc    更新供应商
 * @access  Editor
 */
router.put(
  '/:id',
  editorMiddleware,
  validate(vendorSchemas.update),
  vendorController.updateVendor
);

/**
 * @route   PUT /api/v1/vendors/order
 * @desc    批量更新供应商排序
 * @access  Editor
 */
router.put('/order', editorMiddleware, vendorController.updateVendorOrder);

/**
 * @route   DELETE /api/v1/vendors/:id
 * @desc    删除供应商
 * @access  Editor
 */
router.delete('/:id', editorMiddleware, vendorController.deleteVendor);

export default router;
