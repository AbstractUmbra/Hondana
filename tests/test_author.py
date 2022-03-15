from __future__ import annotations

import json
import pathlib
from copy import deepcopy
from typing import TYPE_CHECKING

from hondana.author import Author
from hondana.http import HTTPClient
from hondana.relationship import Relationship
from hondana.utils import to_snake_case


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
        assert len(author.relationships) == len(PAYLOAD["data"]["relationships"])

    def test_sub_relationship_creation(self):
        ret: list[Relationship] = []
        author = clone_author()
        for relationship in author._relationships:
            ret.append(Relationship(relationship))

        assert len(ret) == len(author.relationships)

    def test_manga_prop(self):
        manga: list[Relationship] = []
        author = clone_author()
        rels = deepcopy(author._relationships)
        for relationship in rels:
            manga.append(Relationship(relationship))

        manga = [r for r in manga if r.type == "manga"]

        assert author.manga is not None
        assert len(manga) == len(author.manga)
