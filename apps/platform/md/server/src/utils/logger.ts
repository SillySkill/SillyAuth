import winston from 'winston';
import path from 'path';

// 定义日志级别
const levels = {
  error: 0,
  warn: 1,
  info: 2,
  http: 3,
  debug: 4,
};

// 定义日志颜色
const colors = {
  error: 'red',
  warn: 'yellow',
  info: 'green',
  http: 'magenta',
  debug: 'blue',
};

// 告诉 winston 使用这些颜色
winston.addColors(colors);

// 定义日志格式
const format = winston.format.combine(
  // 添加时间戳
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss:ms' }),
  // 错误堆栈跟踪
  winston.format.errors({ stack: true }),
  // 使用自定义颜色
  winston.format.colorize({ all: true }),
  // 自定义格式
  winston.format.printf(
    (info) => `${info.timestamp} ${info.level}: ${info.message}${info.stack ? '\n' + info.stack : ''}`
  )
);

// 定义传输方式（控制台和文件）
const transports = [
  // 控制台输出
  new winston.transports.Console(),
  // 错误日志文件
  new winston.transports.File({
    filename: path.join(process.cwd(), 'logs', 'error.log'),
    level: 'error',
  }),
  // 所有日志文件
  new winston.transports.File({
    filename: path.join(process.cwd(), 'logs', 'combined.log'),
  }),
];

// 创建 logger 实例
export const logger = winston.createLogger({
  level: process.env.NODE_ENV === 'development' ? 'debug' : 'info',
  levels,
  format,
  transports,
});

// 导出 logger
export default logger;
