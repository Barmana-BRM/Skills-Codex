# Output Files

所有输出文件写入 `03_visual_spec/` 目录。

---

## visual-analysis.md

包含 4 个章节，对应阶段 1-4 的分析结果。第 1 节必须先完成 UI 类型判定与可见元素证据。

### 结构模板

```markdown
# Visual Analysis

## 1. 全局构图

- **UI Type**: [application-dashboard / panorama-scene / image-led-landing / mobile-app / poster-like-ui / unknown]
- **UI Type Confidence**: [0-1]
- **页面尺寸**：[宽 x 高]
- **宽高比**：[ratio]
- **主视觉模型**：[structured-layout / raster-scene-layer / media-led-layout / unknown]

### UI Type Rationale

[用 2-4 条证据说明为什么选择该 UI type；如果存在候选类型，列出 top-2。]

### Visible Element Inventory

| 元素 | bbox (px 或 %) | 视觉证据 | Source | Confidence |
|------|----------------|----------|--------|------------|
| ... | x:..., y:..., w:..., h:... | 截图中可见的文字/图标/边界/形状 | reference-visible | ... |

### Rejected Assumptions

| 假设组件/结构 | 拒绝原因 | 影响 |
|---------------|----------|------|
| RightPanel | 截图中无右侧独立详情面板 bbox | 不得生成 RightPanel 组件 |

### Asset Strategy

| 资产/视觉层 | 实现方式 | 原因 | Source | Confidence |
|-------------|----------|------|--------|------------|
| SceneImageLayer | raster asset | 照片级/3D 场景无法用 CSS 精确重建 | reference-visible | ... |
| Overlay controls | HTML/CSS | 独立浮层控件，可重建 | reference-visible | ... |

### 视觉区域

| 区域 | 边界框 | 层级 | 背景/实现方式 | Source | Confidence |
|------|--------|------|---------------|--------|------------|
| ... | ... | ... | ... | ... | ... |

## 2. 颜色系统

| Token 名 | Hex | 角色 | 出现位置 | Source | Confidence |
|----------|-----|------|----------|--------|------------|
| ... | ... | ... | ... | ... | ... |

### 估算对比度

| 前景 | 背景 | 估算比值 | 备注 |
|------|------|----------|------|
| ... | ... | ... | estimated-contrast |

## 3. 字体排印

| 语义角色 | 字体族 | 字号 | 字重 | 行高 | 颜色 Token | Source | Confidence |
|----------|--------|------|------|------|-----------|--------|------------|
| ... | ... | ... | ... | ... | ... | ... | ... |

## 4. 间距系统

- **基础单位**：[n]px
- **内边距模式**：[描述]
- **外边距/浮层边距模式**：[描述]
- **网格/坐标系统**：[列数/overlay coordinates]，间距 [n]px

| 间距 Token | 值 | 用途 | Source | Confidence |
|-----------|-----|------|--------|------------|
| ... | ... | ... | ... | ... |
```

---

## layout-spec.md

### 结构模板

```markdown
# Layout Specification

## 整体布局

- **UI Type**：[值]
- **容器宽度**：[值]
- **容器高度**：[值]
- **布局模式**：[flex / grid / absolute-overlay / fixed-canvas]
- **坐标系统**：[viewport pixels / percentages / responsive constraints]

## 区域规格

### [区域名称]

| 属性 | 值 | Source | Confidence |
|------|-----|--------|------------|
| 定位方式 | flex / grid / absolute / fixed | ... | ... |
| bbox | x/y/w/h 或 anchor + size | ... | ... |
| 宽度 | ... | ... | ... |
| 高度 | ... | ... | ... |
| 溢出 | visible / scroll / hidden | ... | ... |
| Z-index | ... | ... | ... |
| 圆角 | ... | ... | ... |

[对每个主要区域重复]

## Overlay 约束（适用于 panorama-scene / image-led-landing）

| 组件 | Anchor | bbox | z-index | 响应式约束 | Source | Confidence |
|------|--------|------|---------|------------|--------|------------|
| ... | top-left / top-center / bottom-center | ... | ... | ... | ... | ... |
```

