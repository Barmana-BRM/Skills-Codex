"""
bpmn_layout_engine.py — 通用 BPMN 布局引擎

用途：
    从 JeecgBoot/Flowable BPMN XML 中提取拓扑结构，自动计算正确坐标
    并重写 <bpmndi:BPMNDiagram> 区块，解决节点重叠、连线穿节点等问题。

用法（CLI）：
    python bpmn_layout_engine.py \\
        --api-base http://192.168.1.66:8080 \\
        --token <JWT> \\
        --process-id <ID> \\
        [--force]

    --force：跳过检测，无论是否有问题都强制重建布局。

用法（Python）：
    from bpmn_layout_engine import recompute_layout, fix_layout_if_needed

    new_xml = recompute_layout(xml_str)
    fixed = fix_layout_if_needed(api_base, token, process_id)
"""

import re
import json
import base64
import sys
import os
import argparse
import collections
import xml.etree.ElementTree as ET
import urllib.request
import urllib.parse

# ─────────────────────────────────────────────
# 节点尺寸配置
# ─────────────────────────────────────────────
NODE_W = {
    'startEvent': 36, 'endEvent': 36,
    'userTask': 100, 'serviceTask': 100, 'scriptTask': 100, 'callActivity': 100,
    'exclusiveGateway': 50, 'parallelGateway': 50, 'inclusiveGateway': 50,
}
NODE_H = {
    'startEvent': 36, 'endEvent': 36,
    'userTask': 80, 'serviceTask': 80, 'scriptTask': 80, 'callActivity': 80,
    'exclusiveGateway': 50, 'parallelGateway': 50, 'inclusiveGateway': 50,
}

# 布局常量
BASE_X = 400
BASE_Y = 40
Y_GAP = 40
COL_STRIDE = 220

# 支持的节点类型（正则用）
NODE_TYPES = [
    'startEvent', 'endEvent', 'userTask', 'serviceTask', 'scriptTask',
    'callActivity', 'exclusiveGateway', 'parallelGateway', 'inclusiveGateway',
]

# ─────────────────────────────────────────────
# 1. 图解析
# ─────────────────────────────────────────────

def _attr(tag_str, attr):
    """从标签字符串中提取指定属性值，找不到返回 None。"""
    m = re.search(r'\b' + re.escape(attr) + r'\s*=\s*"([^"]*)"', tag_str)
    return m.group(1) if m else None


def parse_bpmn_graph(xml):
    """
    从 BPMN XML 中解析节点、边和默认流信息。
    仅处理主流程层（跳过 subProcess 内部节点）。
    返回 (nodes, edges, default_flows)：
      nodes: {id: {'type': str, 'name': str}}
      edges: {id: {'source': str, 'target': str, 'name': str}}
      default_flows: set of flow IDs that are default flows
    """
    nodes = {}
    edges = {}
    default_flows = set()

    # 去除 subProcess 内部内容，避免误解析内嵌节点
    # 用简单方法：找到 subProcess 开闭区间并跳过
    xml_main = _remove_subprocess_content(xml)

    # 解析节点
    ns_pat = r'(?:bpmn2?:)?'
    for ntype in NODE_TYPES:
        pattern = r'<' + ns_pat + ntype + r'([^>]*/?>)'
        for m in re.finditer(pattern, xml_main, re.DOTALL):
            tag_body = m.group(1)
            nid = _attr(tag_body, 'id')
            name = _attr(tag_body, 'name') or ''
            default = _attr(tag_body, 'default')
            if nid:
                nodes[nid] = {'type': ntype, 'name': name}
                if default:
                    default_flows.add(default)

    # 解析 sequenceFlow
    sf_pattern = r'<' + ns_pat + r'sequenceFlow([^>]*/?>)'
    for m in re.finditer(sf_pattern, xml_main, re.DOTALL):
        tag_body = m.group(1)
        fid = _attr(tag_body, 'id')
        src = _attr(tag_body, 'sourceRef')
        tgt = _attr(tag_body, 'targetRef')
        name = _attr(tag_body, 'name') or ''
        if fid and src and tgt:
            edges[fid] = {'source': src, 'target': tgt, 'name': name}

    print(f"[parse] 节点数={len(nodes)}, 边数={len(edges)}, 默认流={default_flows}")
    return nodes, edges, default_flows


def _remove_subprocess_content(xml):
    """
    将 subProcess 标签内部内容替换为占位符，
    防止内嵌节点被当作主流程节点解析。
    """
    ns_pat = r'(?:bpmn2?:)?'
    result = xml
    # 逐步替换最内层 subProcess（非贪婪，支持嵌套需多次迭代）
    for _ in range(5):
        new = re.sub(
            r'<' + ns_pat + r'subProcess\b[^>]*>.*?</' + ns_pat + r'subProcess>',
            '<subProcess id="__sp_placeholder__"/>',
            result, flags=re.DOTALL
        )
        if new == result:
            break
        result = new
    return result


