# 跨境收款、汇率与现金流执行手册

## 汇率与费用

`converted_amount = original_amount × target_currency_per_source_currency`。

已经使用净到账金额时，不再次扣除包含其中的兑换点差或交易费。分别记录 `quoted_rate, effective_rate, rate_timestamp, fee_base, percentage_fee, fixed_fee, refunds, reserves`。

只有计费基数相同，费率才可相加。退款是否退回原手续费、拒付费是否另计，依合同逐项列出。

## 现金流表

`period_start, opening_available_cash, settlements_received, other_confirmed_inflows, deposits_paid, balances_paid, freight_paid, ads_paid, tax_paid, refunds_paid, other_outflows, closing_available_cash, restricted_cash, evidence_ids`

`closing_available_cash = opening_available_cash + confirmed_inflows - cash_outflows`。期末余额滚入下一期；销售额、应收、保证金和现钞各保留独立列。

## 三种情景

基准、回款延迟、成本/汇率恶化。情景幅度由历史波动或用户假设指定并标记 ASSUMPTION，不能伪装成概率预测。

每种情景列出最大资金缺口、最早缺口日期、最低安全余额和可实施措施。采购延后、分批交付、加急运费与销售损失分别评价。

## 定价

从商品贡献目标倒算价格范围，再比较目标市场可接受性。仅做汇率折算无法推导最终售价；税费、支付费、物流和本地竞争都需加入。
