"""Tests for the renderer (end-to-end document generation)."""

import os
import tempfile

from src.spec_parser import parse_spec
from src.renderer import render


MINIMAL_SPEC = """\
---
title: Renderer Test
output: renderer_test.docx
---

## [title] Test Document

**Subtitle**: Automated test

**Notes**: Cover page notes.

---

## [content] Test Content

- Alpha
- Beta
- Gamma

**Notes**: Section notes.
"""


def test_render_produces_docx():
    fd, spec_path = tempfile.mkstemp(suffix=".spec.md")
    os.close(fd)
    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(MINIMAL_SPEC)

    output_dir = tempfile.mkdtemp()
    try:
        spec = parse_spec(spec_path)
        out = render(spec, output_dir, spec_path=spec_path)
        assert out.endswith(".docx")
        assert os.path.isfile(out)
        assert os.path.getsize(out) > 0
    finally:
        os.unlink(spec_path)
        for f_name in os.listdir(output_dir):
            os.unlink(os.path.join(output_dir, f_name))
        os.rmdir(output_dir)


def test_render_section_selection():
    fd, spec_path = tempfile.mkstemp(suffix=".spec.md")
    os.close(fd)
    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(MINIMAL_SPEC)

    output_dir = tempfile.mkdtemp()
    try:
        spec = parse_spec(spec_path)
        out = render(spec, output_dir, spec_path=spec_path, section_selection="2")
        assert os.path.isfile(out)
    finally:
        os.unlink(spec_path)
        for f_name in os.listdir(output_dir):
            os.unlink(os.path.join(output_dir, f_name))
        os.rmdir(output_dir)
