#!/usr/bin/env python3
"""
更新中山律师地图标记点位置
基于图片视觉分析更新位置
地图说明：
- N (北) 在顶部
- 顶部标签: 蓝天东社区, 蓝天西社区
- 底部: 松江内环 → 松江大学城方向
- 有24个编号标记点
"""

import asyncio
import asyncpg
import os

# 基于图片视觉分析的位置数据
# 这些位置是根据图片结构估算的，需要根据实际OCR结果调整
POSITIONS = {
    # 顶部区域 (北) - 基于蓝天东社区、蓝天西社区标签位置
    "月厦": {"x": 20, "y": 10},       # 左上区域
    "星辰园": {"x": 38, "y": 8},     # 上中部
    "檀香": {"x": 52, "y": 10},      # 上中部偏右
    "御上海郡": {"x": 68, "y": 12},  # 上部右侧
    "东鼎": {"x": 85, "y": 15},      # 右上区域

    # 蓝天系列 - 顶部标签区域
    "蓝天一村": {"x": 15, "y": 18},  # 左上
    "蓝天二村": {"x": 30, "y": 16},  # 上中部左
    "蓝天四村": {"x": 58, "y": 14},  # 上中部右
    "蓝天五村": {"x": 45, "y": 22},  # 上中部
    "蓝天东": {"x": 38, "y": 28},    # 蓝天东社区标签位置
    "蓝天西": {"x": 58, "y": 26},    # 蓝天西社区标签位置

    # 上中部区域
    "方西": {"x": 12, "y": 32},      # 左上
    "北门": {"x": 32, "y": 30},      # 上中部
    "郑舍": {"x": 50, "y": 28},      # 中部偏上
    "花锦": {"x": 68, "y": 30},      # 中部偏上右
    "三湘四季": {"x": 82, "y": 32},  # 右中部
    "茸达": {"x": 88, "y": 35},      # 右侧

    # 中部区域
    "中山苑": {"x": 22, "y": 42},    # 中部偏左
    "同济雅筑": {"x": 40, "y": 38},  # 中部
    "花桥": {"x": 55, "y": 40},      # 中部偏右
    "茸树": {"x": 68, "y": 42},      # 中部偏右
    "东附件": {"x": 82, "y": 45},    # 中部右侧

    # 下部区域
    "莱顿": {"x": 15, "y": 58},      # 下部左侧
    "淡家浜": {"x": 32, "y": 60},    # 下部左侧
    "黄渡浜": {"x": 48, "y": 62},    # 下部中间
    "郭家河": {"x": 62, "y": 65},    # 下部偏右 (郭家河标签位置)
    "平桥": {"x": 72, "y": 58},      # 下部右侧

    # 底部区域 (南)
    "茸梅": {"x": 42, "y": 70},      # 下部
    "北九峰": {"x": 58, "y": 72},    # 下部
    "南其": {"x": 75, "y": 70},      # 下部右侧
    "方东": {"x": 55, "y": 78},      # 底部区域
    "白云": {"x": 70, "y": 80},      # 底部
    "南门": {"x": 85, "y": 82},      # 底部右侧
    "东外": {"x": 38, "y": 85},      # 底部左侧
    "茸吉": {"x": 52, "y": 88},      # 底部
    "茸星": {"x": 68, "y": 90},      # 底部
    "五龙": {"x": 32, "y": 92},      # 最底部
    "松汇": {"x": 45, "y": 55},      # 中部偏下
    "广富林": {"x": 88, "y": 68},    # 右侧下部

    # 额外的数据条目
    "星定": {"x": 92, "y": 38},       # 最右侧
}

async def update_positions():
    # 连接数据库
    conn = await asyncpg.connect(
        user='sillymd',
        password='sillymd123',
        host='www.sillymd.com',
        port=5432,
        database='sillymd'
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
            float(pos["x"]), float(pos["y"]), name
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
