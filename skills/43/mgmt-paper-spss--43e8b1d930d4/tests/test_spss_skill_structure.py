from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_skill_frontmatter():
    text = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
    assert text.startswith('---\n')
    assert 'name: mgmt-paper-spss' in text
    assert 'description:' in text


def test_templates_exist_and_contain_spss_commands():
    templates = list((ROOT / 'templates/spss').glob('*.sps'))
    assert len(templates) >= 4
    joined = '\n'.join(p.read_text(encoding='utf-8') for p in templates)
    for token in ['RELIABILITY', 'FACTOR', 'REGRESSION', 'LOGISTIC REGRESSION']:
        assert token in joined


def test_references_are_substantial():
    text = (ROOT / 'references/spss-workflow.md').read_text(encoding='utf-8')
    assert 'Cronbach' in text
    assert 'Reviewer Risks' in text


def test_spss_cli_checker_exists():
    script = ROOT / 'scripts/check_spss_cli.py'
    assert script.is_file()
    assert 'SPSS executable not found' in script.read_text(encoding='utf-8')
