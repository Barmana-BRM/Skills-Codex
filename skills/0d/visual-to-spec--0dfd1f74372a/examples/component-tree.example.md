# Component Tree

## UI Type

- **值**: panorama-scene
- **组件树模型**: raster-scene-with-overlays

## 树形结构

```text
PanoramaExperience [source: inferred-implementation, confidence: 0.92]
├── SceneImageLayer [source: reference-visible, confidence: 0.95]
├── OverlayLayer [source: inferred-implementation, confidence: 0.9]
│   ├── BrandOverlay [source: reference-visible, confidence: 0.9]
│   │   ├── LogoMark [source: reference-visible, confidence: 0.86]
│   │   └── BrandText [source: reference-visible, confidence: 0.9]
│   ├── TitleOverlay [source: reference-visible, confidence: 0.88]
│   ├── RegionGuidePanel [source: reference-visible, confidence: 0.9]
│   │   ├── MiniMapPreview [source: reference-visible, confidence: 0.82]
│   │   └── RegionList [source: reference-visible, confidence: 0.88]
│   ├── OperationGuidePanel [source: reference-visible, confidence: 0.88]
│   ├── TopHintOverlay [source: reference-visible, confidence: 0.86]
│   ├── TopRightControls [source: reference-visible, confidence: 0.9]
│   │   ├── IconControl [source: reference-visible, confidence: 0.9]
│   │   ├── IconControl [source: reference-visible, confidence: 0.9]
│   │   └── IconControl [source: reference-visible, confidence: 0.9]
│   ├── HotspotMarkers [source: reference-visible, confidence: 0.86]
│   │   └── HotspotMarker (multiple) [source: reference-visible, confidence: 0.86]
│   ├── Drag360Indicator [source: reference-visible, confidence: 0.84]
│   └── ViewThumbnailCarousel [source: reference-visible, confidence: 0.9]
│       └── ViewThumbnail (multiple) [source: reference-visible, confidence: 0.88]
└── InteractionLayer [source: inferred-implementation, confidence: 0.8]
```

## 组件详情

### PanoramaExperience

- **Source**: inferred-implementation
- **bbox**: full viewport
- **尺寸**: 100vw × 100vh
- **背景**: color.background-page
- **内容类型**: 顶层体验容器
- **Confidence**: 0.92
- **Notes**: 实现性 wrapper，截图中无直接对应的视觉元素。

### SceneImageLayer

- **Source**: reference-visible
- **bbox**: x:0, y:0, w:100%, h:100%
- **尺寸**: cover viewport, preserve screenshot aspect-ratio
- **背景**: raster asset
- **内容类型**: 图片/全景/3D 场景主视觉
- **Confidence**: 0.95
- **Notes**: 照片级展台、地面反射、复杂光影、3D 物体必须作为 raster asset 或真实 3D/全景资源，不应由 CSS/SVG 重建。

### RegionGuidePanel

- **Source**: reference-visible
- **bbox**: x:22px, y:188px, w:214px, h:370px
- **背景**: color.panel-glass
- **边框**: 1px color.border-glass
- **圆角**: borderRadius.lg
- **内容类型**: 浮层面板（文本 + 缩略图 + 编号列表）
- **Confidence**: 0.9

### HotspotMarker

- **Source**: reference-visible
- **bbox**: center x/y + diameter
- **背景**: color.hotspot-blue
- **边框**: 2px color.text-primary
- **圆角**: circle
- **内容类型**: 交互热点
- **Confidence**: 0.86

### ViewThumbnailCarousel

- **Source**: reference-visible
- **bbox**: x:313px, y:767px, w:1126px, h:104px
- **背景**: transparent with thumbnail cards
- **边框**: active item uses color.hotspot-blue
- **圆角**: borderRadius.md
- **内容类型**: 底部视角缩略图导航
- **Confidence**: 0.9

---

## Dashboard 分流示例（仅当 uiType = application-dashboard）

```text
AppShell [source: inferred-implementation]
├── Sidebar [source: reference-visible]
├── MainContent [source: inferred-implementation]
└── RightPanel [source: reference-visible]
```

只有截图中确实存在独立侧栏、主内容区、右侧面板时，才能使用该骨架。否则应写入 Rejected Assumptions。
