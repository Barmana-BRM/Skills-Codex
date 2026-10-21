import os
from .._base import create_node_from_template

_DIR = os.path.dirname(os.path.abspath(__file__))


def create_node(node_id: str, x: int, y: int) -> dict:
    return create_node_from_template(_DIR, node_id, x, y)


def validate_node(node: dict, prefix: str) -> list:
    errors = []
    opts = node.get("properties", {}).get("options", {})
    if not opts.get("knowIds"):
        errors.append(f"{prefix}: 必须选择至少一个知识库(knowIds)")
    write_type = opts.get("writeType", "text")
    if write_type == "text" and not opts.get("content"):
        errors.append(f"{prefix}: writeType=text 时，写入内容不能为空(content)")
    elif write_type == "file" and not opts.get("fileSources"):
        errors.append(f"{prefix}: writeType=file 时，文件来源不能为空(fileSources)")
    return errors


def upgrade_node(node: dict):
    props = node.get("properties", {})
    opts = props.setdefault("options", {})
    if opts.get("writeType") is None:
        opts["writeType"] = "text"
    if not isinstance(opts.get("fileSources"), list):
        opts["fileSources"] = []
    if opts.get("segmentStrategy") is None:
        opts["segmentStrategy"] = "auto"
    if opts.get("separator") is None:
        opts["separator"] = "\\n"
    if opts.get("customSeparator") is None:
        opts["customSeparator"] = ""
    if opts.get("maxSegment") is None:
        opts["maxSegment"] = 800
    if opts.get("overlap") is None:
        opts["overlap"] = 10
    if not isinstance(opts.get("textRules"), list):
        opts["textRules"] = []
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
