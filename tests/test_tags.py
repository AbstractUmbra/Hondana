from __future__ import annotations

import json
import pathlib
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Mapping

from hondana.http import HTTPClient
from hondana.manga import Manga
from hondana.relationship import Relationship
from hondana.tags import QueryTags, Tag


if TYPE_CHECKING:
    from hondana.types.manga import GetMangaResponse


PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "manga.json"

PAYLOAD: GetMangaResponse = json.load(open(PATH, "r"))
HTTP: HTTPClient = HTTPClient(username=None, password=None, email=None)


def clone_tags() -> list[Tag]:
    t = deepcopy(PAYLOAD)
    return Manga(HTTP, t["data"]).tags


class TestTags:
    def test_ids(self):
        tags = clone_tags()

        tag_ids = [t.id for t in tags]

        assert len(tag_ids) == len(PAYLOAD["data"]["attributes"]["tags"])

    def test_tag_names(self):
        tags = clone_tags()

        raw_tags: list[str] = []
        for item in PAYLOAD["data"]["attributes"]["tags"]:
            raw_tags.extend(str(sub_key) for sub_key in item["attributes"]["name"].values())

        for tag, raw_tag in zip(
            sorted(tags, key=lambda t: t.name),
            sorted(raw_tags, key=lambda t: t),
        ):
            assert tag.name == raw_tag

    def test_tag_relationships(self):  # currently, tags have no relationships, but even so.
        tags = clone_tags()

        tag_rels: list[Relationship] = [r for tag in tags for r in tag.relationships]

        raw_rels: list[Mapping[str, Any]] = [
            obj for rel in PAYLOAD["data"]["attributes"]["tags"] for obj in rel["relationships"]
        ]

        for a, b in zip(sorted(tag_rels, key=lambda r: r.id), sorted(raw_rels, key=lambda r: r["id"])):
            assert a == b

    def test_tag_descriptions(self):  # currently, tags have no descriptions, but even so.
        tags = clone_tags()
        raw_tags = PAYLOAD["data"]["attributes"]["tags"]

        for tag, raw_tag in zip(sorted(tags, key=lambda t: t.id), sorted(raw_tags, key=lambda t: t["id"])):
            _description = tag.description
            _raw_description = {k: v for obj in raw_tag["attributes"]["description"] for k, v in obj.items()}
            assert _description == _raw_description


class TestQueryTags:
    def test_query_tags(self):
        tags = QueryTags("Comedy", "Genderswap", "Romance", mode="OR")
        assert tags.mode == "OR"
        assert tags.tags == [
            "4d32cc48-9f00-4cca-9b5a-a839f0764984",
            "2bd2e8d0-f146-434a-9b51-fc9ff2c5fe6a",
            "423e2eae-a7a2-4a8b-ac03-a8351462d71d",
        ]

        tags = QueryTags("Comedy", "Mecha", mode="AND")
        assert tags.mode == "AND"
        assert tags.tags == ["4d32cc48-9f00-4cca-9b5a-a839f0764984", "50880a9d-5440-4732-9afb-8f457127e836"]

        try:
            tags = QueryTags("SomethingElse", mode="OR")
        except ValueError:
            pass
        else:
            raise AssertionError("Tags failed to fail.")
