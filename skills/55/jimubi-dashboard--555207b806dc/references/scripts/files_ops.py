"""
files_ops.py — 文件数据集操作预置脚本（支持单文件 singleFile 和多文件 FILES）

━━ 单文件模式（--single）━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  py files_ops.py create-bind API_BASE TOKEN PAGE_ID
      --files data.xlsx
      --single                        # ← 启用单文件模式
      --comp JPie                     # 组件类型（默认 JPie）
      --title "数据饼图"
      --x 0 --y 0 --w 12 --h 30      # 仪表盘栅格坐标
      [--ds-name "数据集名称"]
      [--col-name  <维度列名>]        # 不指定则自动选第一个 String 列
      [--col-sales <数值列名>]        # 不指定则自动选第一个非 String 列
      [--no-chart]

  数据集特征：dataType=singleFile，code=表名，dbSource=PAGE_ID
  组件特征：dataSetIzAgent=''（空字符串，区别于 FILES 的 '1'）

━━ 多文件模式（默认）━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  py files_ops.py create-bind API_BASE TOKEN PAGE_ID
      --files file1.xlsx file2.xlsx ...
      --join-on product_id            # JOIN 键（两表同名列）
      --group-by region,category      # GROUP BY 字段（逗号分隔）
      --agg amount                    # SUM 聚合字段
      --comp JMultipleBar
      --title "各大区各品类销售额"
      --x 50 --y 100 --w 1820 --h 520
      [--ds-name "数据集名称"]
      [--parent-id "示例数据集ID"]
      [--col-name  name]
      [--col-type  type]
      [--col-sales sales]
      [--no-chart]

━━ 其他子命令 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  py files_ops.py upload API_BASE TOKEN PAGE_ID --files file1.xlsx ...
  py files_ops.py list-tables API_BASE TOKEN PAGE_ID
  py files_ops.py add-chart API_BASE TOKEN PAGE_ID
      --ds-id DS_ID --ds-name "名称" --comp JBar --title "标题"
      --x 0 --y 0 --w 12 --h 30
      --fields "name:维度:String,value:数值:Integer"
"""
import sys, json, os, time, uuid, argparse, subprocess
import urllib.request

# ── 工具函数 ─────────────────────────────────────────────────────────────────

def init_bi(api_base, token):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import bi_utils as _bu
    _bu.API_BASE = api_base
    _bu.TOKEN    = token
    return _bu

def upload_file(bi, page_id, file_path, is_single=False):
    boundary  = 'bnd_' + uuid.uuid4().hex
    base      = os.path.basename(file_path)
    name, ext = os.path.splitext(base)
    # 单文件模式保留原文件名（表名需可预测）；多文件模式加 uuid 后缀避免冲突
    if is_single:
        filename = base
    else:
        ts       = uuid.uuid4().hex[:8].upper()
        filename = f'{name}{ts}{ext}'
    CRLF = b'\r\n'
    with open(file_path, 'rb') as f:
        data = f.read()
    body  = b'--' + boundary.encode() + CRLF
    body += b'Content-Disposition: form-data; name="reportId"' + CRLF + CRLF
    body += page_id.encode() + CRLF
    if is_single:
        body += b'--' + boundary.encode() + CRLF
        body += b'Content-Disposition: form-data; name="isSingle"' + CRLF + CRLF
        body += b'true' + CRLF
    body += b'--' + boundary.encode() + CRLF
    body += ('Content-Disposition: form-data; name="file"; filename="' + filename + '"').encode() + CRLF
    body += b'Content-Type: application/octet-stream' + CRLF + CRLF
    body += data + CRLF
    body += b'--' + boundary.encode() + b'--' + CRLF
    url = bi.API_BASE + '/jmreport/source/datasource/files/add'
    req = urllib.request.Request(url, data=body)
    req.add_header('Content-Type',   'multipart/form-data; boundary=' + boundary)
    req.add_header('X-Access-Token', bi.TOKEN)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode('utf-8'))

def get_file_tables(bi, page_id):
    r      = bi._request('GET', '/jmreport/source/datasource/files/get', params={'reportId': page_id})
    result = r.get('result') or {}
    return json.loads(result.get('dbUrl', '[]'))   # [{"fileName":..., "name":"jmf.Sheet1_xxx"}]

