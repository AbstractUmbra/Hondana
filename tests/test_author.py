from __future__ import annotations

import datetime
import json
import pathlib
from copy import deepcopy
from typing import TYPE_CHECKING

from hondana.author import Author
from hondana.http import HTTPClient
from hondana.utils import relationship_finder, to_snake_case


if TYPE_CHECKING:
    from hondana.types.author import GetSingleAuthorResponse


PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "author.json"


PAYLOAD: GetSingleAuthorResponse = json.load(open(PATH, "r"))
HTTP: HTTPClient = HTTPClient(username=None, password=None, email=None)


def clone_author() -> Author:
    t = deepcopy(PAYLOAD)
    return Author(HTTP, t["data"])


class TestAuthor:
    def test_id(self):
        author = clone_author()
        assert author.id == "7e552c08-f7cf-4e0e-9723-409d749dd77c"

    def test_attributes(self):
        author = clone_author()
        for item in PAYLOAD["data"]["attributes"]:
            getattr(author, to_snake_case(item))

    def test_relationship_length(self):
        author = clone_author()
        obj_len = len(author._manga_relationships)
        assert "relationships" in PAYLOAD["data"]
        assert obj_len == len(PAYLOAD["data"]["relationships"])

    def test_manga_relationships(self):
        author = clone_author()
        assert "relationships" in PAYLOAD["data"]
        rels = relationship_finder(PAYLOAD["data"]["relationships"], "manga", limit=None)

        assert author.manga is not None
        assert len(rels) == len(author.manga)

    def test_timezone_properties(self):
        author = clone_author()

        assert author.created_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["createdAt"])
        assert author.updated_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["updatedAt"])
