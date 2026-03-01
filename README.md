# 微信公众号文章转 Markdown

一个简单易用的 Python 脚本，用于抓取微信公众号文章并将其转换为 Markdown 文档，自动下载文章中的图片。

## ✨ 功能特性

- 📄 **自动提取**文章标题、作者、来源链接
- 🖼️ **自动下载**文章中的所有图片到本地
- 🔄 **完整转换**为 Markdown 格式（标题、列表、代码块、引用等）
- 🎥 **视频标记**自动标记微信视频位置（提示到原文观看）
- 📁 **灵活输出**支持普通模式和 Obsidian 模式
- 🛠️ **文件名清理**自动处理文件名中的非法字符

## 📦 安装

### 前置要求

- Python 3.6+
- pip

### 安装依赖

```bash
pip install requests beautifulsoup4
```

## 🚀 使用方法

### 普通模式

```bash
# 基本用法（自动下载图片到 images/ 目录）
python scripts/wechat_article_to_md.py https://mp.weixin.qq.com/s/xxxxxx

# 指定输出目录
python scripts/wechat_article_to_md.py https://mp.weixin.qq.com/s/xxxxxx ~/Documents
```

### Obsidian 模式

```bash
# 图片保存到 attachments/img/，使用 ![[filename]] 引用格式
python scripts/wechat_article_to_md.py https://mp.weixin.qq.com/s/xxxxxx . -obsidian
```

### 指定图片目录

```bash
# 指定图片保存的绝对路径
python scripts/wechat_article_to_md.py https://mp.weixin.qq.com/s/xxxxxx . -img-dir /path/to/images
```

## 📝 输出示例

```markdown
# 文章标题

**作者**: 公众号作者

**来源**: https://mp.weixin.qq.com/s/xxxxxx

---

文章正文内容...

![](images/图片文件名.png)

> 🎥 [视频 1]
> 注：微信视频无法在 Markdown 中直接查看
> 请访问原文观看: https://mp.weixin.qq.com/s/xxxxxx
```

## ⚠️ 注意事项

- 微信视频无法直接下载，脚本会在视频位置添加提示标记
- 图片下载可能受网络环境影响，超时时间设置为 30 秒
- 部分微信文章可能有访问限制

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！