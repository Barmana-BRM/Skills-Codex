# Script-Backed Boundary

本 skill 明确区分三类操作的能力边界。当缺少脚本支持时，LLM 做 best-effort 估算并在 notes 中标注限制。

---

## LLM 可独立完成

以下操作 LLM 可直接完成，无需外部工具：

| 操作 | 说明 | 典型 Confidence |
|------|------|----------------|
| UI 类型判定 | 判断 dashboard、panorama-scene、image-led 等 | 0.65 - 0.95 |
| 视觉识别 | 识别组件类型、布局模式、浮层控件 | 0.7 - 0.95 |
| 颜色估算 | 从截图估算 hex 值 | 0.6 - 0.85 |
| 布局判断 | 判断 flex/grid/absolute/overlay | 0.75 - 0.95 |
| 组件分类 | 识别按钮、卡片、导航、热点、缩略图等 | 0.8 - 0.95 |
| 比例估算 | 估算元素相对大小与 bbox | 0.6 - 0.8 |
| 字体识别 | 识别常见字体族 | 0.5 - 0.85 |
| 层级推断 | 推断 z-index 关系 | 0.7 - 0.9 |
| 间距模式 | 识别间距规律 | 0.6 - 0.8 |
| Rejected Assumptions | 列出截图中不存在但容易被补全的结构 | 0.7 - 0.9 |

---

## 需要脚本辅助（Script-Backed）

以下操作需要脚本/工具才能获得精确结果：

| 操作 | 无脚本时的处理 | 脚本工具 |
|------|---------------|----------|
| 精确颜色值提取 | 估算 hex，标注 `screenshot-estimated` | 像素采样脚本 |
| WCAG 对比度计算 | 标注 `estimated-contrast`，不做 pass/fail 判断 | contrast-ratio 计算器 |
| delta-E 颜色差异 | 跳过，标注需脚本验证 | delta-E 计算库 |
| 精确像素测量 | 估算 bbox，标注 confidence | 图像测量工具 |
| bbox 批量验证 | 给出人工估算，标注需脚本验证 | 边缘检测/标注工具 |
| 字体精确匹配 | 标注最接近的匹配 + confidence | 字体识别服务 |
| 亚像素渲染分析 | 跳过 | 图像分析工具 |
| 视觉回归 | 不声明像素级匹配 | Playwright screenshot diff、SSIM、pixelmatch |
| 主视觉资产裁切 | 标注 asset strategy，等待素材确认 | 图像裁切/切图工具 |

### 无脚本时的标注方式

```json
{
  "$value": "#1A2B3C",
  "$type": "color",
  "$extensions": {
    "source": "screenshot-estimated",
    "confidence": 0.7,
    "confidenceLabel": "medium",
    "strictness": "required",
    "notes": "LLM estimated; script verification recommended for exact value."
  }
}
```

---

## 需要人工确认

以下情况必须标记为需人工审查：

| 情况 | 原因 | 处理方式 |
|------|------|----------|
| 低置信度颜色值 | 截图压缩/模糊 | 写入 human-review-needed.md |
| 模糊的组件边界 | 元素重叠或边界不清 | 标注两种可能的解读 |
| 不确定的 UI 类型 | 后续组件树会完全不同 | 列出候选类型与证据 |
| 不确定的字体识别 | 非标准字体或小字号 | 列出 top-3 候选 |
| 渐变色端点 | 渐变方向和端点不确定 | 估算 + 标注 |
| 半透明效果 | 无法确定 opacity 值 | 估算 + 标注 |
| 动效暗示 | 静态截图无法确认 | 记录观察到的暗示 |
| raster 主视觉 | 无法从截图推断独立素材 | 标注 asset strategy 与素材需求 |
| 全景/3D 场景交互 | 静态截图无法确认拖拽、旋转、热点逻辑 | 产品/设计稿确认 |

---

## 边界决策流程

对每个提取值，按以下流程决定处理方式：

```text
截图中是否清晰可见并可给出 bbox？
├── 是 → source: reference-visible, confidence: 0.85+
└── 否 → 能否从像素估算？
    ├── 是 → source: screenshot-estimated
    │   └── 有脚本？
    │       ├── 是 → 运行脚本，提高 confidence
    │       └── 否 → best-effort 估算，标注需脚本验证
    └── 否 → 能否从上下文推断？
        ├── 是 → source: screenshot-inferred
        │   └── confidence >= 0.6?
        │       ├── 是 → 正常记录
        │       └── 否 → 标记 human-review-needed
        └── 否 → 是否为实现性需要？
            ├── 是 → source: inferred-implementation
            └── 否 → 写入 Rejected Assumptions 或不记录
```

---

## 与其他 skill 的协作

- **spec-compliance-review**：负责精确 WCAG 对比度、bbox、视觉回归验证，本 skill 只做估算和验证需求标注。
- **code-from-spec**：消费本 skill 的输出进行实现；如果 `asset strategy` 说明主视觉必须用 raster，后续实现不得用 CSS/SVG 重建主视觉。
- 本 skill 的 `implementation-risks.md` 中应标注哪些项需要后续 skill 或脚本验证。
