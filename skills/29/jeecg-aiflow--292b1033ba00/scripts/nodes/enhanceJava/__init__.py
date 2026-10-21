import os
from .._base import create_node_from_template

_DIR = os.path.dirname(os.path.abspath(__file__))


def create_node(node_id: str, x: int, y: int) -> dict:
    return create_node_from_template(_DIR, node_id, x, y)


def validate_node(node: dict, prefix: str) -> list:
    errors = []
    opts = node.get("properties", {}).get("options", {})
    enhance = opts.get("enhance", {})
    if not enhance.get("path"):
        errors.append(f"{prefix}: 必须配置 Java 类路径或 Bean 名称(enhance.path)")
    return errors


def upgrade_node(node: dict):
    pass
