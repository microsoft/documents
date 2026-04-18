"""Tests for the spec writer."""

import os
import tempfile

from src.spec_parser import parse_spec
from src.spec_writer import write_spec


def test_round_trip():
    """Write a spec, re-parse it, and verify the data survives."""
    spec = {
        "metadata": {
            "title": "Round Trip Test",
            "output": "test.docx",
        },
        "sections": [
            {
                "type": "title",
                "title": "Hello",
                "subtitle": "World",
                "notes": "Some notes",
                "content_urls": [],
                "image": None,
                "image_prompt": None,
                "enriched": False,
            },
            {
                "type": "content",
                "title": "Bullets",
                "bullets": ["First", "Second"],
                "notes": "Bullet notes",
                "content_urls": [],
                "image": None,
                "image_prompt": None,
                "enriched": False,
            },
        ],
    }

    fd, path = tempfile.mkstemp(suffix=".spec.md")
    os.close(fd)
    try:
        write_spec(spec, path)
        reparsed = parse_spec(path)
        assert reparsed["metadata"]["title"] == "Round Trip Test"
        assert len(reparsed["sections"]) == 2
        assert reparsed["sections"][0]["type"] == "title"
        assert reparsed["sections"][0]["subtitle"] == "World"
        assert reparsed["sections"][1]["bullets"] == ["First", "Second"]
    finally:
        os.unlink(path)
