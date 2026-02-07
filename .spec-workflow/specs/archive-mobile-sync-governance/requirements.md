# Requirements Document

## Introduction
本规格覆盖两类新增能力：
1. 移动端右下角筛选入口（贴边 block 形式）与抽屉交互规范
2. 归档数据自动同步与发布策略（低频、可恢复、可手动）

## Alignment with Product Vision
- 对齐“稳定优先、节制抓取、离线优先”原则
- 确保页面长期可用，不因数据缺失或高频抓取导致服务不稳定

## Requirements

### Requirement 1 - 移动端筛选入口贴边规范
**User Story:** 作为移动端读者，我希望筛选入口与官方风格一致并不遮挡正文，以便更自然地打开筛选抽屉。

#### Acceptance Criteria
1. WHEN 页面在移动端显示 THEN 系统 SHALL 将筛选入口固定在右下角贴边位置（`right: 0`）。
2. WHEN 用户点击筛选入口 THEN 系统 SHALL 打开左侧筛选抽屉。
3. WHEN 抽屉已打开 THEN 系统 SHALL 隐藏该入口，避免遮挡与误触。

### Requirement 2 - 抽屉关闭与交互一致性
**User Story:** 作为用户，我希望抽屉可通过点击遮罩直接关闭，不依赖额外顶部关闭栏。

#### Acceptance Criteria
1. WHEN 任意抽屉打开 THEN 系统 SHALL 显示遮罩层并锁定主页面滚动。
2. WHEN 用户点击遮罩 THEN 系统 SHALL 关闭抽屉。
3. THEN 抽屉顶部不再强制显示独立“关闭栏 + X”区域。

### Requirement 3 - 自动同步频率治理
**User Story:** 作为维护者，我希望自动同步频率可控，避免对官网造成过高抓取压力。

#### Acceptance Criteria
1. WHEN 定时同步启用 THEN 系统 SHALL 使用低频策略（当前：每日 1 次）。
2. IF 需要临时立即同步 THEN 系统 SHALL 提供手动触发入口（workflow_dispatch）。
3. THEN 不应存在默认高频（如每 2 小时）自动抓取任务。

### Requirement 4 - 发布链路数据可用性
**User Story:** 作为读者，我希望页面始终能加载数据，不出现长期“数据加载失败”。

#### Acceptance Criteria
1. WHEN GitHub Pages 发布执行 THEN 系统 SHALL 在发布前生成/恢复 `data/posts.json` 与 `data/member.json`。
2. THEN 发布产物 SHALL 包含 `data/` 目录。
3. IF `data/*.json` 缺失 THEN 该发布视为不可接受。

### Requirement 5 - 成员月度图更新覆盖
**User Story:** 作为读者，我希望成员侧栏中的 `グリーティングカード` 和 `フォト` 能随官网月度更新。

#### Acceptance Criteria
1. WHEN 同步任务执行 THEN 系统 SHALL 同步成员图片映射并下载本地化资源。
2. THEN 页面 SHALL 使用本地化后的成员图渲染。
3. IF 官网月度图变化 THEN 在后续同步窗口内 SHALL 反映到归档页。

## Non-Functional Requirements

### Reliability
- 发布后 `data/posts.json` 与 `data/member.json` 可直接访问（HTTP 200）。

### Performance
- 抽屉开关无明显卡顿，正文滚动流畅。

### Operational Safety
- 抓取脚本需保留请求间隔参数，避免过于激进请求。
