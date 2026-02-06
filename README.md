# Nagisa Blog Archive

一个面向 **小島凪紗公式ブログ** 的前端归档项目原型，当前支持：

- 统一时间线浏览
- 标签过滤
- 关键词搜索（标题 + 正文）
- 文章详情阅读
- 可分享直链（`#<postId>`）

## 本地预览

```bash
python3 -m http.server 8000
```

然后打开 `http://localhost:8000`。

## 目录结构

- `index.html`：页面结构
- `styles.css`：页面样式
- `app.js`：归档交互逻辑（加载、过滤、渲染、hash 路由）
- `data/posts.json`：示例数据
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

## 手动回归清单

1. 启动页面后，左侧显示时间线，右侧默认显示最新文章详情。
2. 标签选择 `季节` 后，仅保留 1 篇文章，标题为 `夏に向けて`。
3. 标签切回 `全部`，关键词输入 `最近` 后，仅保留标题 `最近のこと`。
4. 同时设置 `标签=日常` 与关键词 `第二篇`，结果仍应命中 `最近のこと`。
5. 打开 `http://localhost:8000/#0`，应直接展示 `初めまして、小島凪紗です`。
6. 打开 `http://localhost:8000/#999`，应自动回退到可见列表第一篇并修正 hash。
7. 手动把 `data/posts.json` 改名后刷新页面，应显示“数据加载失败”。

## 下一步建议

1. 对接真实博客数据源（手动抓取、RSS、API 或爬虫导出 JSON）。
2. 按 `.spec-workflow/specs/archive-search-experience/tasks.md` 继续迭代任务。
3. 增加自动化测试（过滤函数 + hash 行为 + 异常状态）。
