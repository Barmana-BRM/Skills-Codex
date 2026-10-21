# 浏览器运行时与操作手册

## 选择运行时

| 可用能力 | 执行方式 |
|---|---|
| 环境内浏览器工具/MCP | 阅读实时工具 schema，使用 navigation/snapshot/action 等当前能力 |
| Playwright 已安装 | 读取所用版本文档，创建任务专用 context，定位页面可见语义元素 |
| browser-use CLI | 先读取本地 `--help`，按其声明区分新旧接口 |
| 均不可用 | 输出 HOLD 与缺少的能力；可对已有 HTML/导出离线分析，但不宣称完成浏览器验证 |

安装不是页面采集的默认前置动作；已有工具满足任务时直接使用。用户要求安装时按当前官方说明执行，并核对实际版本。

## 当前 Python helper 接口

上游 [CLI 实现](https://github.com/browser-use/browser-use/blob/main/browser_use/cli.py) 在 2026-09-13 核查时使用 Python helper 入口，并为多条旧式子命令返回迁移提示。这是版本核对线索，不是对所有本地版本的保证。

仅在当前 `--help` 明确支持下列 helper 时使用此最小只读示例：

```bash
browser-use <<'PY'
new_tab("https://example.com")
print(page_info())
PY
```

下一步读取页面结果后再选择交互或截图操作。具体截图返回类型与保存方式以当前帮助/schema 为准，不假设 base64、文件路径或 bytes 可以互换。

## 旧式 CLI 的兼容路径

只有实际帮助列出 `open`、`state` 和 `--session` 时，才可使用：

```bash
browser-use --session hermes-research open https://example.com
browser-use --session hermes-research state
```

后续每条命令保持相同会话标识，并重新读取 state。不要将上例中的历史语法写入不支持它的版本。若本地版本只有默认会话且已被他人使用，改用任务专用浏览器上下文，不能接管或重启其他任务。

## 表单与恢复

填写前确认字段与数据来源；填写后检查可见值。提交需要用户授权覆盖具体外部动作。提交超时后先检索订单/消息/变更状态，不能机械再次点击。

元素丢失先重新观察页面；只读网络失败可按有限次数重试并记录最终原因。禁止用“失败就 close --all”的通用恢复方式。

## 高级模式

需要 CDP、设备模拟或网络观察时查当前公开 API。不要使用旧版 `browser._session`、`browser._run` 私有属性配方，也不要为了抓取商品信息导出整站 Cookie 或抓取无关网络响应。

云浏览器、隧道或账户注册只有在本任务明确需要且用户授权覆盖数据和费用时采用；不自动同步所有 profile、开放本地服务或生成账户认领链接。
