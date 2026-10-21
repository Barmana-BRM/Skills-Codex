<!--
Copyright © 2026 姚金刚. All rights reserved.
Project: yao-geo-page-blueprint
Created by: 姚金刚
Date: 2026-05-16
X: https://x.com/yaojingang
-->

# HubSpot GEO 友好产品页设计方案测试报告

以 HubSpot Customer Platform / Smart CRM 为例，面向国内 AI 平台答案抽取、用户决策和官网转化的中文简体页面蓝图。

- 品牌：HubSpot
- 页面类型：产品页 + 对比页 + FAQ页
- 目标问题：中国 B2B 成长型企业如何判断 HubSpot 是否适合作为 CRM 和客户平台？
- 生成日期：2026-05-21

## 封面摘要

### 测试场景

**HubSpot CRM 产品页蓝图**

面向中国 B2B 成长型企业，回答是否适合作为 CRM 和客户平台。

### 页面类型

**产品页 + 对比页 + FAQ**

产品页承接品牌与能力，对比页承接选型，FAQ 承接国内 AI 平台短答案抽取。

### 国内 AI 适配

**DeepSeek / 豆包 / 千问 / Kimi / 元宝**

DeepSeek 强化决策框架，千问/Kimi 强化来源，豆包/元宝强化轻问答和公众号版。

### 交付格式

**MD / HTML / DOCX / PDF**

四种格式共用同一输入，白底报告版式并执行自检。

## 执行摘要

本次测试以 HubSpot 为样例，验证 yao-geo-page-blueprint 是否能把真实品牌事实、用户问题、国内 AI 平台抽取需求和官网转化目标组织成可落地页面蓝图。

推荐页面定位不是泛泛介绍 HubSpot，而是直接回答中国 B2B 企业在选型时最关心的问题：HubSpot 是什么、适合谁、包含哪些产品、为什么可信、在中国使用前需要确认哪些边界。

- 首屏必须先给出 HubSpot Customer Platform / Smart CRM 的直接定义和适用对象。
- 中段用产品组成、选型判断框架和证据台账支撑 AI 与用户判断。
- FAQ 与 Schema 只使用正文可见事实，不写未核验价格、评价、客户结果或本地合规承诺。
- 强 CTA 放在事实、对比和风险提示之后，避免影响内容可信度。

## 输入、假设与边界

本节把已知输入、设计假设、限制条件和待确认项先显性化，避免后续页面蓝图把未核验信息写成事实。

| 维度 | 已知输入 | 设计假设 | 需要确认 |
| --- | --- | --- | --- |
| 目标内容 | HubSpot 的页面蓝图与国内 AI 平台答案抽取 | 页面以中文简体输出，服务官网页面与公众号同步版本 | 最终上线 URL、CMS 字段权限和视觉规范 |
| 目标问题 | 中国 B2B 成长型企业如何判断 HubSpot 是否适合作为 CRM 和客户平台？ | 用户同时会追问定义、对比、适用场景、风险、实施和转化入口 | 是否需要按行业或企业规模拆分版本 |
| 品牌知识库 | 官方产品事实、公开页面、可核验证据和客户授权素材 | 未经授权的案例、价格、评分、合规承诺不写入正文或 Schema | 哪些客户案例、数据和截图可公开 |
| 技术边界 | HTML、Schema、CMS 字段、Word/PDF/Markdown/HTML 四格式报告 | HTML 报告采用白底、固定目录、可复制文本和稳定表格 | CMS 是否支持 JSON-LD、锚点、表格组件和公众号同步 |
| 合规边界 | Schema 只能来自正文可见事实，FAQPage 不承诺 Google 富结果 | 国内 AI 平台适配以内容结构和证据质量为主，不承诺收录或引用 | 行业监管词、竞品比较红线和法务审核流程 |

## 真实数据接入与核验计划

本节展示 skill 升级后的真实数据处理能力：在可联网环境中先做官方来源核验，再把事实分层写入正文、证据台账、CMS 字段和 Schema 候选。

