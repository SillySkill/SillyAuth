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
 * 提交供应商申请
 */
export async function submitVendorApplication(req: Request, res: Response) {
  const client = await pool.connect();
  try {
    const userId = req.user?.userId;
    if (!userId) {
      return res.status(401).json(errorResponse('未登录'));
    }

    const {
      realName,
      idCardNumber,
      professionalField,
      yearsOfExperience,
      bio,
      portfolioUrls
    } = req.body;

    // 验证必填字段
    if (!realName || !idCardNumber || !professionalField || !yearsOfExperience) {
      return res.status(400).json(errorResponse('请填写所有必填字段'));
    }

    // 检查是否已有待审核的申请
    const existingApplication = await client.query(
      `SELECT id, application_status FROM vendor_applications
       WHERE user_id = $1 AND application_status IN ('pending', 'reviewing')
       ORDER BY created_at DESC LIMIT 1`,
      [userId]
    );

    if (existingApplication.rows.length > 0) {
      return res.status(400).json(errorResponse('您已有待审核的申请，请耐心等待'));
    }

    // 创建申请
    const result = await client.query(
      `INSERT INTO vendor_applications
       (user_id, real_name, id_card_number, professional_field, years_of_experience, bio, portfolio_urls, application_status)
       VALUES ($1, $2, $3, $4, $5, $6, $7, 'pending')
       RETURNING *`,
      [userId, realName, idCardNumber, professionalField, yearsOfExperience, bio, JSON.stringify(portfolioUrls || [])]
    );

    const application = result.rows[0];

    logger.info(`用户 ${userId} 提交供应商申请`);

    return res.status(201).json(successResponse({
      id: application.id,
      status: application.application_status,
      createdAt: application.created_at
    }, '申请提交成功，我们将在 3-5 个工作日内审核'));
  } catch (error) {
    logger.error('提交供应商申请失败:', error);
    return res.status(500).json(errorResponse('提交申请失败，请稍后重试'));
  } finally {
    client.release();
  }
}

/**
 * 获取用户的供应商申请状态
 */
export async function getVendorApplicationStatus(req: Request, res: Response) {
  const client = await pool.connect();
  try {
    const userId = req.user?.userId;
    if (!userId) {
      return res.status(401).json(errorResponse('未登录'));
    }

    const result = await client.query(
      `SELECT
        id,
        real_name,
        professional_field,
        years_of_experience,
        bio,
        portfolio_urls,
        application_status,
        rejection_reason,
        created_at,
        reviewed_at
       FROM vendor_applications
       WHERE user_id = $1
       ORDER BY created_at DESC
       LIMIT 1`,
      [userId]
    );

    if (result.rows.length === 0) {
      return res.json(successResponse(null, '暂无申请记录'));
    }

    const application = result.rows[0];

    return res.json(successResponse({
      id: application.id,
      realName: application.real_name,
      professionalField: application.professional_field,
      yearsOfExperience: application.years_of_experience,
      bio: application.bio,
      portfolioUrls: application.portfolio_urls,
      status: application.application_status,
      rejectionReason: application.rejection_reason,
      createdAt: application.created_at,
      reviewedAt: application.reviewed_at
    }));
  } catch (error) {
    logger.error('获取供应商申请状态失败:', error);
    return res.status(500).json(errorResponse('获取申请状态失败'));
  } finally {
    client.release();
  }
}

/**
 * 获取所有供应商申请（管理员）
 */
export async function getAllVendorApplications(req: Request, res: Response) {
  const client = await pool.connect();
  try {
    const { status, page = 1, limit = 20 } = req.query;
    const offset = (Number(page) - 1) * Number(limit);

    let query = `
      SELECT
        va.id,
        va.user_id,
        u.username,
        u.email,
        va.real_name,
        va.professional_field,
        va.years_of_experience,
        va.bio,
        va.portfolio_urls,
        va.application_status,
        va.rejection_reason,
        va.created_at,
        va.reviewed_at
      FROM vendor_applications va
      LEFT JOIN users u ON va.user_id = u.id
      WHERE 1=1
    `;
    const params: any[] = [];

    if (status) {
      query += ` AND va.application_status = $${params.length + 1}`;
      params.push(status);
    }

    query += ` ORDER BY va.created_at DESC LIMIT $${params.length + 1} OFFSET $${params.length + 2}`;
    params.push(Number(limit), offset);

    const result = await client.query(query, params);

    // 获取总数
    let countQuery = 'SELECT COUNT(*) FROM vendor_applications WHERE 1=1';
    const countParams: any[] = [];

    if (status) {
      countQuery += ` AND application_status = $${countParams.length + 1}`;
      countParams.push(status);
    }

    const countResult = await client.query(countQuery, countParams);
    const total = parseInt(countResult.rows[0].count);

    return res.json(successResponse({
      applications: result.rows,
      pagination: {
        page: Number(page),
        limit: Number(limit),
        total,
        totalPages: Math.ceil(total / Number(limit))
      }
    }));
  } catch (error) {
    logger.error('获取供应商申请列表失败:', error);
    return res.status(500).json(errorResponse('获取申请列表失败'));
  } finally {
    client.release();
  }
}

