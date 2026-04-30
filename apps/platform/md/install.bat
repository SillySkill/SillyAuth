@echo off
chcp 65001 >nul
echo ================================
echo SillyMD CMS 快速安装脚本
echo ================================

:: 检查 Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误: 未安装 Node.js，请先安装 Node.js ^>= 18.0.0
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node -v') do set NODE_VERSION=%%i
echo ✓ Node.js 版本: %NODE_VERSION%

:: 进入后端目录
cd server

echo.
echo ================================
echo 1. 安装后端依赖
echo ================================
call npm install

if %errorlevel% neq 0 (
    echo ❌ 后端依赖安装失败
    pause
    exit /b 1
)

echo ✓ 后端依赖安装完成

:: 检查 .env 文件
if not exist .env (
    echo.
    echo ================================
    echo 2. 配置环境变量
    echo ================================
    copy .env.example .env
    echo ✓ 已创建 .env 文件
    echo ⚠️  请编辑 .env 文件，配置数据库连接信息
    echo.
    pause
)

:: 生成 Prisma Client
echo.
echo ================================
echo 3. 生成 Prisma Client
echo ================================
call npm run prisma:generate

if %errorlevel% neq 0 (
    echo ❌ Prisma Client 生成失败
    pause
    exit /b 1
)

echo ✓ Prisma Client 生成完成

:: 运行数据库迁移
echo.
echo ================================
echo 4. 运行数据库迁移
echo ================================
set /p MIGRATE="是否运行数据库迁移? (y/n): "
if /i "%MIGRATE%"=="y" (
    call npm run prisma:migrate

    if %errorlevel% neq 0 (
        echo ❌ 数据库迁移失败
        pause
        exit /b 1
    )

    echo ✓ 数据库迁移完成
)

:: 填充种子数据
echo.
echo ================================
echo 5. 填充种子数据
echo ================================
set /p SEED="是否填充种子数据? (y/n): "
if /i "%SEED%"=="y" (
    call npm run seed

    if %errorlevel% neq 0 (
        echo ❌ 填充种子数据失败
        pause
        exit /b 1
    )

    echo ✓ 种子数据填充完成
)

:: 返回根目录
cd ..

:: 进入前端目录
cd admin

echo.
echo ================================
echo 6. 安装前端依赖
echo ================================
call npm install

if %errorlevel% neq 0 (
    echo ❌ 前端依赖安装失败
    pause
    exit /b 1
)

echo ✓ 前端依赖安装完成

:: 完成
echo.
echo ================================
echo ✓ 安装完成！
echo ================================
echo.
echo 启动指南：
echo.
echo 1. 启动后端服务：
echo    cd server
echo    npm run dev
echo.
echo 2. 启动前端服务（新终端）：
echo    cd admin
echo    npm run dev
echo.
echo 3. 访问系统：
echo    前端: http://localhost:3000
echo    后端: http://localhost:3001
echo.
echo 默认账号：
echo    邮箱: admin@sillymd.com
echo    密码: admin123456
echo.
echo ================================
pause
