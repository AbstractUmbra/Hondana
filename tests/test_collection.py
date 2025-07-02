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
from typing import TYPE_CHECKING, Any, Literal, overload

from hondana.author import Author
from hondana.chapter import Chapter
from hondana.collections import (
    AuthorCollection,
    BaseCollection,
    ChapterFeed,
    CoverCollection,
    CustomListCollection,
    LegacyMappingCollection,
    MangaCollection,
    MangaRelationCollection,
    ReportCollection,
    ScanlatorGroupCollection,
    UserCollection,
    UserReportCollection,
)
from hondana.cover import Cover
from hondana.custom_list import CustomList
from hondana.legacy import LegacyItem
from hondana.manga import Manga, MangaRelation
from hondana.scanlator_group import ScanlatorGroup
from hondana.user import User

if TYPE_CHECKING:
    from hondana.http import HTTPClient
    from hondana.types_.author import GetMultiAuthorResponse
    from hondana.types_.chapter import GetMultiChapterResponse
    from hondana.types_.cover import GetMultiCoverResponse
    from hondana.types_.custom_list import GetMultiCustomListResponse
    from hondana.types_.legacy import GetLegacyMappingResponse
    from hondana.types_.manga import MangaRelationResponse, MangaSearchResponse
    from hondana.types_.scanlator_group import GetMultiScanlationGroupResponse
    from hondana.types_.user import GetMultiUserResponse

PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "collections"
HTTP: HTTPClient = object()  # pyright: ignore[reportAssignmentType] # this is just for test purposes.

CollectionType = Literal[
    "authors",
    "chapter_feed",
    "covers",
    "custom_lists",
    "legacy_mapping",
    "manga",
    "manga_relations",
    "reports",  # not supported, needs moderator access
    "scanlator_groups",
    "users",  # needs authentication access
    "user_reports",  # not supported, needs moderator access
]


@overload
def clone_collection(type_: Literal["authors"], /) -> AuthorCollection: ...


@overload
def clone_collection(type_: Literal["chapter_feed"], /) -> ChapterFeed: ...


@overload
def clone_collection(type_: Literal["covers"], /) -> CoverCollection: ...


@overload
def clone_collection(type_: Literal["custom_lists"], /) -> CustomListCollection: ...


@overload
def clone_collection(type_: Literal["legacy_mapping"], /) -> LegacyMappingCollection: ...


@overload
def clone_collection(type_: Literal["manga"], /) -> MangaCollection: ...


@overload
def clone_collection(type_: Literal["manga_relations"], /) -> MangaRelationCollection: ...


@overload
def clone_collection(type_: Literal["reports"], /) -> ReportCollection: ...


@overload
def clone_collection(type_: Literal["scanlator_groups"], /) -> ScanlatorGroupCollection: ...


@overload
def clone_collection(type_: Literal["users"], /) -> UserCollection: ...


@overload
def clone_collection(type_: Literal["user_reports"], /) -> UserReportCollection: ...


def clone_collection(type_: CollectionType, /) -> BaseCollection[Any]:
    path = PATH / f"{type_}.json"
    if type_ == "authors":
        author_payload: GetMultiAuthorResponse = json.load(path.open())
        authors = [Author(HTTP, item) for item in author_payload["data"]]
        return AuthorCollection(HTTP, author_payload, authors=authors)
    if type_ == "chapter_feed":
        chapter_payload: GetMultiChapterResponse = json.load(path.open())
        chapters = [Chapter(HTTP, item) for item in chapter_payload["data"]]
        return ChapterFeed(HTTP, chapter_payload, chapters=chapters)
    if type_ == "covers":
        cover_payload: GetMultiCoverResponse = json.load(path.open())
        covers = [Cover(HTTP, item) for item in cover_payload["data"]]
        return CoverCollection(HTTP, cover_payload, covers=covers)
    if type_ == "custom_lists":
        custom_list_payload: GetMultiCustomListResponse = json.load(path.open())
        custom_lists = [CustomList(HTTP, item) for item in custom_list_payload["data"]]
        return CustomListCollection(HTTP, custom_list_payload, lists=custom_lists)
    if type_ == "legacy_mapping":
        mapping_payload: GetLegacyMappingResponse = json.load(path.open())
        mappings = [LegacyItem(HTTP, item) for item in mapping_payload["data"]]
        return LegacyMappingCollection(HTTP, mapping_payload, mappings=mappings)
    if type_ == "manga":
        manga_payload: MangaSearchResponse = json.load(path.open())
        manga: list[Manga] = [Manga(HTTP, item) for item in manga_payload["data"]]
        return MangaCollection(HTTP, manga_payload, manga=manga)
    if type_ == "manga_relations":
        relation_payload: MangaRelationResponse = json.load(path.open())
        parent_id: str = ""
        manga_relation: list[MangaRelation] = [MangaRelation(HTTP, parent_id, item) for item in relation_payload["data"]]
        return MangaRelationCollection(HTTP, relation_payload, relations=manga_relation)
    if type_ == "scanlator_groups":
        group_payload: GetMultiScanlationGroupResponse = json.load(path.open())
        groups = [ScanlatorGroup(HTTP, item) for item in group_payload["data"]]
        return ScanlatorGroupCollection(HTTP, group_payload, groups=groups)
    if type_ == "users":
        user_payload: GetMultiUserResponse = json.load(path.open())
        users = [User(HTTP, item) for item in user_payload["data"]]
        return UserCollection(HTTP, user_payload, users=users)

    raise RuntimeError("Unreachable code in testing suite.")


