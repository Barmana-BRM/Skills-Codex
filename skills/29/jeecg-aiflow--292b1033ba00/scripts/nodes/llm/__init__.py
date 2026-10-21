import os
from .._base import create_node_from_template

_DIR = os.path.dirname(os.path.abspath(__file__))


def create_node(node_id: str, x: int, y: int) -> dict:
    return create_node_from_template(_DIR, node_id, x, y)


def validate_node(node: dict, prefix: str) -> list:
    errors = []
    opts = node.get("properties", {}).get("options", {})
    model = opts.get("model", {})
    if not model.get("modeId"):
        errors.append(f"{prefix}: 必须选择模型(model.modeId)")
    if not model.get("params", {}).get("model"):
        errors.append(f"{prefix}: 必须填写模型名称(model.params.model)，取模型列表的text字段")
    if opts.get("structuredOutput"):
        fields = opts.get("structuredOutputFields", [])
        if not fields:
            errors.append(f"{prefix}: 启用结构化输出时，至少需要配置一个输出字段")
        elif any(not f.get("field") for f in fields):
            errors.append(f"{prefix}: 结构化输出字段名不能为空")
    return errors


def upgrade_node(node: dict):
    from .._base import merge_io_params
    props = node.get("properties", {})
    opts = props.setdefault("options", {})
    merge_io_params(props,
        def_input=[],
        def_output=[{"field": "text", "name": "回复内容", "type": "string"}])
    if not isinstance(opts.get("showToolExecution"), bool):
        opts["showToolExecution"] = False
    if not isinstance(opts.get("structuredOutput"), bool):
        opts["structuredOutput"] = False
    if not isinstance(opts.get("structuredOutputFields"), list):
        opts["structuredOutputFields"] = []
    if opts.get("systemPromptMode") == "ref" and not opts.get("systemPromptRefId"):
        opts["systemPromptMode"] = "fill"
