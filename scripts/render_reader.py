#!/usr/bin/env python3
"""Render an overview-first reader from explicit, localized JSON content."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import uuid
from pathlib import Path
from urllib.parse import urlsplit


LANGUAGE_TAG = re.compile(
    r"(?:[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*|[xXiI](?:-[A-Za-z0-9]{1,8})+)\Z"
)
DIRECTIONS = {"auto", "ltr", "rtl"}
LABEL_KEYS = ("overview", "full", "expand", "collapse", "body", "source")
TEMPLATE = Path(__file__).resolve().parents[1] / "assets" / "reader.html"


def text_value(value: object, field: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        raise ValueError(f"{field} must be {'a string' if allow_empty else 'a nonempty string'}")
    if "\x00" in value:
        raise ValueError(f"{field} contains a null character, which HTML cannot preserve")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as error:
        raise ValueError(f"{field} contains an invalid Unicode surrogate") from error
    return value


def language_value(value: object, field: str) -> str:
    value = text_value(value, field)
    if not LANGUAGE_TAG.fullmatch(value):
        raise ValueError(f"{field} must be a basic BCP 47 language tag, such as en or zh-Hant")
    return value


def direction_value(value: object, field: str) -> str:
    if not isinstance(value, str) or value not in DIRECTIONS:
        raise ValueError(f"{field} must be auto, ltr, or rtl")
    return value


def validate(data: object) -> dict:
    if not isinstance(data, dict):
        raise ValueError("input must be a JSON object")
    output = {
        "title": text_value(data.get("title"), "title"),
        "language": language_value(data.get("language"), "language"),
        "notice": text_value(data.get("notice"), "notice"),
        "direction": direction_value(data.get("direction", "auto"), "direction"),
        "byline": text_value(data.get("byline", ""), "byline", allow_empty=True),
    }
    labels = data.get("labels")
    if not isinstance(labels, dict):
        raise ValueError("labels must be an object containing every required localized label")
    output["labels"] = {key: text_value(labels.get(key), f"labels.{key}") for key in LABEL_KEYS}
    sections = data.get("sections")
    if not isinstance(sections, list) or not sections:
        raise ValueError("sections must be a nonempty array")
    output["sections"] = []
    for index, section in enumerate(sections, 1):
        path = f"sections[{index - 1}]"
        if not isinstance(section, dict):
            raise ValueError(f"{path} must be an object")
        section_language = language_value(section.get("language", output["language"]), f"{path}.language")
        output["sections"].append(
            {
                "heading": text_value(section.get("heading", ""), f"{path}.heading", allow_empty=True),
                "overview": text_value(section.get("overview"), f"{path}.overview"),
                "body": text_value(section.get("body"), f"{path}.body"),
                "language": section_language,
                "overview_language": language_value(section.get("overview_language", section_language), f"{path}.overview_language"),
                "body_language": language_value(section.get("body_language", section_language), f"{path}.body_language"),
                "direction": direction_value(section.get("direction", "auto"), f"{path}.direction"),
            }
        )
    source_url = data.get("source_url", "")
    output["source_url"] = text_value(source_url, "source_url", allow_empty=True)
    if source_url:
        parsed = urlsplit(source_url)
        if (
            parsed.scheme.lower() not in {"http", "https"}
            or not parsed.netloc
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or any(char.isspace() or ord(char) < 32 for char in source_url)
        ):
            raise ValueError("source_url must be an HTTP(S) URL without credentials or whitespace")
    return output


def escape_text(value: str) -> str:
    # Character references preserve CR characters through HTML's newline normalization.
    return html.escape(value, quote=False).replace("\r", "&#13;")


def escape_attribute(value: str) -> str:
    return html.escape(value, quote=True).replace("\r", "&#13;").replace("\n", "&#10;")


def render(data: dict, *, standalone: bool = False) -> str:
    normalized = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    content_id = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    root_id = "quick-read-" + uuid.uuid4().hex
    labels = data["labels"]
    sections = []
    for index, section in enumerate(data["sections"], 1):
        section_id = f"{root_id}-section-{index}"
        heading = (
            f'<span class="or-heading">{escape_text(section["heading"])}</span>'
            if section["heading"]
            else ""
        )
        sections.append(
            f'<details id="{section_id}" data-section="{index}" '
            f'lang="{escape_attribute(section["language"])}" '
            f'dir="{section["direction"]}">\n'
            f'<summary class="cursor-interaction" lang="{escape_attribute(section["overview_language"])}">\n'
            '<span class="or-summary-content">\n'
            f'{heading}\n'
            f'<span class="or-overview">{escape_text(section["overview"])}</span>\n'
            f'<span class="or-disclosure-label" lang="{escape_attribute(data["language"])}" dir="auto" aria-hidden="true">'
            f'<span class="or-closed-label">{escape_text(labels["expand"])}</span>'
            f'<span class="or-open-label">{escape_text(labels["collapse"])}</span>'
            '</span>\n</span>\n</summary>\n'
            f'<div class="or-full-body" lang="{escape_attribute(section["body_language"])}">\n'
            f'<p class="or-body-label" lang="{escape_attribute(data["language"])}" dir="auto">{escape_text(labels["body"])}</p>\n'
            f'<div class="or-body-text">{escape_text(section["body"])}</div>\n'
            '</div>\n</details>'
        )
    replacements = {
        "ROOT_ID": root_id,
        "CONTENT_ID": content_id,
        "LANGUAGE": escape_attribute(data["language"]),
        "DIRECTION": data["direction"],
        "TITLE": escape_text(data["title"]),
        "BYLINE": f'<p class="or-byline">{escape_text(data["byline"])}</p>' if data["byline"] else "",
        "NOTICE": escape_text(data["notice"]),
        "OVERVIEW_LABEL": escape_text(labels["overview"]),
        "FULL_LABEL": escape_text(labels["full"]),
        "SECTIONS": "\n".join(sections),
        "SOURCE": (
            '<footer class="or-source">'
            f'<a href="{escape_attribute(data["source_url"])}" target="_blank" rel="noopener noreferrer">'
            f'{escape_text(labels["source"])}</a></footer>'
            if data["source_url"]
            else ""
        ),
    }
    template = TEMPLATE.read_text(encoding="utf-8")
    # A single substitution pass prevents content resembling a token being rewritten.
    fragment = re.sub(r"@@([A-Z_]+)@@", lambda match: replacements[match.group(1)], template)
    if not standalone:
        if len(fragment.encode("utf-8")) > 1_000_000:
            raise ValueError("fragment exceeds 1 MB; use --standalone or split the document without truncating it")
        return fragment
    return (
        '<!doctype html>\n'
        f'<html lang="{escape_attribute(data["language"])}" dir="{data["direction"]}">\n'
        '<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<meta name="color-scheme" content="light dark">\n'
        f'<title>{escape_text(data["title"])}</title>\n'
        '<style>body { margin: 0; padding: 20px 12px; background: light-dark(#f6f6f3, #181917); }</style>\n'
        '</head>\n<body>\n' + fragment + '\n</body>\n</html>\n'
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="UTF-8 JSON content file")
    parser.add_argument("output", type=Path, help="HTML output file")
    parser.add_argument("--standalone", action="store_true", help="write a complete HTML document instead of a fragment")
    parser.add_argument("--force", action="store_true", help="replace an existing regular output file")
    args = parser.parse_args()
    try:
        if args.input.resolve() == args.output.resolve():
            raise ValueError("input and output must be different files")
        if args.output.is_symlink():
            raise ValueError("output must not be a symbolic link")
        if args.output.exists() and not args.output.is_file():
            raise ValueError("output must be a regular file")
        data = validate(json.loads(args.input.read_text(encoding="utf-8")))
        result = render(data, standalone=args.standalone)
        mode = "w" if args.force else "x"
        with args.output.open(mode, encoding="utf-8", newline="") as destination:
            destination.write(result)
    except (OSError, ValueError, KeyError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print(str(args.output.resolve()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
