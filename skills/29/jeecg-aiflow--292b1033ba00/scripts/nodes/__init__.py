"""
节点注册表
每个节点模块导出三个标准接口：
  - create_node(node_id, x, y) → dict    从 template.json 生成节点
  - validate_node(node, prefix) → list    返回校验错误列表
  - upgrade_node(node) → None             就地升级老数据格式（预留口子）
"""
import importlib
import os

_NODES_DIR = os.path.dirname(os.path.abspath(__file__))

# 自动发现所有节点目录（包含 template.json 的子目录）
_registry = {}

def _discover():
    for name in os.listdir(_NODES_DIR):
        sub = os.path.join(_NODES_DIR, name)
        if os.path.isdir(sub) and os.path.exists(os.path.join(sub, 'template.json')):
            _registry[name] = None  # lazy load

_discover()


def get_node_module(node_type: str):
    """获取节点模块，lazy import"""
    if node_type not in _registry:
        raise ValueError(f"未知的节点类型: {node_type}。可用: {list(_registry.keys())}")
    if _registry[node_type] is None:
        _registry[node_type] = importlib.import_module(f".{node_type}", package=__name__)
    return _registry[node_type]


def get_available_types() -> list:
    return list(_registry.keys())


def create_node(node_type: str, node_id: str, x: int, y: int) -> dict:
    mod = get_node_module(node_type)
    return mod.create_node(node_id, x, y)


def validate_node(node: dict) -> list:
    """调用节点自身的校验。如果节点模块没有 validate_node，返回空列表。"""
    ntype = node.get("type", "")
    if ntype not in _registry:
        return []
    mod = get_node_module(ntype)
    fn = getattr(mod, 'validate_node', None)
    if fn is None:
        return []
    props = node.get("properties", {})
    prefix = f"节点[{props.get('text', ntype)}({node.get('id', '?')})]"
    return fn(node, prefix)


def upgrade_node(node: dict):
    """调用节点自身的数据升级。如果没有 upgrade_node，跳过。"""
    ntype = node.get("type", "")
    if ntype not in _registry:
        return
    mod = get_node_module(ntype)
    fn = getattr(mod, 'upgrade_node', None)
    if fn:
        fn(node)
