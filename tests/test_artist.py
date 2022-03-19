from __future__ import annotations

import datetime
import json
import pathlib
from copy import deepcopy
from typing import TYPE_CHECKING

from hondana.artist import Artist
from hondana.http import HTTPClient
from hondana.relationship import Relationship
from hondana.utils import to_snake_case


if TYPE_CHECKING:
    from hondana.types.artist import GetSingleArtistResponse

PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "artist.json"


PAYLOAD: GetSingleArtistResponse = json.load(open(PATH, "r"))
HTTP: HTTPClient = HTTPClient(username=None, password=None, email=None)


def clone_artist() -> Artist:
    t = deepcopy(PAYLOAD)
    return Artist(HTTP, t["data"])


class TestArtist:
    def test_id(self):
        artist = clone_artist()
        assert artist.id == "7e552c08-f7cf-4e0e-9723-409d749dd77c"

    def test_attributes(self):
        artist = clone_artist()
        for item in PAYLOAD["data"]["attributes"]:
            getattr(artist, to_snake_case(item))

    def test_relationship_length(self):
        artist = clone_artist()
        assert len(artist.relationships) == len(PAYLOAD["data"]["relationships"])

    def test_sub_relationship_creation(self):
        ret: list[Relationship] = []
        artist = clone_artist()
        ret.extend(Relationship(relationship) for relationship in artist._relationships)

        assert len(ret) == len(artist.relationships)

    def test_manga_prop(self):
        manga: list[Relationship] = []
        artist = clone_artist()
        rels = deepcopy(artist._relationships)
        for relationship in rels:
            manga.append(Relationship(relationship))

        manga = [r for r in manga if r.type == "manga"]

        assert artist.manga is not None
        assert len(manga) == len(artist.manga)

    def test_datetime_props(self):
        artist = clone_artist()

        assert artist.created_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["createdAt"])
        assert artist.updated_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["updatedAt"])
