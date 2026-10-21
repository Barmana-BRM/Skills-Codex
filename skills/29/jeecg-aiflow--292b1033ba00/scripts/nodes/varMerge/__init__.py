import os
from .._base import create_node_from_template

_DIR = os.path.dirname(os.path.abspath(__file__))


def create_node(node_id: str, x: int, y: int) -> dict:
    return create_node_from_template(_DIR, node_id, x, y)


def validate_node(node: dict, prefix: str) -> list:
    errors = []
    opts = node.get("properties", {}).get("options", {})
    groups = opts.get("varGroups", [])
    if not groups:
        errors.append(f"{prefix}: 变量分组不能为空(varGroups)")
    else:
        for i, g in enumerate(groups):
            if not g.get("name"):
                errors.append(f"{prefix}: 第{i+1}个分组名称不能为空")
            v_list = g.get("vars", [])
            if not v_list:
                errors.append(f"{prefix}: 第{i+1}个分组({g.get('name', '')})的变量列表为空(vars)")
            else:
                for j, v in enumerate(v_list):
                    if v.get("isCustom"):
                        continue
                    if not v.get("nodeId"):
                        errors.append(f"{prefix}: 分组{g.get('name', '')}第{j+1}个变量缺少引用节点(nodeId)")
                    if not v.get("field"):
                        errors.append(f"{prefix}: 分组{g.get('name', '')}第{j+1}个变量缺少引用字段(field)")
    return errors


def upgrade_node(node: dict):
    pass
