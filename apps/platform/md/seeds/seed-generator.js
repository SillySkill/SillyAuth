/**
 * SillyMD 种子数据生成器 - 真实版
 * 
 * 生成逼真的模拟用户和 Skills 数据
 * 用法: node seed-generator.js --users 50 --skills 200
 */

const fs = require('fs');
const path = require('path');

// ============ 配置 ============
const CONFIG = {
  // 行业分类
  industries: [
    { name: '金融', icon: '🟣', color: '#FFD700' },
    { name: '电商', icon: '🟢', color: '#4CAF50' },
    { name: '教育', icon: '🟡', color: '#FFC107' },
    { name: '医疗', icon: '🟣', color: '#9C27B0' },
    { name: '制造', icon: '🟠', color: '#FF9800' },
    { name: '旅游', icon: '🔵', color: '#2196F3' },
    { name: '娱乐', icon: '🟣', color: '#E91E63' },
    { name: '餐饮', icon: '🟧', color: '#795548' }
  ],
  
  // 应用场景
  scenarios: [
    { name: '数据分析', icon: '📊' },
    { name: '自动化', icon: '🤖' },
    { name: '客户服务', icon: '🎧' },
    { name: '市场营销', icon: '📱' },
    { name: '产品开发', icon: '💻' },
    { name: '项目管理', icon: '📋' },
    { name: '内容创作', icon: '✍️' }
  ],
  
  // Skills 类型
  skillTypes: ['code', 'design', 'product', 'marketing', 'content', 'operation'],
  
  // 定价类型
  pricingTypes: ['free', 'onetime', 'subscription'],
  
  // 供应商等级分布权重
  vendorDistribution: {
    user: 0.2,
    normal: 0.35,
    premium: 0.3,
    gold: 0.15
  }
};

