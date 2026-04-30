@echo off
REM ============================================
REM SillyMD 数据库迁移执行脚本 (Windows)
REM 版本: 1.0
REM 描述: 自动执行所有未应用的数据库迁移
REM ============================================

SETLOCAL EnableDelayedExpansion

REM ============================================
REM 配置变量
REM ============================================

REM 数据库连接配置
IF "%DB_HOST%"=="" SET DB_HOST=localhost
IF "%DB_PORT%"=="" SET DB_PORT=5432
IF "%DB_NAME%"=="" SET DB_NAME=sillymd
IF "%DB_USER%"=="" SET DB_USER=postgres

REM 迁移脚本目录
SET MIGRATIONS_DIR=%~dp0
SET LOG_FILE=%MIGRATIONS_DIR%migration_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log
SET LOG_FILE=%LOG_FILE: =0%

REM ============================================
REM 日志函数
REM ============================================

:log
echo [%date% %time%] %~1
echo [%date% %time%] %~1 >> "%LOG_FILE%"
GOTO :EOF

:error
echo [ERROR] [%date% %time%] %~1
echo [ERROR] [%date% %time%] %~1 >> "%LOG_FILE%"
GOTO :EOF

:warn
echo [WARN] [%date% %time%] %~1
echo [WARN] [%date% %time%] %~1 >> "%LOG_FILE%"
GOTO :EOF

:info
echo [INFO] [%date% %time%] %~1
echo [INFO] [%date% %time%] %~1 >> "%LOG_FILE%"
GOTO :EOF

REM ============================================
REM 检查函数
REM ============================================

:check_dependencies
CALL :log "检查依赖..."
WHERE psql >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    CALL :error "psql 未安装，请先安装 PostgreSQL 客户端"
    EXIT /B 1
)
CALL :info "依赖检查完成"
GOTO :EOF

:check_connection
CALL :log "检查数据库连接..."
SET PGPASSWORD=%DB_PASSWORD%
psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d postgres -c \q >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    CALL :error "无法连接到数据库服务器"
    CALL :error "请检查连接配置: host=%DB_HOST% port=%DB_PORT% user=%DB_USER%"
    EXIT /B 1
)
CALL :info "数据库连接成功"
GOTO :EOF

:check_database
CALL :log "检查数据库是否存在..."
SET PGPASSWORD=%DB_PASSWORD%
FOR /f "delims=" %%i IN ('psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -lqt ^| cut -d "%%" -f 1 ^| findstr /x "%DB_NAME%"') DO SET DB_EXISTS=%%i
IF "%DB_EXISTS%"=="" (
    CALL :warn "数据库 %DB_NAME% 不存在，将自动创建"
    CALL :info "创建数据库: %DB_NAME%"
    psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d postgres -c "CREATE DATABASE %DB_NAME% ENCODING 'UTF8';"
    CALL :log "数据库创建成功"
) ELSE (
    CALL :info "数据库 %DB_NAME% 已存在"
)
GOTO :EOF

REM ============================================
REM 执行迁移
REM ============================================

:apply_migration
SET FILE=%~1
SET FILENAME=%~n1%~x1
SET VERSION=%~n1

REM 检查是否已应用
SET PGPASSWORD=%DB_PASSWORD%
FOR /f "delims=" %%i IN ('psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -tAc "SELECT COUNT(*) FROM schema_migrations WHERE version=''!VERSION!'';" 2^>nul') DO SET APPLIED_COUNT=%%i

IF !APPLIED_COUNT! GTR 0 (
    CALL :info "跳过已应用的迁移: %FILENAME%"
    GOTO :EOF
)

CALL :log "应用迁移: %FILENAME%"

SET PGPASSWORD=%DB_PASSWORD%
psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -f "%FILE%" >> "%LOG_FILE%" 2>&1
IF %ERRORLEVEL% EQU 0 (
    CALL :log "迁移 %FILENAME% 应用成功"
    GOTO :EOF
) ELSE (
    CALL :error "迁移 %FILENAME% 应用失败，请查看日志: %LOG_FILE%"
    EXIT /B 1
)

REM ============================================
REM 主流程
REM ============================================

:main
CALL :log "======================================"
CALL :log "SillyMD 数据库迁移开始"
CALL :log "======================================"
CALL :log "数据库: %DB_NAME%@%DB_HOST%:%DB_PORT%"
CALL :log "迁移目录: %MIGRATIONS_DIR%"
CALL :log "======================================"

REM 检查依赖
CALL :check_dependencies
IF %ERRORLEVEL% NEQ 0 EXIT /B %ERRORLEVEL%

REM 检查连接
CALL :check_connection
IF %ERRORLEVEL% NEQ 0 EXIT /B %ERRORLEVEL%

REM 检查数据库
CALL :check_database
IF %ERRORLEVEL% NEQ 0 EXIT /B %ERRORLEVEL%

REM 获取所有迁移文件
CALL :info "扫描迁移文件..."

SET COUNT=0
FOR %%f IN ("%MIGRATIONS_DIR%\*.sql") DO (
    SET /A COUNT+=1
)

IF %COUNT% EQU 0 (
    CALL :warn "未找到迁移文件"
    EXIT /B 0
)

CALL :info "找到 %COUNT% 个迁移文件"

REM 执行迁移
SET TOTAL=0
SET APPLIED=0
SET FAILED=0

FOR %%f IN ("%MIGRATIONS_DIR%0*.sql") DO (
    SET /A TOTAL+=1
    CALL :apply_migration "%%f"
    IF %ERRORLEVEL% EQU 0 (
        SET /A APPLIED+=1
    ) ELSE (
        SET /A FAILED+=1
        CALL :error "迁移失败，停止执行"
        GOTO show_result
    )
)

:show_result
CALL :log "======================================"
CALL :log "迁移执行完成"
CALL :log "总迁移数: %TOTAL%"
CALL :log "应用成功: %APPLIED%"
CALL :log "失败: %FAILED%"
CALL :log "日志文件: %LOG_FILE%"
CALL :log "======================================"

IF %FAILED% GTR 0 EXIT /B 1
GOTO :EOF

REM ============================================
REM 启动
REM ============================================

CALL :main
