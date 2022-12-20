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
from typing import TYPE_CHECKING, Optional

from .query import ScanlatorGroupIncludes
from .scanlator_group import ScanlatorGroup
from .utils import RelationshipResolver, require_authentication


if TYPE_CHECKING:
    from .http import HTTPClient
    from .types_.relationship import RelationshipResponse
    from .types_.scanlator_group import ScanlationGroupResponse
    from .types_.token import TokenPayload
    from .types_.user import UserResponse

__all__ = ("User",)


class UserInfo:
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
        return f"<Permissions type={self.type!r} issuer={self.issuer!r} audience={self.audience!r} issued_at={self.issued_at} not_before={self.not_before} expires={self.expires} user_id={self.user_id!r} sid={self.sid!r}>"


class User:
    """
    A class representing a user from the MangaDex API.

    Attributes
    -----------
    id: :class:`str`
        The user's UUID.
    username: :class:`str`
        The user's username.
    version: :class:`int`
        The user's version revision.
    roles: List[:class:`str`]
        The list of roles this person has.


    .. note::
        Unlike most other api objects, this type does not have related relationship properties due to not returning a full ``relationships`` key.


    """

    __slots__ = (
        "_http",
        "_data",
        "_attributes",
        "_relationships",
        "id",
        "username",
        "version",
        "roles",
        "_group_relationships",
        "__groups",
    )

    def __init__(self, http: HTTPClient, payload: UserResponse) -> None:
        self._http = http
        self._data = payload
        self._attributes = self._data["attributes"]
        relationships: list[RelationshipResponse] = self._data.pop("relationships", [])
        self.id: str = self._data["id"]
        self.username: str = self._attributes["username"]
        self.version: int = self._attributes["version"]
        self.roles: list[str] = self._attributes["roles"]
        self._group_relationships: list[ScanlationGroupResponse] = RelationshipResolver["ScanlationGroupResponse"](
            relationships, "scanlation_group"
        ).resolve()
        self.__groups: Optional[list[ScanlatorGroup]] = None

    def __repr__(self) -> str:
        return f"<User id={self.id!r} username={self.username!r}>"

    def __str__(self) -> str:
        return self.username

    def __eq__(self, other: object) -> bool:
        return isinstance(other, User) and self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @property
    def url(self) -> str:
        """The URL to this user.

        Returns
        --------
        :class:`str`
            The URL of the user.
        """
        return f"https://mangadex.org/user/{self.id}"

    async def get_scanlator_groups(self) -> Optional[list[ScanlatorGroup]]:
        """|coro|

        This method will fetch the scanlator groups of this user from the API.

        Returns
        --------
        Optional[List[:class:`~hondana.ScanlatorGroup`]]
            The list of groups for this user, if any.
        """
        if not self._group_relationships:
            return

        ids = [r["id"] for r in self._group_relationships]

        data = await self._http.scanlation_group_list(
            limit=100, offset=0, ids=ids, name=None, focused_language=None, includes=ScanlatorGroupIncludes(), order=None
        )

        fmt: list[ScanlatorGroup] = [ScanlatorGroup(self._http, payload) for payload in data["data"]]
        if not fmt:
            return

        self.__groups = fmt
        return self.__groups

    @require_authentication
    async def delete(self) -> None:
        """|coro|

        This method will delete a user from the MangaDex API.

        Raises
        -------
        :exc:`Forbidden`
            The response returned an error due to authentication failure.
        :exc:`NotFound`
            The user specified cannot be found.
        """

        await self._http.delete_user(self.id)
