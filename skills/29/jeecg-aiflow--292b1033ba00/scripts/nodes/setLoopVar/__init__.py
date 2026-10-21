import os
from .._base import create_node_from_template

_DIR = os.path.dirname(os.path.abspath(__file__))


def create_node(node_id: str, x: int, y: int) -> dict:
    return create_node_from_template(_DIR, node_id, x, y)


def validate_node(node: dict, prefix: str) -> list:
    errors = []
    opts = node.get("properties", {}).get("options", {})
    if not opts.get("targetField"):
        errors.append(f"{prefix}: 目标字段不能为空(targetField)")
    source = opts.get("sourceVar", {})
    if not source.get("nodeId") and not source.get("customValue"):
        errors.append(f"{prefix}: 来源变量必须选择引用节点或填写自定义值(sourceVar)")
    if source.get("nodeId") and not source.get("field"):
        errors.append(f"{prefix}: 来源变量已选择节点但缺少字段(sourceVar.field)")
    return errors


def upgrade_node(node: dict):
    pass
