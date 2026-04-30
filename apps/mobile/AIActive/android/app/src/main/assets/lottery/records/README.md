# 抽奖记录存储目录

本目录用于存储抽奖活动的运行时数据，包括中奖记录和剩余候选人信息。

## 文件说明

### winners.json
存储所有中奖者的记录信息。

**格式：**
```json
{
  "winners": [
    {
      "candidate_id": "U100156001",
      "candidate_name": "七分甜",
      "department": "开元商铺",
      "prize_name": "一等奖",
      "winner_time": "2026-01-24 12:00:00",
      "program_id": "jlot10004"
    }
  ],
  "last_updated": "2026-01-24 12:00:00",
  "version": "1.0"
}
```

### remaining_candidates.json
存储当前剩余可用的候选人ID列表。

**格式：**
```json
{
  "remaining_candidate_ids": ["U100156001", "U100156002"],
  "total_count": 2,
  "last_updated": "2026-01-24 12:00:00",
  "auto_reset": false
}
```

## 使用场景

1. **数据持久化** - 应用关闭后保留抽奖进度
2. **数据备份** - 可导出进行数据备份
3. **断点续抽** - 重启应用后继续抽奖
4. **审计追踪** - 查看历史中奖记录

## 管理说明

- 这些文件会在应用首次运行时自动创建
- 支持手动编辑这些JSON文件来导入/导出数据
- 重置抽奖时会清空这些文件
