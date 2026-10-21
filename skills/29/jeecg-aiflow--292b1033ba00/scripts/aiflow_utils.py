"""
AIFlow 核心工具库
- 通过 nodes/ 模块生成节点 JSON（每个节点独立维护模板和校验）
- 公共校验逻辑（结构完整性、边合法性、孤儿节点、连通性）
- 节点插入 / 删除（坐标自动调整）
"""
import json
import os
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Snowflake ID 生成器 ───

class _SnowflakeID:
    """移植自前端 snowflake-id.js：41位时间戳 + 10位机器ID + 12位序列号"""
    def __init__(self, mid=1, offset=0):
        self.seq = 0
        self.mid = mid % 1023
        self.offset = offset
        self.last_time = 0

    def generate(self):
        now = int(time.time() * 1000)
        if self.last_time == now:
            self.seq += 1
            if self.seq > 4095:
                self.seq = 0
                while int(time.time() * 1000) <= now:
                    pass
                now = int(time.time() * 1000)
        else:
            self.seq = 0
        self.last_time = now
        ts = now - self.offset
        sid = (ts << 22) | (self.mid << 12) | self.seq
        return str(sid)

_snowflake = _SnowflakeID(mid=1)

def gen_id():
    return _snowflake.generate()

_gen_id = gen_id


# ─── 节点模块 ───

from nodes import create_node as _nodes_create, validate_node as _nodes_validate
from nodes import upgrade_node as _nodes_upgrade, get_available_types

NODE_WIDTH = 332
NODE_HEIGHT = 62
X_GAP = 400
Y_GAP = 180
LOOP_BODY_SUFFIX = "_loopBody"
LOOP_BODY_GAP_Y = 320


# ─── 生成 design ───

def generate_design_from_types(node_types: list, flow_name: str = "新流程") -> dict:
    """根据节点类型列表生成完整的 design JSON。
    如果列表中包含 loop，会自动创建对应的 loopBody 节点和 loop→loopBody 的边。
    不要在列表中手动传入 loopBody。
    """
    x_start = 200
    y_center = 300
    nodes = []
    edges = []

    for i, ntype in enumerate(node_types):
        if ntype == "loopBody":
            continue
        node_id = _gen_id()
        x = x_start + X_GAP * i
        y = y_center
        node = _nodes_create(ntype, node_id, x, y)
        nodes.append(node)

        if ntype == "loop":
            body_node, body_edge = _create_loop_body(node)
            nodes.append(body_node)
            edges.append(body_edge)

    return {"nodes": nodes, "edges": edges}


# ─── 插入节点 ───

def insert_node_after(design: dict, node_type: str, after_id: str) -> dict:
    """在 after_id 节点之后插入新节点，自动右移下游坐标。不处理连线。
    如果插入 loop 类型，会自动创建 loopBody 节点和 loop→loopBody 边。
    返回新创建的主节点（loop 场景下返回 loop 节点，loopBody 信息在返回结果的 _loopBody 中）。
    """
    if node_type == "loopBody":
        raise ValueError("loopBody 不能手动创建，它由 loop 节点自动管理")

    nodes = design.get("nodes", [])
    edges = design.get("edges", [])

    node_map = {n["id"]: n for n in nodes}
    if after_id not in node_map:
        raise ValueError(f"after 节点不存在: {after_id}。当前节点ID: {list(node_map.keys())}")

    after_node = node_map[after_id]
    after_x = after_node.get("x", 200)
    after_y = after_node.get("y", 300)
    new_x = after_x + X_GAP

    new_node = _nodes_create(node_type, _gen_id(), new_x, after_y)

    # 右移下游节点
    shift_ids = _collect_downstream_ids(after_id, edges, node_map)
    if shift_ids:
        for n in nodes:
            if n["id"] in shift_ids and n.get("x", 0) >= new_x:
                n["x"] = n.get("x", 0) + X_GAP
    else:
        for n in nodes:
            if n["id"] != after_id and n.get("x", 0) >= new_x:
                n["x"] = n.get("x", 0) + X_GAP

    after_idx = next(i for i, n in enumerate(nodes) if n["id"] == after_id)
    nodes.insert(after_idx + 1, new_node)

    if node_type == "loop":
        body_node, body_edge = _create_loop_body(new_node)
        nodes.insert(after_idx + 2, body_node)
        edges.append(body_edge)

    return new_node


