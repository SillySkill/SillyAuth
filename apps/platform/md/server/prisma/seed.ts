import { PrismaClient, UserRole, UserStatus } from '@prisma/client';
import * as bcrypt from 'bcrypt';

const prisma = new PrismaClient();

async function main() {
  console.log('开始种子数据...');

  // 创建默认管理员用户
  const hashedPassword = await bcrypt.hash('admin123456', 10);

  const admin = await prisma.user.upsert({
    where: { email: 'admin@sillymd.com' },
    update: {},
    create: {
      email: 'admin@sillymd.com',
      username: 'admin',
      password: hashedPassword,
      role: UserRole.ADMIN,
      status: UserStatus.ACTIVE,
      avatar: null,
    },
  });

  console.log('创建管理员用户:', admin.email);

  // 创建编辑用户
  const editorPassword = await bcrypt.hash('editor123456', 10);
  const editor = await prisma.user.upsert({
    where: { email: 'editor@sillymd.com' },
    update: {},
    create: {
      email: 'editor@sillymd.com',
      username: 'editor',
      password: editorPassword,
      role: UserRole.EDITOR,
      status: UserStatus.ACTIVE,
    },
  });

  console.log('创建编辑用户:', editor.email);

  // 创建示例导航菜单
  const navHome = await prisma.navigation.create({
    data: {
      title: '首页',
      key: 'home',
      url: '/',
      icon: 'HomeOutlined',
      order: 1,
      isActive: true,
      language: 'zh',
    },
  });

  const navAbout = await prisma.navigation.create({
    data: {
      title: '关于',
      key: 'about',
      url: '/about',
      icon: 'UserOutlined',
      order: 2,
      isActive: true,
      language: 'zh',
    },
  });

  const navSkills = await prisma.navigation.create({
    data: {
      title: '技能',
      key: 'skills',
      url: '/skills',
      icon: 'ToolOutlined',
      order: 3,
      isActive: true,
      language: 'zh',
    },
  });

  console.log('创建导航菜单: 首页, 关于, 技能');

  // 创建示例轮播图
  await prisma.carousel.create({
    data: {
      title: '欢迎来到 SillyMD',
      description: '一个现代化的内容管理系统',
      mediaType: 'IMAGE',
      mediaUrl: '/uploads/carousel/slide-1.jpg',
      order: 1,
      isActive: true,
      language: 'zh',
    },
  });

  await prisma.carousel.create({
    data: {
      title: '强大的功能',
      description: '支持多语言、SEO优化、内容版本控制',
      mediaType: 'IMAGE',
      mediaUrl: '/uploads/carousel/slide-2.jpg',
      order: 2,
      isActive: true,
      language: 'zh',
    },
  });

  console.log('创建示例轮播图');

  // 创建示例技能
  const skills = [
    { name: 'React', category: '前端', level: 90, order: 1 },
    { name: 'Vue', category: '前端', level: 85, order: 2 },
    { name: 'Node.js', category: '后端', level: 88, order: 3 },
    { name: 'Python', category: '后端', level: 82, order: 4 },
    { name: 'TypeScript', category: '前端', level: 87, order: 5 },
    { name: 'MySQL', category: '数据库', level: 80, order: 6 },
    { name: 'MongoDB', category: '数据库', level: 75, order: 7 },
    { name: 'Docker', category: '运维', level: 78, order: 8 },
  ];

  for (const skill of skills) {
    await prisma.skill.create({
      data: {
        ...skill,
        isActive: true,
        language: 'zh',
      },
    });
  }

  console.log('创建示例技能数据');

  // 创建示例供应商
  const vendors = [
    { name: 'GitHub', logo: '/uploads/vendors/github.png', website: 'https://github.com', order: 1 },
    { name: 'Google', logo: '/uploads/vendors/google.png', website: 'https://google.com', order: 2 },
    { name: 'Microsoft', logo: '/uploads/vendors/microsoft.png', website: 'https://microsoft.com', order: 3 },
    { name: 'Amazon', logo: '/uploads/vendors/amazon.png', website: 'https://amazon.com', order: 4 },
  ];

  for (const vendor of vendors) {
    await prisma.vendor.create({
      data: {
        ...vendor,
        isActive: true,
        language: 'zh',
      },
    });
  }

  console.log('创建示例供应商数据');

  // 创建示例SEO配置
  await prisma.sEOSettings.create({
    data: {
      page: 'home',
      title: 'SillyMD - 现代化内容管理系统',
      description: 'SillyMD是一个功能强大、易于使用的内容管理系统，支持多语言、SEO优化等功能。',
      keywords: 'CMS, 内容管理, SillyMD, 博客, 网站',
      ogType: 'website',
      language: 'zh',
    },
  });

  console.log('创建示例SEO配置');

  // 创建示例翻译
  const translations = [
    { key: 'common.welcome', language: 'zh', value: '欢迎' },
    { key: 'common.welcome', language: 'en', value: 'Welcome' },
    { key: 'common.login', language: 'zh', value: '登录' },
    { key: 'common.login', language: 'en', value: 'Login' },
    { key: 'common.logout', language: 'zh', value: '退出' },
    { key: 'common.logout', language: 'en', value: 'Logout' },
    { key: 'nav.home', language: 'zh', value: '首页' },
    { key: 'nav.home', language: 'en', value: 'Home' },
    { key: 'nav.about', language: 'zh', value: '关于' },
    { key: 'nav.about', language: 'en', value: 'About' },
  ];

  for (const translation of translations) {
    await prisma.translation.upsert({
      where: {
        key_language: {
          key: translation.key,
          language: translation.language,
        },
      },
      update: { value: translation.value },
      create: translation,
    });
  }

  console.log('创建示例翻译数据');

  // 创建系统配置
  const configs = [
    { key: 'site.name', value: 'SillyMD', type: 'STRING', category: 'site', description: '网站名称', isPublic: true },
    { key: 'site.description', value: '现代化内容管理系统', type: 'STRING', category: 'site', description: '网站描述', isPublic: true },
    { key: 'site.logo', value: '/uploads/logo.png', type: 'STRING', category: 'site', description: '网站Logo', isPublic: true },
    { key: 'seo.robots', value: 'index,follow', type: 'STRING', category: 'seo', description: 'Robots设置', isPublic: false },
    { key: 'upload.maxSize', value: '10485760', type: 'NUMBER', category: 'upload', description: '最大上传大小(字节)', isPublic: false },
    { key: 'i18n.defaultLanguage', value: 'zh', type: 'STRING', category: 'i18n', description: '默认语言', isPublic: true },
  ];

  for (const config of configs) {
    await prisma.systemConfig.upsert({
      where: { key: config.key },
      update: {},
      create: config,
    });
  }

  console.log('创建系统配置');

  console.log('种子数据创建完成!');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
