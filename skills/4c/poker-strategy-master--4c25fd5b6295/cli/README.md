# 德州扑克策略 CLI

把 德州扑克策略 master skill 的认知 OS 物化成 bash 工具。
不替代 SKILL.md（思维顾问），是它的「执行端」：交互问询 → 应用 playbook / protocol → 输出结构化报告。

## 用法

所有脚本支持 `--help` / `--explain` / `--dry-run` / `--json` 四个标准 flag。

```bash
# 拿到新问题时, 按 N 个研究维度做功课
./protocol/agentic.sh

# 决策树评估 (基于 playbook)
./decision/topic-1.sh
# SOP 走查 (workflow)
./workflow/solver-workflow-sim-node-lock-he.sh

# 看背后的心智模型 / playbook (不交互)
./protocol/agentic.sh --explain
```

## 脚本清单

| 脚本 | 作用 |
|------|------|
| `protocol/agentic.sh` | Agentic Protocol (7 维度) — 拿到新问题时按这一行的研究维度做功课 |
| `decision/topic-1.sh` | 对手 决策树 (2 条规则) |
| `decision/solver.sh` | Solver 决策树 (3 条规则) |
| `decision/topic-3.sh` | 偏离 决策树 (1 条规则) |
| `decision/topic-4.sh` | 决策 决策树 (1 条规则) |
| `decision/icm.sh` | Icm 决策树 (1 条规则) |
| `workflow/solver-workflow-sim-node-lock-he.sh` | Solver 研究 workflow（建翻前范围 → 跑 sim → 读节点/频率 → node-lock 剥削 → 抽象成 heuristic） SOP 走查 |
| `workflow/hand-history-review-solver-gto.sh` | 牌局复盘 / hand history review（标记疑难手 → 数据库/solver 比对 → 找偏离 GTO 的漏洞） SOP 走查 |
| `workflow/leak-finding-via-hud-leak-filter.sh` | Leak finding via HUD+数据库 / 自动 leak 报告（filter spot → 对比 GTO baseline → 定位高频亏损点 → 针对性修补） SOP 走查 |
| `workflow/game-table-site-selection-bankro.sh` | 赛前准备：game/table/site selection + bankroll check（开打前的元决策） SOP 走查 |
| `workflow/sop-bankroll.sh` | 资金管理 / 升降级 SOP（bankroll 规则、何时升降级、方差缓冲） SOP 走查 |
| `workflow/tilt-routine.sh` | 心态 / tilt 管理 routine（赛前-赛中-赛后三段） SOP 走查 |

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
  --industry-cn "德州扑克策略"
```
