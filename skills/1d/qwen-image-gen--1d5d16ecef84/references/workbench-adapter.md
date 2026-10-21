# 可选：离线工作台请求构建器

`scripts/prepare_workbench_request.py` 把完成的改写 JSON 转成一个工作台请求 JSON。它使用 Python 3 标准库，不联网、不调用语言模型或图像模型、不提交任务。

这是作者本地工作台的适配示例，**不是 Qwen 官方通用 API**。下面限制来自该协议：文生图每边 256–2048、32 的倍数；编辑只支持一个输入图，按参考比例输出约 1MP，不接收指定输出宽高。其他服务可以有不同限制。

在 `skills/qwen-image-gen` 目录运行：

```bash
python3 scripts/prepare_workbench_request.py rewrite.json --quality high --seed 0 --out request.json
python3 scripts/prepare_workbench_request.py edit.json --mode edit --reference reference.png --out edit-request.json
```

文生图输入示例：

```json
{"rewritten_prompt":"A single portrait photograph in a sunlit garden.","wh_ratio":"9:16"}
```

编辑输入示例：

```json
{"rewritten_prompt":"把图片中头巾改为红色，保留其形状和褶皱，其他内容不变。","wh_ratio":"","ratio_follow":"<image1>"}
```

9:16 在 `standard` 档映射为 864×1536，在 `high` 档为 1152×2048。`high` 是尺寸预设，不是保证质量提升的模型开关。显式画布用 `--width` 与 `--height` 覆盖，适合固定画布的 A/B 测试。

编辑请求嵌入原始参考图字节。生成的请求文件权限为 0600，已存在的文件不会被覆盖。含参考图的请求文件属于用户工作数据，不应提交到公共仓库。

CLI 的 `submitted:false` 明确表示尚未提交。脚本不检查图像模型是否运行，也不会自动连接任何服务器。调用方需按照自己的 API 完成鉴权、提交、轮询与下载。
