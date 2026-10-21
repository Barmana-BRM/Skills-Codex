# Extraction Workflow

9 阶段串行执行。在 Claude Code 环境中按阶段写入文件；在 ChatGPT 环境中按阶段生成结构化内容，最后一次性输出。

如果任何阶段产生低置信度结果（confidence < 0.6），标记为需要人工审查。布局类型、主视觉资产策略、可见组件边界属于高影响判断：即使 confidence 为 medium，也要在 `human-review-needed.md` 中给出复核入口。

---

## 阶段 1：全局构图分析

### 1.1 UI 类型判定（强制）

先判定 `uiType`，再进入普通布局分析。可选值：

| uiType | 判定线索 | 后续布局模型 |
|--------|----------|--------------|
| `application-dashboard` | 明确侧栏、表格、卡片、图表、详情面板 | flex/grid 应用布局 |
| `panorama-scene` | 360°、全景、展厅、3D/照片级场景、大面积背景图 + 浮层控件 | raster scene layer + absolute overlay |
| `image-led-landing` | 大图/产品图主导首屏，少量导航/CTA 覆盖 | image/media layer + responsive overlay |
| `mobile-app` | 手机比例或移动端控件 | mobile viewport layout |
| `poster-like-ui` | 海报、封面、静态视觉主导，弱交互 | image/text composition |
| `unknown` | 类型不清晰 | 输出多候选并进入人工复核 |

不得默认套用 dashboard / 三栏 / AppShell。若 `uiType` 低于 0.75 confidence，必须列出 top-2 候选与选择理由。

### 1.2 可见元素证据

输出 Visible Element Inventory。每个 `reference-visible` 元素必须有：

- 名称
- bbox（px 或 %，至少 x/y/w/h）
- 视觉证据（截图中可指认的文字、图标、边界、形状、位置）
- source/confidence

### 1.3 Rejected Assumptions

列出容易误判但截图中不存在的组件或结构。例如：右侧详情面板、TabBar、地图拓扑、状态栏、数据表格。被列入 Rejected Assumptions 的内容不得进入 component-tree。

### 1.4 Asset Strategy

判断哪些视觉内容必须作为 raster/image asset 实现，哪些可以用 HTML/CSS/SVG 实现：

- `panorama-scene` / `image-led-landing`：主视觉、3D 展台、真实产品、复杂光影、地面反射通常必须作为 raster asset。
- 浮层面板、文字、热点、按钮、缩略图容器通常可用 HTML/CSS 实现。
- 若没有独立素材，必须说明只能做到截图级静态复刻，不能凭 CSS/SVG 重建照片级主体。

**输出**：`visual-analysis.md`（第 1 节）

---

## 阶段 2：颜色提取

对图中每个不同的颜色提取：

- Hex 值
- 角色分类：
  - `background` | `surface` | `primary` | `secondary` | `accent`
  - `text-primary` | `text-secondary` | `text-muted`
  - `border` | `shadow`
  - `success` | `warning` | `error` | `info`
- 出现位置（区域 + 元素）
- 估算对比度（标注 `estimated-contrast`；精确 WCAG 判断交给后续脚本或 spec-compliance-review）

对 `panorama-scene`：区分 scene/raster 中的环境色与可实现 UI token。不要把照片级光影的全部像素色都升级成设计 token；只提取会被前端复用的 UI 颜色和关键品牌/发光色。

格式：DTCG-inspired JSON schema（兼容 DTCG 思路，允许项目级简化；若项目已有 token 标准，优先适配项目标准）

**输出**：`visual-analysis.md`（第 2 节）+ `tokens.json`（颜色部分）

---

## 阶段 3：字体排印提取

对每个文本元素提取：

- 字体族（可识别则标注，否则标注最接近的匹配）
- 字号（px，估算）
- 字重（100-900）
- 行高
- 字间距（如果显著）
- 颜色（引用阶段 2 的 token）
- 语义角色：`h1` | `h2` | `h3` | `body` | `caption` | `label` | `button` | `code` | `overline`

对贴在 raster 主视觉内且无法独立实现的文字（如展台墙面 logo），标注为 `asset-embedded-text`，不要强制作为 DOM 文本。

**输出**：`visual-analysis.md`（第 3 节）+ `tokens.json`（字体排印部分）

---

## 阶段 4：间距与网格系统

测量：

- 基础间距单位（通常 4px 或 8px）
- 内边距模式（组件内部）
- 外边距模式（组件之间）
- 网格列数和间距（如适用）
- 区块间距

对 overlay UI：记录浮层与画布边缘的距离、浮层之间的间距、热点标记相对画布坐标。不要把大面积场景透视距离误判为 CSS grid。

