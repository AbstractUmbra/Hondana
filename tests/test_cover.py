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

from hondana.cover import Cover
from hondana.utils import RelationshipResolver, to_snake_case

if TYPE_CHECKING:
    from hondana.http import HTTPClient
    from hondana.types_.cover import GetSingleCoverResponse
    from hondana.types_.user import UserResponse


PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "cover.json"

PAYLOAD: GetSingleCoverResponse = json.load(PATH.open())
HTTP: HTTPClient = object()  # pyright: ignore[reportAssignmentType] # this is just for test purposes.


def clone_cover() -> Cover:
    t = deepcopy(PAYLOAD)
    return Cover(HTTP, t["data"])


class TestCover:
    def test_id(self) -> None:
        cover = clone_cover()
        assert cover.id == PAYLOAD["data"]["id"]

    def test_attributes(self) -> None:
        cover = clone_cover()
        for item in PAYLOAD["data"]["attributes"]:
            getattr(cover, to_snake_case(item))

    def test_uploader(self) -> None:
        cover = clone_cover()

        assert cover.uploader is not None
        assert "relationships" in PAYLOAD["data"]
        rel = RelationshipResolver["UserResponse"](PAYLOAD["data"]["relationships"], "user").pop()
        assert rel is not None
        assert cover.uploader.id == rel["id"]

    def test_url(self) -> None:
        cover = clone_cover()

        cover.url()

        cover.url(256)

        cover.url(512)

    def test_datetime_properties(self) -> None:
        cover = clone_cover()

        assert cover.created_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["createdAt"])
        assert cover.updated_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["updatedAt"])