def find_col(cols, keywords):
    for kw in [k.lower() for k in keywords]:
        for c in cols:
            if kw in c.lower():
                return c
    return None

def discover_cols(bi, ds_id, ds_entity, table):
    """临时将 SQL 设为 SELECT * LIMIT 3，调 getAllChartData 获取列名列表"""
    payload = dict(ds_entity)
    payload['querySql'] = f'SELECT * FROM {table} LIMIT 3'
    bi._request('POST', '/drag/onlDragDatasetHead/edit', data=payload)
    r    = bi._request('POST', '/drag/onlDragDatasetHead/getAllChartData', data={'id': ds_id})
    rows = ((r.get('result') or {}).get('data') or [])
    return list(rows[0].keys()) if rows else []

def get_or_create_group(bi, group_name='示例数据集', default_id='1516743332632494082'):
    r      = bi._request('GET', '/drag/onlDragDatasetHead/getAllGroup')
    groups = r.get('result') or []
    if isinstance(groups, dict):
        groups = groups.get('records', [])
    for g in (groups if isinstance(groups, list) else []):
        if g.get('name') == group_name and g.get('dataType') is None:
            return g.get('id', default_id)
    # 创建
    cr = bi._request('POST', '/drag/onlDragDatasetHead/addGroup', data={'name': group_name})
    return (cr.get('result') or {}).get('id', default_id)

def add_chart_to_page(bi, page_id, comp_type, title, x, y, w, h,
                       ds_id, ds_name, data_mapping, field_option,
                       defaults_path='default_configs.json',
                       dataset_type='FILES', iz_agent='1',
                       sql=''):
    """将组件添加到页面（安全：先加载已有 template）"""
    defaults = json.load(open(defaults_path, 'r', encoding='utf-8'))
    cfg = json.loads(json.dumps(defaults.get(comp_type, {})))
    cfg.pop('w', None); cfg.pop('h', None)
    cfg['background']  = '#FFFFFF'
    cfg['borderColor'] = '#E8E8E8'
    opt = cfg.get('option', {})
    if isinstance(opt, str):
        try:    opt = json.loads(opt)
        except: opt = {}
    t = opt.get('title')
    if isinstance(t, str):
        opt['title'] = {'text': title, 'show': True}
    elif isinstance(t, dict):
        t['text'] = title
    cfg['option'] = opt
    # 像素尺寸：w*75, h*11（仪表盘栅格转像素公式）
    px_w, px_h = w * 75, h * 11
    cfg.update({
        'dataType':       2,
        'dataSetId':      ds_id,
        'dataSetName':    ds_name,
        'dataSetType':    dataset_type,
        'dataSetApi':     sql,          # 传入实际 SQL 或 API URL，禁止留空
        'dataSetMethod':  'get',
        'dataSetIzAgent': iz_agent,
        'chartData':      '[]',
        'viewLoading':    True,
        'paramOption':    [],
        'dataMapping':    data_mapping,
        'fieldOption':    field_option,
        'size':           {'width': px_w, 'height': px_h},  # 必须是像素值
        'chart':          {'subclass': comp_type, 'category': 'Bar'},
        'turnConfig':     {},
        'linkageConfig':  [],
    })
    page = bi.query_page(page_id)
    tmpl = page.get('template', [])
    comp = {
        'i':             bi._gen_uuid(),
        'component':     comp_type,
        'componentName': title,
        'x': x, 'y': y, 'w': w, 'h': h,
        'dataType':      2,
        'config':        json.dumps(cfg, ensure_ascii=False),
        'dataMapping':   {},
        'size':          {'width': px_w, 'height': px_h},   # 必须是像素值
        'chart':         {'subclass': comp_type, 'category': 'Bar'},
        'turnConfig':    {},
        'linkageConfig': [],
    }
    tmpl.insert(0, comp)
    bi._page_components[page_id] = tmpl
    bi.save_page(page_id)
    return comp['i']

# ── 子命令实现 ────────────────────────────────────────────────────────────────

