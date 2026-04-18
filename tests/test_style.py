"""Tests for style resolution."""

from src.style import Style


def test_default_style():
    s = Style()
    assert s.title_font is not None
    assert s.body_font is not None
    assert s.heading_color == "#1F2937"
    assert s.accent_color == "#0078D4"


def test_custom_style():
    s = Style({"title_font_size": 40, "heading_color": "#FF0000"})
    from docx.shared import Pt
    assert s.title_font == Pt(40)
    assert s.heading_color == "#FF0000"
    # Defaults still apply for unset values
    assert s.accent_color == "#0078D4"
