#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


@dataclass(frozen=True)
class Finding:
    message: str
    context: str | None = None


class IndexHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._in_title = False
        self._in_h1 = False

        self.title_text = ""
        self.h1_texts: list[str] = []
        self.meta_viewport_content: str | None = None
        self.html_lang: str | None = None
        self.meta_charset: str | None = None

        self.resource_urls: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)

        if tag == "html":
            self.html_lang = attrs_dict.get("lang") or None
        elif tag == "title":
            self._in_title = True
        elif tag == "h1":
            self._in_h1 = True
        elif tag == "meta":
            if "charset" in attrs_dict and attrs_dict["charset"]:
                self.meta_charset = attrs_dict["charset"]
            if attrs_dict.get("name") == "viewport":
                self.meta_viewport_content = attrs_dict.get("content") or ""

        for attr_name in ("href", "src"):
            if attrs_dict.get(attr_name):
                self.resource_urls.append((tag, attrs_dict[attr_name] or ""))

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif tag == "h1":
            self._in_h1 = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_text += data
        elif self._in_h1:
            if data.strip():
                self.h1_texts.append(data.strip())


def is_external_url(url: str) -> bool:
    parsed = urlparse(url)
    return bool(parsed.scheme) or url.startswith("//")


def normalize_doc_ref(url: str) -> str:
    parsed = urlparse(url)
    return parsed.path


def validate_index_html(docs_dir: Path) -> list[Finding]:
    findings: list[Finding] = []

    index_path = docs_dir / "index.html"
    if not index_path.exists():
        return [Finding("Missing docs/index.html", context=str(index_path))]

    content = index_path.read_text(encoding="utf-8")

    if not content.lstrip().lower().startswith("<!doctype html"):
        findings.append(Finding("index.html should start with <!doctype html>"))

    parser = IndexHTMLParser()
    try:
        parser.feed(content)
    except Exception as exc:  # pragma: no cover
        findings.append(Finding("HTML parser failed", context=str(exc)))
        return findings

    if not (parser.html_lang and parser.html_lang.strip()):
        findings.append(Finding("Missing <html lang=\"...\"> attribute"))

    if not (parser.meta_charset and parser.meta_charset.strip()):
        findings.append(Finding("Missing <meta charset=\"...\">"))

    if not parser.meta_viewport_content:
        findings.append(Finding("Missing <meta name=\"viewport\" ...>"))

    title = parser.title_text.strip()
    if not title:
        findings.append(Finding("Missing/empty <title>"))

    h1_combined = " ".join(parser.h1_texts).strip()
    if not re.search(r"\bhello\s+world\b", h1_combined, flags=re.IGNORECASE):
        findings.append(Finding("Missing <h1> containing 'Hello World'"))

    findings.extend(validate_resource_links(docs_dir, parser.resource_urls))
    return findings


def validate_resource_links(
    docs_dir: Path, resource_urls: list[tuple[str, str]]
) -> list[Finding]:
    findings: list[Finding] = []

    docs_root = docs_dir.resolve()

    for tag, raw_url in resource_urls:
        url = (raw_url or "").strip()
        if not url or url.startswith("#"):
            continue
        if url.startswith(("mailto:", "tel:")):
            continue
        if is_external_url(url):
            continue
        if url.startswith("/"):
            findings.append(
                Finding(
                    "Avoid root-relative URLs (breaks under GitHub Pages subpaths)",
                    context=f"{tag} → {url}",
                )
            )
            continue

        ref = normalize_doc_ref(url)
        if not ref:
            continue

        target = (docs_root / ref).resolve()
        if target != docs_root and docs_root not in target.parents:
            findings.append(
                Finding("Ref escapes docs/ directory", context=f"{tag} → {url}")
            )
            continue

        if not target.exists():
            findings.append(
                Finding(
                    "Broken relative reference (file not found)",
                    context=f"{tag} → {url}",
                )
            )

    return findings


def main(argv: list[str]) -> int:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Validate the docs/ GitHub Pages site")
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=repo_root / "docs",
        help="Path to docs directory (default: <repo>/docs)",
    )
    args = parser.parse_args(argv)

    docs_dir: Path = args.docs_dir
    if not docs_dir.exists():
        print(f"ERROR: docs dir does not exist: {docs_dir}", file=sys.stderr)
        return 2

    findings = validate_index_html(docs_dir)
    if findings:
        for finding in findings:
            if finding.context:
                print(f"FAIL: {finding.message} ({finding.context})", file=sys.stderr)
            else:
                print(f"FAIL: {finding.message}", file=sys.stderr)
        return 1

    print("OK: docs/index.html validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
