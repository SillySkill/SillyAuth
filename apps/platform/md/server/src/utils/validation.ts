import Joi from 'joi';
import { UserRole } from '@prisma/client';

// 用户相关验证
export const userSchemas = {
  register: Joi.object({
    email: Joi.string().email().required().messages({
      'string.email': '请输入有效的邮箱地址',
      'any.required': '邮箱不能为空',
    }),
    username: Joi.string().alphanum().min(3).max(30).required().messages({
      'string.alphanum': '用户名只能包含字母和数字',
      'string.min': '用户名至少3个字符',
      'string.max': '用户名最多30个字符',
      'any.required': '用户名不能为空',
    }),
    password: Joi.string().min(6).required().messages({
      'string.min': '密码至少6个字符',
      'any.required': '密码不能为空',
    }),
    role: Joi.string()
      .valid(...Object.values(UserRole))
      .optional(),
  }),

  login: Joi.object({
    email: Joi.string().email().required().messages({
      'string.email': '请输入有效的邮箱地址',
      'any.required': '邮箱不能为空',
    }),
    password: Joi.string().required().messages({
      'any.required': '密码不能为空',
    }),
  }),

  update: Joi.object({
    email: Joi.string().email().optional(),
    username: Joi.string().alphanum().min(3).max(30).optional(),
    password: Joi.string().min(6).optional(),
    role: Joi.string()
      .valid(...Object.values(UserRole))
      .optional(),
    avatar: Joi.string().optional(),
    status: Joi.string().valid('ACTIVE', 'INACTIVE', 'BANNED').optional(),
  }),
};

// 内容相关验证
export const contentSchemas = {
  create: Joi.object({
    key: Joi.string().required().messages({
      'any.required': '内容键不能为空',
    }),
    type: Joi.string()
      .valid('PAGE', 'SECTION', 'COMPONENT', 'TEXT', 'HTML', 'MARKDOWN')
      .required()
      .messages({
        'any.required': '内容类型不能为空',
        'any.only': '无效的内容类型',
      }),
    title: Joi.string().required().messages({
      'any.required': '标题不能为空',
    }),
    content: Joi.string().allow('').optional(),
    metadata: Joi.object().optional(),
    language: Joi.string().length(2).default('zh'),
    status: Joi.string().valid('DRAFT', 'PUBLISHED', 'ARCHIVED').default('DRAFT'),
    seo: Joi.object().optional(),
  }),

  update: Joi.object({
    type: Joi.string()
      .valid('PAGE', 'SECTION', 'COMPONENT', 'TEXT', 'HTML', 'MARKDOWN')
      .optional(),
    title: Joi.string().optional(),
    content: Joi.string().allow('').optional(),
    metadata: Joi.object().optional(),
    language: Joi.string().length(2).optional(),
    status: Joi.string().valid('DRAFT', 'PUBLISHED', 'ARCHIVED').optional(),
    seo: Joi.object().optional(),
  }),
};

// 导航相关验证
export const navigationSchemas = {
  create: Joi.object({
    title: Joi.string().required().messages({
      'any.required': '标题不能为空',
    }),
    key: Joi.string().required().messages({
      'any.required': '键不能为空',
    }),
    url: Joi.string().required().messages({
      'any.required': 'URL不能为空',
    }),
    icon: Joi.string().optional(),
    parentId: Joi.string().uuid().allow(null).optional(),
    order: Joi.number().integer().min(0).default(0),
    isActive: Joi.boolean().default(true),
    isNewWindow: Joi.boolean().default(false),
    language: Joi.string().length(2).default('zh'),
  }),

  update: Joi.object({
    title: Joi.string().optional(),
    key: Joi.string().optional(),
    url: Joi.string().optional(),
    icon: Joi.string().optional(),
    parentId: Joi.string().uuid().allow(null).optional(),
    order: Joi.number().integer().min(0).optional(),
    isActive: Joi.boolean().optional(),
    isNewWindow: Joi.boolean().optional(),
    language: Joi.string().length(2).optional(),
  }),
};

