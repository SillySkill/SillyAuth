"""
初始化教程和下载资源的示例数据
"""
import os
import sys

# 添加server/api到路径
server_api_path = os.path.join(os.path.dirname(__file__), '..', 'api')
sys.path.insert(0, server_api_path)

from database import get_db
from psycopg2.extras import RealDictCursor


def init_tutorials_and_downloads():
    """初始化教程和下载数据"""

    # 从环境变量获取数据库配置
    DB_CONFIG = {
        "host": os.getenv("DB_HOST", "47.96.133.238"),
        "port": int(os.getenv("DB_PORT", 5432)),
        "database": os.getenv("DB_NAME", "sillymd"),
        "user": os.getenv("DB_USER", "sillymd"),
        "password": os.getenv("DB_PASSWORD", "sillymd@2025")
    }

    print("=" * 60)
    print("初始化教程和下载资源数据")
    print("=" * 60)

    try:
        with get_db(DB_CONFIG) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:

                # 检查现有数据
                cur.execute('SELECT COUNT(*) as count FROM tutorials')
                tutorial_count = cur.fetchone()['count']
                print(f"\n现有教程数量: {tutorial_count}")

                cur.execute('SELECT COUNT(*) as count FROM downloads')
                download_count = cur.fetchone()['count']
                print(f"现有下载资源数量: {download_count}")

                # 插入教程数据
                if tutorial_count == 0:
                    print("\n插入示例教程...")
                    cur.execute('''
                        INSERT INTO tutorials (
                            tutorial_key, slug,
                            title_zh_CN, title_en,
                            description_zh_CN, description_en,
                            content_zh_CN, content_en,
                            category, subcategory, difficulty,
                            tags, featured, is_published,
                            position, view_count, like_count,
                            published_at, created_at
                        ) VALUES
                        (
                            'claude-code-getting-started',
                            'claude-code-getting-started',
                            'Claude Code 入门教程',
                            'Claude Code Getting Started',
                            '学习如何安装和使用 Anthropic Claude Code，这款强大的 AI 编程助手',
                            'Learn how to install and use Anthropic Claude Code, the powerful AI coding assistant',
                            '本教程将带你从零开始学习 Claude Code 的安装、配置和基本使用方法。',
                            'This tutorial will take you from zero to hero with Claude Code installation, configuration, and basic usage.',
                            'claude-code',
                            'installation',
                            'beginner',
                            'AI编程, Claude, 教程',
                            TRUE,
                            TRUE,
                            1,
                            0,
                            0,
                            CURRENT_TIMESTAMP,
                            CURRENT_TIMESTAMP
                        ),
                        (
                            'openclaw-ai-assistant',
                            'openclaw-ai-assistant',
                            'OpenClaw AI 助手完全指南',
                            'OpenClaw AI Assistant Complete Guide',
                            '深入了解 OpenClaw AI 助手的功能和使用技巧',
                            'Deep dive into OpenClaw AI Assistant features and usage tips',
                            'OpenClaw 是一款创新的 AI 助手工具，本教程将介绍其核心功能和高级用法。',
                            'OpenClaw is an innovative AI assistant tool. This tutorial introduces its core features and advanced usage.',
                            'openclaw',
                            'usage',
                            'intermediate',
                            'AI助手, OpenClaw, 进阶',
                            TRUE,
                            TRUE,
                            2,
                            0,
                            0,
                            CURRENT_TIMESTAMP,
                            CURRENT_TIMESTAMP
                        ),
                        (
                            'cursor-ide-basics',
                            'cursor-ide-basics',
                            'Cursor IDE 基础教程',
                            'Cursor IDE Basics Tutorial',
                            '掌握 Cursor IDE 的核心功能和快捷键',
                            'Master Cursor IDE core features and shortcuts',
                            'Cursor 是一款强大的 AI 原生 IDE，本教程教你如何高效使用它。',
                            'Cursor is a powerful AI-native IDE. This tutorial teaches you how to use it efficiently.',
                            'cursor',
                            'usage',
                            'beginner',
                            'IDE, Cursor, 快捷键',
                            FALSE,
                            TRUE,
                            3,
                            0,
                            0,
                            CURRENT_TIMESTAMP,
                            CURRENT_TIMESTAMP
                        ),
                        (
                            'windsurf-surfing-ai',
                            'windsurf-surfing-ai',
                            'Windsurf AI 冲浪指南',
                            'Windsurf AI Surfing Guide',
                            '探索 Windsurf AI 的无限可能',
                            'Explore the infinite possibilities of Windsurf AI',
                            'Windsurf 提供了独特的 AI 辅助编程体验，让我们一起探索吧！',
                            'Windsurf offers a unique AI-assisted coding experience. Let''s explore!',
                            'windsurf',
                            'tips',
                            'intermediate',
                            'Windsurf, AI, 技巧',
                            FALSE,
                            TRUE,
                            4,
                            0,
                            0,
                            CURRENT_TIMESTAMP,
                            CURRENT_TIMESTAMP
                        )
                        ON CONFLICT (tutorial_key) DO NOTHING
                    ''')
                    conn.commit()
                    print(f"✓ 插入了示例教程")

                    # 插入章节数据
                    cur.execute('''
                        INSERT INTO tutorial_chapters (
                            tutorial_id, chapter_order, chapter_key,
                            title_zh_CN, title_en,
                            description_zh_CN, description_en,
                            content_zh_CN, content_en,
                            is_free
                        ) VALUES
                        (1, 1, 'chapter-1', '第一章：认识 Claude Code', 'Chapter 1: Meet Claude Code',
                         '了解 Claude Code 是什么', 'Learn what Claude Code is',
                         'Claude Code 是...', 'Claude Code is...', TRUE),
                        (1, 2, 'chapter-2', '第二章：安装与配置', 'Chapter 2: Installation',
                         '安装 Claude Code', 'Install Claude Code',
                         '安装步骤...', 'Installation steps...', TRUE),
                        (2, 1, 'chapter-1', '第一章：OpenClaw 简介', 'Chapter 1: OpenClaw Introduction',
                         'OpenClaw 是什么', 'What is OpenClaw',
                         'OpenClaw 是...', 'OpenClaw is...', TRUE)
                        ON CONFLICT DO NOTHING
                    ''')
                    conn.commit()
                    print(f"✓ 插入了示例章节")
                else:
                    print("✓ 教程数据已存在")

                # 插入下载数据
                if download_count == 0:
                    print("\n插入示例下载资源...")
                    cur.execute('''
                        INSERT INTO downloads (
                            download_key, slug,
                            title_zh_CN, title_en,
                            description_zh_CN, description_en,
                            category, subcategory,
                            version, platform,
                            file_name, file_url, file_size, file_type,
                            github_url, official_url,
                            featured, is_published, is_official,
                            position, download_count, view_count, like_count,
                            published_at, created_at
                        ) VALUES
                        (
                            'wsl2-windows',
                            'wsl2-windows',
                            'WSL2 for Windows 安装包',
                            'WSL2 for Windows Installer',
                            '适用于 Windows 10/11 的 WSL2 安装包，国内镜像下载',
                            'WSL2 installer for Windows 10/11, mirror download',
                            'wsl',
                            'installer',
                            '2.0.0',
                            'windows',
                            'wsl.2.0.0.x64.msi',
                            'https://jc-st.tos-cn-shanghai.volces.com/sillymd/downloads/wsl.2.0.0.x64.msi',
                            256000000,
                            'msi',
                            'https://github.com/microsoft/WSL',
                            'https://learn.microsoft.com/en-us/windows/wsl/',
                            TRUE,
                            TRUE,
                            TRUE,
                            1,
                            0,
                            0,
                            0,
                            CURRENT_TIMESTAMP,
                            CURRENT_TIMESTAMP
                        ),
                        (
                            'python-312-windows',
                            'python-312-windows',
                            'Python 3.12 for Windows',
                            'Python 3.12 for Windows',
                            'Python 3.12.1 Windows x64 安装包，国内镜像下载',
                            'Python 3.12.1 Windows x64 installer, mirror download',
                            'python',
                            'installer',
                            '3.12.1',
                            'windows',
                            'python-3.12.1-amd64.exe',
                            'https://jc-st.tos-cn-shanghai.volces.com/sillymd/downloads/python-3.12.1-amd64.exe',
                            25600000,
                            'exe',
                            'https://www.python.org/downloads/',
                            'https://www.python.org/',
                            TRUE,
                            TRUE,
                            TRUE,
                            2,
                            0,
                            0,
                            0,
                            CURRENT_TIMESTAMP,
                            CURRENT_TIMESTAMP
                        ),
                        (
                            'git-windows',
                            'git-windows',
                            'Git for Windows',
                            'Git for Windows',
                            'Git 版本控制工具 Windows 版本',
                            'Git version control tool for Windows',
                            'git',
                            'installer',
                            '2.43.0',
                            'windows',
                            'Git-2.43.0-64-bit.exe',
                            'https://jc-st.tos-cn-shanghai.volces.com/sillymd/downloads/Git-2.43.0-64-bit.exe',
                            50000000,
                            'exe',
                            'https://git-scm.com/',
                            'https://git-scm.com/',
                            FALSE,
                            TRUE,
                            TRUE,
                            3,
                            0,
                            0,
                            0,
                            CURRENT_TIMESTAMP,
                            CURRENT_TIMESTAMP
                        ),
                        (
                            'vscode-windows',
                            'vscode-windows',
                            'Visual Studio Code',
                            'Visual Studio Code',
                            '强大的代码编辑器 VS Code',
                            'Powerful code editor VS Code',
                            'vscode',
                            'installer',
                            '1.85.0',
                            'windows',
                            'VSCodeUserSetup-x64.exe',
                            'https://jc-st.tos-cn-shanghai.volces.com/sillymd/downloads/VSCodeUserSetup-x64.exe',
                            90000000,
                            'exe',
                            'https://code.visualstudio.com/',
                            'https://code.visualstudio.com/',
                            TRUE,
                            TRUE,
                            TRUE,
                            4,
                            0,
                            0,
                            0,
                            CURRENT_TIMESTAMP,
                            CURRENT_TIMESTAMP
                        ),
                        (
                            'nodejs-windows',
                            'nodejs-windows',
                            'Node.js for Windows',
                            'Node.js for Windows',
                            'Node.js JavaScript 运行时',
                            'Node.js JavaScript runtime',
                            'nodejs',
                            'installer',
                            '20.10.0',
                            'windows',
                            'node-v20.10.0-x64.msi',
                            'https://jc-st.tos-cn-shanghai.volces.com/sillymd/downloads/node-v20.10.0-x64.msi',
                            35000000,
                            'msi',
                            'https://nodejs.org/',
                            'https://nodejs.org/',
                            FALSE,
                            TRUE,
                            TRUE,
                            5,
                            0,
                            0,
                            0,
                            CURRENT_TIMESTAMP,
                            CURRENT_TIMESTAMP
                        )
                        ON CONFLICT (download_key) DO NOTHING
                    ''')
                    conn.commit()
                    print(f"✓ 插入了示例下载资源")

                    # 插入版本数据
                    cur.execute('''
                        INSERT INTO download_versions (
                            download_id, version, version_code,
                            file_name, file_url, file_size,
                            release_date, is_latest, is_stable
                        ) VALUES
                        (1, '2.0.0', 2000000, 'wsl.2.0.0.x64.msi',
                         'https://jc-st.tos-cn-shanghai.volces.com/sillymd/downloads/wsl.2.0.0.x64.msi',
                         256000000, CURRENT_DATE, TRUE, TRUE),
                        (2, '3.12.1', 31201, 'python-3.12.1-amd64.exe',
                         'https://jc-st.tos-cn-shanghai.volces.com/sillymd/downloads/python-3.12.1-amd64.exe',
                         25600000, '2024-01-15', TRUE, TRUE),
                        (4, '1.85.0', 18500, 'VSCodeUserSetup-x64.exe',
                         'https://jc-st.tos-cn-shanghai.volces.com/sillymd/downloads/VSCodeUserSetup-x64.exe',
                         90000000, '2024-01-10', TRUE, TRUE)
                        ON CONFLICT DO NOTHING
                    ''')
                    conn.commit()
                    print(f"✓ 插入了示例版本数据")
                else:
                    print("✓ 下载资源数据已存在")

                # 查询统计信息
                cur.execute('SELECT COUNT(*) as count FROM tutorials WHERE is_published = TRUE')
                published_tutorials = cur.fetchone()['count']

                cur.execute('SELECT COUNT(*) as count FROM downloads WHERE is_published = TRUE')
                published_downloads = cur.fetchone()['count']

                print("\n" + "=" * 60)
                print("数据初始化完成")
                print("=" * 60)
                print(f"已发布教程: {published_tutorials} 条")
                print(f"已发布资源: {published_downloads} 条")
                print("=" * 60)

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    init_tutorials_and_downloads()
