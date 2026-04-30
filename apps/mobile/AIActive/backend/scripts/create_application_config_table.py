"""
创建 application_configs 表的脚本
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from database_admin import engine


async def create_table():
    """创建 application_configs 表"""
    async with engine.begin() as conn:
        # 创建表
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS application_configs (
                id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
                app_id VARCHAR(100) NOT NULL UNIQUE COMMENT '统一应用标识(如com.jcoding.aiactivity)',
                app_name VARCHAR(100) NOT NULL COMMENT '应用名称',
                package_name VARCHAR(100) COMMENT '包名',
                version VARCHAR(20) COMMENT '版本号',
                config JSON NOT NULL COMMENT 'JSON配置，存储所有配置项',
                status SMALLINT DEFAULT 1 COMMENT '状态: 1=启用, 0=禁用',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                INDEX idx_app_id (app_id),
                INDEX idx_status (status)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='应用配置表';
        """))

        print("✓ 表 application_configs 创建成功")

        # 插入默认配置（基于Android端的config.json）
        default_config = {
            "app": {
                "name": "AI活动秀",
                "version": "1.0.0",
                "debug": True
            },
            "features": {
                "ai_show": {
                    "enabled": True,
                    "invite_code_mode": True,
                    "payment_mode": True,
                    "employee_mode": True,
                    "auto_close_time": 20
                },
                "quiz": {
                    "enabled": True,
                    "voice_input": False,
                    "push_prize": True
                },
                "lottery": {
                    "enabled": True,
                    "voice_trigger": False,
                    "push_winner": True
                },
                "inner_show": {
                    "enabled": True,
                    "digital_human_announce": True
                }
            }
        }

        # 检查是否已存在默认配置
        result = await conn.execute(
            text("SELECT COUNT(*) FROM application_configs WHERE app_id = 'com.jcoding.aiactivity'")
        )
        count = result.scalar()

        if count == 0:
            await conn.execute(text("""
                INSERT INTO application_configs (app_id, app_name, package_name, version, config, status)
                VALUES (:app_id, :app_name, :package_name, :version, :config, 1)
            """), {
                'app_id': 'com.jcoding.aiactivity',
                'app_name': 'AI活动秀',
                'package_name': 'com.jcoding.aiactivity',
                'version': '1.0.0',
                'config': str(default_config).replace("'", '"')
            })
            print("✓ 默认配置插入成功")
        else:
            print("ℹ 默认配置已存在，跳过插入")


if __name__ == "__main__":
    print("开始创建 application_configs 表...")
    asyncio.run(create_table())
    print("完成！")
