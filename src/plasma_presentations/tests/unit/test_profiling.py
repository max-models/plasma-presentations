"""The opt-in scope-profiler regions: off unless the application enables the tag."""

from __future__ import annotations

import subprocess

import pytest
import scope_profiler as sp

from plasma_presentations import new_talk, render


@pytest.fixture(autouse=True)
def _fresh_profiler(monkeypatch):
    """Keep the profiling state of these tests out of the others."""
    monkeypatch.delenv("SCOPE_PROFILER_ENABLE_TAGS", raising=False)
    sp.reset()
    yield
    sp.reset()


@pytest.fixture
def _fake_quarto(monkeypatch):
    """A Quarto that succeeds without running."""
    monkeypatch.delenv("QUARTO_PATH", raising=False)
    monkeypatch.setattr("shutil.which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(
        subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 0, "", "")
    )


def _region_names(tmp_path, **setup_kwargs) -> set[str]:
    qmd = new_talk(tmp_path / "talk")
    sp.setup(output=None, **setup_kwargs)
    # an application region, recorded either way
    with sp.region("user.run"):
        render(qmd, "html")
    results = sp.finalize(verbose=False, return_results=True)
    return set(results.region_names)


@pytest.mark.usefixtures("_fake_quarto")
def test_regions_are_off_by_default(tmp_path) -> None:
    assert _region_names(tmp_path) == {"user.run"}


@pytest.mark.usefixtures("_fake_quarto")
@pytest.mark.parametrize("tags", [["plasma_presentations"], ["*"]])
def test_enabling_the_tag_records_the_regions(tmp_path, tags: list[str]) -> None:
    assert _region_names(tmp_path, enable_tags=tags) == {
        "plasma_presentations.render",
        "user.run",
    }
