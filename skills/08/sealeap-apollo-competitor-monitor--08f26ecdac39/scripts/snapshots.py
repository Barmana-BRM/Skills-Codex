#!/usr/bin/env python3
"""Append evidence-labelled Amazon snapshots to SQLite and render a local report."""
import argparse
import html
import json
import math
import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = '''CREATE TABLE IF NOT EXISTS snapshots (
 own_asin TEXT NOT NULL, marketplace TEXT NOT NULL, asin TEXT NOT NULL,
 source TEXT NOT NULL, data_mode TEXT NOT NULL, captured_at TEXT NOT NULL,
 payload TEXT NOT NULL, PRIMARY KEY (own_asin, marketplace, asin, source, data_mode, captured_at))'''

def normalized(record):
    for key in ('own_asin', 'asin'):
        if not re.fullmatch(r'[A-Z0-9]{10}', record.get(key, '')):
            raise ValueError(key + ' must be an explicit 10-character ASIN')
    if not re.fullmatch(r'[A-Z]{2}', record.get('marketplace', '')):
        raise ValueError('marketplace must be explicit')
    if any(not record.get(k) for k in ('source', 'captured_at', 'evidence_id', 'verification_reason')):
        raise ValueError('Missing source, capture time or verification evidence')
    if record.get('data_mode') not in {'REAL', 'SYNTHETIC'}:
        raise ValueError('data_mode must be REAL or SYNTHETIC')
    if record.get('status') not in {'verified', 'candidate', 'rejected', 'error'}:
        raise ValueError('Invalid verification status')
    if record['status'] == 'verified' and (record.get('detail_asin') != record['asin'] or record.get('relevance') != 'matched'):
        raise ValueError('Verified rows require an exact detail ASIN and matched relevance')
    when = datetime.fromisoformat(record['captured_at'].replace('Z', '+00:00'))
    if when.tzinfo is None:
        raise ValueError('Capture time must have a timezone')
    metrics = record.get('metrics')
    if not isinstance(metrics, dict) or not metrics:
        raise ValueError('metrics must be a nonempty object')
    for name, metric in metrics.items():
        if not isinstance(metric, dict) or 'value' not in metric or any(not metric.get(k) for k in ('evidence_id', 'period', 'unit', 'label')):
            raise ValueError(name + ': metric value and provenance required')
        if metric['label'] not in {'FACT', 'ESTIMATE', 'ASSUMPTION', 'UNKNOWN'}:
            raise ValueError(name + ': invalid label')
        value = metric['value']
        if isinstance(value, bool) or isinstance(value, (dict, list)):
            raise ValueError(name + ': only scalar values or null are supported')
        if isinstance(value, (int, float)) and not math.isfinite(value):
            raise ValueError(name + ': finite numbers required')
    result = dict(record)
    result['captured_at'] = when.astimezone(timezone.utc).isoformat()
    json.dumps(result, allow_nan=False)
    return result

def import_rows(db_path, records):
    if not records:
        raise ValueError('No snapshots supplied')
    batch = [normalized(record) for record in records]
    db_path.parent.mkdir(parents=True, exist_ok=True)
    existed = db_path.exists()
    conn = sqlite3.connect(db_path)
    if not existed:
        os.chmod(db_path, 0o600)
    added = duplicate = 0
    try:
        conn.execute(SCHEMA)
        with conn:
            for record in batch:
                key = tuple(record[k] for k in ('own_asin', 'marketplace', 'asin', 'source', 'data_mode', 'captured_at'))
                payload = json.dumps(record, ensure_ascii=False, sort_keys=True, allow_nan=False)
                old = conn.execute('SELECT payload FROM snapshots WHERE own_asin=? AND marketplace=? AND asin=? AND source=? AND data_mode=? AND captured_at=?', key).fetchone()
                if old:
                    if old[0] != payload:
                        raise ValueError('Snapshot conflict; historical content was not replaced')
                    duplicate += 1
                else:
                    conn.execute('INSERT INTO snapshots VALUES (?,?,?,?,?,?,?)', (*key, payload))
                    added += 1
        stored = conn.execute('SELECT COUNT(*) FROM snapshots').fetchone()[0]
        return {'added': added, 'duplicates': duplicate, 'stored': stored}
    finally:
        conn.close()

