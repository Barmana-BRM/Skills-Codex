import os
from .._base import create_node_from_template

_DIR = os.path.dirname(os.path.abspath(__file__))


def create_node(node_id: str, x: int, y: int) -> dict:
    return create_node_from_template(_DIR, node_id, x, y)


def validate_node(node: dict, prefix: str) -> list:
    errors = []
    opts = node.get("properties", {}).get("options", {})
    if not opts.get("content"):
        errors.append(f"{prefix}: 回复内容不能为空(content)")
    return errors


def upgrade_node(node: dict):
    opts = node.get("properties", {}).setdefault("options", {})
    if opts.get("stream") is None:
        opts["stream"] = False
