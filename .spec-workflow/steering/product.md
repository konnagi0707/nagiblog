# Product Overview

## Product Purpose
为「小島凪紗公式博客」提供一个可持续维护的非官方归档前端，重点提升文章检索效率、阅读连续性和可分享性。

## Target Users
- 博客读者：希望快速查找某篇历史文章
- 内容整理者：希望按标签和时间批量浏览
- 分享者：希望通过直链快速定位某篇文章

## Key Features
1. **时间线浏览**：按时间倒序浏览所有文章。
2. **筛选与搜索**：支持标签过滤与关键词检索（标题/正文）。
3. **详情阅读**：查看正文摘要、标签、来源链接。
4. **直链访问**：通过 `#<postId>` 直接打开目标文章。

## Business Objectives
- 降低目标文章查找时间。
- 提高归档页面的可用性和稳定性。
- 形成可复用的 spec 驱动开发方式，便于后续迭代。

## Success Metrics
- 文章定位操作（筛选或搜索）可在 3 步内完成。
- 常见交互（切换标签、查看详情）无明显卡顿。
- 新功能上线前均有对应规格文档（requirements/design/tasks）。

## Product Principles
1. **可检索优先**：优先保证“找得到”。
2. **可读性优先**：阅读区信息层级清晰。
3. **可演进优先**：每次改动都可追溯到规格与任务。

## Monitoring & Visibility
- **Dashboard Type**：Spec Workflow Web Dashboard
- **Real-time Updates**：通过 MCP + Dashboard 观察任务状态
- **Key Metrics Displayed**：规格状态、任务进度、审批状态
- **Sharing Capabilities**：通过 Git 和文档协作共享进展

## Future Vision
### Potential Enhancements
- **Remote Access**：支持远程协作查看规格进度。
- **Analytics**：统计阅读热点标签和访问路径。
- **Collaboration**：多人协作审批和任务分配。
