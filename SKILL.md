---
name: skill-dynamic-page-to-markdown
description: 将 JavaScript 动态渲染网页的已渲染 DOM 内容提取、清洗并保存为 Markdown 文档。用于用户提供网页 URL，并要求“保存网页内容”“提取动态页面”“抓取 JS 渲染页面”“转成 Markdown”“保存对话页/文档页/文章页”为 Markdown 时触发；尤其适用于简单 HTTP 抓取拿不到正文、必须通过真实浏览器加载后再提取的场景。
disable-model-invocation: true
user-invocable: true
argument-hint: [webpage-url]
---

# Skill Dynamic Page to Markdown

## Goal

通过 browser-use MCP 驱动真实浏览器，加载 JavaScript 渲染的网页，提取其完整内容并保存为格式规范的 Markdown 文档。本技能只使用 browser-use 工具链，不回退到其他浏览器或抓取工具。

## Required Inputs

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `url` | URL 字符串 | 是 | 待提取的目标网页地址 |
| `output_path` | 文件路径 | 否 | 输出文件路径，默认为 `URL 解析的文件名.md` |
| `page_title` | 字符串 | 否 | 页面标题，未提供时从 `<title>` 标签或 URL 路径中推断 |

## Workflow

### Step 1：打开目标页面

使用 `browser-use_browser_navigate` 打开目标网页 URL。

### Step 2：验证页面加载

使用 `browser-use_browser_get_state` 截图确认页面已加载（`include_screenshot: true`）。

### Step 3：滚动加载全部内容

使用 `browser-use_browser_scroll` 触发懒加载内容。重复滚动直到所有内容可见。若页面无限滚动，则滚动至底部后等待 2 秒再继续，直到连续两次滚动后新增内容不再变化。

### Step 4：提取完整 HTML

使用 `browser-use_browser_get_html` 获取页面完整 DOM HTML。不要切换到 Playwright、通用 browser 工具或其他抓取工具。

### Step 4.5：确认 browser-use 会话状态

若 `browser-use_browser_get_html`、`browser-use_browser_get_state` 或相邻 browser-use 工具返回 `SessionManager not initialized`、会话未创建、浏览器未连接等错误，不要改用其他工具链。直接报告 browser-use MCP 运行环境异常，并要求先修复 browser-use 会话后再重试。

### Step 5：解析 HTML 结构

优先识别正文容器，并尽量排除导航、页脚、侧栏、弹窗和广告。优先级如下：

- 主内容区：`<main>`、`<article>`、`[role="main"]`
- 文本块：`<p>` 及包含连续文本的语义容器
- 列表：`<ul>`、`<ol>` 及其 `<li>` 子项
- 标题层级：保留 `<h1>` 至 `<h6>` 的层级关系
- 聊天/对话页面：按 `role`、消息容器结构或发言顺序区分用户与助手消息并标注归属

### Step 6：调用脚本转换为 Markdown

将 HTML 写入临时文件后，优先调用仓库内脚本：

```bash
python scripts/html_to_markdown.py --file <captured.html> --url "<url>" --title "<page_title>"
```

要求脚本输出满足以下规则：

- 移除 `<script>`、`<style>` 及其内容
- 保留语义结构：标题、列表、引用、链接、图片、代码块
- 保留代码块正文和语言标记
- 正文为空、代码块为空、出现大段样式文本时，视为转换失败

### Step 7：按模板格式化输出

```markdown
# [页面标题]

> 来源： [URL]
> 日期： YYYY年MM月DD日

---

[正文内容，保持正确标题层级]

---

*内容由 AI 提取，不能完全保障原始内容的完全准确性*
```

### Step 8：保存文档

将脚本标准输出写入 `output_path`（UTF-8 编码）。若未提供 `output_path`，则使用基于 URL 推断的文件名。

## Decision Rules

1. **页面加载失败**：重试导航最多 2 次，仍失败则报告错误
2. **内容被截断**：向下滚动后重新获取 HTML
3. **无法确定标题**：使用文件名或 URL 路径作为回退标题
4. **聊天/对话页面**：必须尽量区分用户消息与助手回复，并在 Markdown 中保留发言顺序
5. **代码块保留**：保留原始换行、缩进和语言标记（` ```lang `）
6. **图片处理**：若需保留图片，仅保留 `src` 与 Markdown 图片语法；不额外下载资源
7. **browser-use 会话异常**：若出现 `SessionManager not initialized`、浏览器未连接或会话丢失，停止执行并报告环境故障，不切换到其他工具
8. **正文定位失败**：先重新滚动并重新抓取 DOM；仍失败则在 browser-use 工具链内报告抓取失败，不跨工具回退

## Output Requirements

返回以下信息：

1. **文件路径**：保存的 Markdown 文件完整路径
2. **内容摘要**：标题数量、估计字符数、内容结构说明
3. **执行状态**：保存成功或错误详情

## Validation

1. 确认文件写入成功
2. 确认 Markdown 包含有意义内容（非空）
3. 确认标题层级被正确保留（`h1` → `#`，`h2` → `##`，以此类推）
4. 确认无残留 HTML 标签和大段 CSS/JS 文本
5. 确认代码块正文未丢失
6. 确认正文不是以站点导航、页脚或广告为主

## Fallback

| 失败场景 | 回退方案 |
|---------|---------|
| browser-use 会话异常 | 明确报告 browser-use MCP 运行环境异常，要求先修复会话或浏览器连接后重试 |
| DOM 提取或正文定位失败 | 在结果中标注 browser-use 已成功加载页面但正文识别失败，建议人工调整页面状态后重试 |
| 浏览器导航失败 | 提供手动保存指引（Ctrl+S / 打印为 PDF） |
| 文件写入失败 | 请用户确认输出目录有效性 |
| 内容仍不完整 | 在文档中标注「内容可能不完整，建议手动补充」|

## Examples

### Trigger Phrases

- `把这个页面保存成 Markdown`
- `提取这个动态页面正文并导出 markdown`
- `抓取这个 JS 渲染页面的内容`
- `把这个对话页面转成 markdown 文件`
- `把这个文档页/文章页保存为 markdown`

### 触发示例

- `把这个页面提取为 Markdown：https://example.com/article`
- `提取这个动态加载页面的内容并保存`
- `把这个 JS 渲染的网页抓取为 markdown 格式`
- `把这个聊天记录页面导出为 markdown：https://example.com/chat`
- `这个页面 curl 抓不到正文，帮我转成 markdown：https://example.com/docs`

### 端到端示例

用户：`把 https://github.com/JasonCai2024/skill-dynamic-page-to-markdown 的内容保存为 markdown`

执行流程：
1. `browser-use_browser_navigate` 打开目标页面
2. 截图确认加载成功
3. 滚动加载全部内容（README、代码块等）
4. `browser-use_browser_get_html` 获取完整 DOM
5. 识别 `<main>` 主内容区并排除导航、页脚等噪声
6. 调用 `scripts/html_to_markdown.py` 转换正文
7. 检查 Markdown 是否存在空代码块、样式文本或正文缺失
8. 写入 `skill-dynamic-page-to-markdown.md`

## Reference

仅在需要补充细节时读取 `references/`：

| 文件 | 内容 |
|------|------|
| `references/browser-use-mcp.md` | browser-use MCP 工具用法、推荐调用顺序、失败处理 |
| `references/markdown-template.md` | Markdown 模板、格式规范、转换检查清单 |
