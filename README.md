# 微信公众号文章转 Markdown

> **Claude Code Skill** - 抓取微信公众号文章并转换为 Markdown 文档，自动下载图片

一个专为 Claude Code 设计的技能，用于快速抓取微信公众号文章并将其转换为格式整洁的 Markdown 文档。支持自动下载图片、标记视频位置，**完美适配 Obsidian 等笔记工具**。

## ✨ 功能特性

- 📄 **自动提取**文章标题、作者、来源链接
- 🖼️ **自动下载**文章中的所有图片到本地
- 🔄 **完整转换**为 Markdown 格式（标题、列表、代码块、引用等）
- 🎥 **视频标记**自动标记微信视频位置（提示到原文观看）
- 📁 **灵活输出**支持普通模式和 Obsidian 模式
- 🛠️ **文件名清理**自动处理文件名中的非法字符
- 🤖 **Claude Code 集成**无缝集成 Claude Code 工作流
- 💎 **Obsidian 深度适配**专为 Obsidian 优化的图片引用格式

## 🚀 快速开始

### 安装依赖

```bash
pip install requests beautifulsoup4
```

### 使用方法

```bash
# 普通模式
python scripts/wechat_article_to_md.py https://mp.weixin.qq.com/s/xxxxxx

# Obsidian 模式（推荐）
python scripts/wechat_article_to_md.py https://mp.weixin.qq.com/s/xxxxxx . -obsidian

# 指定 Obsidian 的图片目录
python scripts/wechat_article_to_md.py https://mp.weixin.qq.com/s/xxxxxx . -obsidian -img-dir /path/to/obsidian/vault/attachments/img
```

## 💎 Obsidian 完美适配

### 为什么推荐 Obsidian 模式？

| 特性 | 普通模式 | Obsidian 模式 |
|-----|---------|--------------|
| 图片引用格式 | `![](images/filename.png)` | `![[filename.png]]` |
| 图片目录 | `images/` | `attachments/img/` |
| 通用性 | 通用 Markdown | Obsidian 专用 |
| 便携性 | 图片路径相对固定 | 自动查找 vault 目录 |

### Obsidian 使用场景

- 📚 将公众号文章收藏到知识库
- 🔍 支持 Obsidian 全文搜索和双向链接
- 📸 图片自动保存到 vault，离线可用
- 🔄 方便二次编辑和笔记整理

### Obsidian 快速上手

1. 创建一个 Obsidian vault
2. 将脚本输出到 vault 目录
3. 使用 `-obsidian` 参数运行，图片自动保存到 `attachments/img/`
4. 在 Obsidian 中打开生成的 .md 文件，图片正常显示

## 📖 详细文档

查看 [SKILL.md](./SKILL.md) 了解完整使用说明。

## 🤖 在 Claude Code 中使用

将此技能添加到 Claude Code 后，即可在对话中使用：

```
请帮我抓取 https://mp.weixin.qq.com/s/xxxxxx 这篇文章并转换为 Markdown（Obsidian 模式）
```

## ⚠️ 注意事项

- 微信视频无法直接下载，脚本会在视频位置添加提示标记
- 图片下载可能受网络环境影响
- 部分微信文章可能有访问限制

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 🔗 相关链接

- [Claude Code 官方文档](https://claude.ai/claude-code)
- [Obsidian 官网](https://obsidian.md)
- [微信公众号](https://mp.weixin.qq.com)