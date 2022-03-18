from __future__ import annotations

import json
import pathlib
from copy import deepcopy
from typing import TYPE_CHECKING

from hondana.http import HTTPClient
from hondana.relationship import Relationship
from hondana.scanlator_group import ScanlatorGroup
from hondana.utils import to_snake_case


if TYPE_CHECKING:
    from hondana.types.scanlator_group import GetSingleScanlationGroupResponse

PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "scanlator_group.json"

PAYLOAD: GetSingleScanlationGroupResponse = json.load(open(PATH, "r"))
HTTP: HTTPClient = HTTPClient(username=None, password=None, email=None)


def clone_group() -> ScanlatorGroup:
    t = deepcopy(PAYLOAD)
    return ScanlatorGroup(HTTP, t["data"])


class TestScanlatorGroup:
    def test_id(self):
        group = clone_group()
        assert group.id == PAYLOAD["data"]["id"]

    def test_attributes(self):
        group = clone_group()

        for item in PAYLOAD["data"]["attributes"]:
            if item == "publishDelay":
                item = "_publish_delay"  # we made this a property to allow manipulation
            assert hasattr(group, to_snake_case(item))

    def test_relationship_length(self):
        group = clone_group()

        assert len(group.relationships) == len(PAYLOAD["data"]["relationships"])

    def test_sub_relationship_create(self):
        group = clone_group()
        ret: list[Relationship] = [Relationship(relationship) for relationship in deepcopy(group._relationships)]

        assert len(ret) == len(group.relationships)

    def test_cached_slot_property_relationships(self):
        group = clone_group()
        assert not hasattr(group, "_cs_relationships")
        group.relationships
        assert hasattr(group, "_cs_relationships")
