"""Renderer – orchestrates parsing, enrichment, image generation, and section building.

Adapted from the presentations renderer to produce Word (.docx) documents.
"""

from __future__ import annotations

import os

from docx import Document

from .enrichment import enrich_content_from_urls, enrich_notes_from_urls
from .images import resolve_image_prompt
from .sections import SECTION_BUILDERS
from .spec_writer import write_spec
from .style import Style

# ---------------------------------------------------------------------------
# Versioned output path
# ---------------------------------------------------------------------------


def _next_version_path(output_dir: str, filename: str) -> str:
    """Return a versioned path: ``file.docx``, ``file_1.docx``, …"""
    base, ext = os.path.splitext(filename)
    candidate = os.path.join(output_dir, filename)
    n = 1
    while os.path.exists(candidate):
        candidate = os.path.join(output_dir, f"{base}_{n}{ext}")
        n += 1
    return candidate


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def _parse_section_selection(selection: str, total: int) -> list[int]:
    """Parse a section selection string into a sorted list of 0-based indices.

    *selection* uses 1-based section numbers.  Supports single numbers (``5``),
    ranges (``3-7``), and comma-separated combinations (``1,3,5-8``).
    Out-of-range values are silently clamped.
    """
    indices: set[int] = set()
    for part in selection.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            lo_s, hi_s = part.split("-", 1)
            lo = max(1, int(lo_s.strip()))
            hi = min(total, int(hi_s.strip()))
            indices.update(range(lo - 1, hi))  # convert to 0-based
        else:
            n = int(part)
            if 1 <= n <= total:
                indices.add(n - 1)
    return sorted(indices)


def render(
    spec: dict,
    output_dir: str = "output",
    image_model: str | None = None,
    refetch: bool = False,
    spec_path: str | None = None,
    section_selection: str | None = None,
) -> str:
    """Render a parsed spec into a Word document and return the output path."""
    metadata = spec["metadata"]
    sections = spec["sections"]

    # Determine output filename (replace .pptx with .docx if needed)
    out_name = metadata.get("output", "document.docx")
    if out_name.endswith(".pptx"):
        out_name = out_name[:-5] + ".docx"
    elif not out_name.endswith(".docx"):
        out_name = os.path.splitext(out_name)[0] + ".docx"

    # Filter sections if a selection was provided
    if section_selection:
        selected = _parse_section_selection(section_selection, len(sections))
        if not selected:
            raise SystemExit(f"Error: no valid sections in selection '{section_selection}' (doc has {len(sections)} sections)")
        sections = [sections[i] for i in selected]
        print(f"Generating {len(sections)} of {len(spec['sections'])} sections (selection: {section_selection})")

    # Image model priority: CLI flag > front-matter
    default_model = (
        image_model
        or metadata.get("image_model", "").strip().lower()
    )
    if not default_model:
        print(
            "Warning: no image_model specified in front matter or --image-model flag. "
            "ImagePrompt directives will be skipped."
        )

    # Text model for note enrichment: front-matter > env var > default
    text_model = metadata.get("text_model", "").strip()

    # Build Style from front-matter
    style = Style(metadata.get("style"))

    doc = Document()

    # Set default document font
    doc_style = doc.styles["Normal"]
    doc_style.font.size = style.body_font

    # Set document title in core properties
    doc.core_properties.title = metadata.get("title", "")
    doc.core_properties.author = metadata.get("author", "")

    any_enriched = False

    for section_data in sections:
        stype = section_data["type"]
        builder = SECTION_BUILDERS.get(stype)
        if builder is None:
            print(f"Warning: unknown section type '{stype}', skipping.")
            continue

        # Skip enrichment if already cached (unless --refetch)
        already_enriched = section_data.get("enriched", False)
        if already_enriched and not refetch:
            pass  # use cached content
        else:
            # Enrich section content from ContentUrls before building
            old_bullets = list(section_data.get("bullets", []))
            old_left = list(section_data.get("left_bullets", []))
            old_right = list(section_data.get("right_bullets", []))
            old_notes = section_data.get("notes", "")

            enrich_content_from_urls(section_data, text_model=text_model)
            enrich_notes_from_urls(section_data, text_model=text_model)

            # Detect if enrichment actually changed anything
            new_bullets = section_data.get("bullets", [])
            new_left = section_data.get("left_bullets", [])
            new_right = section_data.get("right_bullets", [])
            new_notes = section_data.get("notes", "")
            if (new_bullets != old_bullets or new_left != old_left
                    or new_right != old_right or new_notes != old_notes):
                section_data["enriched"] = True
                any_enriched = True

        # Resolve any ImagePrompt → generate images before building
        had_image = bool(section_data.get("image"))
        resolve_image_prompt(section_data, output_dir, default_model=default_model)
        if not had_image and section_data.get("image"):
            any_enriched = True

        builder(doc, section_data, style)

    # Write enriched spec back to disk so next run uses cached data
    if any_enriched and spec_path:
        write_spec(spec, spec_path)
        print(f"Saved enriched spec -> {spec_path}")

    os.makedirs(output_dir, exist_ok=True)
    out_path = _next_version_path(output_dir, out_name)
    doc.save(out_path)
    print(f"Saved {len(sections)} sections -> {out_path}")
    return out_path
