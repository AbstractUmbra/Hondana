"""
The MIT License (MIT)

Copyright (c) 2021-Present AbstractUmbra

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import argparse
import platform
import sys

import aiohttp
import pkg_resources

import hondana


def show_version() -> None:
    entries: list[str] = []

    version_info = sys.version_info
    entries.append(f"- Python v{version_info.major}.{version_info.minor}.{version_info.micro}-{version_info.releaselevel}")

    md_version_info = hondana.version_info
    entries.append(
        f"- Hondana v{md_version_info.major}.{md_version_info.minor}."
        f"{md_version_info.micro}-{md_version_info.releaselevel}"
    )

    if md_version_info.releaselevel != "final":
        pkg = pkg_resources.get_distribution("Hondana")
        if pkg:
            entries.append(f"    - Hondana pkg_resources: v{pkg.version}")

    entries.append(f" - aiohttp {aiohttp.__version__}")
    uname = platform.uname()
    entries.append(f"- system info: {uname.system} {uname.release} {uname.version}")

    print("\n".join(entries))


def parse_args() -> tuple[argparse.ArgumentParser, argparse.Namespace]:
    parser = argparse.ArgumentParser(prog="hondana", description="Tools for helping with Hondana")
    parser.add_argument("-v", "--version", action="store_true", help="shows the wrapper version")

    parser.set_defaults(func=core)

    return parser, parser.parse_args()


def core(_: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.version:
        show_version()


def main() -> None:
    parser, args = parse_args()
    args.func(parser, args)


main()
