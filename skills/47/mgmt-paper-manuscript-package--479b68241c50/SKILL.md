---
name: mgmt-paper-manuscript-package
description: 面向管理学论文从材料整理到预投稿 package 的全流程 Skill。覆盖论文材料盘点、证据矩阵、结构答辩、章节撰写、章节间一致性、整合修订、预审稿件 package、cover letter、匿名稿、补充材料、数据代码清单和投稿前质量门。当用户需要把一个粗糙研究项目整理成可给导师、合作者、预审人或期刊提交的完整论文包时调用。
tags: [management, manuscript, package, submission, chapter-writing, revision, defense, checklist]
version: 0.1.0
author: MGMT-Paper-Skills Contributors
license: Apache-2.0
display_name: "MGMT - Paper - Manuscript Package"
---

# MGMT - Paper - Manuscript Package — 论文材料整理与预投稿包

## 适用场景

用于把一个分散的研究项目收束成可审查、可答辩、可投稿的完整稿件包。常见输入包括：粗糙 idea、文献笔记、理论框架、数据说明、回归表、访谈材料、图表、草稿章节、审稿意见或导师批注。

## 核心原则

1. **先整理材料，再写正文**：不要在证据、变量、表图、贡献和限制还不清楚时直接润色。
2. **每一章都要能答辩**：章节不只是文本，而是一个可被追问的论证单元。
3. **修订必须整合**：单点修改后要回查摘要、引言、理论、方法、结果、讨论、表图、附录和 cover letter 是否一致。
4. **package 是审稿体验**：匿名稿、补充材料、数据代码说明、图表、cover letter、投稿检查表要让编辑和审稿人低摩擦地理解贡献。

## 工作流

1. **材料盘点**
   - 读取 `templates/material_inventory.md`。
   - 把论文现有材料分成：理论、文献、数据、方法、结果、图表、定性证据、附录、代码、投稿文件。
   - 标记每项材料状态：ready / partial / missing / risky。

2. **证据矩阵**
   - 读取 `templates/evidence_matrix.csv`。
   - 每个核心主张必须对应至少一类证据：理论推导、定量结果、稳健性、定性证据、外部事实、附录说明。
   - 没有证据支撑的主张要降级、删除或标注为未来研究。

3. **结构答辩**
   - 读取 `references/structure-defense.md`。
   - 用 10 个问题检验论文结构：研究问题、理论张力、贡献、识别、机制、边界、替代解释、管理含义、伦理边界、投稿 fit。
   - 输出“答得上 / 答不稳 / 答不上”的清单。

4. **章节撰写**
   - 读取 `references/chapter-writing.md`。
   - 逐章生成：本章目标、必须出现的证据、段落顺序、禁写内容、与其他章节的回指关系。
   - 章节写作后同步更新摘要、引言贡献段、理论假说、结果段和讨论段。

5. **整合修订**
   - 读取 `references/integrated-revision.md`。
   - 每一次修改都检查：术语、构念名、假说编号、样本口径、变量命名、表图编号、显著性表述、贡献边界是否一致。
   - 对大修生成 revision log，记录修改原因、涉及文件、风险和后续动作。

6. **预审 package**
   - 读取 `templates/presubmission_package_checklist.md`。
   - 生成预审包：匿名主文档、标题页、cover letter、highlights、supplement、data/code availability、figures/tables、response memo。
   - 标注哪些文件可直接给导师/合作者，哪些可给外部预审人，哪些仅供内部。

## 输出格式

返回一个“稿件交付包报告”：

1. Materials Inventory：现有材料与缺口。
2. Evidence Matrix：主张—证据—表图—附录映射。
3. Structure Defense：最容易被追问的问题和答辩稿。
4. Chapter Plan：逐章写作与修订任务。
5. Integrated Revision Plan：跨章节一致性修订清单。
6. Presubmission Package：投稿前文件清单与缺口。

## 与其他 Skills 协同

- 用 `mgmt-paper-writing` 写作章节。
- 用 `mgmt-paper-reviewer-simulation` 做预审。
- 用 `mgmt-paper-style-benchmark` 做风格与格式校准。
- 用 `mgmt-paper-project-management` 把修订任务排期。
- 用 `mgmt-paper-tables`、`mgmt-paper-charts`、`mgmt-paper-journal-figures` 检查表图。

## 边界

不得补造数据、结果、引用或审稿意见。缺失材料必须标注为缺口，不能用“合理推测”伪装成已经完成的证据。
