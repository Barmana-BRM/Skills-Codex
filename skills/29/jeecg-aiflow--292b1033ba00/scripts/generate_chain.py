"""
AIFlow Chain 生成器 (Python)
将 design JSON (nodes + edges) 转换为 LiteFlow EL 表达式。

源码移植自前端 logicflow-liteflow 库：
  - MyParse.ts      → class MyParse
  - MyContext.ts     → class MyContext
  - ELStack.ts       → class ELStack
  - type/ELNode.ts   → class ELNode
  - type/ELType.ts   → ELType / GroupType 常量
  - switch-node/utils.ts     → switch_get_case_list / switch_get_anchor_id
  - classifier-node/utils.ts → classifier_get_case_list / classifier_get_anchor_id
  - var-extract-node/utils.ts → var_extract_get_anchor_id

源文件位置:
  E:\\Projects\\BJGJ\\jeecg-claude-root\\jeecgboot-vue3\\src\\views\\super\\airag\\aiflow\\lib\\logicflow-liteflow\\
  E:\\Projects\\BJGJ\\jeecg-claude-root\\jeecgboot-vue3\\src\\views\\super\\airag\\aiflow\\nodes\\switch-node\\utils.ts
  E:\\Projects\\BJGJ\\jeecg-claude-root\\jeecgboot-vue3\\src\\views\\super\\airag\\aiflow\\nodes\\classifier-node\\utils.ts
  E:\\Projects\\BJGJ\\jeecg-claude-root\\jeecgboot-vue3\\src\\views\\super\\airag\\aiflow\\nodes\\var-extract-node\\utils.ts

最后同步日期: 2026-06-03

用法:
  python generate_chain.py < design.json
  echo '<json>' | python generate_chain.py
"""
import copy
import json
import sys

# ─── 常量（ELType.ts） ───

class ELType:
    ID = "ID"
    WHEN = "WHEN"
    THEN = "THEN"
    SWITCH = "SWITCH"
    IF = "IF"
    GROUP = "GROUP"
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"
    OR = "OR"
    AND = "AND"
    NOT = "NOT"

class GroupType:
    CATCH = "CATCH"
    LOGIC = "LOGIC"
    CONFIG = "CONFIG"
    FOR = "FOR"
    WHILE = "WHILE"
    ITERATOR = "ITERATOR"

class NodeTypes:
    START = "start"
    END = "end"
    LLM = "llm"
    SWITCH = "switch"
    CLASSIFIER = "classifier"
    KNOWLEDGE = "knowledge"
    KNOWLEDGE_WRITE = "knowledgeWrite"
    CODE = "code"
    SUBFLOW = "subflow"
    ENHANCE_JAVA = "enhanceJava"
    HTTP = "http"
    TOOLS = "tools"
    BRAVE_SEARCH = "braveSearch"
    REPLY = "reply"
    SQL = "sql"
    LOOP = "loop"
    LOOP_BREAK = "loopBreak"
    LOOP_CONTINUE = "loopContinue"
    LOOP_BODY = "loopBody"
    SET_LOOP_VAR = "setLoopVar"
    VAR_MERGE = "varMerge"
    VAR_EXTRACT = "varExtract"
    CHAT_VAR_GET = "chatVarGet"
    CHAT_VAR_SET = "chatVarSet"
    CHAT_MEMORY_GET = "chatMemoryGet"
    CHAT_MEMORY_SET = "chatMemorySet"
    SYS_GET_USERINFO = "sysGetUserinfo"

CUSTOM_SWITCH_NODES = [NodeTypes.SWITCH, NodeTypes.CLASSIFIER, NodeTypes.VAR_EXTRACT]

# ─── Switch/Classifier/VarExtract utils ───

def switch_get_case_list(node):
    """switch-node/utils.ts → getCaseList"""
    result = []
    opts = (node.get("properties") or {}).get("options") or {}
    if_list = opts.get("if")
    if isinstance(if_list, list):
        for i, item in enumerate(if_list):
            result.append({
                "type": "IF" if i == 0 else "ELIF",
                "label": f"CASE {i + 1}",
                "value": item,
            })
    if opts.get("else"):
        result.append({"type": "ELSE", "label": "ELSE", "value": opts["else"]})
    return result

