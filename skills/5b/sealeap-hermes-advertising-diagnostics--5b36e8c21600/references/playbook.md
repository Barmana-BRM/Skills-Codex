# 跨境广告诊断与受控实验执行手册

## 指标口径

| 指标 | 定义 | 必须对齐 |
|---|---|---|
| CTR | clicks / impressions | 同一投放范围与日期 |
| CPC | spend / clicks | 币种与有效点击 |
| 广告订单 CVR | attributed_orders / clicks | 广告类型、归因窗口和报告定义 |
| ACOS | spend / attributed_sales | 同一广告销售基数与成熟窗口 |
| TACOS | spend / total_sales | 同一店铺/商品范围、币种和可解释日期 |

订单数、售出件数、访客数不能互换。跨广告类型的归因重叠可能使广告销售不可直接相加；没有统一去重口径时分别展示。自然销售不能机械地用总销售减广告销售推算。

广告前单位贡献 = 一致收入口径 − 采购/物流/履约/佣金/税费/退货等非广告变动成本。对应盈亏平衡 ACOS = 该单位贡献 / 与广告销售一致的单位收入；混合商品时需要按收入贡献加权，并披露缺失成本。

## 搜索词与否词

先排除不相关或不允许的查询。相关但暂未成交的词须检查点击样本、归因成熟度、库存与详情页问题。每个否定候选保留实际搜索词、匹配范围、证据与可能损失；迁词后不自动否定所有来源词。

## 实验记录

`experiment_id, account, marketplace, object_id, hypothesis, primary_variable, baseline_window, treatment, primary_metric, guardrails, attribution_maturity, budget_cap, stop_condition, rollback_value, authorization_scope, execution_state`

无对照实验的前后变化只能作提示；同期价格、促销、节日和库存变化单列。样本不足时继续观察或 HOLD，不输出显著增长结论。

## 促销与站外广告

评估优惠、活动和站外获客时计入折扣、活动费、创作者佣金与履约影响；自然销售与广告归因不要重复算收益。不同平台的 ROAS 不能在窗口和收入口径不同的情况下直接排名。
