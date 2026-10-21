from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load_contract(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_if_missing(path: Path, text: str) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _material_state(workspace: Path) -> dict[str, str]:
    checks = {
        "template": "present" if (workspace / "main.tex").exists() else "missing",
        "main_tex": "present" if (workspace / "main.tex").exists() else "missing",
        "chapter_tex": "present" if (workspace / "chapters").exists() else "missing",
        "pdf_sources": "present" if (workspace / "pdf").exists() else "missing",
        "overleaf_sources": "present" if (workspace / "Overleaf_ref").exists() else "missing",
        "bib_and_style": "present" if (workspace / "references").exists() else "missing",
        "figures_tables": "present" if (workspace / "figures").exists() or (workspace / "tables").exists() else "unknown",
        "metadata": "unknown",
    }
    return checks


def _readiness_lines(material_state: dict[str, str]) -> list[str]:
    lines: list[str] = []
    for key, value in material_state.items():
        if value == "missing":
            lines.append(f"- [ ] 缺少 `{key}`：需要用户补齐或说明替代来源")
        elif value == "unknown":
            lines.append(f"- [ ] `{key}` 当前状态未确认：需要用户说明是否存在以及放在何处")
    if not lines:
        lines.append("- [x] 核心材料入口已基本就绪，可进入下一步问题清单与角色映射")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True)
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    skill_root = Path(__file__).resolve().parents[1]
    contract = _load_contract(skill_root / "assets" / "workspace_contract.json")

    for rel in contract.get("required_directories", []):
        (workspace / rel).mkdir(parents=True, exist_ok=True)
    (workspace / "codex_md" / "mermaid").mkdir(parents=True, exist_ok=True)

    material_state = _material_state(workspace)

    _write_if_missing(
        workspace / "codex_md" / "material_index.md",
        "# 材料索引\n\n| 类别 | 状态 | 位置 | 备注 |\n|---|---|---|---|\n"
        + "\n".join(
            f"| {key} | {value} | `{key}` | |" for key, value in material_state.items()
        )
        + "\n",
    )
    _write_if_missing(
        workspace / "codex_md" / "material_readiness.md",
        "# 材料就绪度检查\n\n"
        "## 当前判断\n"
        + "\n".join(_readiness_lines(material_state))
        + "\n\n## 用户需补充说明\n"
        "- [ ] 学校模板或当前权威仓库路径\n"
        "- [ ] 哪份 `main.tex` / 源稿是当前基线\n"
        "- [ ] 哪些 PDF / Overleaf 源稿是后续重构的权威来源\n",
    )
    _write_if_missing(
        workspace / "codex_md" / "missing_info.md",
        "# 待补信息清单\n\n- [ ] 待补实验细节\n- [ ] 待补图注与图源\n- [ ] 待补引用\n- [ ] 待补数字核验\n",
    )
    _write_if_missing(
        workspace / "codex_md" / "question_list.md",
        "# 本轮问题单\n\n## 本轮目标\n- \n\n## 问题列表\n| 优先级 | 涉及章节 | 问题 | 修改方向 | 验收标准 |\n|---|---|---|---|---|\n",
    )
    _write_if_missing(
        workspace / "codex_md" / "00_thesis_outline.md",
        "# 毕业论文主线大纲\n\n## 论文主线\n- \n\n## 章节角色\n- 第 1 章：\n- 第 2 章：\n- 第 3 章：\n\n## 当前未定问题\n- \n",
    )
    _write_if_missing(
        workspace / "claude_md" / "review_checklist.md",
        "# 终稿复查清单\n\n## 编译与模板\n- [ ] main.tex 可编译\n- [ ] 模板参数正确\n\n## 内容与证据\n- [ ] 关键数字已核对\n- [ ] 引用与论断匹配\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