def switch_get_anchor_id(node_id, case_type, case_idx):
    """switch-node/utils.ts → getAnchorId"""
    if case_type == "IF":
        case_id = "source_if"
    elif case_type == "ELSE":
        case_id = "source_else"
    else:
        case_id = f"case_{case_idx}"
    return f"{node_id}_{case_id}"

def classifier_get_case_list(node):
    """classifier-node/utils.ts → getCaseList"""
    result = []
    opts = (node.get("properties") or {}).get("options") or {}
    cats = opts.get("categories")
    if isinstance(cats, list):
        for i, item in enumerate(cats):
            result.append({
                "type": "CASE",
                "label": f"分类 {i + 1}",
                "value": item,
            })
    if opts.get("else"):
        result.append({"type": "ELSE", "label": "ELSE", "value": opts["else"]})
    return result

def classifier_get_anchor_id(node_id, case_type, case_idx):
    """classifier-node/utils.ts → getAnchorId"""
    case_id = f"case_{'else' if case_type == 'ELSE' else case_idx}"
    return f"{node_id}_{case_id}"

def var_extract_get_anchor_id(node_id, anchor):
    """var-extract-node/utils.ts → getAnchorId"""
    return f"{node_id}_{anchor}"


# ─── ELNode（type/ELNode.ts） ───

