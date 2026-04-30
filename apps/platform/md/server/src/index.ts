import express, { Application } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import rateLimit from 'express-rate-limit';
import path from 'path';
import { config } from './config';
import { connectDatabase, disconnectDatabase } from './config/database';
import { logger } from './utils/logger';
import { errorHandler, notFoundHandler } from './middleware/error';
import routes from './routes';

// 创建Express应用
const app: Application = express();

// 安全中间件
app.use(helmet());

// CORS配置
app.use(cors(config.cors));

// 压缩响应
app.use(compression());

// 速率限制
const limiter = rateLimit({
  windowMs: config.rateLimit.windowMs,
  max: config.rateLimit.maxRequests,
  message: {
    success: false,
    message: '请求过于频繁，请稍后再试',
    error: 'TOO_MANY_REQUESTS',
  },
});
app.use('/api/', limiter);

// 解析请求体
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// 静态文件服务
app.use('/uploads', express.static(config.upload.dir));

// 白板应用 /board
app.use('/board', express.static(path.join(__dirname, '../../board')));

// SPA fallback for /board - serve index.html for nested routes
app.get('/board/*', (req, res) => {
  res.sendFile(path.join(__dirname, '../../board/index.html'));
});

// 请求日志
app.use((req, res, next) => {
  logger.debug(`${req.method} ${req.url}`);
  next();
});

// API路由
app.use(config.apiPrefix, routes);

// 根路径
app.get('/', (req, res) => {
  res.json({
    success: true,
    message: 'SillyMD CMS API Server',
    version: '1.0.0',
    docs: `${config.apiPrefix}/health`,
  });
});

// 404处理
app.use(notFoundHandler);

// 错误处理
app.use(errorHandler);

// 启动服务器
async function startServer() {
  try {
    // 连接数据库
    await connectDatabase();

    // 启动HTTP服务器
    const server = app.listen(config.port, () => {
      logger.info(`服务器启动成功: http://localhost:${config.port}`);
      logger.info(`API地址: http://localhost:${config.port}${config.apiPrefix}`);
      logger.info(`环境: ${config.nodeEnv}`);
    });

    // 优雅关闭
    const gracefulShutdown = async (signal: string) => {
      logger.info(`${signal} 信号收到，准备关闭服务器...`);

      server.close(async () => {
        logger.info('HTTP服务器已关闭');

        try {
          await disconnectDatabase();
          logger.info('数据库连接已关闭');
          process.exit(0);
        } catch (error) {
          logger.error('关闭数据库连接时出错:', error);
          process.exit(1);
        }
      });

      // 强制退出
      setTimeout(() => {
        logger.error('强制退出');
        process.exit(1);
      }, 10000);
    };

    process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
    process.on('SIGINT', () => gracefulShutdown('SIGINT'));

  } catch (error) {
    logger.error('启动服务器失败:', error);
    process.exit(1);
  }
}

// 启动应用
startServer();

export default app;
