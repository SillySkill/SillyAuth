/**
 * 版本更新控制器
 * 处理应用版本检查和更新相关的业务逻辑
 */

import { Request, Response } from 'express';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// 获取最新版本信息（公开接口）
export const getLatestVersion = async (req: Request, res: Response): Promise<void> => {
  try {
    const { appKey } = req.query;

    if (!appKey || typeof appKey !== 'string') {
      res.status(400).json({
        success: false,
        error: { code: 'MISSING_APP_KEY', message: '缺少 appKey 参数' }
      });
      return;
    }

    const version = await prisma.appVersion.findFirst({
      where: {
        appKey: appKey as string,
        isActive: true
      },
      orderBy: {
        releaseDate: 'desc'
      }
    });

    if (!version) {
      res.status(404).json({
        success: false,
        error: { code: 'VERSION_NOT_FOUND', message: '未找到版本信息' }
      });
      return;
    }

    res.json({
      success: true,
      data: {
        appKey: version.appKey,
        version: version.version,
        buildNumber: version.buildNumber,
        releaseDate: version.releaseDate,
        releaseNotes: version.releaseNotes,
        downloadUrl: version.downloadUrl,
        isMandatory: version.isMandatory,
        minRequiredVersion: version.minRequiredVersion
      }
    });
  } catch (error) {
    console.error('获取版本信息失败:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'GET_VERSION_FAILED',
        message: '获取版本信息失败'
      }
    });
  }
};

// 检查更新（包含是否需要更新）
export const checkUpdate = async (req: Request, res: Response): Promise<void> => {
  try {
    const { appKey, currentVersion } = req.query;

    if (!appKey || typeof appKey !== 'string') {
      res.status(400).json({
        success: false,
        error: { code: 'MISSING_APP_KEY', message: '缺少 appKey 参数' }
      });
      return;
    }

    const latestVersion = await prisma.appVersion.findFirst({
      where: {
        appKey: appKey as string,
        isActive: true
      },
      orderBy: {
        releaseDate: 'desc'
      }
    });

    if (!latestVersion) {
      res.json({
        success: true,
        data: {
          hasUpdate: false,
          message: '未找到版本信息'
        }
      });
      return;
    }

    // 比较版本号
    const hasUpdate = compareVersions(currentVersion as string, latestVersion.version) < 0;

    res.json({
      success: true,
      data: {
        hasUpdate,
        currentVersion: currentVersion || '0.0.0',
        latestVersion: latestVersion.version,
        releaseDate: latestVersion.releaseDate,
        releaseNotes: latestVersion.releaseNotes,
        downloadUrl: latestVersion.downloadUrl,
        isMandatory: latestVersion.isMandatory,
        minRequiredVersion: latestVersion.minRequiredVersion
      }
    });
  } catch (error) {
    console.error('检查更新失败:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'CHECK_UPDATE_FAILED',
        message: '检查更新失败'
      }
    });
  }
};

// 获取所有版本历史
export const getVersionHistory = async (req: Request, res: Response): Promise<void> => {
  try {
    const { appKey } = req.params;
    const { limit = '20' } = req.query;

    const versions = await prisma.appVersion.findMany({
      where: {
        appKey,
        isActive: true
      },
      orderBy: {
        releaseDate: 'desc'
      },
      take: parseInt(limit as string)
    });

    res.json({
      success: true,
      data: versions.map(v => ({
        version: v.version,
        buildNumber: v.buildNumber,
        releaseDate: v.releaseDate,
        releaseNotes: v.releaseNotes,
        isMandatory: v.isMandatory
      }))
    });
  } catch (error) {
    console.error('获取版本历史失败:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'GET_HISTORY_FAILED',
        message: '获取版本历史失败'
      }
    });
  }
};

// 管理员：创建新版本
export const createVersion = async (req: Request, res: Response): Promise<void> => {
  try {
    const {
      appKey,
      version,
      buildNumber,
      releaseNotes,
      downloadUrl,
      checksum,
      fileSize,
      isMandatory,
      minRequiredVersion
    } = req.body;

    // 检查版本是否已存在
    const existing = await prisma.appVersion.findUnique({
      where: {
        appKey_version: {
          appKey,
          version
        }
      }
    });

    if (existing) {
      res.status(400).json({
        success: false,
        error: { code: 'VERSION_EXISTS', message: '该版本已存在' }
      });
      return;
    }

    const newVersion = await prisma.appVersion.create({
      data: {
        appKey,
        version,
        buildNumber,
        releaseNotes,
        downloadUrl,
        checksum,
        fileSize,
        isMandatory: isMandatory || false,
        minRequiredVersion
      }
    });

    res.status(201).json({
      success: true,
      data: newVersion
    });
  } catch (error) {
    console.error('创建版本失败:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'CREATE_VERSION_FAILED',
        message: '创建版本失败'
      }
    });
  }
};

// 管理员：更新版本信息
export const updateVersion = async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    const updateData = req.body;

    const version = await prisma.appVersion.update({
      where: { id },
      data: updateData
    });

    res.json({
      success: true,
      data: version
    });
  } catch (error) {
    console.error('更新版本失败:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'UPDATE_VERSION_FAILED',
        message: '更新版本失败'
      }
    });
  }
};

// 管理员：删除版本
export const deleteVersion = async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;

    // 软删除
    await prisma.appVersion.update({
      where: { id },
      data: { isActive: false }
    });

    res.json({
      success: true,
      message: '版本已删除'
    });
  } catch (error) {
    console.error('删除版本失败:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'DELETE_VERSION_FAILED',
        message: '删除版本失败'
      }
    });
  }
};

// 管理员：获取所有应用版本列表
export const getAllAppVersions = async (req: Request, res: Response): Promise<void> => {
  try {
    const { appKey } = req.query;

    const where = appKey ? { appKey: appKey as string } : {};

    const versions = await prisma.appVersion.findMany({
      where,
      orderBy: [
        { appKey: 'asc' },
        { releaseDate: 'desc' }
      ]
    });

    // 按应用分组
    const groupedVersions: Record<string, any[]> = {};
    versions.forEach(v => {
      if (!groupedVersions[v.appKey]) {
        groupedVersions[v.appKey] = [];
      }
      groupedVersions[v.appKey].push(v);
    });

    res.json({
      success: true,
      data: groupedVersions
    });
  } catch (error) {
    console.error('获取版本列表失败:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'GET_VERSIONS_FAILED',
        message: '获取版本列表失败'
      }
    });
  }
};

// 工具函数：比较版本号
// 返回值：0 相等，-1 当前版本更新，1 有可用更新
function compareVersions(current: string, latest: string): number {
  if (!current) return 1;

  const currentParts = current.split('.').map(Number);
  const latestParts = latest.split('.').map(Number);

  for (let i = 0; i < Math.max(currentParts.length, latestParts.length); i++) {
    const a = currentParts[i] || 0;
    const b = latestParts[i] || 0;

    if (a < b) return 1;  // 有可用更新
    if (a > b) return -1; // 当前版本更新
  }

  return 0; // 版本相同
}
