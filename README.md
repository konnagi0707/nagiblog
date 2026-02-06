# Nagisa Blog Archive

一个面向 **小島凪紗公式ブログ** 的前端归档项目，当前支持：

- 统一时间线浏览
- 标签过滤
- 关键词搜索（标题 + 正文）
- 文章详情阅读
- 可分享直链（`#<postId>`）

## 本地预览

```bash
cd "/Users/yanq1201/Documents/nagiblog"
python3 -m http.server 8000
```

然后打开 `http://localhost:8000`。

## 同步真实博客数据

已内置抓取脚本，可从櫻坂46官方站点抓取小島凪紗全部公开博客并写入 `data/posts.json`。

```bash
cd "/Users/yanq1201/Documents/nagiblog"
python3 scripts/fetch_nagisa_blog.py --output data/posts.json
```

当前数据规模：`93` 篇（最新抓取结果）。

## 目录结构

- `index.html`：页面结构
- `styles.css`：页面样式
- `app.js`：归档交互逻辑（加载、过滤、渲染、hash 路由）
- `data/posts.json`：真实博客数据
- `scripts/fetch_nagisa_blog.py`：抓取脚本
- `.spec-workflow/`：Spec Workflow 文档（中文）

## Spec Coding（按 spec-workflow-mcp）

本项目采用官方流程：

```text
指导 -> 规格 -> 实现 -> 验证
```

### 1. 指导文档

路径：`.spec-workflow/steering/`

- `product.md`
- `tech.md`
- `structure.md`

### 2. 首个功能规格（示例）

路径：`.spec-workflow/specs/archive-search-experience/`

- `requirements.md`
- `design.md`
- `tasks.md`

### 3. 启动 Dashboard 与 MCP

```bash
# 终端 A：启动 Dashboard
npx -y @pimzino/spec-workflow-mcp@latest --dashboard

# 终端 B：连接当前项目
npx -y @pimzino/spec-workflow-mcp@latest /Users/yanq1201/Documents/nagiblog
```

Dashboard 默认地址：`http://localhost:5000`

### 4. 推荐中文提示词

- `请根据 .spec-workflow/steering 文档，为 archive-search-experience 继续细化 requirements。`
- `请根据已批准的 requirements 生成 design 文档。`
- `请根据 design 生成 tasks，并按优先级从任务 1 开始实现。`

## 手动回归清单（真实数据）

1. 打开页面后，左侧列表文章数应在 `90+`，右侧默认显示最新文章详情。
2. 标签选择 `2026-01`，列表应至少有 1 篇，且可看到标题 `1月❄️`。
3. 标签切回 `全部`，关键词输入 `皆さん初めまして`，应能命中最早期自我介绍文章。
4. 打开 `http://localhost:8000/#52533`，应直达对应文章详情。
5. 打开 `http://localhost:8000/#9999999`，应自动回退到有效文章并修正 hash。
6. 临时将 `data/posts.json` 改名后刷新页面，应显示“数据加载失败”。