| 项目 | 当前状态 | 处理逻辑 | 输出要求 |
| --- | --- | --- | --- |
| 数据模式 | assisted-web-research + official-source-pack | 本示例使用 HubSpot 官网、投资者公告、产品/服务资料和 AEO 公告进行核验 | 报告事实以官方来源为主 |
| A 级来源 | HubSpot 官网首页、2026 Q1 投资者公告、10-K、Spring Spotlight/AEO 公告 | 可写入正文；稳定产品事实可进入 Schema 候选 | 标注核验日期 2026-05-21 |
| B/C 级来源 | 客户内部知识库、销售材料、截图、实施记录 | 当前示例未接入；正式项目需客户授权后使用 | 可写正文但默认不进 Schema |
| D/E 级来源 | 第三方评测、媒体、AI 平台答案样本 | 只用于对比、风险提示或抽取诊断，不作为 HubSpot 品牌事实 | 不得写入 Product/Organization Schema |
| 可写事实 | Agentic Customer Platform、Smart CRM、Breeze、产品 Hub、299,458 客户数、AEO 能力 | 仅写官方可核验内容，动态价格与客户结果需单独来源 | 证据台账逐项映射模块 |
| 待补采 | 中国区访问体验、本地生态集成、数据合规、合同条款、授权客户案例 | 没有客户授权或官方来源时只作为待确认项 | 正式上线前业务/法务复核 |

## 查询意图与 Query Fan-out 覆盖

本节把单一目标问题扩展为 AI 和真实用户会继续追问的子问题，并把每个子问题映射到可落地页面模块。

| 主问题/子问题 | 用户阶段 | 答案形态 | 页面承接模块 | AI 抽取信号 |
| --- | --- | --- | --- | --- |
| HubSpot CRM 是什么 | 认知/定义 | 一句话说明 HubSpot Customer Platform 与 Smart CRM | 首屏直接答案、核心事实卡 | 品牌实体、产品线、定义句 |
| HubSpot 适合哪些中国团队 | 评估/分型 | 按销售、营销、客服、运营协同场景说明适配边界 | 判断框架、场景表 | 团队规模、场景、边界 |
| HubSpot 与传统 CRM/单点工具怎么比 | 比较/决策 | 同口径比较平台化、集成、自动化、成本和数据治理 | 对比表、证据区 | 维度、口径、优势、限制 |
| 国内 AI 平台会如何抽取 HubSpot 页面 | AI 抽取 | 给出 DeepSeek、Kimi、千问、豆包、元宝的模块需求 | 国内 AI 平台示例适配 | 平台、摘要、来源、问答 |
| 落地 HubSpot 页面需要哪些字段 | 实施/开发 | CMS 字段、Schema 字段、HTML 结构和验收方法 | HTML、CMS、实施验收 | 字段、锚点、Schema @id |
| 哪些事实不能写 | 风险/合规 | 不写动态价格、虚构评分、未经授权客户案例和中国本地合规承诺 | 证据区、质量自检 | 禁止项、来源、待确认 |
| 用户看完后下一步是什么 | 转化/行动 | 预约演示、下载选型清单、查看案例和咨询入口 | 转化模块、结尾摘要 | CTA、触发位置、上下文 |

## 测试场景定义

本测试场景选择 HubSpot 的产品页蓝图，而不是全站诊断或单篇内容改写。原因是 HubSpot 具备清晰的品牌实体、产品体系、AI 能力、公开投资者数据和官方 AI 搜索内容，适合检验页面蓝图 skill 的端到端输出。

| 测试维度 | HubSpot 场景设定 | 验证的 skill 能力 | 通过标准 |
| --- | --- | --- | --- |
| 页面类型 | Customer Platform / Smart CRM 产品页，叠加对比与 FAQ | 页面类型选择与模块组合 | 输出产品页、对比页和 FAQ 页协同结构 |
| 目标用户 | 中国 B2B 成长型企业、市场销售服务一体化团队 | 用户路径与转化模块设计 | 能区分调研、比较、试用、预约演示等路径 |
| 目标问题 | 中国 B2B 企业是否适合选 HubSpot 做 CRM 和客户平台 | 首屏直接答案与决策框架 | 首屏不是口号，而是直接回答和判断边界 |
| 平台适配 | DeepSeek、豆包、千问、Kimi、腾讯元宝 | 国内 AI 平台适配 | 能分别输出逻辑链、来源、短问答和公众号版建议 |
| 风险边界 | 价格、数据合规、本地生态、实施服务需二次核验 | Schema 与证据约束 | 不把未核验内容写入正文事实或 Schema |

