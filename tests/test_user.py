"""
The MIT License (MIT)

Copyright (c) 2021-Present AbstractUmbra

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

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
HTTP: HTTPClient = object()  # pyright: ignore[reportAssignmentType] # this is just for test purposes.


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

        assert user._group_relationships is not None  # pyright: ignore[reportPrivateUsage] # sorry, need this for test purposes
        obj_len = len(user._group_relationships)  # pyright: ignore[reportPrivateUsage] # sorry, need this for test purposes

        assert "relationships" in PAYLOAD["data"]
        assert obj_len == len(PAYLOAD["data"]["relationships"])

    def test_attribute_matching(self) -> None:
        user = clone_user()

        assert user.username == PAYLOAD["data"]["attributes"]["username"]
        assert sorted(user.roles) == sorted(PAYLOAD["data"]["attributes"]["roles"])
