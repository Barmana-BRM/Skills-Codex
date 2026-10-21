#!/usr/bin/env python3
"""List Verilog/SystemVerilog modules, the instance tree of a top module, and module ports.

Purpose : speeds up analysis stage 1 (RHD-030..033) and the port part of stage 3: module definitions,
          instantiations (instance, module, file:line, parameterized or not), hierarchy tree to a depth,
          and the declared ports of one module. The RTL is only read (RHD-002).
Usage   : python rtl_hier.py RTL_DIR [--top MODULE] [--depth N] [--ports MODULE] [--md]
Input   : *.v, *.sv, *.vh, *.svh files below RTL_DIR.
Output  : text, or Markdown tables with --md, on stdout.
Exit    : 0 success, 2 usage error or module not found.
Limits  : text-level parser. Compiler directives are not evaluated (inactive `ifdef branches are listed too)
          and generate blocks are not unrolled; confirm the result in the RTL.
Only the Python standard library is used.
"""
import argparse
import os
import re
import sys

KEYWORDS = set("""module endmodule input output inout wire reg logic integer parameter localparam assign always
always_ff always_comb always_latch initial begin end if else case endcase for generate endgenerate function
endfunction task endtask genvar posedge negedge or and not nand nor xor xnor buf default while repeat forever
supply0 supply1 tri""".split())
PARAM = r"(#\s*\((?:[^()]|\((?:[^()]|\([^()]*\))*\))*\)\s*)"
INSTANCE = re.compile(r"(?:^|[;\n\)])\s*(\w+)(?:\s+|\s*" + PARAM + r")(\w+)\s*(?:\[[^\]]*\]\s*)?\(")


def strip_comments(text):
    text = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    text = re.sub(r"//[^\n]*", "", text)
    text = re.sub(r"^[ \t]*`(?:include|timescale|define|undef|ifdef|ifndef|else|elsif|endif)[^\n]*$", "", text, flags=re.M)
    return text


def scan(root):
    modules, instances, order = {}, {}, []
    for folder, _, names in os.walk(root):
        for name in sorted(names):
            if not name.lower().endswith((".v", ".sv", ".vh", ".svh")):
                continue
            path = os.path.join(folder, name)
            rel = os.path.relpath(path, root).replace("\\", "/")
            with open(path, encoding="utf-8", errors="replace") as handle:
                text = strip_comments(handle.read())
            starts = [(m.group(1), m.start()) for m in re.finditer(r"\bmodule\s+(\w+)", text)]
            ends = [m.end() for m in re.finditer(r"\bendmodule\b", text)]
            for index, (mod, start) in enumerate(starts):
                end = ends[index] if index < len(ends) else len(text)
                line = text.count("\n", 0, start) + 1
                modules[mod] = {"file": rel, "line": line, "path": path}
                order.append(mod)
                body = text[start:end]
                header_end = body.find(";")
                header_lines = body.count("\n", 0, header_end + 1) if header_end >= 0 else 0
                body = body[header_end + 1:] if header_end >= 0 else body
                for m in INSTANCE.finditer(body):
                    kind, inst = m.group(1), m.group(3)
                    if kind in KEYWORDS or inst in KEYWORDS or kind == mod:
                        continue
                    ln = line + header_lines + body.count("\n", 0, m.start(1))
                    instances.setdefault(mod, []).append(
                        {"inst": inst, "module": kind, "file": rel, "line": ln, "param": m.group(2) is not None})
    return modules, instances, order


def ports_of(modules, name):
    info = modules.get(name)
    if not info:
        return None
    with open(info["path"], encoding="utf-8", errors="replace") as handle:
        text = re.sub(r"//[^\n]*", "", re.sub(r"/\*.*?\*/", "", handle.read(), flags=re.S))
    m = re.search(r"\bmodule\s+" + re.escape(name) + r"\b(.*?)\bendmodule\b", text, flags=re.S)
    if not m:
        return None
    found, seen = [], set()
    pattern = r"\b(input|output|inout)\b\s*(?:(?:wire|reg|logic|signed|var)\s+)*(\[[^\]]*\])?\s*([\w\s,\[\]]+?)\s*(?:[;,)]|$)"
    for d in re.finditer(pattern, m.group(1)):
        for raw in d.group(3).split(","):
            port = re.sub(r"\[.*", "", re.sub(r"\s+", "", raw))
            if re.fullmatch(r"\w+", port) and port not in KEYWORDS and port not in seen:
                seen.add(port)
                found.append((port, d.group(1), d.group(2) or ""))
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("rtl_dir")
    parser.add_argument("--top")
    parser.add_argument("--depth", type=int)
    parser.add_argument("--ports")
    parser.add_argument("--md", action="store_true")
    args = parser.parse_args()
    if not os.path.isdir(args.rtl_dir):
        print("error: RTL_DIR is not a directory", file=sys.stderr)
        return 2
    modules, instances, order = scan(args.rtl_dir)
    if args.ports:
        found = ports_of(modules, args.ports)
        if not found:
            print(f"error: module '{args.ports}' not found or has no declared ports", file=sys.stderr)
            return 2
        if args.md:
            print("| Port | Direction | Width |\n|---|---|---|")
            for port, direction, width in found:
                print(f"| {port} | {direction} | {width or '1'} |")
        else:
            for port, direction, width in found:
                print(f"{port:32s} {direction:7s} {width or '1'}")
        return 0
    used = {i["module"] for lst in instances.values() for i in lst}
    tops = [m for m in order if m not in used]

    def reach(mod, seen):
        if mod in seen:
            return 0
        seen.add(mod)
        return 1 + sum(reach(i["module"], seen) for i in instances.get(mod, []) if i["module"] in modules)

    top = args.top
    if top is None:
        print(f"Modules defined: {len(order)}; candidate tops (not instantiated anywhere): {' '.join(tops)}")
        if not tops:
            print("error: no top module found", file=sys.stderr)
            return 2
        top = sorted(tops, key=lambda m: -reach(m, set()))[0]
        print(f"Selected top: {top} (largest hierarchy); use --top to override")
    if top not in modules:
        print(f"error: top module '{top}' not found", file=sys.stderr)
        return 2
    if args.md:
        print("| Depth | Instance | Module | File:line | Parent | Parameterized |\n|---|---|---|---|---|---|")
        print(f"| 0 | TOP | {top} | {modules[top]['file']}:{modules[top]['line']} | - | - |")
    else:
        print(f"TOP ({top})  {modules[top]['file']}:{modules[top]['line']}")

    def walk(mod, depth, path, parent):
        if args.depth is not None and depth > args.depth:
            return
        for i in instances.get(mod, []):
            known = i["module"] in modules
            note = "" if known else " (not defined in RTL_DIR)"
            if args.md:
                print(f"| {depth} | {i['inst']} | {i['module']}{note} | {i['file']}:{i['line']} | {parent} | {'yes' if i['param'] else 'no'} |")
            else:
                print("  " * depth + f"{i['inst']} ({i['module']}){note}  {i['file']}:{i['line']}" + ("  #params" if i["param"] else ""))
            if known and i["module"] not in path:
                walk(i["module"], depth + 1, path | {mod}, i["inst"])

    walk(top, 1, set(), "TOP")
    if not args.md:
        missing = sorted({i["module"] for lst in instances.values() for i in lst if i["module"] not in modules})
        if missing:
            print("\nModules instantiated but not defined in RTL_DIR: " + " ".join(missing))
        unref = [m for m in order if m not in used and m != top]
        if unref:
            print("Defined but never instantiated: " + " ".join(unref))
    return 0


if __name__ == "__main__":
    sys.exit(main())
