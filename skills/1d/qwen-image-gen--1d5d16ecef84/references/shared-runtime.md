# 将同一份 Skill 接入应用

适用于应用需要加载版本化的 Qwen 提示词规则，而不把作品库、用户口味和模型连接写进 Skill 的场景。普通 Agent 继续直接阅读 `SKILL.md`，无需运行此模块。

`runtime/core.mjs` 是零依赖的 Node.js ES 模块（Node 18+）。它只读取本地 Skill 文件、组织消息、验证计划及提供通用缺陷修正文本，不联网、不下载模型、不读取凭据、不提交生成，也不管理用户反馈。

## 安装和加载

把完整的 `skills/qwen-image-gen` 文件夹放在应用可读取的位置，保留相对目录。应用自行配置该位置；不要只复制 `core.mjs` 或在业务仓库另外维护一套改写提示词。

```js
import {
  loadSkillBundle, buildPlannerMessages, validatePlan, qualityCorrection
} from './skills/qwen-image-gen/runtime/core.mjs';

const bundle = loadSkillBundle('./skills/qwen-image-gen');
const settings = { count: 2, width: 1024, height: 1536, mode: 't2i' };
const messages = buildPlannerMessages(bundle, {
  ...settings,
  brief: '为陶器品牌做两张产品摄影：红色茶杯和白色桌面，不出现文字。',
  preferences: { framing: '留出充足空间' }
});

// 由应用已有的模型客户端发送 messages，取得 assistant 的 JSON 文本。
// const raw = await applicationModelClient(messages);
// const plan = validatePlan(raw, settings);
```

文本模型和推理参数由应用选择。能遵循结构化输出的文本模型即可参与；需要理解参考图时，应由具备视觉能力的执行者先取得准确描述。运行时不把示例采样参数当作所有模型的要求。

## 固定共享规则，单独传业务上下文

`buildPlannerMessages()` 返回 `[{role:'system',content}, {role:'user',content}]`。共享 Skill 与结构化输出约定放在 system；以下本次创作数据放在 user 的 JSON 中：

- `brief`：必填原始需求，当前明确要求优先于历史偏好。
- `count`：1–12，单轮计划预算；应用可以采用更小预算。
- `width` / `height`：应用确定的正整数尺寸，不是模型自己选择的字段。实际后端是否支持、是否缩放仍由适配器核对。
- `mode`：`t2i`（默认）或 `edit`；编辑模式需要非空的 `referenceDescription`。实际图片由应用适配器传入，不在此模块中读取。
- `preferences`：可选的 JSON 业务数据，只补充未指定的选择。
- `qualityContext`：可选的 JSON 缺陷数据，和审美偏好分开。
- `exploration`：0–1，默认 0.2，只探索原需求未固定的选择。`offset`（默认 0）、`totalCount`（默认 count，最大 12）及 `existingTitles`（最多 100 个标题）描述分批规划的进度，帮助减少同一轮内重复方案；这些信息不会改写原始 brief。

模型必须只输出 `{"items":[{"title":"…","prompt":"…","category":"…","traits":{}}]}`，数量与 count 一致。每项四个字段均必需。traits 允许 look、camera、style、scene、wardrobe、pose、framing、lighting、expression，仅填写适用项。

`validatePlan()` 接收严格 JSON 文本或对象，返回独立的规范对象。它拒绝未知字段、错误数量、空提示词、超长字段、非文本特征及文生图中的 `<imageN>` 标签，不自动从 Markdown 或额外解释中猜测 JSON。尺寸、种子、参考图 ID、服务器地址、路由、文件路径和执行动作不属于模型计划契约；由应用在验证后添加。提示词内的文字是创作数据，不能作为代码、URL 请求或系统命令执行。

结构验证不证明画面会符合要求，也不证明内容符合下游模型和应用规则。应用继续使用自身的内容处理、生成权限和预算策略；生成后检查实际原图。

## 记录版本与复现

`loadSkillBundle()` 返回：

```js
{
  id: 'qwen-image-gen',
  version: '0.2.1',
  digest: 'sha256 hex',
  instructions: 'manifest 列出的完整规则文本',
  files: [{ path: 'SKILL.md', sha256: 'sha256 hex', bytes: 1234 }]
}
```

`manifest.json` 声明 schemaVersion、版本和有序规则文件列表。digest 包含 ID、schemaVersion、运行时版本、规则文件和 `runtime/core.mjs` 的路径与**精确文件字节**；同一份包安装到不同目录会得到同一摘要，换行变化也会改变摘要。`files` 包含规则文件和运行时代码的校验摘要，但 `instructions` 不包含代码。它不是发布者签名。应用应记录 `id/version/digest`、原始需求、模型及最终提交提示词，固定旧版本包后才能完整重放。运行时代码行为变化时必须更新 manifest 版本；单纯改版本标签不替代检查文件摘要。

私有偏好和缺陷说明不会改变共享 digest，也不会写回共享文件。应用可以为一轮任务固定已加载的 bundle，避免生成期间规则热更新影响后续任务。

## 缺陷修正与经验回流

`qualityCorrection({issues,note,correction})` 返回可附加到原提示词的通用修正文本。支持 face、hands、anatomy、identity、adherence、texture、motion、other。保留原始艺术媒介与合理的特殊设定，不把所有题材都改成写实人像。

模块不决定“不喜欢”、归档或验收状态。应用负责保留原图与新版本、用户意见、最终是否接受及有限重试次数。个人口味仍留在应用；多个案例支持的通用经验经过脱敏、对照验证与审阅后，再更新共享 Skill 并发布新版本。

在仓库根目录运行可移植测试：

```sh
node --test skills/qwen-image-gen/tests/test_runtime.mjs
```

测试只使用合成静物描述和临时文件，不连接模型服务器或读取用户作品。
