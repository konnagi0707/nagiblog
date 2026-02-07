# Design Document

## Overview
采用“UI 轻量改动 + 发布链路兜底”的方式：
- 前端：调整移动端筛选按钮定位与样式，继续使用遮罩关闭抽屉
- CI/CD：将数据同步并入 Pages 发布链路，配合缓存恢复与低频定时

## Steering Alignment

### With product.md
- 满足移动端可用性与稳定更新目标
- 降低人工维护与数据不可用风险

### With tech.md
- 不引入新框架；保持 HTML/CSS/JS + Python + GitHub Actions
- 通过 schedule + workflow_dispatch 满足低频自动 + 手动补偿

## Current vs Target

### Current (Before)
- 移动筛选按钮并非紧贴右下角
- 曾出现发布产物缺失 `data/` 导致前端 404
- 自动同步频率存在偏高风险

### Target (After)
- 筛选入口为右下角贴边 block（官网近似风格）
- Pages 发布前始终执行数据同步并打包 `data/`
- 自动同步降为每日 1 次，手动同步独立保留

## Architecture Changes

### Frontend
- 文件：`index.html`, `styles.css`, `app.js`
- 关键点：
  - `#open-filter-drawer` 采用图标形式
  - 移动端 `mobile-drawer-actions` 固定右下角贴边
  - 抽屉打开时隐藏浮动按钮

### Workflow
- 文件：`.github/workflows/pages.yml`
- 关键点：
  1. Checkout
  2. Setup Python
  3. Restore cache
  4. Sync archive data
  5. Build artifact with `data/`
  6. Deploy

- 文件：`.github/workflows/sync-archive.yml`
- 关键点：仅手动触发，作为维护/落库备用流程

## Trade-offs
1. **发布时同步**
   - 优点：保证线上数据可用
   - 代价：部署耗时增加
2. **低频定时**
   - 优点：降低官网请求压力
   - 代价：更新不是分钟级实时
3. **贴边按钮**
   - 优点：接近官方视觉，减少遮挡
   - 代价：在不同手机安全区需细调 `bottom` 值

## Validation Plan
1. 视觉验证（移动端）：右下角按钮贴边、抽屉可开关
2. 发布验证：Actions 成功
3. 数据可用性验证：
   - `/nagiblog/data/posts.json` -> 200
   - `/nagiblog/data/member.json` -> 200
4. 同步策略验证：
   - `pages.yml` 为每日 cron
   - `sync-archive.yml` 无 schedule，仅 workflow_dispatch