// ============ 真实姓名库 ============
const REAL_NAMES = {
  // 常见姓氏
  surnames: [
    '王', '李', '张', '刘', '陈', '杨', '黄', '赵', '吴', '周',
    '徐', '孙', '马', '朱', '胡', '郭', '何', '高', '林', '罗',
    '郑', '梁', '谢', '宋', '唐', '许', '韩', '冯', '邓', '曹',
    '彭', '曾', '肖', '田', '董', '袁', '潘', '于', '蒋', '蔡',
    '余', '杜', '叶', '程', '苏', '魏', '吕', '丁', '任', '沈'
  ],
  
  // 男性名字
  maleNames: [
    '伟', '强', '磊', '军', '洋', '勇', '杰', '涛', '超', '明',
    '辉', '刚', '建', '峰', '宇', '浩', '博', '文', '翔', '俊',
    '志', '鹏', '飞', '凯', '龙', '华', '东', '国', '鑫', '毅',
    '林', '宁', '波', '川', '昊', '天', '诚', '康', '亮', '辉',
    '锋', '睿', '哲', '旭', '辰', '昊', '轩', '皓', '泽', '晨'
  ],
  
  // 女性名字
  femaleNames: [
    '芳', '娜', '秀英', '敏', '静', '丽', '娟', '霞', '秀兰', '燕',
    '玲', '桂英', '华', '梅', '莉', '婷', '雪', '颖', '倩', '慧',
    '悦', '怡', '琳', '欣', '蕾', '茜', '雯', '菲', '萍', '红',
    '莹', '洁', '珊', '珍', '月', '媛', '妮', '婕', '薇', '琪',
    '璐', '彤', '宁', '璐', '曼', '依', '萱', '璇', '韵', '彤'
  ],
  
  // 中文技术花名 - 古风文艺风
  coderNicknamesCN: [
    '云深', '墨白', '清风', '明月', '星河', '流年', '浮生', '若水',
    '青衫', '墨染', '长亭', '故渊', '南山', '北海', '东临', '西窗',
    '听雨', '观澜', '知秋', '踏雪', '寻梅', '折柳', '扶桑', '蓬莱',
    '逍遥', '自在', '无为', '空明', '虚竹', '灵均', '子衿', '子佩',
    '陌上', '花开', '浅笑', '安然', '静好', '如初', '如故', '倾城'
  ],
  
  // 中文技术花名 - 动物萌系风
  coderNicknamesAnimal: [
    '程序猿', '代码猫', 'Bug兔', '运维狗', '测试喵', '产品熊',
    '熊猫君', '狐狸酱', '狼少年', '鹿先生', '鲸落', '蝶舞',
    '蜂鸟', '燕子', '喜鹊', '乌鸦', '猫头鹰', '萤火虫',
    '小熊猫', '树懒', '考拉', '企鹅', '海豹', '海豚',
    '龙猫', '皮卡丘', '可达鸭', '杰尼龟', '小火龙', '妙蛙种子'
  ],
  
  // 中文技术花名 - 食物系
  coderNicknamesFood: [
    '奶茶', '咖啡', '可乐', '雪碧', '橙汁', '西瓜', '草莓', '芒果',
    '布丁', '果冻', '泡芙', '蛋糕', '面包', '饼干', '巧克力', '糖果',
    '火锅', '烧烤', '麻辣烫', '螺蛳粉', '臭豆腐', '煎饼', '油条', '豆浆',
    '红烧肉', '糖醋排骨', '清蒸鱼', '白切鸡', '小笼包', '饺子', '汤圆', '粽子'
  ],
  
  // 中文技术花名 - 技术梗
  coderNicknamesTech: [
    '404', '500', 'Null', 'Undefined', 'NaN', 'Infinity',
    'HelloWorld', 'ConsoleLog', 'GitPush', 'CodeReview', 'MergeConflict',
    'StackOverflow', 'SegmentFault', 'OutOfMemory', 'DeadLock', 'RaceCondition',
    '递归大师', '回调地狱', 'Promise', 'AsyncAwait', 'EventLoop',
    '闭包侠', '原型链', '作用域', '执行栈', '垃圾回收',
    '单线程', '多进程', '微服务', '分布式', '高并发'
  ],
  
  // 中文技术花名 - 简约单字
  coderNicknamesSingle: [
    '枫', '岚', '霄', '宸', '瑾', '瑜', '琛', '璟',
    '逸', '轩', '昊', '泽', '睿', '哲', '翰', '霖',
    '溪', '川', '岳', '峰', '辰', '星', '月', '阳',
    '风', '雨', '雪', '霜', '露', '霞', '虹', '霓',
    '竹', '松', '柏', '梅', '兰', '菊', '荷', '莲'
  ],
  
  // 中文技术花名 - 二次元风
  coderNicknamesAnime: [
    '御坂美琴', '桐人', '亚丝娜', '鸣人', '佐助', '路飞', '索隆', '娜美',
    '柯南', '小兰', '小新', '哆啦A梦', '大雄', '静香', '胖虎', '小夫',
    '樱木花道', '流川枫', '赤木晴子', '三井寿', '宫城良田', '安西教练',
    '碇真嗣', '绫波丽', '明日香', '初号机', '零号机', '二号机',
    '悟空', '贝吉塔', '悟饭', '比克', '布尔玛', '琪琪', '天津饭', '饺子'
  ],
  
  // 中文技术花名 - 职业+称呼
  coderNicknamesTitle: [
    '前端小王', '后端老李', '算法老张', '运维老刘', '测试老陈',
    '产品小周', '设计小吴', '运营小郑', '市场小冯', '商务小何',
    'CTO大人', 'CEO陛下', '架构师爷爷', '程序员爸爸', '产品经理妈妈',
    '实习生小弟', '外包小哥', '外包小妹', '临时工', '正式工',
    '大佬', '巨佬', '神佬', '萌新', '菜鸟', '老鸟', '大神', '小白'
  ],
  
  // 英文风格（保留一些）
  coderNicknamesEN: [
    'CodeMaster', 'BugHunter', 'DataWizard', 'CloudBuilder',
    'DevOps', 'AIGuru', 'WebNinja', 'ScriptKid',
    'GitHero', 'DockerBoy', 'K8sGirl', 
    'Pythonista', 'JavaKing', 'GoMaster', 'RustAce'
  ],
  
  // 设计师风格花名 - 中文
  designerNicknamesCN: [
    '画中人', '墨染青衣', '素手丹青', '执笔绘梦', '一纸山河',
    '色彩诗人', '光影魔术师', '视觉诗人', '美学信徒', '设计狂热者',
    '像素猎人', '矢量精灵', '图层守护者', '蒙版大师', '渐变之王',
    '字体控', '排版癌', '配色盲', '对齐强迫症', '留白艺术家'
  ],
  
  // 产品/运营风格花名 - 中文
  productNicknamesCN: [
    '需求收割机', '用户代言人', '数据信徒', '增长黑客', '变现大师',
    '留存专家', '激活达人', '转化之王', '漏斗分析师', '路径优化师',
    'PRD制造机', '原型绘制者', '会议组织员', '文档生产队', '邮件发送器',
    '背锅侠', '甩锅王', '撕逼能手', '扯皮专家', '甩锅接盘侠'
  ]
};

