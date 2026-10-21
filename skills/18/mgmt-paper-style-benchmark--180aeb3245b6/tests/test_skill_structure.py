from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_skill_frontmatter():
    fm = read("SKILL.md").split("---", 2)[1]
    assert re.search(r"^name:\s*mgmt-paper-style-benchmark\s*$", fm, re.M)
    assert 'display_name: "MGMT - Paper - Style Benchmark"' in fm


def test_assets_exist():
    for rel in [
        "references/style-dimensions.md",
        "references/formatting-gates.md",
        "templates/style_benchmark_matrix.md",
        "templates/paragraph_revision_grid.md",
    ]:
        assert (ROOT / rel).is_file()
        assert len(read(rel)) > 120


def test_copyright_boundary_present():
    text = read("SKILL.md")
    assert "不得复制" in text
    assert "原创表达" in text
    assert "author guidelines" in text
