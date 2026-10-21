# 卖家精灵工具路由

已核对 Ecomi 官方开放平台适配器 `sellersprite_open` 的端点定义：

- `market_research`：`POST /v1/market/research`。

发现命令：`ecomi ssopen --help`、`ecomi ssopen --list`。查询使用 `--endpoint`，站点用 `--marketplace`，ASIN 用 `--asin`；额外 POST 字段放 `--body` JSON，GET 字段放 `--params` JSON。业务 body 字段必须再对照当前提供方文档；端点表只证明方法和路径存在。

`sellersprite_open` 与 `sellersprite` 登录态适配器是不同通路，参数不可直接互换。若使用已有登录态通路，逐项检查能力与原始业务状态；授权或配额错误不视为成功。不新增账户、不复制 Cookie，也不在本任务中设置凭据。

## 实际执行

先复用范围匹配的授权导出或历史结果，再选择当前可用连接器。下列映射只验证了接口声明或本地代码，未验证在线鉴权、配额和真实返回。运行时重新查看工具 schema；存在同名工具也不等于字段、窗口、分页语义相同。

保留原始响应与业务状态，工具错误不得转成空数组。未提供的筛选器只可在已取得的样本上筛选，并披露样本边界。没有可用通路时交付缺口和可用数据分析，不编造接口或用其他数据源冒充指定提供方。