class ELNode:
    def __init__(self, id_=""):
        self.id = id_
        self.type = ""
        self.origin_type = ""
        self.group_type = None
        self.alias_id = ""
        self.name = ""
        self.data = ""
        self.tag = ""
        self.node_id = ""
        self.child = []
        self.coming_edge_text = ""
        self.el_string = None
        self.properties = None
        self.start_node = None
        self.break_node = None
        self.exception_node = None
        self.start_num = 0
        self.max_line_num = 25
        self.anchors_next_ids = []

    def add_child(self, n):
        self.child.append(n)

    @property
    def child_first_id(self):
        if not self.child:
            return ""
        c = self.child[0]
        if c.type in (ELType.WHEN, ELType.THEN):
            return c.child_first_id
        return c.id

    def get_el_string(self):
        tag_str = ""
        if self.type != ELType.GROUP and self.properties and self.properties.get("tag"):
            tag_str = f".tag('{self.properties['tag']}')"
        data_str = ""
        if self.properties and self.properties.get("data"):
            data_str = f".data('{self.properties['data']}')"
        return f"{self.get_el_string_raw()}{tag_str}{data_str}"

    def get_el_string_raw(self):
        if self.type == ELType.ID:
            return self.node_id
        if self.el_string:
            return self.el_string
        if self.type == ELType.IF:
            return self._el_if()
        if self.type == ELType.GROUP:
            return self._el_group()
        if self.type == ELType.SWITCH:
            return self._el_switch()
        if self.type in (ELType.WHEN, ELType.THEN):
            return self._el_when_then()
        if self.type == NodeTypes.CODE:
            return self.id
        return self.type

    @staticmethod
    def _indent(s):
        return "    " + s.replace("\n", "\n    ")

    def _el_when_then(self):
        children = self.child or []
        id_str = ""
        tag_str = ""
        if self.alias_id:
            if self.alias_id.startswith("tag:"):
                id_str = f'.tag("{self.alias_id[4:]}")'
            else:
                id_str = f'.id("{self.alias_id}")'
        if self.child_first_id:
            tag_str = f'.tag("{self.child_first_id}")'
        strs = [c.get_el_string() for c in children]
        joins = ",".join(strs)
        if len(children) == 1:
            if not self.alias_id or children[0].type in (ELType.THEN, ELType.WHEN):
                return f"{joins}{id_str}"
        if len(joins) < self.max_line_num - 6:
            return f"{self.type}({joins}){tag_str or id_str}"
        formatted = self._indent(",\n".join(strs))
        return f"{self.type}(\n{formatted}\n){tag_str or id_str}"

    def _el_group(self):
        children = self.child or []
        strs = [c.get_el_string() for c in children]
        joins = ",".join(strs)
        if self.group_type == GroupType.CONFIG:
            ig = ".ignoreError(true)" if self.properties and self.properties.get("ignoreError") else ""
            an = "any(true)" if self.properties and self.properties.get("any") else ""
            mu = f"must({self.properties['must']})" if self.properties and self.properties.get("must") else ""
            return f"{joins}{ig}{an}{mu}"
        if self.group_type == GroupType.LOGIC:
            return self.el_string or ""
        name = self.group_type
        if self.group_type == GroupType.CATCH:
            ex_str = self.exception_node.get_el_string()
            return f"{name}({joins}).DO({ex_str})"
        break_str = f".BREAK({self.break_node.get_el_string()})" if self.break_node else ""
        if self.origin_type == NodeTypes.LOOP:
            start_str = f"{self.origin_type}.tag('{self.id}')"
        else:
            start_str = self.start_node.get_el_string() if (self.start_node and self.start_node.node_id) else str(self.start_num)
        if len(children) == 1:
            return f"{name}({start_str}).DO({joins}){break_str}"
        return f"{name}({start_str}).DO(WHEN({joins})){break_str}"

    def _el_if(self):
        strs = [c.get_el_string() for c in (self.child or [])]
        joins = ",".join(strs)
        if len(joins) < self.max_line_num - 4:
            return f"IF({joins})"
        formatted = self._indent(",\n".join(strs))
        return f"IF(\n{formatted}\n)"

    def _el_switch(self):
        self._parse_switch_children()
        strs = [c.get_el_string() for c in (self.child or [])]
        joins = ",".join(strs)
        ot = self.origin_type or NodeTypes.SWITCH
        id_str = f"{ot}.tag('{self.node_id}')"
        switch_tag = f".tag('{self.id}')"
        if len(joins) < self.max_line_num - 13 - len(self.node_id or ""):
            return f"SWITCH({id_str}).to({joins}){switch_tag}"
        formatted = self._indent(",\n".join(strs))
        return f"SWITCH({id_str}).to(\n{formatted}\n){switch_tag}"

    def _parse_switch_children(self):
        if not self.anchors_next_ids:
            return
        children = self.child or []
        if len(children) <= len(self.anchors_next_ids):
            return
        for ani in self.anchors_next_ids:
            next_ids = ani["nextIds"]
            if len(next_ids) <= 1:
                continue
            when_node = ELNode()
            when_node.type = ELType.WHEN
            for ni, nid in enumerate(next_ids):
                idx = None
                for ci, ch in enumerate(children):
                    cid = ch.id
                    if not cid and ch.child:
                        cid = ch.child[0].id
                    if cid == nid or ch.child_first_id == nid:
                        idx = ci
                        break
                if idx is not None:
                    if ni == 0:
                        when_node.add_child(children[idx])
                        children[idx] = when_node
                    else:
                        when_node.add_child(children.pop(idx))
        self.child = children


# ─── ELStack（ELStack.ts） ───

class ELStack:
    def __init__(self):
        self.stack = []
        self.ebp_stack = []

    def pop(self):
        return self.stack.pop()

    def push(self, item):
        self.stack.append(item)

    def resolve(self):
        ebp = self.ebp_stack[-1]
        type_node = self.stack[ebp + 1]
        for i in range(ebp + 2, len(self.stack)):
            type_node.add_child(self.stack[i])
        return type_node

    def quit(self):
        type_node = self.resolve()
        end_point = self.stack[self.ebp_stack[-1]]
        while len(self.stack) > self.ebp_stack[-1]:
            self.stack.pop()
        self.stack.append(type_node)
        self.ebp_stack.pop()
        return end_point

    def create(self):
        self.ebp_stack.append(len(self.stack))
        self.stack.append(ELNode())

    def add_end_point(self, n):
        self.stack[self.ebp_stack[-1]] = n


