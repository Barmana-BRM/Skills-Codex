from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_skill_frontmatter():
    text = read("SKILL.md")
    assert text.startswith("---\n")
    fm = text.split("---", 2)[1]
    assert re.search(r"^name:\s*mgmt-paper-manuscript-package\s*$", fm, re.M)
    assert 'display_name: "MGMT - Paper - Manuscript Package"' in fm
    assert "description:" in fm


def test_required_files_exist_and_are_substantive():
    required = [
        "README.md",
        "NOTICE",
        "LICENSE",
        "references/structure-defense.md",
        "references/chapter-writing.md",
        "references/integrated-revision.md",
        "templates/material_inventory.md",
        "templates/evidence_matrix.csv",
        "templates/presubmission_package_checklist.md",
    ]
    for rel in required:
        path = ROOT / rel
        assert path.is_file(), rel
        assert len(read(rel)) >= 120, rel


def test_license_mentions_apache_2():
    text = read("LICENSE")
    assert "Apache License" in text
    assert "Version 2.0" in text


def test_workflow_mentions_package_and_revision():
    text = read("SKILL.md")
    for kw in ["材料盘点", "结构答辩", "章节撰写", "整合修订", "预审 package"]:
        assert kw in text
