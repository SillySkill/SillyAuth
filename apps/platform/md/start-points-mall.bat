@echo off
REM 积分商城快速启动脚本
REM 用于启动API服务和打开前端页面

echo ========================================
echo 积分商城系统 - 快速启动
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

echo [1/3] 检查数据库连接...
cd server\api
python test-db-connection.py
if %errorlevel% neq 0 (
    echo 警告: 数据库连接失败，请检查配置
    echo 继续启动可能会失败...
)
echo.

echo [2/3] 启动API服务器...
echo API服务将运行在: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.
echo 按Ctrl+C停止服务器
echo.

start "SillyMD API" python main.py

REM 等待API服务器启动
echo 等待API服务器启动...
timeout /t 3 /nobreak >nul

REM 检查API是否启动成功
curl -s http://localhost:8000/api/health >nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: API服务器可能未成功启动
) else (
    echo API服务器启动成功！
)

echo.

echo [3/3] 打开积分商城页面...
start "" "..\..\examples\points-mall.html"

echo.
echo ========================================
echo 启动完成！
echo ========================================
echo.
echo 积分商城页面: examples/points-mall.html
echo API服务器: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.
echo 如需测试API，运行:
echo   cd server\api
echo   python test_points_mall.py
echo.
echo 按任意键退出此窗口（API服务器将继续运行）...
pause >nul
