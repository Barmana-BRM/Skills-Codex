# Warning Triage

建议把问题分成三类：

## P1 阻断提交

- 编译失败
- 引用缺失
- 关键文件缺失
- 模板模式错误

## P2 必须修复

- 关键图表未引用
- 公式未解释
- 摘要与正文数字不一致
- 严重排版问题

## P3 记录观察

- 轻微 overfull / underfull
- 个别模板 warning
- 局部风格问题

## 回退原则

- 结构问题：回 Markdown 层
- 引用问题：回 citation 增强层
- 图文问题：回 visual/layout 层
- 单纯排版问题：留在 TeX 层修

