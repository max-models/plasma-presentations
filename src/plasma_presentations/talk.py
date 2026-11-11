"""Talks written as Quarto slides with the max-models look.

A talk is a ``.qmd`` file next to the ``plasma`` Quarto extension (``_extensions/plasma``),
which gives two formats: ``plasma-revealjs`` (HTML slides) and ``plasma-beamer`` (a PDF with
Beamer), and the ``plasma-figure`` shortcode for figures written by :func:`figure`.

>>> qmd = new_talk("kickoff", title="Spokes in 3D")  # doctest: +SKIP
>>> render(qmd)  # doctest: +SKIP
[PosixPath('kickoff/talk.html'), PosixPath('kickoff/talk.pdf')]
"""

from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
from importlib import resources
from pathlib import Path

import scope_profiler as sp

from plasma_presentations._profiling import PROFILE_TAGS

#: The output formats of :func:`render`, and the Quarto format each one uses.
FORMATS = {"html": "plasma-revealjs", "pdf": "plasma-beamer"}

#: The size in pixels of the images :func:`figure` draws of a Plotly figure: 80 % of a slide.
IMAGE_SIZE = (1280, 680)

#: The font size of those images, and of the figures in HTML slides, unless the figure sets one.
FONT_SIZE = 22

#: The name of the Quarto extension, in ``_extensions/<name>``.
EXTENSION = "plasma"


def _data(name: str) -> Path:
    """A file or folder shipped in the package."""
    return Path(str(resources.files("plasma_presentations").joinpath(name)))


def _front_matter(
    title: str, subtitle: str, author: str, institute: str, date: str
) -> str:
    """The YAML header of a talk, with both formats."""
    lines = ["---", f"title: {json.dumps(title)}"]
    if subtitle:
        lines.append(f"subtitle: {json.dumps(subtitle)}")
    if author:
        lines.append(f"author: {json.dumps(author)}")
    if institute:
        lines.append(f"institute: {json.dumps(institute)}")
    lines += [
        f"date: {json.dumps(date)}",
        "format:",
        "  plasma-revealjs: default",
        "  plasma-beamer: default",
        "---",
        "",
    ]
    return "\n".join(lines)


def install_extension(folder: str | Path, overwrite: bool = True) -> Path:
    """Copy the ``plasma`` Quarto extension into a folder of talks.

    Quarto finds the extension in ``_extensions/plasma`` next to a talk or in a folder above
    it, so one copy serves every talk below ``folder``.

    Args:
        folder: The folder to copy it into, created if missing.
        overwrite: Replace an existing copy, e.g. to update it to this version of the package.

    Returns:
        The extension's folder, ``folder/_extensions/plasma``.

    Raises:
        FileExistsError: If the extension is there and ``overwrite`` is False.
    """
    target = Path(folder) / "_extensions" / EXTENSION
    if target.exists():
        if not overwrite:
            raise FileExistsError(f"{target} exists; pass overwrite=True to replace it")
        shutil.rmtree(target)
    shutil.copytree(_data(f"_extensions/{EXTENSION}"), target)
    return target


def new_talk(
    folder: str | Path,
    title: str = "Title of the talk",
    *,
    subtitle: str = "",
    author: str = "",
    institute: str = "",
    date: str = "today",
    name: str = "talk.qmd",
) -> Path:
    """Start a talk: a starter ``.qmd`` and the ``plasma`` extension in a new folder.

    Args:
        folder: The folder of the talk; it must be empty or not exist yet.
        title: The talk's title.
        subtitle: A subtitle below it; empty for none.
        author: The speaker, or several as one line; empty for none.
        institute: The speaker's institute; empty for none.
        date: The date on the title slide; ``"today"`` is the day it is rendered.
        name: The file name of the talk.

    Returns:
        The path of the ``.qmd`` file.

    Raises:
        FileExistsError: If the folder exists and is not empty.
    """
    folder = Path(folder)
    if folder.exists() and any(folder.iterdir()):
        raise FileExistsError(f"{folder} is not empty")
    folder.mkdir(parents=True, exist_ok=True)
    install_extension(folder)
    body = _data("templates/talk.qmd").read_text()
    qmd = folder / name
    qmd.write_text(_front_matter(title, subtitle, author, institute, date) + body)
    return qmd


def find_quarto() -> str:
    """The Quarto program: ``$QUARTO_PATH``, else ``quarto`` on the ``PATH``.

    Returns:
        The path of the ``quarto`` executable.

    Raises:
        FileNotFoundError: If Quarto is not installed.
    """
    configured = os.environ.get("QUARTO_PATH")
    if configured:
        if not Path(configured).is_file():
            raise FileNotFoundError(
                f"QUARTO_PATH is {configured!r}, which is not a file"
            )
        return configured
    quarto = shutil.which("quarto")
    if quarto is None:
        raise FileNotFoundError(
            "quarto is not installed: see https://quarto.org/docs/get-started/ "
            "(the PDF also needs a TeX distribution with lualatex and beamer)"
        )
    return quarto


