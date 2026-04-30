import { Request, Response } from 'express';
import { prisma } from '../config/database';
import { successResponse, errorResponse } from '../utils/response';
import { logger } from '../utils/logger';

/**
 * 公共 API 控制器
 * 无需认证的公开接口
 */

/**
 * 获取市场统计数据（公开）
 *
 * @route   GET /api/v1/public/market/stats
 * @desc    获取平台统计数据，包括 Skills、供应商、团队等数量
 * @access  Public
 */
export async function getMarketStats(req: Request, res: Response) {
  try {
    // 并行获取各种统计数据
    const [
      totalSkills,
      totalVendors,
      totalTeams,
      totalUsers,
      totalDownloads,
    ] = await Promise.all([
      // Skills 总数（仅统计已审核通过的）
      prisma.skill.count({
        where: {
          status: 'approved',
          is_deleted: false,
        },
      }),

      // 认证供应商总数
      prisma.vendor_verification.count({
        where: {
          is_verified: true,
        },
      }),

      // 团队总数
      prisma.team.count(),

      // 活跃用户总数
      prisma.user.count({
        where: {
          status: 'ACTIVE',
        },
      }),

      // 总下载量（聚合查询）
      prisma.skill.aggregate({
        where: {
          status: 'approved',
          is_deleted: false,
        },
        _sum: {
          download_count: true,
        },
      }),
    ]);

    const stats = {
      total_skills: totalSkills || 0,
      total_vendors: totalVendors || 0,
      total_teams: totalTeams || 0,
      total_users: totalUsers || 0,
      total_downloads: totalDownloads._sum.download_count || 0,
      ai_accuracy: '99.9%', // AI 审核准确率（固定值，可后续从配置读取）
    };

    logger.info('获取市场统计数据成功', { stats });
    return res.json(successResponse(stats));
  } catch (error) {
    logger.error('获取市场统计数据失败:', error);
    return res.status(500).json(errorResponse('获取统计数据失败'));
  }
}

/**
 * 获取 Skills 列表（公开）
 *
 * @route   GET /api/v1/public/skills
 * @desc    获取公开的 Skills 列表，支持筛选、排序和分页
 * @access  Public
 *
 * @query   type - Skills 类型 (free/commercial)
 * @query   category - 分类 (tech/product/design/marketing/operations)
 * @query   status - 状态 (默认: approved)
 * @query   is_featured - 是否精选
 * @query   limit - 返回数量 (默认: 10, 最大: 50)
 * @query   sort - 排序字段 (默认: download_count)
 * @query   page - 页码 (默认: 1)
 */
export async function getPublicSkills(req: Request, res: Response) {
  try {
    const {
      type,
      category,
      status = 'approved',
      is_featured,
      limit = '10',
      sort = 'download_count',
      page = '1',
    } = req.query;

    // 构建查询条件
    const where: any = {
      is_deleted: false,
    };

    // 状态筛选
    if (status && typeof status === 'string') {
      where.status = status;
    }

    // 类型筛选
    if (type && typeof type === 'string') {
      where.type = type;
    }

    // 分类筛选
    if (category && typeof category === 'string') {
      where.category = category;
    }

    // 精选筛选
    if (is_featured !== undefined) {
      where.is_featured = is_featured === 'true';
    }

    // 分页参数
    const pageNum = parseInt(page as string);
    const limitNum = Math.min(parseInt(limit as string), 50); // 最多返回50条
    const skip = (pageNum - 1) * limitNum;

    // 查询 Skills 列表
    const [skills, total] = await Promise.all([
      prisma.skill.findMany({
        where,
        skip,
        take: limitNum,
        orderBy: {
          [sort as string]: 'desc',
        },
        select: {
          skill_id: true,
          name: true,
          description: true,
          author_id: true,
          category: true,
          type: true,
          price: true,
          version: true,
          status: true,
          is_featured: true,
          published_at: true,
          view_count: true,
          download_count: true,
          favorite_count: true,
          rating_avg: true,
          rating_count: true,
          created_at: true,
          updated_at: true,
        },
      }),
      prisma.skill.count({ where }),
    ]);

    logger.info('获取 Skills 列表成功', {
      count: skills.length,
      total,
      page: pageNum,
    });

    return res.json(
      successResponse(skills, {
        page: pageNum,
        limit: limitNum,
        total,
        totalPages: Math.ceil(total / limitNum),
      })
    );
  } catch (error) {
    logger.error('获取 Skills 列表失败:', error);
    return res.status(500).json(errorResponse('获取 Skills 列表失败'));
  }
}

/**
 * 获取供应商列表（公开）
 *
 * @route   GET /api/v1/public/vendors
 * @desc    获取公开的供应商列表，支持筛选和排序
 * @access  Public
 *
 * @query   is_verified - 是否认证 (true/false)
 * @query   limit - 返回数量 (默认: 10, 最大: 50)
 * @query   sort - 排序字段 (rating/download_count)
 * @query   page - 页码 (默认: 1)
 */
