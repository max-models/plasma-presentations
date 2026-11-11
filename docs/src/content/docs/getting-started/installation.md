---
title: Installation
description: Install plasma-presentations, Quarto and a TeX distribution.
---

Install the package with pip:

```bash
pip install plasma-presentations
# with figures from plasma-plots:
pip install "plasma-presentations[figures]"
```

Rendering needs [Quarto](https://quarto.org/docs/get-started/) 1.4 or newer on the `PATH` (or
its path in `QUARTO_PATH`). The PDF slides also need a TeX distribution with lualatex and Beamer:
TeX Live, MacTeX or MiKTeX, or `quarto install tinytex`.

## Optional extras

| Extra     | Installs                                                  |
| --------- | --------------------------------------------------------- |
| `figures` | plasma-plots with Plotly and kaleido, for `figure`        |
| `test`    | `pytest` and `coverage`                                   |
| `docs`    | the notebook runner and griffe for the API reference      |
| `dev`     | formatters and linters, plus the `test` and `docs` extras |
