# browser-use MCP 工具说明

## 工具列表

### browser_navigate

打开指定 URL。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `url` | string | 是 | 目标网页 URL |
| `timeout` | int | 否 | 超时毫秒数，默认 30000 |

### browser_get_state

获取浏览器当前状态。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `include_screenshot` | bool | 否 | 是否返回截图，默认 false |

### browser_scroll

滚动页面以加载懒加载内容。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `direction` | string | 否 | `down`（默认）或 `up` |
| `amount` | int | 否 | 每次滚动像素数，默认 500 |

### browser_get_html

获取页面完整 DOM HTML（**推荐用于 JS 渲染页面**）。

无参数，返回完整 HTML 字符串。

### browser_extract_content

提取页面主要内容（适用于静态页面，不推荐用于 JS 渲染页面）。

## 常见问题

**Q: 页面无限滚动怎么办？**
A: 滚动至底部后等待 2 秒，若出现新内容则继续滚动，直到连续两次滚动后新增内容不变。

**Q: 浏览器端口是多少？**
A: 默认端口 9222（Edge CDP），由 `start-edge-cdp.ps1` 启动。

**Q: 如何确认页面完全加载？**
A: 使用 `browser_get_state` 截图，查看主要内容是否全部可见。
