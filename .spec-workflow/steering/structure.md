# Project Structure

## Directory Organization

```text
nagiblog/
├── index.html
├── styles.css
├── app.js
├── data/
│   └── posts.json
└── .spec-workflow/
    ├── README.zh-CN.md
    ├── steering/
    │   ├── product.md
    │   ├── tech.md
    │   └── structure.md
    ├── templates/
    │   ├── requirements-template.md
    │   ├── design-template.md
    │   ├── tasks-template.md
    │   ├── product-template.md
    │   ├── tech-template.md
    │   └── structure-template.md
    └── specs/
        └── archive-search-experience/
            ├── requirements.md
            ├── design.md
            └── tasks.md
```

## Naming Conventions

### Files
- 功能规格名使用 `kebab-case`，例如：`archive-search-experience`
- 规格文档固定命名：`requirements.md`、`design.md`、`tasks.md`
- 页面资源文件保持语义化命名（如 `app.js`, `styles.css`）

### Code
- **Functions/Methods**：`camelCase`
- **Constants**：`UPPER_SNAKE_CASE`
- **Variables**：`camelCase`

## Import Patterns
- 当前为原生脚本，暂无模块化 import。
- 后续若拆分文件，优先按“数据/过滤/渲染/路由”分层。

## Code Structure Patterns
- 推荐顺序：状态定义 -> 纯函数 -> 渲染函数 -> 事件绑定 -> `init()`。
- 每个函数尽量单一职责，避免超长函数。

## Code Organization Principles
1. **单一职责**：数据处理与 UI 渲染分离。
2. **可测试**：过滤、排序等逻辑优先写成纯函数。
3. **一致性**：DOM 命名和 CSS 命名保持一致。
4. **渐进式演进**：优先小步提交，避免一次性大改。

## Module Boundaries
- **Data Layer**：读取/转换文章数据
- **Filter Layer**：标签与关键词过滤
- **Presentation Layer**：列表与详情渲染
- **Routing Layer**：hash 解析与同步

## Code Size Guidelines
- **File size**：建议单文件不超过 300 行（超过则拆分）
- **Function size**：建议单函数不超过 40 行
- **Nesting depth**：尽量不超过 3 层

## Documentation Standards
- 每个规格都要有可执行的任务列表。
- 任务必须标注 `_Requirements`，确保可追溯。
- 需求变化时，先更新规格，再更新实现。
