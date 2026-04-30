import { Router } from 'express';
import * as uploadController from '../controllers/upload.controller';
import { authMiddleware, editorMiddleware } from '../middleware/auth';
import { uploadSingle, uploadMultiple } from '../middleware/upload';

const router = Router();

// 所有路由都需要认证
router.use(authMiddleware);

/**
 * @route   POST /api/v1/upload
 * @desc    上传单个文件
 * @access  Editor
 */
router.post(
  '/',
  editorMiddleware,
  uploadSingle('file'),
  uploadController.uploadFile
);

/**
 * @route   POST /api/v1/upload/batch
 * @desc    上传多个文件
 * @access  Editor
 */
router.post(
  '/batch',
  editorMiddleware,
  uploadMultiple('files', 10),
  uploadController.uploadFiles
);

/**
 * @route   GET /api/v1/upload
 * @desc    获取媒体文件列表
 * @access  Private
 */
router.get('/', uploadController.getMediaList);

/**
 * @route   DELETE /api/v1/upload/:id
 * @desc    删除媒体文件
 * @access  Editor
 */
router.delete('/:id', editorMiddleware, uploadController.deleteMedia);

export default router;
