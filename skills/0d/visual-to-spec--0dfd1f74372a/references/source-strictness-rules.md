# Source & Strictness Rules

所有从截图提取的值必须携带 source、confidence、strictness 标注。这是本 skill 的核心质量保证机制。

---

## Source 标签

每个值必须标注其来源：

| 标签 | 定义 | 使用场景 |
|------|------|----------|
| `reference-visible` | 截图中清晰可见，可直接读取，并能给出 bbox 与视觉证据 | 明确的文字内容、清晰的图标、明显的浮层/按钮/面板/场景区域 |
| `screenshot-estimated` | 从截图像素估算得出 | 颜色取样、字号估算、间距测量、bbox 微调 |
| `screenshot-inferred` | 从截图上下文推断 | 间距规律、网格系统、重复模式、z-index 关系 |
| `inferred-implementation` | 实现性推断，截图中无直接对应 | wrapper 组件（AppShell、OverlayLayer、SceneImageLayer）、逻辑容器 |

### reference-visible 证明规则

任何 `reference-visible` 主张必须能回答：

1. 它在截图中的 bbox 是什么？格式为 `x, y, w, h`（px 或 %）。
2. 视觉证据是什么？例如可见文字、图标形状、边框、面板背景、热点圆点、缩略图。
3. 这个元素是否真的独立于背景/主视觉资产？如果它是照片级场景的一部分，可能应标为 `asset-embedded` 或写入 asset strategy，而不是 DOM 组件。

不能给出 bbox 和视觉证据的组件不得标为 `reference-visible`。例如：图中没有右侧详情面板时，不得把 `RightPanel` 写成 `reference-visible`；只能写入 Rejected Assumptions。

### 标注原则

- 如果能在截图中直接指出，并能给出 bbox → `reference-visible`
- 如果需要从像素采样或测量 → `screenshot-estimated`
- 如果需要从模式或上下文推断 → `screenshot-inferred`
- 如果是为实现而添加的逻辑结构 → `inferred-implementation`
- 如果是图中不存在但模型容易补全的业务结构 → 写入 Rejected Assumptions，不进入组件树

---

## Confidence 标注

每个值必须包含数值置信度和对应标签：

| 数值范围 | 标签 | 含义 |
|----------|------|------|
| 0.8 - 1.0 | `high` | 高度确信，可直接用于实现 |
| 0.6 - 0.79 | `medium` | 较有把握，建议验证 |
| 0.0 - 0.59 | `low` | 不确定，必须人工审查 |

### 影响 confidence 的因素

**提高 confidence 的因素：**
- 截图清晰度高
- 元素边界明确
- 有重复模式可交叉验证
- 标准字体/颜色可识别
- 能给出稳定 bbox 与视觉证据

**降低 confidence 的因素：**
- 截图模糊或压缩严重
- 元素重叠或边界不清
- 渐变、发光、半透明效果
- 非标准字体
- 小尺寸元素
- UI 类型可能有多个解释
- 主视觉是照片级/3D/raster 场景，DOM 与资产边界不清

---

## Strictness 标签

每个 token 必须标注实现严格度：

| 标签 | 定义 | 实现要求 |
|------|------|----------|
| `required` | 必须精确匹配 | 偏差不可接受，如品牌色、主视觉资产、关键浮层位置 |
| `recommended` | 建议遵循 | 允许微调（±1-2px 或相近色值） |
| `flexible` | 可根据实现调整 | 如响应式 wrapper padding、辅助间距 |

### Strictness 判断依据

- 品牌相关（logo 颜色、主色调）→ `required`
- 主视觉资产、全屏场景图、关键 overlay bbox → `required`
- 视觉一致性相关（文字颜色、主要间距）→ `recommended`
- 实现便利性相关（wrapper padding、辅助间距）→ `flexible`

---

## 值结构模板

每个提取的值必须遵循以下结构：

```json
{
  "value": "<实际值>",
  "source": "<source 标签>",
  "confidence": 0.82,
  "confidenceLabel": "high",
  "strictness": "<strictness 标签>",
  "bbox": "x:0,y:0,w:100,h:48",
  "evidence": "<截图中的视觉证据>",
  "notes": "<补充说明，可选>"
}
```

在 tokens.json 中，这些字段位于 `$extensions` 内：

```json
{
  "$value": "<实际值>",
  "$type": "<类型>",
  "$extensions": {
    "source": "<source 标签>",
    "confidence": 0.82,
    "confidenceLabel": "high",
    "strictness": "<strictness 标签>",
    "notes": "<补充说明>",
    "usedBy": ["<组件列表>"]
  }
}
```

---

## 低置信度处理规则

当 confidence < 0.6 时：

1. 该值仍然写入 tokens.json（作为 best-effort 估算）
2. 必须在 `notes` 中说明不确定原因
3. 必须出现在 `human-review-needed.md` 中
4. 必须在 DESIGN.md 的置信度摘要中计入"低"类别

UI 类型、asset strategy、主视觉是否可 DOM 化属于高影响判断；即使 confidence 为 medium，也要在 human-review-needed 中给出复核入口。

---

## 禁止行为

- 不得将 source 标为 `reference-visible` 除非确实能在截图中直接指出 bbox。
- 不得省略任何一个必需字段（source、confidence、confidenceLabel、strictness）。
- 不得对 `inferred-implementation` 类型的值标注 `strictness: required`。
- 不得引入截图中不存在的颜色、字体、间距值、业务面板、导航、表格、图表或地图。
- 不得把照片级主视觉中的复杂场景对象拆成可精确 CSS 复刻的 DOM 组件，除非截图/需求明确提供独立资产或矢量结构。
