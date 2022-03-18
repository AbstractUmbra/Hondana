from __future__ import annotations

import json
import pathlib
from copy import deepcopy
from typing import TYPE_CHECKING, Any

from hondana.chapter import Chapter
from hondana.http import HTTPClient
from hondana.relationship import Relationship
from hondana.utils import to_snake_case


if TYPE_CHECKING:
    from hondana.types.chapter import GetSingleChapterResponse


PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "chapter.json"

PAYLOAD: GetSingleChapterResponse = json.load(open(PATH, "r"))
HTTP: HTTPClient = HTTPClient(username=None, password=None, email=None)


def clone_chapter() -> Chapter:
    t = deepcopy(PAYLOAD)
    return Chapter(HTTP, t["data"])


class TestChapter:
    def test_id(self):
        chapter = clone_chapter()
        assert chapter.id == PAYLOAD["data"]["id"]

    def test_attributes(self):
        chapter = clone_chapter()
        for item in PAYLOAD["data"]["attributes"]:
            if item == "publishAt":
                item = "publishedAt"  # special cased because it's the only attribute that is future tense, i.e. created_at, updated_at vs publish_at.
            assert hasattr(chapter, to_snake_case(item))

    def test_relationship_length(self):
        chapter = clone_chapter()
        assert len(chapter.relationships) == len(PAYLOAD["data"]["relationships"])

    def test_sub_relationship_create(self):
        ret: list[Relationship] = []
        chapter = clone_chapter()
        for relationship in deepcopy(chapter._relationships):
            ret.append(Relationship(relationship))

        assert len(ret) == len(chapter.relationships)

    def test_to_dict(self):
        chapter = clone_chapter()
        ret: dict[str, Any] = chapter.to_dict()

        assert bool(ret) is True

    def test_cache_slot_property_relationships(self):
        chapter = clone_chapter()
        assert not hasattr(chapter, "_cs_relationships")
        chapter.relationships
        assert hasattr(chapter, "_cs_relationships")

    def test_manga_property(self):
        chapter = clone_chapter()
        ret: list[Relationship] = []

        for relationship in deepcopy(chapter._relationships):
            ret.append(Relationship(relationship))

        ret = [r for r in ret if r.type == "manga"]

        assert chapter.manga is not None
        assert len(ret) == 1

    def test_manga_id_property(self):
        chapter = clone_chapter()

        assert chapter.manga is not None
        assert chapter.manga_id == chapter.manga.id

    def test_scanlator_groups_property(self):
        chapter = clone_chapter()
        ret: list[Relationship] = []

        for relationship in deepcopy(chapter._relationships):
            ret.append(Relationship(relationship))

        ret = [r for r in ret if r.type == "scanlation_group"]

        assert chapter.scanlator_groups is not None
        assert len(ret) == len(chapter.scanlator_groups)

    def test_uploader_property(self):
        chapter = clone_chapter()

        assert chapter.uploader is not None

        assert chapter.uploader.id == "62d0ea7c-7350-4759-ab6c-58e421dbde79"
