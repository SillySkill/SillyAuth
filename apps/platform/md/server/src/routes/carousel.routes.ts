import { Router } from 'express';
import * as carouselController from '../controllers/carousel.controller';
import { authMiddleware, editorMiddleware } from '../middleware/auth';
import { validate } from '../middleware/validation';
import { carouselSchemas } from '../utils/validation';

const router = Router();

// 所有路由都需要认证
router.use(authMiddleware);

/**
 * @route   GET /api/v1/carousel
 * @desc    获取轮播图列表
 * @access  Private
 */
router.get('/', carouselController.getCarousels);

/**
 * @route   GET /api/v1/carousel/:id
 * @desc    获取单个轮播图
 * @access  Private
 */
router.get('/:id', carouselController.getCarouselById);

/**
 * @route   POST /api/v1/carousel
 * @desc    创建轮播图
 * @access  Editor
 */
router.post(
  '/',
  editorMiddleware,
  validate(carouselSchemas.create),
  carouselController.createCarousel
);

/**
 * @route   PUT /api/v1/carousel/:id
 * @desc    更新轮播图
 * @access  Editor
 */
router.put(
  '/:id',
  editorMiddleware,
  validate(carouselSchemas.update),
  carouselController.updateCarousel
);

/**
 * @route   PUT /api/v1/carousel/:id/toggle
 * @desc    切换轮播图启用状态
 * @access  Editor
 */
router.put('/:id/toggle', editorMiddleware, carouselController.toggleCarousel);

/**
 * @route   PUT /api/v1/carousel/order
 * @desc    批量更新轮播图排序
 * @access  Editor
 */
router.put('/order', editorMiddleware, carouselController.updateCarouselOrder);

/**
 * @route   DELETE /api/v1/carousel/:id
 * @desc    删除轮播图
 * @access  Editor
 */
router.delete('/:id', editorMiddleware, carouselController.deleteCarousel);

export default router;