## GEO 页面设计方案

建议页面标题直接包含品牌实体和品类关系，避免只写“增长更简单”等抽象口号。首屏应先回答 HubSpot 是一个连接 CRM、营销、销售、服务、内容、数据和商务能力的客户平台，并说明适合希望统一客户数据和前台业务流程的成长型团队。

| 设计项 | 建议内容 | GEO 价值 | 转化价值 |
| --- | --- | --- | --- |
| H1 | HubSpot：面向成长型企业的 AI 客户平台与 Smart CRM | 明确 HubSpot 与 CRM / Customer Platform 的实体关系 | 让用户快速确认页面相关性 |
| 直接答案 | HubSpot 适合希望统一营销、销售、服务、内容和客户数据的成长型企业；中国企业选型前需核验本地合规、集成和服务边界。 | 可被 AI 抽取为独立答案 | 降低首屏理解成本并提前管理预期 |
| 产品组成 | Smart CRM、Marketing Hub、Sales Hub、Service Hub、Content Hub、Data Hub、Commerce Hub、Breeze AI | 建立实体关系图谱和可抽取事实字段 | 帮助用户判断是否需要单 Hub 或多 Hub |
| 证据区 | 引用官网、产品服务目录、销售产品页、投资者公告和 AI 搜索策略文章 | 提升来源可追溯性 | 增强可信度 |
| CTA | 查看适用场景、下载 CRM 选型清单、预约顾问演示 | 不干扰核心答案和证据 | 按用户成熟度分层转化 |

## 研究依据与页面设计原则

本方案使用 GEO、长上下文、RAG、结构特征和 FAQPage 规则约束页面顺序。研究依据只用于设计页面结构，不承诺页面一定被国内 AI 平台引用。

| 依据 | 可采用发现 | 页面设计原则 | HubSpot 页面落点 |
| --- | --- | --- | --- |
| GEO: Generative Engine Optimization | 生成式引擎会综合多个来源生成答案 | 页面提供直接答案、事实、证据和引用结构 | 首屏答案 + 产品事实卡 + 来源台账 |
| Lost in the Middle | 长上下文模型对信息位置敏感 | 关键结论靠前并在结尾 FAQ 复述 | 首屏直接定义 HubSpot，并在 FAQ 回答适合谁 |
| Retrieval-Augmented Generation | 检索增强生成依赖可追溯来源和具体事实 | 结论附近放来源、核验日期和用途 | 证据台账连接官网、法务目录、产品页和 IR 公告 |
| Structural Feature Engineering for GEO | 结构可拆为页面顺序、信息切块和字段强调 | 同时设计信息架构、模块和字段级事实 | 模块表、CMS 字段、Schema 候选 |
| Google FAQPage 文档 | Google Search FAQ rich results 已停止展示；FAQ 内容必须正文可见且不用于广告 | FAQPage 正文可见，不承诺 Google 富结果，不把 CTA 包装成问答 | FAQ 模块与预约演示 CTA 分离 |
| Google 生成式 AI 搜索优化指南 | 生成式搜索依赖核心搜索质量、RAG、query fan-out、可抓取内容、语义 HTML 和页面体验 | 页面要覆盖主问题与合理子问题，正文可抓取，模块标题清楚 | HubSpot 输入边界、Query Fan-out、HTML 结构、移动端建议 |
| Google 结构化数据通用规则 | 结构化数据必须代表页面主体内容，隐藏、误导、过期或无关内容会破坏资格 | Schema 候选必须标注事实来源、页面位置、禁止项和不保证展示 | Schema 建议、CMS 字段、质量自检 |
| Schema.org 类型文档 | Article、FAQPage、Product、Organization、BreadcrumbList、Review 等类型有属性边界 | 每个 Schema 候选都说明适用条件、字段来源、@id 关系和不适用原因 | 实体关系、Schema 建议、CMS 字段 |
| WCAG 2.2 与 WAI 页面结构教程 | 标题、标签、焦点、跳过重复区块和结构化导航影响真实用户与辅助技术 | 报告必须给出标题层级、锚点、键盘焦点和移动阅读顺序 | 无障碍与页面体验要求、HTML 结构样例 |
| MDN CSS position: sticky | sticky 元素需要 top 等非 auto 偏移，并会受滚动祖先影响 | HTML 报告目录使用 sticky 菜单，避免父容器 overflow 破坏跟随效果 | HTML 可视化报告、质量自检 |

