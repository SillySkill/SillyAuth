import { Router } from 'express';
import * as projectController from '../controllers/project.controller';
import { authMiddleware } from '../middleware/auth';

const router = Router();

// 所有路由都需要认证
router.use(authMiddleware);

/**
 * @route   GET /api/v1/projects
 * @desc    获取项目列表
 * @access  Private
 */
router.get('/', projectController.getProjects);

/**
 * @route   GET /api/v1/projects/:id
 * @desc    获取项目详情
 * @access  Private
 */
router.get('/:id', projectController.getProjectById);

/**
 * @route   POST /api/v1/projects
 * @desc    创建项目
 * @access  Private
 */
router.post('/', projectController.createProject);

/**
 * @route   PUT /api/v1/projects/:id
 * @desc    更新项目
 * @access  Private
 */
router.put('/:id', projectController.updateProject);

/**
 * @route   DELETE /api/v1/projects/:id
 * @desc    删除项目
 * @access  Private
 */
router.delete('/:id', projectController.deleteProject);

/**
 * @route   POST /api/v1/projects/:id/skills
 * @desc    添加项目 Skill
 * @access  Private
 */
router.post('/:id/skills', projectController.addProjectSkill);

/**
 * @route   DELETE /api/v1/projects/:id/skills/:skillId
 * @desc    移除项目 Skill
 * @access  Private
 */
router.delete('/:id/skills/:skillId', projectController.removeProjectSkill);

/**
 * @route   POST /api/v1/projects/:id/milestones
 * @desc    创建项目里程碑
 * @access  Private
 */
router.post('/:id/milestones', projectController.createMilestone);

export default router;
