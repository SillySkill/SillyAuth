/**
 * 二维码登录控制器
 * 处理扫码登录相关的业务逻辑
 */

import { Request, Response } from 'express';
import { PrismaClient } from '@prisma/client';
import { v4 as uuidv4 } from 'uuid';

const prisma = new PrismaClient();

// 生成二维码
export const generateQRCode = async (req: Request, res: Response): Promise<void> => {
  try {
    // 生成唯一的二维码标识
    const code = uuidv4().replace(/-/g, '').substring(0, 16);
    const expiresAt = new Date(Date.now() + 5 * 60 * 1000); // 5分钟后过期

    // 创建二维码会话
    const session = await prisma.qRCodeSession.create({
      data: {
        code,
        expiresAt,
        status: 'PENDING'
      }
    });

    // 返回二维码数据（实际项目中这里会生成二维码图片）
    res.json({
      success: true,
      data: {
        sessionId: session.id,
        code: session.code,
        expiresAt: session.expiresAt,
        // 前端可以使用 this code 生成二维码
        // 建议前端使用 qrcode 库生成二维码图片
      }
    });
  } catch (error) {
    console.error('生成二维码失败:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'GENERATE_QR_FAILED',
        message: '生成二维码失败'
      }
    });
  }
};

// 检查二维码状态（前端轮询）
export const checkQRStatus = async (req: Request, res: Response): Promise<void> => {
  try {
    const { code } = req.params;

    const session = await prisma.qRCodeSession.findUnique({
      where: { code },
      include: {
        user: {
          select: {
            id: true,
            username: true,
            email: true,
            avatar: true,
            role: true
          }
        }
      }
    });

    if (!session) {
      res.status(404).json({
        success: false,
        error: { code: 'SESSION_NOT_FOUND', message: '二维码不存在' }
      });
      return;
    }

    // 检查是否过期
    if (new Date() > session.expiresAt && session.status === 'PENDING') {
      await prisma.qRCodeSession.update({
        where: { id: session.id },
        data: { status: 'EXPIRED' }
      });

      res.json({
        success: true,
        data: {
          status: 'EXPIRED',
          message: '二维码已过期，请刷新重试'
        }
      });
      return;
    }

    res.json({
      success: true,
      data: {
        status: session.status,
        expiresAt: session.expiresAt,
        user: session.status === 'CONFIRMED' ? session.user : null,
        scannedAt: session.scannedAt,
        confirmedAt: session.confirmedAt
      }
    });
  } catch (error) {
    console.error('检查二维码状态失败:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'CHECK_QR_FAILED',
        message: '检查二维码状态失败'
      }
    });
  }
};

// 扫码确认登录（移动端操作）
export const scanQRCode = async (req: Request, res: Response): Promise<void> => {
  try {
    const { code } = req.params;
    const userId = (req as any).user?.id;

    if (!userId) {
      res.status(401).json({
        success: false,
        error: { code: 'UNAUTHORIZED', message: '请先登录' }
      });
      return;
    }

    const session = await prisma.qRCodeSession.findUnique({
      where: { code }
    });

    if (!session) {
      res.status(404).json({
        success: false,
        error: { code: 'SESSION_NOT_FOUND', message: '二维码不存在' }
      });
      return;
    }

    if (session.status !== 'PENDING') {
      res.status(400).json({
        success: false,
        error: { code: 'INVALID_STATUS', message: '二维码状态无效' }
      });
      return;
    }

    if (new Date() > session.expiresAt) {
      res.status(400).json({
        success: false,
        error: { code: 'EXPIRED', message: '二维码已过期' }
      });
      return;
    }

    // 更新会话状态为已扫描
    const updatedSession = await prisma.qRCodeSession.update({
      where: { id: session.id },
      data: {
        status: 'SCANNED',
        userId,
        scannedAt: new Date()
      }
    });

    res.json({
      success: true,
      data: {
        status: 'SCANNED',
        expiresAt: updatedSession.expiresAt,
        message: '扫码成功，请在手机上确认登录'
      }
    });
  } catch (error) {
    console.error('扫码失败:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'SCAN_QR_FAILED',
        message: '扫码失败'
      }
    });
  }
};

// 确认登录（移动端操作）
export const confirmLogin = async (req: Request, res: Response): Promise<void> => {
  try {
    const { code } = req.params;

    const session = await prisma.qRCodeSession.findUnique({
      where: { code }
    });

    if (!session) {
      res.status(404).json({
        success: false,
        error: { code: 'SESSION_NOT_FOUND', message: '二维码不存在' }
      });
      return;
    }

    if (session.status !== 'SCANNED') {
      res.status(400).json({
        success: false,
        error: { code: 'INVALID_STATUS', message: '请先扫码' }
      });
      return;
    }

    if (new Date() > session.expiresAt) {
      await prisma.qRCodeSession.update({
        where: { id: session.id },
        data: { status: 'EXPIRED' }
      });

      res.status(400).json({
        success: false,
        error: { code: 'EXPIRED', message: '二维码已过期' }
      });
      return;
    }

    // 生成JWT Token
    const jwt = require('jsonwebtoken');
    const config = require('../config');

    const token = jwt.sign(
      {
        userId: session.userId,
        sessionId: session.id
      },
      config.JWT_SECRET || 'sillymd-secret',
      { expiresIn: '7d' }
    );

    // 更新会话状态为已确认
    await prisma.qRCodeSession.update({
      where: { id: session.id },
      data: {
        status: 'CONFIRMED',
        confirmedAt: new Date()
      }
    });

    // 获取用户信息
    const user = await prisma.user.findUnique({
      where: { id: session.userId },
      select: {
        id: true,
        username: true,
        email: true,
        avatar: true,
        role: true
      }
    });

    res.json({
      success: true,
      data: {
        token,
        user,
        expiresIn: '7d'
      }
    });
  } catch (error) {
    console.error('确认登录失败:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'CONFIRM_LOGIN_FAILED',
        message: '确认登录失败'
      }
    });
  }
};

// 取消登录
export const cancelLogin = async (req: Request, res: Response): Promise<void> => {
  try {
    const { code } = req.params;

    await prisma.qRCodeSession.update({
      where: { code },
      data: { status: 'CANCELLED' }
    });

    res.json({
      success: true,
      message: '已取消登录'
    });
  } catch (error) {
    console.error('取消登录失败:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'CANCEL_LOGIN_FAILED',
        message: '取消登录失败'
      }
    });
  }
};

// 清理过期会话（定时任务）
export const cleanupExpiredSessions = async (): Promise<void> => {
  try {
    const result = await prisma.qRCodeSession.updateMany({
      where: {
        status: 'PENDING',
        expiresAt: { lt: new Date() }
      },
      data: { status: 'EXPIRED' }
    });

    console.log(`清理了 ${result.count} 个过期的二维码会话`);
  } catch (error) {
    console.error('清理过期会话失败:', error);
  }
};
