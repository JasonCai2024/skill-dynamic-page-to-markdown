# browser-use MCP 工具说明

在本技能中，优先使用以下调用顺序：

1. `browser-use_browser_navigate`
2. `browser-use_browser_get_state`
3. `browser-use_browser_scroll`
4. `browser-use_browser_get_html`

## 核心工具

### `browser-use_browser_navigate`

打开指定 URL。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `url` | string | 是 | 目标网页 URL |
| `new_tab` | bool | 否 | 是否在新标签页打开 |

### `browser-use_browser_get_state`

获取浏览器当前状态。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `include_screenshot` | bool | 否 | 是否返回截图，默认 false |

### `browser-use_browser_scroll`

滚动页面以加载懒加载内容。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `direction` | string | 否 | `down` 或 `up` |

### `browser-use_browser_get_html`

获取页面完整 DOM HTML（**推荐用于 JS 渲染页面**）。

可选参数：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `selector` | string | 否 | 只获取指定元素的 HTML |

本技能不设计跨工具降级路径，也不要求使用其他提取工具。

## 常见问题

**Q: 页面无限滚动怎么办？**
A: 滚动至底部后等待 2 秒，若出现新内容则继续滚动，直到连续两次滚动后新增内容不变。

**Q: `SessionManager not initialized` 是什么问题？**
A: 这是 browser-use MCP 的运行环境或会话初始化问题，不是本技能的内容转换逻辑问题。应先修复 browser-use 会话，再重新执行技能。

**Q: 如何确认页面完全加载？**
A: 使用 `browser-use_browser_get_state` 截图，并在滚动后再次确认正文区域、代码块和懒加载内容是否都已出现。
