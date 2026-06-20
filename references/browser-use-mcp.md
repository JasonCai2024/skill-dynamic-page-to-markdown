# browser-use MCP 使用约束

本技能把 `browser-use` 视为**动态页面提取主引擎**，而不是“打开网页后顺手抓一份 HTML”。

## 推荐调用顺序

1. `browser-use_browser_navigate`
2. `browser-use_browser_get_state`
3. `browser-use_browser_click` / `browser-use_browser_scroll`
4. `browser-use_browser_get_state`
5. `browser-use_browser_extract_content`
6. `browser-use_browser_get_html`

其中：

- `get_state` 用来确认页面当前到底渲染出了什么
- `click` / `scroll` 用来触发目录跳转、展开折叠、懒加载
- `extract_content` 用来提取当前运行态可见正文
- `get_html` 只做补充，不做唯一真源

## 核心原则

### 1. 不依赖初始 HTML 判断正文边界

很多动态页面的初始 HTML 只包含前半段内容，后半段由前端运行后再异步加载。

因此：

- 初始 HTML 里没有，不代表正文不存在
- 只有当运行态页面也确认不存在时，才能判断正文结束

### 2. 先驱动页面，再提取内容

如果页面存在以下元素，必须先交互再采集：

- 目录 / TOC
- “展开更多”
- 折叠块
- 标签页
- 无限滚动列表
- 懒加载图片区

### 3. `get_state` 是完整性校验器

每处理完一轮滚动或点击后，都要重新调用 `get_state`，确认：

- 新章节是否已出现
- 新图片是否已出现
- 代码块是否已出现
- 页面是否仍在加载更多内容

### 4. `extract_content` 是运行态提取器

当页面已经渲染完成后，应优先尝试对当前章节或当前视口正文使用 `extract_content`。

如果失败：

- 先继续驱动页面
- 再尝试局部提取
- 最后才使用 `get_html` 辅助人工整理

### 5. `get_html` 是补充工具

`get_html` 主要用于：

- 读取当前可见容器的 DOM
- 查找图片 `src`
- 保留代码块语言标记
- 补充链接 `href`

不应把整页 `get_html` 结果直接当成完整正文。

## 对话 / 聊天记录页的要求

若页面是 AI 对话、论坛楼层、评论串或问答页，必须把“消息节点”而不是“整页首段文本”作为提取单位。

执行要求：

1. 先确认当前 DOM 中是否存在重复消息容器
2. 先估算消息节点总数，再开始整理正文
3. 若存在“加载更多历史 / 展开全部 / 查看更多消息”，先点击再重新计数
4. 若 `extract_content` 返回空、只返回第一条，或明显少于消息节点总数，立即切换到 `get_html` 遍历消息节点
5. 不得因为“滚动后没有变化”就认定对话页提取完成；完成判定应以消息总数与输出条数是否一致为准

可优先关注的常见节点线索：

- `message-item`
- `chat-bubble`
- `conversation-item`
- `message-row`
- `send-msg-bubble`
- `receive-msg-bubble`
- `md-box-root`
- `user`
- `assistant`
- `bot`
- `question`
- `answer`

## 对目录型文档页的要求

若左侧或右侧存在目录：

1. 识别目录项数量
2. 逐项点击或滚动定位
3. 确认章节标题进入视口
4. 采集章节内容
5. 标记章节已完成

最终 Markdown 中的章节数，原则上应与目录中的正文章节数接近。

## 对图片的要求

图片处理必须遵循：

1. 先在运行态页面确认图片已可见
2. 再通过局部 DOM 查找其 `src`
3. 再下载到 `attachments/`
4. 再在 Markdown 原位置引用

禁止：

- 用其他章节的图片冒充当前章节图片
- 仅凭文件名猜测图片归属
- 截图里能看到图，就直接编造本地图片引用

### `blob:` 图片的特殊处理

有些站点会把已加载图片挂成浏览器内存中的 `blob:` URL，例如：

```text
blob:https://example.com/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

这表示：

- 图片在当前浏览器标签页里可见
- 但技能工具未必能直接拿到该图片的原始下载地址
- 也未必能直接读取该 `blob:` 的二进制内容

因此：

1. 如果 DOM 周边还能找到真实资源 URL、token、文件接口，再继续下载
2. 如果只能看到 `blob:` URL，则应停止伪自动化下载，并在正文原位置插入占位说明
3. 不得拿其他图片顶替

## 常见问题

**Q: 页面滚动到底后内容还不完整怎么办？**  
A: 先检查是否存在目录、展开按钮、分页或标签切换；很多页面不是“继续滚动”而是“必须点目录/展开”。

**Q: `browser-use_browser_extract_content` 抓不到内容怎么办？**  
A: 不要立即回退为“整页 HTML 抓取”。先让章节进入视口，再尝试局部提取；实在失败，再用 `get_html` 做辅助整理。

**Q: 对话页里 `extract_content` 只抓到第一条消息怎么办？**  
A: 这不应被视为提取完成。应立即统计 DOM 中消息节点总数，并改用 `get_html` 逐条遍历消息节点，按角色和顺序重建完整消息流。

**Q: `SessionManager not initialized` 是什么问题？**  
A: 这是 browser-use 运行环境故障，不是页面提取逻辑问题。必须先修复 browser-use 会话。

**Q: 为什么不能只靠 `get_html`？**  
A: 因为动态页面常见情况是“页面能看见，初始 HTML 没有”。技能目标就是解决这种问题，所以不能退化为 HTML 抓取器。

**Q: 页面会无预警跳回 `about:blank` 怎么办？**  
A: 这同样属于 browser-use 会话不稳定。应记录为运行环境异常，而不是把页面误判为正文为空或 DOM 丢失。
