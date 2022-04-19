from __future__ import annotations

import datetime
import json
import pathlib
from copy import deepcopy
from typing import TYPE_CHECKING, Any

from hondana.chapter import Chapter
from hondana.http import HTTPClient
from hondana.utils import relationship_finder, to_snake_case


if TYPE_CHECKING:
    from hondana.types.chapter import GetSingleChapterResponse


PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "chapter.json"

PAYLOAD: GetSingleChapterResponse = json.load(open(PATH, "r"))
HTTP: HTTPClient = HTTPClient(username=None, password=None, email=None)


def clone_chapter() -> Chapter:
    t = deepcopy(PAYLOAD)
    assert "relationships" in t["data"]
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
        assert chapter.manga is not None
        assert chapter.scanlator_groups is not None
        assert chapter.uploader is not None
        obj_len = len(chapter.scanlator_groups) + 2  # scanlator and manga

        assert "relationships" in PAYLOAD["data"]
        assert obj_len == len(PAYLOAD["data"]["relationships"])

    def test_to_dict(self):
        chapter = clone_chapter()
        ret: dict[str, Any] = chapter.to_dict()

        assert bool(ret)

    def test_manga_property(self):
        chapter = clone_chapter()

        cloned = deepcopy(PAYLOAD)
        assert "relationships" in cloned["data"]
        manga_rel = relationship_finder(cloned["data"]["relationships"], "manga", limit=1)

        assert chapter.manga is not None
        assert manga_rel is not None
        assert chapter.manga.id == manga_rel["id"]

    def test_manga_id_property(self):
        chapter = clone_chapter()

        assert chapter.manga is not None
        assert chapter.manga_id == chapter.manga.id

    def test_scanlator_groups_property(self):
        chapter = clone_chapter()

        cloned = deepcopy(PAYLOAD)
        assert "relationships" in cloned["data"]
        ret = relationship_finder(cloned["data"]["relationships"], "scanlation_group", limit=None)

        assert chapter.scanlator_groups is not None
        assert len(ret) == len(chapter.scanlator_groups)

    def test_uploader_property(self):
        chapter = clone_chapter()

        assert chapter.uploader is not None

        assert "relationships" in PAYLOAD["data"]
        uploader_rel = relationship_finder(PAYLOAD["data"]["relationships"], "user", limit=1)
        assert uploader_rel is not None

        assert chapter.uploader.id == uploader_rel["id"]

    def test_datetime_props(self):
        chapter = clone_chapter()

        assert chapter.created_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["createdAt"])
        assert chapter.published_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["publishAt"])
        assert chapter.updated_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["updatedAt"])
