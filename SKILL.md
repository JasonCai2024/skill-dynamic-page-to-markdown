---
name: skill-dynamic-page-to-markdown
description: 使用 browser-use MCP 驱动真实浏览器，对 JavaScript 动态渲染、懒加载、目录跳转、展开折叠后才出现正文的网页进行运行态采集，并整理为 Markdown 文档。适用于“简单 HTTP/初始 HTML 抓不到完整正文”的页面；尤其适用于文档站、知识库、对话页、富文本详情页。禁止回退到其他浏览器工具链。
disable-model-invocation: true
user-invocable: true
argument-hint: [webpage-url]
---

# Skill Dynamic Page to Markdown

## Goal

通过 `browser-use` 让页面真正完成渲染，再基于**运行态页面内容**而不是“初始 HTML 快照”提取正文、代码块、图片、链接和结构信息，最终保存为 Markdown。

这个技能的核心不是“抓 HTML”，而是：

1. 用 `browser-use` 触发页面真实加载
2. 用 `browser-use` 触发懒加载、目录跳转、展开折叠
3. 在运行后的页面状态中采集内容
4. 再将采集结果整理为 Markdown

## Required Inputs

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `url` | URL 字符串 | 是 | 目标动态网页地址 |
| `output_path` | 文件路径 | 否 | Markdown 输出路径 |
| `page_title` | 字符串 | 否 | 页面标题；未提供时从运行态页面标题推断 |
| `attachments_dir` | 文件路径 | 否 | 图片附件目录；默认使用 `output_path` 同级 `attachments/` |

## Non-Goals

- 不把“初始 HTML”当作内容真源
- 不依赖单次 `browser-use_browser_get_html` 结果判断页面是否完整
- 不切换到 Playwright、通用 browser、requests、curl 等其他浏览器/抓取工具链

## Workflow

### Step 1：打开页面

使用 `browser-use_browser_navigate` 打开目标 URL。

### Step 2：确认初始渲染

使用 `browser-use_browser_get_state(include_screenshot: true)` 确认页面已经可交互，并记录：

- 当前标题
- 当前可见正文区域
- 当前可见目录、导航、展开按钮、分页按钮
- 当前可见图片数量和位置

### Step 3：识别页面加载模式

基于运行态页面判断该页面属于哪一类：

- 普通长文正文页
- 左侧目录 / 锚点跳转页
- 折叠块 / 手风琴页
- 无限滚动 / 懒加载流式页面
- 对话 / 聊天记录页

若页面存在目录、折叠块、分页、标签页、展开按钮，应优先触发这些交互，而不是直接抓 HTML。

### Step 4：驱动页面加载完整内容

必须使用 `browser-use` 让正文真正出现在运行态页面里。

优先策略：

1. 若存在目录（TOC），逐项点击目录项，触发对应章节渲染
2. 若存在“展开更多 / 查看全部 / Read more / 展开”按钮，逐项点击
3. 若正文按滚动懒加载，重复 `browser-use_browser_scroll(direction: down)`
4. 若滚动到底后内容仍变化，继续滚动，直到连续两次采集结果无新增正文

### Step 5：以运行态内容为主进行采集

采集优先级如下：

1. `browser-use_browser_get_state`
   用于确认当前可见标题、段落、列表、按钮、链接、代码块、图片是否已实际出现
2. `browser-use_browser_extract_content`
   若对当前页面或当前章节可提取，则优先用它抽取结构化正文
3. `browser-use_browser_get_html`
   只作为**补充材料**使用，用于：
   - 补充当前可见容器的 DOM
   - 查找图片 `src`
   - 保留代码块、链接、局部语义结构

禁止将“抓到的初始完整 HTML”直接视为整页最终正文。

### Step 6：章节化采集

若页面存在目录或明显章节边界，应按章节处理：

1. 点击某个目录项或滚动到某章节
2. 使用 `browser-use_browser_get_state` 确认章节标题已可见
3. 采集该章节正文、列表、代码块、图片、链接
4. 记录该章节已采集
5. 继续处理下一章节

若页面目录里有 N 个章节，最终产出的 Markdown 至少应覆盖这些章节标题；若缺失，视为采集不完整。

### Step 7：图片处理

图片同样必须以**运行态页面**为准：

1. 先在运行态确认图片已真实出现
2. 再通过当前可见 DOM / HTML 补充图片源地址
3. 将图片保存到 `attachments/`
4. 在 Markdown 对应位置使用本地相对路径引用

如果图片在截图中可见，但运行态 DOM 中暂时拿不到稳定 `src`，不得伪造或错配图片；应在正文原位置插入占位说明，例如：