# ─── 删除节点 ───

def remove_node(design: dict, node_id: str) -> dict:
    """删除指定节点，移除相关边，左移下游坐标。不创建新连线。
    loop 和 loopBody 联动删除：删除其中一个时自动删除另一个及其内部子节点。
    """
    nodes = design.get("nodes", [])
    edges = design.get("edges", [])

    node_map = {n["id"]: n for n in nodes}
    if node_id not in node_map:
        raise ValueError(f"节点不存在: {node_id}。当前节点ID: {list(node_map.keys())}")

    target_node = node_map[node_id]
    if target_node.get("type") == "start":
        raise ValueError("不允许删除开始节点(start)")

    # 收集要删除的所有节点 ID（loop/loopBody 联动）
    remove_ids = {node_id}
    target_type = target_node.get("type", "")

    if target_type == "loop":
        body_id = node_id + LOOP_BODY_SUFFIX
        if body_id in node_map:
            remove_ids.add(body_id)
            children = node_map[body_id].get("properties", {}).get("children", [])
            remove_ids.update(children)
    elif target_type == "loopBody":
        children = target_node.get("properties", {}).get("children", [])
        remove_ids.update(children)
        loop_id = node_id.replace(LOOP_BODY_SUFFIX, "")
        if loop_id in node_map and node_map[loop_id].get("type") == "loop":
            remove_ids.add(loop_id)

    removed_x = target_node.get("x", 0)
    shift_ids = _collect_downstream_ids(node_id, edges, node_map)

    design["nodes"] = [n for n in nodes if n["id"] not in remove_ids]
    design["edges"] = [
        e for e in edges
        if e.get("sourceNodeId") not in remove_ids and e.get("targetNodeId") not in remove_ids
    ]

    if shift_ids:
        for n in design["nodes"]:
            if n["id"] in shift_ids and n.get("x", 0) > removed_x:
                n["x"] = n.get("x", 0) - X_GAP
    else:
        for n in design["nodes"]:
            if n.get("x", 0) > removed_x:
                n["x"] = n.get("x", 0) - X_GAP

    return target_node


# ─── 公共校验 ───

# 只需入边的节点类型（无出边正常）
ONLY_IN_TYPES = {"end", "loopBreak", "loopContinue"}
# 只需出边的节点类型（无入边正常）
ONLY_OUT_TYPES = {"start"}
# 由 loop 联动管理，跳过孤儿检查的类型
_LOOP_MANAGED_TYPES = {"loopBody"}