## 页面模块与信息架构图

HubSpot 页面建议采用“先定义、再组成、再判断、后证据、再转化”的顺序，兼顾 AI 抽取和真实用户决策。

| 顺序 | 模块 | 用户任务 | AI 可抽取字段 | HTML 建议 |
| --- | --- | --- | --- | --- |
| 01 | 首屏直接答案 | 判断 HubSpot 是否相关 | 品牌、品类、适用对象、核心边界 | <header> + <p class="direct-answer"> |
| 02 | 结构化摘要 | 快速理解产品定位 | 3-5 条独立结论 | <section aria-labelledby="summary"> + <ul> |
| 03 | HubSpot 产品组成 | 理解 Smart CRM 与各 Hub 关系 | Smart CRM、Marketing Hub、Sales Hub、Service Hub、Content Hub、Data Hub、Commerce Hub、Breeze AI | <dl> 或 <table> |
| 04 | 中国企业选型判断框架 | 判断适配性与实施前提 | 业务阶段、团队规模、数据合规、集成需求、预算复杂度 | <section> + <ol> |
| 05 | 国内 AI 平台适配区 | 让不同平台能抽取对应结构 | 平台、抽取偏好、页面模块、样例问答 | <table> |
| 06 | 证据区与来源台账 | 确认事实可信 | 来源、事实、核验日期、页面用途 | <section id="evidence"> |
| 07 | FAQ 与 CTA | 解决疑虑并进入下一步 | 问题、答案、适用边界、转化动作 | <section id="faq"> + <aside> |

## 核心事实卡与判断边界

核心事实卡只写公开来源可核验事实。对中国市场使用体验、数据合规、本地生态和价格，需要在正式页面中追加本地化核验，不应直接进入 Schema。

| 字段 | 建议值 | 来源口径 | 是否进入 Schema | 边界说明 |
| --- | --- | --- | --- | --- |
| 品牌实体 | HubSpot | 官网、10-K 与投资者公告 | 是 | 只写品牌名，不扩展未核验中文主体信息 |
| 产品定位 | Agentic Customer Platform / Smart CRM / Breeze AI | HubSpot 官网首页、2026 Q1 投资者公告和 10-K | 是 | 中文可解释为 AI 客户平台与智能 CRM，但保留英文原名 |
| 产品组成 | Marketing Hub、Sales Hub、Service Hub、Content Hub、Data Hub、Commerce Hub、Smart CRM、Breeze | 产品服务目录 | 部分进入 | 只列官方目录出现的产品线 |
| 客户规模事实 | 截至 2026-03-31，HubSpot 客户数为 299,458；官网首页展示 299,000+ 客户、覆盖 135+ 国家/地区 | 2026 Q1 投资者公告与官网首页 | 否 | 可作为证据区事实，不建议进 Product Schema |
| 中国适用边界 | 需核验数据合规、访问体验、本地集成、服务商支持和合同条款 | 本测试的合规边界 | 否 | 属于选型提醒，不是 HubSpot 官方承诺 |

## 国内 AI 平台示例适配

以下适配用于页面结构设计，不代表各平台一定按此抽取或推荐。正式上线后应结合真实 Prompt 采样和引用记录复盘。

