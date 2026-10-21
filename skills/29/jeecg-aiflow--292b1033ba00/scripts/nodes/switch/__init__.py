import os
from .._base import create_node_from_template

_DIR = os.path.dirname(os.path.abspath(__file__))


def create_node(node_id: str, x: int, y: int) -> dict:
    return create_node_from_template(_DIR, node_id, x, y)


def validate_node(node: dict, prefix: str) -> list:
    errors = []
    opts = node.get("properties", {}).get("options", {})
    if_list = opts.get("if", [])
    if not if_list:
        errors.append(f'{prefix}: "IF"分支条件不能为空')
    else:
        for idx, branch in enumerate(if_list):
            conditions = branch.get("conditions", [])
            if not conditions:
                errors.append(f'{prefix}: 第{idx+1}个分支条件列表为空')
            for ci, cond in enumerate(conditions):
                if not cond.get("nodeId"):
                    errors.append(f'{prefix}: 第{idx+1}个分支第{ci+1}个条件缺少引用节点(nodeId)')
                if not cond.get("field"):
                    errors.append(f'{prefix}: 第{idx+1}个分支第{ci+1}个条件缺少引用字段(field)')
    return errors


def upgrade_node(node: dict):
    from .._base import merge_io_params
    props = node.get("properties", {})
    merge_io_params(props,
        def_output=[{"field": "index", "name": "分支索引", "type": "number"}])
