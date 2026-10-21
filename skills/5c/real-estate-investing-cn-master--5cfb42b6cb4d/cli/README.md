# 国内房产投资(房产投资人视角 — 城市与地段选择 / 政策与调控解读 / 一手房与二手房 / 房产金融与杠杆 / 估值与尽职调查 / 交易流程与税费 / 持有运营与出租 / 退出与流动性 / 风险识别 / 房产在个人资产配置中的位置 / 投资者的决策框架与心态 — 聚焦中国大陆,2021 年以来深度下行期的真实市场) CLI

把 国内房产投资(房产投资人视角 — 城市与地段选择 / 政策与调控解读 / 一手房与二手房 / 房产金融与杠杆 / 估值与尽职调查 / 交易流程与税费 / 持有运营与出租 / 退出与流动性 / 风险识别 / 房产在个人资产配置中的位置 / 投资者的决策框架与心态 — 聚焦中国大陆,2021 年以来深度下行期的真实市场) master skill 的认知 OS 物化成 bash 工具。
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
| `protocol/agentic.sh` | Agentic Protocol (9 维度) — 拿到新问题时按这一行的研究维度做功课 |
| `decision/topic-1.sh` | —— 决策树 (8 条规则) |
| `decision/topic-2.sh` | 政策 决策树 (1 条规则) |
| `workflow/workflow-1.sh` | 选城市(判断「这个城市的房子有没有基本面」) SOP 走查 |
| `workflow/workflow-2.sh` | 选板块与地段(在选定城市内部锁定区域价值单元) SOP 走查 |
| `workflow/vs.sh` | 选房(一手房 vs 二手房的标的筛选与初判) SOP 走查 |
| `workflow/workflow-3.sh` | 估值与尽职调查(合理价格判断 + 产权法律核查) SOP 走查 |
| `workflow/workflow-4.sh` | 交易与税费(网签 → 资金监管 → 缴税 → 过户 → 放款) SOP 走查 |
| `workflow/workflow-5.sh` | 持有与运营(出租 + 持有成本管理) SOP 走查 |
| `workflow/workflow-6.sh` | 退出与流动性(卖出时机判断 + 挂牌成交 + 止损决策) SOP 走查 |
| `workflow/workflow-7.sh` | 政策跟踪(政策原文 → 影响判断 → 留余量) SOP 走查 |
| `workflow/vs.sh` | 自住 vs 投资决策分流 + 杠杆/断供应对(两条逻辑严格分开) SOP 走查 |

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
  --industry-cn "国内房产投资(房产投资人视角 — 城市与地段选择 / 政策与调控解读 / 一手房与二手房 / 房产金融与杠杆 / 估值与尽职调查 / 交易流程与税费 / 持有运营与出租 / 退出与流动性 / 风险识别 / 房产在个人资产配置中的位置 / 投资者的决策框架与心态 — 聚焦中国大陆,2021 年以来深度下行期的真实市场)"
```
