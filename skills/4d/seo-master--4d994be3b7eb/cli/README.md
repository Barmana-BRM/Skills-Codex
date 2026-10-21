# SEO 专家 CLI

把 SEO 专家 master skill 的认知 OS 物化成 bash 工具。
不替代 SKILL.md（思维顾问），是它的「执行端」：交互问询 → 应用 playbook / protocol → 输出结构化报告。

## 用法

所有脚本支持 `--help` / `--explain` / `--dry-run` / `--json` 四个标准 flag。

```bash
# 拿到新问题时, 按 N 个研究维度做功课
./protocol/agentic.sh

# 决策树评估 (基于 playbook)
./decision/topic-1.sh
# SOP 走查 (workflow)
./workflow/seo-90.sh

# 看背后的心智模型 / playbook (不交互)
./protocol/agentic.sh --explain
```

## 脚本清单

| 脚本 | 作用 |
|------|------|
| `protocol/agentic.sh` | Agentic Protocol (5 维度) — 拿到新问题时按这一行的研究维度做功课 |
| `decision/topic-1.sh` | 链接 决策树 (1 条规则) |
| `decision/search.sh` | Search 决策树 (1 条规则) |
| `decision/topic-3.sh` | 内容 决策树 (3 条规则) |
| `decision/seo.sh` | Seo 决策树 (2 条规则) |
| `decision/general-playbook.sh` | 通用 Playbook 决策树 (2 条规则) |
| `workflow/seo-90.sh` | 新站 SEO 上线 (90 天打基线) SOP 走查 |
| `workflow/seo-pillar-cluster.sh` | 内容 SEO 生产 (Pillar + Cluster) SOP 走查 |
| `workflow/seo-site-audit-crawlability.sh` | 技术 SEO 审计 (Site Audit + Crawlability) SOP 走查 |
| `workflow/link-building.sh` | 链接建设 (Link Building) — 白帽路径 SOP 走查 |
| `workflow/ai-search-geo-llmo-2024-2026.sh` | AI Search 优化 (GEO / LLMO) — 2024-2026 新流派 SOP 走查 |

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
  --industry-cn "SEO 专家"
```
