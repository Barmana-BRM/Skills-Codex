from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_skill_frontmatter():
    fm = read("SKILL.md").split("---", 2)[1]
    assert re.search(r"^name:\s*mgmt-paper-reviewer-simulation\s*$", fm, re.M)
    assert 'display_name: "MGMT - Paper - Reviewer Simulation"' in fm


def test_reviewer_assets():
    for rel in [
        "references/reviewer-roles.md",
        "references/journal-review-profiles.md",
        "templates/reviewer_report.md",
        "templates/revision_backlog.csv",
    ]:
        assert (ROOT / rel).is_file()
        assert len(read(rel)) > 120


def test_mentions_top_journal_roles():
    text = read("SKILL.md")
    for kw in ["Handling Editor", "Theory Reviewer", "Methods Reviewer", "Skeptical Reviewer", "AMJ", "ASQ", "Management Science"]:
        assert kw in text