# ─── MyContext（MyContext.ts） ───

class MyContext:
    def __init__(self, anchor_next_ids_map):
        self.end_points = {}
        self.source_num = {}
        self.node_map = {}
        self.in_group_node = {}
        self.el_stack = ELStack()
        self.start_id = "start"
        self.end_id = "end"
        self.anchor_next_ids_map = anchor_next_ids_map

    def is_end(self, id_):
        return self.end_id == id_

    def is_start(self, id_):
        return self.start_id == id_

    def get_node_by_id(self, id_):
        return self.node_map.get(id_)

    def _init_edge(self, src_id, end_id, edge_text=""):
        if self.in_group_node.get(src_id) or self.in_group_node.get(end_id):
            return
        if src_id not in self.end_points:
            self.end_points[src_id] = []
        node = self.node_map[end_id]
        node.coming_edge_text = edge_text
        self.end_points[src_id].append(node)
        self.source_num[end_id] = self.source_num.get(end_id, 0) + 1

    def init(self, logic_flow):
        group_nodes = []
        for n in logic_flow.get("nodes", []):
            if not n.get("id"):
                continue
            t = self._type_format(n["type"])
            if t == ELType.GROUP:
                group_nodes.append(n)
                continue
            self._init_el_node(n)

        for n in group_nodes:
            self._init_loop_el_node(n)

        start = ELNode(self.start_id)
        self.node_map[self.start_id] = start
        end = ELNode(self.end_id)
        self.node_map[self.end_id] = end

        for edge in logic_flow.get("edges", []):
            src = edge.get("sourceNodeId")
            tgt = edge.get("targetNodeId")
            if not src or not tgt:
                continue
            src_node = self.node_map.get(src)
            text = edge.get("text", "")
            if isinstance(text, dict):
                text = text.get("value", "")
            if src_node and src_node.type == ELType.IF:
                self._parse_if_edge(text, src, tgt)
            else:
                self._init_edge(src, tgt, text or "")

        for n in logic_flow.get("nodes", []):
            nid = n.get("id")
            if not nid or self.in_group_node.get(nid):
                continue
            if nid not in self.end_points:
                self._init_edge(nid, self.end_id)
            if nid not in self.source_num:
                self._init_edge(self.start_id, nid)

        if not logic_flow.get("nodes"):
            self._init_edge(self.start_id, self.end_id)

    def _parse_if_edge(self, text, src_id, tgt_id):
        target = self.node_map[tgt_id]
        ends = self.end_points.get(src_id)
        if not ends:
            ends = [None, None]
        true_texts = ["是", "true", "True", "TRUE"]
        false_texts = ["否", "false", "False", "FALSE"]
        if text in true_texts:
            if ends[0]:
                if len(ends) < 2:
                    ends.append(ends[0])
                else:
                    ends[1] = ends[0]
            ends[0] = target
        elif text in false_texts:
            if len(ends) < 2:
                ends.append(None)
            if ends[1]:
                ends[0] = ends[1]
            ends[1] = target
        else:
            if not ends[0]:
                ends[0] = target
            else:
                if len(ends) < 2:
                    ends.append(target)
                else:
                    ends[1] = target
        self.end_points[src_id] = ends
        self.source_num[tgt_id] = self.source_num.get(tgt_id, 0) + 1

    def _init_el_node(self, lf_node):
        props = dict(lf_node.get("properties") or {})
        props["nodeId"] = lf_node["id"]
        props["name"] = props.get("text", "")
        props["tag"] = lf_node["id"]
        lf_node["properties"] = props

        node = ELNode()
        node.id = lf_node["id"]
        node.type = self._type_format(lf_node["type"])
        node.origin_type = lf_node["type"]
        self._handle_switch_node(node, lf_node)
        node.properties = props
        node.node_id = props.get("nodeId", "")
        node.name = props.get("name", "")
        node.group_type = props.get("groupType")
        node.data = props.get("data", "")
        node.alias_id = props.get("aliasId", "")
        node.tag = props.get("tag", "")
        node.start_num = props.get("startNum", 0)
        self.node_map[node.id] = node
        return node

    def _handle_switch_node(self, node, lf_node):
        if node.type != ELType.SWITCH:
            return
        if node.origin_type == NodeTypes.SWITCH:
            case_list = switch_get_case_list(lf_node)
            get_anchor = switch_get_anchor_id
        elif node.origin_type == NodeTypes.CLASSIFIER:
            case_list = classifier_get_case_list(lf_node)
            get_anchor = classifier_get_anchor_id
        elif node.origin_type == NodeTypes.VAR_EXTRACT:
            return
        else:
            return
        for i, c in enumerate(case_list):
            anchor_id = get_anchor(lf_node["id"], c["type"], i + 1)
            next_ids = self.anchor_next_ids_map.get(anchor_id)
            if next_ids:
                node.anchors_next_ids.append({"anchorId": anchor_id, "nextIds": next_ids})

    def _init_loop_el_node(self, lf_node):
        if not lf_node.get("flowData") or not lf_node["flowData"].get("nodes"):
            lf_node["flowData"] = {"nodes": [], "edges": []}
        node = self._init_el_node(lf_node)
        if node.group_type == GroupType.LOGIC:
            node.el_string = self._get_logic_str(lf_node["flowData"])
        else:
            node.add_child(MyParse(lf_node["flowData"], self.anchor_next_ids_map).parse())
        self.node_map[node.id] = node
        for n in lf_node["flowData"]["nodes"]:
            self.in_group_node[n["id"]] = True

    def _type_format(self, t):
        if t in CUSTOM_SWITCH_NODES:
            return ELType.SWITCH
        if t == NodeTypes.LOOP:
            return ELType.GROUP
        mapping = {"IF": ELType.IF, "SWITCH": ELType.SWITCH, "GROUP": ELType.GROUP,
                    "AND": ELType.AND, "NOT": ELType.NOT, "OR": ELType.OR}
        return mapping.get(t, t)

    def get_end_num(self, n):
        return len(self.end_points.get(n.id, []))

    def get_end_list(self, n):
        return self.end_points.get(n.id, [])

    def push(self, n):
        self.el_stack.push(n)

    def pop(self):
        return self.el_stack.pop()

    def create_stack_env(self, node):
        self.el_stack.create()
        nn = ELNode()
        nn.id = node.id
        nn.type = node.type
        nn.origin_type = node.origin_type
        nn.group_type = node.group_type
        nn.alias_id = node.alias_id
        nn.name = node.name
        nn.data = node.data
        nn.tag = node.tag
        nn.node_id = node.node_id
        nn.child = node.child
        nn.coming_edge_text = node.coming_edge_text
        nn.el_string = node.el_string
        nn.anchors_next_ids = node.anchors_next_ids
        nn.start_node = node.start_node
        nn.break_node = node.break_node
        nn.exception_node = node.exception_node
        nn.start_num = node.start_num
        self.el_stack.push(nn)

    def quit_stack_env(self):
        return self.el_stack.quit()

    def set_stack_end_point(self, n):
        self.el_stack.add_end_point(n)

    def _get_logic_str(self, logic_flow):
        node_map = {}
        for n in logic_flow["nodes"]:
            node_map[n["id"]] = n
        target_num_map = {}
        for e in logic_flow["edges"]:
            target_num_map[e["sourceNodeId"]] = target_num_map.get(e["sourceNodeId"], 0) + 1
        first_zero = None
        for n in logic_flow["nodes"]:
            if not target_num_map.get(n["id"]):
                first_zero = n["id"]
                break

        def get_str(id_):
            nd = node_map[id_]
            start_ids = [e["sourceNodeId"] for e in logic_flow["edges"] if e["targetNodeId"] == id_]
            parts = []
            for sid in start_ids:
                sn = node_map[sid]
                if sn["type"] == ELType.ID:
                    parts.append(sn.get("properties", {}).get("nodeId", ""))
                elif sn["type"] in (ELType.AND, ELType.OR, ELType.NOT):
                    parts.append(get_str(sn["id"]))
                else:
                    raise ValueError("未知的节点类型")
            return f"{nd['type']}({','.join(parts)})"

        return get_str(first_zero)


