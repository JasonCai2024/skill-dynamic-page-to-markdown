---
name: dynamic-page-to-markdown
description: Extracts content from dynamically rendered web pages and saves as Markdown. Use when user provides a webpage URL with JavaScript-rendered content that cannot be extracted via simple HTTP fetch. Triggers on: save webpage content, extract dynamic page, scrape JS-rendered page.
disable-model-invocation: true
user-invocable: true
argument-hint: [webpage-url]
---

# Dynamic Page to Markdown

## Goal

Extract content from dynamically rendered web pages (JavaScript-rendered pages) and save as formatted Markdown documents.

## Required Inputs

- Webpage URL with JS-rendered content
- Output file path (optional)
- Page title or description (optional)

## Workflow

1. **Navigate to target page**

   Use `browser-use_browser_navigate` to open the webpage URL.

2. **Verify page load**

   Use `browser-use_browser_get_state` with `include_screenshot: true`.

3. **Scroll to load all content**

   Use `browser-use_browser_scroll` to load lazy-loaded content. Repeat until all content is visible.

4. **Extract raw HTML**

   Use `browser-use_browser_get_html` to get the full page HTML. Do NOT use `browser-use_browser_extract_content` for dynamically rendered pages.

5. **Analyze HTML structure**

   Identify content containers from the HTML:
   - Primary content: usually in `<main>`, `<article>`, or specific containers
   - Text blocks: `<p>`, `<div>` with text content
   - Lists: `<ul>`, `<ol>` with `<li>` items
   - Preserve heading hierarchy (`<h1>` to `<h6>`)

6. **Parse and clean content**

   - Remove script and style tags
   - Preserve meaningful HTML structure
   - Convert to Markdown formatting

7. **Format as Markdown document**

   Apply this template:

   ```markdown
   # [Page Title]

   > 来源： [URL]
   > 日期： YYYY年MM月DD日

   ---

   [Content with proper heading hierarchy]

   ---

   *内容由 AI 提取，不能完全保障原始内容的完全准确性*
   ```

8. **Save document**

   Use `write` tool with UTF-8 encoding.

## Decision Rules

- If page fails to load, retry navigation up to 2 times.
- If content is truncated, scroll down and re-fetch HTML.
- If title cannot be determined, use filename or URL path as fallback.
- Preserve semantic structure: headings, lists, blockquotes, code blocks.
- For chat/conversation pages: pair user and AI messages with proper attribution.

## Output Requirements

Return:

1. Full path of saved Markdown file
2. Content structure summary (headings count, approximate length)
3. Confirmation of save success or error details

## Validation

- Verify file was written successfully
- Confirm Markdown contains meaningful content (not empty)
- Ensure proper heading hierarchy is preserved

## Fallback

- If HTML parsing fails, try `browser-use_browser_extract_content` as alternative
- If browser navigation fails, provide manual save instructions
- If write fails, ask user for valid output directory

## Examples

- `Extract this page to Markdown: https://example.com/article`
- `Save the content from this dynamically loaded page`
- `Scrape this JS-rendered webpage and save as markdown`