class TestCollection:
    def test_author_collection(self) -> None:
        path = PATH / "authors.json"
        payload: GetMultiAuthorResponse = json.load(path.open())
        collection = clone_collection("authors")

        assert collection.limit == payload["limit"]
        assert collection.total == payload["total"]
        assert collection.offset == payload["offset"]
        assert len(collection.items) == len(payload["data"])

    def test_chapter_feed(self) -> None:
        path = PATH / "chapter_feed.json"
        payload: GetMultiChapterResponse = json.load(path.open())
        collection = clone_collection("chapter_feed")

        assert collection.limit == payload["limit"]
        assert collection.total == payload["total"]
        assert collection.offset == payload["offset"]
        assert len(collection.items) == len(payload["data"])

    def test_cover_collection(self) -> None:
        path = PATH / "covers.json"
        payload: GetMultiCoverResponse = json.load(path.open())
        collection = clone_collection("covers")

        assert collection.limit == payload["limit"]
        assert collection.total == payload["total"]
        assert collection.offset == payload["offset"]
        assert len(collection.items) == len(payload["data"])

    def test_custom_list_collection(self) -> None:
        path = PATH / "custom_lists.json"
        payload: GetMultiCustomListResponse = json.load(path.open())
        collection = clone_collection("custom_lists")

        assert collection.limit == payload["limit"]
        assert collection.total == payload["total"]
        assert collection.offset == payload["offset"]
        assert len(collection.items) == len(payload["data"])

    def test_legacy_mapping_collection(self) -> None:
        path = PATH / "legacy_mapping.json"
        payload: GetLegacyMappingResponse = json.load(path.open())
        collection = clone_collection("legacy_mapping")

        assert collection.limit == payload["limit"]
        assert collection.total == payload["total"]
        assert collection.offset == payload["offset"]
        assert len(collection.items) == len(payload["data"])

    def test_manga_collection(self) -> None:
        path = PATH / "manga.json"
        payload: MangaSearchResponse = json.load(path.open())
        collection = clone_collection("manga")

        assert collection.limit == payload["limit"]
        assert collection.total == payload["total"]
        assert collection.offset == payload["offset"]
        assert len(collection.items) == len(payload["data"])

    def test_manga_relation_collection(self) -> None:
        path = PATH / "manga_relations.json"
        payload: MangaRelationResponse = json.load(path.open())
        collection = clone_collection("manga_relations")

        assert collection.limit == payload["limit"]
        assert collection.total == payload["total"]
        assert collection.offset == payload["offset"]
        assert len(collection.items) == len(payload["data"])

    def test_scanlator_group_collection(self) -> None:
        path = PATH / "scanlator_groups.json"
        payload: GetMultiScanlationGroupResponse = json.load(path.open())
        collection = clone_collection("scanlator_groups")

        assert collection.limit == payload["limit"]
        assert collection.total == payload["total"]
        assert collection.offset == payload["offset"]
        assert len(collection.items) == len(payload["data"])

    def test_user_collection(self) -> None:
        path = PATH / "users.json"
        payload: GetMultiUserResponse = json.load(path.open())
        collection = clone_collection("users")

        assert collection.limit == payload["limit"]
        assert collection.total == payload["total"]
        assert collection.offset == payload["offset"]
        assert len(collection.items) == len(payload["data"])
