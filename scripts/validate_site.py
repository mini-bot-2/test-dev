#!/usr/bin/env python3

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path


@dataclass
class PageSignals:
    title: str = ""
    h1_texts: list[str] = field(default_factory=list)
    has_viewport: bool = False
    stylesheets: list[str] = field(default_factory=list)
    scripts: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)


class SignalsParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.signals = PageSignals()
        self._stack: list[str] = []
        self._title_chunks: list[str] = []
        self._h1_chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {k.lower(): (v or "") for k, v in attrs}
        self._stack.append(tag.lower())

        if tag.lower() == "meta":
            if attrs_dict.get("name", "").lower() == "viewport":
                self.signals.has_viewport = True

        if tag.lower() == "link":
            if attrs_dict.get("rel", "").lower() == "stylesheet":
                href = attrs_dict.get("href", "")
                if href:
                    self.signals.stylesheets.append(href)

        if tag.lower() == "script":
            src = attrs_dict.get("src", "")
            if src:
                self.signals.scripts.append(src)

        if tag.lower() == "a":
            href = attrs_dict.get("href", "")
            if href:
                self.signals.links.append(href)

    def handle_endtag(self, tag: str) -> None:
        tag_lower = tag.lower()
        if tag_lower == "title":
            self.signals.title = " ".join("".join(self._title_chunks).split())
            self._title_chunks.clear()
        if tag_lower == "h1":
            text = " ".join("".join(self._h1_chunks).split())
            if text:
                self.signals.h1_texts.append(text)
            self._h1_chunks.clear()

        while self._stack:
            popped = self._stack.pop()
            if popped == tag_lower:
                break

    def handle_data(self, data: str) -> None:
        if not self._stack:
            return
        current = self._stack[-1]
        if current == "title":
            self._title_chunks.append(data)
        if current == "h1":
            self._h1_chunks.append(data)


def is_relative_link(href: str) -> bool:
    lowered = href.lower().strip()
    if lowered.startswith(("http://", "https://", "mailto:", "tel:", "#", "data:")):
        return False
    return True


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    docs_dir = repo_root / "docs"
    index_path = docs_dir / "index.html"

    errors: list[str] = []

    if not docs_dir.is_dir():
        errors.append(f"Missing docs directory: {docs_dir}")
        return report(errors)

    if not (docs_dir / ".nojekyll").is_file():
        errors.append("Missing docs/.nojekyll (recommended for GitHub Pages static sites).")

    if not index_path.is_file():
        errors.append(f"Missing main page: {index_path}")
        return report(errors)

    html = index_path.read_text(encoding="utf-8")

    parser = SignalsParser()
    parser.feed(html)
    parser.close()
    s = parser.signals

    if "hello world" not in s.title.lower():
        errors.append(f"Expected <title> to contain 'Hello World', got: {s.title!r}")

    if not any("hello world" in t.lower() for t in s.h1_texts):
        errors.append(f"Expected an <h1> containing 'Hello World', got: {s.h1_texts!r}")

    if not s.has_viewport:
        errors.append("Missing responsive meta viewport tag.")

    for stylesheet in s.stylesheets:
        if is_relative_link(stylesheet) and not (docs_dir / stylesheet).is_file():
            errors.append(f"Stylesheet link not found: docs/{stylesheet}")

    for script in s.scripts:
        if is_relative_link(script) and not (docs_dir / script).is_file():
            errors.append(f"Script src not found: docs/{script}")

    for href in s.links:
        if is_relative_link(href) and not (docs_dir / href).exists():
            errors.append(f"Relative link target not found: docs/{href}")

    return report(errors)


def report(errors: list[str]) -> int:
    if not errors:
        print("OK: docs/index.html looks healthy.")
        return 0

    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

