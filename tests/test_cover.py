from __future__ import annotations

import datetime
import json
import pathlib
from copy import deepcopy
from typing import TYPE_CHECKING

from hondana.cover import Cover
from hondana.http import HTTPClient
from hondana.utils import to_snake_case


if TYPE_CHECKING:
    from hondana.types.cover import GetSingleCoverResponse


PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "cover.json"

PAYLOAD: GetSingleCoverResponse = json.load(open(PATH, "r"))
HTTP: HTTPClient = HTTPClient(username=None, password=None, email=None)


def clone_cover() -> Cover:
    t = deepcopy(PAYLOAD)
    return Cover(HTTP, t["data"])


class TestCover:
    def test_id(self):
        cover = clone_cover()
        assert cover.id == PAYLOAD["data"]["id"]

    def test_attributes(self):
        cover = clone_cover()
        for item in PAYLOAD["data"]["attributes"]:
            getattr(cover, to_snake_case(item))

    def test_slot_property_relationships(self):
        cover = clone_cover()

        assert not hasattr(cover, "_cs_relationships")

        cover.relationships

        assert hasattr(cover, "_cs_relationships")

    def test_url(self):
        cover = clone_cover()

        cover.url()

        cover.url(256)

        cover.url(512)

    def test_datetime_properties(self):
        cover = clone_cover()

        assert cover.created_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["createdAt"])
        assert cover.updated_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["updatedAt"])