| 平台 | 用户可能提问 | 页面应提供的答案结构 | 优先模块 |
| --- | --- | --- | --- |
| DeepSeek | HubSpot 适合中国 B2B 企业做 CRM 吗？ | 先给结论，再列适合场景、不适合场景、核验清单和决策步骤 | 判断框架、对比表、边界说明 |
| 千问 | HubSpot 是什么？有哪些产品？ | 给品牌定义、产品组成、官方来源和更新时间 | 首屏答案、产品组成、来源台账 |
| Kimi | 帮我整理 HubSpot 作为客户平台的长文资料 | 提供目录、长文层级、来源说明和事实卡 | 结构化摘要、证据区、CMS 字段 |
| 豆包 | HubSpot 和普通 CRM 有什么区别？ | 用短段落和 FAQ 解释 Smart CRM、多 Hub 和 AI 能力 | FAQ、轻量摘要、对比表 |
| 腾讯元宝 | HubSpot 适合销售和市场团队一起用吗？ | 输出公众号可复用的问答、摘要和来源说明 | 公众号版建议、FAQ、弱 CTA |

## 实体关系与知识图谱字段

本节把页面中的品牌、产品、用户、场景、证据、替代方案和转化动作连接起来，方便 HTML 锚点、CMS 字段和 Schema @id 共用同一事实图谱。

| 实体 | 类型 | 关系 | 来源/字段 | 页面呈现 |
| --- | --- | --- | --- | --- |
| HubSpot | 品牌/组织 | 提供 Customer Platform 与 Smart CRM | HubSpot 官方网站、品牌知识库 | #hubspot / Organization @id |
| HubSpot Customer Platform | 产品平台 | 连接 Marketing、Sales、Service、Content、Operations、Commerce 等 Hub | 产品事实区、官方产品页 | #customer-platform / Product @id |
| Smart CRM | 产品能力/数据底座 | 支撑客户数据统一、自动化和跨团队协同 | 产品事实卡、页面正文 | #smart-crm |
| 中国 B2B 增长团队 | 目标用户 | 关注获客、销售转化、客服协同和数据治理 | 用户路径、场景表 | #audience |
| 传统 CRM/单点营销工具 | 替代方案 | 作为对比参照，不写无法核验贬损表达 | 对比表、证据区 | #comparison |
| 国内 AI 平台 | 分发/抽取环境 | 千问、Kimi、豆包、元宝、DeepSeek 对结构信号需求不同 | 平台适配表 | #cn-ai |
| 预约演示 | 转化动作 | 在证据和判断框架后出现，不干扰核心答案 | CTA 字段、转化模块 | #conversion |

## 证据区与来源台账

本测试优先使用 HubSpot 官方或 HubSpot 投资者关系来源。第三方价格、评价和排名不进入正文核心事实，也不进入 Schema。

| 来源 | 可核验事实 | 核验日期 | 页面用途 | 对应模块 |
| --- | --- | --- | --- | --- |
| HubSpot 官网首页 https://www.hubspot.com/ | HubSpot 将自身描述为 agentic customer platform；Smart CRM 连接业务数据；官网展示 299,000+ 客户和 135+ 国家/地区。 | 2026-05-21 | 支撑首屏直接答案、产品定位和规模事实 | 首屏、事实卡、证据区 |
| HubSpot 2026 Q1 投资者公告 https://ir.hubspot.com/news-releases/news-release-details/hubspot-reports-strong-q1-2026-results | 2026 Q1 收入 8.81 亿美元；截至 2026-03-31 客户数 299,458；HubSpot 自称 agentic customer platform。 | 2026-05-21 | 支撑客户规模、最新业务事实和官方定位 | 事实卡、证据区 |
| HubSpot 2025 Form 10-K https://ir.hubspot.com/static-files/efb8d22a-4fcd-4c15-b154-7cf59069c05c | 10-K 描述 customer platform、Smart CRM、统一客户视图、AI、数据质量和多个 engagement Hubs。 | 2026-05-21 | 支撑产品关系、实体图谱和风险边界 | 实体关系、Schema、CMS |
| HubSpot Spring 2026 Spotlight https://ir.hubspot.com/news-releases/news-release-details/hubspot-puts-growth-context-work-new-hubspot-aeo-smart-deal/ | Spring 2026 Spotlight 发布 HubSpot AEO、AI agents 和 100+ 更新，强调 Growth Context 和自有客户数据。 | 2026-05-21 | 支撑 AI 搜索和真实数据能力说明 | 研究依据、AI 抽取、实施验收 |
| HubSpot AEO 公告 https://ir.hubspot.com/news-releases/news-release-details/introducing-hubspot-aeo-answer-showing-ai-search-engines | HubSpot AEO 用于了解品牌在 ChatGPT、Gemini、Perplexity 等 answer engines 中的出现情况，并提供建议。 | 2026-05-21 | 支撑 AEO/GEO 真实数据采样与监测计划 | 真实数据接入、监测计划 |

