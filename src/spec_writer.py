"""Serialize an enriched spec dict back to ``.spec.md`` format."""

from __future__ import annotations

import yaml


def write_spec(spec: dict, path: str) -> None:
    """Write the spec (metadata + sections) back to *path* as ``.spec.md``."""
    lines: list[str] = []

    # --- YAML front matter ---
    lines.append("---")
    fm = yaml.dump(spec["metadata"], default_flow_style=False, sort_keys=False).rstrip()
    lines.append(fm)
    lines.append("---")
    lines.append("")

    for i, section in enumerate(spec["sections"]):
        lines.extend(_serialize_section(section))
        if i < len(spec["sections"]) - 1:
            lines.append("")
            lines.append("---")
            lines.append("")

    # Ensure trailing newline
    text = "\n".join(lines)
    if not text.endswith("\n"):
        text += "\n"

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _serialize_section(section: dict) -> list[str]:
    """Serialize a single section dict into markdown lines."""
    lines: list[str] = []
    stype = section["type"]
    title = section["title"]

    lines.append(f"## [{stype}] {title}")
    lines.append("")

    # Subtitle
    if "subtitle" in section and section["subtitle"]:
        lines.append(f"**Subtitle**: {section['subtitle']}")
        lines.append("")

    # Two-column content
    if stype == "two-column":
        left = section.get("left_bullets", [])
        right = section.get("right_bullets", [])
        if left:
            lines.append("**Left**:")
            for b in left:
                lines.append(f"- {b}")
            lines.append("")
        if right:
            lines.append("**Right**:")
            for b in right:
                lines.append(f"- {b}")
            lines.append("")

    # Regular bullets (content sections)
    elif stype == "content":
        bullets = section.get("bullets", [])
        if bullets:
            for b in bullets:
                lines.append(f"- {b}")
            lines.append("")

    # Resource-box content
    elif stype == "resource-box":
        for box in section.get("boxes", []):
            lines.append(f"**Box**: {box['label']}")
            for row in box.get("rows", []):
                if row.get("url"):
                    lines.append(f"- {row['name']} | {row['url']}")
                else:
                    lines.append(f"- {row['name']}")
            lines.append("")

    # Image
    img = section.get("image")
    if img:
        parts = [img["path"]]
        for k in ("left", "top", "width", "height"):
            if k in img:
                parts.append(str(img[k]))
        lines.append(f"**Image**: {', '.join(parts)}")

    # ImagePrompt
    ip = section.get("image_prompt")
    if ip:
        parts = [ip["prompt"]]
        for k in ("left", "top", "width", "height"):
            if k in ip:
                parts.append(str(ip[k]))
        lines.append(f"**ImagePrompt**: {', '.join(parts)}")
        if "model" in ip:
            lines.append(f"**ImageModel**: {ip['model']}")

    # ContentUrls
    urls = section.get("content_urls", [])
    if urls:
        lines.append("")
        lines.append("**ContentUrls**:")
        for url in urls:
            lines.append(f"- {url}")

    # Enriched flag
    if section.get("enriched"):
        lines.append("")
        lines.append("**Enriched**: true")

    # Notes
    notes = section.get("notes", "")
    if notes:
        lines.append("")
        lines.append(f"**Notes**: {notes}")

    return lines