// ============ 真实头像服务 ============
// 使用多个免费的真实人像服务
const AVATAR_SERVICES = {
  // 随机真实人像（男女混合）
  random: (seed, gender) => {
    // 使用 thispersondoesnotexist 或类似服务
    // 这里使用多个可靠的随机头像源
    const services = [
      // 使用 pravatar.cc（真实人像库）
      `https://i.pravatar.cc/150?u=${seed}`,
      // 使用 uifaces.co 风格
      `https://randomuser.me/api/portraits/${gender === 'female' ? 'women' : 'men'}/${seed % 100}.jpg`,
      // 备用
      `https://api.dicebear.com/7.x/notionists/svg?seed=${seed}`,
    ];
    return services[0];
  },
  
  // 男性头像
  male: (seed) => {
    const id = (seed * 17) % 100;
    return `https://randomuser.me/api/portraits/men/${id}.jpg`;
  },
  
  // 女性头像
  female: (seed) => {
    const id = (seed * 13) % 100;
    return `https://randomuser.me/api/portraits/women/${id}.jpg`;
  }
};

// ============ 公司/职位库 ============
const WORK_INFO = {
  companies: [
    '阿里巴巴', '腾讯', '字节跳动', '美团', '京东', '百度', '快手', '拼多多',
    '华为', '小米', '网易', '滴滴', '携程', 'B站', '知乎', '豆瓣',
    'Google', 'Microsoft', 'Amazon', 'Meta', 'Apple', 'Netflix', 'Twitter',
    '阿里云', '腾讯云', '华为云', '百度云', '京东云',
    '蚂蚁金服', '微众银行', '平安科技', '招商银行科技',
    '商汤科技', '旷视科技', '依图科技', '云从科技',
    '理想汽车', '蔚来汽车', '小鹏汽车', '比亚迪',
    '米哈游', '莉莉丝', '鹰角网络', '叠纸游戏',
    '小红书', '得物', '叮咚买菜', '货拉拉',
    '自由职业', '独立开发者', '创业中', '远程工作'
  ],
  
  positions: {
    tech: ['高级前端工程师', '后端架构师', '全栈工程师', '算法工程师', 'DevOps工程师', '移动端开发', '测试开发', '技术专家', '技术总监', 'CTO'],
    design: ['高级UI设计师', 'UX研究员', '视觉设计师', '品牌设计师', '动画设计师', '设计总监', '创意总监'],
    product: ['产品经理', '高级产品经理', '产品总监', '用户研究员', '数据产品经理', '策略产品经理'],
    marketing: ['市场总监', '增长黑客', '品牌经理', '内容运营', '用户运营', '活动运营', '新媒体运营'],
    management: ['技术经理', '项目经理', '研发总监', '事业部总监', 'VP', '联合创始人']
  }
};

