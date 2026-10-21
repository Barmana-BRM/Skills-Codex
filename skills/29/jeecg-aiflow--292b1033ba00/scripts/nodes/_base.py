"""
节点基类工具——所有节点的 create_node 通用逻辑 + upgrade 公共方法。
各节点的 __init__.py 调用此模块来加载 template.json 并生成节点。
"""
import copy
import json
import os


def load_template(node_dir: str) -> dict:
    path = os.path.join(node_dir, "template.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_node_from_template(node_dir: str, node_id: str, x: int, y: int) -> dict:
    """通用的 create_node 实现：加载 template.json，设置 id/x/y，清除内部字段。"""
    tpl = load_template(node_dir)
    node = copy.deepcopy(tpl)
    node["id"] = node_id
    node["x"] = x
    node["y"] = y
    for key in ("_idPrefix", "_groupType", "_internal", "_width", "_height"):
        node.pop(key, None)
    return node


def merge_io_params(props: dict, def_input: list = None, def_output: list = None):
    """对应前端 useUpdateSettings 的 mergeIOParams：按 field+nodeId 去重合并默认参数。"""
    if def_input is not None:
        _merge_param_list(props, "inputParams", def_input)
    if def_output is not None:
        _merge_param_list(props, "outputParams", def_output)


def _merge_param_list(props: dict, key: str, defaults: list):
    current = props.get(key, [])
    if not isinstance(current, list):
        current = []
    existing = {_param_key(p) for p in current}
    for p in defaults:
        if _param_key(p) not in existing:
            current.append(dict(p))
    props[key] = current


def _param_key(p: dict) -> str:
    return p.get("field", "") + "_" + p.get("nodeId", "")
