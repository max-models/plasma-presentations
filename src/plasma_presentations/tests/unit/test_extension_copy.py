"""The copy of the Quarto extension at the repository's root, which `quarto add` installs."""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]
PACKAGE = ROOT / "src" / "plasma_presentations" / "_extensions"
COPY = ROOT / "_extensions"


def _files(folder: Path) -> dict[str, bytes]:
    return {
        str(path.relative_to(folder)): path.read_bytes()
        for path in sorted(folder.rglob("*"))
        if path.is_file()
    }


@pytest.mark.skipif(not COPY.is_dir(), reason="not run from a source checkout")
def test_the_root_copy_matches_the_package() -> None:
    assert _files(COPY) == _files(PACKAGE), "run `make extension`"
