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

from hondana.author import Author
from hondana.utils import RelationshipResolver, to_snake_case

if TYPE_CHECKING:
    from hondana.http import HTTPClient
    from hondana.types_.author import GetSingleAuthorResponse
    from hondana.types_.manga import MangaResponse


PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "author.json"


PAYLOAD: GetSingleAuthorResponse = json.load(PATH.open())
HTTP: HTTPClient = object()  # pyright: ignore[reportAssignmentType] # this is just for test purposes.


def clone_author() -> Author:
    t = deepcopy(PAYLOAD)
    return Author(HTTP, t["data"])


class TestAuthor:
    def test_id(self) -> None:
        author = clone_author()
        assert author.id == PAYLOAD["data"]["id"]

    def test_attributes(self) -> None:
        author = clone_author()
        for item in PAYLOAD["data"]["attributes"]:
            getattr(author, to_snake_case(item))

    def test_relationship_length(self) -> None:
        author = clone_author()
        obj_len = len(author._manga_relationships)  # pyright: ignore[reportPrivateUsage] # sorry, need this for test purposes
        assert "relationships" in PAYLOAD["data"]

        # remove empty relationships
        resolved_relationships = [r for r in PAYLOAD["data"]["relationships"] if "attributes" in r]

        assert obj_len == len(resolved_relationships)

    def test_manga_relationships(self) -> None:
        author = clone_author()
        assert "relationships" in PAYLOAD["data"]
        rels = RelationshipResolver["MangaResponse"](PAYLOAD["data"]["relationships"], "manga").resolve(remove_empty=True)

        assert author.manga is not None
        assert len(rels) == len(author.manga)

    def test_timezone_properties(self) -> None:
        author = clone_author()

        assert author.created_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["createdAt"])
        assert author.updated_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["updatedAt"])
