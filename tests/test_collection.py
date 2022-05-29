from __future__ import annotations

import json
import pathlib
from typing import TYPE_CHECKING, Literal, overload

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
from hondana.http import HTTPClient
from hondana.legacy import LegacyItem
from hondana.manga import Manga, MangaRelation
from hondana.scanlator_group import ScanlatorGroup
from hondana.user import User


if TYPE_CHECKING:
    from hondana.types.author import GetMultiAuthorResponse
    from hondana.types.chapter import GetMultiChapterResponse
    from hondana.types.cover import GetMultiCoverResponse
    from hondana.types.custom_list import GetMultiCustomListResponse
    from hondana.types.legacy import GetLegacyMappingResponse
    from hondana.types.manga import MangaRelationResponse, MangaSearchResponse
    from hondana.types.scanlator_group import GetMultiScanlationGroupResponse
    from hondana.types.user import GetMultiUserResponse

PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "collections"
HTTP: HTTPClient = object()  # type: ignore # this is just for test purposes.

CollectionType = Literal[
    "author",
    "chapter_feed",
    "cover",
    "custom_list",
    "legacy_mapping",
    "manga",
    "manga_relation",
    "report",  # not supported, needs moderator access
    "scanlator_group",
    "user",  # needs authentication access
    "user_report",  # not supported, needs moderator access
]


@overload
def clone_collection(type_: Literal["author"], /) -> AuthorCollection:
    ...


@overload
def clone_collection(type_: Literal["chapter_feed"], /) -> ChapterFeed:
    ...


@overload
def clone_collection(type_: Literal["cover"], /) -> CoverCollection:
    ...


@overload
def clone_collection(type_: Literal["custom_list"], /) -> CustomListCollection:
    ...


@overload
def clone_collection(type_: Literal["legacy_mapping"], /) -> LegacyMappingCollection:
    ...


@overload
def clone_collection(type_: Literal["manga"], /) -> MangaCollection:
    ...


@overload
def clone_collection(type_: Literal["manga_relation"], /) -> MangaRelationCollection:
    ...


@overload
def clone_collection(type_: Literal["report"], /) -> ReportCollection:
    ...


@overload
def clone_collection(type_: Literal["scanlator_group"], /) -> ScanlatorGroupCollection:
    ...


@overload
def clone_collection(type_: Literal["user"], /) -> UserCollection:
    ...


@overload
def clone_collection(type_: Literal["user_report"], /) -> UserReportCollection:
    ...


def clone_collection(type_: CollectionType, /) -> BaseCollection:
    path = PATH / f"{type_}.json"
    if type_ == "author":
        author_payload: GetMultiAuthorResponse = json.load(open(path, "r"))
        authors = [Author(HTTP, item) for item in author_payload["data"]]
        return AuthorCollection(HTTP, author_payload, authors=authors)
    elif type_ == "chapter_feed":
        chapter_payload: GetMultiChapterResponse = json.load(open(path, "r"))
        chapters = [Chapter(HTTP, item) for item in chapter_payload["data"]]
        return ChapterFeed(HTTP, chapter_payload, chapters=chapters)
    elif type_ == "cover":
        cover_payload: GetMultiCoverResponse = json.load(open(path, "r"))
        covers = [Cover(HTTP, item) for item in cover_payload["data"]]
        return CoverCollection(HTTP, cover_payload, covers=covers)
    elif type_ == "custom_list":
        custom_list_payload: GetMultiCustomListResponse = json.load(open(path, "r"))
        custom_lists = [CustomList(HTTP, item) for item in custom_list_payload["data"]]
        return CustomListCollection(HTTP, custom_list_payload, lists=custom_lists)
    elif type_ == "legacy_mapping":
        mapping_payload: GetLegacyMappingResponse = json.load(open(path, "r"))
        mappings = [LegacyItem(HTTP, item) for item in mapping_payload["data"]]
        return LegacyMappingCollection(HTTP, mapping_payload, mappings=mappings)
    elif type_ == "manga":
        manga_payload: MangaSearchResponse = json.load(open(path, "r"))
        manga: list[Manga] = [Manga(HTTP, item) for item in manga_payload["data"]]
        return MangaCollection(HTTP, manga_payload, manga=manga)
    elif type_ == "manga_relation":
        relation_payload: MangaRelationResponse = json.load(open(path, "r"))
        parent_id: str = ""
        manga_relation: list[MangaRelation] = [MangaRelation(HTTP, parent_id, item) for item in relation_payload["data"]]
        return MangaRelationCollection(HTTP, relation_payload, relations=manga_relation)
    elif type_ == "scanlator_group":
        group_payload: GetMultiScanlationGroupResponse = json.load(open(path, "r"))
        groups = [ScanlatorGroup(HTTP, item) for item in group_payload["data"]]
        return ScanlatorGroupCollection(HTTP, group_payload, groups=groups)
    elif type_ == "user":
        user_payload: GetMultiUserResponse = json.load(open(path, "r"))
        users = [User(HTTP, item) for item in user_payload["data"]]
        return UserCollection(HTTP, user_payload, users=users)

    raise RuntimeError("Unreachable code in testing suite.")