def clean_old_files(bi, page_id, file_path):
    """删除与 file_path 同名（含 _N 后缀变体）的旧文件，避免服务端自动加后缀"""
    import re
    base     = os.path.basename(file_path)
    name, ext = os.path.splitext(base)
    pattern  = re.compile(rf'^{re.escape(name)}(_\d+)?{re.escape(ext)}$', re.IGNORECASE)
    existing = get_file_tables(bi, page_id)
    to_del   = [f for f in existing if pattern.match(f.get('fileName', ''))]
    if to_del:
        print(f'[0] 清理旧文件 ({len(to_del)} 个): {[f["fileName"] for f in to_del]}')
        for f in to_del:
            bi._request('DELETE', '/jmreport/source/datasource/files/del/file',
                        params={'reportId': page_id, 'fileName': f['fileName']})


def cmd_create_bind_single(bi, args):
    """单文件 singleFile 模式：isSingle 上传 → queryFileFieldBySql → singleFile 数据集 → 图表"""
    t0      = time.time()
    ds_name = args.ds_name or args.title
    parent_id = args.parent_id or get_or_create_group(bi)

    # ── 0. 清理同名旧文件（防止服务端加 _N 后缀）
    fp = args.files[0]
    clean_old_files(bi, args.page_id, fp)

    # ── 1. 上传文件（isSingle=true）
    print(f'[1] 上传: {os.path.basename(fp)} (isSingle=true)')
    r  = upload_file(bi, args.page_id, fp, is_single=True)
    print(f'    {r.get("message", "ok")}')
    if not r.get('success'):
        print(f'    失败: {r}'); sys.exit(1)

    # ── 2. 取表名
    file_list  = get_file_tables(bi, args.page_id)
    # 找本次上传的文件（最后一条，或按文件名匹配）
    base = os.path.basename(fp)
    matched = [f for f in file_list if base in f.get('fileName', '')]
    entry  = matched[-1] if matched else file_list[-1]
    table_name = entry['name']
    print(f'[2] 表名: {table_name}')

    # ── 3. queryFileFieldBySql 解析真实列名
    print(f'[3] 解析字段 (queryFileFieldBySql)...')
    fr    = bi._request('POST', '/drag/onlDragDatasetHead/queryFileFieldBySql',
                         data={'sql': f'select * from {table_name}', 'dbCode': args.page_id})
    flds  = fr.get('result') or []
    if isinstance(flds, dict):
        flds = flds.get('fieldList') or []
    print(f'    {[(f.get("fieldName"), f.get("fieldType")) for f in flds]}')

    # 字段为空时从 getAllChartData 回退
    # 🚨 修复：不能 DELETE 临时数据集——删除会触发后端清空 H2 表和 dbUrl，
    #    导致后续新建数据集查询时报 "Object not found"。
    #    解决：临时数据集创建后直接复用（edit 改名+更新字段），不再单独新建。
    fallback_ds_id = None   # 记录临时数据集 ID，供步骤4复用
    if not flds:
        print(f'    queryFileFieldBySql 返回空，尝试从数据行推断字段...')
        tmp_ds = bi._request('POST', '/drag/onlDragDatasetHead/add', data={
            'name': '__tmp__', 'code': table_name, 'dataType': 'singleFile',
            'dbSource': args.page_id, 'querySql': f'select * from {table_name}',
            'content': json.dumps(file_list, ensure_ascii=False), 'apiMethod': 'GET',
            'parentId': parent_id, 'datasetItemList': [], 'datasetParamList': [],
        })
        fallback_ds_id = (tmp_ds.get('result') or {}).get('id')
        if fallback_ds_id:
            vr  = bi._request('POST', '/drag/onlDragDatasetHead/getAllChartData', data={'id': fallback_ds_id})
            dl2 = ((vr.get('result') or {}).get('data') or [])
            if dl2:
                flds = [{'fieldName': k, 'fieldTxt': k,
                         'fieldType': 'Integer' if isinstance(v, (int, float)) else 'String',
                         'izShow': 'Y', 'orderNum': i}
                        for i, (k, v) in enumerate(dl2[0].items())]
                print(f'    从数据行推断到 {len(flds)} 个字段')
            # 不 DELETE——保留 H2 表注册，步骤4直接 edit 复用此数据集

    # ── 4. 创建或复用 singleFile 数据集（code 必须 == table_name）
    print(f'[4] 创建 singleFile 数据集...')
    dataset_items = [
        {'fieldName': f.get('fieldName'), 'fieldTxt': f.get('fieldTxt', f.get('fieldName')),
         'fieldType': f.get('fieldType', 'String'), 'izShow': 'Y', 'orderNum': i}
        for i, f in enumerate(flds)
    ]
    if fallback_ds_id:
        # 复用临时数据集：edit 改名 + 写入字段，避免重新创建触发 H2 表丢失
        ds_entity = (bi._request('GET', '/drag/onlDragDatasetHead/queryById',
                                  params={'id': fallback_ds_id}).get('result') or {})
        ds_entity['name'] = ds_name
        ds_entity['datasetItemList'] = dataset_items
        bi._request('POST', '/drag/onlDragDatasetHead/edit', data=ds_entity)
        ds_id = fallback_ds_id
    else:
        ds_resp = bi._request('POST', '/drag/onlDragDatasetHead/add', data={
            'name':             ds_name,
            'code':             table_name,   # 🚨 必须等于 table_name
            'dataType':         'singleFile',
            'dbSource':         args.page_id, # 页面 ID 作为 dbSource
            'querySql':         f'select * from {table_name}',
            'content':          json.dumps(file_list, ensure_ascii=False),
            'apiMethod':        'GET',
            'parentId':         parent_id,
            'datasetItemList':  dataset_items,
            'datasetParamList': [],
        })
        res   = ds_resp.get('result') or {}
        ds_id = res.get('id') if isinstance(res, dict) else res
    print(f'    DS_ID: {ds_id}')
    if not ds_id:
        print(f'    失败'); sys.exit(1)

    # ── 5. 验证数据
    val_r    = bi._request('POST', '/drag/onlDragDatasetHead/getAllChartData', data={'id': ds_id})
    val_data = ((val_r.get('result') or {}).get('data') or [])
    print(f'[5] 验证: {len(val_data)} 条数据')
    if val_data:
        print(f'    样本: {val_data[:1]}')

    # ── 6. 添加图表（dataSetIzAgent='' 区别于 FILES 的 '1'）
    if not args.no_chart:
        col_name  = args.col_name  if args.col_name  != 'name'  else None
        col_sales = args.col_sales if args.col_sales != 'sales' else None
        # 自动选列
        if flds:
            str_flds = [f for f in flds if f.get('fieldType', 'String').lower()
                        in ('string', 'varchar', 'text', 'char')]
            num_flds = [f for f in flds if f.get('fieldType', 'String').lower()
                        not in ('string', 'varchar', 'text', 'char')]
            if not col_name  and str_flds: col_name  = str_flds[0]['fieldName']
            if not col_sales and num_flds: col_sales = num_flds[0]['fieldName']
        col_name  = col_name  or (flds[0]['fieldName']  if flds else 'name')
        col_sales = col_sales or (flds[1]['fieldName']  if len(flds) > 1 else 'value')
        print(f'    维度={col_name}  数值={col_sales}')

        data_mapping = [
            {'filed': '维度', 'mapping': col_name},
            {'filed': '数值', 'mapping': col_sales},
        ]
        field_option = [
            {'label': f.get('fieldName'), 'text': f.get('fieldTxt', f.get('fieldName')),
             'type': f.get('fieldType', 'String'), 'value': f.get('fieldName'), 'show': 'Y'}
            for f in flds
        ] if flds else [
            {'label': col_name,  'text': '维度', 'type': 'String',  'value': col_name,  'show': 'Y'},
            {'label': col_sales, 'text': '数值', 'type': 'Integer', 'value': col_sales, 'show': 'Y'},
        ]

        scripts_dir   = os.path.dirname(os.path.abspath(__file__))
        defaults_path = os.path.join(scripts_dir, 'default_configs.json')
        comp_id = add_chart_to_page(
            bi, args.page_id, args.comp, args.title,
            args.x, args.y, args.w, args.h,
            ds_id, ds_name, data_mapping, field_option, defaults_path,
            dataset_type='singleFile', iz_agent='',  # 🚨 singleFile 必须空字符串
            sql=f'select * from {table_name}',        # 传入实际 SQL，禁止留空
        )
        print(f'[6] 图表已添加: {comp_id}')

    url = f'{bi.API_BASE}/drag/page/view/{args.page_id}'
    print(f'\n预览地址:\n{url}')
    print(f'耗时: {time.time()-t0:.1f}s')


