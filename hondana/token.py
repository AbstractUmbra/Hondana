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

import datetime
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .types.token import TokenPayload


__all__ = ("Permissions",)


class Permissions:
    """
    A helper class for the permission attributes of the logged-in user's token details.

    Attributes
    -----------
    type: Literal[``session``]
        The type of token we have received.
    issuer: Literal[``mangadex.org``]
        The issuer of the token.
    audience: Literal[``mangadex.org``]
        The target audience for the token.
    issued_at: :class:`datetime.datetime`
        When the token was issued.
    not_before: :class:`datetime.datetime`
        The datetime that the token is valid from.
    expires: :class:`datetime.datetime`
        When the token expires.
    user_id: :class:`str`
        The logged-in user's UUID.
    roles: List[:class:`str`]
        The list of roles the logged-in user has.
    permissions: List[:class:`str`]
        The list of permissions this user has.
    sid: :class:`str`
        At the moment I'm not too sure what this is...
    """

    __slots__ = (
        "type",
        "issuer",
        "audience",
        "issued_at",
        "not_before",
        "expires",
        "user_id",
        "roles",
        "permissions",
        "sid",
    )

    def __init__(self, payload: TokenPayload) -> None:
        self.type: str = payload["typ"]
        self.issuer: str = payload["iss"]
        self.audience: str = payload["aud"]
        self.issued_at: datetime.datetime = datetime.datetime.fromtimestamp(payload["iat"], datetime.timezone.utc)
        self.not_before: datetime.datetime = datetime.datetime.fromtimestamp(payload["nbf"], datetime.timezone.utc)
        self.expires: datetime.datetime = datetime.datetime.fromtimestamp(payload["exp"], datetime.timezone.utc)
        self.user_id: str = payload["uid"]
        self.roles: list[str] = payload["rol"]
        self.permissions: list[str] = payload["prm"]
        self.sid: str = payload["sid"]

    def __repr__(self) -> str:
        return f"<Permissions type={self.type} issuer={self.issuer} audience={self.issuer} issued_at={self.issued_at} not_before={self.not_before} expires={self.expires} user_id={self.user_id} sid={self.sid}>"