// ============ 个人简介模板 ============
const BIO_TEMPLATES = [
  '现任{company}{position}，专注{field}领域{years}年。相信技术改变世界，乐于分享实战经验。',
  '前{company}{position}，现{currentStatus}。{years}年{field}经验，服务过{count}+企业客户。',
  '{company}资深{position}，热爱{field}，擅长{skill}。致力于用技术解决实际问题。',
  '连续创业者，{field}领域专家。曾任{company}{position}，现专注{skill}方向。',
  '{years}年{field}老兵，{company}技术负责人。开源爱好者，多个热门项目维护者。',
  '独立{role}，{years}年{field}实战经验。前{company}{position}，现专注{skill}。',
  '热衷于{field}的{position}，在{company}工作{years}年。喜欢钻研{skill}，乐于分享。',
  '{company}高级{position}，{field}领域深耕{years}年。擅长{skill}，追求极致用户体验。',
  '从{company}到{currentStatus}，{years}年{field}历程。专注{skill}，服务{count}+客户。',
  '技术布道师，{field}领域专家。{company}前{position}，现专注于{skill}研究与实践。'
];

// ============ 工具函数 ============
function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function randomPick(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function randomPicks(arr, count) {
  const shuffled = [...arr].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, count);
}

function randomDate(start, end) {
  const startDate = new Date(start);
  const endDate = new Date(end);
  const date = new Date(startDate.getTime() + Math.random() * (endDate.getTime() - startDate.getTime()));
  return date.toISOString().split('T')[0];
}

function generateId(prefix, index) {
  return `${prefix}_${String(index).padStart(3, '0')}`;
}

// ============ 真实用户生成器 ============
class RealUserGenerator {
  constructor(seed = 1) {
    this.seed = seed;
    this.userIndex = 1;
    this.usedUsernames = new Set();
  }
  
  /**
   * 生成真实中文姓名
   */
  generateRealName(gender) {
    const surname = randomPick(REAL_NAMES.surnames);
    const namePool = gender === 'female' ? REAL_NAMES.femaleNames : REAL_NAMES.maleNames;
    const givenName = randomPick(namePool);
    return surname + givenName;
  }
  
  /**
   * 生成真实感用户名（英文/拼音风格）
   */
  generateUsername(realName, gender) {
    // 姓氏拼音 + 名字首字母 + 数字
    const pinyinMap = {
      '王': 'wang', '李': 'li', '张': 'zhang', '刘': 'liu', '陈': 'chen',
      '杨': 'yang', '黄': 'huang', '赵': 'zhao', '吴': 'wu', '周': 'zhou',
      '徐': 'xu', '孙': 'sun', '马': 'ma', '朱': 'zhu', '胡': 'hu',
      '郭': 'guo', '何': 'he', '高': 'gao', '林': 'lin', '罗': 'luo'
    };
    
    const surname = realName.charAt(0);
    const pinyin = pinyinMap[surname] || surname.toLowerCase();
    
    const patterns = [
      `${pinyin}${randomInt(1980, 2010)}`,
      `${pinyin}_${randomPick(['dev', 'pro', 'ai', 'design', 'pm'])}`,
      `${pinyin}${randomInt(1, 999)}`,
      `${pinyin}.${randomPick(['cn', 'io', 'dev', 'ai'])}`,
      `${pinyin}_${randomInt(88, 99)}`,
      `${pinyin}${randomPick(['dev', 'code', 'ai', 'ux', 'pm'])}`,
    ];
    
    let username = randomPick(patterns);
    let attempts = 0;
    
    // 确保唯一性
    while (this.usedUsernames.has(username) && attempts < 100) {
      username = `${pinyin}${randomInt(1, 9999)}`;
      attempts++;
    }
    
    this.usedUsernames.add(username);
    return username;
  }
  
