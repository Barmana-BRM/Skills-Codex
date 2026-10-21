# Amazon 店铺报表、订单与履约：工具路由

只定位并读取当前模式的工具说明。以下路由沿用原有能力映射，具体鉴权、额度、参数版本与可用性在执行时确认；不是新增接口或在线验证声明。

| 能力 | 路由类别 | 详细参数与边界 |
|---|---|---|
| Amazon 账户授权检查 | 官方账户连接或导出文件 | [详细路由](capabilities/amazon-account-auth/tool-routing.md) |
| Amazon 经营报表 | 官方账户连接或导出文件 | [详细路由](capabilities/amazon-account-report/tool-routing.md) |
| Amazon 订单核对 | 官方账户连接或导出文件 | [详细路由](capabilities/amazon-account-orders/tool-routing.md) |
| Amazon 外部履约 | 官方账户连接或导出文件 | [详细路由](capabilities/amazon-account-external-fulfillment/tool-routing.md) |
| Amazon 政策更新核对 | 公开网页或授权接口 | [详细路由](capabilities/amazon-policy-monitor/tool-routing.md) |
