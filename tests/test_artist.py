from __future__ import annotations

import datetime
import json
import pathlib
from copy import deepcopy
from typing import TYPE_CHECKING

from hondana.artist import Artist
from hondana.http import HTTPClient
from hondana.utils import relationship_finder, to_snake_case


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
        obj_len = len(artist._manga_relationships)
        assert obj_len == len(PAYLOAD["data"]["relationships"])

    def test_manga_relationships(self):
        artist = clone_artist()
        rels = relationship_finder(PAYLOAD["data"]["relationships"], "manga", limit=None)

        assert artist.manga is not None
        assert len(rels) == len(artist.manga)

    def test_datetime_props(self):
        artist = clone_artist()

        assert artist.created_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["createdAt"])
        assert artist.updated_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["updatedAt"])
