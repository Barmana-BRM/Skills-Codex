# LLM agent 基础设施 CLI

把 LLM agent 基础设施 master skill 的认知 OS 物化成 bash 工具。
不替代 SKILL.md（思维顾问），是它的「执行端」：交互问询 → 应用 playbook / protocol → 输出结构化报告。

## 用法

所有脚本支持 `--help` / `--explain` / `--dry-run` / `--json` 四个标准 flag。

```bash
# 拿到新问题时, 按 N 个研究维度做功课
./protocol/agentic.sh

# 决策树评估 (基于 playbook)
./decision/agent.sh
# SOP 走查 (workflow)
./workflow/build-production-ready-rag-agent.sh

# 看背后的心智模型 / playbook (不交互)
./protocol/agentic.sh --explain
```

## 脚本清单

| 脚本 | 作用 |
|------|------|
| `protocol/agentic.sh` | Agentic Protocol (5 维度) — 拿到新问题时按这一行的研究维度做功课 |
| `decision/agent.sh` | Agent 决策树 (4 条规则) |
| `decision/eval.sh` | Eval 决策树 (2 条规则) |
| `decision/production.sh` | Production 决策树 (1 条规则) |
| `workflow/build-production-ready-rag-agent.sh` | Build production-ready RAG agent SOP 走查 |
| `workflow/add-observability-eval-to-existi.sh` | Add observability + eval to existing agent SOP 走查 |
| `workflow/audit-fix-failing-agent-in-produ.sh` | Audit + fix failing agent in production SOP 走查 |

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
  --industry-cn "LLM agent 基础设施"
```
