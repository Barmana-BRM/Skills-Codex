"""
AIFlow API 封装层
所有后端 HTTP 接口的纯调用封装，不包含业务逻辑。
包含 JeecgBoot Sign 签名（移植自前端 signMd5Utils.js）。
"""
import hashlib
import json
import re
import time
import urllib.request
import urllib.error
import urllib.parse

_api_base = ""
_token = ""
_SIGN_SECRET = "dd05f1c54d63749eda95f9fa6d49v442a"


def init_api(api_base: str, token: str):
    global _api_base, _token
    _api_base = api_base.rstrip("/")
    _token = token


# ─── Sign 签名（移植自前端 signMd5Utils.js） ───

def _parse_query_string(url: str) -> dict:
    """从 URL 中解析查询参数和 path variable"""
    result = {}
    # 提取最后一段 path variable（含逗号的，如 /getDictItems/sys_user,realname,id）
    last_segment = url.rsplit("/", 1)[-1]
    if "?" in last_segment:
        last_segment = last_segment.split("?", 1)[0]
    if "," in last_segment:
        result["x-path-variable"] = urllib.parse.unquote(last_segment)
    # 解析 ? 后面的参数
    if "?" in url:
        qs = url.split("?", 1)[1]
        for kv in qs.split("&"):
            if "=" in kv:
                k, v = kv.split("=", 1)
                v = urllib.parse.unquote(v)
                # 数值转字符串
                try:
                    float(v)
                    result[k] = v
                except ValueError:
                    result[k] = v
            elif kv:
                result[kv] = ""
    return result


def _merge_and_sort(url_params: dict, request_params: dict = None, body_params: dict = None) -> dict:
    """合并所有参数并按 key 升序排序"""
    merged = dict(url_params)
    for src in (request_params, body_params):
        if src:
            for k, v in src.items():
                if isinstance(v, (int, float)):
                    v = str(v)
                elif isinstance(v, bool):
                    v = str(v).lower()
                merged[k] = v
    merged.pop("_t", None)
    return dict(sorted(merged.items()))


def _get_sign(url: str, request_params: dict = None, body_params: dict = None) -> str:
    """生成 JeecgBoot 请求签名"""
    url_params = _parse_query_string(url)
    sorted_obj = _merge_and_sort(url_params, request_params, body_params)
    raw = json.dumps(sorted_obj, ensure_ascii=False, separators=(",", ":")) + _SIGN_SECRET
    return hashlib.md5(raw.encode("utf-8")).hexdigest().upper()


def _get_timestamp() -> str:
    return str(int(time.time() * 1000))


# ─── HTTP 请求 ───

def _url(path: str):
    return f"{_api_base}{path}"


def _request(method: str, path: str, data=None, params=None, timeout=30):
    url = _url(path)
    if params:
        url += "?" + urllib.parse.urlencode(params)

    body_dict = data if data else None
    body = json.dumps(data, ensure_ascii=False).encode("utf-8") if data else None

    # 生成签名
    sign = _get_sign(url, params, body_dict)
    timestamp = _get_timestamp()

    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "X-Access-Token": _token,
        "X-Sign": sign,
        "X-TIMESTAMP": timestamp,
    }

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {error_body}")

# ─── 流程 CRUD ───

def list_flows(page=1, size=10, keyword=None, exclude_id=None):
    params = {"pageNo": page, "pageSize": size}
    if keyword:
        params["name"] = f"*{keyword}*"
    if exclude_id:
        params["excludeFlowId"] = exclude_id
    return _request("GET", "/airag/flow/list", params=params)

def add_flow(name: str, descr: str = "", icon: str = "", chain: str = "", design=None):
    """创建流程。chain 和 design 为必填（后端校验），一步完成创建+保存设计。"""
    data = {"name": name, "descr": descr, "icon": icon, "chain": chain}
    if design is not None:
        data["design"] = json.dumps(design, ensure_ascii=False) if isinstance(design, dict) else design
    return _request("POST", "/airag/flow/add", data=data)