def build_graph(nodes, edges):
    """
    构建邻接表和入度表。
    返回 (succs, preds, in_degree)：
      succs: {node_id: [node_id, ...]}
      preds: {node_id: [node_id, ...]}
      in_degree: {node_id: int}
    """
    succs = {nid: [] for nid in nodes}
    preds = {nid: [] for nid in nodes}
    in_degree = {nid: 0 for nid in nodes}

    for eid, e in edges.items():
        src, tgt = e['source'], e['target']
        if src in nodes and tgt in nodes:
            succs[src].append(tgt)
            preds[tgt].append(src)
            in_degree[tgt] += 1

    return succs, preds, in_degree


# ─────────────────────────────────────────────
# 2. 排名分配（Y 轴）— 最长路径算法
# ─────────────────────────────────────────────

def assign_ranks(nodes, succs, preds, in_degree):
    """
    用 Kahn 拓扑排序 + 最长路径算法分配每个节点的 rank（层级）。
    rank[start] = 0，rank[node] = max(rank[pred] + 1)
    返回 rank dict。
    """
    rank = {nid: 0 for nid in nodes}
    # Kahn 拓扑排序
    in_deg = dict(in_degree)
    queue = collections.deque([nid for nid in nodes if in_deg[nid] == 0])
    topo_order = []

    while queue:
        nid = queue.popleft()
        topo_order.append(nid)
        for succ in succs[nid]:
            rank[succ] = max(rank[succ], rank[nid] + 1)
            in_deg[succ] -= 1
            if in_deg[succ] == 0:
                queue.append(succ)

    # 处理环（若有，给予当前最大 rank + 1）
    for nid in nodes:
        if nid not in rank or nid not in [x for x in topo_order]:
            rank[nid] = max(rank.values(), default=0) + 1

    print(f"[rank] 层级分配: {dict(sorted(rank.items(), key=lambda x: x[1]))}")
    return rank, topo_order


# ─────────────────────────────────────────────
# 3. 网关分支检测
# ─────────────────────────────────────────────

def find_branches_and_join(gateway_id, succs, rank, nodes):
    """
    检测 split 网关的各分支及 join 节点。
    返回 (branches, join_node)：
      branches: [(branch_start, [中间节点列表]), ...]（按路径长度降序）
      join_node: str or None
    """
    branch_starts = succs.get(gateway_id, [])
    if len(branch_starts) <= 1:
        return [(b, []) for b in branch_starts], None

    # 计算每个节点可从哪些 branch_start 到达（DFS）
    def reachable_from(start, visited=None):
        """返回从 start 可达的所有节点集合（不含 start 本身）。"""
        if visited is None:
            visited = set()
        for succ in succs.get(start, []):
            if succ not in visited:
                visited.add(succ)
                reachable_from(succ, visited)
        return visited

    reachable = {bs: reachable_from(bs) for bs in branch_starts}

    # join = 拓扑序中第一个可从 ALL branch_starts 到达的节点
    # 按 rank 升序排列所有节点来找
    all_nodes_by_rank = sorted(nodes.keys(), key=lambda n: rank.get(n, 0))
    join_node = None
    for candidate in all_nodes_by_rank:
        if candidate == gateway_id:
            continue
        if all(candidate in reachable[bs] for bs in branch_starts):
            # 确保 rank 比所有 branch_starts 都大
            if rank.get(candidate, 0) > rank.get(gateway_id, 0):
                join_node = candidate
                break

    # 计算每个分支的中间节点路径（从 branch_start 到 join，排除 join 本身）
    def path_to_join(start, join):
        """BFS 找从 start 到 join 的路径中间节点（不含 start 和 join）。"""
        if join is None:
            return list(reachable_from(start))
        # DFS 收集路径（简化：按 rank 顺序线性推进）
        visited = []
        cur = start
        seen = {gateway_id, start}
        # 如果 start 直接等于 join，路径为空（不应出现）
        if start == join:
            return []
        # 若 start 是 join 的直接前驱，路径为空（bypass）
        if join in succs.get(start, []):
            return []
        # 否则收集中间节点
        stack = [start]
        path_nodes = []
        while stack:
            node = stack.pop()
            for succ in succs.get(node, []):
                if succ == join:
                    continue
                if succ not in seen:
                    seen.add(succ)
                    path_nodes.append(succ)
                    stack.append(succ)
        return path_nodes

    branches = []
    for bs in branch_starts:
        path = path_to_join(bs, join_node)
        branches.append((bs, path))

    # 按路径长度降序排列（最长路径分配中心列）
    branches.sort(key=lambda x: len(x[1]), reverse=True)

    return branches, join_node


