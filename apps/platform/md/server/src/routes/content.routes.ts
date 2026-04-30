import { Router } from 'express';
import * as contentController from '../controllers/content.controller';
import { authMiddleware, editorMiddleware } from '../middleware/auth';
import { validate } from '../middleware/validation';
import { contentSchemas } from '../utils/validation';

const router = Router();

// 所有路由都需要认证
router.use(authMiddleware);

/**
 * @route   GET /api/v1/content
 * @desc    获取内容列表
 * @access  Private
 */
router.get('/', contentController.getContents);

/**
 * @route   GET /api/v1/content/key/:key
 * @desc    根据key获取内容
 * @access  Public
 */
router.get('/key/:key', contentController.getContentByKey);

/**
 * @route   GET /api/v1/content/:id
 * @desc    获取单个内容
 * @access  Private
 */
router.get('/:id', contentController.getContentById);

/**
 * @route   GET /api/v1/content/:id/versions
 * @desc    获取内容版本历史
 * @access  Private
 */
router.get('/:id/versions', contentController.getContentVersions);

/**
 * @route   POST /api/v1/content
 * @desc    创建内容
 * @access  Editor
 */
router.post(
  '/',
  editorMiddleware,
  validate(contentSchemas.create),
  contentController.createContent
);

/**
 * @route   PUT /api/v1/content/:id
 * @desc    更新内容
 * @access  Editor
 */
router.put(
  '/:id',
  editorMiddleware,
  validate(contentSchemas.update),
  contentController.updateContent
);

/**
 * @route   PUT /api/v1/content/:id/publish
 * @desc    发布内容
 * @access  Editor
 */
router.put('/:id/publish', editorMiddleware, contentController.publishContent);

/**
 * @route   DELETE /api/v1/content/:id
 * @desc    删除内容
 * @access  Editor
 */
router.delete('/:id', editorMiddleware, contentController.deleteContent);

export default router;
