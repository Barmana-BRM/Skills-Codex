import os
from .._base import create_node_from_template

_DIR = os.path.dirname(os.path.abspath(__file__))


def create_node(node_id: str, x: int, y: int) -> dict:
    return create_node_from_template(_DIR, node_id, x, y)


def validate_node(node: dict, prefix: str) -> list:
    return []


def upgrade_node(node: dict):
    from .._base import merge_io_params
    props = node.get("properties", {})
    merge_io_params(props,
        def_input=[],
        def_output=[{"field": "result", "name": "执行结果", "type": "string"}])
