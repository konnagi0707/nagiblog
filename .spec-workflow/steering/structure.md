# Project Structure

## Directory Organization

```text
nagiblog/
├── index.html
├── styles.css
├── app.js
├── portrait.jpeg
├── portrait.png
├── scripts/
│   └── fetch_nagisa_blog.py
├── data/
│   ├── posts.json
│   ├── member.json
│   ├── images/
│   └── member/
├── .github/
│   └── workflows/
│       ├── pages.yml
│       └── sync-archive.yml
└── .spec-workflow/
    ├── README.zh-CN.md
    ├── steering/
    ├── templates/
    └── specs/
```

## Layering (Runtime)
1. **Data Fetch Layer**（`app.js`）
   - 读取 `data/posts.json` / `data/member.json`
2. **State & Filter Layer**（`app.js`）
   - 标签、关键词、activeId、hash 同步
3. **Presentation Layer**（`app.js` + `styles.css`）
   - 时间线、正文、成员侧栏、移动端抽屉
4. **Sync Layer**（`scripts/` + `workflows/`）
   - 增量抓取、图片本地化、Pages 发布

## Naming Conventions
- 规格目录：`kebab-case`（例如 `archive-mobile-sync-governance`）
- JS：`camelCase`
- 常量：`UPPER_SNAKE_CASE`
- workflow：语义化命名（`pages.yml`、`sync-archive.yml`）

## File Responsibility
- `index.html`：静态骨架和关键挂载点
- `styles.css`：布局、响应式、视觉样式
- `app.js`：状态、过滤、渲染、事件与 hash 路由
- `scripts/fetch_nagisa_blog.py`：抓取与本地化
- `.github/workflows/pages.yml`：发布时同步并部署
- `.github/workflows/sync-archive.yml`：手动同步并提交

## Operational Rules
1. 任何涉及同步策略的改动，必须同时更新：
   - `steering/tech.md`
   - 对应 spec 的 `requirements/design/tasks`
2. 任何移动端交互改动，必须在 spec 中记录：
   - 触发入口
   - 关闭行为
   - 遮罩层与层级规则
3. 发布链路改动后必须验证：
   - `https://konnagi0707.github.io/nagiblog/data/posts.json` 返回 200
   - `https://konnagi0707.github.io/nagiblog/data/member.json` 返回 200

## Documentation Standards
- 已完成任务使用 `[x]` 标记，并附 Requirements 编号。
- 每个规格必须体现“为何这么做（trade-off）”。
- 需求变更优先更新规格，再更新实现。
