"""Build the example script pages from Python scripts and their Matplotlib figures.

A script that sets ``SLIDES`` to the path of a rendered reveal.js talk (``talk.html``) also gets
its slides published next to its page and embedded in it.
"""

from __future__ import annotations

import ast
import json
import os
import re
import runpy
import shutil
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parents[1]

# The MDX escaping of the theme's notebook tool (installed with the npm packages)
sys.path.insert(
    0, str(DOCS / "node_modules" / "@max-models" / "starlight-theme" / "tools")
)
from notebooks import sanitize_markdown  # noqa: E402

ROOT = DOCS.parent
SOURCES = ROOT / "examples"
# the "Scripts" group of the Examples section, next to the notebook pages in examples/
CONTENT = DOCS / "src" / "content" / "docs" / "example-scripts"
PUBLIC = DOCS / "public" / "example-scripts"
# what of a talk's folder is not needed to show its HTML slides
NOT_SLIDES = shutil.ignore_patterns(
    "_extensions", ".quarto", "*.qmd", "*.tex", "page-*.png"
)


def source_fence(code: str) -> str:
    """Wrap the complete source without truncating long scripts."""
    ticks = "```"
    while ticks in code:
        ticks += "`"
    return f"{ticks}python\n{code.rstrip()}\n{ticks}"


def publish_slides(html: Path, output: Path, slug: str, title: str) -> list[str]:
    """Copy a rendered reveal.js talk into the site and return the page section showing it."""
    html = Path(html).resolve()
    if not html.is_file():
        raise FileNotFoundError(f"SLIDES is {html}, which does not exist")
    target = output / "slides"
    shutil.copytree(html.parent, target, ignore=NOT_SLIDES)
    url = f"/plasma-presentations/example-scripts/{slug}/slides/{html.name}"
    pdf = html.with_suffix(".pdf")
    links = f'<a href="{url}" target="_blank" rel="noopener">Open the slides in a new tab</a>'
    if (target / pdf.name).is_file():
        pdf_url = f"/plasma-presentations/example-scripts/{slug}/slides/{pdf.name}"
        links += f' · <a href="{pdf_url}">Download the PDF</a>'
    return [
        "## Slides",
        "",
        "The HTML slides this script renders, as built for this site. Click into them and use",
        "the arrow keys to move between slides, `F` for full screen and `Esc` for an overview.",
        "",
        f'<iframe src="{url}" title={json.dumps(title + ": slides")} loading="lazy" '
        "allowFullScreen style={{width: '100%', aspectRatio: '16 / 9', "
        "border: '1px solid var(--sl-color-gray-5)'}} />",
        "",
        f"<p>{links}</p>",
        "",
    ]


def build_example(source: Path, order: int) -> tuple[str, str]:
    """Run one script and publish its docstring, source, and open figures."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    slug = re.sub(r"[^a-z0-9]+", "-", source.stem.lower()).strip("-")
    code = source.read_text()
    docstring = ast.get_docstring(ast.parse(code))
    if not docstring:
        raise ValueError(f"{source}: a module docstring is required")
    title, _, description = docstring.partition("\n")
    # the first line is a sentence; the title drops its period
    title = title.strip().rstrip(".")
    description = description.strip()
    summary = description.split("\n\n", 1)[0].replace("\n", " ") or title
    output = PUBLIC / slug
    shutil.rmtree(output, ignore_errors=True)
    output.mkdir(parents=True)
    plt.close("all")
    previous = Path.cwd()
    try:
        os.chdir(source.parent)
        namespace = runpy.run_path(str(source), run_name="__main__")
    finally:
        os.chdir(previous)
    plots = []
    for index, number in enumerate(plt.get_fignums(), start=1):
        filename = f"plot-{index}.png"
        plt.figure(number).savefig(output / filename, dpi=150, bbox_inches="tight")
        plots.append(
            f"![Plot {index} from {title}](/plasma-presentations/example-scripts/{slug}/{filename})"
        )
    plt.close("all")
    slides = namespace.get("SLIDES")
    section = publish_slides(slides, output, slug, title) if slides else []
    page = [
        "---",
        f"title: {json.dumps(title)}",
        f"description: {json.dumps(summary)}",
        "sidebar:",
        f"  order: {order}",
        "---",
        "",
        sanitize_markdown(description) if description else "",
        "",
        *section,
        "## Python source",
        "",
        source_fence(code),
        "",
        "## Plots",
        "",
        "\n\n".join(plots) if plots else "This example does not produce plots.",
        "",
    ]
    CONTENT.mkdir(parents=True, exist_ok=True)
    (CONTENT / f"{slug}.mdx").write_text("\n".join(page))
    return title, summary


def main() -> None:
    """Regenerate all example script pages and assets."""
    shutil.rmtree(CONTENT, ignore_errors=True)
    shutil.rmtree(PUBLIC, ignore_errors=True)
    examples = sorted(SOURCES.glob("*.py"))
    listing = []
    for order, source in enumerate(examples, start=1):
        title, summary = build_example(source, order)
        slug = re.sub(r"[^a-z0-9]+", "-", source.stem.lower()).strip("-")
        listing.append(
            f"- [{title}](/plasma-presentations/example-scripts/{slug}/): {summary}"
        )
        print(f"[examples] {source} -> {CONTENT / slug}.mdx")
    CONTENT.mkdir(parents=True, exist_ok=True)
    (CONTENT / "index.md").write_text(
        "---\ntitle: Scripts\ndescription: Complete Python scripts and their plots.\n"
        "sidebar:\n  order: 0\n---\n\n"
        "Complete Python scripts are listed below. Each page shows the script and its plots.\n\n"
        + "\n".join(listing)
        + "\n"
    )


if __name__ == "__main__":
    main()
