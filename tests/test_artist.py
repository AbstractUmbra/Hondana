from __future__ import annotations

import datetime
import json
import pathlib
from copy import deepcopy
from typing import TYPE_CHECKING

from hondana.artist import Artist
from hondana.http import HTTPClient
from hondana.utils import RelationshipResolver, to_snake_case


if TYPE_CHECKING:
    from hondana.types_.artist import GetSingleArtistResponse
    from hondana.types_.manga import MangaResponse

PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "artist.json"


PAYLOAD: GetSingleArtistResponse = json.load(open(PATH, "r"))
HTTP: HTTPClient = object()  # type: ignore # this is just for test purposes.


def clone_artist() -> Artist:
    t = deepcopy(PAYLOAD)
    return Artist(HTTP, t["data"])


class TestArtist:
    def test_id(self):
        artist = clone_artist()
        assert artist.id == PAYLOAD["data"]["id"]

    def test_attributes(self):
        artist = clone_artist()
        for item in PAYLOAD["data"]["attributes"]:
            getattr(artist, to_snake_case(item))

    def test_relationship_length(self):
        artist = clone_artist()
        obj_len = len(artist._manga_relationships)  # type: ignore # sorry, need this for test purposes
        assert "relationships" in PAYLOAD["data"]
        assert obj_len == len(PAYLOAD["data"]["relationships"])

    def test_manga_relationships(self):
        artist = clone_artist()
        assert "relationships" in PAYLOAD["data"]
        rels = RelationshipResolver["MangaResponse"](PAYLOAD["data"]["relationships"], "manga").resolve()

        assert artist.manga is not None
        assert len(rels) == len(artist.manga)

    def test_datetime_props(self):
        artist = clone_artist()

        assert artist.created_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["createdAt"])
        assert artist.updated_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["updatedAt"])
