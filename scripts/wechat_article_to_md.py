#!/usr/bin/env python3
"""
微信公众号文章抓取并转换为 Markdown 文档
"""

import re
import sys
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"缺少依赖库: {e}")
    print("请运行: pip install requests beautifulsoup4")
    sys.exit(1)


def sanitize_filename(name):
    """清理文件名中的非法字符"""
    # 替换 Windows/macOS/Linux 非法字符
    illegal_chars = r'[<>:"/\\|?*]'
    name = re.sub(illegal_chars, '_', name)
    # 去除首尾空格和点
    name = name.strip('. ')
    return name or 'article'


def clear_images_directory(img_dir):
    """清理图片目录中的所有图片文件"""
    if not img_dir or not img_dir.exists():
        return
    try:
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp', '*.bmp']:
            image_files.extend(img_dir.glob(ext))
        for file_path in image_files:
            file_path.unlink()
        if image_files:
            print(f"  已清理 {len(image_files)} 个旧图片文件")
    except Exception as e:
        print(f"  清理图片目录失败: {e}")


def download_image(url, img_dir, index, article_id=None):
    """下载图片到本地

    Args:
        url: 图片 URL
        img_dir: 图片保存目录
        index: 图片序号
        article_id: 文章唯一标识，用于生成唯一文件名
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # 从 URL 中提取文件扩展名
        ext = Path(url).suffix or '.png'
        # 如果 URL 中有参数，提取文件扩展名
        if '?' in ext:
            ext = ext.split('?')[0]
        if not ext or ext == '':
            ext = '.png'

        # 确保扩展名有效
        valid_exts = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
        if ext.lower() not in valid_exts:
            ext = '.png'

        # 使用文章 ID 作为前缀，避免不同文章的图片文件名冲突
        if article_id:
            filename = f"{article_id}_{index:03d}{ext}"
        else:
            filename = f"image_{index:03d}{ext}"
        file_path = img_dir / filename

        file_path.write_bytes(response.content)
        print(f"  下载图片: {filename}")
        return filename
    except Exception as e:
        print(f"  下载图片失败 ({url}): {e}")
        return None


def html_to_markdown(soup, img_dir=None, article_id=None, obsidian_mode=False, article_url=None):
    """将 HTML 内容转换为 Markdown，保持原始元素顺序

    Args:
        soup: BeautifulSoup 对象
        img_dir: 图片保存目录
        article_id: 文章唯一标识，用于生成唯一图片文件名
        obsidian_mode: 是否使用 Obsidian 格式（图片保存到 attachments/img/，使用 ![[filename]]）
        article_url: 原文链接，用于视频提示
    """
    md_content = []
    img_index = 0
    img_map = {}  # URL -> 本地文件名映射
    video_index = 0  # 视频计数器

    # 首先收集所有图片并下载
    if img_dir:
        for img in soup.find_all('img'):
            src = img.get('data-src') or img.get('src', '')
            if src and src not in img_map:
                img_index += 1
                local_img = download_image(src, img_dir, img_index, article_id)
                if local_img:
                    if obsidian_mode:
                        # Obsidian 格式：只需要文件名，不需要路径前缀
                        img_map[src] = local_img
                    else:
                        img_map[src] = f"images/{local_img}"

    def process_inline_elements(element):
        """处理元素内的内联元素（粗体、斜体、链接、图片）"""
        parts = []
        for child in element.children:
            if hasattr(child, 'name') and child.name:
                tag_name = child.name

                # 粗体
                if tag_name in ['b', 'strong']:
                    text = child.get_text(strip=True)
                    if text:
                        parts.append(f"**{text}**")

                # 斜体
                elif tag_name in ['i', 'em']:
                    text = child.get_text(strip=True)
                    if text:
                        parts.append(f"*{text}*")

                # 链接
                elif tag_name == 'a':
                    href = child.get('href', '')
                    text = child.get_text(strip=True)
                    if text:
                        parts.append(f"[{text}]({href})")

                # 图片
                elif tag_name == 'img':
                    src = child.get('data-src') or child.get('src', '')
                    alt = child.get('alt', '')
                    if src:
                        if src in img_map:
                            if obsidian_mode:
                                parts.append(f"![[{img_map[src]}]]")
                            else:
                                parts.append(f"![{alt}]({img_map[src]})")
                        else:
                            parts.append(f"![{alt}]({src})")

                # 递归处理其他嵌套元素
                else:
                    result = process_inline_elements(child)
                    if result:
                        parts.append(result)
            else:
                # 文本节点
                text = str(child).strip()
                if text:
                    parts.append(text)

        return ''.join(parts)

    def process_element(element, depth=0):
        """处理单个元素"""
        tag_name = element.name

        # 图片 - 最高优先级
        if tag_name == 'img':
            src = element.get('data-src') or element.get('src', '')
            alt = element.get('alt', '')
            if src:
                if src in img_map:
                    if obsidian_mode:
                        md_content.append(f"![[{img_map[src]}]]\n")
                    else:
                        md_content.append(f"![{alt}]({img_map[src]})\n")
                else:
                    md_content.append(f"![{alt}]({src})\n")
            return

        # 视频 iframe
        if tag_name == 'iframe':
            video_index += 1
            md_content.append(f"\n> 🎥 [视频 {video_index}]\n")
            md_content.append("> 注：微信视频无法在 Markdown 中直接查看\n")
            if article_url:
                md_content.append(f"> 请访问原文观看: {article_url}\n")
            md_content.append("\n")
            return

        # 标题
        if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(tag_name[1])
            text = element.get_text(strip=True)
            if text:
                md_content.append(f"\n{'#' * level} {text}\n\n")
            return

        # 段落
        if tag_name == 'p':
            content = process_inline_elements(element)
            if content:
                md_content.append(f"{content}\n\n")
            return

        # section 标签 - 微信公众号常用
        if tag_name == 'section':
            # 检查是否有直接文本内容
            direct_text = ''
            for child in element.children:
                if not hasattr(child, 'name') or child.name is None:
                    text = str(child).strip()
                    if text:
                        direct_text += text

            if direct_text:
                md_content.append(f"{direct_text}\n\n")
            else:
                # 递归处理 section 内的子元素
                for child in element.children:
                    if hasattr(child, 'name') and child.name:
                        # 避免重复处理已在父级处理的元素
                        if child.name not in ['section']:
                            process_element(child, depth + 1)
            return

        # 无序列表
        if tag_name == 'ul':
            for li in element.find_all('li', recursive=False):
                text = li.get_text(strip=True)
                if text:
                    md_content.append(f"- {text}\n")
            md_content.append("\n")
            return

        # 有序列表
        if tag_name == 'ol':
            for i, li in enumerate(element.find_all('li', recursive=False), 1):
                text = li.get_text(strip=True)
                if text:
                    md_content.append(f"{i}. {text}\n")
            md_content.append("\n")
            return

        # 引用
        if tag_name == 'blockquote':
            text = element.get_text(strip=True)
            if text:
                md_content.append(f"\n> {text}\n\n")
            return

        # 代码块
        if tag_name == 'pre':
            code = element.get_text()
            if code:
                md_content.append(f"\n```\n{code}\n```\n\n")
            return

        # 分隔线
        if tag_name == 'hr':
            md_content.append("\n---\n\n")
            return

        # div/span - 递归处理内容
        if tag_name in ['div', 'span']:
            content = process_inline_elements(element)
            if content and depth == 0:
                # 只在最顶层添加换行
                md_content.append(f"{content}\n\n")
            elif content:
                md_content.append(content)
            return

        # br 标签
        if tag_name == 'br':
            md_content.append("\n")
            return

        # 其他容器元素 - 递归处理
        if tag_name in ['article', 'main', 'figure', 'figcaption']:
            for child in element.children:
                if hasattr(child, 'name') and child.name:
                    process_element(child, depth + 1)
            return

    # 遍历所有直接子元素
    for child in soup.children:
        if hasattr(child, 'name') and child.name:
            process_element(child)

    # 如果没有内容，尝试直接处理所有文本和图片
    if not md_content:
        for element in soup.descendants:
            if hasattr(element, 'name'):
                if element.name == 'img':
                    src = element.get('data-src') or element.get('src', '')
                    alt = element.get('alt', '')
                    if src:
                        if src in img_map:
                            if obsidian_mode:
                                md_content.append(f"![[{img_map[src]}]]\n")
                            else:
                                md_content.append(f"![{alt}]({img_map[src]})\n")
                        else:
                            md_content.append(f"![{alt}]({src})\n")
                elif element.name == 'p':
                    text = element.get_text(strip=True)
                    if text:
                        md_content.append(f"{text}\n\n")

    return '\n'.join(md_content)


def find_attachments_img_dir(start_path):
    """从起始路径向上查找固定的 attachments/img/ 目录

    Args:
        start_path: 开始查找的路径（通常是 md 文件所在目录或输出目录）

    Returns:
        找到的 attachments/img/ 目录路径，如果没找到则返回 None
    """
    path = Path(start_path).resolve()

    # 向上最多查找 3 层目录
    max_levels = 3
    for level in range(max_levels):
        attachments_dir = path / 'attachments'
        img_dir = attachments_dir / 'img'

        # 检查 attachments/img/ 是否存在，或者可以创建
        # 优先使用已存在的目录
        if img_dir.exists() and img_dir.is_dir():
            return img_dir

        # 检查 attachments/ 目录是否存在
        if attachments_dir.exists() and attachments_dir.is_dir():
            # 尝试创建 img 目录
            img_dir.mkdir(exist_ok=True)
            return img_dir

        # 如果这层不是 attachments/，继续向上查找
        if path.parent == path:  # 已到达根目录
            break
        path = path.parent

    # 如果没找到，尝试在 start_path 的父目录创建
    path = Path(start_path).resolve().parent
    for level in range(max_levels):
        attachments_dir = path / 'attachments'
        img_dir = attachments_dir / 'img'

        if attachments_dir.exists() or level == 0:  # 第一层直接尝试创建
            img_dir.mkdir(parents=True, exist_ok=True)
            return img_dir

        if path.parent == path:
            break
        path = path.parent

    # 最后尝试在 start_path 下方创建（降级方案）
    fallback_img_dir = Path(start_path).resolve() / 'attachments' / 'img'
    fallback_img_dir.mkdir(parents=True, exist_ok=True)
    print(f"  注意: 降级在 {start_path} 下创建图片目录")
    return fallback_img_dir


def fetch_wechat_article(url, output_dir='.', download_images=True, obsidian_mode=False, img_output_dir=None):
    """
    抓取微信公众号文章

    Args:
        url: 微信文章链接
        output_dir: 输出目录（Markdown 文件保存位置）
        download_images: 是否下载图片到本地
        obsidian_mode: 是否使用 Obsidian 格式（图片引用格式 ![[filename]]）
        img_output_dir: 图片保存目录（绝对路径，None 表示相对于 output_dir）
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }

    print(f"正在请求: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
    except Exception as e:
        print(f"请求失败: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # 获取标题
    title = soup.find('meta', property='og:title')
    if title:
        title = title.get('content', '无标题')
    else:
        title_elem = soup.find('h1', class_='rich_media_title')
        title = title_elem.get_text(strip=True) if title_elem else '无标题'

    print(f"标题: {title}")

    # 获取作者 - 优先从 js_author_name 获取
    author_elem = soup.find(id='js_author_name')
    author = author_elem.get_text(strip=True) if author_elem else None
    if not author:
        # 备用方式：从 rich_media_meta_link 获取
        author_elem = soup.find('a', class_='rich_media_meta_link')
        author = author_elem.get_text(strip=True) if author_elem else '未知作者'
    print(f"作者: {author}")

    # 获取正文内容
    content_div = soup.find('div', class_='rich_media_content') or soup.find('div', id='js_content')
    if not content_div:
        print("未找到文章内容")
        return

    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 创建图片目录
    img_dir = None
    article_id = None
    if download_images:
        if img_output_dir:
            # 使用指定的绝对路径作为图片目录
            img_dir = Path(img_output_dir)
            img_dir.mkdir(parents=True, exist_ok=True)
            print(f"创建图片目录: {img_dir.absolute()}/")
        elif obsidian_mode:
            # Obsidian 模式：向上查找固定的 attachments/img/ 目录
            img_dir = find_attachments_img_dir(output_dir)
            print(f"使用固定图片目录: {img_dir.relative_to(Path.cwd()) if img_dir.is_relative_to(Path.cwd()) else img_dir}/")
        else:
            # 普通模式：保存到 images/
            img_dir = output_path / 'images'
            img_dir.mkdir(exist_ok=True)
            print("创建图片目录: images/")
        # 使用清理后的标题作为文章唯一标识
        article_id = sanitize_filename(title)
        # 清理旧图片
        clear_images_directory(img_dir)

    # 构建 Markdown
    md_lines = []
    md_lines.append(f"# {title}\n")
    md_lines.append(f"**作者**: {author}\n")
    md_lines.append(f"**来源**: {url}\n")
    md_lines.append("---\n\n")

    # 转换正文
    body_md = html_to_markdown(content_div, img_dir, article_id, obsidian_mode, url)
    md_lines.append(body_md)

    md_content = '\n'.join(md_lines)

    # 保存文件
    filename = sanitize_filename(title) + '.md'
    file_path = output_path / filename

    file_path.write_text(md_content, encoding='utf-8')
    print(f"\n保存成功: {file_path.absolute()}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python wechat_article_to_md.py <微信文章URL> [输出目录] [选项]")
        print("选项:")
        print("  -obsidian     使用 Obsidian 格式（图片引用格式 ![[filename]]）")
        print("  -img-dir DIR  指定图片保存目录（绝对路径，优先于默认位置）")
        print("示例:")
        print("  python wechat_article_to_md.py https://mp.weixin.qq.com/s/B5hK8BywPla6LG3hVxHGqA")
        print("  python wechat_article_to_md.py https://mp.weixin.qq.com/s/B5hK8BywPla6LG3hVxHGqA . -obsidian")
        print("  python wechat_article_to_md.py https://mp.weixin.qq.com/s/B5hK8BywPla6LG3hVxHGqA . -obsidian -img-dir /attachments/img")
        sys.exit(1)

    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].upper().startswith('-') else '.'
    obsidian_mode = any(arg.upper() == '-OBSIDIAN' for arg in sys.argv)

    # 解析 -img-dir 参数
    img_output_dir = None
    for i, arg in enumerate(sys.argv):
        if arg.upper() == '-IMG-DIR' and i + 1 < len(sys.argv):
            img_output_dir = sys.argv[i + 1]
            break

    fetch_wechat_article(url, output_dir, True, obsidian_mode, img_output_dir)