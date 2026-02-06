# Nagisa Blog Archive

一个面向 **小島凪紗公式ブログ** 的前端归档项目，当前支持：

- 时间线浏览 + 标签过滤 + 关键词搜索
- 正文段落化渲染、图片自适应
- 文章直链（`#<postId>`）
- 右侧成员介绍卡（姓名、资料、主图、Greeting Card/Photo）
- 离线归档（`posts.json` + 本地图片 + `member.json`）

## 本地预览

```bash
cd "/Users/yanq1201/Documents/nagiblog"
python3 -m http.server 8000
```

打开：`http://localhost:8000`

## 数据同步（博客 + 成员）

抓取脚本会同步：

- `data/posts.json`
- `data/images/<post_id>/...`
- `data/member.json`
- `data/member/...`

### 首次全量

```bash
python3 scripts/fetch_nagisa_blog.py --full --output data/posts.json --member-output data/member.json
```

### 日常增量（推荐）

```bash
python3 scripts/fetch_nagisa_blog.py --output data/posts.json --member-output data/member.json
```

可选限速参数：

```bash
python3 scripts/fetch_nagisa_blog.py --output data/posts.json --member-output data/member.json --sleep 0.2 --image-sleep 0.05
```

## GitHub Pages（无需手动提交数据文件）

工作流：`/.github/workflows/pages.yml`

部署时会自动：

1. 恢复上次缓存的数据（`posts.json` / 图片 / `member.json`）
2. 执行增量抓取（官网有更新就同步）
3. 将生成后的 `data/` 打包进 Pages artifact

因此你**不需要每次把 `posts.json` 和图片手动 push 到仓库**。

> 仓库已在 `.gitignore` 忽略这些生成文件，避免仓库体积膨胀。

## 目录结构

- `/Users/yanq1201/Documents/nagiblog/index.html`：页面结构
- `/Users/yanq1201/Documents/nagiblog/styles.css`：样式
- `/Users/yanq1201/Documents/nagiblog/app.js`：交互逻辑
- `/Users/yanq1201/Documents/nagiblog/scripts/fetch_nagisa_blog.py`：抓取脚本
- `/Users/yanq1201/Documents/nagiblog/data/`：运行时生成数据

## Spec Coding（spec-workflow-mcp）

流程：`指导 -> 规格 -> 实现 -> 验证`

- 指导文档：`.spec-workflow/steering/`
- 模板：`.spec-workflow/templates/`

启动：

```bash
# 终端 A
npx -y @pimzino/spec-workflow-mcp@latest --dashboard

# 终端 B
npx -y @pimzino/spec-workflow-mcp@latest /Users/yanq1201/Documents/nagiblog
```

Dashboard：`http://localhost:5000`
