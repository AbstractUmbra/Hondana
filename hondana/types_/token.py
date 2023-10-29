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

__all__ = ("TokenPayload",)


class _InnerAccountData(TypedDict):
    """
    roles: list[:class:`str`]
        The list of roles for the current session state
    """

    roles: list[str]


class _InnerSessionState(TypedDict):
    """
    account: :class:`_InnerAccountData`
        The current session account data
    """

    account: _InnerAccountData


class _BaseToken(TypedDict):
    exp: int
    iat: int
    jti: str
    iss: Literal["https://auth.mangadex.org/realms/mangadex"]
    aud: Literal["https://auth.mangadex.org/realms/mangadex"]
    sub: str
    typ: Literal["Bearer", "Refresh"]
    azp: str
    scope: str
    sid: str


class TokenPayload(_BaseToken):
    """
    typ: Literal[``Bearer``]

    iss: Literal[``https://auth.mangadex.org/realms/mangadex``]
        Issuer name

    aud: Literal[``account``]
        Token audience

    iat: :class:`int`
        Time token was issued in UTC timestamp

    exp: :class:`int`
        Expiring time in UTC timestamp

    sid: :class:`str`
        Session UUID

    auth_time: :class:`int`
        Time when authentication occurred in UTC timestamp.

    jti: :class:`str`
        JWT unique identifier

    sub :class:`str`
        Token subject UUID.

    azp: :class:`str`
        Authorized party name

    session_state: dict[:class:`str`, :class:`_InnerSessionState`]
        The current session state data

    scope: :class:`str`
        A space delimited list of oauth scopes

    roles: list[:class:`str`]
        A list of roles the user has in the API

    groups: :class:`str`
        A space delimited string of groups one has in the API

    preferred_username: :class:`str`
        The username of the current user

    email_address: :class:`str`
        The email address of the current user
    """

    act: str
    auth_time: int
    scope: str
    roles: list[str]
    groups: list[str]
    preferred_username: str
    email: str
    session_state: dict[str, _InnerSessionState]


class AuthToken(TypedDict):
    session_state: str


GetTokenPayload = TypedDict(
    "GetTokenPayload",
    {
        "access_token": str,
        "expires_in": int,
        "refresh_expires_in": int,
        "refresh_token": str,
        "token_type": Literal["Bearer"],
        "id_token": str,
        "not-before-policy": int,
        "session_state": str,
        "scope": str,
    },
)
