"""Style resolution: reads font sizes and colors from spec front-matter ``style`` block.

Adapted for Word document generation using python-docx units.
"""

from docx.shared import Pt

# Fallback defaults (used when spec omits a value)
_DEFAULTS = {
    "title_font_size": 28,
    "subtitle_font_size": 16,
    "body_font_size": 11,
    "heading_font_size": 18,
    "column_heading_font_size": 14,
    "column_body_font_size": 11,
    "heading_color": "#1F2937",
    "body_color": "#374151",
    "accent_color": "#0078D4",
    "title_color": "#000000",
    "subtitle_color": "#4B5563",
    "table_header_bg": "#0078D4",
    "table_header_color": "#FFFFFF",
    "table_border_color": "#D1D5DB",
    "resource_label_bg": "#E3008C",
    "resource_label_color": "#FFFFFF",
}


class Style:
    """Immutable bag of resolved font sizes (as ``Pt`` values) and colors."""

    def __init__(self, spec_style: dict | None = None):
        t = {**_DEFAULTS, **(spec_style or {})}
        self.title_font = Pt(int(t["title_font_size"]))
        self.subtitle_font = Pt(int(t["subtitle_font_size"]))
        self.body_font = Pt(int(t["body_font_size"]))
        self.heading_font = Pt(int(t["heading_font_size"]))
        self.col_heading_font = Pt(int(t["column_heading_font_size"]))
        self.col_body_font = Pt(int(t["column_body_font_size"]))
        # Color settings
        self.heading_color = str(t["heading_color"])
        self.body_color = str(t["body_color"])
        self.accent_color = str(t["accent_color"])
        self.title_color = str(t["title_color"])
        self.subtitle_color = str(t["subtitle_color"])
        self.table_header_bg = str(t["table_header_bg"])
        self.table_header_color = str(t["table_header_color"])
        self.table_border_color = str(t["table_border_color"])
        self.resource_label_bg = str(t["resource_label_bg"])
        self.resource_label_color = str(t["resource_label_color"])