def cmd_list_tables(bi, args):
    file_list = get_file_tables(bi, args.page_id)
    if not file_list:
        print('[!] 该大屏暂无上传文件')
        return
    print(f'大屏 {args.page_id} 已上传文件:')
    for f in file_list:
        print(f'  {f.get("fileName","?"):30s} -> {f.get("name")}')

def cmd_upload(bi, args):
    t0 = time.time()
    for fp in args.files:
        print(f'上传: {fp} ...')
        r = upload_file(bi, args.page_id, fp)
        print(f'  {r.get("message","ok")}')
    file_list = get_file_tables(bi, args.page_id)
    print('当前表名:')
    for f in file_list:
        print(f'  {f.get("name")}')
    print(f'耗时: {time.time()-t0:.1f}s')

def cmd_add_chart(bi, args):
    t0 = time.time()
    # 解析 --fields "name:大区:String,type:品类:String,sales:销售额:Integer"
    data_mapping = []
    field_option = []
    SLOT_MAP_3 = ['分组', '维度', '数值']
    SLOT_MAP_2 = ['维度', '数值']
    raw_fields = [f.strip() for f in args.fields.split(',') if f.strip()]
    slots = SLOT_MAP_3 if len(raw_fields) >= 3 else SLOT_MAP_2
    for i, part in enumerate(raw_fields):
        parts = part.split(':')
        fname = parts[0].strip()
        ftxt  = parts[1].strip() if len(parts) > 1 else fname
        ftype = parts[2].strip() if len(parts) > 2 else 'String'
        slot  = slots[i] if i < len(slots) else fname
        data_mapping.append({'filed': slot, 'mapping': fname})
        field_option.append({'label': fname, 'text': ftxt, 'type': ftype, 'value': fname, 'show': 'Y'})
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    defaults_path = os.path.join(scripts_dir, 'default_configs.json')
    comp_id = add_chart_to_page(
        bi, args.page_id, args.comp, args.title,
        args.x, args.y, args.w, args.h,
        args.ds_id, args.ds_name,
        data_mapping, field_option, defaults_path
    )
    print(f'[OK] 组件已添加: {comp_id}')
    url = f'{bi.API_BASE}/drag/share/view/{args.page_id}?token={bi.TOKEN}&tenantId=2'
    print(f'预览地址:\n{url}')
    print(f'耗时: {time.time()-t0:.1f}s')

