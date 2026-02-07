# Spec Workflow 使用说明（中文）

本项目采用 `spec-workflow-mcp` 的标准流程：

```text
指导（Steering） -> 规格（Requirements/Design/Tasks） -> 实现（Implementation） -> 验证（Validation）
```

## 1. 指导文档（Steering）

路径：`.spec-workflow/steering/`

- `product.md`：产品目标、运营策略、成功指标
- `tech.md`：技术栈、同步与发布链路、约束
- `structure.md`：目录结构、职责边界、文档更新规则

## 2. 规格文档（Specs）

路径：`.spec-workflow/specs/`

当前已维护：

1. `archive-search-experience/`
   - 关键词搜索、标签过滤、hash 直链的基础体验规格
2. `archive-mobile-sync-governance/`
   - 移动端抽屉与右下角入口
   - 自动同步频率治理
   - Pages 发布数据可用性

## 3. 与当前项目执行方式对齐

### 自动同步与发布
- `pages.yml`：
  - push / 手动 / 每日定时触发
  - 发布前执行增量同步并打包 `data/`
- `sync-archive.yml`：
  - 仅手动触发
  - 用于需要把数据提交回仓库时执行

### 关键验证项（每次发布后）
- `https://konnagi0707.github.io/nagiblog/data/posts.json` 返回 200
- `https://konnagi0707.github.io/nagiblog/data/member.json` 返回 200

## 4. 运行方式（Dashboard + MCP）

1. 启动 Dashboard（终端 A）

```bash
npx -y @pimzino/spec-workflow-mcp@latest --dashboard
```

2. 启动当前项目 MCP 服务（终端 B）

```bash
npx -y @pimzino/spec-workflow-mcp@latest /Users/yanq1201/Documents/nagiblog
```

3. 在 AI 对话中使用中文指令

```text
请先读取 steering 文档，然后按照 archive-mobile-sync-governance 的 tasks 执行。
```

## 5. 推荐工作节奏

1. 先更新 `steering/*.md`
2. 每个主题按 `requirements -> design -> tasks`
3. 每次只推进一组相关任务
4. 实现后执行最小可验证检查（功能 + 回归）
5. 需求变更时先改规格，再改代码
