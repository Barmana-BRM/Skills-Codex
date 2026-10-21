# 半导体芯片制造工艺 CLI

把 半导体芯片制造工艺 master skill 的认知 OS 物化成 bash 工具。
不替代 SKILL.md（思维顾问），是它的「执行端」：交互问询 → 应用 playbook / protocol → 输出结构化报告。

## 用法

所有脚本支持 `--help` / `--explain` / `--dry-run` / `--json` 四个标准 flag。

```bash
# 拿到新问题时, 按 N 个研究维度做功课
./protocol/agentic.sh

# 决策树评估 (基于 playbook)
./decision/topic-1.sh
# SOP 走查 (workflow)
./workflow/ppac-pdk-doe-spc.sh

# 看背后的心智模型 / playbook (不交互)
./protocol/agentic.sh --explain
```

## 脚本清单

| 脚本 | 作用 |
|------|------|
| `protocol/agentic.sh` | Agentic Protocol (6 维度) — 拿到新问题时按这一行的研究维度做功课 |
| `decision/topic-1.sh` | 工艺 决策树 (3 条规则) |
| `decision/topic-2.sh` | 良率 决策树 (3 条规则) |
| `decision/topic-3.sh` | 节点 决策树 (2 条规则) |
| `workflow/ppac-pdk-doe-spc.sh` | 新节点 / 新工艺导入（PPAC 定义 → 工艺整合+PDK → 单元工艺 DOE → 量测 SPC → 良率爬坡 → 量产移交） SOP 走查 |
| `workflow/doe-cmp.sh` | 单元工艺配方开发（DOE 找工艺窗口）— 以刻蚀/沉积/CMP 为代表 SOP 走查 |
| `workflow/yield-ramp-commonality-spc.sh` | 良率爬坡 Yield Ramp（缺陷采集→分类→commonality→根因→改善→SPC固化） SOP 走查 |
| `workflow/fa-deprocess-fa.sh` | 失效分析 FA / 缺陷根因闭环（电性定位→物理 deprocess→FA→反馈改工艺） SOP 走查 |
| `workflow/dtco-pathfinding-pdk.sh` | DTCO 设计-工艺协同优化（pathfinding → 协同迭代 → 设计规则/标准单元 → PDK） SOP 走查 |
| `workflow/copy-exactly-td-hvm-fab-fab.sh` | 工艺移植 / Copy-Exactly（TD→HVM、fab→fab 量产移交与持续改善） SOP 走查 |
| `workflow/patterning-opc-overlay.sh` | 光刻层 patterning 方案开发（曝光条件 → OPC/计算光刻 → overlay 预算 → 多重曝光分解） SOP 走查 |

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
  --industry-cn "半导体芯片制造工艺"
```
