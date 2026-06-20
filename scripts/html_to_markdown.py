# -*- coding: utf-8 -*-
"""
html_to_markdown.py

将已确认的 HTML 片段整理为 Markdown。

注意：
1. 本脚本不是动态页面完整性发现器。
2. 它不能替代 browser-use 去驱动懒加载、目录跳转、展开折叠。
3. 在本技能中，它的职责是“整理已采集内容”，不是“证明页面内容已经采集完整”。

Usage:
    python html_to_markdown.py --html "<html>...</html>" --url "https://example.com"
    python html_to_markdown.py --file input.html --url "https://example.com"
"""

import argparse
import hashlib
import mimetypes
import re
import sys
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import Request, urlopen


class HTMLToMarkdownConverter(HTMLParser):
    def __init__(self, page_url: str = '', attachments_dir: str = '', image_path_prefix: str = 'attachments'):
        super().__init__()
        self.result = []
        self.tag_stack = []
        self.in_pre = False
        self.pre_content = []
        self.pre_lang = ''
        self.skip_depth = 0
        self.list_stack = []
        self.skip_tags = {'head', 'script', 'style', 'title'}
        self.block_tags = {
            'article', 'aside', 'blockquote', 'br', 'div', 'footer', 'h1', 'h2', 'h3',
            'h4', 'h5', 'h6', 'header', 'hr', 'li', 'main', 'nav', 'ol', 'p', 'pre',
            'section', 'table', 'tr', 'ul'
        }
        self.page_url = page_url
        self.attachments_dir = Path(attachments_dir) if attachments_dir else None
        self.image_path_prefix = image_path_prefix.replace('\\', '/').rstrip('/') or 'attachments'
        self.image_map = {}
        self.image_counter = 0

    def append_text(self, text):
        if not text:
            return
        if self.result and not self.result[-1].endswith(('\n', ' ', '(', '[', '> ', '*', '`')):
            self.result.append(' ')
        self.result.append(text)

    def append_block_break(self, count=2):
        if not self.result:
            return
        existing = len(self.result[-1]) - len(self.result[-1].rstrip('\n'))
        needed = max(count - existing, 0)
        if needed:
            self.result.append('\n' * needed)

    def resolve_image_src(self, src: str) -> str:
        if src.startswith('//'):
            scheme = urlparse(self.page_url).scheme or 'https'
            return f'{scheme}:{src}'
        return urljoin(self.page_url, src) if self.page_url else src

    def guess_extension(self, resolved_src: str, content_type: str = '') -> str:
        path = urlparse(resolved_src).path
        suffix = Path(unquote(path)).suffix
        if suffix:
            return suffix.lower()
        if content_type:
            ext = mimetypes.guess_extension(content_type.split(';', 1)[0].strip())
            if ext:
                return ext
        return '.bin'

    def download_image(self, src: str, alt: str) -> str:
        resolved_src = self.resolve_image_src(src)
        if not self.attachments_dir:
            return resolved_src
        if resolved_src in self.image_map:
            return self.image_map[resolved_src]

        self.attachments_dir.mkdir(parents=True, exist_ok=True)
        self.image_counter += 1
        digest = hashlib.sha1(resolved_src.encode('utf-8')).hexdigest()[:10]
        ext = self.guess_extension(resolved_src)
        filename = f'image-{self.image_counter:03d}-{digest}{ext}'
        local_path = self.attachments_dir / filename
        request = Request(
            resolved_src,
            headers={
                'User-Agent': 'Mozilla/5.0',
                'Referer': self.page_url or resolved_src,
            },
        )
        with urlopen(request, timeout=20) as response:
            content = response.read()
            content_type = response.headers.get('Content-Type', '')
        if not local_path.suffix or local_path.suffix == '.bin':
            better_ext = self.guess_extension(resolved_src, content_type)
            if better_ext != local_path.suffix:
                local_path = local_path.with_suffix(better_ext)
        local_path.write_bytes(content)
        relative_path = f'{self.image_path_prefix}/{local_path.name}'
        self.image_map[resolved_src] = relative_path
        return relative_path

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if self.skip_depth:
            if tag in self.skip_tags:
                self.skip_depth += 1
            return

        if tag == 'h1':
            self.append_block_break()
            self.result.append('# ')
        elif tag == 'h2':
            self.append_block_break()
            self.result.append('## ')
        elif tag == 'h3':
            self.append_block_break()
            self.result.append('### ')
        elif tag == 'h4':
            self.append_block_break()
            self.result.append('#### ')
        elif tag == 'h5':
            self.append_block_break()
            self.result.append('##### ')
        elif tag == 'h6':
            self.append_block_break()
            self.result.append('###### ')
        elif tag == 'p':
            self.append_block_break()
        elif tag == 'br':
            self.result.append('  \n')
        elif tag == 'strong' or tag == 'b':
            self.result.append('**')
        elif tag == 'em' or tag == 'i':
            self.result.append('*')
        elif tag == 'code':
            if not self.in_pre:
                self.result.append('`')
        elif tag == 'pre':
            self.in_pre = True
            self.pre_content = []
            self.pre_lang = ''
            if 'class' in attrs_dict:
                match = re.search(r'language-(\w+)', attrs_dict['class'])
                if match:
                    self.pre_lang = match.group(1)
            self.append_block_break()
        elif tag == 'a':
            href = attrs_dict.get('href', '#')
            self.result.append('[')
            self.tag_stack.append(('a', href))
        elif tag == 'blockquote':
            self.append_block_break()
            self.result.append('> ')
        elif tag == 'hr':
            self.append_block_break()
            self.result.append('---')
            self.append_block_break()
        elif tag == 'ul':
            self.list_stack.append({'type': 'ul', 'index': 0})
        elif tag == 'ol':
            self.list_stack.append({'type': 'ol', 'index': 0})
        elif tag == 'li':
            self.append_block_break(1)
            indent = '  ' * max(len(self.list_stack) - 1, 0)
            if self.list_stack:
                current = self.list_stack[-1]
                if current['type'] == 'ul':
                    self.result.append(f'{indent}- ')
                else:
                    current['index'] += 1
                    self.result.append(f"{indent}{current['index']}. ")
        elif tag in self.skip_tags:
            self.skip_depth = 1
        elif tag == 'img':
            src = attrs_dict.get('src', '')
            alt = attrs_dict.get('alt', 'image')
            if src:
                local_or_remote = self.download_image(src, alt)
                self.append_text(f'![{alt}]({local_or_remote})')
        elif tag in {'div', 'section', 'article', 'main'}:
            self.append_block_break()

    def handle_endtag(self, tag):
        if self.skip_depth:
            if tag in self.skip_tags:
                self.skip_depth -= 1
            return
        if tag == 'strong' or tag == 'b':
            self.result.append('**')
        elif tag == 'em' or tag == 'i':
            self.result.append('*')
        elif tag == 'code':
            if not self.in_pre:
                self.result.append('`')
        elif tag == 'pre':
            self.in_pre = False
            code = ''.join(self.pre_content).rstrip('\n')
            self.result.append(f"```{self.pre_lang}\n{code}\n```")
            self.pre_content = []
            self.pre_lang = ''
            self.append_block_break()
        elif tag == 'a':
            if self.tag_stack and self.tag_stack[-1][0] == 'a':
                _, href = self.tag_stack.pop()
                self.result.append(f']({href})')
        elif tag == 'ul' or tag == 'ol':
            if self.list_stack:
                self.list_stack.pop()
            self.append_block_break()
        elif tag in self.block_tags:
            self.append_block_break()

    def handle_data(self, data):
        if self.skip_depth:
            return
        data = data.replace('\ufeff', '')
        if self.in_pre:
            self.pre_content.append(data)
        else:
            normalized = re.sub(r'\s+', ' ', data)
            text = normalized.strip()
            if not text:
                return
            if normalized.startswith(' ') and self.result and not self.result[-1].endswith((' ', '\n')):
                self.result.append(' ')
            self.append_text(text)
            if normalized.endswith(' ') and not self.result[-1].endswith((' ', '\n')):
                self.result.append(' ')

    def get_markdown(self):
        result = ''.join(self.result)
        result = re.sub(r'\n{3,}', '\n\n', result)
        result = re.sub(r'[ \t]+\n', '\n', result)
        return result.strip()