export async function getPublicVendors(req: Request, res: Response) {
  try {
    const { is_verified, limit = '10', sort = 'rating', page = '1' } = req.query;

    // 分页参数
    const pageNum = parseInt(page as string);
    const limitNum = Math.min(parseInt(limit as string), 50);
    const skip = (pageNum - 1) * limitNum;

    // 构建查询条件
    const where: any = {
      status: 'ACTIVE',
    };

    // 认证筛选
    if (is_verified === 'true') {
      where.vendor_verifications = {
        some: {
          is_verified: true,
        },
      };
    }

    // 查询供应商
    const vendors = await prisma.user.findMany({
      where,
      skip,
      take: limitNum,
      include: {
        _count: {
          select: {
            skills: {
              where: {
                status: 'approved',
                is_deleted: false,
              },
            },
          },
        },
        skills: {
          where: {
            status: 'approved',
            is_deleted: false,
          },
          select: {
            download_count: true,
            rating_avg: true,
            rating_count: true,
          },
        },
        vendor_verifications: {
          select: {
            is_verified: true,
            tier_id: true,
          },
        },
      },
      select: {
        id: true,
        username: true,
        email: true,
        bio: true,
        avatar_url: true,
        created_at: true,
        _count: true,
        skills: true,
        vendor_verifications: true,
      },
    });

    // 计算统计数据
    const vendorsWithStats = vendors.map((vendor) => {
      const totalSkills = vendor._count.skills;
      const totalDownloads = vendor.skills.reduce(
        (sum, s) => sum + (s.download_count || 0),
        0
      );

      // 计算平均评分（只考虑有评分的 Skills）
      const ratedSkills = vendor.skills.filter((s) => s.rating_avg !== null);
      const avgRating =
        ratedSkills.length > 0
          ? ratedSkills.reduce((sum, s) => sum + (s.rating_avg || 0), 0) /
            ratedSkills.length
          : 0;

      return {
        id: vendor.id,
        username: vendor.username,
        email: vendor.email,
        bio: vendor.bio || '优质创作者',
        avatar_url: vendor.avatar_url,
        is_verified: vendor.vendor_verifications.length > 0
          ? vendor.vendor_verifications[0].is_verified
          : false,
        total_skills: totalSkills,
        total_downloads: totalDownloads,
        rating_avg: parseFloat(avgRating.toFixed(1)),
        rating_count: ratedSkills.reduce((sum, s) => sum + (s.rating_count || 0), 0),
        created_at: vendor.created_at,
      };
    });

    // 排序
    vendorsWithStats.sort((a, b) => {
      if (sort === 'rating') {
        return b.rating_avg - a.rating_avg;
      }
      if (sort === 'download_count') {
        return b.total_downloads - a.total_downloads;
      }
      return 0;
    });

    // 获取总数（用于分页）
    const total = await prisma.user.count({ where });

    logger.info('获取供应商列表成功', {
      count: vendorsWithStats.length,
      total,
      page: pageNum,
    });

    return res.json(
      successResponse(vendorsWithStats, {
        page: pageNum,
        limit: limitNum,
        total,
        totalPages: Math.ceil(total / limitNum),
      })
    );
  } catch (error) {
    logger.error('获取供应商列表失败:', error);
    return res.status(500).json(errorResponse('获取供应商列表失败'));
  }
}

/**
 * 获取单个 Skill 详情（公开）
 *
 * @route   GET /api/v1/public/skills/:skillId
 * @desc    获取单个 Skill 的详细信息
 * @access  Public
 */
export async function getPublicSkillById(req: Request, res: Response) {
  try {
    const { skillId } = req.params;

    const skill = await prisma.skill.findFirst({
      where: {
        skill_id: skillId,
        is_deleted: false,
        status: 'approved',
      },
      include: {
        author: {
          select: {
            id: true,
            username: true,
            avatar_url: true,
            bio: true,
          },
        },
      },
    });

    if (!skill) {
      return res.status(404).json(errorResponse('Skill 不存在'));
    }

    // 增加浏览量
    await prisma.skill.update({
      where: { id: skill.id },
      data: {
        view_count: {
          increment: 1,
        },
      },
    });

    logger.info('获取 Skill 详情成功', { skillId });
    return res.json(successResponse(skill));
  } catch (error) {
    logger.error('获取 Skill 详情失败:', error);
    return res.status(500).json(errorResponse('获取 Skill 详情失败'));
  }
}

/**
 * 获取分类列表（公开）
 *
 * @route   GET /api/v1/public/skills/categories
 * @desc    获取所有 Skills 分类及其数量
 * @access  Public
 */
export async function getSkillCategories(req: Request, res: Response) {
  try {
    // 聚合查询各分类的 Skills 数量
    const categories = await prisma.skill.groupBy({
      by: ['category'],
      where: {
        is_deleted: false,
        status: 'approved',
      },
      _count: {
        category: true,
      },
    });

    const categoryMap: Record<string, string> = {
      tech: '技术',
      product: '产品',
      design: '设计',
      marketing: '市场',
      operations: '运营',
    };

    const result = categories.map((cat) => ({
      value: cat.category,
      label: categoryMap[cat.category as keyof typeof categoryMap] || cat.category,
      count: cat._count.category,
    }));

    logger.info('获取分类列表成功', { count: result.length });
    return res.json(successResponse(result));
  } catch (error) {
    logger.error('获取分类列表失败:', error);
    return res.status(500).json(errorResponse('获取分类列表失败'));
  }
}
