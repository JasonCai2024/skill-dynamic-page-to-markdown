# 安装指南

## 前置依赖

- **Python 3.8+**（用于运行 `scripts/html_to_markdown.py`）
- **browser-use MCP** 已配置并运行（端口 9222，驱动 Edge 浏览器）
- Mavis 或 Claude Code 运行环境

## 安装步骤

### 方式一：直接安装到 Mavis

```powershell
mavis skill install https://github.com/JasonCai2024/skill-dynamic-page-to-markdown.git
```

### 方式二：克隆到本地

```bash
git clone https://github.com/JasonCai2024/skill-dynamic-page-to-markdown.git
```

然后将目录路径添加到 Mavis 技能扫描路径：

```powershell
mavis skill install "E:\BaiduSyncdisk\WorkSpace\ForAgent\SKILLS-编程开发\skill-dynamic-page-to-markdown"
```

### 方式三：通过 Claude Code 使用

将本目录放入 Claude Code 的 skills 扫描路径，技能将自动识别。

## 启动浏览器自动化

在使用本技能前，确保 browser-use MCP 已启动：

```powershell
powershell -File C:\Users\pc\.mavis\bin\start-edge-cdp.ps1
```

## 验证安装

安装后，可在 Mavis 中运行：

```
/skill skill-dynamic-page-to-markdown
```

或直接触发：

```
把这个页面提取为 Markdown：https://example.com/article
```
