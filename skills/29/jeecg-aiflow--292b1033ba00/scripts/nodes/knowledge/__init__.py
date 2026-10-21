import os
from .._base import create_node_from_template

_DIR = os.path.dirname(os.path.abspath(__file__))


def create_node(node_id: str, x: int, y: int) -> dict:
    return create_node_from_template(_DIR, node_id, x, y)


def validate_node(node: dict, prefix: str) -> list:
    errors = []
    props = node.get("properties", {})
    opts = props.get("options", {})
    if not opts.get("knowIds"):
        errors.append(f"{prefix}: 必须选择至少一个知识库(knowIds)")
    input_params = props.get("inputParams", [])
    if not input_params:
        errors.append(f"{prefix}: 必须配置查询变量(inputParams)")
    elif input_params:
        first = input_params[0]
        if not first.get("nodeId") or not first.get("field"):
            errors.append(f"{prefix}: 查询变量必须选择引用节点和字段")
    return errors


def upgrade_node(node: dict):
    pass
