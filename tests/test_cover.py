from __future__ import annotations

import datetime
import json
import pathlib
from copy import deepcopy
from typing import TYPE_CHECKING

from hondana.cover import Cover
from hondana.utils import RelationshipResolver, to_snake_case

if TYPE_CHECKING:
    from hondana.http import HTTPClient
    from hondana.types_.cover import GetSingleCoverResponse
    from hondana.types_.user import UserResponse


PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "cover.json"

PAYLOAD: GetSingleCoverResponse = json.load(PATH.open())
HTTP: HTTPClient = object()  # type: ignore # this is just for test purposes.


def clone_cover() -> Cover:
    t = deepcopy(PAYLOAD)
    return Cover(HTTP, t["data"])


class TestCover:
    def test_id(self) -> None:
        cover = clone_cover()
        assert cover.id == PAYLOAD["data"]["id"]

    def test_attributes(self) -> None:
        cover = clone_cover()
        for item in PAYLOAD["data"]["attributes"]:
            getattr(cover, to_snake_case(item))

    def test_uploader(self) -> None:
        cover = clone_cover()

        assert cover.uploader is not None
        assert "relationships" in PAYLOAD["data"]
        rel = RelationshipResolver["UserResponse"](PAYLOAD["data"]["relationships"], "user").resolve()[0]
        assert rel is not None
        assert cover.uploader.id == rel["id"]

    def test_url(self) -> None:
        cover = clone_cover()

        cover.url()

        cover.url(256)

        cover.url(512)

    def test_datetime_properties(self) -> None:
        cover = clone_cover()

        assert cover.created_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["createdAt"])
        assert cover.updated_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["updatedAt"])
