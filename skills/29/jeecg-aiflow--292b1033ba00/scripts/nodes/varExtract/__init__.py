import os
from .._base import create_node_from_template

_DIR = os.path.dirname(os.path.abspath(__file__))


def create_node(node_id: str, x: int, y: int) -> dict:
    return create_node_from_template(_DIR, node_id, x, y)


def validate_node(node: dict, prefix: str) -> list:
    errors = []
    props = node.get("properties", {})
    opts = props.get("options", {})
    model = opts.get("model", {})
    if not model.get("modeId"):
        errors.append(f"{prefix}: 必须选择模型(model.modeId)")
    if not model.get("params", {}).get("model"):
        errors.append(f"{prefix}: 必须填写模型名称(model.params.model)，取模型列表的text字段")
    input_params = props.get("inputParams", [])
    if not input_params:
        errors.append(f"{prefix}: 必须配置输入变量(inputParams)")
    elif input_params:
        first = input_params[0]
        if not first.get("nodeId") or not first.get("field"):
            errors.append(f"{prefix}: 输入变量必须选择引用节点和字段")
        p_type = first.get("type", "string")
        if p_type != "string":
            errors.append(f"{prefix}: 输入类型只支持 string，当前为 {p_type}")
    variables = opts.get("variables", [])
    if not variables:
        errors.append(f"{prefix}: 至少需要配置一个提取变量(variables)")
    else:
        names = []
        for i, v in enumerate(variables):
            vname = v.get("name", "")
            if not vname:
                errors.append(f"{prefix}: 第{i+1}个提取变量名称不能为空")
            elif vname in names:
                errors.append(f"{prefix}: 提取变量名称重复: {vname}")
            names.append(vname)
            if v.get("required") and not v.get("failTip"):
                errors.append(f"{prefix}: 必填变量 {vname} 需要配置提取失败提示(failTip)")
    return errors


def upgrade_node(node: dict):
    from .._base import merge_io_params
    props = node.get("properties", {})
    merge_io_params(props,
        def_input=[{"field": "input", "name": "", "nodeId": "", "type": "string"}])
    variables = props.get("options", {}).get("variables", [])
    output_params = []
    for v in variables:
        if v.get("name"):
            output_params.append({"field": v["name"], "name": v["name"], "type": v.get("type", "string")})
    output_params.append({"field": "failVarName", "name": "失败变量名", "type": "string"})
    output_params.append({"field": "failMessage", "name": "失败提示", "type": "string"})
    props["outputParams"] = output_params
