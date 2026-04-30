import { Request, Response, NextFunction } from 'express';
import { Schema, ValidationError } from 'joi';
import { validationErrorResponse } from '../utils/response';
import { logger } from './logger';

/**
 * 验证中间件工厂函数
 */
export function validate(schema: Schema, property: 'body' | 'query' | 'params' = 'body') {
  return (req: Request, res: Response, next: NextFunction) => {
    try {
      const data = req[property];
      const { error, value } = schema.validate(data, {
        abortEarly: false,
        stripUnknown: true,
      });

      if (error) {
        // 格式化错误信息
        const errors: Record<string, string[]> = {};
        error.details.forEach((detail) => {
          const key = detail.path.join('.');
          if (!errors[key]) {
            errors[key] = [];
          }
          errors[key].push(detail.message);
        });

        logger.debug('验证错误:', errors);
        return res.status(400).json(validationErrorResponse(errors));
      }

      // 将验证后的数据替换原数据
      req[property] = value;
      next();
    } catch (error) {
      logger.error('验证中间件错误:', error);
      return res.status(500).json({
        success: false,
        message: '服务器错误',
      });
    }
  };
}
