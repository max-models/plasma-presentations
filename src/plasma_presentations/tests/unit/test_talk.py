"""Starting, rendering and illustrating talks."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from plasma_presentations import (
    figure,
    find_quarto,
    has_extension,
    install_extension,
    new_talk,
    render,
)
from plasma_presentations.main import main

EXTENSION_FILES = {
    "_extension.yml",
    "plasma.scss",
    "plasma-beamer.tex",
    "plasma-figure.lua",
    "plasma-revealjs.html",
}


class _Runs:
    """A stand-in for subprocess.run that records the commands."""

    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = ""):
        self.calls: list[tuple[list[str], Path]] = []
        self.result = (returncode, stdout, stderr)

    def __call__(self, command, cwd=None, **kwargs):
        self.calls.append((command, Path(cwd)))
        return subprocess.CompletedProcess(command, *self.result)


@pytest.fixture
def fake_quarto(monkeypatch):
    monkeypatch.delenv("QUARTO_PATH", raising=False)
    monkeypatch.setattr("shutil.which", lambda name: f"/usr/bin/{name}")
    runs = _Runs()
    monkeypatch.setattr(subprocess, "run", runs)
    return runs


def test_new_talk_writes_the_talk_and_the_extension(tmp_path):
    qmd = new_talk(
        tmp_path / "kickoff",
        "Spokes in 3D",
        subtitle="Kickoff",
        author="Max Lindqvist",
        institute="IPP",
        date="2026-12-04",
    )
    assert qmd == tmp_path / "kickoff" / "talk.qmd"
    text = qmd.read_text()
    assert text.startswith('---\ntitle: "Spokes in 3D"\nsubtitle: "Kickoff"\n')
    assert 'author: "Max Lindqvist"' in text
    assert 'institute: "IPP"' in text
    assert 'date: "2026-12-04"' in text
    assert "  plasma-revealjs: default\n  plasma-beamer: default\n---\n" in text
    assert "## Motivation" in text
    extension = tmp_path / "kickoff" / "_extensions" / "plasma"
    assert {path.name for path in extension.iterdir()} == EXTENSION_FILES
    assert has_extension(qmd)


def test_new_talk_leaves_out_empty_fields(tmp_path):
    text = new_talk(tmp_path / "talk").read_text()
    assert "subtitle" not in text and "author" not in text and "institute" not in text
    assert 'date: "today"' in text


def test_a_title_with_quotes_and_colons_stays_valid_yaml(tmp_path):
    text = new_talk(tmp_path / "talk", 'Ions: "fast" ones').read_text()
    assert 'title: "Ions: \\"fast\\" ones"' in text


def test_new_talk_refuses_a_folder_that_is_not_empty(tmp_path):
    (tmp_path / "notes.txt").write_text("keep me")
    with pytest.raises(FileExistsError, match="not empty"):
        new_talk(tmp_path)


def test_new_talk_accepts_an_empty_folder(tmp_path):
    assert new_talk(tmp_path, name="kickoff.qmd").name == "kickoff.qmd"


def test_install_extension_updates_or_refuses(tmp_path):
    target = install_extension(tmp_path)
    (target / "plasma.scss").write_text("old")
    with pytest.raises(FileExistsError, match="overwrite"):
        install_extension(tmp_path, overwrite=False)
    install_extension(tmp_path)
    assert (target / "plasma.scss").read_text() != "old"


def test_a_talk_below_the_extension_finds_it(tmp_path):
    install_extension(tmp_path)
    (tmp_path / "talks" / "a").mkdir(parents=True)
    assert has_extension(tmp_path / "talks" / "a" / "talk.qmd")
    assert not has_extension(tmp_path.parent / "elsewhere" / "talk.qmd")


def test_render_runs_quarto_once_per_format(tmp_path, fake_quarto):
    qmd = new_talk(tmp_path / "talk")
    assert render(qmd) == [qmd.with_suffix(".html"), qmd.with_suffix(".pdf")]
    assert fake_quarto.calls == [
        (
            ["/usr/bin/quarto", "render", "talk.qmd", "--to", "plasma-revealjs"],
            qmd.parent,
        ),
        (
            ["/usr/bin/quarto", "render", "talk.qmd", "--to", "plasma-beamer"],
            qmd.parent,
        ),
    ]


def test_render_one_format(tmp_path, fake_quarto):
    qmd = new_talk(tmp_path / "talk")
    assert render(qmd, "pdf") == [qmd.with_suffix(".pdf")]
    assert len(fake_quarto.calls) == 1


def test_render_rejects_an_unknown_format(tmp_path):
    with pytest.raises(ValueError, match="to must be"):
        render(tmp_path / "talk.qmd", "pptx")


def test_render_needs_the_talk(tmp_path):
    with pytest.raises(FileNotFoundError, match="does not exist"):
        render(tmp_path / "talk.qmd")


def test_render_needs_the_extension(tmp_path):
    qmd = tmp_path / "talk.qmd"
    qmd.write_text("---\ntitle: x\n---\n")
    with pytest.raises(FileNotFoundError, match="plasma-presentations install"):
        render(qmd)


def test_render_reports_the_end_of_quartos_output(tmp_path, monkeypatch):
    qmd = new_talk(tmp_path / "talk")
    monkeypatch.delenv("QUARTO_PATH", raising=False)
    monkeypatch.setattr("shutil.which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(
        subprocess, "run", _Runs(1, "rendering\n", "ERROR: no lualatex")
    )
    with pytest.raises(RuntimeError, match="no lualatex"):
        render(qmd, "pdf")


def test_find_quarto_reports_a_missing_quarto(monkeypatch):
    monkeypatch.delenv("QUARTO_PATH", raising=False)
    monkeypatch.setattr("shutil.which", lambda name: None)
    with pytest.raises(FileNotFoundError, match="quarto is not installed"):
        find_quarto()


def test_find_quarto_takes_quarto_path(tmp_path, monkeypatch):
    program = tmp_path / "quarto"
    program.write_text("")
    monkeypatch.setenv("QUARTO_PATH", str(program))
    assert find_quarto() == str(program)
    monkeypatch.setenv("QUARTO_PATH", str(tmp_path / "missing"))
    with pytest.raises(FileNotFoundError, match="not a file"):
        find_quarto()


class _PlotlyFigure:
    """Records what a Plotly figure is asked to write; copies share the record."""

    def __init__(self, font_size=None):
        self.images = []
        self.layout = SimpleNamespace(font=SimpleNamespace(size=font_size))

    def __deepcopy__(self, memo):
        copied = _PlotlyFigure(self.layout.font.size)
        copied.images = self.images
        return copied

    def update_layout(self, font_size):
        self.layout.font.size = font_size

    def write_json(self, path):
        Path(path).write_text(json.dumps({"data": [], "layout": {}}))

    def write_image(self, path, **kwargs):
        Path(path).write_bytes(b"image")
        self.images.append((Path(path).suffix, self.layout.font.size, kwargs))


def test_figure_of_a_plotly_figure(tmp_path):
    fig = _PlotlyFigure()
    files = figure(fig, tmp_path / "figures" / "growth", dpi=300)
    assert [path.name for path in files] == ["growth.json", "growth.pdf", "growth.png"]
    assert all(path.is_file() for path in files)
    size = {"width": 1280, "height": 680}
    assert fig.images == [(".pdf", 22, size), (".png", 22, {**size, "scale": 3.0})]
    assert fig.layout.font.size is None  # the figure itself is left as it is


def test_figure_keeps_a_font_size_of_its_own(tmp_path):
    fig = _PlotlyFigure(font_size=30)
    figure(fig, tmp_path / "growth")
    assert [font for _, font, _ in fig.images] == [30, 30]


def test_figure_of_a_plot_result_uses_its_figure(tmp_path):
    class Result:
        fig = _PlotlyFigure()

    files = figure(Result(), tmp_path / "growth")
    assert json.loads(files[0].read_text()) == {"data": [], "layout": {}}


def test_figure_of_a_matplotlib_figure(tmp_path):
    plt = pytest.importorskip("matplotlib.pyplot")
    pytest.importorskip("plasma_plots.plotly_backend")
    fig, ax = plt.subplots()
    ax.plot([0, 1, 2], [0, 1, 4], label="growth")
    ax.set(xlabel="t", ylabel="E")
    files = figure(fig, tmp_path / "growth")
    plt.close(fig)
    assert files[1].read_bytes().startswith(b"%PDF")
    assert files[2].read_bytes().startswith(b"\x89PNG")
    (trace,) = json.loads(files[0].read_text())["data"]
    assert trace["type"] == "scatter" and trace["name"] == "growth"


def test_figure_of_a_matplotlib_plot_result_converts_it(tmp_path):
    class Fig:
        def savefig(self, path, **kwargs):
            Path(path).write_bytes(b"image")

    class Converted:
        fig = _PlotlyFigure()

    class Result:
        fig = Fig()

        def to_plotly(self):
            return Converted()

    files = figure(Result(), tmp_path / "growth")
    assert json.loads(files[0].read_text()) == {"data": [], "layout": {}}


def test_figure_rejects_other_objects(tmp_path):
    with pytest.raises(TypeError, match="PlotResult"):
        figure(object(), tmp_path / "growth")


def test_cli_new_install_and_build(tmp_path, fake_quarto, capsys):
    folder = tmp_path / "kickoff"
    assert main(["new", str(folder), "--title", "Kickoff", "--author", "Max"]) == 0
    assert 'title: "Kickoff"' in (folder / "talk.qmd").read_text()
    assert main(["install", str(tmp_path / "talks")]) == 0
    assert (tmp_path / "talks" / "_extensions" / "plasma" / "_extension.yml").is_file()
    assert main(["build", str(folder / "talk.qmd"), "--to", "html"]) == 0
    output = capsys.readouterr().out
    assert "talk.qmd" in output and "talk.html" in output and "_extensions" in output


QUARTO = shutil.which("quarto")


@pytest.mark.skipif(QUARTO is None, reason="needs Quarto")
def test_render_html_with_quarto(tmp_path, monkeypatch):
    qmd = new_talk(tmp_path / "talk", "A talk")
    figures = qmd.parent / "figures"
    figures.mkdir()
    (figures / "line.json").write_text(
        json.dumps({"data": [{"type": "scatter", "y": [1, 3, 2]}], "layout": {}})
    )
    with qmd.open("a") as file:
        file.write(
            '\n## A figure\n\n{{< plasma-figure figures/line caption="A line" >}}\n'
        )
    (html,) = render(qmd, "html")
    page = html.read_text()
    assert "plasma-figure-plot" in page
    assert "plotly.min.js" in page
    assert "A line" in page


@pytest.mark.skipif(
    QUARTO is None or shutil.which("lualatex") is None,
    reason="needs Quarto and lualatex",
)
def test_render_pdf_with_quarto(tmp_path):
    plt = pytest.importorskip("matplotlib.pyplot")
    qmd = new_talk(tmp_path / "talk", "A talk")
    fig, ax = plt.subplots()
    ax.plot([0, 1], [1, 0])
    fig.savefig(qmd.parent / "line.pdf")
    plt.close(fig)
    with qmd.open("a") as file:
        file.write(
            '\n## A figure\n\n{{< plasma-figure line caption="A $\\\\gamma$ line" >}}\n'
        )
    (pdf,) = render(qmd, "pdf")
    assert pdf.read_bytes().startswith(b"%PDF")
    tex = qmd.with_suffix(".tex")
    assert not tex.exists() or "line.pdf" in tex.read_text()
