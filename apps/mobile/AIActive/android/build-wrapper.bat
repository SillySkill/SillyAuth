@echo off
REM 关闭Excel进程以释放临时文件
echo 检查Excel进程...
tasklist /FI "IMAGENAME eq EXCEL.EXE" 2>nul | find /I /N "EXCEL.EXE">nul
if "%ERRORLEVEL%"=="0" (
    echo 发现Excel进程正在运行，尝试关闭...
    taskkill /F /IM EXCEL.EXE >nul 2>&1
    timeout /t 2 /nobreak >nul
)

REM 清理Excel临时文件
echo 清理Excel临时文件...
for /r "src\main\assets" %%f in (~$*.xlsx ~$*.xls) do (
    if exist "%%f" (
        del /f /q "%%f" 2>nul
        if exist "%%f" (
            echo 无法删除: %%f
        ) else (
            echo 已删除: %%f
        )
    )
)

REM 执行Gradle构建
echo.
echo 开始构建...
call gradlew.bat assembleDebug
if %ERRORLEVEL% EQU 0 (
    echo.
    echo 构建成功，开始安装...
    adb install -r app\build\outputs\apk\debug\app-debug.apk
) else (
    echo 构建失败
)
pause
