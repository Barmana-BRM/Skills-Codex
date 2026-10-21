# PRD→HLD 漂移检测指南

先按 `../../../references/review-boundaries.md` 选择 `formal_design` 或 `bounded_change`。本文的全量 PRD 覆盖与追溯格式适用于正式 HLD；有限增量使用相关批准依据和受影响链路，不补造整套文档。以下 P0/P1 示例都以有效基线、实际影响和本轮范围成立为前提，不能凭关键词或缺章节自动判级。

## 为什么漂移检测是最高优先级？

在多 AI Agent 协同工作中，PRD 和 HLD 可能由：
- 不同的 AI session 生成
- 不同的上下文环境
- 不同的时间点

这导致 **隐性知识断裂**，容易产生漂移。人类工程师有「隐性记忆」可以自动对齐，但 AI Agent 没有。

**漂移的代价极其高昂**：
- 需求遗漏 → 功能缺失，晚期返工
- 需求膨胀 → 过度工程，资源浪费
- 需求曲解 → 做出来不是用户要的，推倒重来

因此先检查范围与语义。关键依据不明会阻止该部分准出，但不阻止其他可独立判断部分的审查。

---

## 四种漂移类型

### 1. 需求遗漏

**定义**：PRD 中明确定义的需求，在 HLD 中没有对应的设计。

**检测方法**：
```
For each approved in-scope requirement:
    Search HLD for corresponding design
    If not found:
        Distinguish missing evidence from an actual omitted behavior
        Grade the proven omission by impact; do not infer P0 from a missing heading
```

**常见表现**：
- PRD 的验收标准在 HLD 中无法验证
- PRD 的功能点在 HLD 中未提及
- PRD 的非功能需求被忽略

**示例**：
```
PRD: "系统应支持密码重置功能，用户可通过邮箱验证码重置密码"
HLD: （未提及密码重置相关设计）
→ 已证实范围内功能遗漏；按用户影响分级，不由缺章节自动判 P0。
```

---

### 2. 需求膨胀

**定义**：HLD 中出现了 PRD 未定义的功能或设计。

**检测方法**：
```
For each changed behavior/responsibility/dependency in the proposed design:
    Trace scope to an original approved requirement/ADR/authorized owner decision
    If within that scope and delegated engineering authority:
        Evaluate technical necessity and the smallest sufficient design
    Else if it clearly violates a known boundary and can be reverted:
        Report the defect and request restoration of that boundary
    Else:
        Record DECISION_REQUIRED; evaluate feasibility without granting scope
    Never accept a "technical necessity" annotation or a reviewer comment as approval
```

**需要区分**：
| 类型 | 是否允许 | 处理方式 |
|------|----------|----------|
| 违反明确范围的额外功能 | ❌ 未批准 | 按影响列缺陷，优先退回既定边界，不诱导补范围 |
| 明确提出的边界变更提案 | ⚠️ 待有权 Owner 决定 | 分开输出技术结论与 DECISION_REQUIRED |
| 标注为「技术必要性」的设计 | ⚠️ 只是理由 | 仍须核查授权来源及更小方案 |
| 授权范围内的纯实现细节 | ✅ 可由工程 Owner 决定 | 路由 LLD；不是 HLD 新职责 |

**技术必要性的论证维度**（没有任何一项可以替代授权）：

| 维度 | 应核实的证据 | 不能自行推出的要求 |
|------|--------------|--------------------|
| 实现依赖 | 既定功能为何失败、边界内替代方案为何不足 | 登录功能不天然授权新会话模型或延长 TTL |
| 安全合规 | 适用法规/批准安全目标、当前威胁和改变的权限主体 | “更安全”不天然授权让机器任务依赖用户 PDP |
| 稳定性 | 已批准交付/恢复语义、当前持久化和重试能力 | 异步不天然要求 DLQ、新队列或重放平台 |
| 行业惯例 | 对既定目标的实际作用及维护成本 | API 不天然要求新版本号/双轨协议 |

论证可直接写在既有请求中：关联 invariant、真实失败、边界内最小替代、额外依赖/费用/运维、原始批准来源。增加注释或回补未经批准的 PRD 不能消除漂移。旧 Reviewer comment 及由它抄写的 APPROVED 文档不能循环充当新授权。

**示例**：
```
PRD: "实现用户登录功能"
HLD: "设计用户登录、第三方 OAuth 登录、单点登录（SSO）"
→ OAuth 和 SSO 超出已知范围；注释“技术必要性”不能批准它们。
  明确既有登录即可满足需求时退回；若用户请求变更，再由有权 Owner 决策。
```

---

### 3. 需求曲解

