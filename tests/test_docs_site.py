import unittest
from pathlib import Path


class TestDocsSite(unittest.TestCase):
    def setUp(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        self.index_path = repo_root / "docs" / "index.html"

    def test_docs_index_exists(self) -> None:
        self.assertTrue(self.index_path.exists(), f"Missing {self.index_path}")

    def test_docs_index_has_expected_structure(self) -> None:
        html = self.index_path.read_text(encoding="utf-8")

        self.assertRegex(html.lower(), r"<!doctype\s+html>", "Missing doctype")
        self.assertIn('<html lang="en">', html, "Missing html lang attribute")
        self.assertIn("<head>", html)
        self.assertIn("<body>", html)
        self.assertIn("</html>", html)

        self.assertIn("Hello World", html, "Hello World text missing")
        self.assertRegex(
            html,
            r'<meta\s+name="viewport"\s+content="[^"]*width=device-width[^"]*"\s*/?>',
            "Missing responsive viewport meta",
        )
        self.assertRegex(html, r"<title>[^<]*Hello World[^<]*</title>", "Missing title")

    def test_docs_index_has_no_external_dependencies(self) -> None:
        html = self.index_path.read_text(encoding="utf-8")

        self.assertNotIn(
            "https://",
            html,
            "Page should be self-contained (no external asset URLs)",
        )

    def test_docs_index_has_theme_toggle_hook(self) -> None:
        html = self.index_path.read_text(encoding="utf-8")

        self.assertRegex(
            html,
            r'id="theme-toggle"',
            'Missing theme toggle button id="theme-toggle"',
        )
        self.assertRegex(
            html,
            r"localStorage\.setItem\(\s*['\"]theme['\"]",
            "Missing localStorage theme persistence",
        )


if __name__ == "__main__":
    unittest.main()

