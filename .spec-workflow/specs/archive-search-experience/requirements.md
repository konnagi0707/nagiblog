# Requirements Document

## Introduction
本规格定义归档页面的“筛选 + 搜索 + 阅读联动”能力，以支持用户快速定位历史文章并稳定阅读。

## Alignment with Product Vision
本功能直接支撑 `product.md` 中“可检索优先”和“可读性优先”原则，目标是减少用户查找路径并提升详情页可读性。

## Requirements

### Requirement 1 - 时间线与详情联动
**User Story:** 作为读者，我希望从时间线快速选择文章并查看详情，从而高效浏览归档内容。

#### Acceptance Criteria
1. WHEN 页面初始化完成 THEN 系统 SHALL 按日期倒序渲染时间线列表。
2. WHEN 用户点击任意文章项 THEN 系统 SHALL 高亮该项并在右侧显示对应详情。
3. IF 当前过滤结果为空 THEN 系统 SHALL 显示明确的空状态文案。

### Requirement 2 - 标签与关键词检索
**User Story:** 作为读者，我希望通过标签和关键词缩小结果范围，从而更快找到目标文章。

#### Acceptance Criteria
1. WHEN 用户选择标签 THEN 系统 SHALL 仅展示包含该标签的文章。
2. WHEN 用户输入关键词 THEN 系统 SHALL 在标题和正文中进行不区分大小写匹配。
3. WHEN 标签与关键词同时生效 THEN 系统 SHALL 返回两者条件的交集结果。

### Requirement 3 - 直链与状态一致性
**User Story:** 作为分享者，我希望通过链接直接打开指定文章，从而减少沟通成本。

#### Acceptance Criteria
1. WHEN URL hash 为有效文章 ID THEN 系统 SHALL 自动定位并展示该文章。
2. WHEN 用户切换当前文章 THEN 系统 SHALL 同步更新 URL hash。
3. IF URL hash 无效 THEN 系统 SHALL 回退到当前过滤结果的第一篇文章或空状态。

## Non-Functional Requirements

### Code Architecture and Modularity
- **Single Responsibility Principle**: 数据处理、过滤逻辑、渲染逻辑、路由同步应职责分离。
- **Modular Design**: 新增能力应优先以可复用函数实现。
- **Dependency Management**: 避免 UI 层直接耦合数据加载细节。
- **Clear Interfaces**: 过滤函数与渲染函数使用明确入参/出参。

### Performance
- 标签切换和关键词搜索的交互反馈应接近即时。
- 在中小规模文章数据下保持页面滚动和点击流畅。

### Security
- 外链统一采用安全属性；禁止渲染不可信 HTML。

### Reliability
- 数据加载失败时给出可理解的错误提示，不出现空白页面。

### Usability
- 空状态、无匹配状态、加载失败状态均有明确提示。
- 移动端下列表与详情区域仍可访问。
