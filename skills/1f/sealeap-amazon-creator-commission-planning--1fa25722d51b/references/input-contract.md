# 加佣测算输入

示例为合成情景，不是实际商品报价或账户规则。全部金额按同一可售单位和币种填写。

scope：marketplace、currency、asin。model 固定 sales_commission；CPC 不受支持。
cost_currency 和 revenue_currency 必须显式匹配 scope.currency。

必填金额：net_unit_revenue、commission_base_per_unit、product_unit_cost、platform_fee_per_unit、fulfillment_fee_per_unit、other_variable_cost_per_unit、expected_return_loss_per_unit、target_unit_contribution、fixed_campaign_cost。
另填 selected_commission_rate（0–1 小数比例，例如 0.10）和 planned_units（非负整数）。

net_unit_revenue 是采用一致税费/折扣口径的单位净收入；commission_base_per_unit 来自计划的真实计佣口径，不能因为净收入相同就默认为同一字段。退货损失用有来源的单位期望成本，不再在 other_variable_cost_per_unit 重复扣除。fixed_campaign_cost 包含一次性样品/运费/稿酬等未计入单位成本的费用。

## 输出

单位贡献 = 净收入 − 单位成本合计 − 计佣基数 × 加佣比例。
目标允许比例 = (加佣前单位贡献 − 目标单位贡献) / 计佣基数，限制在 0–1；目标在零佣金时也不可实现则为 null。
固定成本回收数量 = 向上取整(固定成本 / 单位贡献)，单位贡献非正时为 null。
计划贡献 = 单位贡献 × 计划销量 − 固定成本。

贡献利润没有扣完整固定运营开支，不冒称企业净利润；佣金支出不是全部首单现金需求。预算最低值、资格、真实结算调整及增量效果不由脚本证明。null 为缺失，0 只用于明确已知零成本。

stdout JSON 的 PASS 仅表示计算完成；meets_target_contribution 单独表达方案是否达标。退出码 2=HOLD，1=无效。
