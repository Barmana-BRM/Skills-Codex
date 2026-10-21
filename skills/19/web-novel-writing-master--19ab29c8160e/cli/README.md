# 网文写作 CLI

把 网文写作 master skill 的认知 OS 物化成 bash 工具。
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
| `decision/topic-1.sh` | 数据 决策树 (2 条规则) |
| `decision/topic-2.sh` | 读者 决策树 (2 条规则) |
| `decision/topic-3.sh` | 爽点 决策树 (1 条规则) |
| `decision/topic-4.sh` | 平台 决策树 (2 条规则) |
| `decision/general-playbook.sh` | 通用 Playbook 决策树 (1 条规则) |
| `workflow/workflow-1.sh` | 选频道与流派 + 立意与核心设定（开书前定位与地基） SOP 走查 |
| `workflow/workflow-2.sh` | 人物与关系设计 + 大纲制作（可执行蓝图） SOP 走查 |
| `workflow/workflow-3.sh` | 黄金三章 / 开局（网文工艺最核心、与影视编剧差异最大的一环） SOP 走查 |
| `workflow/workflow-4.sh` | 签约与上架 + 日更连载（签约后的连载工程闭环） SOP 走查 |
| `workflow/workflow-5.sh` | 读者数据运营与救书（网文独有的即时反馈闭环） SOP 走查 |
| `workflow/ip.sh` | 完本与 IP 改编变现（短剧时代重写的下游工作流） SOP 走查 |

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
  --industry-cn "网文写作"
```