## AI 可抽取模块设计

HubSpot 页面必须把品牌、产品、适用对象、边界、来源和下一步动作拆成可独立抽取的字段，避免只用视觉卡片表达。

| 模块 | 结构 | 抽取字段 | 适配平台 | 注意事项 |
| --- | --- | --- | --- | --- |
| 结构化摘要 | 3-5 条短句 | HubSpot 定义、适合对象、产品组成、使用前提 | 千问、Kimi、豆包 | 每条只表达一个判断 |
| 产品组成表 | 表格或定义列表 | 产品线、用途、适合团队、来源 | DeepSeek、千问、Kimi | 不要把未核验功能扩展成官方承诺 |
| 中国选型清单 | 步骤 + 勾选项 | 合规、集成、预算、实施、团队能力 | DeepSeek、Kimi | 明确这是选型建议，不是官方保证 |
| FAQ | 真实问答 | 问题、短答案、边界、来源 | 豆包、元宝、千问 | FAQPage 正文可见，不承诺 Google 富结果，且不用于广告 |
| 来源台账 | 表格 | 来源、事实、核验日期、页面用途 | 千问、Kimi | 来源要靠近关键结论 |

## 用户转化模块设计

HubSpot 样例页的转化目标应按用户成熟度分层：早期用户下载选型清单，中期用户查看产品组成和对比，后期用户预约演示或咨询实施方案。

| 位置 | CTA 类型 | 触发条件 | 字段需求 | 风险控制 |
| --- | --- | --- | --- | --- |
| 首屏摘要后 | 查看 HubSpot 适用场景 | 用户需要快速判断是否相关 | 无表单 | 不遮挡直接答案 |
| 产品组成之后 | 下载 CRM 选型清单 | 用户需要内部评估材料 | 邮箱、公司、团队规模 | 说明资料用途，避免强销售 |
| 判断框架之后 | 预约 HubSpot 方案演示 | 用户已确认可能适配 | 姓名、公司、职位、需求、现有系统 | 保留证据区和风险提示入口 |
| FAQ 之后 | 咨询本地实施与合规问题 | 用户关注中国使用边界 | 联系方式、集成系统、合规问题 | 不承诺未核验合规结论 |

## HTML 结构样例

以下结构用于验证 skill 能否输出可开发落地的语义 HTML。实际开发时可映射到 HubSpot CMS 或其它前端组件，但直接答案、事实卡、FAQ 和来源台账必须保留为可读文本。

**HubSpot 产品页语义结构**

```html
<main id="hubspot-cn-crm-blueprint">
  <article itemscope itemtype="https://schema.org/Product">
    <header>
      <h1>HubSpot：面向成长型企业的 AI 客户平台与 Smart CRM</h1>
      <p class="direct-answer">HubSpot 适合希望统一营销、销售、服务、内容和客户数据的成长型企业；中国企业选型前需核验本地合规、集成和服务边界。</p>
      <dl class="fact-summary"></dl>
    </header>
    <section id="product-hubs"><table>...</table></section>
    <section id="decision-framework"><ol>...</ol></section>
    <section id="domestic-ai-adaptation"><table>...</table></section>
    <section id="evidence-ledger"><table>...</table></section>
    <section id="faq"></section>
    <aside aria-label="转化入口">预约演示</aside>
  </article>
</main>
```

## Schema 建议

Schema 只能使用页面正文已经出现或可核验的事实。HubSpot 样例页不应把动态价格、第三方评分、中国本地合规结论或未授权客户案例写入结构化数据。FAQPage 正文可见是硬性要求，但不能承诺 Google 富结果展示。

