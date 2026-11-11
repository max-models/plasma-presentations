# Changelog

All notable changes to this project are documented in this file and maintained manually. The
format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Fixed

- A folder of talks works: Quarto looks for an extension only up to the talk's project folder
  (the nearest `_quarto.yml`), so `install_extension` / `plasma-presentations install` now also
  write a `_quarto.yml` into the folder (unless it has one; `project=False` to skip), and
  `has_extension` follows Quarto's rule. Before, a talk in a subfolder failed with "Unable to
  read the extension 'plasma'".

### Added

- `quarto add max-models/plasma-presentations` installs the extension: a copy of it at the
  repository's root (`_extensions/plasma`), kept equal to the package's by `make extension` and a
  test. `render` also finds the extension where `quarto add` puts it
  (`_extensions/max-models/plasma`).
- The guides "Writing slides" and "Figures in slides" as notebooks; the quickstart links to them.

- The `plasma` Quarto extension (`_extensions/plasma`, shipped in the package): the formats
  `plasma-revealjs` (HTML slides with reveal.js: 16:9, slide numbers, MathJax, the plasma-plots
  accent colour) and `plasma-beamer` (a PDF with Beamer and lualatex, 16:9, the same colours),
  so one `.qmd` renders to both.
- The `plasma-figure` shortcode: `{{< plasma-figure figures/growth caption="..." >}}` shows
  `growth.json` as an interactive Plotly figure in HTML (inlined, drawn when its slide is first
  shown) and `growth.pdf` (else `.png`) in Beamer and other formats.
- `figure(result, "figures/growth")`: writes a plasma-plots result, a Plotly figure or a
  Matplotlib figure as `.json`, `.pdf` and `.png` for the shortcode; Plotly images at slide size
  with a 22 px font.
- `new_talk`, `install_extension`, `render` and `find_quarto`, and the command
  `plasma-presentations new | build | install`; rendering is the opt-in scope-profiler region
  `plasma_presentations.render`.
- Docs: installation, quickstart and the "First talk" example, rendered to HTML and PDF.

## [0.1.0] - 2026-10-05

### Added

- Package layout with a console entry point and pytest tests.
- Astro + Starlight documentation site with executed tutorials and a generated API reference.
- GitHub Actions for tests, ruff, pyright, tutorials, documentation and PyPI publishing.
