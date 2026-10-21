# 公务员考试培训 CLI

把 公务员考试培训 master skill 的认知 OS 物化成 bash 工具。
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
| `decision/topic-1.sh` | 岗位 决策树 (2 条规则) |
| `decision/topic-2.sh` | 分析 决策树 (2 条规则) |
| `decision/topic-3.sh` | 模块 决策树 (2 条规则) |
| `decision/topic-4.sh` | 课程 决策树 (1 条规则) |
| `decision/general-playbook.sh` | 通用 Playbook 决策树 (3 条规则) |
| `workflow/workflow-1.sh` | 考生备考全流程 (报名 → 笔试 → 面试 → 上岸) SOP 走查 |
| `workflow/5-120-135.sh` | 行测备考工作流 (5 模块学习顺序/时间分配/120 分钟 135 题策略) SOP 走查 |
| `workflow/workflow-2.sh` | 申论备考工作流 (材料阅读 → 要点提取 → 题型框架 → 大作文 → 时政积累) SOP 走查 |
| `workflow/workflow-3.sh` | 面试备考工作流 (结构化面试 → 题型 → 框架 → 对练) SOP 走查 |
| `workflow/workflow-4.sh` | 培训机构课程设计工作流 (教研 → 课件 → 试讲 → 迭代) SOP 走查 |
| `workflow/workflow-5.sh` | 模考组织工作流 (出题 → 组卷 → 考试 → 评分 → 数据分析) SOP 走查 |
| `workflow/workflow-6.sh` | 协议班运营工作流 (招生 → 授课 → 退费/录取) SOP 走查 |
| `workflow/ip-b.sh` | 名师 IP 打造工作流 (教研 → B站/抖音 → 粉丝转化 → 变现) SOP 走查 |
| `workflow/ai-ai-ai.sh` | AI+公考新工作流 (AI 批改/AI 面试/智能路径) SOP 走查 |
| `workflow/workflow-7.sh` | 选岗报名决策工作流 (职位表 → 条件筛选 → 报录比 → 确定岗位) SOP 走查 |

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
  --industry-cn "公务员考试培训"
```
