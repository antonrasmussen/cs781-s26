#!/usr/bin/env python3
# Historical milestone build tool (April 2026).
# This script was used to convert project_update.md (a milestone progress document)
# to a professionally styled PDF for submission. The input file project_update.md no
# longer exists in the repository; milestone documents are preserved in
# docs/archive/milestones/. This script is retained as a reference build tool.
# Running it as-is will raise FileNotFoundError because the input file is absent.
"""Convert project_update.md to a professionally styled PDF."""

import markdown
import weasyprint
import os

MD_FILE = os.path.join(os.path.dirname(__file__), "project_update.md")
OUT_FILE = os.path.join(os.path.dirname(__file__), "project_update.pdf")

CSS = """
@page {
    size: letter;
    margin: 1in 1in 0.9in 1in;
    @bottom-center {
        content: counter(page);
        font-size: 9pt;
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
        color: #888;
    }
}

@page :first {
    @bottom-center { content: none; }
}

body {
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.45;
    color: #1a1a1a;
    orphans: 3;
    widows: 3;
}

.title-block {
    text-align: center;
    margin-bottom: 20pt;
    padding-bottom: 14pt;
    border-bottom: 2px solid #333;
}

.title-block h1 {
    font-size: 18pt;
    font-weight: 700;
    margin: 0 0 4pt 0;
    color: #000;
    letter-spacing: 0.5pt;
}

.title-block h2 {
    font-size: 14pt;
    font-weight: 400;
    margin: 0 0 10pt 0;
    color: #333;
    border-bottom: none;
}

.title-block .author {
    font-size: 12pt;
    font-weight: 600;
    margin: 0;
}

.title-block .meta {
    font-size: 10.5pt;
    color: #444;
    margin: 2pt 0 0 0;
}

.project-title {
    text-align: center;
    margin: 18pt 0 24pt 0;
    padding: 0 20pt;
}

.project-title p {
    font-size: 13pt;
    font-weight: 600;
    line-height: 1.4;
    color: #111;
    text-align: center;
}

h1 {
    font-size: 14pt;
    font-weight: 700;
    margin-top: 22pt;
    margin-bottom: 8pt;
    color: #000;
    border-bottom: 1px solid #ccc;
    padding-bottom: 4pt;
    page-break-after: avoid;
}

h2 {
    font-size: 12pt;
    font-weight: 700;
    margin-top: 16pt;
    margin-bottom: 6pt;
    color: #111;
    page-break-after: avoid;
}

h3 {
    font-size: 11pt;
    font-weight: 700;
    margin-top: 12pt;
    margin-bottom: 4pt;
    color: #222;
    page-break-after: avoid;
}

p {
    margin-top: 0;
    margin-bottom: 7pt;
    text-align: justify;
    hyphens: auto;
}

strong {
    font-weight: 700;
}

em {
    font-style: italic;
}

hr {
    display: none;
}

ol, ul {
    margin-top: 4pt;
    margin-bottom: 7pt;
    padding-left: 22pt;
}

li {
    margin-bottom: 3pt;
}

li > ul, li > ol {
    margin-top: 2pt;
    margin-bottom: 2pt;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin-top: 8pt;
    margin-bottom: 8pt;
    font-size: 9pt;
    page-break-inside: avoid;
}

thead th {
    background-color: #f0f0f0;
    font-weight: 700;
    text-align: left;
    padding: 4pt 5pt;
    border: 1px solid #aaa;
}

td {
    padding: 3pt 5pt;
    border: 1px solid #bbb;
    vertical-align: top;
}

img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 8pt 0;
}

tr:nth-child(even) {
    background-color: #fafafa;
}

blockquote {
    border-left: 3pt solid #ccc;
    margin-left: 0;
    padding-left: 12pt;
    color: #444;
}

code {
    font-family: "Courier New", Courier, monospace;
    font-size: 10pt;
    background-color: #f4f4f4;
    padding: 1pt 3pt;
    border-radius: 2pt;
}

pre {
    font-family: "Courier New", Courier, monospace;
    font-size: 9.5pt;
    background-color: #f4f4f4;
    padding: 8pt 10pt;
    border: 1px solid #ddd;
    border-radius: 3pt;
    page-break-inside: avoid;
}
"""

def build_html(md_text: str) -> str:
    lines = md_text.split("\n")

    title_block_end = 0
    for i, line in enumerate(lines):
        if line.strip() == "---":
            title_block_end = i
            break

    # Validate that a title block delimiter was found and that it follows
    # at least one non-empty title line. Otherwise, rendering would produce
    # an empty or misleading title block.
    if title_block_end == 0:
        raise ValueError(
            "Expected a '---' delimiter separating the title block from the body "
            "in project_update.md, but none was found."
        )
    if not any(line.strip() for line in lines[:title_block_end]):
        raise ValueError(
            "Found a '---' delimiter for the title block, but there are no "
            "non-empty title lines before it."
        )
    title_lines = lines[:title_block_end]
    body_lines = lines[title_block_end:]

    course = ""
    subtitle = ""
    author = ""
    meta_parts = []
    for line in title_lines:
        stripped = line.strip()
        if stripped.startswith("# ") and not course:
            course = stripped[2:]
        elif stripped.startswith("## "):
            subtitle = stripped[3:]
        elif stripped.startswith("**") and stripped.endswith("**"):
            author = stripped[2:-2]
        elif stripped and not stripped.startswith("#"):
            meta_parts.append(stripped)

    meta = " | ".join(meta_parts) if meta_parts else ""

    project_title = ""
    clean_body = []
    i = 0
    while i < len(body_lines):
        line = body_lines[i]
        stripped = line.strip()
        if stripped == "# Project Title":
            if i + 2 < len(body_lines):
                next_line = body_lines[i + 1].strip()
                if not next_line:
                    bold_line = body_lines[i + 2].strip()
                    if bold_line.startswith("**") and bold_line.endswith("**"):
                        project_title = bold_line[2:-2]
                        i += 3
                        continue
            i += 1
            continue
        clean_body.append(body_lines[i])
        i += 1

    body_md = "\n".join(clean_body)

    extensions = ["tables", "fenced_code", "sane_lists"]
    body_html = markdown.markdown(body_md, extensions=extensions)

    title_html = f"""<div class="title-block">
    <h1>{course}</h1>
    <h2>{subtitle}</h2>
    <p class="author">{author}</p>
    <p class="meta">{meta}</p>
</div>"""

    project_title_html = ""
    if project_title:
        project_title_html = f"""<div class="project-title">
    <p>{project_title}</p>
</div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <style>{CSS}</style>
</head>
<body>
{title_html}
{project_title_html}
{body_html}
</body>
</html>"""


if __name__ == "__main__":
    with open(MD_FILE, "r", encoding="utf-8") as f:
        md_text = f.read()

    html = build_html(md_text)

    html_path = OUT_FILE.replace(".pdf", ".html")
    with open(html_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)

    doc = weasyprint.HTML(string=html, base_url=os.path.dirname(__file__))
    doc.write_pdf(OUT_FILE)
    print(f"PDF written to {OUT_FILE}")
