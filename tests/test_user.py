from __future__ import annotations

import json
import pathlib
from copy import deepcopy
from typing import TYPE_CHECKING

from hondana.http import HTTPClient
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

        assert user._group_relationships is not None
        obj_len = len(user._group_relationships)

        assert obj_len == len(PAYLOAD["data"]["relationships"])

    def test_attribute_matching(self):
        user = clone_user()

        assert user.username == PAYLOAD["data"]["attributes"]["username"]
        assert sorted(user.roles) == sorted(PAYLOAD["data"]["attributes"]["roles"])