  /**
   * 生成中文花名/昵称
   * 从多个风格的昵称库中随机选择
   */
  generateNickname(role) {
    // 合并所有中文花名库
    const allNicknames = [
      ...REAL_NAMES.coderNicknamesCN,      // 古风文艺
      ...REAL_NAMES.coderNicknamesAnimal,  // 动物萌系
      ...REAL_NAMES.coderNicknamesFood,    // 食物系
      ...REAL_NAMES.coderNicknamesTech,    // 技术梗
      ...REAL_NAMES.coderNicknamesSingle,  // 简约单字
      ...REAL_NAMES.coderNicknamesAnime,   // 二次元
      ...REAL_NAMES.coderNicknamesTitle,   // 职业称呼
    ];
    
    // 根据角色类型给某些风格更高权重
    let preferredNicknames = [...allNicknames];
    
    if (role.includes('design')) {
      preferredNicknames = [
        ...REAL_NAMES.designerNicknamesCN,
        ...REAL_NAMES.coderNicknamesCN,
        ...REAL_NAMES.coderNicknamesSingle
      ];
    } else if (role.includes('product') || role.includes('marketing')) {
      preferredNicknames = [
        ...REAL_NAMES.productNicknamesCN,
        ...REAL_NAMES.coderNicknamesTitle,
        ...REAL_NAMES.coderNicknamesTech
      ];
    }
    
    // 90% 概率使用中文花名，10% 概率使用英文风格
    if (Math.random() > 0.1) {
      return randomPick(preferredNicknames);
    } else {
      return randomPick(REAL_NAMES.coderNicknamesEN);
    }
  }
  
  /**
   * 生成真实头像 URL
   */
  generateAvatar(gender, seed) {
    const avatarUrl = gender === 'female' 
      ? AVATAR_SERVICES.female(seed)
      : AVATAR_SERVICES.male(seed);
    return avatarUrl;
  }
  
  /**
   * 生成真实感简介
   */
  generateBio(gender, role) {
    const template = randomPick(BIO_TEMPLATES);
    const company = randomPick(WORK_INFO.companies);
    
    // 根据角色选择职位
    let positionPool = WORK_INFO.positions.tech;
    if (role.includes('design')) positionPool = WORK_INFO.positions.design;
    else if (role.includes('product')) positionPool = WORK_INFO.positions.product;
    else if (role.includes('marketing')) positionPool = WORK_INFO.positions.marketing;
    else if (Math.random() > 0.7) positionPool = WORK_INFO.positions.management;
    
    const position = randomPick(positionPool);
    const years = randomInt(3, 15);
    const count = randomInt(10, 500);
    const field = randomPick(CONFIG.industries).name;
    const skill = randomPick(['AI应用开发', '数据分析', '用户体验设计', '系统架构', '自动化测试', '前端工程化', '云原生技术', '区块链应用']);
    const currentStatus = randomPick(['自由职业', '创业中', '独立开发者', '远程工作', '技术顾问']);
    const roleTitle = gender === 'female' ? '技术小姐姐' : '技术老炮';
    
    return template
      .replace('{company}', company)
      .replace('{position}', position)
      .replace('{years}', years)
      .replace('{field}', field)
      .replace('{count}', count)
      .replace('{skill}', skill)
      .replace('{currentStatus}', currentStatus)
      .replace('{role}', roleTitle);
  }
  
  /**
   * 选择供应商等级
   */
  selectVendorLevel() {
    const rand = Math.random();
    let cumulative = 0;
    
    for (const [level, weight] of Object.entries(CONFIG.vendorDistribution)) {
      cumulative += weight;
      if (rand <= cumulative) {
        return level;
      }
    }
    return 'user';
  }
  
