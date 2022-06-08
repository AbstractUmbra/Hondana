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

from typing import TYPE_CHECKING, Optional

from .query import ScanlatorGroupIncludes
from .scanlator_group import ScanlatorGroup
from .utils import relationship_finder, require_authentication


if TYPE_CHECKING:
    from .http import HTTPClient
    from .types.relationship import RelationshipResponse
    from .types.scanlator_group import ScanlationGroupResponse
    from .types.user import UserResponse

__all__ = ("User",)


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
        self._group_relationships: list[ScanlationGroupResponse] = relationship_finder(
            relationships, "scanlation_group", limit=None
        )
        self.__groups: Optional[list[ScanlatorGroup]] = None

    def __repr__(self) -> str:
        return f"<User id={self.id!r} username={self.username!r}>"

    def __str__(self) -> str:
        return self.username

    def __eq__(self, other: User) -> bool:
        return isinstance(other, User) and self.id == other.id

    def __ne__(self, other: User) -> bool:
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

        data = await self._http._scanlation_group_list(
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

        await self._http._delete_user(self.id)
