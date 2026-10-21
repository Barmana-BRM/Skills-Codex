# 工具选择与能力边界

先检查当前 Agent 暴露的工具、已安装连接和同口径本地材料。只选择本任务需要的能力；下面是已核对的路由，执行参数以当前 schema 或 CLI 帮助为准。身份、市场、配额、计费与实际数据响应在执行时另行确认。

## 已有 CLI 直连

先使用 `command -v ecomi` 定位；若不在 PATH，从已配置项目的 `.venv/bin/ecomi` 定位，不自动重装或读取凭证内容。

先运行 `ecomi ssopen --help` 核对选项。工具安装和帮助可用只证明接口存在，不证明已登录、有配额或能访问目标数据。

已有卖家精灵登录态连接能满足任务时优先复用；所需方法不存在或登录态不可用时，使用已配置的开放平台 `ssopen` 或官方 MCP。两条通道的认证与字段不同，不能只替换 provider 名。

以下为已核对的开放平台 endpoint 键；使用 `ecomi ssopen --list` 与当前 endpoint 文档确认参数。通过 `--asin`、`--keyword`、`--marketplace`、`--body` 或 `--params` 传递当前 schema 要求的字段。

检查原始顶层业务状态；`ERR_NEED_RE_AUTHORIZED`、`ERR_NEED_RENEWAL_AUTHORIZED` 不能当作空数据成功。授权维护最多对同账户进行一次受支持的刷新与原请求重试；MCP 配额不足不能当可用兜底。

- `aba_research_weekly`：按当前 endpoint/method schema 填写业务输入。
- `aba_research_monthly`：按当前 endpoint/method schema 填写业务输入。
- `aba_research_trends`：按当前 endpoint/method schema 填写业务输入。

已授权调用仍需尊重样本和费用范围。只在当前工具确实覆盖相同市场、实体、时间与指标时换用其他提供方；不能保留原指标名称却悄悄替换成含义不同的数据。

## 本任务不能被替换掉的语义

排名数值下降才是排名提升；转化份额不是 CVR；不同周期不能直接相加；来源覆盖年限以实际数据为准。

接入检查只代表工具存在。新任务中必须根据真实返回记录成功、失败、空结果、字段缺失与数据时间；不得将本地格式校验标成在线业务验证。