  /**
   * 生成单个真实用户
   */
  generateUser() {
    const id = generateId('user', this.userIndex);
    const gender = Math.random() > 0.6 ? 'female' : 'male'; // 技术行业男性偏多
    const realName = this.generateRealName(gender);
    const username = this.generateUsername(realName, gender);
    const nickname = this.generateNickname('tech');
    const vendorLevel = this.selectVendorLevel();
    
    // 生成统计数据
    let stats = { totalSkills: 0, totalSales: 0, rating: 0 };
    
    if (vendorLevel !== 'user') {
      stats.totalSkills = randomInt(1, 30);
      stats.totalSales = vendorLevel === 'gold' ? randomInt(10000, 80000) :
                        vendorLevel === 'premium' ? randomInt(2000, 20000) :
                        randomInt(0, 5000);
      stats.rating = parseFloat((4.2 + Math.random() * 0.8).toFixed(1));
    }
    
    return {
      id,
      username,
      displayName: nickname,  // 使用花名/昵称作为显示名
      nickname,               // 花名/昵称
      realName,               // 真实姓名（备用）
      gender,
      avatar: this.generateAvatar(gender, this.userIndex),
      bio: this.generateBio(gender, 'tech'),
      role: vendorLevel === 'user' ? 'user' : 'vendor',
      vendorLevel,
      joinDate: randomDate('2024-01-01', '2026-01-31'),
      stats,
      location: randomPick(['北京', '上海', '深圳', '杭州', '广州', '成都', '武汉', '西安', ' remote']),
      isMock: true,
      createdAt: new Date().toISOString()
    };
  }
  
  /**
   * 批量生成用户
   */
  generateUsers(count) {
    const users = [];
    for (let i = 0; i < count; i++) {
      users.push(this.generateUser());
      this.userIndex++;
    }
    return users;
  }
}

// ============ Skills 生成器 ============
class SkillGenerator {
  constructor(users) {
    this.users = users.filter(u => u.vendorLevel !== 'user');
    this.skillIndex = 1;
  }
  
  generateSkillName() {
    const prefixes = ['AI', '智能', '自动化', '专业', '企业级', '云端', '实时'];
    const cores = [
      '数据分析平台', '代码审查助手', '交易机器人', '文档生成器', '安全审计工具',
      'UI组件库', '用户增长系统', '内容创作助手', '测试自动化', '部署工具',
      '聊天机器人', '图像识别引擎', '文本处理工具', '流程自动化', '报表生成器',
      'API集成平台', '数据库管理', '性能优化器', 'SEO工具', '社交媒体助手'
    ];
    const suffixes = ['Pro', 'Plus', 'Max', '企业版', '专业版', ''];
    
    const prefix = Math.random() > 0.6 ? randomPick(prefixes) : '';
    const core = randomPick(cores);
    const suffix = Math.random() > 0.7 ? randomPick(suffixes) : '';
    
    return `${prefix}${core}${suffix}`.trim();
  }
  
  generateDescription(skillName, industry, scenario) {
    const templates = [
      '{skill}是一款专为{industry}行业打造的{scenario}解决方案。支持{feature}，已帮助{count}+企业提升效率。',
      '由资深工程师开发的{skill}，专注于{industry}领域的{scenario}场景。集成{feature}，开箱即用。',
      '适用于{industry}行业的{skill}，提供{feature}功能。{scenario}场景下表现优异，用户好评率{rated}%。',
      '{skill} —— {industry}企业的{scenario}利器。支持{feature}，持续迭代更新，值得信赖。',
      '开源社区热门的{skill}，专为{industry}行业设计。{scenario}场景全覆盖，{feature}一键搞定。'
    ];
    
    const template = randomPick(templates);
    const skill = skillName.replace(/(Pro|Plus|Max|企业版|专业版)$/g, '');
    const features = randomPicks([
      '多语言支持', 'API接口', '可视化面板', '自动化工作流', '团队协作',
      '权限管理', '版本控制', '云端存储', '实时同步', '数据加密',
      '自定义配置', '定时任务', '离线模式', '移动端适配', '一键部署'
    ], 3).join('、');
    
    return template
      .replace('{skill}', skill)
      .replace('{industry}', industry)
      .replace('{scenario}', scenario)
      .replace('{feature}', features)
      .replace('{count}', randomInt(50, 1000))
      .replace('{rated}', randomInt(85, 99));
  }
  