class TestCollection:
    def test_author_collection(self):
        path = PATH / "author.json"
        payload: GetMultiAuthorResponse = json.load(open(path, "r"))
        collection = clone_collection("author")

        assert collection.limit == payload["limit"]
        assert collection.total == payload["total"]
        assert collection.offset == payload["offset"]
        assert len(collection.items) == len(payload["data"])

    def test_chapter_feed(self):
        path = PATH / "chapter_feed.json"
        payload: GetMultiChapterResponse = json.load(open(path, "r"))
        collection = clone_collection("chapter_feed")

        assert collection.limit == payload["limit"]
        assert collection.total == payload["total"]
        assert collection.offset == payload["offset"]
        assert len(collection.items) == len(payload["data"])

    def test_cover_collection(self):
        path = PATH / "cover.json"
        payload: GetMultiCoverResponse = json.load(open(path, "r"))
        collection = clone_collection("cover")

        assert collection.limit == payload["limit"]
        assert collection.total == payload["total"]
        assert collection.offset == payload["offset"]
        assert len(collection.items) == len(payload["data"])

    def test_custom_list_collection(self):
        path = PATH / "custom_list.json"
        payload: GetMultiCustomListResponse = json.load(open(path, "r"))
        collection = clone_collection("custom_list")

        assert collection.limit == payload["limit"]
        assert collection.total == payload["total"]
        assert collection.offset == payload["offset"]
        assert len(collection.items) == len(payload["data"])

    def test_legacy_mapping_collection(self):
        path = PATH / "legacy_mapping.json"
        payload: GetLegacyMappingResponse = json.load(open(path, "r"))
        collection = clone_collection("legacy_mapping")

        assert collection.limit == payload["limit"]
        assert collection.total == payload["total"]
        assert collection.offset == payload["offset"]
        assert len(collection.items) == len(payload["data"])

    def test_manga_collection(self):
        path = PATH / "manga.json"
        payload: MangaSearchResponse = json.load(open(path, "r"))
        collection = clone_collection("manga")

        assert collection.limit == payload["limit"]
        assert collection.total == payload["total"]
        assert collection.offset == payload["offset"]
        assert len(collection.items) == len(payload["data"])

    def test_manga_relation_collection(self):
        path = PATH / "manga_relation.json"
        payload: MangaRelationResponse = json.load(open(path, "r"))
        collection = clone_collection("manga_relation")

        assert collection.limit == payload["limit"]
        assert collection.total == payload["total"]
        assert collection.offset == payload["offset"]
        assert len(collection.items) == len(payload["data"])

    def test_scanlator_group_collection(self):
        path = PATH / "scanlator_group.json"
        payload: GetMultiScanlationGroupResponse = json.load(open(path, "r"))
        collection = clone_collection("scanlator_group")

        assert collection.limit == payload["limit"]
        assert collection.total == payload["total"]
        assert collection.offset == payload["offset"]
        assert len(collection.items) == len(payload["data"])

    def test_user_collection(self):
        path = PATH / "user.json"
        payload: GetMultiUserResponse = json.load(open(path, "r"))
        collection = clone_collection("user")

        assert collection.limit == payload["limit"]
        assert collection.total == payload["total"]
        assert collection.offset == payload["offset"]
        assert len(collection.items) == len(payload["data"])