---

## component-tree.md

### 结构模板

```markdown
# Component Tree

## UI Type

- **值**：[application-dashboard / panorama-scene / ...]
- **组件树模型**：[dashboard-shell / raster-scene-with-overlays / media-led-layout]

## 树形结构

PanoramaExperience [source: inferred-implementation]
├── SceneImageLayer [source: reference-visible]
├── OverlayLayer [source: inferred-implementation]
│   ├── BrandOverlay [source: reference-visible]
│   ├── RegionGuidePanel [source: reference-visible]
│   ├── OperationGuidePanel [source: reference-visible]
│   ├── TopHintOverlay [source: reference-visible]
│   ├── TopRightControls [source: reference-visible]
│   ├── HotspotMarkers [source: reference-visible]
│   └── ViewThumbnailCarousel [source: reference-visible]
└── InteractionLayer [source: inferred-implementation]

## 组件详情

### [组件名]

- **Source**: [reference-visible / screenshot-estimated / screenshot-inferred / inferred-implementation]
- **bbox**: [x/y/w/h；reference-visible 必填]
- **尺寸**: [宽 x 高]
- **背景**: [token 引用 / raster asset / transparent]
- **边框**: [描述]
- **圆角**: [token 引用]
- **阴影**: [token 引用]
- **内容类型**: [文本 / 图标 / 图片 / 图表 / 交互 / raster asset]
- **Confidence**: [值]

[对每个组件重复]
```

Dashboard 组件树只应在 `uiType: application-dashboard` 且截图确实可见侧栏/主内容/右面板时使用。

---

## tokens.json

完整 schema 见 → `references/token-schema.md`
示例见 → `examples/tokens.example.json`

---

## implementation-risks.md

### 结构模板

```markdown
# Implementation Risks

## 高风险

| 项目 | 描述 | 建议方案 |
|------|------|----------|
| ... | ... | ... |

## 中风险

| 项目 | 描述 | 建议方案 |
|------|------|----------|
| ... | ... | ... |

## 需脚本验证

| 项目 | 当前估算值 | 验证方式 |
|------|-----------|----------|
| bbox 精确性 | LLM 估算 | 像素测量工具 |
| 视觉回归 | 未执行 | 截图 diff / SSIM / Playwright screenshot |

## 低置信度汇总

| 项目 | 阶段 | Confidence | 影响范围 |
|------|------|------------|----------|
| ... | ... | ... | ... |
```

---

## human-review-needed.md

### 结构模板

```markdown
# Human Review Needed

## 摘要

- 总计需审查项：[n]
- 低置信度 token：[n]
- 不确定组件边界：[n]
- 需脚本验证：[n]
- UI 类型/资产策略复核：[n]

## 审查清单

| # | 阶段 | 项目 | 当前值 | Confidence | 建议验证方式 |
|---|------|------|--------|------------|-------------|
| 1 | ... | ... | ... | ... | 脚本 / 人工目视 / 工具测量 / 产品确认 |

## 详细说明

### [项目名]

- **来源阶段**：[n]
- **当前判断**：[描述]
- **Confidence**：[值]
- **不确定原因**：[描述]
- **建议验证方式**：[描述]
```

---

## DESIGN.md

### 结构模板

```markdown
# DESIGN.md

## 事实来源

- reference.png：[路径]
- 提取日期：[ISO 日期]
- uiType：[值]
- 置信度摘要：高 [n] / 中 [n] / 低 [n]
- 需人工确认：[n] 项
- 需脚本验证：[n] 项

## 能力边界

- LLM 估算项：[list]
- 需脚本验证项：[list]
- 需人工确认项：[list]

## 可见元素证据

[来自 visual-analysis.md]

## Asset Strategy

[来自 visual-analysis.md]

## 布局概览

[来自 layout-spec.md]

## 组件架构

[来自 component-tree.md]

## 设计 Token

[来自 tokens.json 的摘要表格]

## 实现风险

[来自 implementation-risks.md]
```
