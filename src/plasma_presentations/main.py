"""The ``plasma-presentations`` command: start, update and render talks."""

from __future__ import annotations

import argparse

from plasma_presentations import __version__
from plasma_presentations.talk import FORMATS, install_extension, new_talk, render


def main(argv: list[str] | None = None) -> int:
    """Run the ``plasma-presentations`` command.

    ``plasma-presentations new kickoff --title "..."`` starts a talk in the folder
    ``kickoff``, ``plasma-presentations build kickoff/talk.qmd`` renders it to HTML and PDF,
    and ``plasma-presentations install talks`` copies (or updates) the Quarto extension into a
    folder of talks and makes it a Quarto project, so that every talk below it finds the
    extension.

    Args:
        argv: The arguments; the command line's when None.

    Returns:
        The exit status.
    """
    parser = argparse.ArgumentParser(
        prog="plasma-presentations",
        description="Talks written as Quarto slides: HTML with reveal.js, PDF with Beamer.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    new = commands.add_parser("new", help="start a talk in a new folder")
    new.add_argument("folder", help="the folder of the talk, empty or new")
    new.add_argument("--title", default="Title of the talk")
    new.add_argument("--subtitle", default="")
    new.add_argument("--author", default="")
    new.add_argument("--institute", default="")
    new.add_argument("--date", default="today")
    build = commands.add_parser("build", help="render a talk with Quarto")
    build.add_argument("qmd", help="the talk's .qmd file")
    build.add_argument("--to", default="all", choices=("all", *FORMATS))
    install = commands.add_parser(
        "install",
        help="copy or update the Quarto extension in a folder of talks (a Quarto project)",
    )
    install.add_argument("folder", help="the folder; talks below it use the extension")
    args = parser.parse_args(argv)
    if args.command == "new":
        qmd = new_talk(
            args.folder,
            args.title,
            subtitle=args.subtitle,
            author=args.author,
            institute=args.institute,
            date=args.date,
        )
        print(f"wrote {qmd}")
    elif args.command == "build":
        for path in render(args.qmd, args.to):
            print(f"wrote {path}")
    else:
        print(f"wrote {install_extension(args.folder)}")
    return 0