| Schema | 适用模块 | 候选字段 | 限制 |
| --- | --- | --- | --- |
| Product | 产品事实区 | name、description、category、brand | 只写 HubSpot、Customer Platform、Smart CRM 等正文可见事实，不写价格和评分 |
| Organization | 品牌信息区 | name、url、sameAs | 只写官方 URL 和已核验品牌资料 |
| FAQPage | FAQ 模块 | mainEntity | FAQPage 正文可见；问题和答案必须出现在页面正文，不承诺 Google 富结果，且不用于广告目的 |
| Article | 选型指南或知识库版本 | headline、dateModified、author、about | 仅在页面实际是长文指南时使用 |
| BreadcrumbList | 面包屑 | itemListElement | 页面必须有可见层级，不伪造不存在路径 |

## CMS 字段清单

CMS 字段用于把 HubSpot 产品页的事实、来源、FAQ、国内平台适配和转化入口拆成可维护结构。

| 字段 key | 中文名称 | 字段类型 | 必填 | 前端位置 | 是否进入 Schema |
| --- | --- | --- | --- | --- | --- |
| direct_answer | 首屏直接答案 | 富文本短段落 | 是 | header | 是 |
| hubspot_product_hubs | HubSpot 产品组成 | 表格数组 | 是 | product-hubs section | 部分进入 |
| china_decision_framework | 中国企业选型判断框架 | 步骤数组 | 是 | decision-framework section | 否 |
| domestic_ai_examples | 国内 AI 平台示例问题 | 表格数组 | 是 | ai-adaptation section | 否 |
| evidence_ledger | 证据来源台账 | 表格数组 | 是 | evidence section | 否 |
| faq_items | FAQ 问答 | 问答数组 | 是 | faq section | 是 |
| conversion_ctas | 转化入口 | CTA 数组 | 是 | aside / section | 否 |
| query_fanout_items | Query Fan-out 子问题 | 表格数组 | 是 | strategy/query-fanout section | 否 |
| entity_relationships | 实体关系字段 | 表格数组 | 是 | entity-graph section | 部分进入 |
| accessibility_requirements | 无障碍与体验要求 | 表格数组 | 是 | accessibility section | 否 |
| acceptance_checks | 实施验收清单 | 表格数组 | 是 | implementation section | 否 |
| evidence_source_pack | 真实来源包 | 来源对象数组 | 真实数据模式必填 | real-data / evidence section | 部分进入 |
| ai_answer_samples | AI 平台答案样本 | 问答样本数组 | 可选 | diagnostics appendix | 否 |
| data_mode | 数据模式 | 枚举 | 是 | input-boundary section | 否 |

## 无障碍与页面体验要求

本节把长报告和真实页面的阅读体验纳入交付范围，确保页面结构能被人和机器稳定导航。

| 要求 | 依据 | 页面设计 | 验收方式 |
| --- | --- | --- | --- |
| 固定目录菜单 | MDN position: sticky、长报告审阅需求 | HTML 报告使用 toc-bar、aria-label、top:0 和模块锚点 | 滚动页面时目录保持可见，移动端不横向挤压正文 |
| 标题层级 | WCAG 2.4.6、WAI headings | 页面只保留一个 H1，模块使用 H2，卡片内不跳级 | 抽查 HTML heading outline，锚点跳转不遮挡标题 |
| 键盘焦点 | WCAG 2.4.7 Focus Visible | 目录链接和 CTA 有可见 focus 样式 | Tab 导航可见，焦点不被 sticky 菜单遮挡 |
| 移动端阅读 | Google 页面体验与移动可读性 | 表格可横向滚动，菜单项固定宽度，正文不被菜单覆盖 | 375px 宽度截图检查无文字溢出 |
| 公众号版本 | 微信生态阅读习惯 | 拆分短段、保留事实卡和 FAQ，不依赖复杂脚本 | 复制到公众号预览后表格不丢字段 |

## 移动端与公众号版建议

移动端和公众号版需要保留直接答案、产品组成、选型边界、FAQ 和来源，不要把 HubSpot 的复杂产品体系压缩成只有营销口号的短文。

