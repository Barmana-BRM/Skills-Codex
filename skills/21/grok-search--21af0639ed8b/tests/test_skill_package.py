import json
import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class GrokSearchPackageTests(unittest.TestCase):
    def test_required_skill_files_are_present(self):
        required_paths = [
            ROOT / "SKILL.md",
            ROOT / "agents" / "openai.yaml",
            ROOT / "references" / "planning.md",
            ROOT / "config.example.json",
            ROOT / "package.json",
            ROOT / "scripts" / "search.js",
            ROOT / "scripts" / "fetch.js",
            ROOT / "scripts" / "map.js",
            ROOT.parent / "docs" / "usage" / "grok-search.md",
        ]
        missing = [
            str(path.relative_to(ROOT.parent))
            for path in required_paths
            if not path.exists()
        ]
        self.assertEqual(missing, [])

    def test_skill_frontmatter_and_metadata_are_aligned(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"---\n(.*?)\n---", skill_text, re.DOTALL)
        self.assertIsNotNone(match)
        frontmatter = match.group(1)

        self.assertIn("name: grok-search", frontmatter)
        self.assertIn("search the web", frontmatter)

        metadata = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("interface:", metadata)
        self.assertIn('display_name: "Grok Search"', metadata)
        self.assertIn('short_description: "Search and read the live web with sourced results"', metadata)
        self.assertIn("$grok-search", metadata)

    def test_script_routing_and_result_reading_are_documented(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for expected in [
            "scripts/fetch.js",
            "scripts/map.js",
            "scripts/search.js",
            "references/planning.md",
            "Every script prints one JSON object",
            "content.full_path",
        ]:
            self.assertIn(expected, skill_text)

    def test_fetch_writes_full_path_when_truncated(self):
        fetch_script = (ROOT / "scripts" / "fetch.js").read_text(encoding="utf-8")
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("full_path: contentInfo.full_output_path", fetch_script)
        self.assertNotIn("--full-path", fetch_script)
        self.assertIn("content.full_path", skill_text)

    def test_usage_guide_reads_current_search_sources(self):
        usage = (ROOT.parent / "docs" / "usage" / "grok-search.md").read_text(encoding="utf-8")

        self.assertIn("sources.items", usage)
        self.assertNotIn("sources.merged", usage)
        self.assertNotIn("sources.grok[]", usage)

    def test_example_config_carries_no_real_credentials(self):
        config = json.loads((ROOT / "config.example.json").read_text(encoding="utf-8"))

        self.assertEqual(config["apiKey"], "your-grok-api-key")
        self.assertEqual(config["tavilyApiKey"], "")
        self.assertEqual(config["firecrawlApiKey"], "")

    def test_node_test_entrypoint_is_declared(self):
        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))

        self.assertEqual(package["name"], "grok-search")
        self.assertIn("test", package["scripts"])


if __name__ == "__main__":
    unittest.main()
