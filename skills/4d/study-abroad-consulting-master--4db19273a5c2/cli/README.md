# 留学咨询规划 CLI

把 留学咨询规划 master skill 的认知 OS 物化成 bash 工具。
不替代 SKILL.md（思维顾问），是它的「执行端」：交互问询 → 应用 playbook / protocol → 输出结构化报告。

## 用法

所有脚本支持 `--help` / `--explain` / `--dry-run` / `--json` 四个标准 flag。

```bash
# 拿到新问题时, 按 N 个研究维度做功课
./protocol/agentic.sh

# 决策树评估 (基于 playbook)
./decision/topic-1.sh
# SOP 走查 (workflow)
./workflow/workflow-1.sh

# 看背后的心智模型 / playbook (不交互)
./protocol/agentic.sh --explain
```

## 脚本清单

| 脚本 | 作用 |
|------|------|
| `protocol/agentic.sh` | Agentic Protocol (7 维度) — 拿到新问题时按这一行的研究维度做功课 |
| `decision/topic-1.sh` | �� 决策树 (6 条规则) |
| `decision/topic-2.sh` | 学生 决策树 (2 条规则) |
| `decision/topic-3.sh` | 案例 决策树 (2 条规则) |
| `workflow/workflow-1.sh` | 初始咨询与需求诊断 SOP 走查 |
| `workflow/workflow-2.sh` | 选校策略制定 SOP 走查 |
| `workflow/workflow-3.sh` | 背景提升规划 SOP 走查 |
| `workflow/workflow-4.sh` | 文书创作流程 SOP 走查 |
| `workflow/workflow-5.sh` | 申请提交管理 SOP 走查 |
| `workflow/workflow-6.sh` | 标化考试策略 SOP 走查 |
| `workflow/workflow-7.sh` | 签证准备 SOP 走查 |
| `workflow/workflow-8.sh` | 录取后决策 SOP 走查 |
| `workflow/workflow-9.sh` | 行前准备与适应 SOP 走查 |
| `workflow/workflow-10.sh` | 全周期项目管理 SOP 走查 |

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
  --industry-cn "留学咨询规划"
```