**定义**：HLD 的设计偏离了 PRD 的原意，字面上可能覆盖，但实际理解有偏差。

**检测方法**：
```
For each mapping (PRD requirement → HLD design):
    Verify semantic alignment:
        - Does HLD design fulfill the PRD intent?
        - Does HLD design match PRD acceptance criteria?
        - Are there implicit assumptions that differ?
    If misaligned:
        Record the concrete behavior mismatch and grade its actual impact
```

**常见表现**：
- PRD 说「实时」，HLD 设计成「准实时（延迟 5 分钟）」
- PRD 说「支持」，HLD 设计成「部分支持」
- PRD 说「用户」，HLD 理解成「管理员」

**示例**：
```
PRD: "系统应支持实时消息推送"
HLD: "使用消息队列异步处理，延迟约 30 秒"
→ 先核实“实时”的批准指标；若实际超出，按业务影响列语义缺陷，不能自己创造更严 SLO。
```

---

### 4. 边界漂移

**定义**：HLD 改变了 PRD 定义的功能边界（范围、约束、限制）。

**检测方法**：
```
Compare PRD scope definition with HLD scope:
    - In-scope items alignment
    - Out-of-scope items alignment
    - Constraints alignment
    - Assumptions alignment
If a boundary changed:
    Check original authorization and impact
    Classify an actual violation, a scope decision, or missing evidence separately
```

**常见表现**：
- PRD 说「不做 X」，HLD 设计了 X
- PRD 限制「最多 1000 用户」，HLD 设计成「无限制」
- PRD 假设「内网环境」，HLD 设计成「公网环境」

**示例**：
```
PRD: "本期不支持批量导入，单条录入即可"
HLD: "设计批量导入接口，支持 Excel 上传"
→ 边界漂移：超出本期范围 (P1)
```

---

## 漂移检测执行步骤

### Step 1: 检查 PRD 基线标注

正式 HLD 需要完整批准需求基线；有限模式读取相关现有 Contract/HLD/ADR/用户决定即可。当前源码/现网只是事实，不自动成为获批标准。

**检查项**：
- [ ] HLD 是否标注了 PRD 基线版本？
- [ ] PRD 文件路径是否正确？
- [ ] PRD 是否为**最新批准基线**？（非草稿版本）

> **「最新批准基线」定义**：
> - 经过正式评审通过的 PRD 版本，而非仍在迭代中的草稿
> - **证据路径**：检查版本、状态及原始批准记录；状态标签本身不是授权来源。不能确定时先本地定位，再向有权 Owner 提出具体问题。

**处理路径（先查证，必要时询问）**：

| 情况 | 分类 | 处理 |
|------|--------|------|
| 正式 HLD 未标注来源，但已查到有效批准基线 | 覆盖/追溯问题 | 继续核查；按缺失的实际证据说明需补内容 |
| 正式 HLD 缺必要批准需求，且无等价授权依据 | Evidence gap | EVIDENCE_BLOCKED，不签全量证书；其他独立部分可审 |
| Draft 或状态未知，无法确认行为获批 | Evidence gap / Scope decision | 只暂停依赖它的准出，明确缺证或待决定内容 |
| 有限修复无单独 PRD，但相关批准行为可核实 | 非缺陷 | 继续 bounded_change，不要求重写全套 PRD |

**Step 1.1: 如果 HLD 未标注 PRD 来源**：
1. 先查 HLD/ADR/索引中的引用，读取可取得的相关批准来源。
2. 仍有影响结论的缺口时，询问具体依据；不从“没写路径”推断“没有批准”。
3. 正式 HLD 确实缺必要需求依据时：
```
Evidence gap：正式 HLD 的需求依据无法核实
- 缺失：本次要承诺的用户/机器权限边界及其批准来源
- 影响：无法对该边界的一致性签全量准出
- 下一步：取得该具体批准依据；其他已有依据部分继续，不先发明权限方案
```

**Step 1.2: 验证 PRD 状态**：
- 检查 PRD 状态、版本及原始批准记录，不能只信标签。
- **可核实有效批准** → 继续一致性审查。
- **Draft 或状态未知** → 依赖部分不能准出：
```
Evidence gap：目前无法确认该需求为批准基线
- 可以分析方案技术可行性，但不能写 WITHIN_APPROVED_SCOPE 或签全量证书。
- 如果该材料是主动提交的变更提案，另列 DECISION_REQUIRED，交有权 Owner 决定。
```

> ⚠️ 不得假设「HLD 没标注 PRD = 没有 PRD」；也不得假设「文档标了 APPROVED = 有原始授权」。

