# Dynamic Page to Markdown

把动态网页内容提取为 Markdown 的技能，但这里的“动态网页”指的是：

- 初始 HTML 不完整
- 需要目录跳转、展开折叠、滚动懒加载后正文才出现
- 必须依赖真实浏览器运行态才能看到完整内容

## 当前设计定位

这个技能现在明确是：

- `browser-use` 驱动真实浏览器
- 以运行态页面内容为提取主来源
- 以 `html_to_markdown.py` 作为整理器，而不是正文真源

它不再是“打开页面后抓一份 HTML 再转 Markdown”的技能。

## 文件结构

```text
skill-dynamic-page-to-markdown/
├─ SKILL.md
├─ README.md
├─ INSTALL.md
├─ .env.example
├─ .gitignore
├─ references/
│  ├─ browser-use-mcp.md
│  └─ markdown-template.md
└─ scripts/
   └─ html_to_markdown.py
```

## 核心原则

1. 页面完整性优先
2. 运行态内容优先于初始 HTML
3. Browser Use 是主提取引擎，不是辅助打开器
4. 图片宁可缺失，也不能错配
5. 不回退到其他浏览器工具链

## 脚本职责

`scripts/html_to_markdown.py` 的职责是：

- 整理已确认的 HTML 片段
- 下载已知图片 `src`
- 输出 Markdown

它**不负责**：

- 发现懒加载正文
- 驱动目录章节渲染
- 判断页面是否已经完整加载

这些工作必须由 `browser-use` 完成。

## 适用场景

- 飞书云文档
- 文档站 / 知识库
- 目录型详情页
- 展开后才显示全文的页面
- 需要滚动或点击才能加载完整内容的页面

## 不适用场景

- 只是普通静态 HTML 页面，直接抓源代码即可
- 明知需要其他网站 API 才能取回数据，但又禁止交互加载的页面

## 触发提示词

- `把这个动态网页保存成 Markdown`
- `提取这个 JS 渲染页面正文`
- `这个页面要加载完才能抓，帮我转成 markdown`
- `把这个文档页完整导出为 Markdown`

## 前置依赖

- 提供 `browser-use` MCP 的运行时
- Python 3.8+（用于运行整理脚本）

## 安全边界

- 不使用 Playwright 作为降级路径
- 不使用其他抓取工具链替代 `browser-use`
- 出现 `SessionManager not initialized` 等错误时，视为环境异常而不是页面内容异常