def validate_design(design: dict) -> list:
    """
    校验 design JSON 的合法性。
    公共校验 + 各节点自身校验（委托给 nodes/ 模块）。
    """
    errors = []
    nodes = design.get("nodes", [])
    edges = design.get("edges", [])

    if not nodes:
        errors.append("流程中没有任何节点")
        return errors

    # ── 0. 数据升级（老格式 → 新格式） ──
    for node in nodes:
        _nodes_upgrade(node)

    # ── 1. 结构完整性 ──
    node_types = [n.get("type") for n in nodes]
    if "start" not in node_types:
        errors.append("缺少开始节点(start)")
    if "end" not in node_types:
        errors.append("缺少结束节点(end)")

    # ── 2. 边引用合法性 ──
    node_ids = {n["id"] for n in nodes}
    for edge in edges:
        src = edge.get("sourceNodeId")
        tgt = edge.get("targetNodeId")
        if src not in node_ids:
            errors.append(f"边引用了不存在的源节点: {src}")
        if tgt not in node_ids:
            errors.append(f"边引用了不存在的目标节点: {tgt}")

    # ── 3. 各节点自身校验（委托给 nodes/ 模块） ──
    for node in nodes:
        errors.extend(_nodes_validate(node))

    # ── 3.5 分支节点连线完整性（switch/classifier/varExtract 每个分支都必须有 edge） ──
    errors.extend(_validate_branch_edges(nodes, edges))

    # ── 3.6 inputParams / outputParams 参数引用校验（公共） ──
    errors.extend(_validate_params_refs(nodes, node_ids))

    # ── 3.7 循环变量引用校验：下游引用了 loop 的循环变量时，loop 的 outputParams 必须声明 ──
    errors.extend(_validate_loop_var_refs(nodes))

    # ── 4. 孤儿节点检查 ──
    if len(nodes) > 1:
        # 收集所有 loopBody 的 children，循环体内部节点由内部边连通，跳过主流程的孤儿检查
        loop_children_ids = set()
        for node in nodes:
            if node.get("type") == "loopBody":
                for cid in (node.get("children") or []):
                    loop_children_ids.add(cid)
                for cid in ((node.get("properties") or {}).get("children") or []):
                    loop_children_ids.add(cid)

        has_out = set()
        has_in = set()
        for edge in edges:
            has_out.add(edge.get("sourceNodeId"))
            has_in.add(edge.get("targetNodeId"))
        for node in nodes:
            nid = node.get("id")
            ntype = node.get("type")
            label = node.get("properties", {}).get("text", ntype)
            if ntype in _LOOP_MANAGED_TYPES:
                continue
            if nid in loop_children_ids:
                if nid not in has_in:
                    errors.append(f"孤儿节点[{label}({nid})]：循环体内该节点没有入边，请从上游节点连接到它")
                continue
            if ntype in ONLY_OUT_TYPES:
                if nid not in has_out:
                    errors.append(f"孤儿节点[{label}({nid})]：开始节点没有任何出边，请添加连线")
            elif ntype in ONLY_IN_TYPES:
                if nid not in has_in:
                    errors.append(f"孤儿节点[{label}({nid})]：该节点没有任何入边，请添加连线")
            else:
                if nid not in has_out and nid not in has_in:
                    errors.append(f"孤儿节点[{label}({nid})]：该节点没有任何连线，请添加入边和出边")
                elif nid not in has_in:
                    errors.append(f"孤儿节点[{label}({nid})]：该节点没有入边，请从上游节点连接到它")
                elif nid not in has_out:
                    errors.append(f"孤儿节点[{label}({nid})]：该节点没有出边，请从它连接到下游节点")

    # ── 5. 连通性检查 ──
    if "start" in node_types and "end" in node_types and edges:
        out_map = {}
        for edge in edges:
            out_map.setdefault(edge.get("sourceNodeId"), []).append(edge.get("targetNodeId"))

        start_id = next(n["id"] for n in nodes if n["type"] == "start")
        visited = set()
        stack = [start_id]
        while stack:
            nid = stack.pop()
            if nid in visited:
                continue
            visited.add(nid)
            for next_id in out_map.get(nid, []):
                stack.append(next_id)

        for n in nodes:
            if n["type"] == "end" and n["id"] not in visited:
                errors.append(f"结束节点({n['id']})不可达：从开始节点无法到达该结束节点")

    return errors


# ─── 分支连线完整性校验 ───

