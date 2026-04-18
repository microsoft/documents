---
title: Example Document
subtitle: Generated with SpecKit Document Generator
output: Example_Document.docx
author: SpecKit
text_model: gpt-4o-mini
image_model: gpt-image-1.5
style:
  title_font_size: 28
  subtitle_font_size: 16
  body_font_size: 11
  heading_font_size: 18
  heading_color: '#1F2937'
  accent_color: '#0078D4'
---

## [title] SpecKit Document Generator

**Subtitle**: Build Word documents from markdown specs<br>Powered by Azure AI

**Notes**: This is an example document demonstrating the SpecKit document generator capabilities.

---

## [content] Key Features

- Parse `.spec.md` files with YAML front matter and markdown sections
- Generate professional Word documents with consistent formatting
- AI-powered content enrichment via Azure OpenAI
- AI-generated images via Azure AI image endpoint
- Versioned output — each build creates a new file
- Enrichment caching — results are saved back to the spec file

**Notes**: The document generator supports five section types: title, content, section-header, two-column, and resource-box.

---

## [section-header] Architecture Overview

**Subtitle**: How the document generator works

**Notes**: The generator follows a pipeline: parse spec → enrich content → generate images → build document sections → save .docx file.

---

## [two-column] Input vs Output

**Left**:
- Markdown `.spec.md` files
- YAML front matter for metadata
- Section blocks separated by `---`
- Directive-based images and enrichment
- Plain text bullets and notes

**Right**:
- Professional `.docx` Word documents
- Styled headings and body text
- Tables for two-column layouts
- Embedded AI-generated images
- Consistent formatting throughout

**Notes**: The spec file format is identical to the presentations generator, making it easy to reuse content across both formats.

---

## [content] Getting Started

- Install dependencies: `pip install -r requirements.txt`
- Create a `.spec.md` file in `.speckit/specifications/`
- Run: `python documents.py .speckit/specifications/your_doc.spec.md`
- Find the generated `.docx` in the `output/` directory

**Notes**: For AI features (content enrichment and image generation), you need Azure AI Foundry resources. Run `azd up` to provision them.

---

## [resource-box] Useful Resources

**Subtitle**: Links and documentation

**Box**: Documentation
- python-docx Library | https://python-docx.readthedocs.io/
- Azure AI Services | https://learn.microsoft.com/azure/ai-services/
- Azure Developer CLI | https://learn.microsoft.com/azure/developer/azure-developer-cli/

**Box**: Source Code
- Document Generator | https://github.com/microsoft/documents
- Presentation Generator | https://github.com/microsoft/presentations

**Notes**: These resources provide additional context for using and extending the document generator.
