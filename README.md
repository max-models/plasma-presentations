# plasma-presentations


<!-- README.md is generated from README.qmd: edit the .qmd and run `make readme`. -->

[![Tests](https://github.com/max-models/plasma-presentations/actions/workflows/test_pytest.yml/badge.svg)](https://github.com/max-models/plasma-presentations/actions/workflows/test_pytest.yml)
[![Static
analysis](https://github.com/max-models/plasma-presentations/actions/workflows/static_analysis.yml/badge.svg)](https://github.com/max-models/plasma-presentations/actions/workflows/static_analysis.yml)
[![Docs](https://github.com/max-models/plasma-presentations/actions/workflows/docs.yml/badge.svg)](https://max-models.github.io/plasma-presentations/)
[![codecov](https://codecov.io/gh/max-models/plasma-presentations/branch/main/graph/badge.svg)](https://codecov.io/gh/max-models/plasma-presentations)
[![PyPI](https://img.shields.io/pypi/v/plasma-presentations.png)](https://pypi.org/project/plasma-presentations/)
[![Python](https://img.shields.io/pypi/pyversions/plasma-presentations.png)](https://pypi.org/project/plasma-presentations/)

Talks written as [Quarto](https://quarto.org/docs/presentations/) slides
with the max-models look. One `.qmd` renders to HTML slides with
reveal.js (`plasma-revealjs`, with interactive plasma-plots figures) and
to a PDF with Beamer (`plasma-beamer`).

Documentation: <https://max-models.github.io/plasma-presentations/>

## Install

``` bash
pip install plasma-presentations
pip install "plasma-presentations[figures]"  # figures from plasma-plots
```

Rendering needs [Quarto](https://quarto.org/docs/get-started/) 1.4 or
newer, and the PDF a TeX distribution with lualatex and Beamer (TeX
Live, MacTeX, MiKTeX or `quarto install tinytex`).

## A first talk

``` bash
plasma-presentations new kickoff --title "Spokes in 3D" --author "Max Lindqvist"
plasma-presentations build kickoff/talk.qmd   # kickoff/talk.html and kickoff/talk.pdf
```

`new` writes a starter `talk.qmd` and the Quarto extension
(`_extensions/plasma`). The slides are plain Quarto Markdown; a figure
written with

``` python
from plasma_presentations import figure

figure(result, "kickoff/figures/growth")  # growth.json, growth.pdf, growth.png
```

is shown, interactive in HTML and as a PDF in Beamer, with

``` markdown
{{< plasma-figure figures/growth caption="The growth rate." >}}
```

## Development

With [uv](https://docs.astral.sh/uv/):

``` bash
make install    # uv sync --extra dev, plus the pre-commit hooks
make lint       # ruff check, ruff format --check, ssort, pyright
make test       # pytest with coverage
```

## Build docs

The documentation in `docs/` is an Astro + Starlight site with the
shared [starlight-theme](https://github.com/max-models/starlight-theme):
hand-written pages, the notebooks in `tutorials/` executed and published
as pages, the scripts in `examples/` with their figures, and the API
reference generated from the docstrings. It needs Node 22 or newer.

``` bash
make docs-install     # npm packages and the Python docs extra
make docs-notebooks   # execute tutorials/*.ipynb and convert them to pages
make docs-dev         # live preview at http://localhost:4321/plasma-presentations/
make docs-build       # the static site in docs/dist
```

## Releases

Before merging a release to `main`, update the version in
`pyproject.toml` and add the release notes to `CHANGELOG.md`. The push
to `main` creates a GitHub release with a `vX.Y.Z` tag and publishes the
package to PyPI with trusted publishing; the one-time setup is described
in the [publishing
guide](https://max-models.github.io/plasma-presentations/development/publishing/).
