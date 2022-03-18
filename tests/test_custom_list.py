from __future__ import annotations

import json
import pathlib
from copy import deepcopy
from typing import TYPE_CHECKING

from hondana.custom_list import CustomList
from hondana.http import HTTPClient
from hondana.relationship import Relationship
from hondana.utils import to_snake_case


if TYPE_CHECKING:
    from hondana.types.custom_list import GetSingleCustomListResponse

PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "custom_list.json"

PAYLOAD: GetSingleCustomListResponse = json.load(open(PATH, "r"))
HTTP: HTTPClient = HTTPClient(username=None, password=None, email=None)


def clone_custom_list() -> CustomList:
    t = deepcopy(PAYLOAD)
    return CustomList(HTTP, t["data"])


class TestCustomList:
    def test_id(self):
        custom_list = clone_custom_list()

        assert custom_list.id == PAYLOAD["data"]["id"]

    def test_attributes(self):
        custom_list = clone_custom_list()
        for item in PAYLOAD["data"]["attributes"]:
            getattr(custom_list, to_snake_case(item))

    def test_cached_slot_property_relationships(self):
        custom_list = clone_custom_list()

        assert not hasattr(custom_list, "_cs_relationships")

        custom_list.relationships

        assert hasattr(custom_list, "_cs_relationships")

    def test_relationships(self):
        custom_list = clone_custom_list()

        ret: list[Relationship] = [Relationship(relationship) for relationship in deepcopy(custom_list._relationships)]

        assert len(custom_list.relationships) == len(ret)

    def test_owner(self):
        custom_list = clone_custom_list()

        assert custom_list.owner is not None
        assert custom_list.owner.id == "fd14373d-6c5f-483a-bf40-1df9326d68d2"
