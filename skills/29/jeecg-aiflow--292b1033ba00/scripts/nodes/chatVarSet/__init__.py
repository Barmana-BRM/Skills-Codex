import os
from .._base import create_node_from_template

_DIR = os.path.dirname(os.path.abspath(__file__))


def create_node(node_id: str, x: int, y: int) -> dict:
    return create_node_from_template(_DIR, node_id, x, y)


def validate_node(node: dict, prefix: str) -> list:
    errors = []
    opts = node.get("properties", {}).get("options", {})
    variables = opts.get("variables", [])
    if not variables:
        errors.append(f"{prefix}: 变量列表不能为空(variables)")
    else:
        for i, v in enumerate(variables):
            if not v.get("name"):
                errors.append(f"{prefix}: 第{i+1}个变量名称不能为空")
    return errors


def upgrade_node(node: dict):
    pass
