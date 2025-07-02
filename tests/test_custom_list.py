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

from hondana.custom_list import CustomList
from hondana.utils import RelationshipResolver, to_snake_case

if TYPE_CHECKING:
    from hondana.http import HTTPClient
    from hondana.types_.custom_list import GetSingleCustomListResponse
    from hondana.types_.manga import MangaResponse
    from hondana.types_.user import UserResponse

PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "custom_list.json"

PAYLOAD: GetSingleCustomListResponse = json.load(PATH.open())
HTTP: HTTPClient = object()  # pyright: ignore[reportAssignmentType] # this is just for test purposes.


def clone_custom_list() -> CustomList:
    t = deepcopy(PAYLOAD)
    return CustomList(HTTP, t["data"])


class TestCustomList:
    def test_id(self) -> None:
        custom_list = clone_custom_list()

        assert custom_list.id == PAYLOAD["data"]["id"]

    def test_attributes(self) -> None:
        custom_list = clone_custom_list()
        for item in PAYLOAD["data"]["attributes"]:
            getattr(custom_list, to_snake_case(item))

    def test_owner(self) -> None:
        custom_list = clone_custom_list()

        assert custom_list.owner is not None

        owner_rel = RelationshipResolver["UserResponse"](PAYLOAD["data"]["relationships"], "user").pop()
        assert owner_rel is not None

        assert custom_list.owner.id == owner_rel["id"]

    def test_mangas(self) -> None:
        custom_list = clone_custom_list()

        assert custom_list.manga is not None

        manga_rels = RelationshipResolver["MangaResponse"](PAYLOAD["data"]["relationships"], "manga").resolve()
        assert manga_rels is not None

        assert len(custom_list.manga) == len(manga_rels)