def _validate_branch_edges(nodes: list, edges: list) -> list:
    """检查 switch/classifier/varExtract 的每个分支是否都有对应的 edge 连出。"""
    errors = []
    anchor_set = {e.get("sourceAnchorId", "") for e in edges}

    for node in nodes:
        ntype = node.get("type", "")
        nid = node.get("id", "")
        props = node.get("properties", {})
        opts = props.get("options", {})
        label = props.get("text", ntype)
        prefix = f"节点[{label}({nid})]"

        if ntype == "switch":
            if_list = opts.get("if", [])
            for i, branch in enumerate(if_list):
                if i == 0:
                    anchor = f"{nid}_source_if"
                    branch_name = "IF"
                else:
                    anchor = f"{nid}_case_{i + 1}"
                    branch_name = f"ELIF {i + 1}"
                if anchor not in anchor_set:
                    errors.append(f"{prefix}: \"{branch_name}\"分支未连接下一个节点（缺少 sourceAnchorId={anchor} 的边）")
            else_anchor = f"{nid}_source_else"
            if else_anchor not in anchor_set:
                errors.append(f"{prefix}: \"ELSE\"分支未连接下一个节点（缺少 sourceAnchorId={else_anchor} 的边）")

        elif ntype == "classifier":
            cats = opts.get("categories", [])
            for i, cat in enumerate(cats):
                anchor = f"{nid}_case_{i + 1}"
                cat_name = cat.get("category", f"分类{i + 1}")
                if anchor not in anchor_set:
                    errors.append(f"{prefix}: 分类\"{cat_name}\"未连接下一个节点（缺少 sourceAnchorId={anchor} 的边）")
            else_anchor = f"{nid}_case_else"
            if else_anchor not in anchor_set:
                errors.append(f"{prefix}: \"ELSE\"分支未连接下一个节点（缺少 sourceAnchorId={else_anchor} 的边）")

        elif ntype == "varExtract":
            for branch, anchor_suffix in [("成功", "_success"), ("失败", "_fail")]:
                anchor = f"{nid}{anchor_suffix}"
                if anchor not in anchor_set:
                    errors.append(f"{prefix}: \"{branch}\"分支未连接下一个节点（缺少 sourceAnchorId={anchor} 的边）")

    return errors


# ─── 循环变量引用校验 ───

def _validate_loop_var_refs(nodes: list) -> list:
    """当下游节点引用了 loop 节点的循环变量时，检查 loop 的 outputParams 是否声明了该变量。"""
    errors = []
    loop_map = {}
    for n in nodes:
        if n.get("type") == "loop":
            nid = n["id"]
            lp_names = {lp.get("name", "") for lp in n.get("properties", {}).get("options", {}).get("loopParams", []) if lp.get("name")}
            out_fields = {p.get("field", "") for p in n.get("properties", {}).get("outputParams", [])}
            if lp_names:
                loop_map[nid] = {"loopParams": lp_names, "outputFields": out_fields, "label": n.get("properties", {}).get("text", "loop")}

    if not loop_map:
        return errors

    for n in nodes:
        if n.get("type") in ("loop", "loopBody", "loopBreak", "loopContinue", "setLoopVar"):
            continue
        props = n.get("properties", {})
        for param_key in ("inputParams", "outputParams"):
            for p in props.get(param_key, []):
                ref_node_id = p.get("nodeId", "")
                ref_field = p.get("field", "")
                if ref_node_id in loop_map and ref_field in loop_map[ref_node_id]["loopParams"]:
                    if ref_field not in loop_map[ref_node_id]["outputFields"]:
                        loop_label = loop_map[ref_node_id]["label"]
                        node_label = props.get("text", n.get("type", "?"))
                        errors.append(
                            f"节点[{node_label}({n['id']})]引用了循环节点[{loop_label}({ref_node_id})]"
                            f"的循环变量 {ref_field}，但该循环节点的 outputParams 中未声明此变量"
                        )
    return errors


# ─── loop + loopBody 联动 ───

def _create_loop_body(loop_node: dict) -> tuple:
    """为 loop 节点创建配套的 loopBody 节点和连接边。返回 (body_node, edge)。"""
    loop_id = loop_node["id"]
    body_id = loop_id + LOOP_BODY_SUFFIX
    body_x = loop_node.get("x", 200)
    body_y = loop_node.get("y", 300) + NODE_HEIGHT + LOOP_BODY_GAP_Y

    body_node = _nodes_create("loopBody", body_id, body_x, body_y)

    edge = {
        "sourceNodeId": loop_id,
        "targetNodeId": body_id,
        "sourceAnchorId": f"{loop_id}_link_body",
        "targetAnchorId": f"{body_id}_link_loop",
        "type": "base-line-edge",
    }
    return body_node, edge