/**
 * 审核供应商申请（管理员）
 */
export async function reviewVendorApplication(req: Request, res: Response) {
  const client = await pool.connect();
  try {
    const { id } = req.params;
    const reviewerId = req.user?.userId;
    const { status, rejectionReason } = req.body;

    if (!['approved', 'rejected'].includes(status)) {
      return res.status(400).json(errorResponse('无效的审核状态'));
    }

    // 获取申请信息
    const applicationResult = await client.query(
      'SELECT user_id, application_status FROM vendor_applications WHERE id = $1',
      [id]
    );

    if (applicationResult.rows.length === 0) {
      return res.status(404).json(notFoundResponse('申请'));
    }

    const application = applicationResult.rows[0];

    if (application.application_status !== 'pending' && application.application_status !== 'reviewing') {
      return res.status(400).json(errorResponse('该申请已被审核'));
    }

    // 更新申请状态
    await client.query(
      `UPDATE vendor_applications
       SET application_status = $1,
           reviewed_by = $2,
           reviewed_at = CURRENT_TIMESTAMP,
           rejection_reason = $3
       WHERE id = $4`,
      [status === 'approved' ? 'approved' : 'rejected', reviewerId, rejectionReason, id]
    );

    // 如果通过，创建或更新供应商认证记录
    if (status === 'approved') {
      await client.query(
        `INSERT INTO vendor_verifications (user_id, verification_status)
         VALUES ($1, 'approved')
         ON CONFLICT (user_id) DO UPDATE
         SET verification_status = 'approved',
             verified_at = CURRENT_TIMESTAMP`,
        [application.user_id]
      );
    }

    logger.info(`管理员 ${reviewerId} 审核供应商申请 ${id}: ${status}`);

    return res.json(successResponse(null, `申请已${status === 'approved' ? '通过' : '拒绝'}`));
  } catch (error) {
    logger.error('审核供应商申请失败:', error);
    return res.status(500).json(errorResponse('审核失败'));
  } finally {
    client.release();
  }
}

/**
 * 获取供应商等级配置
 */
export async function getVendorTiers(req: Request, res: Response) {
  const client = await pool.connect();
  try {
    const result = await client.query(
      `SELECT * FROM vendor_tiers WHERE is_active = true ORDER BY tier_level ASC`
    );

    return res.json(successResponse(result.rows));
  } catch (error) {
    logger.error('获取供应商等级失败:', error);
    return res.status(500).json(errorResponse('获取等级配置失败'));
  } finally {
    client.release();
  }
}

/**
 * 获取用户认证状态
 */
export async function getUserVendorStatus(req: Request, res: Response) {
  const client = await pool.connect();
  try {
    const userId = req.user?.userId;
    if (!userId) {
      return res.status(401).json(errorResponse('未登录'));
    }

    // 检查认证记录
    const verificationResult = await client.query(
      `SELECT
        verification_status,
        verified_at
       FROM vendor_verifications
       WHERE user_id = $1
       ORDER BY created_at DESC
       LIMIT 1`,
      [userId]
    );

    if (verificationResult.rows.length === 0) {
      return res.json(successResponse({
        isVendor: false,
        status: null
      }));
    }

    const verification = verificationResult.rows[0];

    return res.json(successResponse({
      isVendor: verification.verification_status === 'approved',
      status: verification.verification_status,
      verifiedAt: verification.verified_at
    }));
  } catch (error) {
    logger.error('获取供应商状态失败:', error);
    return res.status(500).json(errorResponse('获取状态失败'));
  } finally {
    client.release();
  }
}
