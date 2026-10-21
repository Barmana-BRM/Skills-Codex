"""Consistency guards for the cloudphone-adb-tunnel skill package.

scripts/spawn.sh and scripts/keepalive.sh must stay byte-identical to the
heredocs embedded in scripts/install-termux.sh (the installer is what actually
writes them onto the phone; the bundled copies are standalone repair tools).
The package must also stay free of credential material — real tokens live only
in the operator's private deploy kit.
"""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "install-termux.sh"

ALLOWED_IPV4 = {"127.0.0.1", "0.0.0.0", "223.5.5.5", "119.29.29.29"}
INTERACTIVE_LINES = (
    'SERVER_URL="${SERVER_URL:-}"',
    'FRPS_TOKEN="${FRPS_TOKEN:-}"',
    'STCP_SK="${STCP_SK:-}"',
)


def _embedded(marker: str) -> str:
    text = INSTALLER.read_text(encoding="utf-8")
    match = re.search(r"<<'" + marker + r"'\n(.*?)\n" + marker + r"\n", text, re.S)
    if not match:
        raise AssertionError(f"installer heredoc <<'{marker}' not found")
    return match.group(1) + "\n"


class ScriptSyncTests(unittest.TestCase):
    def test_bundled_spawn_matches_installer_heredoc(self):
        self.assertEqual(_embedded("SEOF"), (ROOT / "scripts" / "spawn.sh").read_text(encoding="utf-8"))

    def test_bundled_keepalive_matches_installer_heredoc(self):
        self.assertEqual(_embedded("KEOF"), (ROOT / "scripts" / "keepalive.sh").read_text(encoding="utf-8"))


class NoCredentialMaterialTests(unittest.TestCase):
    def test_installer_is_the_interactive_variant(self):
        text = INSTALLER.read_text(encoding="utf-8")
        for line in INTERACTIVE_LINES:
            self.assertIn(line, text, "bundled installer must not pre-fill connection secrets")

    def test_no_32hex_literal_like_tokens_or_keys(self):
        # 只扫源文件; 缓存/字节码产物(__pycache__/.pytest_cache)不在扫描范围
        sources = [ROOT / "SKILL.md", INSTALLER, ROOT / "scripts" / "spawn.sh", ROOT / "scripts" / "keepalive.sh"]
        sources += sorted((ROOT / "references").glob("*.md"))
        pattern = re.compile(r"\b[0-9a-f]{32}\b")
        for path in sources:
            # sha256 校验值是 64 位十六进制, 词边界下不会命中 32 位; 命中即疑似凭据
            self.assertEqual([], pattern.findall(path.read_text(encoding="utf-8", errors="ignore")), str(path))

    def test_visitor_port_default_matches_skill_md(self):
        m = re.search(r'VISITOR_BIND_PORT="\$\{VISITOR_BIND_PORT:-(\d+)\}"', INSTALLER.read_text(encoding="utf-8"))
        self.assertIsNotNone(m, "VISITOR_BIND_PORT default missing in installer")
        self.assertIn(f"bindPort = {m.group(1)}", (ROOT / "SKILL.md").read_text(encoding="utf-8"),
                      "SKILL.md visitor template drifted from the installer default port")

    def test_no_unexpected_ipv4_literals(self):
        for path in sorted((ROOT / "scripts").glob("*.sh")) + [ROOT / "SKILL.md"]:
            for ip in re.findall(r"(\d{1,3}(?:\.\d{1,3}){3})", path.read_text(encoding="utf-8")):
                self.assertIn(ip, ALLOWED_IPV4, f"{path}: unexpected IPv4 literal {ip}")


if __name__ == "__main__":
    unittest.main()
