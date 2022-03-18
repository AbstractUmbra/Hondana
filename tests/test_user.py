from __future__ import annotations

import json
import pathlib
from copy import deepcopy
from typing import TYPE_CHECKING

from hondana.http import HTTPClient
from hondana.relationship import Relationship
from hondana.user import User
from hondana.utils import to_snake_case


if TYPE_CHECKING:
    from hondana.types.user import GetSingleUserResponse


PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "user.json"


PAYLOAD: GetSingleUserResponse = json.load(open(PATH, "r"))
HTTP: HTTPClient = HTTPClient(username=None, password=None, email=None)


def clone_user() -> User:
    t = deepcopy(PAYLOAD)
    return User(HTTP, t["data"])


class TestUser:
    def test_id(self):
        user = clone_user()
        assert user.id == PAYLOAD["data"]["id"]

    def test_attributes(self):
        user = clone_user()
        for item in PAYLOAD["data"]["attributes"]:
            getattr(user, to_snake_case(item))

    def test_relationships_length(self):
        user = clone_user()

        assert len(user.relationships) == len(PAYLOAD["data"]["relationships"])

    def test_sub_relationship_create(self):
        user = clone_user()
        ret: list[Relationship] = [Relationship(relationship) for relationship in deepcopy(user._relationships)]

        assert len(ret) == len(user.relationships)

    def test_attribute_matching(self):
        user = clone_user()

        assert user.username == PAYLOAD["data"]["attributes"]["username"]
        assert sorted(user.roles) == sorted(PAYLOAD["data"]["attributes"]["roles"])
