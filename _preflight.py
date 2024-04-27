"""
This file is inteded for manual CI/Integration usage only.
It is NOT part of the Hondana API or for public use. No support will be provided for this file. Use at your own risk.
"""

import asyncio
import pathlib
import subprocess
import sys

import hondana

TAG_PATH = pathlib.Path("./hondana/extras/tags.json")
REPORT_PATH = pathlib.Path("./hondana/extras/report_reasons.json")

client = hondana.Client()


def __update_tags() -> None:
    asyncio.run(client.update_tags())
    asyncio.run(client.close())

    diff = subprocess.run(["git", "diff", "--exit-code", str(TAG_PATH)], capture_output=False)
    sys.exit(diff.returncode)


def __update_report_reasons() -> None:
    asyncio.run(client.update_report_reasons())
    asyncio.run(client.close())

    diff = subprocess.run(["git", "diff", "--exit-code", str(REPORT_PATH)], capture_output=False)
    sys.exit(diff.returncode)
