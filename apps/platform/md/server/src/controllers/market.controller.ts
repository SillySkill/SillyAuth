import { Request, Response } from 'express';
import { Pool } from 'pg';
import { successResponse, errorResponse } from '../utils/response';
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
 * 获取供应商列表
 */
export async function getMarketVendors(req: Request, res: Response) {
  const client = await pool.connect();
  try {
    const {
      tier,
      category,
      search,
      sort = 'total_sales',
      order = 'DESC',
      page = 1,
      limit = 20
    } = req.query;

    const offset = (Number(page) - 1) * Number(limit);

    // 构建查询
    let query = `
      SELECT DISTINCT
        u.id,
        u.username,
        u.email,
        u.avatar_url,
        u.bio,
        u.created_at,
        vv.verification_status,
        vt.tier_name,
        vt.tier_level,
        vt.commission_rate,
        COALESCE(stats.total_skills, 0) as total_skills,
        COALESCE(stats.total_sales, 0) as total_sales,
        COALESCE(stats.total_revenue, 0) as total_revenue,
        COALESCE(stats.rating_avg, 0) as rating_avg,
        COALESCE(stats.review_count, 0) as review_count
      FROM users u
      LEFT JOIN vendor_verifications vv ON u.id = vv.user_id
      LEFT JOIN vendor_tiers vt ON vv.verification_status = 'approved'
      LEFT JOIN (
        SELECT
          creator_id,
          COUNT(DISTINCT content_type || '-' || content_id) as total_skills,
          COUNT(DISTINCT CASE WHEN o.status = 'paid' THEN o.id END) as total_sales,
          COALESCE(SUM(CASE WHEN o.status = 'paid' THEN o.final_price ELSE 0 END), 0) as total_revenue,
          COALESCE(AVG(rating), 0) as rating_avg,
          COUNT(r.id) as review_count
        FROM paid_products pp
        LEFT JOIN orders o ON pp.content_type = o.content_type AND pp.content_id = o.content_id
        LEFT JOIN reviews r ON pp.id = r.product_id
        WHERE pp.creator_id IS NOT NULL
        GROUP BY creator_id
      ) stats ON u.id = stats.creator_id
      WHERE vv.verification_status = 'approved'
    `;

    const params: any[] = [];

    // 过滤条件
    if (tier) {
      query += ` AND vt.tier_name = $${params.length + 1}`;
      params.push(tier);
    }

    if (search) {
      query += ` AND (u.username ILIKE $${params.length + 1} OR u.bio ILIKE $${params.length + 1})`;
      params.push(`%${search}%`);
    }

    // 排序
    const validSortFields = ['total_sales', 'total_revenue', 'rating_avg', 'created_at', 'total_skills'];
    const sortField = validSortFields.includes(sort as string) ? sort : 'total_sales';
    const sortOrder = order === 'ASC' ? 'ASC' : 'DESC';

    query += ` ORDER BY ${sortField} ${sortOrder} LIMIT $${params.length + 1} OFFSET $${params.length + 2}`;
    params.push(Number(limit), offset);

    const result = await client.query(query, params);

    // 获取总数
    let countQuery = `
      SELECT COUNT(DISTINCT u.id)
      FROM users u
      LEFT JOIN vendor_verifications vv ON u.id = vv.user_id
      WHERE vv.verification_status = 'approved'
    `;
    const countParams: any[] = [];

    if (tier) {
      countQuery += ` AND vv.user_id IN (SELECT user_id FROM user_achievements WHERE achievement_id IN (SELECT id FROM achievements WHERE tier_name = $1))`;
      countParams.push(tier);
    }

    if (search) {
      countQuery += ` AND (u.username ILIKE $${countParams.length + 1} OR u.bio ILIKE $${countParams.length + 1})`;
      countParams.push(`%${search}%`);
    }

    const countResult = await client.query(countQuery, countParams);
    const total = parseInt(countResult.rows[0].count);

    return res.json(successResponse({
      vendors: result.rows,
      pagination: {
        page: Number(page),
        limit: Number(limit),
        total,
        totalPages: Math.ceil(total / Number(limit))
      }
    }));
  } catch (error) {
    logger.error('获取供应商列表失败:', error);
    return res.status(500).json(errorResponse('获取供应商列表失败'));
  } finally {
    client.release();
  }
}

/**
 * 获取供应商详情
 */
