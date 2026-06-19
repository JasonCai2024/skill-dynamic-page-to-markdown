# browser-use MCP 工具说明

在本技能中，优先使用以下调用顺序：

1. `browser_navigate`
2. `browser_get_state`
3. `browser_scroll`
4. `browser_get_html`
5. 仅在 DOM 提取失败时，回退 `browser_extract_content`

## 核心工具

### `browser_navigate`

打开指定 URL。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `url` | string | 是 | 目标网页 URL |
| `new_tab` | bool | 否 | 是否在新标签页打开 |

### `browser_get_state`

获取浏览器当前状态。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `include_screenshot` | bool | 否 | 是否返回截图，默认 false |

### `browser_scroll`

滚动页面以加载懒加载内容。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `direction` | string | 否 | `down` 或 `up` |

### `browser_get_html`

获取页面完整 DOM HTML（**推荐用于 JS 渲染页面**）。

可选参数：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `selector` | string | 否 | 只获取指定元素的 HTML |

### `browser_extract_content`

提取页面主要内容。适合作为回退，不应作为本技能默认主流程。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `query` | string | 是 | 希望抽取的内容说明 |
| `extract_links` | bool | 否 | 是否同时返回链接 |

## 常见问题

**Q: 页面无限滚动怎么办？**
A: 滚动至底部后等待 2 秒，若出现新内容则继续滚动，直到连续两次滚动后新增内容不变。

**Q: 为什么不直接用 `browser_extract_content`？**
A: 因为本技能的目标是提取 JS 渲染后的真实 DOM，`browser_extract_content` 更适合作为回退方案。

**Q: 如何确认页面完全加载？**
A: 使用 `browser_get_state` 截图，并在滚动后再次确认正文区域、代码块和懒加载内容是否都已出现。
