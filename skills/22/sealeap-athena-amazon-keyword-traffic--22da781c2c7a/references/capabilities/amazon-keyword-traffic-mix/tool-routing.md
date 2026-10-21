# 工具选择与能力边界

先检查当前 Agent 暴露的工具、已安装连接和同口径本地材料。只选择本任务需要的能力；下面是已核对的路由，执行参数以当前 schema 或 CLI 帮助为准。身份、市场、配额、计费与实际数据响应在执行时另行确认。

## 直接 MCP 路由

使用当前可用的 Sorftime MCP 工具。按工具名定位并读取完整输入 schema；不要把旧接口的参数名直接传给替代工具。显式填写目标市场，市场枚举以当前 schema 为准。

### `keyword_search_results`

- 当前会话工具标识：`mcp__sorftime_server__keyword_search_results`。
- schema 必填字段：`keyword`。
- 可选字段包括：`keyword_support_site`、`page`、`position_type`。

### `product_traffic_terms`

- 当前会话工具标识：`mcp__sorftime_server__product_traffic_terms`。
- schema 必填字段：`asin`。
- 可选字段包括：`amz_site`、`page`。

### `competitor_product_keywords`

- 当前会话工具标识：`mcp__sorftime_server__competitor_product_keywords`。
- schema 必填字段：`asin`。
- 可选字段包括：`keyword_support_site`、`page`。

优先使用现有 MCP；宿主未暴露时，可在已有 Ecomi 安装中通过 `ecomi sorftime --help` 检查 CLI，再用 `--describe <工具名>` 读取当前参数。没有连接时交付可执行查询计划或处理用户导出数据，不宣称已取到实时结果。

## 本任务不能被替换掉的语义

当前替代工具的自然曝光不能补出 SP/SB/SBV 推荐位；商品级评分不冒充关键词级评分。

接入检查只代表工具存在。新任务中必须根据真实返回记录成功、失败、空结果、字段缺失与数据时间；不得将本地格式校验标成在线业务验证。
