#!/usr/bin/env python3
"""Render an evidence-labelled research payload into standalone HTML/Markdown/JSON."""
import argparse
import html
import json
from pathlib import Path

LABELS = {'FACT', 'ESTIMATE', 'ASSUMPTION', 'UNKNOWN'}
STYLE = '''body{margin:0;background:#f3f6fa;color:#182338;font:16px/1.65 system-ui,sans-serif}
header,main,footer{max-width:1120px;margin:auto;padding:28px}header{border-bottom:4px solid #2474af}
section{background:white;padding:24px;margin:22px 0;border-radius:14px;box-shadow:0 3px 16px #1839570a}
h1{line-height:1.25}h2{font-size:22px}.status{display:inline-block;background:#ddeafb;padding:6px 14px;border-radius:20px}
.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px}td,th{border-bottom:1px solid #e2e8f0;padding:10px;text-align:left;vertical-align:top}
th{background:#f0f5fb;white-space:nowrap}.muted{color:#53647d}.gap{border-left:4px solid #be7a12;padding-left:14px}
pre{white-space:pre-wrap;overflow-wrap:anywhere}nav a{display:inline-block;margin:5px 12px 5px 0;color:#19679e}
@media(max-width:650px){header,main,footer{padding:14px}section{padding:16px}}
'''

def display(value):
    if value is None:
        return '—'
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, allow_nan=False)
    return str(value)

def inspect(data):
    if any(not data.get(k) for k in ('title', 'marketplace', 'data_period', 'sections')):
        raise ValueError('title, marketplace, data_period and nonempty sections are required')
    gaps = list(data.get('critical_gaps', []))
    evidence = {}
    for entry in data.get('evidence', []):
        key = entry.get('id')
        if not isinstance(key, str) or not key or key in evidence:
            raise ValueError('Evidence IDs must be nonempty and unique')
        evidence[key] = entry
        if entry.get('label') not in LABELS:
            raise ValueError('Invalid evidence label')
        if any(not entry.get(k) for k in ('source', 'collected_at', 'data_period', 'marketplace')):
            gaps.append(key + ': incomplete provenance')
        if entry.get('marketplace') != data['marketplace']:
            gaps.append(key + ': marketplace differs from report scope')
        if entry.get('label') == 'UNKNOWN':
            gaps.append(key + ': unknown evidence')
    if not evidence:
        gaps.append('No evidence supplied')
    for section in data['sections']:
        if not section.get('title') or not isinstance(section.get('rows', []), list):
            raise ValueError('Each section requires a title and rows must be a list')
        refs = section.get('evidence_ids', [])
        if not refs or any(r not in evidence for r in refs):
            gaps.append(section['title'] + ': missing or invalid evidence references')
        for row in section.get('rows', []):
            if not isinstance(row, dict):
                raise ValueError('Rows must be objects')
            if 'evidence_ids' in row and (not row['evidence_ids'] or any(r not in evidence for r in row['evidence_ids'])):
                gaps.append(section['title'] + ': row evidence references are invalid')
    decision = data.get('decision', 'HOLD')
    if decision not in {'GO', 'HOLD', 'NO-GO'}:
        raise ValueError('decision must be GO, HOLD or NO-GO')
    return sorted(set(gaps)), 'HOLD' if gaps else decision

def table(rows):
    if not rows:
        return '<p class="muted">没有可展示的记录。</p>', ''
    keys = list(dict.fromkeys(k for row in rows for k in row))
    escaped = lambda value: html.escape(display(value))
    markup = '<div class="scroll"><table><thead><tr>' + ''.join('<th>' + escaped(k) + '</th>' for k in keys) + '</tr></thead><tbody>'
    for row in rows:
        markup += '<tr>' + ''.join('<td>' + escaped(row.get(k)) + '</td>' for k in keys) + '</tr>'
    markup += '</tbody></table></div>'
    md_value = lambda value: display(value).replace('|', '\\|').replace('\n', '<br>')
    md = '| ' + ' | '.join(md_value(k) for k in keys) + ' |\n| ' + ' | '.join('---' for _ in keys) + ' |\n'
    md += '\n'.join('| ' + ' | '.join(md_value(row.get(k)) for k in keys) + ' |' for row in rows)
    return markup, md

def render(data, output):
    # Validate full serialization before writing anything.
    json.dumps(data, ensure_ascii=False, allow_nan=False)
    gaps, decision = inspect(data)
    if output.exists() and any(output.iterdir()):
        raise ValueError('Output directory must be new or empty')
    esc = lambda value: html.escape(display(value))
    scope = data['marketplace'] + ' · ' + data['data_period']
    parts = ['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
             '<title>' + esc(data['title']) + '</title><style>' + STYLE + '</style>',
             '<header><p class="muted">Amazon 研究报告 · 证据与范围</p><h1>' + esc(data['title']) + '</h1><p>' + esc(scope) + '</p><span class="status">' + decision + '</span>',
             '<nav>' + ''.join('<a href="#section-' + str(i) + '">' + esc(s['title']) + '</a>' for i, s in enumerate(data['sections'])) + '</nav></header><main>']
    md = ['# ' + data['title'], scope, '**' + decision + '**']
    if gaps:
        parts.append('<section class="gap"><h2>影响判断的缺口</h2><ul>' + ''.join('<li>' + esc(x) + '</li>' for x in gaps) + '</ul></section>')
        md.extend(['## 影响判断的缺口', '\n'.join('- ' + x for x in gaps)])
    for i, section in enumerate(data['sections']):
        markup, md_table = table(section.get('rows', []))
        summary = section.get('summary', '')
        refs = ', '.join(section.get('evidence_ids', [])) or 'UNKNOWN'
        parts.append('<section id="section-' + str(i) + '"><h2>' + esc(section['title']) + '</h2><p>' + esc(summary) + '</p>' + markup + '<p class="muted">证据：' + esc(refs) + '</p><p class="muted">限制：' + esc(section.get('limitations') or '未另列；以整体缺口为准') + '</p></section>')
        md.extend(['## ' + section['title'], summary, md_table, '证据：' + refs, '限制：' + display(section.get('limitations'))])
    evidence_html, evidence_md = table(data.get('evidence', []))
    parts.append('<section><h2>证据附录</h2>' + evidence_html + '</section></main><footer>此文件渲染已有数据。文件生成完成不表示在线取数、采购批准或业务写入已完成。</footer></html>')
    md.extend(['## 证据附录', evidence_md])
    output.mkdir(parents=True, exist_ok=True)
    (output / 'report.html').write_text('\n'.join(parts), encoding='utf-8')
    (output / 'REPORT.md').write_text('\n\n'.join(md) + '\n', encoding='utf-8')
    (output / 'payload.json').write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    result = {'render_status': 'RENDERED', 'decision': decision, 'critical_gaps': gaps,
              'files': ['report.html', 'REPORT.md', 'payload.json', 'audit.json'], 'live_data_verified': False}
    (output / 'audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding='utf-8'))
    print(json.dumps(render(data, args.output_dir), ensure_ascii=False))

if __name__ == '__main__':
    main()
