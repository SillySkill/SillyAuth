@echo off
REM ============================================
REM SillyMD 数据库部署脚本 (Windows)
REM 版本: 1.0
REM ============================================

SETLOCAL EnableDelayedExpansion

SET SERVER=47.96.133.238
SET SSH_KEY=.ignore\silly.pem
SET REMOTE_USER=root
SET REMOTE_DIR=/opt/sillymd

REM ============================================
REM 部署流程
REM ============================================

echo ======================================
echo SillyMD 数据库部署开始
echo ======================================

REM 1. 检查本地文件
echo [1/6] 检查本地文件...
IF NOT EXIST "%SSH_KEY%" (
    echo [ERROR] 私钥文件不存在: %SSH_KEY%
    EXIT /B 1
)

REM 2. 创建远程目录
echo [2/6] 创建远程目录...
plink -i "%SSH_KEY%" -batch %REMOTE_USER%@%SERVER% "mkdir -p %REMOTE_DIR%/scripts %REMOTE_DIR%/migrations %REMOTE_DIR%/seeds"

REM 3. 上传文件
echo [3/6] 上传配置文件...
pscp -i "%SSH_KEY%" -batch docker-compose.yml %REMOTE_USER%@%SERVER%:%REMOTE_DIR%/

echo [4/6] 上传迁移脚本...
pscp -i "%SSH_KEY%" -batch -r migrations\*.sql %REMOTE_USER%@%SERVER%:%REMOTE_DIR%/migrations/

echo 上传执行脚本...
pscp -i "%SSH_KEY%" -batch scripts\*.sh %REMOTE_USER%@%SERVER%:%REMOTE_DIR%/scripts/

echo [5/6] 上传种子数据...
pscp -i "%SSH_KEY%" -batch -r ..\seeds\output\*.json %REMOTE_USER%@%SERVER%:%REMOTE_DIR%/seeds/

REM 4. 启动数据库
echo [6/6] 启动 PostgreSQL 数据库...
plink -i "%SSH_KEY%" -batch %REMOTE_USER%@%SERVER% bash -c "cd /opt/sillymd ^&^& docker-compose down 2^>^/dev/null ^|^| true ^&^& docker-compose up -d"

echo 等待数据库启动...
timeout /t 10 /nobreak >nul

REM 5. 执行迁移
echo 执行数据库迁移...
plink -i "%SSH_KEY%" -batch %REMOTE_USER%@%SERVER% "bash %REMOTE_DIR%/scripts/run-migrations.sh"

REM 6. 导入种子数据
echo 导入种子数据...
plink -i "%SSH_KEY%" -batch %REMOTE_USER%@%SERVER% "bash %REMOTE_DIR%/scripts/import-seeds.sh"

echo ======================================
echo 部署完成！
echo ======================================
echo 数据库连接信息：
echo   主机: %SERVER%
echo   端口: 5432
echo   数据库: sillymd
echo   用户: sillyAdmin
echo   密码: Jcoding2026
echo.
echo pgAdmin 访问地址：
echo   http://%SERVER%:5050
echo   邮箱: admin@sillymd.com
echo   密码: Jcoding2026
echo ======================================

PAUSE
