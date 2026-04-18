"""Spec-file parser: reads a ``.spec.md`` file into metadata + section list.

Reused from the presentations generator with section terminology.
The spec format is identical — ``## [type] Title`` blocks separated by ``---``.
"""

import re
import sys

import yaml


def parse_spec(path: str) -> dict:
    """Parse a document spec markdown file into metadata + section list."""
    with open(path, encoding="utf-8") as f:
        text = f.read()

    # Split YAML front matter
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not fm_match:
        sys.exit("Error: spec file must start with YAML front matter (--- … ---)")
    metadata = yaml.safe_load(fm_match.group(1))
    body = text[fm_match.end():]

    # Split sections on horizontal rules (--- on its own line)
    raw_sections = re.split(r"\n---\s*\n", body)
    sections = []
    for raw in raw_sections:
        raw = raw.strip()
        if not raw:
            continue
        section = _parse_section(raw)
        if section:
            sections.append(section)

    return {"metadata": metadata, "sections": sections}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_section(raw: str) -> dict | None:
    """Parse a single section block into a structured dict."""
    header_match = re.match(r"^##\s+\[(\w[\w-]*)\]\s+(.+)", raw)
    if not header_match:
        return None
    section_type = header_match.group(1).strip()
    title = header_match.group(2).strip()
    rest = raw[header_match.end():].strip()

    # Extract notes (everything after **Notes**: to end)
    notes = ""
    notes_match = re.split(r"\*\*Notes\*\*\s*:\s*", rest, maxsplit=1)
    if len(notes_match) == 2:
        rest = notes_match[0].strip()
        notes = notes_match[1].strip()

    section: dict = {"type": section_type, "title": title, "notes": notes}

    section["content_urls"] = _parse_content_urls(rest)
    section["image"] = _parse_image_field(rest)
    section["image_prompt"] = _parse_image_prompt_field(rest)
    section["enriched"] = bool(re.search(r"\*\*Enriched\*\*\s*:\s*true", rest, re.IGNORECASE))

    if section_type == "title":
        sub_match = re.search(r"\*\*Subtitle\*\*\s*:\s*(.+)", rest)
        section["subtitle"] = sub_match.group(1).strip() if sub_match else ""

    elif section_type == "section-header":
        sub_match = re.search(r"\*\*Subtitle\*\*\s*:\s*(.+)", rest)
        section["subtitle"] = sub_match.group(1).strip() if sub_match else ""

    elif section_type == "content":
        section["bullets"] = _dedupe_bullets(_extract_bullets(_strip_directives(rest)))

    elif section_type == "two-column":
        section.update(_parse_two_column(rest))

    elif section_type == "resource-box":
        sub_match = re.search(r"\*\*Subtitle\*\*\s*:\s*(.+)", rest)
        section["subtitle"] = sub_match.group(1).strip() if sub_match else ""
        section["boxes"] = _parse_resource_boxes(rest)

    return section


def _extract_bullets(text: str) -> list[str]:
    return [m.group(1).strip() for m in re.finditer(r"^[-*]\s+(.+)", text, re.MULTILINE)]


def _strip_directives(text: str) -> str:
    """Remove directive blocks and metadata lines, leaving only bullet content."""
    text = re.sub(r"\*\*ContentUrls\*\*\s*:\s*\n(?:\s*-\s+\S+\n?)*", "", text)
    text = re.sub(r"---\s+Supplemental\s+\(.*?\)\s+---.*?(?=\n---|$)", "", text, flags=re.DOTALL)
    text = re.sub(
        r"\*\*(?:Image|ImagePrompt|ImageModel|Animation|Enriched|Subtitle)\*\*\s*:\s*.+",
        "", text,
    )
    text = re.sub(r"\*\*\w+Pos\*\*\s*:\s*.+", "", text)
    text = re.sub(r"^[-*]\s+https?://\S+\s*$", "", text, flags=re.MULTILINE)
    return text


def _dedupe_bullets(bullets: list[str]) -> list[str]:
    """Remove duplicate bullets, preserving order."""
    seen: set[str] = set()
    result: list[str] = []
    for b in bullets:
        if b not in seen:
            seen.add(b)
            result.append(b)
    return result


def _parse_two_column(text: str) -> dict:
    result: dict = {}
    left_match = re.search(
        r"\*\*Left\*\*\s*:\s*\n(.*?)(?=\*\*Right\*\*|\*\*Notes\*\*|\*\*Image\*\*|\*\*Animation\*\*|$)",
        text, re.DOTALL,
    )
    result["left_bullets"] = _extract_bullets(left_match.group(1)) if left_match else []
    right_match = re.search(
        r"\*\*Right\*\*\s*:\s*\n(.*?)(?=\*\*Notes\*\*|\*\*Image\*\*|\*\*Animation\*\*|$)",
        text, re.DOTALL,
    )
    result["right_bullets"] = _extract_bullets(right_match.group(1)) if right_match else []
    return result


def _parse_resource_boxes(text: str) -> list[dict]:
    """Parse ``**Box**: label`` sections followed by ``- name | url`` rows."""
    boxes = []
    for m in re.finditer(
        r"\*\*Box\*\*\s*:\s*(.+?)\n((?:\s*-\s+.+\n?)*)",
        text,
    ):
        label = m.group(1).strip()
        rows = []
        for row_m in re.finditer(r"^\s*-\s+(.+)", m.group(2), re.MULTILINE):
            parts = [p.strip() for p in row_m.group(1).split("|", 1)]
            name = parts[0]
            url = parts[1] if len(parts) > 1 else ""
            rows.append({"name": name, "url": url})
        boxes.append({"label": label, "rows": rows})
    return boxes


def _parse_image_field(text: str) -> dict | None:
    match = re.search(r"\*\*Image\*\*\s*:\s*(.+)", text)
    if not match:
        return None
    raw = match.group(1).strip()
    parts = [p.strip() for p in raw.split(",")]
    img: dict = {"path": parts[0]}
    if len(parts) >= 3:
        img["left"] = float(parts[1])
        img["top"] = float(parts[2])
    if len(parts) >= 5:
        img["width"] = float(parts[3])
        img["height"] = float(parts[4])
    return img


def _parse_image_prompt_field(text: str) -> dict | None:
    """Parse optional **ImagePrompt**: description [, left, top, width, height]."""
    match = re.search(r"\*\*ImagePrompt\*\*\s*:\s*(.+)", text)
    if not match:
        return None
    raw = match.group(1).strip()
    parts = [p.strip() for p in raw.split(",")]
    numeric_tail = []
    for p in reversed(parts):
        try:
            numeric_tail.insert(0, float(p))
        except ValueError:
            break
    desc_parts = parts[: len(parts) - len(numeric_tail)]
    prompt: dict = {"prompt": ", ".join(desc_parts)}
    if len(numeric_tail) >= 2:
        prompt["left"] = numeric_tail[0]
        prompt["top"] = numeric_tail[1]
    if len(numeric_tail) >= 4:
        prompt["width"] = numeric_tail[2]
        prompt["height"] = numeric_tail[3]

    model_match = re.search(r"\*\*ImageModel\*\*\s*:\s*(\S+)", text)
    if model_match:
        prompt["model"] = model_match.group(1).strip().lower()

    return prompt


def _parse_content_urls(text: str) -> list[str]:
    match = re.search(
        r"\*\*ContentUrls\*\*\s*:\s*\n((?:\s*-\s+\S+\n?)+)", text
    )
    if not match:
        return []
    urls = []
    for line in match.group(1).strip().splitlines():
        url = line.strip().lstrip("- ").strip()
        if url:
            urls.append(url)
    return urls
