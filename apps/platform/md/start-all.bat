@echo off
chcp 65001 >nul
echo ================================
echo 启动 SillyMD CMS 开发环境
echo ================================
echo.

echo 正在启动后端服务...
start "SillyMD CMS Server" cmd /k "cd server && npm run dev"

timeout /t 3 /nobreak >nul

echo 正在启动前端服务...
start "SillyMD CMS Admin" cmd /k "cd admin && npm run dev"

echo.
echo ✓ 服务启动完成！
echo.
echo 前端地址: http://localhost:3000
echo 后端地址: http://localhost:3001
echo.
echo 默认账号：
echo   邮箱: admin@sillymd.com
echo   密码: admin123456
echo.
echo 按任意键关闭此窗口...
pause >nul
