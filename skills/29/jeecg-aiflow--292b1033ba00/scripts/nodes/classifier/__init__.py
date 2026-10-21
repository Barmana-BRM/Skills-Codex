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
    cats = opts.get("categories", [])
    if not cats:
        errors.append(f'{prefix}: 分类列表不能为空(categories)')
    else:
        for i, cat in enumerate(cats):
            if not cat.get("category"):
                errors.append(f'{prefix}: 第{i+1}个分类描述不能为空(category)')
    return errors


def upgrade_node(node: dict):
    from .._base import merge_io_params
    props = node.get("properties", {})
    merge_io_params(props,
        def_output=[
            {"field": "index", "name": "分类索引", "type": "number"},
            {"field": "content", "name": "分类描述", "type": "string"},
        ])
    for p in props.get("outputParams", []):
        if p.get("field") == "content":
            p["name"] = "分类描述"
