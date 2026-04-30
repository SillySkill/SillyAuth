#!/usr/bin/env python3
"""
更新中山律师地图标记点位置
根据图片识别结果更新数据库中的坐标
"""

import asyncio
import asyncpg
import os

# 根据图片分析得到的24个居委会位置（百分比坐标）
POSITIONS = {
    "月厦": {"x": 22, "y": 12},
    "星辰园": {"x": 40, "y": 8},
    "檀香": {"x": 55, "y": 10},
    "御上海郡": {"x": 72, "y": 12},
    "东鼎": {"x": 88, "y": 14},
    "方西": {"x": 10, "y": 30},
    "郑舍": {"x": 28, "y": 28},
    "花锦": {"x": 44, "y": 26},
    "三湘四季": {"x": 60, "y": 28},
    "茸达": {"x": 76, "y": 30},
    "星定": {"x": 92, "y": 32},
    "中山苑": {"x": 22, "y": 46},
    "蓝天东": {"x": 42, "y": 48},
    "蓝天西": {"x": 60, "y": 46},
    "东附件": {"x": 76, "y": 50},
    "莱顿": {"x": 12, "y": 68},
    "淡家浜": {"x": 30, "y": 70},
    "黄渡浜": {"x": 48, "y": 72},
    "郭家河": {"x": 66, "y": 68},
    "广富林": {"x": 84, "y": 74},
    # 可能有缺失的居委会，添加占位
    "茸梅": {"x": 55, "y": 65},
    "松汇": {"x": 35, "y": 55},
    "南其": {"x": 50, "y": 58},
    "北九峰": {"x": 65, "y": 60},
}

async def update_positions():
    # 连接数据库
    db_url = os.environ.get('DATABASE_URL') or 'postgresql://sillymd:sillymd123@localhost:5432/sillymd'
    # 解析URL
    parts = db_url.replace('postgresql://', '').split('@')
    user_pass = parts[0].split(':')
    host_db = parts[1].split('/')
    host_port = host_db[0].split(':')

    conn = await asyncpg.connect(
        user=user_pass[0],
        password=user_pass[1],
        host=host_port[0],
        port=int(host_port[1]) if len(host_port) > 1 else 5432,
        database=host_db[1]
    )

    print("Connected to database")

    # 更新每个位置
    updated = 0
    not_found = []

    for name, pos in POSITIONS.items():
        result = await conn.execute(
            '''
            UPDATE config_data
            SET position_x = $1, position_y = $2, updated_at = NOW()
            WHERE category = 'public_law_service' AND name = $3
            ''',
            pos["x"], pos["y"], name
        )

        if result == "UPDATE 1":
            updated += 1
            print(f"  Updated: {name} -> ({pos['x']}%, {pos['y']}%)")
        else:
            not_found.append(name)

    print(f"\nUpdated {updated} positions")

    if not_found:
        print(f"Not found in database: {not_found}")

    await conn.close()
    print("Done!")

if __name__ == "__main__":
    asyncio.run(update_positions())
