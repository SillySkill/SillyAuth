import { Request, Response } from 'express';
import { prisma } from '../config/database';
import { successResponse, errorResponse, notFoundResponse } from '../utils/response';
import { logger } from '../utils/logger';

/**
 * 获取供应商列表
 */
export async function getVendors(req: Request, res: Response) {
  try {
    const language = (req.query.language as string) || 'zh';
    const isActive = req.query.isActive;

    const where: any = { language };

    if (isActive !== undefined) {
      where.isActive = isActive === 'true';
    }

    const vendors = await prisma.vendor.findMany({
      where,
      orderBy: { order: 'asc' },
    });

    return res.json(successResponse(vendors));
  } catch (error) {
    logger.error('获取供应商列表失败:', error);
    return res.status(500).json(errorResponse('获取供应商列表失败'));
  }
}

/**
 * 获取单个供应商
 */
export async function getVendorById(req: Request, res: Response) {
  try {
    const { id } = req.params;

    const vendor = await prisma.vendor.findUnique({
      where: { id },
    });

    if (!vendor) {
      return res.status(404).json(notFoundResponse('供应商'));
    }

    return res.json(successResponse(vendor));
  } catch (error) {
    logger.error('获取供应商失败:', error);
    return res.status(500).json(errorResponse('获取供应商失败'));
  }
}

/**
 * 创建供应商
 */
export async function createVendor(req: Request, res: Response) {
  try {
    const userId = req.user!.userId;
    const data = req.body;

    const vendor = await prisma.vendor.create({
      data,
    });

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'VENDOR_CREATED',
        entity: 'Vendor',
        entityId: vendor.id,
        details: { name: vendor.name },
      },
    });

    logger.info(`创建供应商: ${vendor.name}`);

    return res.status(201).json(successResponse(vendor, '供应商创建成功'));
  } catch (error) {
    logger.error('创建供应商失败:', error);
    return res.status(500).json(errorResponse('创建供应商失败'));
  }
}

/**
 * 更新供应商
 */
export async function updateVendor(req: Request, res: Response) {
  try {
    const { id } = req.params;
    const userId = req.user!.userId;
    const data = req.body;

    const vendor = await prisma.vendor.update({
      where: { id },
      data,
    });

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'VENDOR_UPDATED',
        entity: 'Vendor',
        entityId: vendor.id,
        details: { name: vendor.name },
      },
    });

    logger.info(`更新供应商: ${vendor.name}`);

    return res.json(successResponse(vendor, '供应商更新成功'));
  } catch (error) {
    logger.error('更新供应商失败:', error);
    return res.status(500).json(errorResponse('更新供应商失败'));
  }
}

/**
 * 删除供应商
 */
export async function deleteVendor(req: Request, res: Response) {
  try {
    const { id } = req.params;
    const userId = req.user!.userId;

    const vendor = await prisma.vendor.findUnique({
      where: { id },
    });

    if (!vendor) {
      return res.status(404).json(notFoundResponse('供应商'));
    }

    await prisma.vendor.delete({
      where: { id },
    });

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'VENDOR_DELETED',
        entity: 'Vendor',
        entityId: id,
        details: { name: vendor.name },
      },
    });

    logger.info(`删除供应商: ${vendor.name}`);

    return res.json(successResponse(null, '供应商删除成功'));
  } catch (error) {
    logger.error('删除供应商失败:', error);
    return res.status(500).json(errorResponse('删除供应商失败'));
  }
}

/**
 * 批量更新供应商排序
 */
export async function updateVendorOrder(req: Request, res: Response) {
  try {
    const userId = req.user!.userId;
    const { orders } = req.body; // [{id, order}, ...]

    await prisma.$transaction(
      orders.map((item: { id: string; order: number }) =>
        prisma.vendor.update({
          where: { id: item.id },
          data: { order: item.order },
        })
      )
    );

    // 记录操作日志
    await prisma.activityLog.create({
      data: {
        userId,
        action: 'VENDOR_ORDER_UPDATED',
        entity: 'Vendor',
        details: { count: orders.length },
      },
    });

    logger.info(`批量更新供应商排序: ${orders.length} 项`);

    return res.json(successResponse(null, '供应商排序更新成功'));
  } catch (error) {
    logger.error('更新供应商排序失败:', error);
    return res.status(500).json(errorResponse('更新排序失败'));
  }
}