# ─── 参数引用校验 ───

# inputParams 必须存在且非空的节点类型（前端 required=true）
_INPUT_REQUIRED_TYPES = {"knowledge", "braveSearch"}


def _validate_params_refs(nodes: list, node_ids: set) -> list:
    """校验所有节点的 inputParams / outputParams 参数引用完整性。"""
    errors = []
    for node in nodes:
        ntype = node.get("type", "")
        props = node.get("properties", {})
        prefix = f"节点[{props.get('text', ntype)}({node.get('id', '?')})]"

        input_params = props.get("inputParams", [])
        output_params = props.get("outputParams", [])

        # --- inputParams 校验 ---
        # start 节点的 inputParams 是用户输入参数定义（无 nodeId），跳过引用校验
        if ntype == "start":
            for i, p in enumerate(input_params):
                if not isinstance(p, dict):
                    continue
                if not p.get("field"):
                    errors.append(f"{prefix}: 输入参数第{i+1}项缺少字段名(field)")
                if not p.get("name"):
                    errors.append(f"{prefix}: 输入参数第{i+1}项缺少名称(name)")
        else:
            if ntype in _INPUT_REQUIRED_TYPES and not input_params:
                errors.append(f"{prefix}: 输入变量不能为空(inputParams)")

            for i, p in enumerate(input_params):
                if not isinstance(p, dict):
                    continue
                if p.get("isCustom"):
                    continue
                node_id_ref = p.get("nodeId", "")
                field = p.get("field", "")
                name = p.get("name", "")

                # 跳过 mergeIOParams 追加的未绑定默认占位项（nodeId 和 name 都为空）
                if not node_id_ref and not name:
                    continue

                has_binding = node_id_ref or field
                if has_binding:
                    if not node_id_ref:
                        errors.append(f"{prefix}: 输入变量第{i+1}项 field 已配置但缺少 nodeId")
                    elif node_id_ref not in node_ids:
                        errors.append(f"{prefix}: 输入变量第{i+1}项引用了不存在的节点 nodeId={node_id_ref}")
                    if not field:
                        errors.append(f"{prefix}: 输入变量第{i+1}项 nodeId 已配置但缺少 field")

                if not name:
                    errors.append(f"{prefix}: 输入变量第{i+1}项缺少名称(name)")

        # --- outputParams 校验 ---
        for i, p in enumerate(output_params):
            if not isinstance(p, dict):
                continue
            if not p.get("field"):
                errors.append(f"{prefix}: 输出变量第{i+1}项缺少字段名(field)")
            if not p.get("name"):
                errors.append(f"{prefix}: 输出变量第{i+1}项缺少名称(name)")

    return errors


# ─── 内部工具 ───

def _collect_downstream_ids(start_id: str, edges: list, node_map: dict) -> set:
    """BFS 收集 start_id 的所有下游可达节点 ID"""
    visited = set()
    queue = []
    for e in edges:
        if e.get("sourceNodeId") == start_id:
            tid = e.get("targetNodeId")
            if tid and tid not in visited and tid in node_map:
                visited.add(tid)
                queue.append(tid)
    while queue:
        nid = queue.pop(0)
        for e in edges:
            if e.get("sourceNodeId") == nid:
                tid = e.get("targetNodeId")
                if tid and tid not in visited and tid in node_map:
                    visited.add(tid)
                    queue.append(tid)
    return visited


def get_node_template(node_type: str) -> dict:
    """获取节点模板（兼容旧代码）"""
    return _nodes_create(node_type, "__placeholder__", 0, 0)
