# type: ignore[reportUnusedFunction] # preflight use
"""
This file is inteded for manual CI/Integration usage only.
It is NOT part of the Hondana API or for public use. No support will be provided for this file. Use at your own risk.
"""

import argparse
import asyncio
import pathlib
import subprocess  # noqa: S404
import sys

import hondana

TAG_PATH = pathlib.Path("./hondana/extras/tags.json")
REPORT_PATH = pathlib.Path("./hondana/extras/report_reasons.json")


class ProgramNamespace(argparse.Namespace):
    tags: bool
    reports: bool

    def _parsed(self, *, _all: bool = False) -> bool:
        """This quick cheat only works if the `dest` of the params matches the annotations.

        Returns
        --------
        :class:`bool`
        """
        c = all if _all else any
        return c(getattr(self, anno) for anno in self.__annotations__)


parser = argparse.ArgumentParser(description="Small pre-flight CI script for hondana")
parser.add_argument("-t", "--tags", action="store_true", dest="tags", help="Whether to run the 'update tags' action.")
parser.add_argument(
    "-r", "--reports", action="store_true", dest="reports", help="Whether to run the 'update report reasons' action."
)


async def __update_tags(client: hondana.Client, /) -> int:
    await client.update_tags()

    prog: asyncio.subprocess.Process = await asyncio.create_subprocess_exec("git", "diff", "--exit-code", str(REPORT_PATH))
    return await prog.wait()


async def __update_report_reasons(client: hondana.Client, /) -> int:
    await client.update_report_reasons()

    prog: asyncio.subprocess.Process = await asyncio.create_subprocess_exec(
        "git",
        "diff",
        "--exit-code",
        str(REPORT_PATH),
    )
    return await prog.wait()


async def main(args: ProgramNamespace) -> None:
    if not args._parsed():
        msg = "At least one argument must be specified."
        raise RuntimeError(msg)

    client = hondana.Client()

    if args.tags:
        ret = await __update_tags(client)
        if ret == 1:
            msg = "Tags updated."
            raise RuntimeError(msg)
    if args.reports:
        ret = await __update_report_reasons(client)
        if ret == 1:
            msg = "Reports updated."
            raise RuntimeError(msg)

    await client.close()


if __name__ == "__main__":
    args = parser.parse_args(namespace=ProgramNamespace())
    asyncio.run(main(args))
