# 报告数据包

顶层必填 `title`、`marketplace`、`data_period`、非空 `sections`；同时提供 `decision`（GO/HOLD/NO-GO）、`critical_gaps`、`evidence`。

- sections 每项有 `title`、`summary`、`rows`（对象数组）、`evidence_ids`（证据 ID 数组）、`limitations`。
- 每行保留真实数值和 null；不同字段来自不同证据时，用行内 `field_evidence` 对象记录对应 ID/原始字段，也可按证据拆行。
- evidence 每项有唯一 `id`、`source`、`collected_at`、`data_period`、`marketplace`、`label`。label 为 FACT / ESTIMATE / ASSUMPTION / UNKNOWN；可加本地原始文件或公开 URL。
- 原始请求参数保存在私有证据仓；不要把认证头、Cookie、Token 或个人联系方式放进 payload。

示例结构（以下明确为合成样例，不能用于市场结论）：

```json
{
  "title": "合成样例研究",
  "marketplace": "US",
  "data_period": "SYNTHETIC",
  "decision": "HOLD",
  "critical_gaps": ["只有合成示例，没有真实市场证据"],
  "evidence": [{"id":"E1","source":"SYNTHETIC","collected_at":"2026-09-14","data_period":"SYNTHETIC","marketplace":"US","label":"ASSUMPTION"}],
  "sections": [{"title":"商品样本","summary":"演示字段，不构成建议。","evidence_ids":["E1"],"rows":[{"商品":"样例商品","价格":null}],"limitations":["未采集市场数据"]}]
}
```

脚本在证据缺失、错误引用、站点不匹配或 critical_gaps 非空时输出 HOLD；没有缺口时仅保留输入的判断，不自动产生 GO。每个输出目录须为新目录或空目录。
