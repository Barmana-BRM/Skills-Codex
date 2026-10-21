# 科研方法与论文发表 CLI

把 科研方法与论文发表 master skill 的认知 OS 物化成 bash 工具。
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
| `decision/topic-1.sh` | 哪一 决策树 (3 条规则) |
| `decision/general-playbook.sh` | 通用 Playbook 决策树 (7 条规则) |
| `workflow/workflow-1.sh` | 选题与可行性判断 (Decay risk: low) SOP 走查 |
| `workflow/workflow-2.sh` | 文献综述与系统综述 (Decay risk: medium) SOP 走查 |
| `workflow/workflow-3.sh` | 研究设计与预注册 (Decay risk: medium) SOP 走查 |
| `workflow/workflow-4.sh` | 伦理审批与数据合规 (Decay risk: high) SOP 走查 |
| `workflow/workflow-5.sh` | 数据采集与数据管理 (Decay risk: medium) SOP 走查 |
| `workflow/workflow-6.sh` | 分析与稳健性检验 (Decay risk: low) SOP 走查 |
| `workflow/workflow-7.sh` | 图表与结果呈现 (Decay risk: low) SOP 走查 |
| `workflow/workflow-8.sh` | 论文写作 (Decay risk: low) SOP 走查 |
| `workflow/workflow-9.sh` | 期刊选择与投稿 (Decay risk: high) SOP 走查 |
| `workflow/workflow-10.sh` | 同行评审应对 (Decay risk: medium) SOP 走查 |
| `workflow/workflow-11.sh` | 基金申请 (Decay risk: high) SOP 走查 |
| `workflow/workflow-12.sh` | 实验室协作与署名协商 (Decay risk: medium) SOP 走查 |
| `workflow/workflow-13.sh` | 出错之后：更正、关注声明、撤稿与举报 (Decay risk: medium) SOP 走查 |
| `workflow/workflow-14.sh` | 发表之后：归档、传播与被质疑的应对 (Decay risk: medium) SOP 走查 |

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
  --industry-cn "科研方法与论文发表"
```
