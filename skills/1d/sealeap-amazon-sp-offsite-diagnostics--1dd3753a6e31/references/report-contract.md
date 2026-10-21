# 站内外报告核对契约

每份导出保留 account、marketplace、currency、report_type/version、start/end、timezone、attribution_window、generated_at 和成熟时间。列名按当前实际报表映射，未提供的媒体/创作者细分标记 UNAVAILABLE。

记录粒度至少包括 campaign、广告商品和报告实际支持的 site/placement/channel；只有来源明确允许时细分 publisher/creator。原始行、活动小计和总计分开，禁止把总计行再加进明细。

可加总：互斥且同范围的曝光、点击、花费及一致归因口径的订单/销售。
重算：CTR、CPC、订单/点击、ACOS 和渠道占比。
不可直接相加：比率、不同窗口转化、不同报告中的重复订单。

对账残差 = 活动总量 − 已确认互斥分区之和。只将其标为未分配残差；不把残差自动叫作达人、站外或无效流量。若分区重叠，停止求残差。

对照表保留前/后两个绝对值、差值、来源和成熟状态；不能只交付涨跌箭头。