# ─────────────────────────────────────────────
# 4. 列分配（X 轴）
# ─────────────────────────────────────────────

def assign_columns(nodes, succs, preds, rank, topo_order, default_flows, edges):
    """
    递归 DFS 分配每个节点的列偏移（col）。
    中心列=0，右侧=+1,+2...，左侧=-1,-2...
    返回 col dict 和 bypass_cols。

    bypass_cols: {gateway_id: {branch_start: col_offset}}
    记录所有非中心分支（offset != 0）的 gateway→branch_start 边的绕行列偏移，
    供 compute_waypoints 用于边绕行路由（即使 branch_start 最终落在中心列也适用）。
    """
    col = {nid: 0 for nid in nodes}
    visited = set()
    bypass_cols = {}

    def dfs(node_id, current_col):
        if node_id in visited:
            return
        visited.add(node_id)
        col[node_id] = current_col

        out_nodes = succs.get(node_id, [])
        if len(out_nodes) <= 1:
            # 线性节点，继续当前列
            for succ in out_nodes:
                dfs(succ, current_col)
        else:
            # split 网关：分配列偏移
            branches, join_node = find_branches_and_join(node_id, succs, rank, nodes)

            # 列偏移序列：[0, +1, -1, +2, -2, ...]
            offsets = _col_offsets(len(branches))
            bypass_cols[node_id] = {}

            for i, (branch_start, path) in enumerate(branches):
                branch_col = current_col + offsets[i]

                # 所有非中心分支（offset != 0）的 gateway→branch_start 边都需要绕行路由，
                # 记录绕行列偏移（即使 branch_start 已被另一分支访问也要记录）
                if offsets[i] != 0:
                    bypass_cols[node_id][branch_start] = offsets[i]

                if not path:
                    # bypass 分支（直接连到 join/target 无中间节点）
                    # 不覆盖已被更长分支正确分配列的节点
                    if branch_start not in visited:
                        col[branch_start] = branch_col
                        visited.add(branch_start)
                else:
                    # 有中间节点的分支：DFS 访问 branch_start 及路径上的中间节点
                    if branch_start not in visited:
                        dfs(branch_start, branch_col)
                    for mid in path:
                        if mid not in visited:
                            dfs(mid, branch_col)

            # join 节点回到网关所在列
            if join_node and join_node not in visited:
                dfs(join_node, current_col)

    # 从 rank=0 的节点开始
    starts = [nid for nid in nodes if rank.get(nid, 0) == 0]
    if not starts:
        starts = [topo_order[0]] if topo_order else list(nodes.keys())[:1]

    for s in starts:
        dfs(s, 0)

    # 补充未访问节点
    for nid in nodes:
        if nid not in visited:
            col[nid] = 0

    print(f"[col] 列分配: {dict(sorted(col.items(), key=lambda x: col[x[0]]))}")
    return col, bypass_cols


