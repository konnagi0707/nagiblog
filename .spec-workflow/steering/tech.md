# Technology Stack

## Project Type
静态前端单页应用（HTML + CSS + JavaScript），以本地 JSON 作为数据源。

## Core Technologies

### Primary Language(s)
- **Language**: JavaScript (ES6+), HTML5, CSS3
- **Runtime/Compiler**: 浏览器原生运行，无构建步骤
- **Language-specific tools**: `python3 -m http.server` 用于本地预览

### Key Dependencies/Libraries
- **原生 DOM API**：页面渲染与交互
- **Fetch API**：读取 `data/posts.json`

### Application Architecture
- 单页面、状态驱动渲染：
  - 数据加载
  - 过滤计算
  - 列表渲染
  - 详情渲染
  - hash 路由同步

### Data Storage
- **Primary storage**：`data/posts.json`
- **Caching**：当前不做持久缓存，仅内存态
- **Data formats**：JSON

### External Integrations
- **APIs**：当前无外部 API
- **Protocols**：HTTP（静态文件服务）
- **Authentication**：无

## Development Environment

### Build & Development Tools
- **Build System**：无
- **Package Management**：无
- **Development workflow**：修改文件后刷新页面验证

### Code Quality Tools
- **Static Analysis**：当前未启用（后续可加 ESLint）
- **Formatting**：当前未启用（后续可加 Prettier）
- **Testing Framework**：当前以手动回归为主（后续可引入 Vitest/Playwright）
- **Documentation**：Markdown 文档

### Version Control & Collaboration
- **VCS**：Git
- **Branching Strategy**：功能分支 + PR（建议）
- **Code Review Process**：以规格驱动审查为主

## Deployment & Distribution
- **Target Platform(s)**：现代浏览器
- **Distribution Method**：静态托管（可部署到 GitHub Pages 或其他静态托管）
- **Installation Requirements**：浏览器 + 本地静态服务
- **Update Mechanism**：代码更新后重新部署

## Technical Requirements & Constraints

### Performance Requirements
- 中小规模文章列表在普通笔记本浏览器中保持流畅滚动
- 标签切换和搜索响应应接近即时

### Compatibility Requirements
- **Platform Support**：Chrome / Safari / Edge 最新稳定版
- **Dependency Versions**：无第三方依赖

### Security & Compliance
- 外链统一 `target="_blank"` + `rel="noreferrer"`
- 避免直接注入不可信 HTML

### Scalability & Reliability
- 当前优先支持小到中等规模文章数据
- 后续若数据量增长，考虑分页或虚拟列表

## Technical Decisions & Rationale
1. **先保持原生技术栈**：降低复杂度，快速迭代 UI/交互。
2. **JSON 作为初始数据源**：便于快速验证归档体验。
3. **规格先行再改代码**：减少返工，提升可追溯性。

## Known Limitations
- 目前无自动化测试，回归成本较高。
- 数据更新流程仍偏手工，后续需自动化。