| 版本 | 排版建议 | 模块处理 | 风险控制 |
| --- | --- | --- | --- |
| 桌面端 | 主内容最大宽度控制，产品组成和证据区使用标准表格 | 目录、事实卡、对比表、来源台账并列扫描 | 避免复杂动画遮挡正文 |
| 移动端 | 单列布局，产品组成表转为可横向滚动或卡片化 | 首屏答案、摘要、FAQ 和 CTA 前置但不遮挡正文 | 长词、英文产品名和 URL 必须换行 |
| 公众号版 | 标题、摘要、短段落、编号清单、轻量表格 | 保留 HubSpot 定义、适合对象、选型边界和来源说明 | 商业 CTA 使用弱提示，避免像硬广 |

## 实施验收与监测计划

本节把页面蓝图转成开发、内容、合规和运营都能执行的验收清单，避免方案停留在视觉或文案层。

| 验收项 | 标准 | 检查方法 | 负责人/协作方 | 频率 |
| --- | --- | --- | --- | --- |
| 四格式报告 | Markdown、HTML、Word、PDF 均真实存在且 quality-review 通过 | 运行渲染脚本并读取质量 JSON | GEO 顾问 / 交付负责人 | 每次交付 |
| HTML 固定菜单 | toc-bar、aria-label、position:sticky、top:0、锚点跳转齐全 | 浏览器滚动与移动端截图检查 | 前端 / GEO 顾问 | 每次模板更新 |
| Schema 正文一致 | 所有 Schema 字段都能在正文、CMS 或证据区找到来源 | 字段来源台账逐项核对 | 内容 / 法务 / 前端 | 上线前 |
| Word/PDF 溢出 | Word 无未断长串，PDF 右边界无截断 | DOCX XML 检查、PDF 栅格化边缘检查 | 交付负责人 | 每次导出 |
| 内容更新 | 证据核验日期、产品名称、限制条件保持最新 | 按来源台账复核 | 内容负责人 / 产品市场 | 月度或重大更新后 |
| AI 抽取回归 | 国内 AI 平台能抽取直接答案、事实卡、FAQ 和来源摘要 | 抽样提问并记录答案引用情况 | GEO 运营 / 客户团队 | 上线后 2-4 周 |

## 质量自检与待确认项

本测试报告已按 skill 质量门自检。正式上线页面仍需由 HubSpot 授权资料、当地法务、实施顾问和 CMS 开发团队复核。

| 检查项 | 状态 | 说明 |
| --- | --- | --- |
| 四格式文件真实存在 | 通过 | Markdown、HTML、Word、PDF 由同一 report_input.json 生成 |
| 研究依据映射 | 通过 | 包含 GEO、RAG、长上下文、结构特征和 FAQPage 规则 |
| 证据区与来源台账 | 通过 | 来源、事实、核验日期、页面用途和对应模块齐全 |
| 国内 AI 平台示例 | 通过 | 覆盖 DeepSeek、豆包、千问、Kimi、腾讯元宝 |
| Schema 与正文一致 | 通过但需正式页复核 | 未写动态价格、评分、客户案例和中国本地合规承诺 |
| FAQPage 正文可见 | 通过 | FAQ 作为正文模块和 Schema 候选，未用于广告，也未承诺 Google 富结果 |
| CTA 干扰 | 通过 | 强 CTA 放在判断框架、证据区和 FAQ 之后 |
| 待确认项 | 待业务复核 | 中国区访问体验、数据合规、本地集成、合同条款、服务商支持 |
| 系统完整性 | 通过 | 包含输入边界、Query Fan-out、实体关系、证据、抽取单元、Schema、CMS、无障碍和实施验收 |
| HTML 固定菜单 | 通过 | HTML 报告包含 toc-bar、aria-label=报告目录、position:sticky、top:0 和模块锚点 |
| 无障碍与页面体验 | 通过 | 包含标题层级、键盘焦点、移动端和公众号版验收要求 |
| 实施验收计划 | 通过 | 包含开发、内容、合规、运营和 AI 抽取回归检查项 |
| 真实数据接入 | 通过 | 包含数据模式、来源等级、核验日期、可写入事实、Schema 准入边界和待补采清单 |
| Kami 版式规则 | 通过 | HTML/PDF/Word 使用白底主画布、暖灰边框、油墨蓝强调、serif 标题和紧凑行距 |