export async function getVendorProfile(req: Request, res: Response) {
  const client = await pool.connect();
  try {
    const { username } = req.params;

    // 获取供应商基本信息
    const userResult = await client.query(
      `SELECT
        u.id,
        u.username,
        u.email,
        u.avatar_url,
        u.bio,
        u.created_at,
        vv.verification_status,
        vv.verified_at
       FROM users u
       LEFT JOIN vendor_verifications vv ON u.id = vv.user_id
       WHERE u.username = $1`,
      [username]
    );

    if (userResult.rows.length === 0) {
      return res.status(404).json(errorResponse('供应商不存在'));
    }

    const user = userResult.rows[0];

    // 获取供应商统计信息
    const statsResult = await client.query(
      `SELECT
        COUNT(DISTINCT CASE WHEN pp.content_type = 'tutorial' THEN pp.content_id END) as tutorial_count,
        COUNT(DISTINCT CASE WHEN pp.content_type = 'download' THEN pp.content_id END) as download_count,
        COUNT(DISTINCT CASE WHEN o.status = 'paid' THEN o.id END) as total_sales,
        COALESCE(SUM(CASE WHEN o.status = 'paid' THEN o.final_price ELSE 0 END), 0) as total_revenue,
        COALESCE(AVG(r.rating), 0) as avg_rating,
        COUNT(r.id) as total_reviews
       FROM paid_products pp
       LEFT JOIN orders o ON pp.content_type = o.content_type AND pp.content_id = o.content_id
       LEFT JOIN reviews r ON pp.id = r.product_id
       WHERE pp.creator_id = $1`,
      [user.id]
    );

    // 获取供应商的产品列表
    const productsResult = await client.query(
      `SELECT
        pp.id,
        pp.content_type,
        pp.content_id,
        pp.product_name,
        pp.product_description,
        pp.price,
        pp.is_free,
        pp.total_purchases,
        pp.total_revenue,
        pp.created_at,
        COALESCE(AVG(r.rating), 0) as avg_rating
       FROM paid_products pp
       LEFT JOIN reviews r ON pp.id = r.product_id
       WHERE pp.creator_id = $1 AND pp.is_active = true
       GROUP BY pp.id
       ORDER BY pp.created_at DESC
       LIMIT 20`,
      [user.id]
    );

    // 获取供应商等级信息
    const tierResult = await client.query(
      `SELECT
        vt.tier_name,
        vt.tier_level,
        vt.commission_rate,
        vt.benefits,
        vt.description
       FROM vendor_tiers vt
       WHERE vt.is_active = true
       ORDER BY vt.tier_level DESC
       LIMIT 1`
    );

    return res.json(successResponse({
      user: {
        id: user.id,
        username: user.username,
        avatar: user.avatar_url,
        bio: user.bio,
        createdAt: user.created_at,
        verifiedAt: user.verified_at
      },
      stats: statsResult.rows[0] || {},
      products: productsResult.rows,
      tier: tierResult.rows[0] || null
    }));
  } catch (error) {
    logger.error('获取供应商详情失败:', error);
    return res.status(500).json(errorResponse('获取供应商详情失败'));
  } finally {
    client.release();
  }
}

/**
 * 获取市场统计数据
 */
export async function getMarketStats(req: Request, res: Response) {
  const client = await pool.connect();
  try {
    // 总供应商数
    const vendorCountResult = await client.query(
      `SELECT COUNT(DISTINCT user_id) as count
       FROM vendor_verifications
       WHERE verification_status = 'approved'`
    );

    // 总产品数
    const productCountResult = await client.query(
      `SELECT COUNT(*) as count FROM paid_products WHERE is_active = true`
    );

    // 总交易额
    const revenueResult = await client.query(
      `SELECT COALESCE(SUM(final_price), 0) as total
       FROM orders WHERE status = 'paid'`
    );

    // 总订单数
    const orderCountResult = await client.query(
      `SELECT COUNT(*) as count FROM orders WHERE status = 'paid'`
    );

    // 活跃供应商（最近30天有销售）
    const activeVendorResult = await client.query(
      `SELECT COUNT(DISTINCT creator_id) as count
       FROM paid_products pp
       INNER JOIN orders o ON pp.content_type = o.content_type AND pp.content_id = o.content_id
       WHERE o.status = 'paid'
       AND o.paid_at >= CURRENT_DATE - INTERVAL '30 days'`
    );

    return res.json(successResponse({
      totalVendors: parseInt(vendorCountResult.rows[0].count),
      totalProducts: parseInt(productCountResult.rows[0].count),
      totalRevenue: parseFloat(revenueResult.rows[0].total),
      totalOrders: parseInt(orderCountResult.rows[0].count),
      activeVendors: parseInt(activeVendorResult.rows[0].count)
    }));
  } catch (error) {
    logger.error('获取市场统计失败:', error);
    return res.status(500).json(errorResponse('获取统计数据失败'));
  } finally {
    client.release();
  }
}

/**
 * 搜索产品
 */
