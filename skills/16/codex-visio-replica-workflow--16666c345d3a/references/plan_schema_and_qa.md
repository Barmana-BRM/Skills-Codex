# Visio JSON 计划和质量检查

当需要为 `scripts/create_visio_from_plan.ps1` 创建 JSON 计划时，读取本参考文件。

## 最小示例

```json
{
  "page": {
    "name": "系统架构复刻",
    "widthPx": 1440,
    "heightPx": 928,
    "scalePxPerInch": 100
  },
  "referenceImage": "C:/path/to/reference.jpg",
  "shapes": [
    {
      "type": "rect",
      "x1": 20,
      "y1": 90,
      "x2": 1420,
      "y2": 910,
      "text": "",
      "style": {
        "fill": "RGB(255,255,255)",
        "line": "RGB(88,103,150)",
        "weight": 1.4,
        "dash": true
      }
    },
    {
      "type": "text",
      "x1": 590,
      "y1": 35,
      "x2": 850,
      "y2": 75,
      "text": "系统架构图",
      "style": {
        "fontSize": 22,
        "textColor": "RGB(0,153,188)",
        "bold": true
      }
    },
    {
      "type": "line",
      "x1": 300,
      "y1": 200,
      "x2": 430,
      "y2": 200,
      "arrow": "end",
      "style": {
        "weight": 1.2
      }
    },
    {
      "type": "polyline",
      "points": [[300, 250], [300, 310], [430, 310]],
      "arrow": "end",
      "style": {
        "weight": 1.2
      }
    },
    {
      "type": "oval",
      "x1": 500,
      "y1": 220,
      "x2": 550,
      "y2": 270,
      "text": "API",
      "style": {
        "fill": "RGB(231,252,255)",
        "line": "RGB(35,188,211)",
        "fontSize": 8,
        "textColor": "RGB(34,139,155)"
      }
    }
  ]
}
```

## 图形字段

- `rect`：矩形，必须包含 `x1`、`y1`、`x2`、`y2`；可选 `text`、`style`。
- `text`：文本框，坐标同矩形，但无填充、无边框。
- `oval`：椭圆，必须包含外接矩形坐标；可选 `text`、`style`。
- `line`：直线，必须包含起点和终点；`arrow` 可用 `none`、`begin`、`end`、`both`。
- `polyline`：折线，必须包含 `points` 数组；默认只在最后一段加箭头。

坐标采用图片像素坐标：左上角为原点，x 向右增大，y 向下增大。

## 质量检查清单

- 页面比例是否匹配参考图。
- 外框和主要分区线是否先对齐。
- 中文标签是否出现难看的换行或溢出。
- 箭头方向是否与参考图一致。
- 虚线边框是否清晰，但不要比内容框更重。
- 预览文件是否能脱离 Visio 单独打开。
- `.vsdx` 是否由可编辑图形组成，而不是只粘贴了一张位图。
- 参考图是否放在独立页面，或与可编辑绘图明确分离。