# ─── MyParse（MyParse.ts） ───

class MyParse:
    def __init__(self, logic_flow, anchor_next_ids_map):
        self.logic_flow = logic_flow
        self.context = MyContext(anchor_next_ids_map)
        self.context.init(self.logic_flow)

    def parse(self):
        start_id = self.context.start_id
        node = ELNode(start_id)
        self._parse_then_chain(node)
        return self.context.pop()

    def _parse_then_chain(self, node, target_node=None, default_data=None, id_=""):
        env = ELNode()
        env.type = ELType.THEN
        env.alias_id = id_
        self.context.create_stack_env(env)
        if default_data:
            self.context.push(default_data)
        self._parse_single_node(node, target_node)
        return self.context.quit_stack_env()

    def _parse_single_node(self, node, target_node=None):
        id_ = node.id
        out_num = self.context.get_end_num(node)

        if self.context.is_end(id_):
            self.context.set_stack_end_point(node)
            return None
        if target_node and target_node.id == node.id:
            self.context.set_stack_end_point(node)
            return None

        if not self.context.is_start(id_):
            self.context.push(node)

        if ELType.IF == node.type:
            nxt = self._parse_if(self.context.pop())
            return self._parse_single_node(nxt, target_node)
        if ELType.SWITCH == node.type:
            nxt = self._parse_which(self.context.pop())
            return self._parse_single_node(nxt, target_node)
        if ELType.GROUP == node.type:
            nxt = self._parse_group(self.context.pop())
            if node.group_type == GroupType.LOGIC and out_num > 0:
                end_list = self.context.get_end_list(node)
                if end_list and not self.context.is_end(end_list[0].id):
                    logic_node = self.context.pop()
                    nxt = self._parse_if(logic_node)
            return self._parse_single_node(nxt, target_node)

        if out_num == 1:
            return self._parse_single_node(self.context.get_end_list(node)[0], target_node)

        nxt = self._parse_when_chain(node)
        return self._parse_single_node(nxt, target_node)

    def _parse_branch(self, node):
        follows = self.context.get_end_list(node)
        nxt = self._get_branch_end(node)
        for start in follows:
            if start.id == nxt.id:
                continue
            alias = start.coming_edge_text if node.type == ELType.SWITCH else ""
            self._parse_then_chain(start, nxt, None, alias)
        return nxt

    def _parse_if(self, node):
        type_node = ELNode()
        type_node.type = ELType.IF
        self.context.create_stack_env(type_node)
        if node.type == ELType.IF:
            node.type = ELType.ID
        self.context.push(node)
        ends = [n for n in self.context.get_end_list(node) if n is not None]
        out_num = len(ends)
        if out_num == 1:
            child = ends[0]
            ep = self.context.end_points.get(child.id, [None])[0]
            if ep is None or not self.context.is_end(ep.id):
                raise ValueError("IF 判断节点的分支数必须为2")
            self.context.push(child)
            return ep
        if out_num != 2:
            raise ValueError("IF 判断节点的分支数必须为2")
        end = self._parse_branch(node)
        self.context.set_stack_end_point(end)
        return self.context.quit_stack_env()

    def _parse_which(self, node):
        follows = self.context.get_end_list(node)
        if len(follows) <= 1:
            raise ValueError("WHICH 分支节点的分支数必须大于1")
        self.context.create_stack_env(node)
        nxt = self._parse_branch(node)
        self.context.set_stack_end_point(nxt)
        return self.context.quit_stack_env()

    def _parse_when_base(self, follows, end, datas):
        env = ELNode()
        env.type = ELType.WHEN
        self.context.create_stack_env(env)
        for i, s in enumerate(follows):
            if s.id == end.id:
                continue
            self._parse_then_chain(s, end, datas[i] if i < len(datas) else None)
        self.context.quit_stack_env()
        return self.context.pop()

    def _parse_when_chain(self, node):
        env = ELNode()
        env.type = ELType.WHEN
        self.context.create_stack_env(env)
        ends = self.context.get_end_list(node)
        nxt = self._get_branch_end(node)
        end_nodes = self._get_branch_end(node, nxt)

        end_map = {}
        end_data = {}

        sorted_entries = sorted(end_nodes.items(), key=lambda x: len(x[1]))

        for end_id, value in sorted_entries:
            end_node = self.context.get_node_by_id(end_id)
            if len(value) == 1:
                continue
            follows = []
            for idx in value:
                eid = ends[idx].id
                follows.append(end_map.get(eid, eid))
            for idx in value:
                end_map[ends[idx].id] = end_id

            fs = []
            seen = set()
            for fid in follows:
                if fid not in seen:
                    seen.add(fid)
                    fs.append(self.context.get_node_by_id(fid))

            data = self._parse_when_base(fs, end_node, [end_data.get(f.id) for f in fs])
            end_data[end_id] = data

        self.context.push(end_data.get(nxt.id))
        self.context.set_stack_end_point(nxt)
        return self.context.quit_stack_env()

    def _parse_group(self, node):
        ends = self.context.get_end_list(node)
        res = None
        to_end = True
        for end in ends:
            if end.coming_edge_text:
                self._parse_then_chain(end)
                then = self.context.el_stack.pop()
                text = end.coming_edge_text
                if text == "START":
                    node.start_node = then.child[0] if then.child else None
                elif text == "BREAK":
                    node.break_node = then.child[0] if then.child else None
                elif text == "EXCEPTION":
                    node.exception_node = then.child[0] if then.child else None
            else:
                res = end
                to_end = False
        self.context.el_stack.push(node)
        if to_end:
            return ELNode(self.context.end_id)
        return res

    def _get_branch_end(self, node, end_node=None):
        end_nodes = {}
        out_num = self.context.get_end_num(node)
        nodes_id = [n.id for n in self.context.get_end_list(node)]
        visited_count = {}

        while True:
            for i in range(len(nodes_id)):
                id_ = nodes_id[i]
                if not id_:
                    continue
                n = self.context.get_node_by_id(id_)
                visited_count[n.id] = visited_count.get(n.id, 0) + 1

                if n.id not in end_nodes:
                    end_nodes[n.id] = []
                end_nodes[n.id].append(i)

                if visited_count[n.id] == out_num:
                    if node.type == ELType.SWITCH:
                        if any(x.id == n.id for x in self.context.get_end_list(node)):
                            return self._get_branch_end(n)
                    if end_node:
                        return end_nodes
                    return n

                if self.context.is_end(n.id) or (end_node and n.id == end_node.id):
                    nodes_id[i] = ""
                elif self.context.get_end_num(n) > 1:
                    nodes_id[i] = self._get_branch_end(n).id
                else:
                    el = self.context.get_end_list(n)
                    nodes_id[i] = el[0].id if el else ""


