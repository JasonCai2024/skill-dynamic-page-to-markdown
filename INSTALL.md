# 安装指南

## 前置依赖

- 可正常初始化会话的 `browser-use` MCP 运行时
- Python 3.8+
- 支持导入 GitHub 技能仓库的上游系统

## 获取仓库

```bash
git clone https://github.com/JasonCai2024/skill-dynamic-page-to-markdown.git
```

## 仓库导入要求

- 根目录保留 `SKILL.md`
- 保留 `references/`
- 保留 `scripts/html_to_markdown.py`

## 触发提示词

- `把这个动态网页保存成 Markdown`
- `提取这个 JS 渲染页面正文`
- `这个页面要加载完才能抓，帮我转成 markdown`
- `把这个文档页完整导出为 Markdown`

## 运行边界

- 本技能只使用 `browser-use` 浏览器工具链
- 不应回退到 Playwright 或其他浏览器工具
- 若出现 `SessionManager not initialized`、浏览器未连接、会话丢失等错误，应先修复 `browser-use` 运行环境

## 设计变化说明

当前版本与早期版本的关键区别：

- 早期版本偏向“抓完整 HTML 再转 Markdown”
- 当前版本明确改为“Browser Use 驱动运行态页面，再采集正文”

也就是说：

- `browser-use` 是主提取引擎
- `html_to_markdown.py` 只是整理脚本
