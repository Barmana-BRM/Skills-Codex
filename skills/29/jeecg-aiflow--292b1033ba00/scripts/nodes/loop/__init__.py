import os
from .._base import create_node_from_template

_DIR = os.path.dirname(os.path.abspath(__file__))


def create_node(node_id: str, x: int, y: int) -> dict:
    return create_node_from_template(_DIR, node_id, x, y)


def validate_node(node: dict, prefix: str) -> list:
    errors = []
    props = node.get("properties", {})
    opts = props.get("options", {})
    loop_type = opts.get("type", "")
    if not loop_type:
        errors.append(f"{prefix}: 必须选择循环类型(type)")
    elif loop_type == "counted":
        max_times = opts.get("maxLoopTimes", 0)
        if not max_times or max_times <= 0:
            errors.append(f"{prefix}: 循环次数必须大于0(maxLoopTimes)")
    elif loop_type == "array":
        items_param = opts.get("loopItemsParam", {})
        if not items_param.get("nodeId") or not items_param.get("field"):
            errors.append(f"{prefix}: 数组循环必须选择迭代数组来源(loopItemsParam)")
    return errors


def upgrade_node(node: dict):
    pass
