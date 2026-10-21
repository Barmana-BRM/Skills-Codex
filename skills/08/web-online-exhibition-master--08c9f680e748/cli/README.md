# Web 线上展览开发 (虚拟展厅) CLI

把 Web 线上展览开发 (虚拟展厅) master skill 的认知 OS 物化成 bash 工具。
不替代 SKILL.md（思维顾问），是它的「执行端」：交互问询 → 应用 playbook / protocol → 输出结构化报告。

## 用法

所有脚本支持 `--help` / `--explain` / `--dry-run` / `--json` 四个标准 flag。

```bash
# 拿到新问题时, 按 N 个研究维度做功课
./protocol/agentic.sh

# 决策树评估 (基于 playbook)
./decision/topic-1.sh
# SOP 走查 (workflow)
./workflow/3d.sh

# 看背后的心智模型 / playbook (不交互)
./protocol/agentic.sh --explain
```

## 脚本清单

| 脚本 | 作用 |
|------|------|
| `protocol/agentic.sh` | Agentic Protocol (6 维度) — 拿到新问题时按这一行的研究维度做功课 |
| `decision/topic-1.sh` | 案例 决策树 (7 条规则) |
| `decision/topic-2.sh` | 全景 决策树 (2 条规则) |
| `decision/topic-3.sh` | 验收 决策树 (1 条规则) |
| `workflow/3d.sh` | 端到端线上展览制作（自研真 3D 全流程） SOP 走查 |
| `workflow/saas-matterport-artsteps.sh` | SaaS 平台快速搭建（众趣 / 酷雷曼 / Matterport / Artsteps） SOP 走查 |
| `workflow/720.sh` | 全景 720 漫游制作 SOP 走查 |
| `workflow/playbook.sh` | 性能优化 Playbook（命门 — 单列） SOP 走查 |
| `workflow/model-viewer.sh` | 单展品 model-viewer 嵌入 SOP 走查 |
| `workflow/qa.sh` | 跨端兼容 / 上线验收 QA 环 SOP 走查 |
| `workflow/workflow-1.sh` | 高斯泼溅「实景扫描即展厅」管线（新兴） SOP 走查 |
| `workflow/webgl-webgpu-tsl.sh` | WebGL → WebGPU / TSL 迁移 SOP 走查 |

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
  --industry-cn "Web 线上展览开发 (虚拟展厅)"
```