**输出**：`visual-analysis.md`（第 4 节）+ `tokens.json`（间距部分）

---

## 阶段 5：布局规格

先读取阶段 1 的 `uiType`，再选择布局模型：

### application-dashboard

对每个主要区域：

- 定位方式：`flex` | `grid` | `absolute` | `fixed`
- 尺寸：宽度、高度（px 或 %）
- 溢出行为（可见 / 滚动 / 隐藏 — 根据内容密度推断）
- Z-index 层级（如存在重叠元素）
- 每个区域的圆角

### panorama-scene / image-led-landing

使用画布坐标模型：

- `Canvas`：截图尺寸、目标 aspect-ratio、缩放策略（cover/contain/fixed）
- `SceneImageLayer`：主视觉资产路径、铺放方式、是否保持原始比例
- `OverlayLayer`：position absolute/fixed，z-index 层级
- 每个浮层控件：bbox、anchor、z-index、响应式约束、是否覆盖主视觉
- `HotspotMarkers`：每个热点的中心点、直径、标签、点击区域
- 底部/顶部控件：固定位置、滚动/溢出行为

**输出**：`layout-spec.md`

---

## 阶段 6：组件树构建

根据 `uiType` 构建组件树。不要使用不匹配的示例结构。

### application-dashboard 常见骨架

可使用 AppShell / Sidebar / MainContent / RightPanel / Card / Table / Chart 等组件，但只有在截图确实可见时才能标为 `reference-visible`。

### panorama-scene 常见骨架

```text
PanoramaExperience [source: inferred-implementation]
├── SceneImageLayer [source: reference-visible or inferred-implementation]
├── BrandOverlay [source: reference-visible]
├── TitleOverlay [source: reference-visible]
├── RegionGuidePanel [source: reference-visible]
├── OperationGuidePanel [source: reference-visible]
├── TopHintOverlay [source: reference-visible]
├── TopRightControls [source: reference-visible]
├── HotspotMarkers [source: reference-visible]
├── Drag360Indicator [source: reference-visible]
└── ViewThumbnailCarousel [source: reference-visible]
```

对每个组件记录：

- 估算尺寸或 bbox
- 关键样式属性（背景、边框、圆角、阴影）
- 内容类型（文本 / 图标 / 图片 / 图表 / 交互 / raster asset）
- 嵌套深度
- source/confidence/strictness

组件树使用缩进树形格式表示（见 `examples/component-tree.example.md`）。

**输出**：`component-tree.md`

---

## 阶段 7：Token 合并与验证

将所有阶段的 token 合并为单个 `tokens.json`。

Token schema 见 → `references/token-schema.md`

验证规则：

- 每个 token 必须追溯到具体的视觉元素
- 无孤立 token（已定义但未使用）
- 无遗漏 token（在组件树中使用但未定义）
- `panorama-scene` 中 raster 主视觉的环境像素色不得全部变成 UI token；只保留可复用 UI/品牌/发光色

**输出**：`tokens.json`（最终版本）

---

## 阶段 8：实现风险评估

识别：

- CSS/HTML 中难以实现的组件
- 动画/过渡提示（如果暗示了任何动效）
- 需要资源的自定义插图、图标、raster 主视觉、缩略图或切图
- 需要库的图表/数据可视化组件
- 潜在的响应式断点挑战
- 主视觉资产缺失、截图级复刻限制、视觉回归风险
- 低置信度区域汇总（需人工确认项）
- 需要脚本验证的项目（精确颜色值、WCAG 对比度、bbox、视觉回归等）

**输出**：`implementation-risks.md`

---

## 阶段 9：人工复核清单生成

从所有阶段收集：

- confidence < 0.6 的 token
- 不确定的 UI 类型或组件边界
- 需要脚本验证的颜色 / WCAG / 像素值 / bbox / 视觉回归
- 与截图模糊区域相关的判断
- 可能影响实现的低置信结论
- asset strategy 中无法确认的素材来源
- Rejected Assumptions 中仍有争议的结构

每项包含：

- 来源阶段编号
- 具体值或判断
- 当前 confidence
- 建议验证方式（脚本 / 人工目视 / 工具测量 / 产品确认）

**输出**：`human-review-needed.md`

---

## 最终汇总：DESIGN.md

汇总的可读文档，结构如下：

```markdown
# DESIGN.md

## 事实来源
- reference.png：[路径]
- 提取日期：[ISO 日期]
- uiType：[application-dashboard / panorama-scene / ...]
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
[来自 tokens.json 的摘要]

## 实现风险
[来自 implementation-risks.md]
```
