import os
from .._base import create_node_from_template

_DIR = os.path.dirname(os.path.abspath(__file__))


def create_node(node_id: str, x: int, y: int) -> dict:
    return create_node_from_template(_DIR, node_id, x, y)


def validate_node(node: dict, prefix: str) -> list:
    errors = []
    input_params = node.get("properties", {}).get("inputParams", [])
    if not input_params:
        errors.append(f"{prefix}: 必须配置搜索关键词输入变量(inputParams)")
    elif input_params:
        first = input_params[0]
        if not first.get("nodeId") or not first.get("field"):
            errors.append(f"{prefix}: 搜索关键词必须选择引用节点和字段")
    return errors


def upgrade_node(node: dict):
    from .._base import merge_io_params
    props = node.get("properties", {})
    merge_io_params(props,
        def_input=[],
        def_output=[{"field": "result", "name": "搜索结果", "type": "object[]"}])
