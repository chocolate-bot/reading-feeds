# reading-feeds

一个专门用来存放 **OPML / RSS 订阅源清单** 的仓库（来源收集 + 个人整理 + 简单分类）。

## 目录结构

- `sources/`：原始来源（不做改动，便于追溯）
- `curated/`：整理后的版本（Markdown 便于浏览、筛选）
- `scripts/`：小工具脚本（解析/分类/导出）

## 如何使用

### 1) 导入到 RSS 阅读器
大多数阅读器支持导入 OPML：
- Reeder / NetNewsWire / Inoreader / Feedly 等

直接导入：
- `sources/hn-2025-popular-blogs.opml`

### 2) 先浏览再挑选
如果你不想一次性全订（容易信息过载），可以先看：
- `curated/hn-2025-categorized.md`

它是一个**自动分类视图**（启发式规则，不保证完美），方便你快速挑：AI/安全/系统/写作等。

## 当前收录

- HN 2025 Popular Blogs (OPML)
  - Source: https://gist.github.com/emschwartz/e6d2bf860ccc367fe37ff953ba6de66b
  - OPML: `sources/hn-2025-popular-blogs.opml`
  - Categorized view: `curated/hn-2025-categorized.md`
