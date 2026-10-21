#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
扫描 references/node-reference.md 的二级标题（## 章节 = 各节点），算出每个
章节的起始行号(offset)与行数(limit)，输出一张「节点type → 配置位置」索引表到 stdout。

供 SKILL.md 动态注入使用（skill 加载时执行，输出替换占位符注入上下文）：

    <!-- NODE_OPTIONS_INDEX:START -->
    !`python ${CLAUDE_SKILL_DIR}/scripts/gen_node_options_index.py`
    <!-- NODE_OPTIONS_INDEX:END -->

文档结构变化后无需手动重跑，每次加载都是最新。
本脚本只输出纯表格（无副作用、不写任何文件）。
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC = os.path.join(SKILL_ROOT, 'references', 'node-reference.md')
DOC_REL = 'references/node-reference.md'

_TYPE_RE = re.compile(r'^([a-zA-Z][a-zA-Z0-9]*)\s*[—\-]')


def build_index():
    lines = open(DOC, encoding='utf-8').read().split('\n')
    total = len(lines)
    heads = [(i, l[3:].strip()) for i, l in enumerate(lines, start=1) if l.startswith('## ')]
    rows = []
    for idx, (ln, title) in enumerate(heads):
        end_ln = heads[idx + 1][0] - 1 if idx + 1 < len(heads) else total
        m = _TYPE_RE.match(title)
        node_type = m.group(1) if m else ''
        rows.append((title, node_type, ln, end_ln - ln + 1))
    return rows


def render_table(rows):
    out = [
        f'> 以下为 `{DOC_REL}` 各节点的配置位置索引（skill 加载时自动生成，始终对应当前文档）。',
        f'> 用法：用其 offset/limit 直接 `Read("{DOC_REL}", offset, limit)` 读取该节点完整配置，无需全量读。',
        '',
        '| 节点 | type | offset | limit |',
        '|------|------|--------|-------|',
    ]
    for title, typ, ln, span in rows:
        out.append(f'| {title} | `{typ}` | {ln} | {span} |')
    return '\n'.join(out)


def main():
    sys.stdout.write(render_table(build_index()) + '\n')


if __name__ == '__main__':
    main()
