# Layout Specification

## 整体布局

- **UI Type**: panorama-scene
- **容器宽度**: 1774px reference, responsive viewport width
- **容器高度**: 887px reference, responsive viewport height
- **布局模式**: fixed-canvas + absolute-overlay
- **坐标系统**: reference pixels converted to percentages for responsive scaling
- **Source**: screenshot-estimated
- **Confidence**: 0.88

---

## 图层模型

| 图层 | 定位方式 | bbox | Z-index | Source | Confidence |
|------|----------|------|---------|--------|------------|
| SceneImageLayer | absolute, inset:0, object-fit: cover | x:0 y:0 w:1774 h:887 | 0 | reference-visible | 0.95 |
| OverlayLayer | absolute, inset:0 | x:0 y:0 w:1774 h:887 | 10 | inferred-implementation | 0.9 |
| InteractionLayer | absolute, inset:0 | x:0 y:0 w:1774 h:887 | 20 | inferred-implementation | 0.75 |

---

## Overlay 组件规格

### BrandOverlay

| 属性 | 值 | Source | Confidence |
|------|-----|--------|------------|
| 定位方式 | absolute | screenshot-estimated | 0.9 |
| Anchor | top-left | screenshot-estimated | 0.9 |
| bbox | x:22 y:24 w:210 h:52 | screenshot-estimated | 0.86 |
| Z-index | 12 | screenshot-inferred | 0.8 |
| 内容 | logo + AETHEREAL HEALTH | reference-visible | 0.9 |

### TitleOverlay

| 属性 | 值 | Source | Confidence |
|------|-----|--------|------------|
| 定位方式 | absolute | screenshot-estimated | 0.9 |
| Anchor | top-left | screenshot-estimated | 0.9 |
| bbox | x:22 y:98 w:250 h:58 | screenshot-estimated | 0.84 |
| 内容 | 未来医疗科技展台 / 360° 全景导览 | reference-visible | 0.88 |

### RegionGuidePanel

| 属性 | 值 | Source | Confidence |
|------|-----|--------|------------|
| 定位方式 | absolute | screenshot-estimated | 0.92 |
| Anchor | left | screenshot-estimated | 0.9 |
| bbox | x:22 y:188 w:214 h:370 | screenshot-estimated | 0.9 |
| 圆角 | 10-14px | screenshot-estimated | 0.78 |
| 背景 | semi-transparent dark panel | screenshot-estimated | 0.82 |
| Z-index | 14 | screenshot-inferred | 0.8 |

### OperationGuidePanel

| 属性 | 值 | Source | Confidence |
|------|-----|--------|------------|
| 定位方式 | absolute | screenshot-estimated | 0.92 |
| Anchor | left-bottom | screenshot-estimated | 0.88 |
| bbox | x:22 y:574 w:214 h:182 | screenshot-estimated | 0.88 |
| 内容 | 操作指南列表 | reference-visible | 0.88 |

### TopHintOverlay

| 属性 | 值 | Source | Confidence |
|------|-----|--------|------------|
| 定位方式 | absolute | screenshot-estimated | 0.9 |
| Anchor | top-center | screenshot-estimated | 0.86 |
| bbox | x:793 y:27 w:186 h:63 | screenshot-estimated | 0.84 |
| 内容 | 鼠标拖拽提示 | reference-visible | 0.86 |

### TopRightControls

| 属性 | 值 | Source | Confidence |
|------|-----|--------|------------|
| 定位方式 | absolute | screenshot-estimated | 0.92 |
| Anchor | top-right | screenshot-estimated | 0.9 |
| bbox | x:1561 y:24 w:190 h:68 | screenshot-estimated | 0.88 |
| 内容 | 全屏 / 音效 / 介绍 | reference-visible | 0.9 |

### HotspotMarkers

| 属性 | 值 | Source | Confidence |
|------|-----|--------|------------|
| 定位方式 | absolute markers | screenshot-estimated | 0.86 |
| 中心点 | multiple x/y positions | screenshot-estimated | 0.82 |
| 点击区域 | marker diameter + 8px padding | screenshot-inferred | 0.7 |
| 内容 | 编号 1-6 | reference-visible | 0.88 |

### ViewThumbnailCarousel

| 属性 | 值 | Source | Confidence |
|------|-----|--------|------------|
| 定位方式 | absolute | screenshot-estimated | 0.92 |
| Anchor | bottom-center | screenshot-estimated | 0.9 |
| bbox | x:313 y:767 w:1126 h:104 | screenshot-estimated | 0.9 |
| 内容 | 6 个视角缩略图卡片 | reference-visible | 0.9 |

---

## Rejected Layouts

| 假设 | 拒绝原因 |
|------|----------|
| flex 三栏布局 | 图中右侧没有独立信息面板，主体是全屏 raster scene |
| TabBar + 地图可视化 | 图中没有顶部 Tab，也没有地理/网络拓扑地图 |
| 底部状态栏 | 图中底部是视角缩略图导航，不是系统状态栏 |
