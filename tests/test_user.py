from __future__ import annotations

import json
import pathlib
from copy import deepcopy
from typing import TYPE_CHECKING

from hondana.user import User
from hondana.utils import to_snake_case

if TYPE_CHECKING:
    from hondana.http import HTTPClient
    from hondana.types_.user import GetSingleUserResponse


PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "user.json"


PAYLOAD: GetSingleUserResponse = json.load(PATH.open())
HTTP: HTTPClient = object()  # type: ignore # this is just for test purposes.


def clone_user() -> User:
    t = deepcopy(PAYLOAD)
    return User(HTTP, t["data"])


class TestUser:
    def test_id(self) -> None:
        user = clone_user()
        assert user.id == PAYLOAD["data"]["id"]

    def test_attributes(self) -> None:
        user = clone_user()
        for item in PAYLOAD["data"]["attributes"]:
            getattr(user, to_snake_case(item))

    def test_relationships_length(self) -> None:
        user = clone_user()

        assert user._group_relationships is not None  # type: ignore # sorry, need this for test purposes
        obj_len = len(user._group_relationships)  # type: ignore # sorry, need this for test purposes

        assert "relationships" in PAYLOAD["data"]
        assert obj_len == len(PAYLOAD["data"]["relationships"])

    def test_attribute_matching(self) -> None:
        user = clone_user()

        assert user.username == PAYLOAD["data"]["attributes"]["username"]
        assert sorted(user.roles) == sorted(PAYLOAD["data"]["attributes"]["roles"])