### Step 2: 检查需求映射表

**检查项**：
- [ ] HLD 是否包含 PRD↔HLD 需求映射表？
- [ ] 映射表格式是否完整（PRD 需求 ID、描述、HLD 章节）？

**期望的映射表格式**：
```markdown
| PRD 需求 ID | PRD 需求描述 | HLD 覆盖章节 | 覆盖程度 |
|-------------|--------------|--------------|----------|
| REQ-001 | 用户登录 | 3.1 认证设计 | 完全覆盖 |
| REQ-002 | 密码重置 | 3.2 密码管理 | 完全覆盖 |
| REQ-003 | 会话超时 | 3.3 会话管理 | 部分覆盖 |
```

**正式 HLD 缺少可用映射时**（已有等价映射不要求重排表格；有限模式不补全量表）：
```
Evidence gap：无法验证完整需求覆盖
- 请求补充缺少的需求→设计位置，而非为格式偏好制造 P0。
- 若已证实某个范围内必要行为被遗漏，另列实际缺陷及影响。
```

### Step 3: 逐条验证需求覆盖

**执行方法**：

1. **提取 PRD 需求清单**
   - 功能需求（用户故事、功能点）
   - 非功能需求（性能、安全、可用性）
   - 验收标准
   - 约束和假设

2. **逐条在 HLD 中查找**
   ```
   For each PRD_requirement:
       Search HLD for coverage
       Record: {
           prd_id: "REQ-001",
           prd_description: "...",
           hld_section: "3.1" or "未找到",
           coverage: "完全覆盖" | "部分覆盖" | "未覆盖",
           evidence: "HLD:L45-60" or "N/A"
       }
   ```

3. **标记问题**
   - 未覆盖 → 区分实际遗漏与找不到证据；实际遗漏按影响分级
   - 部分覆盖 → 需进一步分析是否可接受

### Step 4: 反向检查需求膨胀

**执行方法**：

1. **提取 HLD 功能设计清单**
   - 所有功能模块
   - 所有接口设计
   - 所有数据设计

2. **逐条在 PRD 中查找来源**
   ```
   For each changed responsibility/feature/dependency/failure behavior:
       Trace original authorized scope and engineering delegation
       Distinguish implementation detail from boundary change
       Never treat annotations, tests, or reviewer-generated approval as authorization
   ```

3. **分类处理**
   - 有有效来源且未改变该语义 → 继续技术验证
   - 有技术必要性论证 → 仍须核实授权及最小方案
   - 无来源 → 区分越界缺陷、待决策提案和证据缺口

### Step 5: 语义对齐验证

**对于映射存在的需求，验证语义是否对齐**：

| 验证项 | 检查内容 |
|--------|----------|
| 功能完整性 | HLD 设计是否完整实现 PRD 功能？ |
| 性能对齐 | HLD 性能目标是否匹配 PRD 要求？ |
| 边界对齐 | 职责、权限主体、数据范围、常态依赖和失败语义是否获批？ |
| 可发布性 | 生产管理入口是否支持拟议输入，还是仅直接调用执行器测试？ |
| 验收可测 | HLD 设计能否验证 PRD 验收标准？ |

---

## 漂移检测输出模板

