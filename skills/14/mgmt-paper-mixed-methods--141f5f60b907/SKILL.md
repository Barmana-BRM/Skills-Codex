---
name: mgmt-paper-mixed-methods
description: 面向管理学、组织研究、战略、创业、营销、信息系统和社会科学的混合方法研究 Skill。覆盖探索型顺序设计、解释型顺序设计、并行汇聚设计、嵌入式设计、定性发现转量化假设、量化结果回到机制解释、joint display、方法整合段落、顶刊审稿风险与论文 story 打磨。当用户需要连接访谈/案例与问卷/实验/档案数据，或设计 mixed-methods paper 时调用。
tags: [mixed-methods, qualitative, quantitative, management, theory-building, joint-display, idea-to-story]
version: 0.1.0
author: MGMT-Paper-Skills Contributors
license: Apache-2.0
display_name: "MGMT - Paper - Mixed Methods"
---

# MGMT - Paper - Mixed Methods — 混合方法研究 Skill

## 核心原则

混合方法不是“定性加一点访谈、定量加几张回归表”。它要求两个证据系统在同一个理论问题下相互约束、相互解释，并清楚说明整合发生在研究设计、数据收集、分析还是写作阶段。

## 适用场景

- 用访谈或案例发现新机制，再转化为可检验假设。
- 用问卷、实验或档案数据发现稳健关系，再回到访谈解释机制。
- 定性结果与定量结果部分一致、部分冲突，需要形成 joint display。
- 管理学顶刊论文需要把 idea → story → paper 连接得更可信。

## 工作流

1. 读取 `references/mixed-methods-workflow.md`。
2. 判断设计类型。
   - 探索型顺序：QUAL → quant。
   - 解释型顺序：QUAN → qual。
   - 并行汇聚：QUAL + QUAN → integrated inference。
   - 嵌入式：主研究内嵌辅助方法。
3. 生成整合矩阵。
   - 定性构念、代表性证据、量化变量、假设、模型、预期符号。
   - 主效应、机制、边界条件、替代解释。
4. 生成 story spine。
   - 现象张力。
   - 理论缺口。
   - 机制命名。
   - 证据路线。
   - 贡献边界。
5. 审稿前检查。
   - 两套证据是否回答同一个问题。
   - 定性是否只是装饰。
   - 定量是否过度声称因果。
   - joint display 是否真的产生整合推断。

## 模板

- `templates/joint_display.csv`
- `templates/idea_to_story_to_paper.md`

## 输出

返回：

1. 推荐的混合方法设计。
2. 定性发现到量化假设的映射。
3. 量化结果回到机制解释的写作方案。
4. joint display 表格。
5. idea → story → paper 结构。
6. 审稿人可能质疑点和补强建议。
