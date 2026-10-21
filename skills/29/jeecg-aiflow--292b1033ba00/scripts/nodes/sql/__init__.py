import os
from .._base import create_node_from_template

_DIR = os.path.dirname(os.path.abspath(__file__))


def create_node(node_id: str, x: int, y: int) -> dict:
    return create_node_from_template(_DIR, node_id, x, y)


def validate_node(node: dict, prefix: str) -> list:
    errors = []
    opts = node.get("properties", {}).get("options", {})
    sql_cfg = opts.get("sql", {})
    if not sql_cfg.get("dataSourceId"):
        errors.append(f"{prefix}: 必须选择数据源(sql.dataSourceId)")
    if not sql_cfg.get("content"):
        errors.append(f"{prefix}: SQL语句不能为空(sql.content)")
    return errors


def upgrade_node(node: dict):
    pass
