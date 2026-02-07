# Tasks Document

- [x] 1. 调整移动端筛选按钮为右下角贴边 block
  - Files: `index.html`, `styles.css`, `app.js`
  - 将按钮由文字入口改为图标入口，位置固定到右下角贴边。
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 2. 清理抽屉顶部关闭栏并统一遮罩关闭行为
  - Files: `index.html`, `app.js`, `styles.css`
  - 删除冗余顶部关闭区域，保留遮罩点击关闭。
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 3. 将 Pages 发布链路恢复为“同步后发布 data/”
  - File: `.github/workflows/pages.yml`
  - 发布前执行抓取并将 `data/` 打包进 artifact。
  - _Requirements: 4.1, 4.2_

- [x] 4. 给 Pages 同步链路加回缓存恢复
  - File: `.github/workflows/pages.yml`
  - 使用 actions/cache 恢复 `posts/member/images` 缓存，加速增量同步。
  - _Requirements: 4.1, 5.1_

- [x] 5. 下调自动同步频率到每日
  - File: `.github/workflows/pages.yml`
  - 使用每日 cron，避免过高频抓取。
  - _Requirements: 3.1_

- [x] 6. 将独立同步流程改为手动触发
  - File: `.github/workflows/sync-archive.yml`
  - 去除 schedule，保留 workflow_dispatch。
  - _Requirements: 3.2, 3.3_

- [x] 7. 上线后验证数据可达性
  - Verification:
    - `https://konnagi0707.github.io/nagiblog/data/posts.json`
    - `https://konnagi0707.github.io/nagiblog/data/member.json`
  - 目标：均返回 HTTP 200。
  - _Requirements: 4.3, 5.2, 5.3_
