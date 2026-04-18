"""Tests for the spec parser."""

import os
import tempfile

from src.spec_parser import parse_spec


SAMPLE_SPEC = """\
---
title: Test Document
subtitle: A test
output: Test.docx
style:
  title_font_size: 28
---

## [title] Test Title

**Subtitle**: Hello World

**Notes**: Title notes here.

---

## [content] First Section

- Bullet one
- Bullet two
- Bullet three

**Notes**: Content notes here.

---

## [section-header] Break Point

**Subtitle**: Mid-document break

---

## [two-column] Comparison

**Left**:
- Left item 1
- Left item 2

**Right**:
- Right item 1
- Right item 2

**Notes**: Two column notes.

---

## [resource-box] Resources

**Subtitle**: Helpful links

**Box**: Docs
- Item A | https://example.com/a
- Item B | https://example.com/b
"""


def _write_temp_spec(content: str) -> str:
    fd, path = tempfile.mkstemp(suffix=".spec.md")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def test_parse_metadata():
    path = _write_temp_spec(SAMPLE_SPEC)
    try:
        spec = parse_spec(path)
        assert spec["metadata"]["title"] == "Test Document"
        assert spec["metadata"]["output"] == "Test.docx"
    finally:
        os.unlink(path)


def test_parse_sections_count():
    path = _write_temp_spec(SAMPLE_SPEC)
    try:
        spec = parse_spec(path)
        assert len(spec["sections"]) == 5
    finally:
        os.unlink(path)


def test_parse_title_section():
    path = _write_temp_spec(SAMPLE_SPEC)
    try:
        spec = parse_spec(path)
        title = spec["sections"][0]
        assert title["type"] == "title"
        assert title["title"] == "Test Title"
        assert title["subtitle"] == "Hello World"
        assert "Title notes" in title["notes"]
    finally:
        os.unlink(path)


def test_parse_content_section():
    path = _write_temp_spec(SAMPLE_SPEC)
    try:
        spec = parse_spec(path)
        content = spec["sections"][1]
        assert content["type"] == "content"
        assert len(content["bullets"]) == 3
        assert content["bullets"][0] == "Bullet one"
    finally:
        os.unlink(path)


def test_parse_two_column():
    path = _write_temp_spec(SAMPLE_SPEC)
    try:
        spec = parse_spec(path)
        two_col = spec["sections"][3]
        assert two_col["type"] == "two-column"
        assert len(two_col["left_bullets"]) == 2
        assert len(two_col["right_bullets"]) == 2
    finally:
        os.unlink(path)


def test_parse_resource_box():
    path = _write_temp_spec(SAMPLE_SPEC)
    try:
        spec = parse_spec(path)
        rb = spec["sections"][4]
        assert rb["type"] == "resource-box"
        assert len(rb["boxes"]) == 1
        assert rb["boxes"][0]["label"] == "Docs"
        assert len(rb["boxes"][0]["rows"]) == 2
        assert rb["boxes"][0]["rows"][0]["name"] == "Item A"
        assert rb["boxes"][0]["rows"][0]["url"] == "https://example.com/a"
    finally:
        os.unlink(path)


def test_parse_section_header():
    path = _write_temp_spec(SAMPLE_SPEC)
    try:
        spec = parse_spec(path)
        sh = spec["sections"][2]
        assert sh["type"] == "section-header"
        assert sh["subtitle"] == "Mid-document break"
    finally:
        os.unlink(path)
