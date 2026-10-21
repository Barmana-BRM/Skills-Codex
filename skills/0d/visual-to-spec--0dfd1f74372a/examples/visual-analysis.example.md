# Visual Analysis

## 1. 全局构图

- **UI Type**: panorama-scene
- **UI Type Confidence**: 0.92
- **页面尺寸**: 1774px × 887px
- **宽高比**: 2:1
- **主视觉模型**: raster-scene-layer + absolute overlays
- **Source**: reference-visible
- **Confidence**: 0.92

### UI Type Rationale

- 截图中央为照片级/3D 展台场景，包含复杂光影、反射、设备和机器人，不能用普通 CSS 精确重建。
- UI 控件以浮层形式覆盖在全屏场景之上，包括左侧导览、顶部提示、右上控制组、底部视角缩略图。
- 可见 `360°` 与视角缩略图，符合全景/虚拟展台体验。

### Visible Element Inventory

| 元素 | bbox (px) | 视觉证据 | Source | Confidence |
|------|-----------|----------|--------|------------|
| SceneImageLayer | x:0 y:0 w:1774 h:887 | 全屏展厅、地面反射、展台主体 | reference-visible | 0.95 |
| BrandOverlay | x:22 y:24 w:210 h:52 | AETHEREAL HEALTH logo/text | reference-visible | 0.90 |
| TitleOverlay | x:22 y:98 w:250 h:58 | 未来医疗科技展台 / 360° 全景导览 | reference-visible | 0.88 |
| RegionGuidePanel | x:22 y:188 w:214 h:370 | 标题“展台区域导览” + 小地图 + 编号列表 | reference-visible | 0.90 |
| OperationGuidePanel | x:22 y:574 w:214 h:182 | 标题“操作指南” + 图标说明列表 | reference-visible | 0.88 |
| TopHintOverlay | x:793 y:27 w:186 h:63 | 鼠标图标 + “点击并拖动鼠标” | reference-visible | 0.86 |
| TopRightControls | x:1561 y:24 w:190 h:68 | 全屏 / 音效 / 介绍 三个图标按钮 | reference-visible | 0.90 |
| HotspotMarkers | multiple | 蓝色编号 1-6 圆形标记 | reference-visible | 0.86 |
| Drag360Indicator | x:843 y:664 w:122 h:73 | “360°”与拖拽提示 | reference-visible | 0.84 |
| ViewThumbnailCarousel | x:313 y:767 w:1126 h:104 | 底部 6 个视角缩略图卡片 | reference-visible | 0.90 |

### Rejected Assumptions

| 假设组件/结构 | 拒绝原因 | 影响 |
|---------------|----------|------|
| RightPanel | 截图右侧没有独立详情面板 bbox | 不得生成 RightPanel |
| TabBar | 截图顶部没有 Tab 导航 | 不得生成 TabBar |
| MapVisualization | 中央是展台场景，不是地理/网络拓扑地图 | 不得生成地图 SVG |
| StatusBar | 底部是视角缩略图导航，不是状态栏 | 不得生成系统状态栏 |
| Sidebar navigation | 左侧是浮层导览面板，不是全高应用侧栏 | 不得生成固定 Sidebar |

### Asset Strategy

| 资产/视觉层 | 实现方式 | 原因 | Source | Confidence |
|-------------|----------|------|--------|------------|
| 展台主视觉 | raster asset / panorama engine | 照片级 3D 展台、反射、设备、墙面 logo 不能由 CSS 精确复刻 | reference-visible | 0.95 |
| 热点编号 | HTML/CSS/SVG overlay | 蓝色圆形编号可独立复刻 | reference-visible | 0.86 |
| 左侧导览面板 | HTML/CSS overlay | 半透明面板、文字和图标可独立实现 | reference-visible | 0.88 |
| 底部缩略图 | raster thumbnails + HTML card frame | 缩略图内容来自场景截图，卡片边框可 CSS 实现 | reference-visible | 0.90 |

### 视觉区域

| 区域 | 边界框 | 层级 | 背景/实现方式 | Source | Confidence |
|------|--------|------|---------------|--------|------------|
| 主场景 | x:0 y:0 w:1774 h:887 | 主要 | raster scene | reference-visible | 0.95 |
| 左侧浮层组 | x:22 y:24 w:250 h:732 | 次要 | HTML/CSS overlay | reference-visible | 0.88 |
| 顶部浮层组 | x:793 y:24 w:958 h:68 | 次要 | HTML/CSS overlay | reference-visible | 0.86 |
| 中央热点层 | multiple | 交互 | HTML/CSS/SVG overlay | reference-visible | 0.84 |
| 底部缩略图导航 | x:313 y:767 w:1126 h:104 | 次要 | image thumbnails + overlay cards | reference-visible | 0.90 |

## 2. 颜色系统

| Token 名 | Hex | 角色 | 出现位置 | Source | Confidence |
|----------|-----|------|----------|--------|------------|
| overlay-panel | #1E1F22CC | surface | 左侧面板、顶部提示、右上工具组 | screenshot-estimated | 0.76 |
| overlay-border | #FFFFFF33 | border | 浮层边框 | screenshot-estimated | 0.68 |
| hotspot-blue | #2F88FF | primary | 编号热点、active 缩略图边框 | screenshot-estimated | 0.78 |
| glow-cyan | #6FE6FF | accent | 展台灯带、标题蓝光 | screenshot-estimated | 0.72 |
| text-primary | #FFFFFF | text-primary | 品牌、面板标题、控件文字 | screenshot-estimated | 0.90 |
| text-cyan | #9DEEFF | text-primary | 左上中文标题 | screenshot-estimated | 0.78 |

### 估算对比度

| 前景 | 背景 | 估算比值 | 备注 |
|------|------|----------|------|
| text-primary | overlay-panel | ~12:1 | estimated-contrast |
| text-cyan | dark scene | ~10:1 | estimated-contrast |

## 3. 字体排印

| 语义角色 | 字体族 | 字号 | 字重 | 行高 | 颜色 Token | Source | Confidence |
|----------|--------|------|------|------|-----------|--------|------------|
| brand | Sans-serif / display | 24px | 700 | 1.1 | text-primary | screenshot-estimated | 0.65 |
| h1 | PingFang SC / system sans | 24px | 700 | 1.25 | text-cyan | screenshot-estimated | 0.70 |
| panel-title | PingFang SC / system sans | 15px | 600 | 1.3 | text-primary | screenshot-estimated | 0.72 |
| body | PingFang SC / system sans | 14px | 400 | 1.4 | text-primary | screenshot-estimated | 0.68 |
| thumbnail-label | PingFang SC / system sans | 14px | 500 | 1.2 | text-primary | screenshot-estimated | 0.68 |

## 4. 间距系统

- **基础单位**: 4px
- **内边距模式**: 浮层面板 12-16px
- **外边距/浮层边距模式**: 左侧边距约 22px，顶部边距约 24px，底部缩略图区距底约 16px
- **网格/坐标系统**: absolute overlay coordinates

| 间距 Token | 值 | 用途 | Source | Confidence |
|-----------|-----|------|--------|------------|
| overlay-edge-x | 22px | 左侧浮层距画布左边 | screenshot-estimated | 0.82 |
| overlay-top | 24px | 顶部浮层距画布上边 | screenshot-estimated | 0.80 |
| panel-padding | 14px | 面板内边距 | screenshot-estimated | 0.70 |
| thumbnail-gap | 14px | 底部缩略图卡片间距 | screenshot-estimated | 0.68 |
