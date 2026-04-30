import { Router } from 'express';
import * as skillController from '../controllers/skill.controller';
import { authMiddleware, editorMiddleware } from '../middleware/auth';
import { validate } from '../middleware/validation';
import { skillSchemas } from '../utils/validation';

const router = Router();

// 所有路由都需要认证
router.use(authMiddleware);

/**
 * @route   GET /api/v1/skills
 * @desc    获取技能列表（分组）
 * @access  Private
 */
router.get('/', skillController.getSkills);

/**
 * @route   GET /api/v1/skills/all
 * @desc    获取所有技能（扁平）
 * @access  Private
 */
router.get('/all', skillController.getAllSkills);

/**
 * @route   GET /api/v1/skills/:id
 * @desc    获取单个技能
 * @access  Private
 */
router.get('/:id', skillController.getSkillById);

/**
 * @route   POST /api/v1/skills
 * @desc    创建技能
 * @access  Editor
 */
router.post(
  '/',
  editorMiddleware,
  validate(skillSchemas.create),
  skillController.createSkill
);

/**
 * @route   PUT /api/v1/skills/:id
 * @desc    更新技能
 * @access  Editor
 */
router.put(
  '/:id',
  editorMiddleware,
  validate(skillSchemas.update),
  skillController.updateSkill
);

/**
 * @route   PUT /api/v1/skills/order
 * @desc    批量更新技能排序
 * @access  Editor
 */
router.put('/order', editorMiddleware, skillController.updateSkillOrder);

/**
 * @route   DELETE /api/v1/skills/:id
 * @desc    删除技能
 * @access  Editor
 */
router.delete('/:id', editorMiddleware, skillController.deleteSkill);

export default router;
