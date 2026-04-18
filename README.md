# Document Generator

Reads a `.spec.md` file and produces a Word document (`.docx`) with styled headings,
bullet lists, tables, images, AI-generated visuals, and AI-enriched content.

Adapted from [microsoft/presentations](https://github.com/microsoft/presentations) —
same spec format, Word output instead of PowerPoint.

## Prerequisites

- Python 3.10+ — [Download](https://www.python.org/downloads/)
- pip — included with Python; used to install dependencies
- Azure Developer CLI (`azd`) — required for provisioning Azure infrastructure ([Install](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd))
- Azure CLI (`az`) — run `az login` so `DefaultAzureCredential` can authenticate ([Install](https://learn.microsoft.com/cli/azure/install-azure-cli))

## Quick Start

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
python documents.py .speckit/specifications/example.spec.md
```

## Project Structure

```
documents.py              # thin wrapper – delegates to src/
src/
├── __init__.py           # package exports (main, render, parse_spec)
├── cli.py                # argparse CLI entry point
├── spec_parser.py        # .spec.md → metadata + section list
├── style.py              # Style class (font sizes from front-matter)
├── sections.py           # section builder functions (one per layout)
├── images.py             # image generation via Azure AI REST endpoint
├── enrichment.py         # ContentUrl fetching & note enrichment via Azure AI
├── renderer.py           # orchestrates parsing → enrichment → images → docx
└── spec_writer.py        # serialize enriched spec back to .spec.md
tests/
├── test_cli.py           # CLI argument parsing
├── test_renderer.py      # end-to-end render pipeline
├── test_sections.py      # section builder functions
├── test_spec_parser.py   # .spec.md parsing
├── test_spec_writer.py   # spec round-trip writing
└── test_style.py         # Style resolution from front-matter
```

## Features

- **Section types**: `title`, `content`, `section-header`, `two-column`, `resource-box`
- **Static images**: reference local files with `**Image**: path`
- **AI-generated images**: describe an image with `**ImagePrompt**` — generated via the Azure AI image endpoint and cached locally
- **ContentUrls & enrichment**: add `**ContentUrls**` per section to fetch reference content and auto-enrich both bullets and notes via Azure AI Inference
- **Enrichment caching**: enriched sections are written back to the spec file with `**Enriched**: true` so subsequent builds skip re-enrichment (override with `--refetch`)
- **Style from spec**: font sizes, colors configurable in the front-matter `style:` block
- **Versioned output**: each build creates a new versioned `.docx` so previous runs are never overwritten

## Spec File Format

Spec files use Markdown with YAML front matter:

```yaml
---
title: My Document
subtitle: A subtitle
output: My_Document.docx
text_model: gpt-4o-mini
image_model: gpt-image-1.5
style:
  title_font_size: 28
  body_font_size: 11
  heading_font_size: 18
  heading_color: '#1F2937'
  accent_color: '#0078D4'
---

## [title] My Title

**Subtitle**: Author name here

---

## [content] Section Title

- Bullet one
- Bullet two

**Image**: images/diagram.png
**ImagePrompt**: A futuristic cityscape at sunset

**ContentUrls**:
- https://learn.microsoft.com/azure/ai-services/openai/overview

**Notes**: Additional context for this section.
```

### Section Types

| Type | Description |
|------|-------------|
| `title` | Cover page with large centred title + subtitle |
| `content` | Heading + bullet list |
| `section-header` | Page break with prominent section heading |
| `two-column` | Side-by-side content via table (`**Left**:` / `**Right**:`) |
| `resource-box` | Labelled resource tables with name/URL rows |

## CLI Reference

```
python documents.py <spec-file> [options]

positional arguments:
  spec                  Path to the .spec.md file

options:
  -o, --output-dir DIR  Output directory (default: output)
  --image-model MODEL   Image generation model name (overrides front-matter)
  --refetch             Re-fetch and regenerate all AI enrichments
  --sections SELECTION  Section numbers to generate (1-indexed).
                        Examples: '5', '3-7', '1,3,5-8'. Default: all.
```

## Running Tests

```powershell
pip install pytest
pytest tests/ -v
```

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit [Contributor License Agreements](https://cla.opensource.microsoft.com).

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
