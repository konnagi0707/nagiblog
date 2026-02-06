# Spec Workflow 使用说明（中文）

本项目采用 `spec-workflow-mcp` 的标准流程：

```text
指导（Steering） -> 规格（Requirements/Design/Tasks） -> 实现（Implementation） -> 验证（Validation）
```

## 1. 指导文档（已初始化）

路径：`.spec-workflow/steering/`

- `product.md`：产品目标、用户、成功指标
- `tech.md`：技术选型、架构和约束
- `structure.md`：代码结构与命名规范

## 2. 规格文档（示例已初始化）

路径：`.spec-workflow/specs/archive-search-experience/`

- `requirements.md`：定义“做什么”
- `design.md`：定义“怎么做”
- `tasks.md`：定义“怎么分步做”

## 3. 运行方式（按官方文档）

1. 启动 Dashboard（终端 A）：

```bash
npx -y @pimzino/spec-workflow-mcp@latest --dashboard
```

2. 启动当前项目的 MCP 服务（终端 B）：

```bash
npx -y @pimzino/spec-workflow-mcp@latest /Users/yanq1201/Documents/nagiblog
```

3. 在 AI 对话中使用中文提示词：

```text
请先读取 steering 文档，然后为 archive-search-experience 规格实现任务 1.1
```

## 4. 推荐工作节奏

1. 先完善 `steering/*.md`
2. 每个功能严格按 `requirements -> design -> tasks` 顺序
3. 每次只实现 1 个或 1 组相关任务
4. 实现后做最小可验证检查（功能 + 基本回归）
5. 如需求变更，先更新 `requirements/design` 再刷新 `tasks`
