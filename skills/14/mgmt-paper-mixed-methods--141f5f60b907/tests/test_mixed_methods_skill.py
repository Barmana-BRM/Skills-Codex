from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_skill_frontmatter():
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---\n")
    assert "name: mgmt-paper-mixed-methods" in text
    assert "joint display" in text


def test_reference_mentions_core_designs():
    text = (ROOT / "references/mixed-methods-workflow.md").read_text(encoding="utf-8")
    for token in ["Exploratory sequential", "Explanatory sequential", "Convergent parallel", "Reviewer Risks"]:
        assert token in text


def test_templates_exist():
    assert (ROOT / "templates/joint_display.csv").is_file()
    assert (ROOT / "templates/idea_to_story_to_paper.md").is_file()