def infer_title_from_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.rstrip('/')
    if path:
        return path.split('/')[-1] or parsed.netloc or 'untitled-page'
    return parsed.netloc or 'untitled-page'


def convert(
    html: str,
    url: str = '',
    page_title: str = '',
    attachments_dir: str = '',
    image_path_prefix: str = 'attachments',
) -> str:
    """将已采集的 HTML 片段转换为 Markdown 文档。"""
    converter = HTMLToMarkdownConverter(
        page_url=url,
        attachments_dir=attachments_dir,
        image_path_prefix=image_path_prefix,
    )
    try:
        converter.feed(html)
    except Exception as e:
        print(f"HTML 解析警告: {e}", file=sys.stderr)

    content = converter.get_markdown()
    date = datetime.now().strftime('%Y年%m月%d日')
    title = page_title.strip() or infer_title_from_url(url)

    lines = []
    lines.append(f'# {title}')
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
    parser.add_argument('--attachments-dir', type=str, default='', help='图片下载目录')
    parser.add_argument('--image-path-prefix', type=str, default='attachments', help='Markdown 中图片路径前缀')
    args = parser.parse_args()

    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            html = f.read()
    elif args.html:
        html = args.html
    else:
        print('请提供 --html 或 --file 参数', file=sys.stderr)
        sys.exit(1)

    md = convert(
        html,
        args.url,
        args.title,
        attachments_dir=args.attachments_dir,
        image_path_prefix=args.image_path_prefix,
    )
    print(md)
