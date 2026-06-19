# -*- coding: utf-8 -*-
"""
html_to_markdown.py

将 HTML 字符串转换为 Markdown 格式。

Usage:
    python html_to_markdown.py --html "<html>...</html>" --url "https://example.com"
    python html_to_markdown.py --file input.html --url "https://example.com"
"""

import argparse
import re
import sys
from datetime import datetime
from html.parser import HTMLParser


class HTMLToMarkdownConverter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []
        self.tag_stack = []
        self.in_pre = False
        self.pre_content = []
        self.in_list = False
        self.list_type = None

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag == 'h1':
            self.result.append('\n# ')
        elif tag == 'h2':
            self.result.append('\n## ')
        elif tag == 'h3':
            self.result.append('\n### ')
        elif tag == 'h4':
            self.result.append('\n#### ')
        elif tag == 'h5':
            self.result.append('\n##### ')
        elif tag == 'h6':
            self.result.append('\n###### ')
        elif tag == 'p':
            self.result.append('\n\n')
        elif tag == 'br':
            self.result.append('  \n')
        elif tag == 'strong' or tag == 'b':
            self.result.append('**')
        elif tag == 'em' or tag == 'i':
            self.result.append('*')
        elif tag == 'code':
            if self.in_pre:
                self.pre_content.append('<code>')
            else:
                self.result.append('`')
        elif tag == 'pre':
            self.in_pre = True
            lang = ''
            if 'class' in attrs_dict:
                match = re.search(r'language-(\w+)', attrs_dict['class'])
                if match:
                    lang = match.group(1)
            self.result.append(f'\n```{lang}\n')
        elif tag == 'a':
            href = attrs_dict.get('href', '#')
            self.result.append(f'[')
            self.tag_stack.append(('a', href))
        elif tag == 'blockquote':
            self.result.append('\n> ')
        elif tag == 'hr':
            self.result.append('\n---\n')
        elif tag == 'ul':
            self.in_list = True
            self.list_type = 'ul'
        elif tag == 'ol':
            self.in_list = True
            self.list_type = 'ol'
        elif tag == 'li':
            if self.list_type == 'ul':
                self.result.append('\n- ')
            elif self.list_type == 'ol':
                self.result.append('\n1. ')
        elif tag == 'script' or tag == 'style':
            pass  # skip
        elif tag == 'img':
            src = attrs_dict.get('src', '')
            alt = attrs_dict.get('alt', '')
            self.result.append(f'![{alt}]({src})')
        elif tag == 'div' or tag == 'span':
            pass  # inline containers, ignore

    def handle_endtag(self, tag):
        if tag == 'strong' or tag == 'b':
            self.result.append('**')
        elif tag == 'em' or tag == 'i':
            self.result.append('*')
        elif tag == 'code':
            if self.in_pre:
                self.pre_content.append('</code>')
            else:
                self.result.append('`')
        elif tag == 'pre':
            self.in_pre = False
            self.result.append('\n```\n')
        elif tag == 'a':
            if self.tag_stack and self.tag_stack[-1][0] == 'a':
                _, href = self.tag_stack.pop()
                self.result.append(f']({href})')
        elif tag == 'ul' or tag == 'ol':
            self.in_list = False
            self.list_type = None
        elif tag == 'h1':
            self.result.append('\n')
        elif tag == 'h2':
            self.result.append('\n')
        elif tag == 'h3':
            self.result.append('\n')
        elif tag == 'h4':
            self.result.append('\n')
        elif tag == 'h5':
            self.result.append('\n')
        elif tag == 'h6':
            self.result.append('\n')

    def handle_data(self, data):
        text = data.strip()
        if not text:
            return
        if self.in_pre:
            self.pre_content.append(text)
        else:
            # collapse whitespace
            text = re.sub(r'\s+', ' ', text)
            self.result.append(text)

    def get_markdown(self):
        result = ''.join(self.result)
        # cleanup extra newlines
        result = re.sub(r'\n{3,}', '\n\n', result)
        return result.strip()


def convert(html: str, url: str = '', page_title: str = '') -> str:
    """将 HTML 转换为 Markdown 文档。"""
    converter = HTMLToMarkdownConverter()
    try:
        converter.feed(html)
    except Exception as e:
        print(f"HTML 解析警告: {e}", file=sys.stderr)

    content = converter.get_markdown()
    date = datetime.now().strftime('%Y年%m月%d日')

    lines = []
    if page_title:
        lines.append(f'# {page_title}')
    lines.append(f'\n> 来源： {url}')
    lines.append(f'> 日期： {date}')
    lines.append('\n---')
    lines.append(f'\n{content}')
    lines.append('\n\n---')
    lines.append('\n*内容由 AI 提取，不能完全保障原始内容的完全准确性*')

    return '\n'.join(lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HTML to Markdown converter')
    parser.add_argument('--html', type=str, help='HTML 字符串')
    parser.add_argument('--file', type=str, help='HTML 文件路径')
    parser.add_argument('--url', type=str, default='', help='来源 URL')
    parser.add_argument('--title', type=str, default='', help='页面标题')
    args = parser.parse_args()

    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            html = f.read()
    elif args.html:
        html = args.html
    else:
        print('请提供 --html 或 --file 参数', file=sys.stderr)
        sys.exit(1)

    md = convert(html, args.url, args.title)
    print(md)
