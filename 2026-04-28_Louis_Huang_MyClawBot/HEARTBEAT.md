# HEARTBEAT.md

## 测试任务：检测 heartbeat 传入的 metadata

收到 heartbeat 时，报告收到的完整消息内容和 metadata（特别是 `updatedAt` 或时间戳相关字段），然后回复 HEARTBEAT_OK。

## 写入 last-interaction.json

如果 heartbeat 消息中包含 Louis 最后一条消息的时间戳（`updatedAt` 或类似字段），则将其写入 `memory/last-interaction.json`（单时间戳格式：`{"lastInteraction": "..."}`）。

格式要求：ISO 8601，带时区，例如 `2026-04-28T15:45:00+08:00`