def cmd_create_bind(bi, args):
    # 单文件模式路由
    if args.single:
        if not args.files:
            print('[!] --single 模式需要 --files 指定一个文件'); sys.exit(1)
        return cmd_create_bind_single(bi, args)

    t0 = time.time()
    ds_name   = args.ds_name or args.title
    parent_id = args.parent_id or get_or_create_group(bi)

    # ── 1. 创建空 FILES 数据集
    add_r = bi._request('POST', '/drag/onlDragDatasetHead/add', data={
        'name':     ds_name,
        'code':     'files_' + uuid.uuid4().hex[:8],
        'dataType': 'FILES',
        'dbSource': args.page_id,
        'querySql': '',
        'parentId': parent_id,
    })
    ds_id = (add_r.get('result') or {}).get('id')
    print(f'[1] 数据集已创建: {ds_id}')
    if not ds_id:
        print(f'    失败: {add_r}'); sys.exit(1)

    # ── 2. 上传文件
    for fp in args.files:
        print(f'[2] 上传: {os.path.basename(fp)}')
        r = upload_file(bi, args.page_id, fp)
        print(f'    {r.get("message","ok")}')

    # ── 3. 获取表名
    file_list = get_file_tables(bi, args.page_id)
    print(f'[3] 表名: {[f["name"] for f in file_list]}')

    # ── 4. queryById 取实体
    qb_r      = bi._request('GET', '/drag/onlDragDatasetHead/queryById', params={'id': ds_id})
    ds_entity = (qb_r.get('result') or {})

    # ── 5. 自动推断列名（如未指定 SQL）
    col_name  = args.col_name  or 'name'
    col_type  = args.col_type  or 'type'
    col_sales = args.col_sales or 'sales'

    if args.group_by and args.agg and len(args.files) >= 2:
        # 多文件 JOIN 模式
        kws = [k.strip() for k in args.group_by.split(',')]
        join_col = args.join_on

        # 匹配表：按文件名关键词
        ordered_tables = []
        for fp in args.files:
            kw = os.path.splitext(os.path.basename(fp))[0].lower()
            tbl = next((f['name'] for f in file_list if kw in f['name'].lower()),
                       f'jmf.Sheet1_{kw}_excel')
            ordered_tables.append(tbl)

        # 探查每张表列名
        all_cols = {}
        for i, tbl in enumerate(ordered_tables):
            cols = discover_cols(bi, ds_id, ds_entity, tbl)
            alias = chr(ord('a') + i)
            all_cols[alias] = (tbl, cols)
            print(f'[4] 表 {tbl} 列: {cols}')

        # 推断 GROUP BY 和 AGG 字段所在表
        aliases = list(all_cols.keys())
        group_exprs = []
        group_aliases = [col_name, col_type][:len(kws)]
        for i, kw in enumerate(kws):
            found = None
            for alias in aliases:
                _, cols = all_cols[alias]
                col = find_col(cols, [kw])
                if col:
                    found = (alias, col)
                    break
            if found:
                group_exprs.append(f'{found[0]}.{found[1]} as {group_aliases[i]}')
            else:
                group_exprs.append(f'{kw} as {group_aliases[i]}')

        agg_field = None
        for alias in aliases:
            _, cols = all_cols[alias]
            agg_field = find_col(cols, [args.agg])
            if agg_field:
                agg_alias = alias
                break
        agg_expr = f'SUM({agg_alias}.{agg_field}) as {col_sales}' if agg_field else f'SUM({args.agg}) as {col_sales}'

        # 构建 JOIN
        a0, (t0_tbl, _) = list(all_cols.items())[0]
        a1, (t1_tbl, _) = list(all_cols.items())[1]
        agg_sql = (
            f"SELECT {', '.join(group_exprs)}, {agg_expr}\n"
            f"FROM {t0_tbl} {a0}\n"
            f"JOIN {t1_tbl} {a1} ON {a0}.{join_col} = {a1}.{join_col}\n"
            f"GROUP BY {', '.join(g.split(' as ')[0] for g in group_exprs)}\n"
            f"ORDER BY {', '.join(g.split(' as ')[0] for g in group_exprs)}"
        )
    elif len(args.files) == 1:
        # 单表聚合
        kw  = os.path.splitext(os.path.basename(args.files[0]))[0].lower()
        tbl = next((f['name'] for f in file_list if kw in f['name'].lower()),
                   f'jmf.Sheet1_{kw}_excel')
        cols = discover_cols(bi, ds_id, ds_entity, tbl)
        print(f'[4] 表 {tbl} 列: {cols}')
        agg_sql = f'SELECT * FROM {tbl} LIMIT 50'
    else:
        agg_sql = f"SELECT * FROM {ordered_tables[0]} LIMIT 50"

    print(f'[5] SQL:\n{agg_sql}')

    # ── 6. 更新数据集（写 SQL + 字段列表）
    num_groups = len(kws) if args.group_by else 1
    fields = [{'fieldName': col_name, 'fieldTxt': '维度1', 'fieldType': 'String', 'izShow': 'Y', 'orderNum': 0}]
    if num_groups >= 2:
        fields.append({'fieldName': col_type, 'fieldTxt': '维度2', 'fieldType': 'String', 'izShow': 'Y', 'orderNum': 1})
    fields.append({'fieldName': col_sales, 'fieldTxt': '数值', 'fieldType': 'Integer', 'izShow': 'Y', 'orderNum': len(fields)})

    payload = dict(ds_entity)
    payload['querySql']       = agg_sql
    payload['datasetItemList'] = fields
    bi._request('POST', '/drag/onlDragDatasetHead/edit', data=payload)

    # ── 7. 验证
    val_r    = bi._request('POST', '/drag/onlDragDatasetHead/getAllChartData', data={'id': ds_id})
    val_data = ((val_r.get('result') or {}).get('data') or [])
    print(f'[6] 验证: {len(val_data)} 条数据')
    if val_data:
        print(f'    样本: {val_data[:2]}')

    # ── 8. 添加图表
    if not args.no_chart:
        # 根据 group 数量决定 slot
        if num_groups >= 2:
            data_mapping = [
                {'filed': '分组', 'mapping': col_type},
                {'filed': '维度', 'mapping': col_name},
                {'filed': '数值', 'mapping': col_sales},
            ]
            field_option = [
                {'label': col_name,  'text': '大区',  'type': 'String',  'value': col_name,  'show': 'Y'},
                {'label': col_type,  'text': '品类',  'type': 'String',  'value': col_type,  'show': 'Y'},
                {'label': col_sales, 'text': '数值',  'type': 'Integer', 'value': col_sales, 'show': 'Y'},
            ]
        else:
            data_mapping = [
                {'filed': '维度', 'mapping': col_name},
                {'filed': '数值', 'mapping': col_sales},
            ]
            field_option = [
                {'label': col_name,  'text': '维度', 'type': 'String',  'value': col_name,  'show': 'Y'},
                {'label': col_sales, 'text': '数值', 'type': 'Integer', 'value': col_sales, 'show': 'Y'},
            ]

        scripts_dir   = os.path.dirname(os.path.abspath(__file__))
        defaults_path = os.path.join(scripts_dir, 'default_configs.json')
        comp_id = add_chart_to_page(
            bi, args.page_id, args.comp, args.title,
            args.x, args.y, args.w, args.h,
            ds_id, ds_name, data_mapping, field_option, defaults_path,
            sql=agg_sql,  # 传入实际 SQL，禁止留空
        )
        print(f'[7] 图表已添加: {comp_id}')

    url = f'{bi.API_BASE}/drag/share/view/{args.page_id}?token={bi.TOKEN}&tenantId=2'
    print(f'\n预览地址:\n{url}')
    print(f'耗时: {time.time()-t0:.1f}s')