def has_extension(qmd: str | Path) -> bool:
    """Whether Quarto finds the ``plasma`` extension for a talk.

    Args:
        qmd: The talk's ``.qmd`` file.

    Returns:
        True if ``_extensions/plasma`` is next to the talk or in a folder above it.
    """
    folder = Path(qmd).resolve().parent
    return any(
        (parent / "_extensions" / EXTENSION / "_extension.yml").is_file()
        for parent in (folder, *folder.parents)
    )


@sp.profile("plasma_presentations.render", tags=PROFILE_TAGS)
def render(qmd: str | Path, to: str = "all") -> list[Path]:
    """Render a talk to HTML slides, a Beamer PDF or both, with Quarto.

    Args:
        qmd: The talk's ``.qmd`` file.
        to: ``"html"`` (``plasma-revealjs``), ``"pdf"`` (``plasma-beamer``) or ``"all"``.

    Returns:
        The files written, next to the talk.

    Raises:
        ValueError: If ``to`` is not one of the formats.
        FileNotFoundError: If the talk, the extension or Quarto is missing.
        RuntimeError: If Quarto fails; the message ends with the end of its output.
    """
    if to != "all" and to not in FORMATS:
        raise ValueError(f"to must be 'all' or one of {sorted(FORMATS)}, not {to!r}")
    qmd = Path(qmd).resolve()
    if not qmd.is_file():
        raise FileNotFoundError(f"{qmd} does not exist")
    if not has_extension(qmd):
        raise FileNotFoundError(
            f"no _extensions/{EXTENSION} next to {qmd.name} or above it: run "
            f"`plasma-presentations install {qmd.parent}`"
        )
    quarto = find_quarto()
    written = []
    for suffix in FORMATS if to == "all" else [to]:
        result = subprocess.run(
            [quarto, "render", qmd.name, "--to", FORMATS[suffix]],
            cwd=qmd.parent,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            log = "\n".join((result.stdout + result.stderr).splitlines()[-30:])
            raise RuntimeError(f"quarto failed on {qmd} ({FORMATS[suffix]}):\n{log}")
        written.append(qmd.with_suffix(f".{suffix}"))
    return written


def _to_plotly(result, matplotlib_figure):
    """The Plotly figure of a Matplotlib figure or result, by plasma-plots' conversion."""
    if hasattr(result, "to_plotly"):
        return result.to_plotly().fig
    from plasma_plots.plotly_backend import to_plotly

    return to_plotly(matplotlib_figure)


def figure(result, path: str | Path, *, dpi: int = 200) -> list[Path]:
    """Write a figure for the ``plasma-figure`` shortcode of a talk.

    Writes ``<path>.json`` (the interactive Plotly figure, for HTML slides), ``<path>.pdf``
    (for Beamer) and ``<path>.png``. ``result`` can be a plasma-plots ``PlotResult``, a Plotly
    figure or a Matplotlib figure; a Matplotlib figure gets its JSON from plasma-plots'
    conversion to Plotly (``PlotResult.to_plotly``), so it needs plasma-plots with Plotly.
    The images of a Plotly figure are drawn by kaleido at :data:`IMAGE_SIZE`, with
    :data:`FONT_SIZE` unless the figure sets its font size.

    Args:
        result: The figure.
        path: The files' path without suffix, e.g. ``"figures/growth"``, relative to the
            current folder; show them with ``{{< plasma-figure figures/growth >}}`` in a talk
            in that folder.
        dpi: The resolution of the PNG.

    Returns:
        The files written: the JSON, the PDF and the PNG.

    Raises:
        TypeError: If ``result`` is none of the figure types.
    """
    stem = Path(path)
    stem.parent.mkdir(parents=True, exist_ok=True)
    files = [stem.with_name(stem.name + suffix) for suffix in (".json", ".pdf", ".png")]
    figure_ = getattr(result, "fig", result)  # a PlotResult holds its figure in .fig
    if hasattr(figure_, "write_json"):  # Plotly
        figure_.write_json(files[0])
        image = copy.deepcopy(figure_)
        if image.layout.font.size is None:  # Plotly's 12 px is too small on a slide
            image.update_layout(font_size=FONT_SIZE)
        width, height = IMAGE_SIZE
        image.write_image(files[1], width=width, height=height)
        image.write_image(files[2], width=width, height=height, scale=dpi / 100)
    elif hasattr(figure_, "savefig"):  # Matplotlib
        figure_.savefig(files[1], bbox_inches="tight")
        figure_.savefig(files[2], dpi=dpi, bbox_inches="tight")
        _to_plotly(result, figure_).write_json(files[0])
    else:
        raise TypeError(
            "result must be a plasma-plots PlotResult, a Plotly figure or a Matplotlib "
            f"figure, not {type(result).__name__}"
        )
    return files
