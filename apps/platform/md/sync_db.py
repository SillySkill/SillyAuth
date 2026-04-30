#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import urllib.request
import urllib.parse
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Excel中的24个居委会
EXCEL_COMMUNITIES = [
    "莱顿", "淡家浜", "黄渡浜", "中山苑", "花桥", "郭家娄",
    "茸树", "茸梅", "茸星", "五龙", "北门", "方西",
    "蓝天一村", "蓝天二村", "蓝天四村", "蓝天五村", "同济雅筑", "平桥",
    "东外", "方东", "白云", "南门", "茸虹", "茸吉"
]

def get_all_items():
    url = "https://www.sillymd.com/api/config-data/list/public_law_service"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read().decode('utf-8'))
    return data['data']['items']

def delete_item(name):
    url = f"https://www.sillymd.com/api/config-data/public_law_service/{urllib.parse.quote(name)}"
    req = urllib.request.Request(url, method='DELETE')
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return True
    except Exception as e:
        print(f"    Error: {e}")
        return False

def create_item(name, data):
    url = "https://www.sillymd.com/api/config-data/"
    json_data = json.dumps({
        "category": "public_law_service",
        "name": name,
        "data": data,
        "position_x": 50,
        "position_y": 50
    }).encode('utf-8')

    req = urllib.request.Request(url, data=json_data, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return True
    except Exception as e:
        print(f"    Error: {e}")
        return False

print("同步数据库与Excel...")
print("=" * 60)

# 获取数据库中的所有条目
items = get_all_items()
db_names = [item['name'] for item in items]
print(f"Excel中有 {len(EXCEL_COMMUNITIES)} 个居委会")
print(f"数据库中有 {len(db_names)} 个居委会")

# 找出需要删除的（数据库中有但Excel中没有的）
to_delete = [name for name in db_names if name not in EXCEL_COMMUNITIES]
print(f"\n需要删除 {len(to_delete)} 个不在Excel中的条目：")
for name in to_delete:
    print(f"  - {name}")

# 找出需要添加的（Excel中有但数据库中没有的）
to_add = [name for name in EXCEL_COMMUNITIES if name not in db_names]
print(f"\n需要添加 {len(to_add)} 个Excel中有但数据库中没有的条目：")
for name in to_add:
    print(f"  - {name}")

# 执行删除
if to_delete:
    print("\n" + "=" * 60)
    print("删除不在Excel中的条目...")
    for name in to_delete:
        print(f"  删除 {name}...", end=" ")
        if delete_item(name):
            print("成功")
        else:
            print("失败")

print("\n" + "=" * 60)
print("同步完成！")
