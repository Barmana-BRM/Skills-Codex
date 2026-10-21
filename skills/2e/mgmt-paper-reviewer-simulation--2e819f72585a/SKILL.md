---
name: mgmt-paper-reviewer-simulation
description: 面向管理学顶级期刊的严格审稿模拟 Skill。按目标期刊和研究类型模拟 editor、theory reviewer、methods reviewer、empirical reviewer、qualitative reviewer、managerial relevance reviewer 和 skeptical reviewer，生成拒稿风险、major revision 路线、可执行补强清单和 response strategy。当用户需要投稿前预审、顶刊严审、R&R 策略、审稿意见拆解或模拟 AMJ/ASQ/SMJ/Organization Science/MISQ/Management Science 等期刊审稿人时调用。
tags: [management, peer-review, reviewer-simulation, utd, journal-fit, revision, pre-submission]
version: 0.1.0
author: MGMT-Paper-Skills Contributors
license: Apache-2.0
display_name: "MGMT - Paper - Reviewer Simulation"
---

# MGMT - Paper - Reviewer Simulation — 顶刊审稿模拟

## 适用场景

用于投稿前或 R&R 前进行高压预审。它不做鼓励式点评，而是模拟严苛顶刊审稿人，从理论、方法、证据、贡献、机制、期刊 fit 和写作透明度上寻找最可能导致拒稿的问题。

## 审稿角色

读取 `references/reviewer-roles.md` 后，根据论文类型选择 3-6 个角色：

- Handling Editor：是否值得送审或继续 revise。
- Theory Reviewer：理论张力、构念定义、贡献边界。
- Methods Reviewer：识别、研究设计、测量、内生性、稳健性。
- Empirical Reviewer：数据、模型、表图、可复现性。
- Qualitative Reviewer：案例选择、编码、证据链、Gioia 或过程逻辑。
- Managerial Relevance Reviewer：管理含义是否具体、有约束、非空泛。
- Skeptical Reviewer：最苛刻地寻找“没有新意/证据不足/过度声称”。

## 期刊校准

读取 `references/journal-review-profiles.md`。不要声称知道某期刊最新编辑政策，除非用户提供最新指南或要求联网核查。稳定校准包括：

- AMJ：理论贡献、管理现象、机制、边界条件。
- ASQ：组织理论深度、解释力、定性/过程证据严谨性。
- SMJ：战略理论、竞争优势、识别与机制。
- Organization Science：理论机制、方法多样性、组织现象解释。
- MISQ：IS 理论、技术/组织交互、设计与实证严谨性。
- Management Science：模型、识别、实证严谨性和跨领域贡献。

## 工作流

1. **输入诊断**
   - 明确目标期刊、研究类型、稿件阶段、核心贡献、主方法、主要结果。
   - 如果缺少稿件全文，要求至少提供摘要、引言、理论、方法、主表和讨论。

2. **独立审稿**
   - 每个 reviewer 先独立输出 3-5 个 major concerns。
   - 每条 concern 必须包含：严重度、依据、可能后果、补强方案。

3. **编辑决策模拟**
   - 读取 `templates/reviewer_report.md`。
   - 给出 desk reject / reject after review / major revision / minor revision / conditional accept 的模拟判断。
   - 判断必须克制，不能为了迎合用户而虚高。

4. **修订路线**
   - 按阻塞程度排序：kill issues、major issues、polish issues。
   - 生成“先做什么、后做什么、哪些可并行”的修订计划。

5. **三轮复查**
   - Round 1：贡献与理论。
   - Round 2：方法与证据。
   - Round 3：写作、表图、投稿 package。

## 输出

返回：

1. Simulated Editorial Decision。
2. Reviewer Panel Reports。
3. Fatal Risks。
4. Major Revision Plan。
5. Evidence and Analysis Requests。
6. Response Strategy。
7. Final Pre-Submission Gate。

## 与其他 Skills 协同

- 用 `mgmt-paper-project-management` 把 reviewer concerns 转成任务。
- 用 `mgmt-paper-manuscript-package` 生成预审 package。
- 用 `mgmt-paper-style-benchmark` 做语言与结构修订。
- 用 `mgmt-paper-causal-methods`、`mgmt-paper-qualitative`、`mgmt-paper-mixed-methods` 处理方法问题。

## 边界

模拟审稿不是实际同行评议。不得伪造真实审稿人意见、真实期刊反馈或编辑承诺。对于最新投稿政策和格式，优先使用用户提供的官方指南或联网核查官方页面。
