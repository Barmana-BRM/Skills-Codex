import os
from .._base import create_node_from_template

_DIR = os.path.dirname(os.path.abspath(__file__))


def create_node(node_id: str, x: int, y: int) -> dict:
    return create_node_from_template(_DIR, node_id, x, y)


def validate_node(node: dict, prefix: str) -> list:
    errors = []
    opts = node.get("properties", {}).get("options", {})
    http_cfg = opts.get("http", {})
    if not http_cfg.get("url"):
        errors.append(f"{prefix}: 请求地址不能为空(http.url)")
    if not http_cfg.get("method"):
        errors.append(f"{prefix}: 请求方法不能为空(http.method)")
    return errors


def upgrade_node(node: dict):
    from .._base import merge_io_params
    props = node.get("properties", {})
    merge_io_params(props,
        def_input=[],
        def_output=[
            {"field": "body", "name": "回复内容", "type": "string"},
            {"field": "statusCode", "name": "状态码", "type": "number"},
        ])
    http_cfg = props.get("options", {}).get("http", {})
    rb = http_cfg.get("requestBody")
    if rb is None or isinstance(rb, str):
        http_cfg["requestBody"] = {"type": "none", "body": rb or ""}
