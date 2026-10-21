# Online 表单高级查询（SuperQuery）参考

> 高级查询是 Online 表单列表页面的动态多条件查询构造器，允许用户自由组合字段-规则-值的查询条件，支持 AND/OR 逻辑运算和查询方案保存/加载。

## 功能概述

| 功能 | 说明 |
|------|------|
| 动态条件行 | 可增删任意数量的查询条件行，每行包含字段选择、匹配规则、查询值 |
| AND/OR 模式 | 切换所有条件之间的逻辑关系（AND=全部匹配，OR=任意匹配） |
| 规则自动适配 | 根据字段类型自动提供合适的匹配规则（如文本类默认 like、文件类默认 empty） |
| 查询保存/加载 | 支持将当前查询方案保存到 localStorage 或自定义 API，右侧面板可查看/加载/删除 |
| 子表字段支持 | 字段选择器以树形展示主子表结构，子表字段以 `子表名@字段名` 格式选择 |
| 全屏模式 | 弹窗支持最大化，自动调整表单高度和下拉框高度 |
| 日期修正 | 自动处理年/月/周选择器的日期偏移（统一归一化到周期的第一天） |
| 取消查询 | 查询执行中显示旋转图标，点击可取消查询 |
| 响应式布局 | 屏幕宽度 < 1050px 时条件行垂直堆叠 |
| 自定义保存 | 支持通过 `isCustomSave` 开关切换到服务端 API 保存查询方案 |

## 组件位置

```
src/views/super/online/cgform/auto/comp/superquery/
├── SuperQuery.vue            # 主组件（按钮 + 弹窗 + 保存弹窗）
├── SuperQueryValComponent.vue # 值输入组件（TSX 渲染函数，动态渲染表单控件）
└── useSuperQuery.ts          # 核心 hook（状态管理 + 逻辑）
```

全局注册名：`SuperQuery` / `OnlineSuperQuery`

## 组件 Props

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `config` | Object | `[]` | 表单 JSON Schema，传给 `useSuperQuery.init()` 构建字段树 |
| `status` | Boolean | `false` | 查询执行中状态，`true` 时按钮显示旋转动画 |
| `online` | Boolean | `false` | `true`=Online 模式（直接 emit 数组），`false`=代码生成器模式（emit 包装对象） |
| `isCustomSave` | Boolean | `false` | 启用自定义保存模式，配合 `save` + `saveSearchData` 使用 |
| `saveSearchData` | Array | `[]` | 自定义保存模式下的外部查询方案数据 |
| `save` | Function | - | 自定义保存 API 函数，接收 `(curPageSave, type)`，type 为 `create`/`update`/`delete` |
| `queryBtnCfg` | Object | `{buttonName:'高级查询', buttonIcon:'ant-design:filter-outlined'}` | 按钮显示配置 |

## 组件 Emits

| 事件 | 参数 | 说明 |
|------|------|------|
| `search` | `(params, matchType?)` | 执行查询/重置/取消时触发 |

**两种参数格式：**
- **Online 模式** (`online=true`)：emit 原始数组 `(dataArray, matchType)`，数组中每项为 `{field, rule, val, type, dbType}`
- **代码生成器模式** (`online=false`)：emit 包装对象 `{superQueryMatchType, superQueryParams: encodeURI(JSON.stringify(arr))}`

## 核心 Hook：useSuperQuery

文件：`src/views/super/online/cgform/auto/comp/superquery/useSuperQuery.ts`（约 700 行）

### 主要状态

| 状态 | 类型 | 说明 |
|------|------|------|
| `dynamicRowValues` | `ref<{values: SuperQueryItem[]}>` | 当前所有条件行数据 |
| `matchType` | `ref<'and'\|'or'>` | 条件逻辑关系 |
| `fieldTreeData` | `ref<TreeModel[]>` | 字段选择树数据（主表+子表） |
| `fieldProperties` | `ref<Record<string, any>>` | fieldKey → fieldConfig 的查找表 |
| `saveTreeData` | `ref<TreeModel[]>` | 已保存查询方案的树数据 |

### 数据结构

```typescript
// 条件行
interface SuperQueryItem {
  key: string;        // 唯一标识 (UUID)
  field: string;      // 字段名（子表格式: "子表名@字段名"）
  rule: string;       // 匹配规则 (eq/like/gt/lt/between/in/empty/not_empty...)
  val: any;           // 查询值
  curLineAlign?: string;
  fileType?: string;
  view?: string;      // 控件类型
  originView?: string;
}

// 字段树节点
interface TreeModel {
  title: string;      // 显示名
  value: string;      // 字段值（子表格式: "子表名@字段名"）
  isLeaf?: boolean;
  disabled?: boolean;
  children?: TreeModel[];
  order?: number;
  fieldType?: string; // 数据库字段类型
  view?: string;      // 控件类型
  originView?: string;
}
```

### 核心方法

