# B2B 大客户销售 CLI

把 B2B 大客户销售 master skill 的认知 OS 物化成 bash 工具。
不替代 SKILL.md（思维顾问），是它的「执行端」：交互问询 → 应用 playbook / protocol → 输出结构化报告。

## 用法

所有脚本支持 `--help` / `--explain` / `--dry-run` / `--json` 四个标准 flag。

```bash
# 拿到新问题时, 按 N 个研究维度做功课
./protocol/agentic.sh

# 决策树评估 (基于 playbook)
./decision/topic-1.sh
# SOP 走查 (workflow)
./workflow/run-a-complete-discovery-call.sh

# 看背后的心智模型 / playbook (不交互)
./protocol/agentic.sh --explain
```

## 脚本清单

| 脚本 | 作用 |
|------|------|
| `protocol/agentic.sh` | Agentic Protocol (6 维度) — 拿到新问题时按这一行的研究维度做功课 |
| `decision/topic-1.sh` | —— 决策树 (5 条规则) |
| `decision/topic-2.sh` | 决策 决策树 (1 条规则) |
| `decision/deal.sh` | Deal 决策树 (2 条规则) |
| `decision/general-playbook.sh` | 通用 Playbook 决策树 (1 条规则) |
| `workflow/run-a-complete-discovery-call.sh` | Run a complete discovery call（跑一个完整的需求挖掘电话） SOP 走查 |
| `workflow/qualify-disqualify-an-opportunit.sh` | Qualify / disqualify an opportunity with MEDDPICC（用 MEDDPICC 资格审查一个机会） SOP 走查 |
| `workflow/build-an-outbound-prospecting-se.sh` | Build an outbound prospecting sequence from 0（从 0 建立一个外呼开发序列） SOP 走查 |
| `workflow/manage-a-poc-technical-validatio.sh` | Manage a POC / technical validation（管理一次技术验证 / POC） SOP 走查 |
| `workflow/build-sell-a-business-case-to-th.sh` | Build & sell a business case to the economic buyer（构建业务价值论证并卖给经济决策人） SOP 走查 |
| `workflow/drive-a-deal-to-close-with-a-mut.sh` | Drive a deal to close with a Mutual Action Plan（用双向行动计划驱动成交） SOP 走查 |
| `workflow/forecast-a-quarter-rep-side.sh` | Forecast a quarter (rep side)（预测一个季度——销售个人侧） SOP 走查 |
| `workflow/negotiate-with-procurement.sh` | Negotiate with procurement（与采购对线 / 谈判） SOP 走查 |
| `workflow/account-planning-land-and-expand.sh` | Account planning / land-and-expand（客户计划 / 落地后扩张） SOP 走查 |
| `workflow/run-a-pipeline-deal-review-manag.sh` | Run a pipeline / deal review (manager side)（运营 pipeline / deal review——管理者侧） SOP 走查 |
| `workflow/multithread-the-buying-committee.sh` | Multithread the buying committee（多线程触达买方委员会） SOP 走查 |

## 设计与生成

CLI 子树由 `tools/cli_writer.py` 自动从 `references/synthesis.md` (Section 2 Playbook + Section 9 Agentic Protocol) 和 `references/research/03-workflows.md` 生成。

完整 spec 在 master-skill 仓库 `references/cli-spec.md`。

## 重新生成

如果 synthesis.md 或 03-workflows.md 更新了, 重跑:

```bash
python3 <master-skill>/tools/cli_writer.py emit \
  --skill-dir <this-skill-dir> \
  --synthesis references/synthesis.md \
  --workflows references/research/03-workflows.md \
  --industry-cn "B2B 大客户销售"
```
