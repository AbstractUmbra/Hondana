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

from typing import Literal, TypedDict


__all__ = (
    "TokenResponse",
    "LoginPayload",
    "RefreshPayload",
    "CheckPayload",
)


class TokenResponse(TypedDict):
    """
    session: :class:`str`

    refresh: :class:`str`
    """

    session: str
    refresh: str


class LoginPayload(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    token: :class:`~hondana.types.TokenResponse`
    """

    result: Literal["ok", "error"]
    token: TokenResponse


class RefreshPayload(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    token: :class:`~hondana.types.TokenResponse`

    message: :class:`str`
    """

    result: Literal["ok", "error"]
    token: TokenResponse
    message: str


class CheckPayload(TypedDict):
    """
    result: Literal[``"ok"``]

    isAuthenticated: :class:`bool`

    roles: List[:class:`str`]

    permissions: List[:class:`str`]
    """

    result: Literal["ok"]
    isAuthenticated: bool
    roles: list[str]
    permissions: list[str]