| 方法 | 说明 |
|------|------|
| `init(json)` | 初始化：解析 JSON Schema → 过滤 link_down → 构建 fieldProperties + fieldTreeData |
| `addOne(index)` | 添加条件行：`true`=打开时补空行，`false`=重置，数字=在该索引后插入 |
| `removeOne(item)` | 按 key 删除条件行 |
| `getSchema(item, index)` | 根据选中字段动态构建 FormSchema，使用 `FormSchemaFactory` 创建表单控件 |
| `getQueryInfo(isEmit)` | 序列化有效条件行，返回 `{field, rule, val, type, dbType}[]` 或 `false` |
| `handleSave()` | 打开保存命名弹窗 |
| `doSaveQueryInfo()` | 执行保存（默认 localStorage，自定义模式调 props.save） |
| `handleTreeSelect(key, node)` | 从右侧面板加载已保存的查询方案 |
| `handleRemoveSaveInfo(title)` | 删除已保存的查询方案 |
| `initDefaultValues(values)` | 从外部数据初始化查询条件 |

### 字段树构建规则

1. 遍历 JSON Schema 的 `properties`，过滤 `link_down` 类型
2. 主表字段直接作为叶子节点
3. 子表字段以子表名作为父节点，子字段作为折叠的子节点
4. 子表字段的 value 格式为 `子表名@字段名`（内部用 `@` 分隔）
5. 字段按 `order` 排序

### 控件类型到查询类型的映射

| 原始控件 | 查询类型 |
|---------|---------|
| `password`, `file`, `image`, `textarea`, `umeditor`, `markdown`, `link_down` | `text` |
| `checkbox` | `list_multi` |
| `radio` | `list` |
| 其他 | 保持原样 |

### 匹配规则自动选择

切换字段时的默认规则（`handleChangeField`）：

| 字段条件 | 默认规则 |
|---------|---------|
| `fieldType=string` 且 view 为 `text` | `like`（模糊查询） |
| view 为 `file`/`image`/`password` | `empty`（为空） |
| 其他 | `eq`（等于） |

### 可用规则列表

通过 `useConditionFilter()` 根据字段的 `view` + `fieldType` 动态过滤可用的匹配规则选项，常见包括：`eq`（等于）、`like`（模糊）、`gt`（大于）、`lt`（小于）、`ge`（大于等于）、`le`（小于等于）、`between`（介于）、`in`（包含）、`empty`（为空）、`not_empty`（不为空）等。

### 空值规则特殊处理

当选择 `empty` 或 `not_empty` 规则时，值输入控件会被禁用（无需输入值），`getQueryInfo` 中仅检查 field 和 rule 是否存在而不检查 val。

## 保存机制

### 默认模式（isCustomSave=false）

- 保存在浏览器 localStorage，key 为 `JSuperQuerySaved_ + route.fullPath`
- 设置 30 天过期时间
- 保存时检查重名，提示是否覆盖

### 自定义模式（isCustomSave=true）

- 调用 `props.save(curPageSave, type)`，type 为 `create`/`update`/`delete`
- 使用 `props.saveSearchData` 替代 localStorage 作为数据源
- 适用于需要服务端持久化或多用户共享查询方案的场景

## 日期修正逻辑（transformDateValus）

针对年/月/周选择器，统一将日期值归一化到周期的第一天：

| 选择器类型 | 处理方式 |
|-----------|---------|
| `year` | 设为该年 1 月 1 日 |
| `month` | 设为该月 1 日 |
| `week` | 设为该周的第一天（startOf('week')） |

> 原因：年/月/周选择器在存储时按周期的第一天存储，查询时需要同样处理以保证匹配。

## 在 Online 列表页的集成方式

在 `OnlineAutoList.vue` 中：

1. 声明 `<online-super-query>` 组件，绑定 `ref="superQueryButtonRef"`
2. 设置 `online=true`，`status` 绑定 `superQueryStatus`
3. 监听 `@search="handleSuperQuery"`
4. 在 `onQueryFormLoaded` 回调中调用 `superQueryButtonRef.value.init(json)` 传入 Schema
5. `handleSuperQuery` 中将参数存入 `onlineTableContext['superQuery']`，重置分页到第 1 页，重新加载数据
6. 后端通过 `superQueryParams` 参数接收并解析高级查询条件

## 全屏模式细节

- 弹窗支持 `canFullscreen: true`，全屏切换时触发 `handleFullScreen`
- 全屏时：表单 `max-height` 设为 `clientHeight - 165px`，树下拉框高度设为内容区的 62%
- 非全屏时：表单最大高度 400px（CSS 写死），树下拉框高度 180px

## 样式要点

- 树下拉框弹窗有 `containTable` 和 `noTable` 两个 CSS class，分别对应有/无子表场景
- 无子表时隐藏 `switcher` 图标，字段名超长时省略号显示
- 有子表时隐藏 `indent-unit`，调整缩进
- 已保存查询面板从右侧滑入/滑出（`right: 0` ↔ `right: -180px`），带折叠箭头按钮
