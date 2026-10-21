import os
from .._base import create_node_from_template

_DIR = os.path.dirname(os.path.abspath(__file__))


def create_node(node_id: str, x: int, y: int) -> dict:
    # code 节点 ID 需要 code_ 前缀
    if not node_id.startswith("code_"):
        node_id = f"code_{node_id}"
    return create_node_from_template(_DIR, node_id, x, y)


def validate_node(node: dict, prefix: str) -> list:
    errors = []
    opts = node.get("properties", {}).get("options", {})
    if not opts.get("code"):
        errors.append(f"{prefix}: 脚本内容不能为空(code)")
    return errors


def upgrade_node(node: dict):
    pass
