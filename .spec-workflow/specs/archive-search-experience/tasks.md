# Tasks Document

- [x] 1. 在页面中增加关键词输入区域
  - File: index.html
  - 在筛选区新增关键词输入框和占位符文案
  - 为输入框提供稳定的 `id`（如 `keyword-input`）
  - Purpose: 让用户可以输入关键词参与过滤
  - _Leverage: 现有 `#tag-select` 结构与侧栏布局_
  - _Requirements: 2.1, 2.2_
  - _Prompt: Role: Frontend Developer | Task: 在现有筛选区接入关键词输入控件并保持语义化结构 | Restrictions: 不破坏现有标签筛选交互与 DOM 结构 | Success: 页面出现可用的关键词输入框且无布局错乱_

- [x] 2. 扩展样式以支持搜索与状态提示
  - File: styles.css
  - 为关键词输入框定义与标签选择器一致的视觉风格
  - 为“加载失败/无匹配”状态定义可读样式
  - Purpose: 保证新增交互在桌面与移动端都可读
  - _Leverage: 现有 `.sidebar`、`.empty`、`#tag-select` 样式_
  - _Requirements: 6.1, 6.2_
  - _Prompt: Role: Frontend UI Engineer | Task: 为新增搜索框和状态提示补充样式并适配移动端 | Restrictions: 保持现有设计基调，不引入新的样式系统 | Success: 新元素样式统一且在 960px 以下可正常显示_

- [x] 3. 在状态中加入关键词字段并接入事件绑定
  - File: app.js
  - 在全局 state 中增加 `keyword`
  - 监听关键词输入事件并触发过滤
  - Purpose: 将关键词输入纳入状态驱动渲染
  - _Leverage: 现有 `tagSelect` 的事件监听模式_
  - _Requirements: 2.2, 2.3_
  - _Prompt: Role: JavaScript Engineer | Task: 在状态模型中加入关键词并绑定输入事件刷新视图 | Restrictions: 不引入框架，不改动现有初始化主流程 | Success: 输入关键词后列表与详情按预期更新_

- [x] 4. 抽离并实现统一过滤函数
  - File: app.js
  - 新增纯函数处理标签 + 关键词的组合过滤
  - 保持过滤结果与 `activeId` 的一致性 fallback
  - Purpose: 降低 `applyFilter` 复杂度并提高可维护性
  - _Leverage: 现有 `applyFilter` 逻辑和 `state.filteredPosts`_
  - _Requirements: 1.3, 2.1, 2.3_
  - _Prompt: Role: JavaScript Engineer | Task: 用纯函数重构过滤逻辑以同时支持标签与关键词 | Restrictions: 不能破坏原有排序和默认选中文章行为 | Success: 所有筛选场景下 activeId 与展示内容一致_

- [x] 5. 增强 hash 同步与无效值回退逻辑
  - File: app.js
  - 统一初始化和 `hashchange` 事件中的 hash 处理
  - 对无效 hash 增加回退策略
  - Purpose: 保证深链分享和页面状态一致
  - _Leverage: 现有 `getHashPostId`、`setHash` 和 `hashchange` 监听_
  - _Requirements: 3.1, 3.2, 3.3_
  - _Prompt: Role: Frontend Engineer | Task: 强化 hash 解析与回退策略并复用现有路由函数 | Restrictions: 不引入新路由库，保持 URL 结构不变 | Success: 有效 hash 可直达，无效 hash 不导致空白或错误状态_

- [x] 6. 完善加载失败和空结果状态渲染
  - File: app.js
  - 在 `init` 中加入 fetch 异常处理
  - 区分“无匹配结果”与“加载失败”的文案
  - Purpose: 提升可靠性和可用性
  - _Leverage: 现有 `renderDetail` 的空状态输出方式_
  - _Requirements: 5.1, 5.2, 6.1_
  - _Prompt: Role: Frontend Engineer | Task: 为加载异常和筛选空结果补全状态渲染 | Restrictions: 不改变现有主布局结构 | Success: 三类状态（正常/无匹配/加载失败）均有明确反馈_

- [x] 7. 手动回归验证关键路径
  - File: README.md
  - 补充“标签 + 搜索 + hash”联合验证步骤
  - 记录最小回归清单
  - Purpose: 建立可重复的功能验收路径
  - _Leverage: 现有本地预览命令说明_
  - _Requirements: 1.1, 2.1, 3.1_
  - _Prompt: Role: QA Engineer | Task: 在 README 中整理可执行的手动回归步骤 | Restrictions: 步骤需简洁且可直接复现 | Success: 新开发者按文档即可完成核心功能验收_
