/**
 * 傻福虾群组路由
 */

import { Router } from 'express';
import * as shrimpGroupController from '../controllers/shrimp-group.controller';
import { authMiddleware, adminMiddleware } from '../middleware/auth';

const router = Router();

// 公开路由
/**
 * @route   GET /api/v1/shrimp-groups
 * @desc    获取所有活跃群组
 * @access  Public
 */
router.get('/', shrimpGroupController.getGroups);

/**
 * @route   GET /api/v1/shrimp-groups/:groupKey/members
 * @desc    获取群组成员列表
 * @access  Public
 */
router.get('/:groupKey/members', shrimpGroupController.getGroupMembers);

// 需要登录的路由
router.use(authMiddleware);

/**
 * @route   GET /api/v1/shrimp-groups/my
 * @desc    获取用户所在的群组
 * @access  Private
 */
router.get('/my/groups', shrimpGroupController.getUserGroups);

/**
 * @route   POST /api/v1/shrimp-groups/join
 * @desc    随机加入一个群组
 * @access  Private
 */
router.post('/join', shrimpGroupController.joinRandomGroup);

// 管理员路由
router.use(adminMiddleware);

/**
 * @route   POST /api/v1/shrimp-groups
 * @desc    创建群组
 * @access  Admin
 */
router.post('/', shrimpGroupController.createGroup);

/**
 * @route   PUT /api/v1/shrimp-groups/:id
 * @desc    更新群组
 * @access  Admin
 */
router.put('/:id', shrimpGroupController.updateGroup);

/**
 * @route   DELETE /api/v1/shrimp-groups/:id
 * @desc    删除群组
 * @access  Admin
 */
router.delete('/:id', shrimpGroupController.deleteGroup);

export default router;