```markdown
[图片占位：该图片在运行态页面中可见，但未成功本地化]
```

特别注意以下动态图片场景：

- 若运行态图片 `src` 为 `blob:` URL，则说明资源已经进入浏览器内存，但不一定还能通过技能工具直接反查其原始下载地址
- 对这类图片，只有在当前运行态 DOM 明确暴露了可下载的真实 URL、token 或文件接口时，才允许落盘到 `attachments/`
- 若页面仅暴露 `blob:` URL，而工具链无法读取其二进制内容或反查原始地址，则该图片应在正文原位置保留占位说明，而不是继续尝试复杂下载

### Step 8：本地整理为 Markdown

运行态内容采集完成后，再使用仓库内脚本做**整理**而不是“盲目抽正文”：

```bash
python scripts/html_to_markdown.py --file <captured-fragment.html> --url "<url>" --title "<page_title>" --attachments-dir "<output_dir>/attachments" --image-path-prefix "attachments"
```

脚本在本技能中的定位：

- 可以把已确认的 HTML 片段整理成 Markdown
- 可以帮助下载已知图片 `src`
- 不能替代 `browser-use` 完成页面完整加载和章节发现

如果采集内容主要来自逐章节运行态观察，也可以直接手工整理 Markdown；不强制要求所有正文必须经过脚本。

### Step 9：按模板输出

```markdown
# [页面标题]

> 来源： [URL]
> 日期： YYYY年MM月DD日

---

[正文内容]

---

*内容由 AI 提取，不能完全保障原始内容的完全准确性*
```

### Step 10：保存文件

将 Markdown 以 UTF-8 写入 `output_path`。

若页面存在图片：

- 确保 `attachments/` 已创建
- 确保 Markdown 引用的是本地相对路径
- 确保没有把错误图片引用到错误章节

## Decision Rules

1. **完整性优先于自动化**
   如果“自动抓 HTML”与“运行态逐章节采集”冲突，优先后者。

2. **以运行态为准**
   页面截图、可见标题、可见正文、可见图片，优先级高于初始 HTML。

3. **目录数对正文数**
   若目录中存在多个章节，而 Markdown 中未覆盖，视为提取不完整。

4. **可见图片对落盘图片**
   若页面可见图片明显多于本地附件数，应在结果中说明缺口。

5. **不伪造图片**
   若图片源地址未拿到，不要复用或错配其他图片；改为在原位置插入图片占位说明。

6. **browser-use 会话异常即停止**
   若出现 `SessionManager not initialized`、会话丢失、浏览器未连接等错误，应报告环境故障，而不是改走其他工具链。

7. **无预警跳回 `about:blank` 视为会话异常**
   若页面在继续采集过程中无用户指令地跳回 `about:blank`、空标签页或丢失当前 DOM，上述情况同样视为 browser-use 会话不稳定，应记录为运行环境问题。

## Validation

1. 文件写入成功
2. Markdown 非空，且不是导航、页脚、菜单为主
3. 标题层级可读
4. 代码块正文未丢失
5. 若存在目录，目录章节基本都在正文中出现
6. 若原页面存在图片，`attachments/` 与 Markdown 图片引用一致
7. 未将无关图片错误引用到 FAQ、正文示意图等位置

## Fallback

| 失败场景 | 处理方式 |
|---------|---------|
| browser-use 会话异常 | 报告 browser-use 运行环境故障，停止执行 |
| 页面截图可见正文，但 `extract_content` 失败 | 改用逐章节 `get_state` + 局部 `get_html` 采集 |
| 初始 HTML 缺失后半段正文 | 继续点击目录、滚动、展开，不得直接认定页面正文结束 |
| 图片可见但拿不到稳定 `src` | 保留正文，并在原位置插入图片占位说明 |
| 图片只有 `blob:` URL | 视为运行态可见图片；若无法反查原始地址，则直接保留图片占位说明 |
| 输出仍不完整 | 在结果中明确标注“内容可能不完整”，说明缺失章节或图片范围 |

## Trigger Phrases

- `把这个动态网页保存成 Markdown`
- `提取这个 JS 渲染页面正文`
- `这个页面要等加载完才能抓，帮我转成 markdown`
- `把这个文档站页面完整保存为 Markdown`
- `提取这个飞书/知识库/文档页并导出 markdown`

## Reference

按需读取：

| 文件 | 用途 |
|------|------|
| `references/browser-use-mcp.md` | browser-use 工具的推荐调用顺序、运行态采集原则 |
| `references/markdown-template.md` | Markdown 模板、结构和校验规则 |
