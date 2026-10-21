# Human Review Needed

## 摘要

- 总计需审查项：9
- 低置信度 token：2
- 不确定组件边界：2
- 需脚本验证：3
- UI 类型/资产策略复核：2

---

## 审查清单

| # | 阶段 | 项目 | 当前值 | Confidence | 建议验证方式 |
|---|------|------|--------|------------|-------------|
| 1 | 1 | UI Type | panorama-scene | 0.72 | 人工目视确认是否为全景/3D 展厅 UI |
| 2 | 1 | 主视觉资产策略 | SceneImageLayer 必须使用 raster asset | 0.78 | 设计稿/素材确认 |
| 3 | 1 | Rejected Assumption: RightPanel | 图中不存在右侧详情面板 | 0.82 | 人工目视确认 |
| 4 | 2 | overlay-panel 颜色 | #1E1F22CC | 0.58 | 像素采样脚本 |
| 5 | 2 | glow-cyan 色值 | #6FE6FF | 0.55 | 像素采样脚本 |
| 6 | 4 | thumbnail-gap | 14px | 0.65 | bbox 测量工具 |
| 7 | 5 | HotspotMarkers 精确中心点 | multiple x/y positions | 0.58 | 图像标注工具 |
| 8 | 5 | 响应式缩放策略 | cover + overlay percentage anchors | 0.55 | 多尺寸设计稿确认 |
| 9 | 8 | 视觉回归阈值 | 未定义 | N/A | Playwright screenshot diff / 人工设定 |

---

## 详细说明

### 1. UI Type

- **来源阶段**：1（全局构图）
- **当前判断**：`panorama-scene`
- **Confidence**：0.72
- **不确定原因**：单张截图无法确认真实 360° 引擎，只能从“360°”文案、底部视角缩略图、全屏场景判断。
- **建议验证方式**：人工确认产品形态；若是普通静态海报，应改为 `poster-like-ui`。

### 2. 主视觉资产策略

- **来源阶段**：1（Asset Strategy）
- **当前判断**：主视觉必须使用 raster asset 或全景/3D 引擎。
- **Confidence**：0.78
- **不确定原因**：截图中可见照片级光影和复杂场景，但无法确认是否有独立背景图、切图或 3D 资源。
- **建议验证方式**：查看设计源文件或素材包；若没有独立素材，后续实现只能用截图级复刻。

### 3. Rejected Assumption: RightPanel

- **来源阶段**：1（Rejected Assumptions）
- **当前判断**：图中不存在右侧独立详情面板。
- **Confidence**：0.82
- **不确定原因**：右上有控制组，但不是面板；需防止模型把它扩展为完整详情栏。
- **建议验证方式**：人工目视确认。

### 4. HotspotMarkers 精确中心点

- **来源阶段**：5（布局规格）
- **当前判断**：热点中心点以 LLM 目测估算。
- **Confidence**：0.58
- **不确定原因**：小圆点受发光、抗锯齿和缩放影响，中心点需要工具测量。
- **建议验证方式**：图像标注工具或脚本测量。
