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

from __future__ import annotations

import json
import pathlib
from copy import deepcopy
from typing import TYPE_CHECKING

from hondana.legacy import LegacyItem

if TYPE_CHECKING:
    from hondana.http import HTTPClient
    from hondana.types_.legacy import GetLegacyMappingResponse


PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "collections" / "legacy_mapping.json"

PAYLOAD: GetLegacyMappingResponse = json.load(PATH.open(encoding="utf-8"))
HTTP: HTTPClient = object()  # pyright: ignore[reportAssignmentType] # this is just for test purposes.


def clone_legacy() -> LegacyItem:
    t = deepcopy(PAYLOAD)
    return LegacyItem(HTTP, t["data"][0])


class TestLegacy:
    def test_id(self) -> None:
        item = clone_legacy()
        assert item.id == PAYLOAD["data"][0]["id"]

    def test_mapping_ids(self) -> None:
        item = clone_legacy()

        assert item.obj_legacy_id == PAYLOAD["data"][0]["attributes"]["legacyId"]
        assert item.obj_new_id == PAYLOAD["data"][0]["attributes"]["newId"]