```markdown
## PRD↔HLD 一致性检查报告

### 基本信息
- **PRD 基线**：[文件路径] v[版本号] ([日期])
- **HLD 文档**：[文件路径]
- **检查时间**：YYYY-MM-DD HH:MM

### 检查结果摘要
- PRD 需求总数：X 条
- 完全覆盖：Y 条 (Y/X = %)
- 部分覆盖：Z 条
- 未覆盖：W 条 ⚠️
- 需求膨胀：V 处 ⚠️

### 需求覆盖详情

| PRD 条目 | HLD 覆盖位置 | 状态 | 非已覆盖说明 |
|----------|-------------|------|-------------|
| REQ-001 用户登录 | 3.1:L45 | ✅ 已覆盖 | — |
| REQ-002 密码重置 | — | ❌ 未覆盖 | HLD 无对应设计，需补充密码重置流程章节 |
| REQ-003 会话管理 | 3.2:L78 | ⚠️ 部分覆盖 | 仅覆盖创建会话，未覆盖 PRD 要求的「登出所有设备」功能 |
| REQ-004 第三方登录 | 3.5:L120 | ⚠️ 部分覆盖 | 膨胀点：PRD 未要求第三方登录，HLD 自行添加，需确认是否在范围内 |

**`非已覆盖说明` 填写规则**：
- ✅ 已覆盖 → 填 `—`
- ⚠️ 部分覆盖 → **必填**：说明哪部分未覆盖、缺了什么
- ❌ 未覆盖 → **必填**：说明遗漏内容、建议补充方向
- ❓ 待澄清 → **必填**：说明需要澄清的问题
- 发现 **膨胀点** → 在说明中标注 `膨胀点：{描述}`

### 漂移问题清单

#### P0 阻塞问题
| # | 类型 | 描述 | PRD 证据 | HLD 证据 |
|---|------|------|----------|----------|
| 1 | 需求遗漏 | REQ-002 密码重置无设计 | PRD:2.3 | - |
| 2 | 需求曲解 | REQ-005 「实时」被设计为 30s 延迟 | PRD:3.1 | HLD:4.2 |

#### P1 严重问题
| # | 类型 | 描述 | PRD 证据 | HLD 证据 |
|---|------|------|----------|----------|
| 1 | 需求膨胀 | 第三方登录未在 PRD 范围内 | - | HLD:3.5 |
| 2 | 边界漂移 | 支持范围超出 PRD 定义 | PRD:1.4 | HLD:2.1 |

### 门一结论（不得用局部完成冒充全量准出）

- technical_verdict：[APPROVED / CHANGES_REQUIRED / EVIDENCE_BLOCKED]
- scope_status：[WITHIN_APPROVED_SCOPE / DECISION_REQUIRED]
- [已完成范围、仍依赖未决事实的部分、可继续的独立部分]

### 修复建议

1. **REQ-002 密码重置**
   - 问题：HLD 缺少对应设计
   - 建议：在 HLD 3.x 节补充密码重置设计

2. **REQ-005 实时性**
   - 问题：HLD 设计与 PRD 要求不符
   - 建议：与 PRD 作者确认「实时」定义，或修改 HLD 设计

3. **第三方登录**
   - 问题：HLD 设计超出 PRD 范围
   - 建议：退回明确的本期边界；确需改变时交有权 Owner 决定，补写 PRD 本身不是授权
```

---

## 常见漂移场景与处理

### 场景 1：PRD 需求模糊，HLD 做了具体化

**示例**：
```
PRD: "系统应有良好的性能"
HLD: "接口响应时间 < 200ms，QPS > 1000"
```

**处理**：
- 数值可作为工程测量目标提案，验证是否符合已授权成本/容量预算。
- 若把它变成产品性能承诺或新增常态成本，需要相应 Owner 决定；不能靠“具体化”自批。

### 场景 2：PRD 有多种理解，HLD 选择了一种

**示例**：
```
PRD: "支持用户导出数据"
HLD: "支持 CSV 格式导出"（未支持 Excel）
```

**处理**：
- 标记为「待澄清」
- 询问 PRD 作者原意
- 不直接判定为漂移

### 场景 3：HLD 发现 PRD 遗漏，补充了设计

**示例**：
```
PRD: 未提及错误处理
HLD: 设计了完整的错误处理机制
```

**处理**：
- 边界内的错误映射、局部重试可属于已授权工程细节，转 LLD 验证。
- 如“完整机制”意味着新 DLQ/恢复平台、改变失败是否可继续或新增用户授权依赖，仍是边界变化。
- 必要性说明只解释理由；要核对原始授权，不能一概宣布“不算膨胀”。

### 场景 4：PRD 变更后 HLD 未同步

**示例**：
```
PRD v2: 新增了 REQ-010
HLD: 基于 PRD v1，缺少 REQ-010
```

**处理**：
- 先确认 PRD v2 已批准且适用于本轮冻结范围；后续未批准草稿不自动改写基线。
- 若确实遗漏本轮有效需求，按影响列缺陷；新范围交 Owner 明确，不因“最新”重开所有已审范围。

---

## 自动化检测建议

对于大型项目，可以考虑半自动化检测：

1. **需求 ID 关联**
   - PRD 需求使用唯一 ID（REQ-001, REQ-002...）
   - HLD 设计引用 PRD ID
   - 工具可自动检查 ID 覆盖率

2. **关键词匹配**
   - 提取 PRD 关键功能词
   - 在 HLD 中搜索匹配
   - 未匹配的标记为待审查

3. **结构化模板**
   - PRD 和 HLD 使用结构化模板
   - 章节一一对应
   - 便于自动化对比

---

## 核心原则

1. **先确认本轮边界与批准来源，再审技术可行性**
2. **没有证据不判定漂移，只标记待澄清**
3. **遗漏与曲解按真实影响分级，不靠类别或数量制造阻断**
4. **合理性不等于授权；必要性、复用、安全和行业惯例都不构成豁免**
5. **正式追溯要完整；有限增量不重造文档集，P2 不续轮**