# ── CLI 入口 ──────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description='FILES 多文件数据集操作')
    p.add_argument('command',   choices=['create-bind','upload','list-tables','add-chart'])
    p.add_argument('api_base')
    p.add_argument('token')
    p.add_argument('page_id')
    p.add_argument('--files',      nargs='+', default=[])
    p.add_argument('--single',     action='store_true', help='单文件 singleFile 模式')
    p.add_argument('--join-on',    default='')
    p.add_argument('--group-by',   default='')
    p.add_argument('--agg',        default='')
    p.add_argument('--comp',       default='JPie', help='组件类型（single 默认 JPie，多文件默认 JMultipleBar）')
    p.add_argument('--title',      default='图表')
    p.add_argument('--x',          type=int, default=0)
    p.add_argument('--y',          type=int, default=0)
    p.add_argument('--w',          type=int, default=12)
    p.add_argument('--h',          type=int, default=30)
    p.add_argument('--ds-name',    default='')
    p.add_argument('--ds-id',      default='')
    p.add_argument('--parent-id',  default='')
    p.add_argument('--col-name',   default='name')
    p.add_argument('--col-type',   default='type')
    p.add_argument('--col-sales',  default='sales')
    p.add_argument('--fields',     default='')   # 仅 add-chart 用
    p.add_argument('--no-chart',   action='store_true')
    args = p.parse_args()

    # bi_utils 与本脚本同目录
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, scripts_dir)
    bi = init_bi(args.api_base, args.token)

    if   args.command == 'list-tables':  cmd_list_tables(bi, args)
    elif args.command == 'upload':       cmd_upload(bi, args)
    elif args.command == 'add-chart':    cmd_add_chart(bi, args)
    elif args.command == 'create-bind':  cmd_create_bind(bi, args)

if __name__ == '__main__':
    main()
