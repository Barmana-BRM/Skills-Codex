# Material Placement

中文毕业论文场景下，建议把材料按下列职责放置。

## 交付层

- `main.tex`
- `chapters/`
- `abstract/`
- `preface/`
- `acknowledgement/`
- `achievements/`
- `references/`

## 材料层

- `pdf/`
  已发表或已投稿论文 PDF

- `Overleaf_ref/`
  Overleaf 源稿、修回稿、补充材料

## 思考层

- `codex_md/`
  中间工作层：
  - `00_thesis_outline.md`
  - `question_list.md`
  - `material_index.md`
  - `missing_info.md`
  - `chapter_role_map.md`
  - `chapter_rewrite_rules.md`
  - `figure_plan.md`
  - `mermaid/`

- `claude_md/`
  复查与终稿核对记录

## 临时排版层

- `tmp_layout/`
- `tmp_layout2/`

## 常见错误

- 把 `chapters/*.tex` 当成思考区直接反复重构
- 把 `pdf/`、`Overleaf_ref/`、`references/` 混在一起
- 没有材料索引，后续找不到哪份稿子才是权威版本