  generatePricing(vendorLevel) {
    const type = randomPick(CONFIG.pricingTypes);
    
    if (type === 'free') {
      return { type, price: 0 };
    }
    
    let basePrice;
    switch (vendorLevel) {
      case 'gold':
        basePrice = randomInt(5000, 20000);
        break;
      case 'premium':
        basePrice = randomInt(1500, 8000);
        break;
      default:
        basePrice = randomInt(200, 3000);
    }
    
    if (type === 'subscription') {
      basePrice = Math.floor(basePrice / 10);
    }
    
    return { type, price: basePrice };
  }
  
  generateIcon(type) {
    const iconMap = {
      code: ['fa-code', 'fa-terminal', 'fa-laptop-code', 'fa-bug', 'fa-file-code', 'fa-git-alt'],
      design: ['fa-paint-brush', 'fa-palette', 'fa-layer-group', 'fa-pen-nib', 'fa-object-group'],
      product: ['fa-lightbulb', 'fa-tasks', 'fa-sitemap', 'fa-chart-line', 'fa-clipboard-list'],
      marketing: ['fa-bullhorn', 'fa-ad', 'fa-chart-pie', 'fa-users', 'fa-share-alt'],
      content: ['fa-pen', 'fa-file-alt', 'fa-video', 'fa-image', 'fa-newspaper'],
      operation: ['fa-cogs', 'fa-server', 'fa-database', 'fa-sync', 'fa-tachometer-alt']
    };
    
    const icons = iconMap[type] || iconMap.code;
    return randomPick(icons);
  }
  
  generateSkill() {
    const author = randomPick(this.users);
    const industry = randomPick(CONFIG.industries);
    const scenario = randomPick(CONFIG.scenarios);
    const type = randomPick(CONFIG.skillTypes);
    const name = this.generateSkillName();
    const pricing = this.generatePricing(author.vendorLevel);
    
    return {
      id: generateId('skill', this.skillIndex++),
      name,
      description: this.generateDescription(name, industry.name, scenario.name),
      authorId: author.id,
      authorName: author.displayName,      // 显示真实姓名
      authorNickname: author.nickname,     // 显示花名
      authorAvatar: author.avatar,
      authorLevel: author.vendorLevel,
      authorLocation: author.location,
      type,
      industry: industry.name,
      industryIcon: industry.icon,
      scenario: scenario.name,
      scenarioIcon: scenario.icon,
      pricing,
      rating: parseFloat((3.8 + Math.random() * 1.2).toFixed(1)),
      downloads: randomInt(0, 10000),
      tags: randomPicks(['AI', '自动化', 'Python', 'JavaScript', '数据分析', '效率工具', '企业级', '开源'], 4),
      icon: this.generateIcon(type),
      status: 'approved',
      isMock: true,
      createdAt: randomDate('2024-03-01', '2026-01-31'),
      updatedAt: new Date().toISOString()
    };
  }
  
  generateSkills(count) {
    const skills = [];
    for (let i = 0; i < count; i++) {
      skills.push(this.generateSkill());
    }
    return skills;
  }
}

// ============ 主程序 ============
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    users: 50,
    skills: 200,
    output: './output',
    seed: Date.now()
  };
  
  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--users':
        options.users = parseInt(args[++i]) || 50;
        break;
      case '--skills':
        options.skills = parseInt(args[++i]) || 200;
        break;
      case '--output':
        options.output = args[++i] || './output';
        break;
      case '--seed':
        options.seed = parseInt(args[++i]) || Date.now();
        break;
    }
  }
  
  return options;
}

