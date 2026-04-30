#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中山街道公共法律服务信息种子数据
根据图片中的居委会名称和位置
"""
import os
import sys
import io
from pathlib import Path

# 修复Windows控制台编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.config_data.services import sync_config_data_service


def get_db_config():
    """获取数据库配置"""
    env_file = project_root / ".env"
    config = {}

    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()

    return {
        "host": config.get("DB_HOST", "localhost"),
        "port": int(config.get("DB_PORT", "5432")),
        "user": config.get("DB_USER", "postgres"),
        "password": config.get("DB_PASSWORD", ""),
        "database": config.get("DB_NAME", "sillymd"),
    }


def seed_public_law_services():
    """Import Zhongshan Street Public Law Service Data - Based on image coordinates"""
    print("[SEED] Importing Zhongshan Street Public Law Service Data...")

    category = "public_law_service"

    # 24个服务站数据 - 根据图片识别位置
    # 图片上的居委会名称和位置（百分比坐标）
    data_list = [
        # 第一行 (顶部)
        {
            "name": "月厦",
            "data": {
                "station_name": "月厦公共法律服务工作（站）室",
                "phone": "57786538",
                "address": "月厦小区",
                "lawyer": "待定",
                "lawyer_phone": "",
                "hours": "每月20日"
            },
            "position_x": 22,
            "position_y": 12
        },
        {
            "name": "星辰园",
            "data": {
                "station_name": "星辰园公共法律服务工作（站）室",
                "phone": "57786538",
                "address": "星辰园小区",
                "lawyer": "待定",
                "lawyer_phone": "",
                "hours": "每月20日"
            },
            "position_x": 40,
            "position_y": 8
        },
        {
            "name": "檀香",
            "data": {
                "station_name": "檀香公共法律服务工作（站）室",
                "phone": "57786538",
                "address": "檀香小区",
                "lawyer": "待定",
                "lawyer_phone": "",
                "hours": "每月20日"
            },
            "position_x": 55,
            "position_y": 10
        },
        {
            "name": "御上海郡",
            "data": {
                "station_name": "御上海郡公共法律服务工作（站）室",
                "phone": "57786538",
                "address": "御上海郡小区",
                "lawyer": "待定",
                "lawyer_phone": "",
                "hours": "每月20日"
            },
            "position_x": 72,
            "position_y": 12
        },
        {
            "name": "东鼎",
            "data": {
                "station_name": "东鼎公共法律服务工作（站）室",
                "phone": "57786538",
                "address": "东鼎小区",
                "lawyer": "待定",
                "lawyer_phone": "",
                "hours": "每月20日"
            },
            "position_x": 88,
            "position_y": 14
        },
        # 第二行
        {
            "name": "方西",
            "data": {
                "station_name": "方西公共法律服务工作（站）室",
                "phone": "57834965",
                "address": "中山东路165弄25号101室",
                "lawyer": "张金标",
                "lawyer_phone": "18817562422",
                "hours": "每月20号（上午9:00-11:00，下午13:00-17:00）"
            },
            "position_x": 10,
            "position_y": 30
        },
        {
            "name": "郑舍",
            "data": {
                "station_name": "郑舍公共法律服务工作（站）室",
                "phone": "57786538",
                "address": "郑舍小区",
                "lawyer": "待定",
                "lawyer_phone": "",
                "hours": "每月20日"
            },
            "position_x": 28,
            "position_y": 28
        },
        {
            "name": "花锦",
            "data": {
                "station_name": "花锦公共法律服务工作（站）室",
                "phone": "57786538",
                "address": "花锦小区",
                "lawyer": "待定",
                "lawyer_phone": "",
                "hours": "每月20日"
            },
            "position_x": 44,
            "position_y": 26
        },
        {
            "name": "三湘四季",
            "data": {
                "station_name": "三湘四季公共法律服务工作（站）室",
                "phone": "57786538",
                "address": "三湘四季小区",
                "lawyer": "待定",
                "lawyer_phone": "",
                "hours": "每月20日"
            },
            "position_x": 60,
            "position_y": 28
        },
        {
            "name": "茸达",
            "data": {
                "station_name": "茸达公共法律服务工作（站）室",
                "phone": "57786538",
                "address": "茸达小区",
                "lawyer": "待定",
                "lawyer_phone": "",
                "hours": "每月20日"
            },
            "position_x": 76,
            "position_y": 30
        },
        {
            "name": "星定",
            "data": {
                "station_name": "星定公共法律服务工作（站）室",
                "phone": "57786538",
                "address": "星定小区",
                "lawyer": "待定",
                "lawyer_phone": "",
                "hours": "每月20日"
            },
            "position_x": 92,
            "position_y": 32
        },
        # 第三行
        {
            "name": "中山苑",
            "data": {
                "station_name": "中山苑公共法律服务工作（站）室",
                "phone": "57783791",
                "address": "茸惠路758弄34号二楼",
                "lawyer": "张艳丽",
                "lawyer_phone": "13564820463",
                "hours": "每月第3个周二（上午9：00-11：00，下午13：00-17：00）"
            },
            "position_x": 22,
            "position_y": 46
        },
        {
            "name": "蓝天东",
            "data": {
                "station_name": "蓝天东公共法律服务工作（站）室",
                "phone": "57786538",
                "address": "蓝天东小区",
                "lawyer": "待定",
                "lawyer_phone": "",
                "hours": "每月20日"
            },
            "position_x": 42,
            "position_y": 48
        },
        {
            "name": "蓝天西",
            "data": {
                "station_name": "蓝天西公共法律服务工作（站）室",
                "phone": "57786538",
                "address": "蓝天西小区",
                "lawyer": "待定",
                "lawyer_phone": "",
                "hours": "每月20日"
            },
            "position_x": 60,
            "position_y": 46
        },
        {
            "name": "东附件",
            "data": {
                "station_name": "东附件公共法律服务工作（站）室",
                "phone": "57786538",
                "address": "东附件小区",
                "lawyer": "待定",
                "lawyer_phone": "",
                "hours": "每月20日"
            },
            "position_x": 76,
            "position_y": 50
        },
        # 第四行 (底部)
        {
            "name": "莱顿",
            "data": {
                "station_name": "莱顿公共法律服务工作（站）室",
                "phone": "57786538",
                "address": "莱顿小城46号楼底楼",
                "lawyer": "吴周杰",
                "lawyer_phone": "13681836930",
                "hours": "每月20日（上午9：00-11：00，下午13：00-17：00）"
            },
            "position_x": 12,
            "position_y": 68
        },
        {
            "name": "淡家浜",
            "data": {
                "station_name": "淡家浜公共法律服务工作（站）室",
                "phone": "67890573",
                "address": "淡家浜街88弄19号底楼",
                "lawyer": "金慧霞",
                "lawyer_phone": "13482726216",
                "hours": "每月20日（上午9：00-11：00，下午13：00-17：00）"
            },
            "position_x": 30,
            "position_y": 70
        },
        {
            "name": "黄渡浜",
            "data": {
                "station_name": "黄渡浜公共法律服务工作（站）室",
                "phone": "67670278",
                "address": "光星路1686号南侧",
                "lawyer": "金慧霞",
                "lawyer_phone": "13482726216",
                "hours": "每月10日（上午9：00-11：00，下午13：00-17：00）"
            },
            "position_x": 48,
            "position_y": 72
        },
        {
            "name": "郭家河",
            "data": {
                "station_name": "郭家河公共法律服务工作（站）室",
                "phone": "67789088",
                "address": "郭家河小区",
                "lawyer": "待定",
                "lawyer_phone": "",
                "hours": "每月20日"
            },
            "position_x": 66,
            "position_y": 68
        },
        {
            "name": "广富林",
            "data": {
                "station_name": "广富林公共法律服务工作（站）室",
                "phone": "57786538",
                "address": "广富林小区",
                "lawyer": "待定",
                "lawyer_phone": "",
                "hours": "每月20日"
            },
            "position_x": 84,
            "position_y": 74
        },
        # 补充剩余的服务站（图片上可能没有显示全）
        {
            "name": "松汇",
            "data": {
                "station_name": "松汇公共法律服务工作（站）室",
                "phone": "57786538",
                "address": "松汇小区",
                "lawyer": "待定",
                "lawyer_phone": "",
                "hours": "每月20日"
            },
            "position_x": 35,
            "position_y": 55
        },
        {
            "name": "茸梅",
            "data": {
                "station_name": "茸梅公共法律服务工作（站）室",
                "phone": "57782674",
                "address": "茸梅路200号天虹四村194号",
                "lawyer": "张婷",
                "lawyer_phone": "15202122794",
                "hours": "每月30号（2月最后一天）（上午9：00-11：00，下午13：00-17：00）"
            },
            "position_x": 50,
            "position_y": 65
        },
        {
            "name": "北九峰",
            "data": {
                "station_name": "北九峰公共法律服务工作（站）室",
                "phone": "57786538",
                "address": "北九峰小区",
                "lawyer": "待定",
                "lawyer_phone": "",
                "hours": "每月20日"
            },
            "position_x": 65,
            "position_y": 60
        },
        {
            "name": "南其",
            "data": {
                "station_name": "南其公共法律服务工作（站）室",
                "phone": "57786538",
                "address": "南其小区",
                "lawyer": "待定",
                "lawyer_phone": "",
                "hours": "每月20日"
            },
            "position_x": 58,
            "position_y": 58
        }
    ]

    # 导入数据
    for item in data_list:
        sync_config_data_service.upsert(
            category=category,
            name=item["name"],
            data=item["data"],
            position_x=item["position_x"],
            position_y=item["position_y"]
        )
        print(f"  [OK] {item['name']} -> ({item['position_x']}%, {item['position_y']}%)")

    print(f"\n[SUCCESS] Imported {len(data_list)} public law service records")


def main():
    print("=" * 50)
    print("Zhongshan Street Public Law Service Data Import")
    print("=" * 50)

    # Initialize table
    print("\n[INIT] Initializing database table...")
    sync_config_data_service.init_table()

    # 导入数据
    seed_public_law_services()

    print("\n[DONE] Completed!")


if __name__ == "__main__":
    main()
