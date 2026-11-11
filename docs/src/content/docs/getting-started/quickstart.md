---
title: Quickstart
description: Start a talk, write slides in Quarto Markdown and render them to HTML and PDF.
---

First, ensure that `plasma-presentations`, Quarto and a TeX distribution are
[installed](/plasma-presentations/getting-started/installation/).

## Start a talk

```bash
plasma-presentations new kickoff --title "Spokes in 3D" --author "Max Lindqvist"
```

writes `kickoff/talk.qmd`, a starter talk, and `kickoff/_extensions/plasma`, the Quarto
extension with the max-models look. The talk's header picks both of its formats:

```yaml
---
title: "Spokes in 3D"
author: "Max Lindqvist"
date: "today"
format:
  plasma-revealjs: default
  plasma-beamer: default
---
```

## Write slides

The slides are plain [Quarto Markdown](https://quarto.org/docs/presentations/): `##` starts a
slide, `#` a section, and lists, maths, columns and incremental lists work in both formats.
The guide [Writing slides](/plasma-presentations/examples/writing-slides/) goes through them.

## Render

```bash
plasma-presentations build kickoff/talk.qmd            # talk.html and talk.pdf
plasma-presentations build kickoff/talk.qmd --to html  # only the reveal.js slides
```

`plasma-revealjs` writes HTML slides with reveal.js (16:9, slide numbers, MathJax) and
`plasma-beamer` a PDF with Beamer and lualatex. `quarto preview kickoff/talk.qmd` reloads the
slides in the browser while you write.

## Figures

`figure(result, "kickoff/figures/growth")` writes a plasma-plots, Plotly or Matplotlib figure
for a talk, and `{{< plasma-figure figures/growth caption="..." >}}` shows it: interactive in
HTML, a PDF in Beamer. See [Figures in slides](/plasma-presentations/examples/figures-in-slides/);
`figure` needs the `figures` extra: `pip install "plasma-presentations[figures]"`.

## More talks in one folder

Quarto finds `_extensions/plasma` next to a talk or in any folder above it, so a folder of talks
needs one copy. `plasma-presentations install talks/` copies it there, or updates it after an
upgrade of the package. Without Python, Quarto installs the extension from GitHub:

```bash
cd talks
quarto add max-models/plasma-presentations
```

## From Python

```python
from plasma_presentations import new_talk, render

qmd = new_talk("kickoff", "Spokes in 3D", author="Max Lindqvist")
render(qmd)  # [kickoff/talk.html, kickoff/talk.pdf]
```

See the [examples](/plasma-presentations/examples/) and the
[API reference](/plasma-presentations/api/plasma_presentations/).

## Profiling

Rendering is a [scope-profiler](https://github.com/max-models/scope-profiler) region,
`plasma_presentations.render`, with the opt-in tag `plasma_presentations`: off by default, and
turned on with `sp.setup(enable_tags=["plasma_presentations"])`,
`SCOPE_PROFILER_ENABLE_TAGS=plasma_presentations` or
`scope-profiler run --enable-tag plasma_presentations`.
