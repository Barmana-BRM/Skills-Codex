# 快照输入

输入 JSON 为记录数组。每条含：

- `own_asin`、`marketplace`、`asin`、`source`、`data_mode`（REAL/SYNTHETIC）。ASIN 为十位大写字母或数字，不要求 B0 前缀。
- `captured_at`：带时区的 ISO 8601 时间；`evidence_id`、`verification_reason`。
- `status`：verified/candidate/rejected/error；verified 还必须有与 asin 一致的 `detail_asin` 和 `relevance: matched`。匹配判断必须在导入前有真实证据，不由脚本替代。
- `metrics`：按字段命名的对象，如 price/title/rating/review_count/bsr/keyword_rank。每项含 `value`、`unit`、`period`、`label`、`evidence_id`。

价格 unit 用货币代码，排名需另行保留关键词和位置类型到字段名或证据中；时间快照 period 用 `snapshot`，某月销量等周期指标用精确月份，避免被当成同基准的价格变化。value 只能为标量或 null。

同一来源、站点、商品、模式和时点重复导入幂等；键相同但内容冲突会回滚整批。不同模式和来源分别比较；缺值、币种、期别或证据标签不一致时只展示前后值，不计算差额。

记录中不得包含 Cookie、认证头、API Key 或个人联系方式。这里只保存业务字段和证据引用；原始响应另存用户授权的私有数据仓。