function main() {
  const options = parseArgs();
  
  console.log('🥚 SillyMD 真实种子数据生成器');
  console.log('==============================');
  console.log(`生成用户数量: ${options.users}`);
  console.log(`生成 Skills 数量: ${options.skills}`);
  console.log(`输出目录: ${options.output}`);
  console.log('');
  
  if (!fs.existsSync(options.output)) {
    fs.mkdirSync(options.output, { recursive: true });
  }
  
  // 1. 生成真实用户
  console.log('👤 正在生成真实用户...');
  const userGen = new RealUserGenerator(options.seed);
  const users = userGen.generateUsers(options.users);
  
  const userStats = users.reduce((acc, u) => {
    acc[u.vendorLevel] = (acc[u.vendorLevel] || 0) + 1;
    acc.gender = acc.gender || {};
    acc.gender[u.gender] = (acc.gender[u.gender] || 0) + 1;
    return acc;
  }, {});
  
  console.log(`   ✓ 生成 ${users.length} 个用户`);
  console.log(`   - 男性: ${userStats.gender?.male || 0} | 女性: ${userStats.gender?.female || 0}`);
  console.log(`   - 普通用户: ${userStats.user || 0}`);
  console.log(`   - 普通供应商: ${userStats.normal || 0}`);
  console.log(`   - 优质供应商: ${userStats.premium || 0}`);
  console.log(`   - 金牌供应商: ${userStats.gold || 0}`);
  
  // 显示几个示例
  console.log('\n   示例用户:');
  users.slice(0, 3).forEach(u => {
    console.log(`   - ${u.displayName} (@${u.username}) | ${u.nickname} | ${u.vendorLevel}`);
  });
  
  // 2. 生成 Skills
  console.log('\n🛠️  正在生成 Skills...');
  const skillGen = new SkillGenerator(users);
  const skills = skillGen.generateSkills(options.skills);
  
  const skillStats = skills.reduce((acc, s) => {
    acc.type = acc.type || {};
    acc.type[s.type] = (acc.type[s.type] || 0) + 1;
    acc.pricing = acc.pricing || {};
    acc.pricing[s.pricing.type] = (acc.pricing[s.pricing.type] || 0) + 1;
    return acc;
  }, {});
  
  console.log(`   ✓ 生成 ${skills.length} 个 Skills`);
  console.log(`   - 类型分布:`, skillStats.type);
  console.log(`   - 定价分布:`, skillStats.pricing);
  
  // 3. 保存数据
  const usersPath = path.join(options.output, 'mock-users.json');
  const skillsPath = path.join(options.output, 'mock-skills.json');
  
  fs.writeFileSync(usersPath, JSON.stringify(users, null, 2), 'utf-8');
  fs.writeFileSync(skillsPath, JSON.stringify(skills, null, 2), 'utf-8');
  
  console.log(`\n💾 数据已保存:`);
  console.log(`   - ${usersPath}`);
  console.log(`   - ${skillsPath}`);
  
  // 4. 生成前端演示数据
  const demoData = {
    users: users.slice(0, 20),
    skills: skills.slice(0, 50),
    stats: {
      totalUsers: users.length,
      totalSkills: skills.length,
      totalVendors: users.filter(u => u.vendorLevel !== 'user').length,
      freeSkills: skills.filter(s => s.pricing.type === 'free').length,
      paidSkills: skills.filter(s => s.pricing.type !== 'free').length
    }
  };
  
  const demoPath = path.join(options.output, 'demo-data.json');
  fs.writeFileSync(demoPath, JSON.stringify(demoData, null, 2), 'utf-8');
  console.log(`   - ${demoPath} (演示数据)`);
  
  console.log('\n✅ 完成！');
  console.log(`\n下一步:`);
  console.log(`  1. 打开 demo-seed.html 查看效果`);
  console.log(`  2. 头像使用 randomuser.me API（真实人像）`);
  console.log(`  3. 用户名如: wang1990, li_dev, zhang_pro 等`);
}

main();
