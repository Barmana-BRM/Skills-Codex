import importlib.util
import os
import pathlib
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
LIB_PATH = ROOT / "scripts" / "review_skill_lib.py"
GOLDEN_DIR = ROOT / "tests" / "golden"


def load_module():
    spec = importlib.util.spec_from_file_location("review_skill_lib", LIB_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ReviewSkillLibTests(unittest.TestCase):
    def sample_context(self):
        return {
            "repo": "/tmp/demo",
            "base": "main",
            "current_branch": "feature/review",
            "scope_mode": "working_tree",
            "status": {"staged": ["src/app.ts"], "unstaged": [], "untracked": []},
            "changed_files": ["src/app.ts", "Dockerfile"],
            "changed_line_ranges": {
                "src/app.ts": {"added": [{"start": 10, "end": 14}], "deleted": []}
            },
            "detected_stack": ["typescript", "node", "docker"],
            "suggested_references": [
                "review-framework.md",
                "output-contract.md",
                "false-positive-control.md",
                "typescript.md",
                "backend-and-integrations.md",
                "verification-and-operations.md",
            ],
            "risk_flags": ["api_or_network_boundary", "container_or_runtime"],
            "risk_level": "high",
            "review_mode_reason": "high-risk change touches sensitive production surfaces",
            "safe_check_commands": [{"command": "npm test", "reason": "Verify regressions."}],
            "review_plan": {
                "mode": "specialist",
                "reviewers": [
                    "correctness",
                    "architecture",
                    "reliability",
                    "security",
                    "tests",
                ],
                "follow_up": ["synthesizer"],
                "risk_level": "high",
                "review_mode_reason": "high-risk change touches sensitive production surfaces",
            },
        }

    def test_skill_documents_phase_gate_review_contract(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        usage_text = (ROOT.parent / "docs" / "usage" / "review-workflows.md").read_text(
            encoding="utf-8"
        )

        for expected in [
            "phase-gate",
            "严重问题",
            "中等问题",
            "非阻塞建议",
            "安全风险",
            "稳定性风险",
            "可维护性风险",
            "测试覆盖",
            "质量评分",
            "通过状态",
            "Manual-required",
        ]:
            self.assertIn(expected, skill_text)

        self.assertIn("Milestone Phase-Gate Review", usage_text)
        self.assertIn("block only on P0/P1 issues", usage_text)
        self.assertIn("send non-blocking suggestions to backlog", usage_text)

    def test_skill_documents_portable_python_interpreter_setup(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
        usage_text = (ROOT.parent / "docs" / "usage" / "review-workflows.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("active Python interpreter", skill_text)
        self.assertIn("Windows:", skill_text)
        self.assertIn("POSIX:", skill_text)
        self.assertIn("python production-code-quality-review/scripts/collect-review-context.py", skill_text)
        self.assertIn("python3 production-code-quality-review/scripts/collect-review-context.py", skill_text)

        self.assertIn("active Python interpreter", readme_text)
        self.assertIn("python production-code-quality-review/scripts/collect-review-context.py", readme_text)
        self.assertIn("python3 production-code-quality-review/scripts/collect-review-context.py", readme_text)
        self.assertIn("python production-code-quality-review/scripts/review-entrypoint.py", usage_text)
        self.assertIn("python3 production-code-quality-review/scripts/review-entrypoint.py", usage_text)

    def test_parse_unified_zero_diff_builds_changed_ranges(self):
        module = load_module()
        diff_text = """diff --git a/src/app.ts b/src/app.ts
index 1111111..2222222 100644
--- a/src/app.ts
+++ b/src/app.ts
@@ -10,0 +11,3 @@ export function run() {
+  const enabled = true;
+  const retries = 3;
+  return enabled && retries > 0;
@@ -20,2 +24,0 @@ export function oldThing() {
-  legacyOne();
-  legacyTwo();
"""

        result = module.parse_unified_zero_diff(diff_text)

        self.assertEqual(
            result["src/app.ts"]["added"],
            [{"start": 11, "end": 13}],
        )
        self.assertEqual(
            result["src/app.ts"]["deleted"],
            [{"start": 20, "end": 21}],
        )

    def test_parse_unified_zero_diff_ignores_pure_rename_without_hunks(self):
        module = load_module()
        diff_text = """diff --git a/src/old_name.ts b/src/new_name.ts
similarity index 100%
rename from src/old_name.ts
rename to src/new_name.ts
"""

        result = module.parse_unified_zero_diff(diff_text)

        self.assertEqual(result, {})

    def test_detect_stack_prefers_specific_references(self):
        module = load_module()
        paths = [
            "package.json",
            "tsconfig.json",
            "src/server.ts",
            "Dockerfile",
            "migrations/001_init.sql",
        ]

        result = module.detect_stack(paths)

        self.assertIn("typescript", result["detected_stack"])
        self.assertIn("node", result["detected_stack"])
        self.assertIn("docker", result["detected_stack"])
        self.assertIn("database", result["detected_stack"])
        self.assertIn("typescript.md", result["suggested_references"])
        self.assertIn("backend-and-integrations.md", result["suggested_references"])
        self.assertIn("review-framework.md", result["suggested_references"])
        self.assertIn("database.md", result["suggested_references"])

    def test_detect_stack_routes_python_to_python_reference(self):
        module = load_module()

        result = module.detect_stack(["pyproject.toml", "src/jobs/reconcile.py"])

        self.assertIn("python", result["detected_stack"])
        self.assertIn("python.md", result["suggested_references"])

    def test_detect_stack_ignores_migration_documentation(self):
        module = load_module()

        result = module.detect_stack(
            ["docs/superpowers/split-image-assets/migration.md"]
        )

        self.assertNotIn("database", result["detected_stack"])
        self.assertNotIn("database.md", result["suggested_references"])

    def test_select_repo_stack_markers_ignores_migration_documentation(self):
        module = load_module()

        markers = module.select_repo_stack_markers(
            [
                "docs/superpowers/split-image-assets/migration.md",
                "migrations/001_init.py",
                "database/schema.sql",
            ]
        )

        self.assertEqual(markers, ["migrations/001_init.py", "database/schema.sql"])

    def test_risk_flags_ignore_migration_documentation(self):
        module = load_module()

        flags = module.derive_risk_flags(
            ["docs/superpowers/split-image-assets/migration.md"], diff_text=""
        )

        self.assertNotIn("database_migration", flags)

    def test_risk_flags_cover_sensitive_surfaces(self):
        module = load_module()
        paths = [
            "src/auth/session.ts",
            "src/payments/stripe.ts",
            "migrations/002_add_accounts.sql",
            ".github/workflows/deploy.yml",
            "Dockerfile",
        ]

        flags = module.derive_risk_flags(paths, diff_text="")

        self.assertIn("auth_or_access_control", flags)
        self.assertIn("payments_or_billing", flags)
        self.assertIn("database_migration", flags)
        self.assertIn("ci_cd_or_deploy", flags)
        self.assertIn("container_or_runtime", flags)

    def test_build_safe_check_commands_matches_detected_stack(self):
        module = load_module()

        commands = module.build_safe_check_commands(
            detected_stack=["typescript", "node", "python", "go", "docker"]
        )

        command_lines = [item["command"] for item in commands]
        self.assertIn("npm test", command_lines)
        self.assertIn("npm run lint", command_lines)
        self.assertIn("npm run typecheck", command_lines)
        self.assertIn("npm run build", command_lines)
        self.assertIn("python3 -m unittest discover", command_lines)
        self.assertIn("go test ./...", command_lines)
        self.assertIn("docker compose config", command_lines)

    def test_build_safe_check_commands_uses_scoped_unittest_targets_for_multi_package_repo(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            (repo / "split-image-assets" / "tests").mkdir(parents=True)
            (repo / "split-image-assets" / "tests" / "test_skill_package.py").write_text(
                "import unittest\n\nclass Demo(unittest.TestCase):\n    pass\n"
            )
            (repo / "production-code-quality-review" / "tests").mkdir(parents=True)
            (
                repo
                / "production-code-quality-review"
                / "tests"
                / "test_review_skill_lib.py"
            ).write_text("import unittest\n\nclass Demo(unittest.TestCase):\n    pass\n")
            (repo / "split-image-assets" / "scripts").mkdir(parents=True)
            (repo / "split-image-assets" / "scripts" / "tool.py").write_text("def run():\n    return 1\n")

            commands = module.build_safe_check_commands(
                detected_stack=["python"],
                repo=repo,
                repo_files=[
                    "split-image-assets/scripts/tool.py",
                    "split-image-assets/tests/test_skill_package.py",
                    "production-code-quality-review/tests/test_review_skill_lib.py",
                ],
            )

        command_lines = [item["command"] for item in commands]
        self.assertIn("python3 -m unittest discover split-image-assets/tests -v", command_lines)
        self.assertIn(
            "python3 -m unittest discover production-code-quality-review/tests -v",
            command_lines,
        )
        self.assertNotIn("python3 -m unittest discover", command_lines)

    def test_expand_repo_paths_flattens_untracked_directories_to_files(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            nested_dir = repo / "tests" / "golden"
            nested_dir.mkdir(parents=True)
            (nested_dir / "review-brief.txt").write_text("golden output\n")
            (repo / "README.md").write_text("demo\n")

            expanded = module.expand_repo_paths(
                repo,
                [
                    "tests/golden",
                    "README.md",
                ],
            )

            self.assertEqual(
                expanded,
                [
                    "tests/golden/review-brief.txt",
                    "README.md",
                ],
            )

    def test_expand_repo_paths_keeps_git_submodule_directory_intact(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            submodule_dir = repo / "vendor" / "shared-lib"
            submodule_dir.mkdir(parents=True)
            (submodule_dir / ".git").write_text("gitdir: ../../.git/modules/shared-lib\n")
            (submodule_dir / "README.md").write_text("submodule readme\n")

            expanded = module.expand_repo_paths(
                repo,
                [
                    "vendor/shared-lib",
                ],
            )

            self.assertEqual(expanded, ["vendor/shared-lib"])

    def test_expand_repo_paths_preserves_binary_file_path(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            binary_file = repo / "assets" / "logo.png"
            binary_file.parent.mkdir(parents=True)
            binary_file.write_bytes(b"\x89PNG\r\n\x1a\n")

            expanded = module.expand_repo_paths(
                repo,
                [
                    "assets/logo.png",
                ],
            )

            self.assertEqual(expanded, ["assets/logo.png"])

    def test_expand_repo_paths_keeps_symlinked_directory_without_recursing(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            target = repo / "target"
            target.mkdir()
            (target / "nested.txt").write_text("nested\n")

            link = repo / "linked"
            try:
                link.symlink_to(target, target_is_directory=True)
            except OSError as exc:
                if os.name == "nt" and getattr(exc, "winerror", None) == 1314:
                    self.skipTest("Windows symlink creation requires elevated privileges")
                raise

            expanded = module.expand_repo_paths(repo, ["linked"])

            self.assertEqual(expanded, ["linked"])

    def test_risk_reference_augmentation_prefers_merged_reference_set(self):
        module = load_module()

        references = module.augment_references_for_risks(
            suggested_references=[
                "review-framework.md",
                "output-contract.md",
                "false-positive-control.md",
                "typescript.md",
            ],
            risk_flags=[
                "api_or_network_boundary",
                "auth_or_access_control",
                "container_or_runtime",
            ],
        )

        self.assertIn("backend-and-integrations.md", references)
        self.assertIn("verification-and-operations.md", references)
        self.assertIn("security.md", references)
        self.assertNotIn("api-integrations.md", references)
        self.assertNotIn("observability.md", references)
        self.assertNotIn("testing.md", references)

    def test_select_review_mode_uses_specialists_for_high_risk_changes(self):
        module = load_module()

        plan = module.select_review_mode(
            changed_files=[
                "src/auth/session.ts",
                "src/payments/stripe.ts",
                "migrations/002_add_accounts.sql",
            ],
            risk_flags=[
                "auth_or_access_control",
                "payments_or_billing",
                "database_migration",
            ],
        )

        self.assertEqual(plan["mode"], "specialist")
        self.assertIn("correctness", plan["reviewers"])
        self.assertIn("security", plan["reviewers"])
        self.assertIn("tests", plan["reviewers"])
        self.assertIn("synthesizer", plan["follow_up"])

    def test_select_review_mode_exposes_reason_and_risk_level(self):
        module = load_module()

        plan = module.select_review_mode(
            changed_files=["src/auth/session.ts", "migrations/002_add_accounts.sql"],
            risk_flags=["auth_or_access_control", "database_migration"],
        )

        self.assertEqual(plan["mode"], "specialist")
        self.assertEqual(plan["risk_level"], "high")
        self.assertIn("high-risk", plan["review_mode_reason"])

    def test_select_review_mode_marks_low_risk_changes(self):
        module = load_module()

        plan = module.select_review_mode(
            changed_files=["src/app.ts"],
            risk_flags=[],
        )

        self.assertEqual(plan["mode"], "single")
        self.assertEqual(plan["risk_level"], "low")
        self.assertIn("small", plan["review_mode_reason"])

    def test_build_review_brief_markdown_includes_scope_and_reviewers(self):
        module = load_module()
        context = self.sample_context()

        markdown = module.build_review_brief_markdown(context)

        self.assertIn("# Review Brief", markdown)
        self.assertIn("- Base: `main`", markdown)
        self.assertIn("- Changed files: `src/app.ts`, `Dockerfile`", markdown)
        self.assertIn("- Review mode: `specialist`", markdown)
        self.assertIn("- Risk level: `high`", markdown)
        self.assertIn("## Suggested References", markdown)
        self.assertIn("- `typescript.md`", markdown)
        self.assertIn("## Verification Commands", markdown)

    def test_build_review_brief_markdown_matches_golden_output(self):
        module = load_module()
        context = self.sample_context()

        markdown = module.build_review_brief_markdown(context)
        expected = (GOLDEN_DIR / "review-brief-markdown.md").read_text()

        self.assertEqual(markdown, expected)

    def test_build_review_brief_compact_matches_golden_output(self):
        module = load_module()
        context = self.sample_context()

        compact = module.build_review_brief_compact(context)
        expected = (GOLDEN_DIR / "review-brief-compact.txt").read_text()

        self.assertEqual(compact, expected)


if __name__ == "__main__":
    unittest.main()
