# Token Schema

tokens.json 采用 DTCG-inspired 格式，兼容 DTCG 思路但允许项目级简化。若项目已有 token 标准，优先适配项目标准。

## 顶层结构

```json
{
  "color": { ... },
  "typography": { ... },
  "spacing": { ... },
  "borderRadius": { ... },
  "shadow": { ... }
}
```

## 单个 Token 结构

每个 token 必须包含以下字段：

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `$value` | string/number | 是 | token 的值 |
| `$type` | string | 是 | token 类型（color, dimension, fontFamily 等） |
| `$extensions` | object | 是 | 扩展元数据（见下方） |

## $extensions 字段

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `source` | string | 是 | 值的来源标签 |
| `confidence` | number | 是 | 置信度数值 0-1 |
| `confidenceLabel` | string | 是 | 置信度标签：high / medium / low |
| `strictness` | string | 是 | 严格度标签 |
| `notes` | string | 否 | 补充说明 |
| `usedBy` | array | 否 | 使用该 token 的组件列表 |
| `bbox` | string | 否 | 当 token 来自单个可见元素时可记录 x/y/w/h |
| `evidence` | string | 否 | 当 source 为 reference-visible 时建议记录视觉证据 |

## source 标签

| 标签 | 含义 |
|------|------|
| `reference-visible` | 截图中清晰可见，可直接读取 |
| `screenshot-estimated` | 从截图估算得出（如颜色取样） |
| `screenshot-inferred` | 从截图上下文推断（如间距规律） |
| `inferred-implementation` | 实现性推断（如 wrapper 组件） |

> `reference-visible` 的组件级值必须在对应 spec 中记录 bbox 与视觉证据；token 级 bbox 可选，用于可追溯性增强。

## strictness 标签

| 标签 | 含义 |
|------|------|
| `required` | 实现时必须精确匹配 |
| `recommended` | 建议遵循，允许微调 |
| `flexible` | 可根据实现需要调整 |

## confidenceLabel 映射

| 数值范围 | 标签 |
|----------|------|
| 0.8 - 1.0 | high |
| 0.6 - 0.79 | medium |
| 0.0 - 0.59 | low |

## $type 可选值

### 颜色
- `color`

### 字体排印
- `fontFamily`
- `fontSize`
- `fontWeight`
- `lineHeight`
- `letterSpacing`

### 间距
- `dimension`（用于 spacing、padding、margin、gap）

### 圆角
- `borderRadius`

### 阴影
- `shadow`

## 完整示例

见 → `examples/tokens.example.json`
