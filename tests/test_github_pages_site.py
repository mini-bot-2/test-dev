import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


class _TagCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[tuple[str, dict[str, str]]] = []
        self.text_chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._add(tag, attrs)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._add(tag, attrs)

    def handle_data(self, data: str) -> None:
        if data:
            self.text_chunks.append(data)

    def _add(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        normalized_attrs: dict[str, str] = {}
        for key, value in attrs:
            if key is None or value is None:
                continue
            normalized_attrs[key.lower()] = value
        self.tags.append((tag.lower(), normalized_attrs))


class TestGitHubPagesHelloWorld(unittest.TestCase):
    def setUp(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        self.docs_dir = repo_root / "docs"
        self.index_html = self.docs_dir / "index.html"

    def test_index_html_exists(self) -> None:
        self.assertTrue(self.index_html.exists(), f"Missing {self.index_html}")

    def test_index_has_doctype_and_title(self) -> None:
        html = self.index_html.read_text(encoding="utf-8")
        self.assertRegex(html, r"(?is)<!doctype\s+html>")
        self.assertRegex(html, r"(?is)<title>\s*Hello World\s*</title>")

    def test_index_has_lang_and_viewport_meta(self) -> None:
        html = self.index_html.read_text(encoding="utf-8")
        parser = _TagCollector()
        parser.feed(html)

        html_tags = [attrs for tag, attrs in parser.tags if tag == "html"]
        self.assertTrue(html_tags, "Missing <html> tag")
        self.assertTrue(
            any(attrs.get("lang") == "en" for attrs in html_tags),
            "Expected <html lang=\"en\">",
        )

        meta_viewports = [
            attrs
            for tag, attrs in parser.tags
            if tag == "meta" and attrs.get("name", "").lower() == "viewport"
        ]
        self.assertTrue(meta_viewports, "Missing <meta name=\"viewport\">")

    def test_hello_world_visible_text(self) -> None:
        html = self.index_html.read_text(encoding="utf-8")
        parser = _TagCollector()
        parser.feed(html)

        text = " ".join(chunk.strip() for chunk in parser.text_chunks if chunk.strip())
        self.assertRegex(text, r"(?i)hello\s+world")

    def test_stylesheet_and_favicon_exist(self) -> None:
        html = self.index_html.read_text(encoding="utf-8")
        parser = _TagCollector()
        parser.feed(html)

        stylesheet_hrefs = [
            attrs.get("href", "")
            for tag, attrs in parser.tags
            if tag == "link" and "stylesheet" in attrs.get("rel", "").lower()
        ]
        self.assertTrue(stylesheet_hrefs, "Missing stylesheet <link rel=\"stylesheet\">")
        self.assertIn(
            "assets/styles.css",
            stylesheet_hrefs,
            "Expected stylesheet href=\"assets/styles.css\"",
        )

        favicon_hrefs = [
            attrs.get("href", "")
            for tag, attrs in parser.tags
            if tag == "link" and attrs.get("rel", "").lower() in {"icon", "shortcut icon"}
        ]
        self.assertTrue(favicon_hrefs, "Missing favicon <link rel=\"icon\">")

        for href in stylesheet_hrefs + favicon_hrefs:
            if not href:
                continue
            if href.startswith(("http://", "https://", "//")):
                continue
            self.assertFalse(
                href.startswith("/"),
                f"Local asset paths should be relative, got: {href}",
            )
            asset_path = (self.docs_dir / href).resolve()
            self.assertTrue(
                asset_path.is_file(),
                f"Missing referenced asset: {href} (resolved to {asset_path})",
            )

    def test_local_links_resolve(self) -> None:
        html = self.index_html.read_text(encoding="utf-8")
        parser = _TagCollector()
        parser.feed(html)

        candidates: set[str] = set()
        for _tag, attrs in parser.tags:
            for key in ("href", "src"):
                value = attrs.get(key)
                if value:
                    candidates.add(value)

        for raw in sorted(candidates):
            if raw.startswith(("#", "mailto:", "tel:", "data:", "javascript:")):
                continue

            split = urlsplit(raw)
            if split.scheme in {"http", "https"} or raw.startswith("//"):
                continue

            path = split.path
            if not path:
                continue

            self.assertFalse(
                path.startswith("/"),
                f"Project Pages should avoid root-absolute paths: {raw}",
            )

            # Prevent accidental traversal outside `docs/`.
            parts = Path(path).parts
            self.assertNotIn("..", parts, f"Disallowed path traversal in link: {raw}")

            target = (self.docs_dir / path).resolve()
            self.assertTrue(
                str(target).startswith(str(self.docs_dir.resolve())),
                f"Link resolves outside docs/: {raw} -> {target}",
            )
            self.assertTrue(target.exists(), f"Broken local link: {raw} -> {target}")
