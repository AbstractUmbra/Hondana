from __future__ import annotations

import datetime
import json
import pathlib
from copy import deepcopy
from typing import TYPE_CHECKING

from hondana.http import HTTPClient
from hondana.scanlator_group import ScanlatorGroup
from hondana.utils import iso_to_delta, to_snake_case


if TYPE_CHECKING:
    from hondana.types_.scanlator_group import GetSingleScanlationGroupResponse

PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "scanlator_group.json"

PAYLOAD: GetSingleScanlationGroupResponse = json.load(open(PATH, "r"))
HTTP: HTTPClient = object()  # type: ignore # this is just for test purposes.


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

        assert group.members is not None
        assert group.leader is not None

        obj_len = len(group.members) + 1  # leader

        assert "relationships" in PAYLOAD["data"]
        assert obj_len == len(PAYLOAD["data"]["relationships"])

    def test_datetime_properties(self):
        group = clone_group()

        assert group.created_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["createdAt"])
        assert group.updated_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["updatedAt"])

        if group.publish_delay is not None or PAYLOAD["data"]["attributes"]["publishDelay"] is not None:
            assert group.publish_delay == iso_to_delta(PAYLOAD["data"]["attributes"]["publishDelay"])