# ─── 预处理：构建 anchorNextIdsMap ───

def build_anchor_next_ids_map(design):
    anchor_map = {}
    edges = design.get("edges", [])

    def find_next_ids(anchor_id):
        return [e["targetNodeId"] for e in edges if e.get("sourceAnchorId") == anchor_id]

    for node in design.get("nodes", []):
        ntype = node.get("type")
        if ntype == NodeTypes.SWITCH:
            for i, c in enumerate(switch_get_case_list(node)):
                aid = switch_get_anchor_id(node["id"], c["type"], i + 1)
                nids = find_next_ids(aid)
                if nids:
                    anchor_map[aid] = nids
        elif ntype == NodeTypes.CLASSIFIER:
            for i, c in enumerate(classifier_get_case_list(node)):
                aid = classifier_get_anchor_id(node["id"], c["type"], i + 1)
                nids = find_next_ids(aid)
                if nids:
                    anchor_map[aid] = nids
        elif ntype == NodeTypes.VAR_EXTRACT:
            for anchor in ("success", "fail"):
                aid = var_extract_get_anchor_id(node["id"], anchor)
                nids = find_next_ids(aid)
                if nids:
                    anchor_map[aid] = nids
    return anchor_map


# ─── 预处理：循环节点 ───

def preprocess_loop_nodes(design):
    """与前端 WorkflowView.vue getLiteFlowData() 对齐的循环预处理。

    前端逻辑分两步：
    1. 过滤掉 loop_start / loop_end / link_body 锚点的边
    2. 用 loopBody.properties.children 直接 partition 节点和边
    Python 版之前用 BFS 遍历边来收集内部节点，遗漏了普通节点类型。
    """
    nodes = design.get("nodes", [])
    edges = design.get("edges", [])

    # ── Step 1: 过滤锚点边，构建 loop→loopBody 映射（对应前端 edges.filter） ──
    loop_link_map = {}
    filtered_edges = []
    for edge in edges:
        target_anchor = edge.get("targetAnchorId", "")
        source_anchor = edge.get("sourceAnchorId", "")
        if target_anchor.endswith("_loop_end"):
            continue
        if source_anchor.endswith("_loop_start"):
            continue
        if source_anchor.endswith("_link_body"):
            loop_link_map[edge["sourceNodeId"]] = edge["targetNodeId"]
            continue
        filtered_edges.append(edge)
    edges = filtered_edges

    # ── Step 2: 按 children 分离节点和边（对应前端 do-while + partition） ──
    loop_nodes = [n for n in nodes if n.get("type") == NodeTypes.LOOP]
    handled = set()
    changed = True
    while changed:
        changed = False
        for loop_node in loop_nodes:
            loop_id = loop_node["id"]
            if loop_id in handled:
                continue
            handled.add(loop_id)

            loop_node.setdefault("properties", {})

            body_id = loop_link_map.get(loop_id)
            if not body_id:
                continue
            body_node = next((n for n in nodes if n["id"] == body_id), None)
            if not body_node:
                continue

            children_ids = (body_node.get("properties") or {}).get("children", []) or []
            if not isinstance(children_ids, list) or len(children_ids) == 0:
                children_ids = body_node.get("children", []) or []
            if not children_ids:
                continue

            children_set = set(children_ids)
            changed = True

            loop_nodes_internal = [n for n in nodes if n["id"] in children_set]
            nodes = [n for n in nodes if n["id"] not in children_set]

            # Exclude edges from loopBody → child (loopBody is a container, not a real flow node)
            loop_edges_internal = [e for e in edges if (e["sourceNodeId"] in children_set or e["targetNodeId"] in children_set) and e["sourceNodeId"] != body_id]
            edges = [e for e in edges if e["sourceNodeId"] not in children_set and e["targetNodeId"] not in children_set and e["sourceNodeId"] != body_id]

            loop_node["flowData"] = {"nodes": loop_nodes_internal, "edges": loop_edges_internal}

            ext_src = [e["sourceNodeId"] for e in edges if e["targetNodeId"] == loop_id]
            ext_tgt = [e["targetNodeId"] for e in edges if e["sourceNodeId"] == loop_id]
            loop_node["sourceNodeIds"] = ext_src
            loop_node["targetNodeIds"] = ext_tgt

            nodes = [n for n in nodes if n["id"] != body_id]

    design["nodes"] = nodes
    design["edges"] = edges


# ─── 公共接口 ───

def generate_chain(design: dict) -> str:
    """
    将 design JSON 转换为 LiteFlow EL 表达式字符串。

    参数:
        design: 包含 nodes 和 edges 的 dict

    返回:
        chain 字符串（LiteFlow EL 表达式）
    """
    design = copy.deepcopy(design)
    preprocess_loop_nodes(design)
    anchor_map = build_anchor_next_ids_map(design)
    return MyParse(design, anchor_map).parse().get_el_string()


# ─── CLI ───

def main():
    input_text = sys.stdin.read()
    try:
        design = json.loads(input_text)
        chain = generate_chain(design)
        print(json.dumps({"success": True, "chain": chain}, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"success": False, "message": str(e)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
