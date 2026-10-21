# 招聘与猎头 CLI

把 招聘与猎头 master skill 的认知 OS 物化成 bash 工具。
不替代 SKILL.md（思维顾问），是它的「执行端」：交互问询 → 应用 playbook / protocol → 输出结构化报告。

## 用法

所有脚本支持 `--help` / `--explain` / `--dry-run` / `--json` 四个标准 flag。

```bash
# 拿到新问题时, 按 N 个研究维度做功课
./protocol/agentic.sh

# 决策树评估 (基于 playbook)
./decision/evidence.sh
# SOP 走查 (workflow)
./workflow/intake.sh

# 看背后的心智模型 / playbook (不交互)
./protocol/agentic.sh --explain
```

## 脚本清单

| 脚本 | 作用 |
|------|------|
| `protocol/agentic.sh` | Agentic Protocol (7 维度) — 拿到新问题时按这一行的研究维度做功课 |
| `decision/evidence.sh` | Evidence 决策树 (8 条规则) |
| `decision/topic-2.sh` | 一个 决策树 (1 条规则) |
| `decision/topic-3.sh` | 岗位 决策树 (1 条规则) |
| `workflow/intake.sh` | intake 需求诊断会 SOP 走查 |
| `workflow/scorecard.sh` | 岗位画像与 scorecard SOP 走查 |
| `workflow/mapping.sh` | 渠道策略与人才地图 mapping SOP 走查 |
| `workflow/outreach.sh` | 主动触达 outreach SOP 走查 |
| `workflow/workflow-1.sh` | 简历筛选与电话初筛 SOP 走查 |
| `workflow/workflow-2.sh` | 面试环节设计与面试官校准 SOP 走查 |
| `workflow/workflow-3.sh` | 工作样本与技术评估 SOP 走查 |
| `workflow/reference-check.sh` | reference check 与背调 SOP 走查 |
| `workflow/offer.sh` | offer 设计与谈判 SOP 走查 |
| `workflow/counter-offer-no-show.sh` | counter-offer 与 no-show 防范 SOP 走查 |
| `workflow/workflow-4.sh` | 入职与早期留存复盘 SOP 走查 |
| `workflow/workflow-5.sh` | 招聘漏斗与数据复盘 SOP 走查 |
| `workflow/workflow-6.sh` | 岗位关闭 / 撤销 / 长期招不到的收尾 SOP 走查 |
| `workflow/bd.sh` | BD 与接单 SOP 走查 |
| `workflow/retained.sh` | 保留制 retained 的交付流程 SOP 走查 |
| `workflow/contingency.sh` | 成功付费 contingency 的作业节奏 SOP 走查 |
| `workflow/candidate-control.sh` | 候选人管理 candidate control SOP 走查 |
| `workflow/off-limits.sh` | off-limits 与职业道德 SOP 走查 |

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
  --industry-cn "招聘与猎头"
```
