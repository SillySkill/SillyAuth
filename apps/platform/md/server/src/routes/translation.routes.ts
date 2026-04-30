import { Router } from 'express';
import * as translationController from '../controllers/translation.controller';
import { authMiddleware, editorMiddleware } from '../middleware/auth';
import { validate } from '../middleware/validation';
import { translationSchemas } from '../utils/validation';

const router = Router();

// 所有路由都需要认证
router.use(authMiddleware);

/**
 * @route   GET /api/v1/translations
 * @desc    获取所有翻译
 * @access  Private
 */
router.get('/', translationController.getTranslations);

/**
 * @route   GET /api/v1/translations/:key/:language
 * @desc    获取单个翻译
 * @access  Private
 */
router.get('/:key/:language', translationController.getTranslationByKey);

/**
 * @route   PUT /api/v1/translations/:key/:language
 * @desc    创建或更新翻译
 * @access  Editor
 */
router.put(
  '/:key/:language',
  editorMiddleware,
  validate(translationSchemas.update),
  translationController.upsertTranslation
);

/**
 * @route   POST /api/v1/translations/batch
 * @desc    批量创建或更新翻译
 * @access  Editor
 */
router.post('/batch', editorMiddleware, translationController.batchUpsertTranslations);

/**
 * @route   GET /api/v1/translations/export
 * @desc    导出翻译
 * @access  Private
 */
router.get('/export', translationController.exportTranslations);

/**
 * @route   GET /api/v1/translations/missing
 * @desc    获取缺失的翻译
 * @access  Private
 */
router.get('/missing', translationController.getMissingTranslations);

/**
 * @route   DELETE /api/v1/translations/:key/:language
 * @desc    删除翻译
 * @access  Editor
 */
router.delete('/:key/:language', editorMiddleware, translationController.deleteTranslation);

export default router;
