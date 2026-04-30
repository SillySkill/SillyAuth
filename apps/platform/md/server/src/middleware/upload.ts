import { Request, Response, NextFunction } from 'express';
import multer from 'multer';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';
import { config } from '../config';
import { logger } from '../utils/logger';
import fs from 'fs';

// 确保上传目录存在
const uploadDir = path.join(process.cwd(), config.upload.dir);
const subDirs = ['images', 'videos', 'documents', 'carousels', 'vendors', 'avatars'];

// 创建所有必要的目录
[uploadDir, ...subDirs.map(dir => path.join(uploadDir, dir))].forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
    logger.info(`创建上传目录: ${dir}`);
  }
});

// 存储配置
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    let subDir = 'documents';

    // 根据文件类型确定子目录
    if (file.mimetype.startsWith('image/')) {
      subDir = 'images';
    } else if (file.mimetype.startsWith('video/')) {
      subDir = 'videos';
    }

    const fullPath = path.join(uploadDir, subDir);
    cb(null, fullPath);
  },

  filename: (req, file, cb) => {
    // 生成唯一文件名
    const ext = path.extname(file.originalname);
    const basename = path.basename(file.originalname, ext);
    const filename = `${basename}-${uuidv4()}${ext}`;
    cb(null, filename);
  },
});

// 文件过滤器
const fileFilter = (req: Request, file: Express.Multer.File, cb: multer.FileFilterCallback) => {
  if (config.upload.allowedMimeTypes.includes(file.mimetype)) {
    cb(null, true);
  } else {
    cb(new Error('不支持的文件类型'));
  }
};

// 创建 multer 实例
export const upload = multer({
  storage,
  fileFilter,
  limits: {
    fileSize: config.upload.maxFileSize,
  },
});

/**
 * 单文件上传中间件
 */
export function uploadSingle(fieldName: string = 'file') {
  return (req: Request, res: Response, next: NextFunction) => {
    const uploadHandler = upload.single(fieldName);

    uploadHandler(req, res, (err) => {
      if (err instanceof multer.MulterError) {
        // Multer 错误
        if (err.code === 'LIMIT_FILE_SIZE') {
          return res.status(400).json({
            success: false,
            message: '文件大小超过限制',
            error: 'FILE_TOO_LARGE',
          });
        }
        return res.status(400).json({
          success: false,
          message: '文件上传失败',
          error: err.message,
        });
      } else if (err) {
        // 其他错误
        logger.error('文件上传错误:', err);
        return res.status(400).json({
          success: false,
          message: err.message,
          error: 'UPLOAD_ERROR',
        });
      }

      next();
    });
  };
}

/**
 * 多文件上传中间件
 */
export function uploadMultiple(fieldName: string = 'files', maxCount: number = 10) {
  return (req: Request, res: Response, next: NextFunction) => {
    const uploadHandler = upload.array(fieldName, maxCount);

    uploadHandler(req, res, (err) => {
      if (err instanceof multer.MulterError) {
        if (err.code === 'LIMIT_FILE_SIZE') {
          return res.status(400).json({
            success: false,
            message: '文件大小超过限制',
            error: 'FILE_TOO_LARGE',
          });
        }
        if (err.code === 'LIMIT_UNEXPECTED_FILE') {
          return res.status(400).json({
            success: false,
            message: `最多只能上传 ${maxCount} 个文件`,
            error: 'TOO_MANY_FILES',
          });
        }
        return res.status(400).json({
          success: false,
          message: '文件上传失败',
          error: err.message,
        });
      } else if (err) {
        logger.error('文件上传错误:', err);
        return res.status(400).json({
          success: false,
          message: err.message,
          error: 'UPLOAD_ERROR',
        });
      }

      next();
    });
  };
}
