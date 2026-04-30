#!/bin/bash

echo "================================"
echo "SillyMD CMS 快速安装脚本"
echo "================================"

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未安装 Node.js，请先安装 Node.js >= 18.0.0"
    exit 1
fi

echo "✓ Node.js 版本: $(node -v)"

# 检查 MySQL
if ! command -v mysql &> /dev/null; then
    echo "⚠️  警告: 未检测到 MySQL 命令，请确保 MySQL 已安装并运行"
fi

# 进入后端目录
cd server

echo ""
echo "================================"
echo "1. 安装后端依赖"
echo "================================"
npm install

if [ $? -ne 0 ]; then
    echo "❌ 后端依赖安装失败"
    exit 1
fi

echo "✓ 后端依赖安装完成"

# 检查 .env 文件
if [ ! -f .env ]; then
    echo ""
    echo "================================"
    echo "2. 配置环境变量"
    echo "================================"
    cp .env.example .env
    echo "✓ 已创建 .env 文件"
    echo "⚠️  请编辑 .env 文件，配置数据库连接信息"
    echo ""
    read -p "按 Enter 继续..."
fi

# 生成 Prisma Client
echo ""
echo "================================"
echo "3. 生成 Prisma Client"
echo "================================"
npm run prisma:generate

if [ $? -ne 0 ]; then
    echo "❌ Prisma Client 生成失败"
    exit 1
fi

echo "✓ Prisma Client 生成完成"

# 运行数据库迁移
echo ""
echo "================================"
echo "4. 运行数据库迁移"
echo "================================"
read -p "是否运行数据库迁移? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    npm run prisma:migrate

    if [ $? -ne 0 ]; then
        echo "❌ 数据库迁移失败"
        exit 1
    fi

    echo "✓ 数据库迁移完成"
fi

# 填充种子数据
echo ""
echo "================================"
echo "5. 填充种子数据"
echo "================================"
read -p "是否填充种子数据? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    npm run seed

    if [ $? -ne 0 ]; then
        echo "❌ 填充种子数据失败"
        exit 1
    fi

    echo "✓ 种子数据填充完成"
fi

# 返回根目录
cd ..

# 进入前端目录
cd admin

echo ""
echo "================================"
echo "6. 安装前端依赖"
echo "================================"
npm install

if [ $? -ne 0 ]; then
    echo "❌ 前端依赖安装失败"
    exit 1
fi

echo "✓ 前端依赖安装完成"

# 完成
echo ""
echo "================================"
echo "✓ 安装完成！"
echo "================================"
echo ""
echo "启动指南："
echo ""
echo "1. 启动后端服务："
echo "   cd server"
echo "   npm run dev"
echo ""
echo "2. 启动前端服务（新终端）："
echo "   cd admin"
echo "   npm run dev"
echo ""
echo "3. 访问系统："
echo "   前端: http://localhost:3000"
echo "   后端: http://localhost:3001"
echo ""
echo "默认账号："
echo "   邮箱: admin@sillymd.com"
echo "   密码: admin123456"
echo ""
echo "================================"
