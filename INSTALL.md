# 安装指南

本文件仅说明作为独立技能仓库时的获取方式。
本地扫描路径安装、手动 slash 调用、运行时本机配置等内容，应迁移到独立的本地安装说明文档。

## 前置依赖

- Python 3.8+（用于运行 `scripts/html_to_markdown.py`）
- 提供 browser-use MCP 能力的运行时
- 支持导入 GitHub 技能仓库的上游系统

## 获取仓库

```bash
git clone https://github.com/JasonCai2024/skill-dynamic-page-to-markdown.git
```

## 仓库导入要求

- 仓库根目录必须保留 `SKILL.md`、`references/`、`scripts/`
- `scripts/html_to_markdown.py` 需可被运行时调用
- `.env.example` 和 `.gitignore` 应随仓库一起保留

## 触发提示词

以下句式应能触发本技能：

- `把这个页面保存成 Markdown`
- `提取这个动态页面正文并导出 markdown`
- `抓取这个 JS 渲染页面的内容`
- `把这个对话页面转成 markdown 文件`
- `这个页面 curl 抓不到正文，帮我转成 markdown`