def _col_offsets(n):
    """生成 n 个列偏移：[0, +1, -1, +2, -2, ...]。"""
    offsets = []
    for i in range(n):
        if i == 0:
            offsets.append(0)
        elif i % 2 == 1:
            offsets.append((i + 1) // 2)
        else:
            offsets.append(-i // 2)
    return offsets


# ─────────────────────────────────────────────
# 5. 像素坐标计算
# ─────────────────────────────────────────────

def compute_pixel_coords(nodes, rank, col):
    """
    根据 rank 和 col 计算每个节点的像素坐标（中心点 cx, cy）及 bounds。
    返回 coords: {node_id: {'cx': int, 'cy': int, 'x': int, 'y': int, 'w': int, 'h': int}}
    """
    # 每层的最大高度
    max_rank = max(rank.values(), default=0)
    rank_max_h = {}
    for nid, r in rank.items():
        ntype = nodes[nid]['type']
        h = NODE_H.get(ntype, 80)
        rank_max_h[r] = max(rank_max_h.get(r, 0), h)

    # 计算每层的 cy（中心 y）
    rank_cy = {}
    cum_y = BASE_Y
    for r in range(max_rank + 1):
        mh = rank_max_h.get(r, 80)
        rank_cy[r] = cum_y + mh // 2
        cum_y += mh + Y_GAP

    coords = {}
    for nid, info in nodes.items():
        ntype = info['type']
        w = NODE_W.get(ntype, 100)
        h = NODE_H.get(ntype, 80)
        r = rank.get(nid, 0)
        c = col.get(nid, 0)
        cx = BASE_X + c * COL_STRIDE
        cy = rank_cy.get(r, BASE_Y + r * (80 + Y_GAP))
        coords[nid] = {
            'cx': cx, 'cy': cy,
            'x': cx - w // 2, 'y': cy - h // 2,
            'w': w, 'h': h,
        }

    return coords


# ─────────────────────────────────────────────
# 6. 边路由（L 形折线）
# ─────────────────────────────────────────────

def compute_waypoints(edges, nodes, coords, col, bypass_cols):
    """
    为每条 sequenceFlow 计算折线 waypoints。
    返回 edge_waypoints: {edge_id: [(x, y), ...]}
    """
    edge_waypoints = {}

    # 找出 bypass edges（网关直连 join 且无中间节点）
    # bypass_cols: {gateway_id: {branch_start: col_offset}}
    bypass_edges = set()
    bypass_edge_info = {}  # edge_id -> (gw_id, branch_start, col_offset)
    for gw_id, branches in bypass_cols.items():
        for bs, col_off in branches.items():
            # 找 gw -> bs 的 edge
            for eid, e in edges.items():
                if e['source'] == gw_id and e['target'] == bs:
                    bypass_edges.add(eid)
                    bypass_edge_info[eid] = (gw_id, bs, col_off)

    for eid, e in edges.items():
        src = e['source']
        tgt = e['target']
        if src not in coords or tgt not in coords:
            edge_waypoints[eid] = []
            continue

        sc = coords[src]
        tc = coords[tgt]
        src_cx, src_cy = sc['cx'], sc['cy']
        tgt_cx, tgt_cy = tc['cx'], tc['cy']
        src_bottom = sc['y'] + sc['h']
        tgt_top = tc['y']
        src_col = col.get(src, 0)
        tgt_col = col.get(tgt, 0)

        if eid in bypass_edges:
            # bypass 边：网关直连 join，无中间节点，需绕行
            gw_id, bs_id, col_off = bypass_edge_info[eid]
            bypass_cx = BASE_X + col_off * COL_STRIDE
            sw = sc['w']
            tw = tc['w']
            if col_off > 0:
                wps = [
                    (src_cx + sw // 2, src_cy),
                    (bypass_cx, src_cy),
                    (bypass_cx, tgt_cy),
                    (tgt_cx + tw // 2, tgt_cy),
                ]
            elif col_off < 0:
                wps = [
                    (src_cx - sw // 2, src_cy),
                    (bypass_cx, src_cy),
                    (bypass_cx, tgt_cy),
                    (tgt_cx - tw // 2, tgt_cy),
                ]
            else:
                # 同列 bypass（中心列直通）
                wps = [(src_cx, src_bottom), (tgt_cx, tgt_top)]
        elif src_col == tgt_col:
            # 同列节点：直连
            wps = [(src_cx, src_bottom), (tgt_cx, tgt_top)]
        else:
            # 普通跨列边
            mid_y = (src_bottom + tgt_top) // 2
            wps = [
                (src_cx, src_bottom),
                (src_cx, mid_y),
                (tgt_cx, mid_y),
                (tgt_cx, tgt_top),
            ]

        edge_waypoints[eid] = wps

    return edge_waypoints


# ─────────────────────────────────────────────
# 7. 连线 label 位置
# ─────────────────────────────────────────────

def compute_label_position(waypoints, label_w=80, label_h=20):
    """
    根据 waypoints 计算 label 位置（BPMNLabel dc:Bounds）。
    优先找最长水平段（label 在段中点上方 18px），
    其次找最长垂直段（label 在段右侧 5px）。
    返回 (x, y, w, h) 或 None。
    """
    if not waypoints or len(waypoints) < 2:
        return None

    best_h_seg = None  # (length, mid_x, mid_y)
    best_v_seg = None  # (length, mid_x, mid_y)

    for i in range(len(waypoints) - 1):
        x1, y1 = waypoints[i]
        x2, y2 = waypoints[i + 1]
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        if dy == 0 and dx > 0:
            # 水平段
            mid_x = (x1 + x2) // 2
            mid_y = min(y1, y2)
            if best_h_seg is None or dx > best_h_seg[0]:
                best_h_seg = (dx, mid_x, mid_y)
        elif dx == 0 and dy > 0:
            # 垂直段
            mid_x = x1
            mid_y = (y1 + y2) // 2
            if best_v_seg is None or dy > best_v_seg[0]:
                best_v_seg = (dy, mid_x, mid_y)

    if best_h_seg:
        _, mid_x, mid_y = best_h_seg
        lx = mid_x - label_w // 2
        ly = mid_y - label_h - 18
        return (lx, ly, label_w, label_h)
    elif best_v_seg:
        _, mid_x, mid_y = best_v_seg
        lx = mid_x + 5
        ly = mid_y - label_h // 2
        return (lx, ly, label_w, label_h)

    # fallback：两端点中点
    x1, y1 = waypoints[0]
    x2, y2 = waypoints[-1]
    return ((x1 + x2) // 2 - label_w // 2, (y1 + y2) // 2 - label_h - 5, label_w, label_h)


# ─────────────────────────────────────────────
# 8. BPMNDiagram 生成
# ─────────────────────────────────────────────

GATEWAY_TYPES = {'exclusiveGateway', 'parallelGateway', 'inclusiveGateway'}


def build_bpmn_diagram(process_id, nodes, edges, coords, edge_waypoints, default_flows):
    """
    生成完整的 <bpmndi:BPMNDiagram> XML 块。
    包含所有 BPMNShape 和 BPMNEdge（含 waypoints 和有名 flow 的 BPMNLabel）。
    """
    lines = []
    lines.append(f'  <bpmndi:BPMNDiagram id="BPMNDiagram_{process_id}">')
    lines.append(f'    <bpmndi:BPMNPlane id="BPMNPlane_{process_id}" bpmnElement="{process_id}">')

    # BPMNShape
    for nid, info in nodes.items():
        c = coords.get(nid)
        if not c:
            continue
        ntype = info['type']
        x, y, w, h = c['x'], c['y'], c['w'], c['h']
        is_gw = ntype in GATEWAY_TYPES
        marker = ' isMarkerVisible="true"' if is_gw else ''
        lines.append(f'      <bpmndi:BPMNShape id="{nid}_di" bpmnElement="{nid}"{marker}>')
        lines.append(f'        <dc:Bounds x="{x}" y="{y}" width="{w}" height="{h}"/>')
        # BPMNLabel for shape（包含名称的节点）
        name = info.get('name', '')
        if name:
            lx = x + w // 2 - 40
            ly = y + h + 2
            lines.append(f'        <bpmndi:BPMNLabel>')
            lines.append(f'          <dc:Bounds x="{lx}" y="{ly}" width="80" height="20"/>')
            lines.append(f'        </bpmndi:BPMNLabel>')
        else:
            lines.append(f'        <bpmndi:BPMNLabel/>')
        lines.append(f'      </bpmndi:BPMNShape>')

    # BPMNEdge
    for eid, e in edges.items():
        src = e['source']
        tgt = e['target']
        name = e.get('name', '')
        wps = edge_waypoints.get(eid, [])

        lines.append(f'      <bpmndi:BPMNEdge id="{eid}_di" bpmnElement="{eid}">')
        for x, y in wps:
            lines.append(f'        <di:waypoint x="{x}" y="{y}"/>')

        # BPMNLabel（有名称的 flow）
        if name:
            lpos = compute_label_position(wps)
            if lpos:
                lx, ly, lw, lh = lpos
                lines.append(f'        <bpmndi:BPMNLabel>')
                lines.append(f'          <dc:Bounds x="{lx}" y="{ly}" width="{lw}" height="{lh}"/>')
                lines.append(f'        </bpmndi:BPMNLabel>')
            else:
                lines.append(f'        <bpmndi:BPMNLabel/>')
        else:
            lines.append(f'        <bpmndi:BPMNLabel/>')

        lines.append(f'      </bpmndi:BPMNEdge>')

    lines.append('    </bpmndi:BPMNPlane>')
    lines.append('  </bpmndi:BPMNDiagram>')

    return '\n'.join(lines)


# ─────────────────────────────────────────────
# 9. 布局问题检测
# ─────────────────────────────────────────────

def _parse_shapes_from_xml(xml):
    """从 BPMNDiagram XML 中提取所有 BPMNShape 的 id 和 dc:Bounds。"""
    shapes = {}
    pattern = r'<bpmndi:BPMNShape[^>]+bpmnElement="([^"]+)"[^>]*>.*?<dc:Bounds\s+([^/]+)/>'
    for m in re.finditer(pattern, xml, re.DOTALL):
        eid = m.group(1)
        attrs_str = m.group(2)
        # 跳过边界事件
        if re.match(r'^(timer_|signal_boundary_|msg_boundary_)', eid):
            continue
        bx = _attr(attrs_str + '"', 'x') or _attr(' x="' + attrs_str, 'x')
        # 简单提取 x, y, width, height
        def ga(a):
            mm = re.search(r'\b' + a + r'\s*=\s*"?([0-9.]+)"?', attrs_str)
            return float(mm.group(1)) if mm else 0
        x, y, w, h = ga('x'), ga('y'), ga('width'), ga('height')
        shapes[eid] = (x, y, w, h)
    return shapes


def _parse_edges_from_xml(xml):
    """从 BPMNDiagram XML 中提取所有 BPMNEdge 的 waypoints。"""
    edge_wps = {}
    edge_pat = r'<bpmndi:BPMNEdge[^>]+bpmnElement="([^"]+)"[^>]*>(.*?)</bpmndi:BPMNEdge>'
    wp_pat = r'<di:waypoint\s+x="([0-9.]+)"\s+y="([0-9.]+)"'
    for m in re.finditer(edge_pat, xml, re.DOTALL):
        eid = m.group(1)
        body = m.group(2)
        wps = [(float(mm.group(1)), float(mm.group(2))) for mm in re.finditer(wp_pat, body)]
        edge_wps[eid] = wps
    return edge_wps


def _rects_overlap(r1, r2, gap=5):
    """检测两个矩形是否重叠（r=(x,y,w,h)）。gap 为最小安全距离。"""
    x1, y1, w1, h1 = r1
    x2, y2, w2, h2 = r2
    return not (x1 + w1 + gap <= x2 or x2 + w2 + gap <= x1 or
                y1 + h1 + gap <= y2 or y2 + h2 + gap <= y1)


def _segment_intersects_rect(p1, p2, rect):
    """检测线段 p1-p2 是否穿越矩形内部（排除端点在矩形上的情况）。"""
    x, y, w, h = rect
    # 用简单的 AABB 线段裁剪（Cohen-Sutherland 简化版）
    rx1, ry1, rx2, ry2 = x, y, x + w, y + h

    # 若线段完全在矩形外，直接跳过
    sx1, sy1 = min(p1[0], p2[0]), min(p1[1], p2[1])
    sx2, sy2 = max(p1[0], p2[0]), max(p1[1], p2[1])
    if sx2 < rx1 or sx1 > rx2 or sy2 < ry1 or sy1 > ry2:
        return False

    # 端点在矩形内则不算穿越
    def pt_in_rect(px, py):
        return rx1 <= px <= rx2 and ry1 <= py <= ry2

    if pt_in_rect(p1[0], p1[1]) and pt_in_rect(p2[0], p2[1]):
        return False  # 两端都在内部（不应出现）

    # 线段是否穿过矩形中部（至少有一段在矩形内）
    # 简化：检测线段与矩形的 4 条边是否有交点
    def seg_intersects_seg(a1, a2, b1, b2):
        def cross(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
        d1 = cross(b1, b2, a1)
        d2 = cross(b1, b2, a2)
        d3 = cross(a1, a2, b1)
        d4 = cross(a1, a2, b2)
        if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
           ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
            return True
        return False

    corners = [(rx1, ry1), (rx2, ry1), (rx2, ry2), (rx1, ry2)]
    rect_edges = [(corners[i], corners[(i + 1) % 4]) for i in range(4)]
    for re1, re2 in rect_edges:
        if seg_intersects_seg(p1, p2, re1, re2):
            return True
    return False


def check_layout_issues(xml):
    """
    检测 BPMNDiagram 中的布局问题：
    ① 节点矩形重叠
    ② 节点间距 < 5px
    ③ 连线线段穿越非端点节点矩形
    返回问题描述列表。
    """
    issues = []
    shapes = _parse_shapes_from_xml(xml)
    edge_wps = _parse_edges_from_xml(xml)

    shape_list = list(shapes.items())

    # ① & ② 节点重叠 / 间距过小
    for i in range(len(shape_list)):
        for j in range(i + 1, len(shape_list)):
            id1, r1 = shape_list[i]
            id2, r2 = shape_list[j]
            if _rects_overlap(r1, r2, gap=5):
                issues.append(f"节点重叠或间距<5px: {id1} 与 {id2}")

    # ③ 连线穿越节点
    for eid, wps in edge_wps.items():
        for i in range(len(wps) - 1):
            seg = (wps[i], wps[i + 1])
            for sid, rect in shapes.items():
                # 排除该边的端点节点（source/target）
                # 无法从 diagram 反查，故只排除端点在矩形边上的情况
                if _segment_intersects_rect(seg[0], seg[1], rect):
                    issues.append(f"连线 {eid} 线段{i} 穿越节点 {sid}")

    print(f"[check] 发现布局问题: {len(issues)} 个")
    return issues


# ─────────────────────────────────────────────
# 10. 主函数
# ─────────────────────────────────────────────

def _extract_process_id(xml):
    """从 XML 中提取主 process 的 id。"""
    m = re.search(r'<(?:bpmn2?:)?process\s[^>]*\bid\s*=\s*"([^"]+)"', xml)
    return m.group(1) if m else 'process1'


def recompute_layout(xml):
    """
    从 XML 解析拓扑，重建 BPMNDiagram，返回新 XML。
    这是布局引擎的核心入口函数。
    """
    print("[layout] 开始重计算布局...")

    # 解析图
    nodes, edges, default_flows = parse_bpmn_graph(xml)
    if not nodes:
        print("[layout] 警告：未找到任何节点，返回原 XML")
        return xml

    succs, preds, in_degree = build_graph(nodes, edges)

    # 排名分配
    rank, topo_order = assign_ranks(nodes, succs, preds, in_degree)

    # 列分配
    col, bypass_cols = assign_columns(nodes, succs, preds, rank, topo_order, default_flows, edges)

    # 像素坐标
    coords = compute_pixel_coords(nodes, rank, col)

    # 边路由
    edge_waypoints = compute_waypoints(edges, nodes, coords, col, bypass_cols)

    # 提取 process id
    process_id = _extract_process_id(xml)

    # 生成新 BPMNDiagram
    new_diagram = build_bpmn_diagram(process_id, nodes, edges, coords, edge_waypoints, default_flows)

    # 替换旧 BPMNDiagram 区块
    new_xml = _replace_bpmn_diagram(xml, new_diagram)

    # 验证 XML 合法性
    try:
        ET.fromstring(new_xml)
        print("[layout] XML 验证通过")
    except ET.ParseError as ex:
        raise ValueError(f"生成的 XML 不合法: {ex}")

    print("[layout] 布局重计算完成")
    return new_xml


def _replace_bpmn_diagram(xml, new_diagram):
    """将 XML 中的 <bpmndi:BPMNDiagram> 区块替换为新内容。"""
    # 找到旧 BPMNDiagram 区块并替换
    pattern = r'<bpmndi:BPMNDiagram\b.*?</bpmndi:BPMNDiagram>'
    if re.search(pattern, xml, re.DOTALL):
        new_xml = re.sub(pattern, new_diagram, xml, count=1, flags=re.DOTALL)
    else:
        # 若没有 BPMNDiagram，插入到 </definitions> 前
        new_xml = xml.replace('</definitions>', new_diagram + '\n</definitions>')
        new_xml = new_xml.replace('</bpmn2:definitions>', new_diagram + '\n</bpmn2:definitions>')

    return new_xml


# ─────────────────────────────────────────────
# HTTP 工具函数
# ─────────────────────────────────────────────

def _http_get(url, token):
    """发送 GET 请求，返回 JSON。"""
    req = urllib.request.Request(url, headers={
        'X-Access-Token': token,
        'Content-Type': 'application/json',
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))


def _http_post_form(url, token, data_dict):
    """发送 POST form-urlencoded 请求，返回 JSON。"""
    body = urllib.parse.urlencode(data_dict).encode('utf-8')
    req = urllib.request.Request(url, data=body, headers={
        'X-Access-Token': token,
        'Content-Type': 'application/x-www-form-urlencoded',
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))


def _http_put(url, token, data_dict):
    """发送 PUT 请求（JSON body），返回 JSON。"""
    body = json.dumps(data_dict).encode('utf-8')
    req = urllib.request.Request(url, data=body, method='PUT', headers={
        'X-Access-Token': token,
        'Content-Type': 'application/json',
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))


# ─────────────────────────────────────────────
# fix_layout_if_needed
# ─────────────────────────────────────────────

def fix_layout_if_needed(api_base, token, process_id, node_cfg_callback=None):
    """
    检测已发布流程的布局，若有问题则自动修复并重新发布。

    参数：
      api_base: JeecgBoot API 地址（如 http://192.168.1.66:8080）
      token: JWT Token
      process_id: 流程 ID（extActProcess 的 id）
      node_cfg_callback(api_base, token, process_id): 可选，重发布后恢复节点配置

    返回 True 表示执行了修复，False 表示无需修复。
    """
    print(f"[fix] 开始检查流程 {process_id} 的布局...")

    # 1. 查询流程信息
    query_url = f"{api_base}/act/process/extActProcess/queryById?id={process_id}"
    resp = _http_get(query_url, token)
    if resp.get('code') != 200 and resp.get('success') is not True:
        print(f"[fix] 查询失败: {resp}")
        return False

    result = resp.get('result', {})
    process_xml_b64 = result.get('processXml', '')
    if not process_xml_b64:
        print("[fix] 未找到 processXml 字段")
        return False

    # 2. base64 解码 processXml
    try:
        xml = base64.b64decode(process_xml_b64).decode('utf-8')
    except Exception as ex:
        print(f"[fix] base64 解码失败: {ex}")
        return False

    print(f"[fix] 成功获取 XML，长度={len(xml)}")

    # 3. 检测布局问题
    issues = check_layout_issues(xml)
    if not issues:
        print("[fix] 布局无问题，无需修复")
        return False

    print(f"[fix] 发现 {len(issues)} 个布局问题，开始修复...")
    for iss in issues[:10]:
        print(f"  - {iss}")

    # 4. 重计算布局
    new_xml = recompute_layout(xml)

    # 5. 保存流程（form-urlencoded）
    save_url = f"{api_base}/act/designer/api/saveProcess"
    # 提取 key 和 name
    key_m = re.search(r'<(?:bpmn2?:)?process\b[^>]*\bkey\s*=\s*"([^"]+)"', new_xml)
    name_m = re.search(r'<(?:bpmn2?:)?process\b[^>]*\bname\s*=\s*"([^"]+)"', new_xml)
    proc_key = key_m.group(1) if key_m else process_id
    proc_name = name_m.group(1) if name_m else process_id

    save_data = {
        'processXml': new_xml,
        'processKey': proc_key,
        'processName': proc_name,
        'id': process_id,
    }
    save_resp = _http_post_form(save_url, token, save_data)
    if save_resp.get('code') != 200 and save_resp.get('success') is not True:
        print(f"[fix] 保存失败: {save_resp}")
        return False
    print(f"[fix] 保存成功: {save_resp.get('message', 'ok')}")

    # 6. 部署流程
    deploy_url = f"{api_base}/act/process/extActProcess/deployProcess"
    deploy_resp = _http_put(deploy_url, token, {'id': process_id})
    if deploy_resp.get('code') != 200 and deploy_resp.get('success') is not True:
        print(f"[fix] 部署失败: {deploy_resp}")
        return False
    print(f"[fix] 部署成功: {deploy_resp.get('message', 'ok')}")

    # 7. 可选：恢复节点配置
    if node_cfg_callback:
        print("[fix] 调用 node_cfg_callback 恢复节点配置...")
        try:
            node_cfg_callback(api_base, token, process_id)
        except Exception as ex:
            print(f"[fix] node_cfg_callback 执行出错: {ex}")

    print("[fix] 布局修复完成")
    return True


def fix_layout_force(api_base, token, process_id, node_cfg_callback=None):
    """
    强制重建布局（跳过检测），直接重计算并重新发布。
    返回 True 表示执行了修复。
    """
    print(f"[fix] 强制模式：跳过检测，直接重建布局...")

    # 查询流程信息
    query_url = f"{api_base}/act/process/extActProcess/queryById?id={process_id}"
    resp = _http_get(query_url, token)
    if resp.get('code') != 200 and resp.get('success') is not True:
        print(f"[fix] 查询失败: {resp}")
        return False

    result = resp.get('result', {})
    process_xml_b64 = result.get('processXml', '')
    if not process_xml_b64:
        print("[fix] 未找到 processXml 字段")
        return False

    try:
        xml = base64.b64decode(process_xml_b64).decode('utf-8')
    except Exception as ex:
        print(f"[fix] base64 解码失败: {ex}")
        return False

    # 直接重计算
    new_xml = recompute_layout(xml)

    # 保存
    save_url = f"{api_base}/act/designer/api/saveProcess"
    key_m = re.search(r'<(?:bpmn2?:)?process\b[^>]*\bkey\s*=\s*"([^"]+)"', new_xml)
    name_m = re.search(r'<(?:bpmn2?:)?process\b[^>]*\bname\s*=\s*"([^"]+)"', new_xml)
    proc_key = key_m.group(1) if key_m else process_id
    proc_name = name_m.group(1) if name_m else process_id

    save_data = {
        'processXml': new_xml,
        'processKey': proc_key,
        'processName': proc_name,
        'id': process_id,
    }
    save_resp = _http_post_form(save_url, token, save_data)
    if save_resp.get('code') != 200 and save_resp.get('success') is not True:
        print(f"[fix] 保存失败: {save_resp}")
        return False
    print(f"[fix] 保存成功")

    # 部署
    deploy_url = f"{api_base}/act/process/extActProcess/deployProcess"
    deploy_resp = _http_put(deploy_url, token, {'id': process_id})
    if deploy_resp.get('code') != 200 and deploy_resp.get('success') is not True:
        print(f"[fix] 部署失败: {deploy_resp}")
        return False
    print(f"[fix] 部署成功")

    if node_cfg_callback:
        print("[fix] 调用 node_cfg_callback...")
        try:
            node_cfg_callback(api_base, token, process_id)
        except Exception as ex:
            print(f"[fix] node_cfg_callback 执行出错: {ex}")

    return True


# ─────────────────────────────────────────────
# 11. CLI 入口
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='BPMN 布局引擎 — 自动修复 JeecgBoot/Flowable 流程图坐标'
    )
    parser.add_argument('--api-base', required=True, help='API 基础地址，如 http://192.168.1.66:8080')
    parser.add_argument('--token', required=True, help='JWT Token（X-Access-Token）')
    parser.add_argument('--process-id', required=True, help='流程 ID（extActProcess 的 id）')
    parser.add_argument('--force', action='store_true', help='跳过检测，强制重建布局')

    args = parser.parse_args()

    if args.force:
        result = fix_layout_force(args.api_base, args.token, args.process_id)
    else:
        result = fix_layout_if_needed(args.api_base, args.token, args.process_id)

    if result:
        print("✓ 布局修复已完成并部署")
    else:
        print("- 无需修复（或修复失败，请查看上方日志）")


if __name__ == '__main__':
    main()