def changes(previous, current):
    output = []
    for name, after in current['metrics'].items():
        before = previous.get('metrics', {}).get(name)
        if not before or before.get('value') == after.get('value'):
            continue
        comparable = (previous['status'] == current['status'] == 'verified'
                      and all(previous[k] == current[k] for k in ('marketplace', 'asin', 'source', 'data_mode'))
                      and all(before.get(k) == after.get(k) for k in ('period', 'unit', 'label'))
                      and before.get('label') != 'UNKNOWN'
                      and before.get('value') is not None and after.get('value') is not None)
        delta = None
        if comparable and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in (before['value'], after['value'])):
            delta = after['value'] - before['value']
        output.append({'field': name, 'before': before.get('value'), 'after': after.get('value'),
                       'delta': delta, 'comparable': comparable, 'unit': after.get('unit')})
    return output

def report(db_path, output):
    if not db_path.is_file():
        raise ValueError('Database does not exist')
    conn = sqlite3.connect(db_path.resolve().as_uri() + '?mode=ro', uri=True)
    try:
        records = [json.loads(r[0]) for r in conn.execute('SELECT payload FROM snapshots ORDER BY captured_at')]
    finally:
        conn.close()
    escape = lambda x: html.escape('—' if x is None else str(x))
    blocks = []
    last = {}
    for record in records:
        key = tuple(record[k] for k in ('own_asin', 'marketplace', 'asin', 'source', 'data_mode'))
        difference = changes(last[key], record) if key in last else []
        metrics = ''.join('<tr><td>' + escape(k) + '</td><td>' + escape(v['value']) + '</td><td>' + escape(v['unit']) + '</td><td>' + escape(v['label']) + '</td><td>' + escape(v['evidence_id']) + '</td></tr>' for k, v in record['metrics'].items())
        diffs = ''.join('<li>' + escape(c['field']) + ': ' + escape(c['before']) + ' → ' + escape(c['after']) + '；差额 ' + escape(c['delta']) + ('（口径可比）' if c['comparable'] else '（口径不足，不计算差额）') + '</li>' for c in difference)
        blocks.append('<section><h2>' + escape(record['marketplace'] + ' · ' + record['asin']) + '</h2><p>' + escape(record['data_mode'] + ' · ' + record['status'] + ' · ' + record['captured_at']) + '</p><p>来源：' + escape(record['source']) + '；核验：' + escape(record['verification_reason']) + '</p><div><table><tr><th>字段</th><th>值</th><th>单位</th><th>标签</th><th>证据</th></tr>' + metrics + '</table></div><ul>' + diffs + '</ul></section>')
        last[key] = record
    page = '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Amazon 竞品快照</title><style>body{max-width:1100px;margin:auto;padding:26px;background:#f3f6fa;color:#182338;font:16px/1.6 system-ui}section{background:white;margin:20px 0;padding:22px;border-radius:12px}table{border-collapse:collapse;width:100%}td,th{text-align:left;padding:8px;border-bottom:1px solid #ddd}section div{overflow:auto}</style><h1>Amazon 竞品快照与变化</h1><p>本地历史数据；REAL 与 SYNTHETIC 分开。数据源已核验不表示前台当前可售。</p>' + ''.join(blocks) + '</html>'
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8') as handle:
        handle.write(page)
    return {'snapshots': len(records), 'output': str(output.resolve()), 'database_access': 'read_only'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    imp = sub.add_parser('import')
    imp.add_argument('--db', type=Path, required=True)
    imp.add_argument('--input', type=Path, required=True)
    out = sub.add_parser('report')
    out.add_argument('--db', type=Path, required=True)
    out.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = import_rows(args.db, json.loads(args.input.read_text(encoding='utf-8'))) if args.command == 'import' else report(args.db, args.output)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == '__main__':
    main()
