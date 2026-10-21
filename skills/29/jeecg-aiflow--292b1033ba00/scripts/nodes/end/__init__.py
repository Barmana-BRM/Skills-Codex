import os
from .._base import create_node_from_template

_DIR = os.path.dirname(os.path.abspath(__file__))


def create_node(node_id: str, x: int, y: int) -> dict:
    return create_node_from_template(_DIR, node_id, x, y)


def validate_node(node: dict, prefix: str) -> list:
    errors = []
    props = node.get("properties", {})
    opts = props.get("options", {})
    output_type = opts.get("outputType", "text")
    output_params = props.get("outputParams", [])

    if output_type == "default":
        if not output_params:
            errors.append(f"{prefix}: outputType=default(JSON) 时，需要配置输出变量(outputParams)")
    elif output_type == "text":
        if not opts.get("outputContent"):
            errors.append(f"{prefix}: outputType=text 时，返回文本不能为空(outputContent)")
    elif output_type == "card":
        if not opts.get("cardConfig"):
            errors.append(f"{prefix}: outputType=card 时，需要绑定卡片(cardConfig)")
    return errors


def upgrade_node(node: dict):
    opts = node.get("properties", {}).get("options", {})

    if "outputText" in opts:
        if not opts.get("outputType"):
            opts["outputType"] = "text" if opts["outputText"] is True else "default"
        del opts["outputText"]
