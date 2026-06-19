---
name: skill-dynamic-page-to-markdown
description: 将 JavaScript 动态渲染的网页内容提取并保存为 Markdown 文档。当用户提供包含 JS 渲染内容的网页 URL，且无法通过简单 HTTP 请求提取时触发。触发词：保存网页内容、提取动态页面、抓取 JS 渲染页面。
disable-model-invocation: true
user-invocable: true
argument-hint: [webpage-url]
---

# Skill Dynamic Page to Markdown

## Goal

通过 browser-use MCP 驱动真实浏览器，加载 JavaScript 渲染的网页，提取其完整内容并保存为格式规范的 Markdown 文档。

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

使用 `browser-use_browser_scroll` 触发懒加载内容。重复滚动直到所有内容可见。若页面无限滚动，则滚动至底部后等待 2 秒再继续，直到新增内容不再变化。

### Step 4：提取完整 HTML

使用 `browser-use_browser_get_html` 获取页面完整 DOM HTML。**不要**使用 `browser-use_browser_extract_content`，后者无法获取 JS 渲染页面的真实 DOM。

### Step 5：解析 HTML 结构

从 HTML 中识别语义内容容器：

- 主内容区：`<main>`、`<article>` 或其他主内容容器
- 文本块：`<p>`、`<div>` 含文本的节点
- 列表：`<ul>`、`<ol>` 及其 `<li>` 子项
- 标题层级：保留 `<h1>` 至 `<h6>` 的层级关系
- 聊天/对话页面：按 `role` 属性区分用户与助手消息并标注归属

### Step 6：清理并转换为 Markdown

- 移除 `<script>`、`<style>` 标签及全部属性
- 保留语义结构：标题、列表、引用、代码块
- 将 HTML 标签转换为对应 Markdown 格式

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

使用 `write` 工具写入文件（UTF-8 编码）。

## Decision Rules

1. **页面加载失败**：重试导航最多 2 次，仍失败则报告错误
2. **内容被截断**：向下滚动后重新获取 HTML
3. **无法确定标题**：使用文件名或 URL 路径作为回退标题
4. **聊天/对话页面**：必须按 `role` 区分用户消息与助手回复，并标注来源
5. **代码块保留**：保留原始缩进和语言标记（` ```lang `）
6. **图片处理**：若需保留图片，提取 `src` 属性并保留 Markdown 图片语法；不需要额外下载

## Output Requirements

返回以下信息：

1. **文件路径**：保存的 Markdown 文件完整路径
2. **内容摘要**：标题数量、估计字符数、内容结构说明
3. **执行状态**：保存成功或错误详情

## Validation

1. 确认文件写入成功
2. 确认 Markdown 包含有意义内容（非空）
3. 确认标题层级被正确保留（`h1` → `#`，`h2` → `##`，以此类推）
4. 确认无残留 HTML 标签（特殊标签 `<code>`、`<strong>` 等除外）

## Fallback

| 失败场景 | 回退方案 |
|---------|---------|
| HTML 解析失败 | 降级使用 `browser-use_browser_extract_content` 作为替代 |
| 浏览器导航失败 | 提供手动保存指引（Ctrl+S / 打印为 PDF）|
| 文件写入失败 | 请用户确认输出目录有效性 |
| 内容仍不完整 | 在文档中标注「内容可能不完整，建议手动补充」|

## Examples

### 触发示例

- `把这个页面提取为 Markdown：https://example.com/article`
- `提取这个动态加载页面的内容并保存`
- `把这个 JS 渲染的网页抓取为 markdown 格式`

### 端到端示例

用户：`把 https://github.com/JasonCai2024/skill-dynamic-page-to-markdown 的内容保存为 markdown`

执行流程：
1. `browser_navigate` 打开目标页面
2. 截图确认加载成功
3. 滚动加载全部内容（README、代码块等）
4. `browser_get_html` 获取完整 DOM
5. 解析 HTML → 识别 `<main>` 主内容区
6. 清理 `<script>`/`<style>`，保留标题层级和代码块
7. 转换为 Markdown 并按模板格式化
8. 写入 `skill-dynamic-page-to-markdown.md`

## Reference

详细工具说明与配置方法见 `references/`：

| 文件 | 内容 |
|------|------|
| `references/browser-use-mcp.md` | browser-use MCP 工具完整列表、参数说明、常见问题 |
| `references/markdown-template.md` | 输出 Markdown 模板、格式规范、标题层级映射表 |
