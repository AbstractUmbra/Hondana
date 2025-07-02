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
from typing import TYPE_CHECKING, Any

from hondana.chapter import Chapter
from hondana.utils import RelationshipResolver, to_snake_case

if TYPE_CHECKING:
    from hondana.http import HTTPClient
    from hondana.types_.chapter import GetSingleChapterResponse
    from hondana.types_.manga import MangaResponse
    from hondana.types_.scanlator_group import ScanlationGroupResponse
    from hondana.types_.user import UserResponse


PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "chapter.json"

PAYLOAD: GetSingleChapterResponse = json.load(PATH.open())
HTTP: HTTPClient = object()  # pyright: ignore[reportAssignmentType] # this is just for test purposes.


def clone_chapter() -> Chapter:
    t = deepcopy(PAYLOAD)
    assert "relationships" in t["data"]
    return Chapter(HTTP, t["data"])


class TestChapter:
    def test_id(self) -> None:
        chapter = clone_chapter()
        assert chapter.id == PAYLOAD["data"]["id"]

    def test_attributes(self) -> None:
        chapter = clone_chapter()
        for item in PAYLOAD["data"]["attributes"]:
            if item == "publishAt":
                item = "publishedAt"  # noqa: PLW2901 # special cased because it's the only attribute that is future tense, i.e. created_at, updated_at vs publish_at.
            assert hasattr(chapter, to_snake_case(item))

    def test_relationship_length(self) -> None:
        chapter = clone_chapter()
        assert chapter.manga is not None
        assert chapter.scanlator_groups is not None
        assert chapter.uploader is not None
        obj_len = len(chapter.scanlator_groups) + 2  # scanlator and manga

        assert "relationships" in PAYLOAD["data"]
        assert obj_len == len(PAYLOAD["data"]["relationships"])

    def test_to_dict(self) -> None:
        chapter = clone_chapter()
        ret: dict[str, Any] = chapter.to_dict()

        assert bool(ret)

    def test_manga_property(self) -> None:
        chapter = clone_chapter()

        cloned = deepcopy(PAYLOAD)
        assert "relationships" in cloned["data"]
        manga_rel = RelationshipResolver["MangaResponse"](cloned["data"]["relationships"], "manga").pop()

        assert chapter.manga is not None
        assert manga_rel is not None
        assert chapter.manga.id == manga_rel["id"]

    def test_manga_id_property(self) -> None:
        chapter = clone_chapter()

        assert chapter.manga is not None
        assert chapter.manga_id == chapter.manga.id

    def test_scanlator_groups_property(self) -> None:
        chapter = clone_chapter()

        cloned = deepcopy(PAYLOAD)
        assert "relationships" in cloned["data"]
        ret = RelationshipResolver["ScanlationGroupResponse"](cloned["data"]["relationships"], "scanlation_group").resolve()

        assert chapter.scanlator_groups is not None
        assert len(ret) == len(chapter.scanlator_groups)

    def test_uploader_property(self) -> None:
        chapter = clone_chapter()

        assert chapter.uploader is not None

        assert "relationships" in PAYLOAD["data"]
        uploader_rel = RelationshipResolver["UserResponse"](PAYLOAD["data"]["relationships"], "user").pop()
        assert uploader_rel is not None

        assert chapter.uploader.id == uploader_rel["id"]

    def test_datetime_props(self) -> None:
        chapter = clone_chapter()

        assert chapter.created_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["createdAt"])
        assert chapter.published_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["publishAt"])
        assert chapter.updated_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["updatedAt"])
