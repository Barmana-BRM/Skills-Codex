import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE_SKILL_README = ROOT / "README.md"
SCRIPT = ROOT / "scripts" / "collect-review-context.py"
REVIEW_ENTRYPOINT = ROOT / "scripts" / "review-entrypoint.py"
INSTALL_SCRIPT = ROOT / "scripts" / "install-local-skill.sh"
UPDATE_SCRIPT = ROOT / "scripts" / "update-local-skill.sh"
VERIFY_RELEASE_SCRIPT = ROOT / "scripts" / "verify-release.sh"
REVIEW_CONTEXT_SCHEMA = ROOT / "references" / "review-context.schema.json"
FINDING_SCHEMA = ROOT / "references" / "finding.schema.json"


class CollectReviewContextCliTests(unittest.TestCase):
    def test_collect_review_context_reports_changed_files_and_ranges(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "package.json").write_text('{"name":"demo","scripts":{"test":"echo ok"}}\n')
            (repo / "tsconfig.json").write_text('{"compilerOptions":{"strict":true}}\n')
            (repo / "src").mkdir()
            (repo / "src" / "app.ts").write_text("export const ready = false;\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "src" / "app.ts").write_text(
                "export const ready = true;\nexport const retries = 3;\n"
            )
            (repo / "Dockerfile").write_text("FROM node:20-alpine\n")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo", str(repo)],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)

            self.assertIn("src/app.ts", payload["changed_files"])
            self.assertIn("Dockerfile", payload["changed_files"])
            self.assertIn("typescript", payload["detected_stack"])
            self.assertIn("docker", payload["detected_stack"])
            self.assertIn("src/app.ts", payload["changed_line_ranges"])
            self.assertIn("risk_level", payload)
            self.assertIn("review_mode_reason", payload)
            self.assertIn("verification-and-operations.md", payload["suggested_references"])
            self.assertIn("npm test", [item["command"] for item in payload["safe_check_commands"]])

    def test_fixture_typescript_api_change_routes_to_backend_and_security_guidance(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "package.json").write_text('{"name":"demo","scripts":{"test":"echo ok","lint":"echo ok","typecheck":"echo ok","build":"echo ok"}}\n')
            (repo / "tsconfig.json").write_text('{"compilerOptions":{"strict":true}}\n')
            (repo / "src").mkdir()
            (repo / "src" / "api-client.ts").write_text("export const timeoutMs = 1000;\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "src" / "api-client.ts").write_text(
                "export const timeoutMs = 2000;\nexport const endpoint = '/admin/users';\n"
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo", str(repo)],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)

            self.assertIn("typescript", payload["detected_stack"])
            self.assertIn("node", payload["detected_stack"])
            self.assertIn("api_or_network_boundary", payload["risk_flags"])
            self.assertEqual(payload["risk_level"], "high")
            self.assertIn("high-risk", payload["review_mode_reason"])
            self.assertIn("backend-and-integrations.md", payload["suggested_references"])
            self.assertIn("verification-and-operations.md", payload["suggested_references"])
            self.assertIn("npm run typecheck", [item["command"] for item in payload["safe_check_commands"]])

    def test_fixture_database_migration_routes_to_database_reference(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "migrations").mkdir()
            (repo / "migrations" / "001_init.sql").write_text("create table users (id integer primary key);\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "migrations" / "002_add_email.sql").write_text(
                "alter table users add column email text not null default '';\n"
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo", str(repo)],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)

            self.assertIn("database", payload["detected_stack"])
            self.assertIn("database_migration", payload["risk_flags"])
            self.assertEqual(payload["risk_level"], "high")
            self.assertIn("database.md", payload["suggested_references"])

    def test_fixture_docker_change_routes_to_verification_and_operations(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "Dockerfile").write_text("FROM node:20-alpine\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "Dockerfile").write_text("FROM node:22-alpine\nRUN adduser -D app\n")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo", str(repo)],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)

            self.assertIn("docker", payload["detected_stack"])
            self.assertIn("container_or_runtime", payload["risk_flags"])
            self.assertEqual(payload["risk_level"], "high")
            self.assertIn("verification-and-operations.md", payload["suggested_references"])
            self.assertIn("docker compose config", [item["command"] for item in payload["safe_check_commands"]])

    def test_review_entrypoint_allows_base_and_scope_overrides(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "package.json").write_text('{"name":"demo"}\n')
            (repo / "src").mkdir()
            (repo / "src" / "app.ts").write_text("export const value = 1;\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "src" / "app.ts").write_text("export const value = 2;\n")

            result = subprocess.run(
                [
                    sys.executable,
                    str(REVIEW_ENTRYPOINT),
                    "--repo",
                    str(repo),
                    "--base",
                    "HEAD",
                    "--scope",
                    "working_tree",
                    "--format",
                    "compact",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("review-mode=", result.stdout)
            self.assertIn("risk-flags=", result.stdout)

    def test_review_entrypoint_json_exposes_schema_version(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "README.md").write_text("initial\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            (repo / "README.md").write_text("updated\n")

            result = subprocess.run(
                [sys.executable, str(REVIEW_ENTRYPOINT), "--repo", str(repo), "--format", "json"],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)

            self.assertEqual(payload["schema_version"], "review-context/v1")
            self.assertIn("review_plan", payload)

    def test_branch_scope_excludes_uncommitted_worktree_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "src").mkdir()
            (repo / "src" / "committed.ts").write_text("export const value = 1;\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "src" / "committed.ts").write_text("export const value = 2;\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "feature change"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            (repo / "src" / "local-only.ts").write_text("export const localOnly = true;\n")

            branch_result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--repo",
                    str(repo),
                    "--base",
                    "HEAD~1",
                    "--scope",
                    "branch",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            working_tree_result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--repo",
                    str(repo),
                    "--base",
                    "HEAD~1",
                    "--scope",
                    "working_tree",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            branch_payload = json.loads(branch_result.stdout)
            working_tree_payload = json.loads(working_tree_result.stdout)

            self.assertEqual(branch_payload["scope_mode"], "branch")
            self.assertIn("src/committed.ts", branch_payload["changed_files"])
            self.assertNotIn("src/local-only.ts", branch_payload["changed_files"])
            self.assertIn("src/local-only.ts", working_tree_payload["changed_files"])

    def test_working_tree_scope_keeps_branch_and_untracked_line_ranges(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "src").mkdir()
            (repo / "src" / "committed.ts").write_text("export const value = 1;\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "src" / "committed.ts").write_text(
                "export const value = 2;\nexport const committedOnly = true;\n"
            )
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "feature change"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            (repo / "src" / "local-only.ts").write_text(
                "export const localOnly = true;\nexport const more = 1;\n"
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--repo",
                    str(repo),
                    "--base",
                    "HEAD~1",
                    "--scope",
                    "working_tree",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)

            self.assertIn("src/committed.ts", payload["changed_files"])
            self.assertIn("src/local-only.ts", payload["changed_files"])
            self.assertIn("src/committed.ts", payload["changed_line_ranges"])
            self.assertIn("src/local-only.ts", payload["changed_line_ranges"])
            self.assertEqual(
                payload["changed_line_ranges"]["src/local-only.ts"]["added"],
                [{"start": 1, "end": 2}],
            )

    def test_infers_develop_base_when_main_is_absent(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "README.md").write_text("base\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(["git", "branch", "-M", "develop"], cwd=repo, check=True)
            subprocess.run(
                ["git", "checkout", "-b", "feature"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            (repo / "README.md").write_text("feature\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "feature"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo", str(repo), "--scope", "branch"],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)

            self.assertEqual(payload["base"], "develop")

    def test_safe_check_commands_follow_package_and_python_tooling(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "package.json").write_text(
                '{"scripts":{"test":"vitest","lint":"eslint .","typecheck":"tsc","build":"vite build"}}\n'
            )
            (repo / "pnpm-lock.yaml").write_text("lockfileVersion: '9.0'\n")
            (repo / "pyproject.toml").write_text(
                "[tool.pytest.ini_options]\naddopts = '-q'\n\n[tool.ruff]\n\n[tool.mypy]\n"
            )
            (repo / "src").mkdir()
            (repo / "src" / "app.ts").write_text("export const value = 1;\n")
            (repo / "src" / "job.py").write_text("def run():\n    return 1\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "src" / "app.ts").write_text("export const value = 2;\n")
            (repo / "src" / "job.py").write_text("def run():\n    return 2\n")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo", str(repo), "--base", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            commands = [item["command"] for item in payload["safe_check_commands"]]

            self.assertIn("pnpm test", commands)
            self.assertIn("pnpm lint", commands)
            self.assertIn("pnpm typecheck", commands)
            self.assertIn("pnpm build", commands)
            self.assertIn("python3 -m pytest", commands)
            self.assertIn("python3 -m ruff check .", commands)
            self.assertIn("python3 -m mypy .", commands)

    def test_collect_review_context_uses_scoped_unittest_targets_for_multi_package_repo(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "alpha-skill" / "scripts").mkdir(parents=True)
            (repo / "alpha-skill" / "scripts" / "tool.py").write_text("def run():\n    return 1\n")
            (repo / "alpha-skill" / "tests").mkdir(parents=True)
            (repo / "alpha-skill" / "tests" / "test_alpha.py").write_text(
                "import unittest\n\nclass Alpha(unittest.TestCase):\n    pass\n"
            )
            (repo / "beta-skill" / "tests").mkdir(parents=True)
            (repo / "beta-skill" / "tests" / "test_beta.py").write_text(
                "import unittest\n\nclass Beta(unittest.TestCase):\n    pass\n"
            )
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "alpha-skill" / "scripts" / "tool.py").write_text("def run():\n    return 2\n")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo", str(repo), "--base", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            commands = [item["command"] for item in payload["safe_check_commands"]]

            self.assertIn("python3 -m unittest discover alpha-skill/tests -v", commands)
            self.assertIn("python3 -m unittest discover beta-skill/tests -v", commands)
            self.assertNotIn("python3 -m unittest discover", commands)

    def test_bun_test_script_uses_package_script(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "package.json").write_text('{"scripts":{"test":"vitest"}}\n')
            (repo / "bun.lockb").write_text("")
            (repo / "src.js").write_text("console.log(1);\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            (repo / "src.js").write_text("console.log(2);\n")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo", str(repo), "--base", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            commands = [item["command"] for item in payload["safe_check_commands"]]

            self.assertIn("bun run test", commands)
            self.assertNotIn("bun test", commands)

    def test_known_empty_package_scripts_do_not_emit_missing_js_commands(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "package.json").write_text('{"scripts":{}}\n')
            (repo / "src.js").write_text("console.log(1);\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            (repo / "src.js").write_text("console.log(2);\n")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo", str(repo), "--base", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)

            self.assertEqual(payload["safe_check_commands"], [])

    def test_missing_package_metadata_keeps_js_command_fallbacks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "src.js").write_text("console.log(1);\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            (repo / "src.js").write_text("console.log(2);\n")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo", str(repo), "--base", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            commands = [item["command"] for item in payload["safe_check_commands"]]

            self.assertIn("npm test", commands)

    def test_review_entrypoint_markdown_outputs_actionable_brief(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "package.json").write_text('{"name":"demo","scripts":{"test":"echo ok"}}\n')
            (repo / "src").mkdir()
            (repo / "src" / "auth.ts").write_text("export const allow = false;\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "src" / "auth.ts").write_text("export const allow = true;\n")

            result = subprocess.run(
                [sys.executable, str(REVIEW_ENTRYPOINT), "--repo", str(repo), "--format", "markdown"],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("# Review Brief", result.stdout)
            self.assertIn("Suggested References", result.stdout)
            self.assertIn("Review mode", result.stdout)
            self.assertIn("Verification Commands", result.stdout)

    def test_review_entrypoint_compact_outputs_single_line_summary(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "package.json").write_text('{"name":"demo"}\n')
            (repo / "src").mkdir()
            (repo / "src" / "app.ts").write_text("export const value = 1;\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "src" / "app.ts").write_text("export const value = 2;\n")

            result = subprocess.run(
                [sys.executable, str(REVIEW_ENTRYPOINT), "--repo", str(repo), "--format", "compact"],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("review-mode=", result.stdout)
            self.assertIn("changed-files=", result.stdout)
            self.assertNotIn("\n\n", result.stdout)

    def test_install_and_update_scripts_are_present(self):
        self.assertTrue(INSTALL_SCRIPT.exists())
        self.assertTrue(UPDATE_SCRIPT.exists())
        self.assertTrue(VERIFY_RELEASE_SCRIPT.exists())

    def test_core_skill_asset_files_are_present(self):
        required_files = [
            CORE_SKILL_README,
            ROOT / "SKILL.md",
            ROOT / "agents" / "openai.yaml",
            ROOT / "references" / "review-framework.md",
            ROOT / "references" / "output-contract.md",
            ROOT / "references" / "false-positive-control.md",
            REVIEW_CONTEXT_SCHEMA,
            FINDING_SCHEMA,
            SCRIPT,
            REVIEW_ENTRYPOINT,
            ROOT / "scripts" / "review_skill_lib.py",
            INSTALL_SCRIPT,
            UPDATE_SCRIPT,
            VERIFY_RELEASE_SCRIPT,
            ROOT / "tests" / "test_collect_review_context_cli.py",
            ROOT / "tests" / "test_review_skill_lib.py",
        ]

        missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
        self.assertEqual(missing, [])

    def test_machine_readable_schema_files_are_present_and_valid_json(self):
        review_context_schema = json.loads(REVIEW_CONTEXT_SCHEMA.read_text())
        finding_schema = json.loads(FINDING_SCHEMA.read_text())

        self.assertEqual(review_context_schema["properties"]["schema_version"]["const"], "review-context/v1")
        self.assertIn("change_classification", finding_schema["required"])

    def test_generated_review_context_satisfies_schema_contract(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            (repo / "README.md").write_text("initial\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            (repo / "README.md").write_text("updated\n")

            result = subprocess.run(
                [sys.executable, str(REVIEW_ENTRYPOINT), "--repo", str(repo), "--format", "json"],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            schema = json.loads(REVIEW_CONTEXT_SCHEMA.read_text())

            self.assert_payload_satisfies_schema_contract(payload, schema)

    def assert_payload_satisfies_schema_contract(self, payload, schema):
        for key in schema["required"]:
            self.assertIn(key, payload)

        for key, definition in schema["properties"].items():
            if key not in payload:
                continue
            if "const" in definition:
                self.assertEqual(payload[key], definition["const"])
            if "enum" in definition:
                self.assertIn(payload[key], definition["enum"])

        for command in payload["safe_check_commands"]:
            self.assertIn("command", command)
            self.assertIn("reason", command)

        plan_schema = schema["properties"]["review_plan"]
        for key in plan_schema["required"]:
            self.assertIn(key, payload["review_plan"])
        self.assertIn(payload["review_plan"]["mode"], plan_schema["properties"]["mode"]["enum"])

    def test_install_helpers_guard_destructive_target_cleanup(self):
        for script in [INSTALL_SCRIPT, UPDATE_SCRIPT]:
            with self.subTest(script=script.name):
                text = script.read_text()
                guard_index = text.index("guard_skill_target()")
                copy_index = text.index("copy_skill_tree()")
                rm_index = text.index('rm -rf "$target_dir"')

                self.assertLess(guard_index, copy_index)
                self.assertIn('guard_skill_target "$source_dir" "$target_dir"', text)
                self.assertLess(
                    text.index('guard_skill_target "$source_dir" "$target_dir"'),
                    rm_index,
                )
                self.assertIn('while [[ ! -d "$existing"', text)
                self.assertIn('basename "$resolved_target"', text)
                self.assertIn('"production-code-quality-review"', text)
                self.assertIn('[[ "$resolved_target" == "/" ]]', text)
                self.assertIn('[[ "$resolved_target" == "$resolved_source" ]]', text)
                self.assertIn('[[ "$resolved_target" == "$resolved_source"/* ]]', text)
                self.assertIn('[[ "$resolved_source" == "$resolved_target"/* ]]', text)
                self.assertIn('Refusing to remove unsafe skill target', text)

    @unittest.skipIf(os.name == "nt", "POSIX install helper test requires Unix path semantics")
    def test_install_script_omits_python_cache_artifacts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = pathlib.Path(temp_dir)
            agents_home = root / ".agents"
            source_root = root / "source"
            target = agents_home / "skills" / "production-code-quality-review"
            shutil.copytree(ROOT, source_root)

            pycache = source_root / "scripts" / "__pycache__"
            pycache.mkdir(exist_ok=True)
            (pycache / "review_skill_lib.cpython-313.pyc").write_bytes(b"cache")
            tests_pycache = source_root / "tests" / "__pycache__"
            tests_pycache.mkdir(exist_ok=True)
            (tests_pycache / "test_review_skill_lib.cpython-313.pyc").write_bytes(b"cache")

            subprocess.run(
                ["bash", str(source_root / "scripts" / "install-local-skill.sh")],
                cwd=source_root,
                env={**os.environ, "AGENTS_HOME": str(agents_home)},
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertFalse((target / "scripts" / "__pycache__").exists())
            self.assertFalse((target / "tests" / "__pycache__").exists())
            self.assertEqual((target / ".skill-source-dir").read_text().strip(), str(source_root))

            review_repo = root / "review-repo"
            review_repo.mkdir()
            subprocess.run(["git", "init"], cwd=review_repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=review_repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=review_repo,
                check=True,
                capture_output=True,
                text=True,
            )
            (review_repo / "README.md").write_text("initial\n")
            subprocess.run(["git", "add", "."], cwd=review_repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=review_repo,
                check=True,
                capture_output=True,
                text=True,
            )
            (review_repo / "README.md").write_text("updated\n")

            subprocess.run(
                [
                    sys.executable,
                    str(target / "scripts" / "review-entrypoint.py"),
                    "--repo",
                    str(review_repo),
                    "--base",
                    "HEAD",
                    "--scope",
                    "working_tree",
                    "--format",
                    "compact",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertFalse((target / "scripts" / "__pycache__").exists())

    @unittest.skipIf(os.name == "nt", "POSIX update helper test requires Unix path semantics")
    def test_update_script_refreshes_installed_copy_from_recorded_source(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = pathlib.Path(temp_dir)
            agents_home = root / ".agents"
            source_root = root / "source"
            target = agents_home / "skills" / "production-code-quality-review"
            target.parent.mkdir(parents=True)
            shutil.copytree(ROOT, source_root)

            subprocess.run(
                ["bash", str(source_root / "scripts" / "install-local-skill.sh")],
                cwd=source_root,
                env={**os.environ, "AGENTS_HOME": str(agents_home)},
                check=True,
                capture_output=True,
                text=True,
            )

            original_skill = (target / "SKILL.md").read_text()
            updated_skill = original_skill + "\n<!-- updated from source checkout -->\n"
            (source_root / "SKILL.md").write_text(updated_skill)

            result = subprocess.run(
                ["bash", str(target / "scripts" / "update-local-skill.sh")],
                cwd=root,
                env={**os.environ, "AGENTS_HOME": str(agents_home)},
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((target / "SKILL.md").read_text(), updated_skill)
            self.assertEqual(
                (target / ".skill-source-dir").read_text().strip(),
                str(source_root),
            )
            self.assertFalse((target / "scripts" / "__pycache__").exists())

    def test_verify_release_script_includes_safe_check_and_summary_steps(self):
        script_text = VERIFY_RELEASE_SCRIPT.read_text()

        self.assertIn("PYTHONDONTWRITEBYTECODE=1", script_text)
        self.assertIn("run-safe-checks.py", script_text)
        self.assertIn("--format compact", script_text)

    def test_collect_review_context_flattens_untracked_directories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            nested_dir = repo / "docs" / "golden"
            nested_dir.mkdir(parents=True)
            (nested_dir / "brief.md").write_text("golden\n")
            (repo / "README.md").write_text("demo\n")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo", str(repo)],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)

            self.assertIn("docs/golden/brief.md", payload["changed_files"])
            self.assertNotIn("docs/golden", payload["changed_files"])

    def test_collect_review_context_keeps_submodule_directory_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            submodule_dir = repo / "vendor" / "shared-lib"
            submodule_dir.mkdir(parents=True)
            (submodule_dir / ".git").write_text("gitdir: ../../.git/modules/shared-lib\n")
            (submodule_dir / "README.md").write_text("nested file\n")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo", str(repo)],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)

            self.assertIn("vendor/shared-lib", payload["changed_files"])
            self.assertNotIn("vendor/shared-lib/README.md", payload["changed_files"])

    def test_collect_review_context_prefers_rename_target_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "src").mkdir()
            (repo / "src" / "old_name.ts").write_text("export const oldName = true;\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            subprocess.run(
                ["git", "mv", "src/old_name.ts", "src/new_name.ts"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo", str(repo)],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)

            self.assertIn("src/new_name.ts", payload["changed_files"])
            self.assertNotIn("src/old_name.ts", payload["changed_files"])


if __name__ == "__main__":
    unittest.main()
