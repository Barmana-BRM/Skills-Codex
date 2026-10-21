---
name: mgmt-paper-style-benchmark
description: 管理学顶刊风格参考与全文风格校准 Skill。用于学习用户提供的目标期刊文章、author guidelines、LaTeX/Word 模板和目标稿件，生成不抄袭、不复刻原文的语言、结构、段落、图表、标题、摘要、引言、讨论、排版和投稿格式改写建议。当用户需要把论文校准到 AMJ/ASQ/SMJ/Organization Science/MISQ/Management Science 或中文管理学顶刊风格时调用。
tags: [management, style, top-journal, polishing, structure, formatting, benchmark, manuscript]
version: 0.1.0
author: MGMT-Paper-Skills Contributors
license: Apache-2.0
display_name: "MGMT - Paper - Style Benchmark"
---

# MGMT - Paper - Style Benchmark — 顶刊风格参考与全文校准

## 适用场景

用于把管理学论文从“内容基本有了”提升到“语言、结构、段落、排版和投稿呈现接近目标期刊口味”。它适合摘要、引言、理论、方法、结果、讨论、图表、附录和 cover letter 的全稿风格校准。

## 重要边界

不得复制或模仿用户未授权文章的表达。只能抽取高层级风格特征：段落功能、论证顺序、句子密度、标题习惯、贡献呈现方式、图表组织和排版规则。短语和句子必须重新写成原创表达。

## 输入

- 目标期刊或期刊族。
- 用户稿件或章节。
- 用户提供的目标论文、author guidelines、LaTeX/Word 模板或 reviewer comments。
- 论文阶段：outline / rough draft / full draft / presubmission / R&R。

## 工作流

1. **风格样本盘点**
   - 读取 `templates/style_benchmark_matrix.md`。
   - 把目标样本拆为：标题、摘要、引言 opening、contribution paragraph、theory setup、method transparency、results narrative、discussion moves、limitations、managerial implications。

2. **风格特征提取**
   - 读取 `references/style-dimensions.md`。
   - 只提取可迁移的写作规律：段落功能、句长、转折密度、claim-evidence 连接、贡献措辞、表图解释方式。

3. **稿件差距诊断**
   - 对用户稿件逐节标注：too vague / too long / overclaiming / under-theorized / table-driven / weak transition / formatting risk。

4. **改写与排版**
   - 读取 `references/formatting-gates.md`。
   - 输出标题、摘要、引言、贡献段、结果段、讨论段、管理启示和局限段的改写建议。
   - 同步检查标题层级、表图编号、图注、脚注、引用格式、匿名化、补充材料标记。

5. **全稿一致性**
   - 统一构念名、理论标签、假说编号、贡献表达、管理启示措辞和 limitations 边界。

## 输出

返回：

1. Style Benchmark Matrix。
2. Section-by-Section Gap Diagnosis。
3. Rewrite Plan。
4. Paragraph-Level Revision Examples。
5. Formatting Gate Checklist。
6. Final Style Risk Memo。

## 与其他 Skills 协同

- 用 `mgmt-paper-writing` 执行具体章节重写。
- 用 `mgmt-paper-manuscript-package` 检查 package 完整性。
- 用 `mgmt-paper-reviewer-simulation` 检查风格修订是否解决审稿风险。
- 用 `mgmt-paper-journal-figures` 和 `mgmt-paper-tables` 对齐表图风格。

## 使用提醒

如果用户要求“参考某篇顶刊文章风格”，先要求用户提供文章、摘要或其可引用片段；不要凭空声称已经学习某篇未提供的文章。若需要最新期刊格式，优先查官方 author guidelines。
