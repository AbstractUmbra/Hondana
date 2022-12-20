from __future__ import annotations

import datetime
import json
import pathlib
from copy import deepcopy
from typing import TYPE_CHECKING

from hondana.author import Author
from hondana.http import HTTPClient
from hondana.utils import RelationshipResolver, to_snake_case


if TYPE_CHECKING:
    from hondana.types_.author import GetSingleAuthorResponse
    from hondana.types_.manga import MangaResponse


PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "author.json"


PAYLOAD: GetSingleAuthorResponse = json.load(open(PATH, "r"))
HTTP: HTTPClient = object()  # type: ignore # this is just for test purposes.


def clone_author() -> Author:
    t = deepcopy(PAYLOAD)
    return Author(HTTP, t["data"])


class TestAuthor:
    def test_id(self):
        author = clone_author()
        assert author.id == PAYLOAD["data"]["id"]

    def test_attributes(self):
        author = clone_author()
        for item in PAYLOAD["data"]["attributes"]:
            getattr(author, to_snake_case(item))

    def test_relationship_length(self):
        author = clone_author()
        obj_len = len(author._manga_relationships)  # type: ignore # sorry, need this for test purposes
        assert "relationships" in PAYLOAD["data"]
        assert obj_len == len(PAYLOAD["data"]["relationships"])

    def test_manga_relationships(self):
        author = clone_author()
        assert "relationships" in PAYLOAD["data"]
        rels = RelationshipResolver["MangaResponse"](PAYLOAD["data"]["relationships"], "manga").resolve()

        assert author.manga is not None
        assert len(rels) == len(author.manga)

    def test_timezone_properties(self):
        author = clone_author()

        assert author.created_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["createdAt"])
        assert author.updated_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["updatedAt"])
