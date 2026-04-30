import { Request, Response } from 'express';
import { Pool } from 'pg';
import { successResponse, errorResponse, notFoundResponse } from '../utils/response';
import { logger } from '../utils/logger';

// PostgreSQL 连接池
const pool = new Pool({
  host: '47.96.133.238',
  port: 5432,
  database: 'sillymd',
  user: 'sillyAdmin',
  password: 'Jcoding2026',
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

/**
 * 获取项目列表
 */
export async function getProjects(req: Request, res: Response) {
  const client = await pool.connect();
  try {
    const userId = req.user?.userId;
    const { teamId, status, page = 1, limit = 20 } = req.query;
    const offset = (Number(page) - 1) * Number(limit);

    let query = `
      SELECT
        tp.id,
        tp.team_id,
        tp.project_name,
        tp.project_slug,
        tp.description,
        tp.owner_id,
        tp.project_status,
        tp.progress,
        tp.is_active,
        tp.created_at,
        tp.updated_at,
        t.team_name,
        u.username as owner_username,
        u.avatar_url as owner_avatar,
        COALESCE(pm.milestones_count, 0) as milestones_count,
        COALESCE(ps.skills_count, 0) as skills_count
      FROM team_projects tp
      LEFT JOIN teams t ON tp.team_id = t.id
      LEFT JOIN users u ON tp.owner_id = u.id
      LEFT JOIN (
        SELECT project_id, COUNT(*) as milestones_count
        FROM project_milestones
        GROUP BY project_id
      ) pm ON tp.id = pm.project_id
      LEFT JOIN (
        SELECT project_id, COUNT(*) as skills_count
        FROM project_skills
        GROUP BY project_id
      ) ps ON tp.id = ps.project_id
      WHERE tp.is_active = true
    `;
    const params: any[] = [];

    // 权限过滤：只返回用户所属团队的项目
    if (userId) {
      query += ` AND EXISTS (
        SELECT 1 FROM team_members tm
        WHERE tm.team_id = tp.team_id
        AND tm.user_id = $${params.length + 1}
      )`;
      params.push(userId);
    }

    if (teamId) {
      query += ` AND tp.team_id = $${params.length + 1}`;
      params.push(teamId);
    }

    if (status) {
      query += ` AND tp.project_status = $${params.length + 1}`;
      params.push(status);
    }

    query += ` ORDER BY tp.updated_at DESC LIMIT $${params.length + 1} OFFSET $${params.length + 2}`;
    params.push(Number(limit), offset);

    const result = await client.query(query, params);

    // 获取总数
    let countQuery = `
      SELECT COUNT(*)
      FROM team_projects tp
      WHERE tp.is_active = true
      AND EXISTS (
        SELECT 1 FROM team_members tm
        WHERE tm.team_id = tp.team_id
        AND tm.user_id = $1
      )
    `;
    const countParams = [userId];

    if (teamId) {
      countQuery += ` AND tp.team_id = $2`;
      countParams.push(teamId);
    }

    if (status) {
      countQuery += ` AND tp.project_status = $${countParams.length + 1}`;
      countParams.push(status);
    }

    const countResult = await client.query(countQuery, countParams);
    const total = parseInt(countResult.rows[0].count);

    return res.json(successResponse({
      projects: result.rows,
      pagination: {
        page: Number(page),
        limit: Number(limit),
        total,
        totalPages: Math.ceil(total / Number(limit))
      }
    }));
  } catch (error) {
    logger.error('获取项目列表失败:', error);
    return res.status(500).json(errorResponse('获取项目列表失败'));
  } finally {
    client.release();
  }
}

/**
 * 获取单个项目详情
 */
export async function getProjectById(req: Request, res: Response) {
  const client = await pool.connect();
  try {
    const { id } = req.params;
    const userId = req.user?.userId;

    const result = await client.query(
      `SELECT
        tp.*,
        t.team_name,
        u.username as owner_username,
        u.avatar_url as owner_avatar
       FROM team_projects tp
       LEFT JOIN teams t ON tp.team_id = t.id
       LEFT JOIN users u ON tp.owner_id = u.id
       WHERE tp.id = $1`,
      [id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json(notFoundResponse('项目'));
    }

    const project = result.rows[0];

    // 检查权限
    const memberCheck = await client.query(
      `SELECT 1 FROM team_members WHERE team_id = $1 AND user_id = $2`,
      [project.team_id, userId]
    );

    if (memberCheck.rows.length === 0) {
      return res.status(403).json(errorResponse('无权访问该项目'));
    }

    // 获取项目关联的 Skills
    const skillsResult = await client.query(
      `SELECT
        ps.id,
        ps.skill_id,
        ps.role,
        ps.order_index,
        s.name,
        s.category,
        s.icon
       FROM project_skills ps
       LEFT JOIN skills s ON ps.skill_id = s.id
       WHERE ps.project_id = $1
       ORDER BY ps.order_index ASC`,
      [id]
    );

    // 获取项目里程碑
    const milestonesResult = await client.query(
      `SELECT * FROM project_milestones
       WHERE project_id = $1
       ORDER BY target_date ASC`,
      [id]
    );

    // 获取项目成员
    const membersResult = await client.query(
      `SELECT
        tm.user_id,
        u.username,
        u.avatar_url,
        tm.role,
        tm.joined_at
       FROM team_members tm
       LEFT JOIN users u ON tm.user_id = u.id
       WHERE tm.team_id = $1`,
      [project.team_id]
    );

    return res.json(successResponse({
      ...project,
      skills: skillsResult.rows,
      milestones: milestonesResult.rows,
      members: membersResult.rows
    }));
  } catch (error) {
    logger.error('获取项目详情失败:', error);
    return res.status(500).json(errorResponse('获取项目详情失败'));
  } finally {
    client.release();
  }
}

/**
 * 创建项目
 */
export async function createProject(req: Request, res: Response) {
  const client = await pool.connect();
  try {
    const userId = req.user?.userId;
    if (!userId) {
      return res.status(401).json(errorResponse('未登录'));
    }

    const { teamId, projectName, projectSlug, description, ownerId } = req.body;

    // 验证必填字段
    if (!teamId || !projectName || !projectSlug) {
      return res.status(400).json(errorResponse('请填写项目名称和标识符'));
    }

    // 检查用户是否是团队成员
    const memberCheck = await client.query(
      `SELECT role FROM team_members WHERE team_id = $1 AND user_id = $2`,
      [teamId, userId]
    );

    if (memberCheck.rows.length === 0) {
      return res.status(403).json(errorResponse('您不是该团队成员'));
    }

    // 验证 slug 唯一性
    const slugCheck = await client.query(
      `SELECT 1 FROM team_projects WHERE team_id = $1 AND project_slug = $2`,
      [teamId, projectSlug]
    );

    if (slugCheck.rows.length > 0) {
      return res.status(400).json(errorResponse('项目标识符已存在'));
    }

    // 创建项目
    const result = await client.query(
      `INSERT INTO team_projects
       (team_id, project_name, project_slug, description, owner_id, project_status, progress)
       VALUES ($1, $2, $3, $4, $5, 'planned', 0)
       RETURNING *`,
      [teamId, projectName, projectSlug, description, ownerId || userId]
    );

    const project = result.rows[0];

    logger.info(`用户 ${userId} 创建项目 ${project.id}`);

    return res.status(201).json(successResponse(project, '项目创建成功'));
  } catch (error) {
    logger.error('创建项目失败:', error);
    return res.status(500).json(errorResponse('创建项目失败'));
  } finally {
    client.release();
  }
}

/**
 * 更新项目
 */
export async function updateProject(req: Request, res: Response) {
  const client = await pool.connect();
  try {
    const { id } = req.params;
    const userId = req.user?.userId;
    const { projectName, description, projectStatus, progress } = req.body;

    // 检查项目是否存在
    const projectResult = await client.query(
      `SELECT tp.*, tm.role FROM team_projects tp
       LEFT JOIN team_members tm ON tp.team_id = tm.team_id
       WHERE tp.id = $1 AND tm.user_id = $2`,
      [id, userId]
    );

    if (projectResult.rows.length === 0) {
      return res.status(404).json(notFoundResponse('项目'));
    }

    const project = projectResult.rows[0];
    const memberRole = project.role;

    // 只有 owner 和 admin 可以编辑
    if (!['owner', 'admin'].includes(memberRole)) {
      return res.status(403).json(errorResponse('只有项目所有者和管理员可以编辑'));
    }

    // 更新项目
    const updateFields: string[] = [];
    const updateValues: any[] = [];
    let paramIndex = 1;

    if (projectName !== undefined) {
      updateFields.push(`project_name = $${paramIndex++}`);
      updateValues.push(projectName);
    }

    if (description !== undefined) {
      updateFields.push(`description = $${paramIndex++}`);
      updateValues.push(description);
    }

    if (projectStatus !== undefined) {
      updateFields.push(`project_status = $${paramIndex++}`);
      updateValues.push(projectStatus);
    }

    if (progress !== undefined) {
      updateFields.push(`progress = $${paramIndex++}`);
      updateValues.push(progress);
    }

    if (updateFields.length === 0) {
      return res.status(400).json(errorResponse('没有要更新的字段'));
    }

    updateValues.push(id);

    const updateResult = await client.query(
      `UPDATE team_projects SET ${updateFields.join(', ')} WHERE id = $${paramIndex} RETURNING *`,
      updateValues
    );

    logger.info(`用户 ${userId} 更新项目 ${id}`);

    return res.json(successResponse(updateResult.rows[0], '项目更新成功'));
  } catch (error) {
    logger.error('更新项目失败:', error);
    return res.status(500).json(errorResponse('更新项目失败'));
  } finally {
    client.release();
  }
}

/**
 * 删除项目
 */
export async function deleteProject(req: Request, res: Response) {
  const client = await pool.connect();
  try {
    const { id } = req.params;
    const userId = req.user?.userId;

    // 检查项目权限
    const projectResult = await client.query(
      `SELECT tp.*, tm.role FROM team_projects tp
       LEFT JOIN team_members tm ON tp.team_id = tm.team_id
       WHERE tp.id = $1 AND tm.user_id = $2`,
      [id, userId]
    );

    if (projectResult.rows.length === 0) {
      return res.status(404).json(notFoundResponse('项目'));
    }

    const project = projectResult.rows[0];

    // 只有 owner 可以删除
    if (project.owner_id !== userId) {
      return res.status(403).json(errorResponse('只有项目所有者可以删除'));
    }

    // 软删除
    await client.query(
      `UPDATE team_projects SET is_active = false WHERE id = $1`,
      [id]
    );

    logger.info(`用户 ${userId} 删除项目 ${id}`);

    return res.json(successResponse(null, '项目删除成功'));
  } catch (error) {
    logger.error('删除项目失败:', error);
    return res.status(500).json(errorResponse('删除项目失败'));
  } finally {
    client.release();
  }
}

/**
 * 添加项目 Skill
 */
export async function addProjectSkill(req: Request, res: Response) {
  const client = await pool.connect();
  try {
    const { id } = req.params;
    const userId = req.user?.userId;
    const { skillId, role, orderIndex } = req.body;

    // 检查项目权限
    const projectResult = await client.query(
      `SELECT tp.*, tm.role FROM team_projects tp
       LEFT JOIN team_members tm ON tp.team_id = tm.team_id
       WHERE tp.id = $1 AND tm.user_id = $2`,
      [id, userId]
    );

    if (projectResult.rows.length === 0) {
      return res.status(404).json(notFoundResponse('项目'));
    }

    // 检查 Skill 是否已存在
    const existingSkill = await client.query(
      `SELECT 1 FROM project_skills WHERE project_id = $1 AND skill_id = $2`,
      [id, skillId]
    );

    if (existingSkill.rows.length > 0) {
      return res.status(400).json(errorResponse('该 Skill 已添加'));
    }

    // 添加 Skill
    const result = await client.query(
      `INSERT INTO project_skills (project_id, skill_id, role, order_index)
       VALUES ($1, $2, $3, $4)
       RETURNING *`,
      [id, skillId, role || 'other', orderIndex || 0]
    );

    logger.info(`项目 ${id} 添加 Skill ${skillId}`);

    return res.status(201).json(successResponse(result.rows[0], 'Skill 添加成功'));
  } catch (error) {
    logger.error('添加项目 Skill 失败:', error);
    return res.status(500).json(errorResponse('添加失败'));
  } finally {
    client.release();
  }
}

/**
 * 移除项目 Skill
 */
export async function removeProjectSkill(req: Request, res: Response) {
  const client = await pool.connect();
  try {
    const { id, skillId } = req.params;
    const userId = req.user?.userId;

    // 检查项目权限
    const projectResult = await client.query(
      `SELECT tp.*, tm.role FROM team_projects tp
       LEFT JOIN team_members tm ON tp.team_id = tm.team_id
       WHERE tp.id = $1 AND tm.user_id = $2`,
      [id, userId]
    );

    if (projectResult.rows.length === 0) {
      return res.status(404).json(notFoundResponse('项目'));
    }

    await client.query(
      `DELETE FROM project_skills WHERE project_id = $1 AND skill_id = $2`,
      [id, skillId]
    );

    logger.info(`项目 ${id} 移除 Skill ${skillId}`);

    return res.json(successResponse(null, 'Skill 移除成功'));
  } catch (error) {
    logger.error('移除项目 Skill 失败:', error);
    return res.status(500).json(errorResponse('移除失败'));
  } finally {
    client.release();
  }
}

/**
 * 创建项目里程碑
 */
export async function createMilestone(req: Request, res: Response) {
  const client = await pool.connect();
  try {
    const { id } = req.params;
    const userId = req.user?.userId;
    const { title, description, targetDate, status } = req.body;

    // 检查项目权限
    const projectResult = await client.query(
      `SELECT tp.*, tm.role FROM team_projects tp
       LEFT JOIN team_members tm ON tp.team_id = tm.team_id
       WHERE tp.id = $1 AND tm.user_id = $2`,
      [id, userId]
    );

    if (projectResult.rows.length === 0) {
      return res.status(404).json(notFoundResponse('项目'));
    }

    // 创建里程碑
    const result = await client.query(
      `INSERT INTO project_milestones (project_id, title, description, target_date, status)
       VALUES ($1, $2, $3, $4, $5)
       RETURNING *`,
      [id, title, description, targetDate, status || 'pending']
    );

    logger.info(`项目 ${id} 创建里程碑`);

    return res.status(201).json(successResponse(result.rows[0], '里程碑创建成功'));
  } catch (error) {
    logger.error('创建里程碑失败:', error);
    return res.status(500).json(errorResponse('创建失败'));
  } finally {
    client.release();
  }
}
