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

import datetime
import json
import pathlib
from copy import deepcopy
from typing import TYPE_CHECKING

from hondana.scanlator_group import ScanlatorGroup
from hondana.utils import iso_to_delta, to_snake_case

if TYPE_CHECKING:
    from hondana.http import HTTPClient
    from hondana.types_.scanlator_group import GetSingleScanlationGroupResponse

PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "scanlator_group.json"

PAYLOAD: GetSingleScanlationGroupResponse = json.load(PATH.open())
HTTP: HTTPClient = object()  # pyright: ignore[reportAssignmentType] # this is just for test purposes.


def clone_group() -> ScanlatorGroup:
    t = deepcopy(PAYLOAD)
    return ScanlatorGroup(HTTP, t["data"])


class TestScanlatorGroup:
    def test_id(self) -> None:
        group = clone_group()
        assert group.id == PAYLOAD["data"]["id"]

    def test_attributes(self) -> None:
        group = clone_group()

        for item in PAYLOAD["data"]["attributes"]:
            if item == "publishDelay":
                item = "_publish_delay"  # noqa: PLW2901  # we made this a property to allow manipulation
            assert hasattr(group, to_snake_case(item))

    def test_relationship_length(self) -> None:
        group = clone_group()

        assert group.members is not None
        assert group.leader is not None

        obj_len = len(group.members) + 1  # leader

        assert "relationships" in PAYLOAD["data"]
        assert obj_len == len(PAYLOAD["data"]["relationships"])

    def test_datetime_properties(self) -> None:
        group = clone_group()

        assert group.created_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["createdAt"])
        assert group.updated_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["updatedAt"])

        if group.publish_delay or PAYLOAD["data"]["attributes"]["publishDelay"]:
            assert group.publish_delay == iso_to_delta(PAYLOAD["data"]["attributes"]["publishDelay"])