// 轮播图相关验证
export const carouselSchemas = {
  create: Joi.object({
    title: Joi.string().required().messages({
      'any.required': '标题不能为空',
    }),
    description: Joi.string().allow('').optional(),
    mediaType: Joi.string()
      .valid('IMAGE', 'VIDEO')
      .required()
      .messages({
        'any.required': '媒体类型不能为空',
        'any.only': '无效的媒体类型',
      }),
    mediaUrl: Joi.string().required().messages({
      'any.required': '媒体URL不能为空',
    }),
    linkUrl: Joi.string().allow('').optional(),
    linkTitle: Joi.string().allow('').optional(),
    order: Joi.number().integer().min(0).default(0),
    isActive: Joi.boolean().default(true),
    language: Joi.string().length(2).default('zh'),
    startDate: Joi.date().iso().optional(),
    endDate: Joi.date().iso().optional(),
  }),

  update: Joi.object({
    title: Joi.string().optional(),
    description: Joi.string().allow('').optional(),
    mediaType: Joi.string().valid('IMAGE', 'VIDEO').optional(),
    mediaUrl: Joi.string().optional(),
    linkUrl: Joi.string().allow('').optional(),
    linkTitle: Joi.string().allow('').optional(),
    order: Joi.number().integer().min(0).optional(),
    isActive: Joi.boolean().optional(),
    language: Joi.string().length(2).optional(),
    startDate: Joi.date().iso().optional(),
    endDate: Joi.date().iso().optional(),
  }),
};

// SEO相关验证
export const seoSchemas = {
  create: Joi.object({
    page: Joi.string().required().messages({
      'any.required': '页面标识不能为空',
    }),
    title: Joi.string().required().messages({
      'any.required': '标题不能为空',
    }),
    description: Joi.string().allow('').optional(),
    keywords: Joi.string().allow('').optional(),
    ogImage: Joi.string().allow('').optional(),
    ogType: Joi.string().allow('').optional(),
    twitterCard: Joi.string().allow('').optional(),
    schema: Joi.object().optional(),
    canonical: Joi.string().allow('').optional(),
    robots: Joi.string().allow('').optional(),
    language: Joi.string().length(2).default('zh'),
  }),

  update: Joi.object({
    title: Joi.string().optional(),
    description: Joi.string().allow('').optional(),
    keywords: Joi.string().allow('').optional(),
    ogImage: Joi.string().allow('').optional(),
    ogType: Joi.string().allow('').optional(),
    twitterCard: Joi.string().allow('').optional(),
    schema: Joi.object().optional(),
    canonical: Joi.string().allow('').optional(),
    robots: Joi.string().allow('').optional(),
    language: Joi.string().length(2).optional(),
  }),
};

// 翻译相关验证
export const translationSchemas = {
  create: Joi.object({
    key: Joi.string().required().messages({
      'any.required': '翻译键不能为空',
    }),
    language: Joi.string().length(2).required().messages({
      'any.required': '语言代码不能为空',
    }),
    value: Joi.string().required().messages({
      'any.required': '翻译值不能为空',
    }),
    namespace: Joi.string().optional(),
    context: Joi.string().optional(),
  }),

  update: Joi.object({
    value: Joi.string().required().messages({
      'any.required': '翻译值不能为空',
    }),
    namespace: Joi.string().optional(),
    context: Joi.string().optional(),
  }),
};

// 技能相关验证
export const skillSchemas = {
  create: Joi.object({
    name: Joi.string().required().messages({
      'any.required': '技能名称不能为空',
    }),
    category: Joi.string().required().messages({
      'any.required': '技能分类不能为空',
    }),
    level: Joi.number().integer().min(0).max(100).default(0),
    icon: Joi.string().allow('').optional(),
    description: Joi.string().allow('').optional(),
    order: Joi.number().integer().min(0).default(0),
    isActive: Joi.boolean().default(true),
    language: Joi.string().length(2).default('zh'),
  }),

  update: Joi.object({
    name: Joi.string().optional(),
    category: Joi.string().optional(),
    level: Joi.number().integer().min(0).max(100).optional(),
    icon: Joi.string().allow('').optional(),
    description: Joi.string().allow('').optional(),
    order: Joi.number().integer().min(0).optional(),
    isActive: Joi.boolean().optional(),
    language: Joi.string().length(2).optional(),
  }),
};

// 供应商相关验证
export const vendorSchemas = {
  create: Joi.object({
    name: Joi.string().required().messages({
      'any.required': '供应商名称不能为空',
    }),
    logo: Joi.string().allow('').optional(),
    website: Joi.string().uri().optional().messages({
      'string.uri': '请输入有效的URL',
    }),
    description: Joi.string().allow('').optional(),
    order: Joi.number().integer().min(0).default(0),
    isActive: Joi.boolean().default(true),
    language: Joi.string().length(2).default('zh'),
  }),

  update: Joi.object({
    name: Joi.string().optional(),
    logo: Joi.string().allow('').optional(),
    website: Joi.string().uri().optional().messages({
      'string.uri': '请输入有效的URL',
    }),
    description: Joi.string().allow('').optional(),
    order: Joi.number().integer().min(0).optional(),
    isActive: Joi.boolean().optional(),
    language: Joi.string().length(2).optional(),
  }),
};
