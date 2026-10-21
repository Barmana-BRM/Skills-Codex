"""
AIFlow 创建器脚本

所有操作基于「工作目录」：init-work 创建工作目录 + meta.json，
后续命令只需传 --work-id 即可定位 design.json 和 API 凭证。

子命令:
  1. init-work    — 创建工作目录，存储 meta.json；带 --flow-id 时自动导出 design
  2. generate     — 根据节点类型列表生成模板 design.json 到工作目录
  3. export       — 单独导出已有流程 design.json（一般不需要，init-work 已自动导出）
  4. add-node     — 在 design.json 中插入新节点
  5. remove-node  — 从 design.json 中删除指定节点
  6. submit       — 校验 + 生成 chain + 保存到后端（--skip-validate 跳过校验，仅编辑时允许）
  7. query        — 查询系统资源（models/knowledge/datasources/subflows）

用法:
  python aiflow_creator.py init-work --name "我的流程" --api-base <url> --token <tk>
  python aiflow_creator.py generate --work-id <id> --types start,llm,end
  python aiflow_creator.py export --work-id <id> --flow-id <flow_id>
  python aiflow_creator.py add-node --work-id <id> --type llm --after <node_id>
  python aiflow_creator.py remove-node --work-id <id> --node-id <node_id>
  python aiflow_creator.py submit --work-id <id>
"""
import argparse
import json
import os
import sys
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from aiflow_utils import (
    generate_design_from_types, validate_design, insert_node_after, remove_node,
    LOOP_BODY_SUFFIX,
)
from aiflow_apis import init_api, list_flows, add_flow, save_design, query_flow_by_id
from generate_chain import generate_chain

WORK_ROOT = os.path.join(tempfile.gettempdir(), "jeecg-aiflow")


def _gen_work_id() -> str:
    while True:
        wid = os.urandom(4).hex()
        if not os.path.exists(os.path.join(WORK_ROOT, wid)):
            return wid


# ─── 工作目录工具 ───

def _work_dir(work_id: str) -> str:
    return os.path.join(WORK_ROOT, work_id)


def _meta_path(work_id: str) -> str:
    return os.path.join(_work_dir(work_id), "meta.json")


def _design_path(work_id: str) -> str:
    return os.path.join(_work_dir(work_id), "design.json")


