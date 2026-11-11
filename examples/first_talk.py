"""First talk.

A short talk started with `new_talk`, with an interactive plasma-plots figure, rendered to
reveal.js slides (`first_talk/talk.html`) and to a Beamer PDF (`first_talk/talk.pdf`). The
HTML slides are embedded below, and the slides of the PDF are shown below the source.
"""

import shutil
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go

from plasma_presentations import figure, new_talk, render

HERE = Path(__file__).resolve().parent
FOLDER = HERE / "first_talk"

shutil.rmtree(FOLDER, ignore_errors=True)
qmd = new_talk(
    FOLDER,
    "Speeds in a thermal plasma",
    author="Jane Doe",
    institute="Example Institute",
    date="2026-12-04",
)

# a figure: a Maxwellian at three temperatures, interactive in HTML and a PDF in Beamer
v = np.linspace(0, 4, 200)
fig = go.Figure()
for temperature in (0.5, 1.0, 2.0):
    f = v**2 * np.exp(-(v**2) / temperature) / temperature**1.5
    fig.add_scatter(x=v, y=f / f.max(), name=f"T = {temperature}")
fig.update_layout(
    template="simple_white", xaxis_title="speed v", yaxis_title="f(v) / max f"
)
figure(fig, FOLDER / "figures" / "maxwellian")

with qmd.open("a") as talk:
    talk.write(
        "\n## The distribution\n\n"
        '{{< plasma-figure figures/maxwellian caption="Normalised to its peak." >}}\n'
    )

html, pdf = render(qmd)
SLIDES = html  # the docs publish these HTML slides and embed them in this page

# the slides of the PDF, as the docs show them
subprocess.run(
    ["pdftoppm", "-png", "-r", "40", str(pdf), str(FOLDER / "page")], check=True
)
pages = sorted(FOLDER.glob("page-*.png"))
fig, axes = plt.subplots(
    (len(pages) + 1) // 2, 2, figsize=(10, 2.9 * ((len(pages) + 1) // 2))
)
for ax in axes.flat:
    ax.set_axis_off()
for ax, page in zip(axes.flat, pages, strict=False):
    ax.imshow(plt.imread(page))
fig.tight_layout()