export async function searchProducts(req: Request, res: Response) {
  const client = await pool.connect();
  try {
    const {
      q,
      category,
      type,
      minPrice,
      maxPrice,
      isFree,
      sort = 'created_at',
      order = 'DESC',
      page = 1,
      limit = 20
    } = req.query;

    const offset = (Number(page) - 1) * Number(limit);

    let query = `
      SELECT
        pp.id,
        pp.content_type,
        pp.content_id,
        pp.product_name,
        pp.product_description,
        pp.price,
        pp.is_free,
        pp.total_purchases,
        pp.total_revenue,
        pp.created_at,
        u.username as creator_username,
        u.avatar_url as creator_avatar,
        COALESCE(AVG(r.rating), 0) as avg_rating,
        COUNT(r.id) as review_count
      FROM paid_products pp
      LEFT JOIN users u ON pp.creator_id = u.id
      LEFT JOIN reviews r ON pp.id = r.product_id
      WHERE pp.is_active = true
    `;

    const params: any[] = [];

    // 搜索条件
    if (q) {
      query += ` AND (pp.product_name ILIKE $${params.length + 1} OR pp.product_description ILIKE $${params.length + 1})`;
      params.push(`%${q}%`);
    }

    if (type) {
      query += ` AND pp.content_type = $${params.length + 1}`;
      params.push(type);
    }

    if (isFree !== undefined) {
      query += ` AND pp.is_free = $${params.length + 1}`;
      params.push(isFree === 'true');
    }

    if (minPrice) {
      query += ` AND pp.price >= $${params.length + 1}`;
      params.push(parseFloat(minPrice as string));
    }

    if (maxPrice) {
      query += ` AND pp.price <= $${params.length + 1}`;
      params.push(parseFloat(maxPrice as string));
    }

    query += ` GROUP BY pp.id, u.username, u.avatar_url`;

    // 排序
    const validSortFields = ['price', 'total_purchases', 'total_revenue', 'avg_rating', 'created_at'];
    const sortField = validSortFields.includes(sort as string) ? sort : 'created_at';
    const sortOrder = order === 'ASC' ? 'ASC' : 'DESC';

    query += ` ORDER BY ${sortField} ${sortOrder} LIMIT $${params.length + 1} OFFSET $${params.length + 2}`;
    params.push(Number(limit), offset);

    const result = await client.query(query, params);

    // 获取总数
    let countQuery = `SELECT COUNT(DISTINCT pp.id) FROM paid_products pp WHERE pp.is_active = true`;
    const countParams: any[] = [];

    if (q) {
      countQuery += ` AND (pp.product_name ILIKE $${countParams.length + 1} OR pp.product_description ILIKE $${countParams.length + 1})`;
      countParams.push(`%${q}%`);
    }

    if (type) {
      countQuery += ` AND pp.content_type = $${countParams.length + 1}`;
      countParams.push(type);
    }

    if (isFree !== undefined) {
      countQuery += ` AND pp.is_free = $${countParams.length + 1}`;
      countParams.push(isFree === 'true');
    }

    if (minPrice) {
      countQuery += ` AND pp.price >= $${countParams.length + 1}`;
      countParams.push(parseFloat(minPrice as string));
    }

    if (maxPrice) {
      countQuery += ` AND pp.price <= $${countParams.length + 1}`;
      countParams.push(parseFloat(maxPrice as string));
    }

    const countResult = await client.query(countQuery, countParams);
    const total = parseInt(countResult.rows[0].count);

    return res.json(successResponse({
      products: result.rows,
      pagination: {
        page: Number(page),
        limit: Number(limit),
        total,
        totalPages: Math.ceil(total / Number(limit))
      }
    }));
  } catch (error) {
    logger.error('搜索产品失败:', error);
    return res.status(500).json(errorResponse('搜索失败'));
  } finally {
    client.release();
  }
}

/**
 * 获取产品详情
 */
export async function getProductDetail(req: Request, res: Response) {
  const client = await pool.connect();
  try {
    const { id } = req.params;

    const result = await client.query(
      `SELECT
        pp.*,
        u.username as creator_username,
        u.avatar_url as creator_avatar,
        u.bio as creator_bio,
        COALESCE(AVG(r.rating), 0) as avg_rating,
        COUNT(r.id) as review_count
       FROM paid_products pp
       LEFT JOIN users u ON pp.creator_id = u.id
       LEFT JOIN reviews r ON pp.id = r.product_id
       WHERE pp.id = $1
       GROUP BY pp.id, u.username, u.avatar_url, u.bio`,
      [id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json(errorResponse('产品不存在'));
    }

    const product = result.rows[0];

    // 获取产品评价
    const reviewsResult = await client.query(
      `SELECT
        r.id,
        r.rating,
        r.comment,
        r.created_at,
        u.username,
        u.avatar_url
       FROM reviews r
       LEFT JOIN users u ON r.user_id = u.id
       WHERE r.product_id = $1
       ORDER BY r.created_at DESC
       LIMIT 10`,
      [id]
    );

    return res.json(successResponse({
      ...product,
      reviews: reviewsResult.rows
    }));
  } catch (error) {
    logger.error('获取产品详情失败:', error);
    return res.status(500).json(errorResponse('获取产品详情失败'));
  } finally {
    client.release();
  }
}