def _read_meta(work_id: str) -> dict:
    path = _meta_path(work_id)
    if not os.path.exists(path):
        _fail(f"工作目录不存在或 meta.json 缺失: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_meta(work_id: str, meta: dict):
    with open(_meta_path(work_id), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def _read_design(work_id: str) -> dict:
    path = _design_path(work_id)
    if not os.path.exists(path):
        _fail(f"design.json 不存在: {path}。请先执行 generate 或 export")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_design(work_id: str, design: dict):
    with open(_design_path(work_id), "w", encoding="utf-8") as f:
        json.dump(design, f, ensure_ascii=False, indent=2)


def _init_api_from_meta(meta: dict):
    api_base = meta.get("apiBase", "")
    token = meta.get("token", "")
    if not api_base or not token:
        _fail("meta.json 中缺少 apiBase 或 token")
    init_api(api_base, token)


def _fail(msg: str):
    print(json.dumps({"success": False, "message": msg}, ensure_ascii=False))
    sys.exit(1)


def _design_file_info(work_id: str) -> dict:
    """读取 design.json，返回总行数、每个节点的起止行号、edges 数组的起止行号。"""
    path = _design_path(work_id)
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    total_lines = len(lines)

    def _find_array_range(key: str):
        """找到顶层 key 对应的数组的起止行号（含 [ 和 ] 行）。"""
        for i, line in enumerate(lines):
            if f'"{key}"' in line and "[" in line:
                arr_start = i
                indent = len(line) - len(line.lstrip())
                for j in range(i + 1, len(lines)):
                    lj = lines[j]
                    j_indent = len(lj) - len(lj.lstrip())
                    if j_indent == indent and lj.strip().startswith("]"):
                        return arr_start + 1, j + 1
                    elif j_indent < indent:
                        break
                if line.rstrip().endswith("[]") or line.rstrip().endswith("[],"):
                    return arr_start + 1, arr_start + 1
        return None, None

    # nodes 数组中每个节点的行号
    node_list = []
    nodes_start_line, nodes_end_line = _find_array_range("nodes")
    if nodes_start_line is not None:
        node_indent = -1
        for i, line in enumerate(lines):
            if '"nodes"' in line and "[" in line:
                node_indent = len(line) - len(line.lstrip()) + 2
                scan_from = i + 1
                break
        if node_indent > 0:
            ns = -1
            for i in range(scan_from, len(lines)):
                stripped = lines[i].rstrip()
                indent = len(lines[i]) - len(lines[i].lstrip())
                if indent == node_indent and stripped.lstrip().startswith("{"):
                    ns = i
                elif indent == node_indent and ns >= 0 and stripped.lstrip().startswith("}"):
                    nid, ntype = "", ""
                    top = node_indent + 2
                    for j in range(ns, i + 1):
                        if len(lines[j]) - len(lines[j].lstrip()) != top:
                            continue
                        ln = lines[j].strip()
                        if ln.startswith('"id"'):
                            nid = ln.split(":", 1)[1].strip().strip('",')
                        elif ln.startswith('"type"'):
                            ntype = ln.split(":", 1)[1].strip().strip('",')
                        if nid and ntype:
                            break
                    node_list.append({"id": nid, "type": ntype, "startLine": ns + 1, "endLine": i + 1})
                    ns = -1
                elif indent < node_indent and ns < 0:
                    break

    # edges 数组行号
    edges_start, edges_end = _find_array_range("edges")

    result = {"totalLines": total_lines, "nodes": node_list}
    if edges_start is not None:
        result["edgesLines"] = {"startLine": edges_start, "endLine": edges_end}
    return result


def _design_summary(work_id: str) -> dict:
    return _design_file_info(work_id)


# ─── 子命令实现 ───

def _do_export(work_id: str, flow_id: str):
    """导出流程 design 到工作目录，返回结果 dict（不含 success/message）。"""
    resp = query_flow_by_id(flow_id)
    if not resp.get("success"):
        _fail(f"查询流程失败: {resp.get('message', 'unknown')}")

    flow = resp.get("result", {})
    design_str = flow.get("design", "")
    if not design_str:
        _fail("该流程没有 design 数据")

    design = json.loads(design_str)
    from nodes import upgrade_node as _upgrade
    for n in design.get("nodes", []):
        _upgrade(n)
    _write_design(work_id, design)

    meta = _read_meta(work_id)
    meta["flowId"] = flow_id
    if flow.get("name"):
        meta["name"] = flow["name"]
    if flow.get("descr"):
        meta["descr"] = flow["descr"]
    _write_meta(work_id, meta)

    nodes = design.get("nodes", [])
    edges = design.get("edges", [])
    result = {
        "flowId": flow_id,
        "flowName": flow.get("name", ""),
        "designPath": _design_path(work_id),
        "nodeCount": len(nodes),
        "edgeCount": len(edges),
    }
    result.update(_design_summary(work_id))
    return result


def cmd_init_work(args):
    # 先校验 API 连通性和 token 有效性
    init_api(args.api_base, args.token)
    try:
        resp = list_flows(page=1, size=1)
    except Exception as e:
        _fail(f"API 连接失败: {e}")
    if not resp.get("success"):
        _fail(f"Token 无效或已过期: {resp.get('message', 'unknown')}")

    work_id = _gen_work_id()
    work_path = _work_dir(work_id)
    os.makedirs(work_path, exist_ok=True)

    meta = {
        "workId": work_id,
        "name": args.name or "新流程",
        "descr": args.descr or "",
        "apiBase": args.api_base,
        "token": args.token,
    }
    if args.flow_id:
        meta["flowId"] = args.flow_id

    _write_meta(work_id, meta)

    result = {
        "success": True,
        "workId": work_id,
        "workDir": work_path,
        "designPath": _design_path(work_id),
    }

    if args.flow_id:
        export_info = _do_export(work_id, args.flow_id)
        result["message"] = f"工作目录已创建，已导出流程 design（{export_info['nodeCount']} 个节点，{export_info['edgeCount']} 条边）"
        result.update(export_info)
    else:
        result["message"] = "工作目录已创建"

    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_generate(args):
    meta = _read_meta(args.work_id)

    types = [t.strip() for t in args.types.split(",") if t.strip()]
    if not types:
        _fail("节点类型列表不能为空")

    try:
        design = generate_design_from_types(types, flow_name=meta.get("name", "新流程"))
    except ValueError as e:
        _fail(str(e))

    _write_design(args.work_id, design)

    result = {
        "success": True,
        "message": f"模板已生成，包含 {len(design['nodes'])} 个节点",
        "designPath": _design_path(args.work_id),
    }
    result.update(_design_summary(args.work_id))
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_export(args):
    meta = _read_meta(args.work_id)
    _init_api_from_meta(meta)

    flow_id = args.flow_id or meta.get("flowId", "")
    if not flow_id:
        _fail("未指定 flow-id，且 meta.json 中无 flowId")

    export_info = _do_export(args.work_id, flow_id)
    result = {
        "success": True,
        "message": f"已导出流程 design（{export_info['nodeCount']} 个节点，{export_info['edgeCount']} 条边）",
    }
    result.update(export_info)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_add_node(args):
    design = _read_design(args.work_id)

    try:
        new_node = insert_node_after(design, args.type, args.after)
    except ValueError as e:
        _fail(str(e))

    _write_design(args.work_id, design)

    result = {
        "success": True,
        "message": f"已在节点 {args.after} 之后插入 {args.type} 节点",
        "newNodeId": new_node["id"],
        "designPath": _design_path(args.work_id),
        "hint": "请用 Read 工具读取 design.json，用 Edit 工具完成：1) 节点业务配置  2) edges 连线",
    }
    result.update(_design_summary(args.work_id))

    if args.type == "loop":
        body_id = new_node["id"] + LOOP_BODY_SUFFIX
        result["loopBodyId"] = body_id
        result["message"] += f"（已自动创建 loopBody 节点 {body_id}）"

    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_remove_node(args):
    design = _read_design(args.work_id)

    nodes_before = {n["id"] for n in design.get("nodes", [])}

    try:
        removed = remove_node(design, args.node_id)
    except ValueError as e:
        _fail(str(e))

    _write_design(args.work_id, design)

    nodes_after = {n["id"] for n in design.get("nodes", [])}
    cascade_removed = nodes_before - nodes_after - {args.node_id}

    result = {
        "success": True,
        "message": f"已删除节点 {removed.get('type', '')}({args.node_id})",
        "removedNodeId": args.node_id,
        "removedNodeType": removed.get("type", ""),
        "designPath": _design_path(args.work_id),
        "hint": "请用 Read 工具读取 design.json，检查并用 Edit 工具补充必要的 edges 连线",
    }
    result.update(_design_summary(args.work_id))

    if cascade_removed:
        result["cascadeRemoved"] = list(cascade_removed)
        result["message"] += f"（级联删除了 {len(cascade_removed)} 个关联节点）"

    print(json.dumps(result, ensure_ascii=False, indent=2))


LOOP_CHILD_TYPES = {"loopBreak", "loopContinue", "setLoopVar"}
LOOP_BODY_SUFFIX = "_loopBody"


def _fill_loop_node_ids(design):
    """Auto-fill loopNodeId for loopBreak/loopContinue/setLoopVar nodes."""
    nodes = design.get("nodes", [])
    node_map = {n["id"]: n for n in nodes}
    for n in nodes:
        if n["type"] != "loopBody":
            continue
        body_id = n["id"]
        if not body_id.endswith(LOOP_BODY_SUFFIX):
            continue
        loop_id = body_id[:-len(LOOP_BODY_SUFFIX)]
        children_ids = n.get("properties", {}).get("children", []) or n.get("children", [])
        for cid in children_ids:
            child = node_map.get(cid)
            if child and child["type"] in LOOP_CHILD_TYPES:
                child.setdefault("properties", {})["loopNodeId"] = loop_id


def cmd_submit(args):
    meta = _read_meta(args.work_id)
    _init_api_from_meta(meta)

    design = _read_design(args.work_id)

    skip = getattr(args, 'skip_validate', False)
    if skip and not meta.get("flowId"):
        _fail("--skip-validate 仅允许编辑已有流程时使用，新建流程不允许跳过校验")

    _fill_loop_node_ids(design)

    errors = validate_design(design)
    if errors and not skip:
        print(json.dumps({
            "success": False,
            "message": "design JSON 校验不通过",
            "errors": errors,
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    try:
        chain = generate_chain(design)
    except Exception as e:
        _fail(f"chain 生成失败: {e}")

    flow_id = meta.get("flowId")
    flow_name = meta.get("name", "新流程")
    flow_descr = meta.get("descr", "")
    design_str = json.dumps(design, ensure_ascii=False)

    if flow_id:
        resp = save_design(flow_id, flow_name, chain, design_str)
        if not resp.get("success"):
            _fail(f"保存设计失败: {resp.get('message', 'unknown')}")
    else:
        resp = add_flow(flow_name, descr=flow_descr, chain=chain, design=design_str)
        if not resp.get("success"):
            _fail(f"创建流程失败: {resp.get('message', 'unknown')}")
        flow_id = resp.get("result")
        meta["flowId"] = flow_id
        _write_meta(args.work_id, meta)

    result = {
        "success": True,
        "message": "流程保存成功" if meta.get("flowId") else "流程创建成功",
        "flowId": flow_id,
        "chain": chain,
    }
    if skip and errors:
        result["skippedErrors"] = errors
        result["message"] += f"（已跳过 {len(errors)} 条校验错误）"
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_query(args):
    """查询系统资源（模型列表、知识库、数据源、子流程），从工作目录自动读取 API 凭证。"""
    from aiflow_apis import list_llm_models, list_knowledge_bases, list_data_sources, list_subflows

    meta = _read_meta(args.work_id)
    _init_api_from_meta(meta)

    query_map = {
        "models": list_llm_models,
        "knowledge": list_knowledge_bases,
        "datasources": list_data_sources,
        "subflows": list_subflows,
    }
    fn = query_map.get(args.resource)
    if not fn:
        _fail(f"未知资源类型: {args.resource}。可选: {', '.join(query_map.keys())}")

    result = fn()
    print(json.dumps(result, ensure_ascii=False, indent=2))


# ─── CLI 入口 ───

def main():
    parser = argparse.ArgumentParser(description="AIFlow 创建器")
    sub = parser.add_subparsers(dest="command")

    # init-work
    iw = sub.add_parser("init-work", help="创建工作目录")
    iw.add_argument("--name", default="新流程", help="流程名称")
    iw.add_argument("--descr", default="", help="流程描述")
    iw.add_argument("--api-base", required=True, help="API 地址")
    iw.add_argument("--token", required=True, help="X-Access-Token")
    iw.add_argument("--flow-id", default=None, help="已有流程 ID（编辑场景）")

    # generate
    gen = sub.add_parser("generate", help="生成模板 design.json")
    gen.add_argument("-w", "--work-id", required=True, help="工作目录 ID")
    gen.add_argument("--types", required=True, help="逗号分隔的节点类型列表")

    # export
    exp = sub.add_parser("export", help="导出已有流程 design.json")
    exp.add_argument("-w", "--work-id", required=True, help="工作目录 ID")
    exp.add_argument("--flow-id", default=None, help="流程 ID（可选，优先级高于 meta.json 中的）")

    # add-node
    add = sub.add_parser("add-node", help="插入新节点")
    add.add_argument("-w", "--work-id", required=True, help="工作目录 ID")
    add.add_argument("--type", required=True, help="新节点类型")
    add.add_argument("--after", required=True, help="插入到此节点 ID 之后")

    # remove-node
    rm = sub.add_parser("remove-node", help="删除节点")
    rm.add_argument("-w", "--work-id", required=True, help="工作目录 ID")
    rm.add_argument("--node-id", required=True, help="要删除的节点 ID")

    # submit
    sb = sub.add_parser("submit", help="校验并提交流程")
    sb.add_argument("-w", "--work-id", required=True, help="工作目录 ID")
    sb.add_argument("--skip-validate", action="store_true", help="跳过校验（仅编辑已有流程时允许）")

    # query
    qr = sub.add_parser("query", help="查询系统资源（models/knowledge/datasources/subflows）")
    qr.add_argument("-w", "--work-id", required=True, help="工作目录 ID")
    qr.add_argument("--resource", required=True, help="资源类型: models, knowledge, datasources, subflows")

    args = parser.parse_args()
    cmd_map = {
        "init-work": cmd_init_work,
        "generate": cmd_generate,
        "export": cmd_export,
        "add-node": cmd_add_node,
        "remove-node": cmd_remove_node,
        "submit": cmd_submit,
        "query": cmd_query,
    }
    fn = cmd_map.get(args.command)
    if fn:
        fn(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
