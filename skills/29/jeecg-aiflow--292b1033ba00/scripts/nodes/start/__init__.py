import os
from .._base import create_node_from_template

_DIR = os.path.dirname(os.path.abspath(__file__))


def create_node(node_id: str, x: int, y: int) -> dict:
    node = create_node_from_template(_DIR, node_id, x, y)
    node["id"] = "start-node"
    return node


def validate_node(node: dict, prefix: str) -> list:
    errors = []
    opts = node.get("properties", {}).get("options", {})
    cron = opts.get("cronTrigger", {})
    if cron.get("enabled"):
        input_params = node.get("properties", {}).get("inputParams", [])
        default_params = cron.get("inputParams", {})
        for p in input_params:
            if p.get("required") and p.get("field") != "history":
                val = default_params.get(p.get("field"))
                if val is None or val == "":
                    errors.append(f"{prefix}: 定时触发器：存在必填参数未配置默认值")
                    break
    return errors


def upgrade_node(node: dict):
    from .._base import merge_io_params
    props = node.get("properties", {})
    merge_io_params(props,
        def_input=[
            {"field": "content", "name": "用户问题", "type": "string", "required": False},
            {"field": "history", "name": "历史记录", "type": "string[]", "required": False},
            {"field": "images", "name": "图片", "type": "picture", "required": False},
        ])
    opts = props.setdefault("options", {})
    cron = opts.setdefault("cronTrigger", {
        "enabled": False, "cronType": "day", "cronExp": "0 0 0 * * ?",
        "beginTime": None, "endTime": None, "inputParams": {},
        "custom": {"minute": 0, "hour": 0, "dayOfMonth": 1, "dayOfWeek": "MON", "month": 1},
    })
    if "custom" not in cron:
        cron["custom"] = {"minute": 0, "hour": 0, "dayOfMonth": 1, "dayOfWeek": "MON", "month": 1}
    if "importParams" in cron and "inputParams" not in cron:
        cron["inputParams"] = cron.pop("importParams")
    for p in props.get("inputParams", []):
        if p.get("field") == "history":
            p["required"] = False
