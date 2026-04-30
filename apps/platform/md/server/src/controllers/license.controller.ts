/**
 * 许可证控制器
 * 处理付费技能许可证相关的业务逻辑（防盗版）
 */

import { Request, Response } from 'express';
import { PrismaClient } from '@prisma/client';
import { v4 as uuidv4 } from 'uuid';
import crypto from 'crypto';

const prisma = new PrismaClient();

// 生成许可证密钥
function generateLicenseKey(): string {
  const uuid = uuidv4().replace(/-/g, '').toUpperCase();
  // 格式：XXXX-XXXX-XXXX-XXXX-XXXX
  return `${uuid.substring(0, 4)}-${uuid.substring(4, 8)}-${uuid.substring(8, 12)}-${uuid.substring(12, 16)}-${uuid.substring(16, 20)}`;
}

// 生成设备ID
function generateDeviceId(deviceInfo: any): string {
  const data = JSON.stringify({
    userAgent: deviceInfo.userAgent,
    platform: deviceInfo.platform,
    screen: deviceInfo.screen,
    timezone: deviceInfo.timezone
  });
  return crypto.createHash('sha256').update(data).digest('hex').substring(0, 32);
}

// 购买技能后生成许可证
export const createLicense = async (req: Request, res: Response): Promise<void> => {
  try {
    const { userId, skillId, durationDays } = req.body;

    // 检查是否已有该技能的许可证
    const existing = await prisma.skillLicense.findFirst({
      where: {
        userId,
        skillId,
        isActive: true
      }
    });

    if (existing) {
      res.status(400).json({
        success: false,
        error: { code: 'LICENSE_EXISTS', message: '您已拥有该技能的许可证' }
      });
      return;
    }

    // 生成许可证
    const licenseKey = generateLicenseKey();
    const expiresAt = durationDays ? new Date(Date.now() + durationDays * 24 * 60 * 60 * 1000) : null;

    const license = await prisma.skillLicense.create({
      data: {
        licenseKey,
        userId,
        skillId,
        expiresAt,
        maxDevices: 3
      },
      include: {
        skill: {
          select: {
            id: true,
            name: true,
            category: true,
            icon: true
          }
        }
      }
    });

    res.status(201).json({
      success: true,
      data: {
        licenseKey: license.licenseKey,
        skill: license.skill,
        expiresAt: license.expiresAt,
        maxDevices: license.maxDevices,
        activatedAt: license.activatedAt
      }
    });
  } catch (error) {
    console.error('创建许可证失败:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'CREATE_LICENSE_FAILED',
        message: '创建许可证失败'
      }
    });
  }
};

// 激活设备（验证许可证）
export const activateDevice = async (req: Request, res: Response): Promise<void> => {
  try {
    const { licenseKey, deviceInfo } = req.body;
    const userId = (req as any).user?.id;

    if (!userId) {
      res.status(401).json({
        success: false,
        error: { code: 'UNAUTHORIZED', message: '请先登录' }
      });
      return;
    }

    // 查找许可证
    const license = await prisma.skillLicense.findUnique({
      where: { licenseKey },
      include: {
        devices: true,
        skill: {
          select: {
            id: true,
            name: true
          }
        }
      }
    });

    if (!license) {
      res.status(404).json({
        success: false,
        error: { code: 'LICENSE_NOT_FOUND', message: '许可证不存在' }
      });
      return;
    }

    // 验证许可证所有者
    if (license.userId !== userId) {
      res.status(403).json({
        success: false,
        error: { code: 'LICENSE_MISMATCH', message: '许可证与用户不匹配' }
      });
      return;
    }

    // 检查是否过期
    if (license.expiresAt && new Date() > license.expiresAt) {
      res.status(400).json({
        success: false,
        error: { code: 'LICENSE_EXPIRED', message: '许可证已过期' }
      });
      return;
    }

    // 检查是否激活
    if (!license.isActive) {
      res.status(400).json({
        success: false,
        error: { code: 'LICENSE_INACTIVE', message: '许可证已停用' }
      });
      return;
    }

    // 生成设备ID
    const deviceId = generateDeviceId(deviceInfo);

    // 检查设备是否已激活
    const existingDevice = license.devices.find(d => d.deviceId === deviceId);
    if (existingDevice) {
      // 更新最后活跃时间
      await prisma.licensedDevice.update({
        where: { id: existingDevice.id },
        data: { lastActiveAt: new Date() }
      });

      // 更新许可证最后验证时间
      await prisma.skillLicense.update({
        where: { id: license.id },
        data: { lastVerifiedAt: new Date() }
      });

      res.json({
        success: true,
        data: {
          activated: true,
          skill: license.skill,
          deviceName: existingDevice.deviceName,
          expiresAt: license.expiresAt
        }
      });
      return;
    }

    // 检查设备数量是否超限
    if (license.devices.filter(d => d.isActive).length >= license.maxDevices) {
      res.status(400).json({
        success: false,
        error: {
          code: 'MAX_DEVICES_REACHED',
          message: `已达到最大设备数(${license.maxDevices})，请先移除其他设备`
        },
        data: {
          maxDevices: license.maxDevices,
          currentDevices: license.devices.filter(d => d.isActive).length
        }
      });
      return;
    }

    // 添加新设备
    await prisma.licensedDevice.create({
      data: {
        licenseId: license.id,
        deviceId,
        deviceName: deviceInfo.deviceName || '未知设备',
        deviceType: deviceInfo.platform || 'unknown'
      }
    });

    // 更新许可证最后验证时间
    await prisma.skillLicense.update({
      where: { id: license.id },
      data: { lastVerifiedAt: new Date() }
    });

    res.json({
      success: true,
      data: {
        activated: true,
        skill: license.skill,
        deviceName: deviceInfo.deviceName || '未知设备',
        expiresAt: license.expiresAt,
        maxDevices: license.maxDevices,
        currentDevices: license.devices.length + 1
      }
    });
  } catch (error) {
    console.error('激活设备失败:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'ACTIVATE_DEVICE_FAILED',
        message: '激活设备失败'
      }
    });
  }
};

