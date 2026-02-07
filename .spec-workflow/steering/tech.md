# Technology Stack

## Project Type
静态前端站点（HTML/CSS/JavaScript）+ Python 抓取脚本 + GitHub Actions 自动化。

## Core Technologies

### Frontend
- HTML5 / CSS3 / JavaScript (ES6+)
- 原生 DOM + Fetch API
- 无构建步骤、无前端框架

### Data Sync
- Python 3.13
- 脚本：`scripts/fetch_nagisa_blog.py`
- 能力：
  - 增量抓取博客列表与详情
  - 下载正文图片到 `data/images/<post_id>/`
  - 抓取成员资料与成员图到 `data/member/`
  - 输出 `data/posts.json` 和 `data/member.json`

### Hosting / Automation
- GitHub Pages
- GitHub Actions:
  - `pages.yml`：push / 手动 / 每日定时触发，执行抓取 + 发布
  - `sync-archive.yml`：手动同步并可提交数据到仓库（维护用途）
- Actions 缓存：`data/posts.json`、`data/member.json`、`data/images`、`data/member`

## Runtime Data Model
- `data/posts.json`：文章数组（含 `contentBlocks`）
- `data/member.json`：成员资料与图片映射
- `data/images/`：文章图片本地化目录
- `data/member/`：成员图片本地化目录（含 `グリーティングカード` / `フォト`）

## Technical Constraints
1. 不引入重型前端框架，保持静态站点可维护性。
2. 抓取频率遵循低频策略（当前：每日 1 次）。
3. 发布产物必须包含 `data/`，避免线上 404。
4. 同步失败不能导致页面 JS 崩溃，需显示可理解错误文案。

## Reliability Notes
- 若缓存缺失，首次抓取耗时会明显上升。
- 若官方页面结构变更，抓取脚本可能退化，需要更新解析逻辑。
- 若 `data/*.json` 不在发布产物中，前端会显示“数据加载失败”。

## Security / Compliance
- 外链统一 `target="_blank" + rel="noreferrer"`
- 前端不直接注入不可信 HTML，文本与图片区块分离渲染
- 抓取频率和延迟参数（`--sleep` / `--image-sleep`）用于降低请求压力

## Local Development
- 预览：`python3 -m http.server 8000`
- 同步（增量）：
  - `python3 scripts/fetch_nagisa_blog.py --output data/posts.json --member-output data/member.json`

## Key Decisions (Current)
1. **发布时抓取 + 缓存恢复**：保证线上 `data/` 可用，避免 404。
2. **定时降频到每日**：避免高频抓取。
3. **手动同步独立工作流**：在需要落库时手动执行，不默认高频提交。
