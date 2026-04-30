# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

### 飞书文件发送

**正确方式**：使用 `message` 工具的 `filePath` 参数直接发送本地文件

```json
{
  "action": "send",
  "channel": "feishu",
  "filePath": "C:\\Users\\Jcoding\\.openclaw\\workspace\\文件.mp4",
  "target": "oc_xxx"
}
```

**适用**：视频、图片、文档、压缩包等所有文件

**注意**：
- 飞书可以正确显示本地文件
- 不要使用 mediaUrl 或 media 参数，那会发送文件夹路径
- 确保文件是本地真实存在的

---

### 聊天记录备份（2026-02-19新增）

**规则**：
1. 每次群聊结束后，将对话内容备份到 `聊天记录/` 目录
2. 文件名：群名_年月日.md
3. 同步创建要点记录文件：群名_要点记录.md
4. 群名更改时：文件名自动更改为新群名

**示例**：
- 聊天记录：马年营销首战AI战斗员群.md
- 要点记录：马年营销首战AI战斗员群_要点记录.md