// 验证设备许可证
export const verifyLicense = async (req: Request, res: Response): Promise<void> => {
  try {
    const { licenseKey, deviceId } = req.body;
    const userId = (req as any).user?.id;

    const license = await prisma.skillLicense.findUnique({
      where: { licenseKey },
      include: {
        devices: true,
        skill: true
      }
    });

    if (!license || license.userId !== userId) {
      res.status(404).json({
        success: false,
        error: { code: 'LICENSE_NOT_FOUND', message: '许可证不存在' }
      });
      return;
    }

    // 检查是否过期
    if (license.expiresAt && new Date() > license.expiresAt) {
      res.status(400).json({
        success: false,
        error: { code: 'LICENSE_EXPIRED', message: '许可证已过期' }
      });
      return;
    }

    // 检查设备是否已激活
    const device = license.devices.find(d => d.deviceId === deviceId);
    if (!device || !device.isActive) {
      res.status(403).json({
        success: false,
        error: { code: 'DEVICE_NOT_ACTIVATED', message: '设备未激活' }
      });
      return;
    }

    // 更新最后验证时间
    await prisma.skillLicense.update({
      where: { id: license.id },
      data: { lastVerifiedAt: new Date() }
    });

    await prisma.licensedDevice.update({
      where: { id: device.id },
      data: { lastActiveAt: new Date() }
    });

    res.json({
      success: true,
      data: {
        valid: true,
        skill: {
          id: license.skill.id,
          name: license.skill.name
        },
        expiresAt: license.expiresAt,
        lastVerifiedAt: new Date()
      }
    });
  } catch (error) {
    console.error('验证许可证失败:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'VERIFY_LICENSE_FAILED',
        message: '验证许可证失败'
      }
    });
  }
};

// 获取用户的许可证列表
export const getUserLicenses = async (req: Request, res: Response): Promise<void> => {
  try {
    const userId = (req as any).user?.id;

    const licenses = await prisma.skillLicense.findMany({
      where: {
        userId,
        isActive: true
      },
      include: {
        skill: true,
        devices: {
          where: { isActive: true }
        }
      }
    });

    res.json({
      success: true,
      data: licenses.map(license => ({
        id: license.id,
        licenseKey: license.licenseKey,
        skill: {
          id: license.skill.id,
          name: license.skill.name,
          category: license.skill.category,
          icon: license.skill.icon
        },
        activatedAt: license.activatedAt,
        expiresAt: license.expiresAt,
        maxDevices: license.maxDevices,
        devices: license.devices.map(d => ({
          id: d.id,
          deviceId: d.deviceId,
          deviceName: d.deviceName,
          deviceType: d.deviceType,
          lastActiveAt: d.lastActiveAt
        }))
      }))
    });
  } catch (error) {
    console.error('获取许可证列表失败:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'GET_LICENSES_FAILED',
        message: '获取许可证列表失败'
      }
    });
  }
};

// 移除设备
export const removeDevice = async (req: Request, res: Response): Promise<void> => {
  try {
    const { licenseId, deviceId } = req.params;
    const userId = (req as any).user?.id;

    const license = await prisma.skillLicense.findUnique({
      where: { id: licenseId }
    });

    if (!license || license.userId !== userId) {
      res.status(404).json({
        success: false,
        error: { code: 'LICENSE_NOT_FOUND', message: '许可证不存在' }
      });
      return;
    }

    await prisma.licensedDevice.update({
      where: {
        licenseId_deviceId: {
          licenseId,
          deviceId
        }
      },
      data: { isActive: false }
    });

    res.json({
      success: true,
      message: '设备已移除'
    });
  } catch (error) {
    console.error('移除设备失败:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'REMOVE_DEVICE_FAILED',
        message: '移除设备失败'
      }
    });
  }
};

// 停用许可证
export const deactivateLicense = async (req: Request, res: Response): Promise<void> => {
  try {
    const { licenseKey } = req.params;
    const userId = (req as any).user?.id;

    const license = await prisma.skillLicense.findUnique({
      where: { licenseKey }
    });

    if (!license || license.userId !== userId) {
      res.status(404).json({
        success: false,
        error: { code: 'LICENSE_NOT_FOUND', message: '许可证不存在' }
      });
      return;
    }

    await prisma.skillLicense.update({
      where: { id: license.id },
      data: { isActive: false }
    });

    res.json({
      success: true,
      message: '许可证已停用'
    });
  } catch (error) {
    console.error('停用许可证失败:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'DEACTIVATE_LICENSE_FAILED',
        message: '停用许可证失败'
      }
    });
  }
};