def edit_flow(flow_id: str, name: str = None, descr: str = None, icon: str = None, status: str = None):
    data = {"id": flow_id}
    if name is not None:
        data["name"] = name
    if descr is not None:
        data["descr"] = descr
    if icon is not None:
        data["icon"] = icon
    if status is not None:
        data["status"] = status
    return _request("PUT", "/airag/flow/edit", data=data)

def delete_flow(flow_id: str):
    return _request("DELETE", "/airag/flow/delete", params={"id": flow_id})

def delete_flows_batch(ids: list):
    return _request("DELETE", "/airag/flow/deleteBatch", params={"ids": ",".join(ids)})

def query_flow_by_id(flow_id: str):
    return _request("GET", "/airag/flow/queryById", params={"id": flow_id})

def copy_flow(flow_id: str, name: str = None):
    data = {"id": flow_id}
    if name:
        data["name"] = name
    return _request("POST", "/airag/flow/copyFlow", data=data)

# ─── 设计保存 ───

def save_design(flow_id: str, name: str, chain: str, design: dict):
    data = {
        "id": flow_id,
        "name": name,
        "chain": chain,
        "design": json.dumps(design, ensure_ascii=False) if isinstance(design, dict) else design,
    }
    return _request("PUT", "/airag/flow/design/save", data=data)

# ─── 发布管理 ───

def release_flow(flow_id: str):
    return edit_flow(flow_id, status="release")

def unrelease_flow(flow_id: str):
    return edit_flow(flow_id, status="enable")

# ─── 子流程 ───

def list_subflows(page=1, size=10, exclude_id=None):
    params = {"pageNo": page, "pageSize": size}
    if exclude_id:
        params["excludeFlowId"] = exclude_id
    return _request("GET", "/airag/flow/subflowList", params=params)

def query_subflow_by_id(flow_id: str):
    return _request("GET", "/airag/flow/querySubflowById", params={"id": flow_id})

# ─── 调试运行 ───

def debug_flow(flow: dict, input_params: dict = None):
    data = {"flow": flow}
    if input_params:
        data["inputParams"] = input_params
    return _request("POST", "/airag/flow/debug", data=data, timeout=600)

def run_flow(flow_id: str, input_params: dict = None, response_mode: str = "blocking"):
    data = {
        "flowId": flow_id,
        "responseMode": response_mode,
    }
    if input_params:
        data["inputParams"] = input_params
    return _request("POST", "/airag/flow/run", data=data, timeout=3600)

def run_flow_plugin(flow_id: str, input_params: dict = None):
    data = input_params or {}
    return _request("POST", f"/airag/flow/plugin/run/{flow_id}", data=data, timeout=3600)

# ─── 应用字典 ───

def list_app_dict():
    return _request("GET", "/airag/app/listDict")

# ─── AI 模型查询 ───

def list_llm_models():
    """查询可用的 LLM 模型列表（用于 llm/classifier/varExtract 节点的 model.modeId）
    返回: {"success": true, "result": [{"value": "模型ID", "text": "模型名称"}, ...]}
    """
    path = "/sys/dict/getDictItems/airag_model%20where%20model_type%20=%20'LLM'%20and%20activate_flag%20=%201,name,id"
    return _request("GET", path)

def list_knowledge_bases(page=1, size=100):
    """查询知识库列表（用于 knowledge/knowledgeWrite 节点的 knowIds）"""
    return _request("GET", "/airag/knowledge/list", params={"pageNo": page, "pageSize": size})

def list_data_sources(page=1, size=100, keyword=None):
    """查询数据源列表（用于 sql 节点的 sql.dataSourceId）"""
    params = {"pageNo": page, "pageSize": size, "column": "createTime", "order": "desc"}
    if keyword:
        params["name"] = f"*{keyword}*"
    return _request("GET", "/sys/dataSource/list", params=params)

# ─── AI 生成测试数据 ───

def gen_test_data(flow_id: str, input_params_schema: list):
    data = {"flowId": flow_id, "inputParams": input_params_schema}
    return _request("POST", "/airag/flow/aigc/test-data", data=data, timeout=120)
