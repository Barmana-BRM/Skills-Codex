---
name: mgmt-paper-spss
description: 面向管理学、心理学、组织行为、营销和社会科学研究的 SPSS 分析 Skill。覆盖数据导入、变量标签、缺失值、信度 Cronbach alpha、探索性因子分析、相关、t 检验、ANOVA、线性/Logistic 回归、中介/调节、PROCESS 使用准备、表格导出和投稿前结果审查。当用户需要 SPSS 语法、SPSS 到 Python/Stata 的衔接、或把问卷/实验数据分析结果写入论文时调用。
tags: [spss, survey, psychology, management, ob, marketing, reliability, factor-analysis, regression]
version: 0.1.0
author: MGMT-Paper-Skills Contributors
license: Apache-2.0
display_name: "MGMT - Paper - SPSS"
---

# MGMT - Paper - SPSS — SPSS 分析模板与审查

## 核心原则

SPSS 适合问卷、实验、心理测量、组织行为和营销研究中的常规统计分析。使用 SPSS 时要保留 `.sps` 语法文件，而不是只保存点选操作截图。

## 工作流

1. 明确研究设计。
   - 横截面问卷、实验、追踪数据、匹配样本或二分类结果。
   - 变量层级：个体、团队、组织、时间。
   - 分析目标：信度、结构效度、均值比较、回归、中介、调节。
2. 读取 `references/spss-workflow.md`。
3. 选择模板。
   - `templates/spss/survey_reliability_factor.sps`
   - `templates/spss/regression_mediation_moderation.sps`
   - `templates/spss/anova_experiment.sps`
   - `templates/spss/logistic_regression.sps`
4. 要求输出。
   - `.sps` 语法文件。
   - 结果表导出路径。
   - 变量字典和缺失值处理说明。
   - 论文结果段落草稿。
5. 审查质量门。
   - 样本量和缺失值处理是否透明。
   - 信度、因子结构、共同方法偏差是否有说明。
   - 中介/调节是否与理论机制匹配。
   - 回归表是否报告 N、R2、标准化/非标准化系数、置信区间。

## 与本地 MCP 串联

若安装了 `mgmt-paper-local-analysis-mcp`，可以让 Codex/Claude 检测本机 SPSS，并运行已有 `.sps` 文件。不要运行来源不明的语法文件。

本机 SPSS 命令行验收：

```bash
python3 scripts/check_spss_cli.py --syntax templates/spss/survey_reliability_factor.sps
```

若返回 `SPSS executable not found.`，说明需要先安装 IBM SPSS Statistics 或显式传入 `--executable`。

## 输出

返回：

1. 适合的 SPSS 分析路径。
2. 可复制的 `.sps` 语法。
3. 需要用户确认的数据列名。
4. 结果表和图表导出建议。
5. 论文写作注意事项。
6. 审稿人可能质疑点。
