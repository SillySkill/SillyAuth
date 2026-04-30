import { Router } from 'express';
import authRoutes from './auth.routes';
import contentRoutes from './content.routes';
import navigationRoutes from './navigation.routes';
import carouselRoutes from './carousel.routes';
import skillRoutes from './skill.routes';
import vendorRoutes from './vendor.routes';
import seoRoutes from './seo.routes';
import translationRoutes from './translation.routes';
import userRoutes from './user.routes';
import dashboardRoutes from './dashboard.routes';
import uploadRoutes from './upload.routes';
import publicRoutes from './public.routes';
import shrimpGroupRoutes from './shrimp-group.routes';
import qrcodeRoutes from './qrcode.routes';
import versionRoutes from './version.routes';
import licenseRoutes from './license.routes';
import clawhubRoutes from './clawhub.routes';

const router = Router();

// 公共路由（无需认证）
router.use('/public', publicRoutes);

// 认证路由
router.use('/auth', authRoutes);

// 仪表盘路由
router.use('/dashboard', dashboardRoutes);

// 内容管理路由
router.use('/content', contentRoutes);

// 导航管理路由
router.use('/navigation', navigationRoutes);

// 轮播图管理路由
router.use('/carousel', carouselRoutes);

// 技能管理路由
router.use('/skills', skillRoutes);

// 供应商管理路由
router.use('/vendors', vendorRoutes);

// SEO管理路由
router.use('/seo', seoRoutes);

// 翻译管理路由
router.use('/translations', translationRoutes);

// 用户管理路由
router.use('/users', userRoutes);

// 文件上传路由
router.use('/upload', uploadRoutes);

// 傻福虾群组路由
router.use('/shrimp-groups', shrimpGroupRoutes);

// 二维码登录路由
router.use('/qrcode', qrcodeRoutes);

// 版本更新路由
router.use('/versions', versionRoutes);

// 许可证路由
router.use('/licenses', licenseRoutes);

// Clawhub 路由
router.use('/clawhub', clawhubRoutes);

// 健康检查
router.get('/health', (req, res) => {
  res.json({
    success: true,
    message: 'Server is running',
    timestamp: new Date().toISOString(),
  });
});

export default router;
