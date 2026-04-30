import { Request, Response } from 'express';
import { prisma } from '../config/database';
import { successResponse, errorResponse, notFoundResponse } from '../utils/response';
import { logger } from '../utils/logger';

/**
 * 获取技能列表
 */
export async function getSkills(req: Request, res: Response) {
  try {
    const language = (req.query.language as string) || 'zh';
    const category = req.query.category as string;
    const isActive = req.query.isActive;

    const where: any = { language };

    if (category) {
      where.category = category;
    }

    if (isActive !== undefined) {
      where.isActive = isActive === 'true';
    }

    const skills = await prisma.skill.findMany({
      where,
      orderBy: [{ category: 'asc' }, { order: 'asc' }],
    });

    // 按分类分组
    const grouped = skills.reduce((acc: any, skill) => {
      if (!acc[skill.category]) {
        acc[skill.category] = [];
      }
      acc[skill.category].push(skill);
      return acc;
    }, {});

    return res.json(successResponse(grouped));
  } catch (error) {
    logger.error('获取技能列表失败:', error);
    return res.status(500).json(errorResponse('获取技能列表失败'));
  }
}

/**
 * 获取所有技能（扁平结构）
 */
export async function getAllSkills(req: Request, res: Response) {
  try {
    const language = (req.query.language as string) || 'zh';

    const skills = await prisma.skill.findMany({
      where: { language },
      orderBy: [{ category: 'asc' }, { order: 'asc' }],
    });

    return res.json(successResponse(skills));
  } catch (error) {
    logger.error('获取技能列表失败:', error);
    return res.status(500).json(errorResponse('获取技能列表失败'));
  }
}

/**
 * 获取单个技能
 */
export async function getSkillById(req: Request, res: Response) {
  try {
    const { id } = req.params;

    const skill = await prisma.skill.findUnique({
      where: { id },
    });

    if (!skill) {
      return res.status(404).json(notFoundResponse('技能'));
    }

    return res.json(successResponse(skill));
  } catch (error) {
    logger.error('获取技能失败:', error);
    return res.status(500).json(errorResponse('获取技能失败'));
  }
}

/**
 * 创建技能
 */
export async function createSkill(req: Request, res: Response) {
  try {
    const userId = req.user!.userId;
    const data = req.body;

    const skill = await prisma.skill.create({
      data,
    });

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'SKILL_CREATED',
        entity: 'Skill',
        entityId: skill.id,
        details: { name: skill.name, category: skill.category },
      },
    });

    logger.info(`创建技能: ${skill.name}`);

    return res.status(201).json(successResponse(skill, '技能创建成功'));
  } catch (error) {
    logger.error('创建技能失败:', error);
    return res.status(500).json(errorResponse('创建技能失败'));
  }
}

/**
 * 更新技能
 */
export async function updateSkill(req: Request, res: Response) {
  try {
    const { id } = req.params;
    const userId = req.user!.userId;
    const data = req.body;

    const skill = await prisma.skill.update({
      where: { id },
      data,
    });

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'SKILL_UPDATED',
        entity: 'Skill',
        entityId: skill.id,
        details: { name: skill.name, category: skill.category },
      },
    });

    logger.info(`更新技能: ${skill.name}`);

    return res.json(successResponse(skill, '技能更新成功'));
  } catch (error) {
    logger.error('更新技能失败:', error);
    return res.status(500).json(errorResponse('更新技能失败'));
  }
}

/**
 * 删除技能
 */
export async function deleteSkill(req: Request, res: Response) {
  try {
    const { id } = req.params;
    const userId = req.user!.userId;

    const skill = await prisma.skill.findUnique({
      where: { id },
    });

    if (!skill) {
      return res.status(404).json(notFoundResponse('技能'));
    }

    await prisma.skill.delete({
      where: { id },
    });

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'SKILL_DELETED',
        entity: 'Skill',
        entityId: id,
        details: { name: skill.name, category: skill.category },
      },
    });

    logger.info(`删除技能: ${skill.name}`);

    return res.json(successResponse(null, '技能删除成功'));
  } catch (error) {
    logger.error('删除技能失败:', error);
    return res.status(500).json(errorResponse('删除技能失败'));
  }
}

/**
 * 批量更新技能排序
 */
export async function updateSkillOrder(req: Request, res: Response) {
  try {
    const userId = req.user!.userId;
    const { orders } = req.body; // [{id, order}, ...]

    await prisma.$transaction(
      orders.map((item: { id: string; order: number }) =>
        prisma.skill.update({
          where: { id: item.id },
          data: { order: item.order },
        })
      )
    );

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'SKILL_ORDER_UPDATED',
        entity: 'Skill',
        details: { count: orders.length },
      },
    });

    logger.info(`批量更新技能排序: ${orders.length} 项`);

    return res.json(successResponse(null, '技能排序更新成功'));
  } catch (error) {
    logger.error('更新技能排序失败:', error);
    return res.status(500).json(errorResponse('更新排序失败'));
  }
}
