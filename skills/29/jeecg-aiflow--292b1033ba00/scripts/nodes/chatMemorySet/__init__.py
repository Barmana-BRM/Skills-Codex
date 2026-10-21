import os
from .._base import create_node_from_template

_DIR = os.path.dirname(os.path.abspath(__file__))


def create_node(node_id: str, x: int, y: int) -> dict:
    return create_node_from_template(_DIR, node_id, x, y)


def validate_node(node: dict, prefix: str) -> list:
    return []


def upgrade_node(node: dict):
    props = node.get("properties", {})
    opts = props.setdefault("options", {})
    if not isinstance(opts.get("waitForVectorize"), bool):
        opts["waitForVectorize"] = False
    if not isinstance(opts.get("waitTimeout"), (int, float)) or opts.get("waitTimeout", 0) <= 0:
        opts["waitTimeout"] = 300
    if opts.get("vectorizeFailStrategy") not in ("error", "ignore"):
        opts["vectorizeFailStrategy"] = "ignore"
    out = props.setdefault("outputParams", [])
    if not isinstance(out, list):
        out = []
        props["outputParams"] = out
    if not any(p.get("field") == "documentIds" for p in out):
        out.append({"field": "documentIds", "name": "documentIds", "type": "string[]"})
