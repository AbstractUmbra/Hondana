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

from typing import TYPE_CHECKING

from .utils import require_authentication


if TYPE_CHECKING:
    from .http import HTTPClient
    from .types.relationship import RelationshipResponse
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
    )

    def __init__(self, http: HTTPClient, payload: UserResponse) -> None:
        self._http = http
        self._data = payload
        self._attributes = self._data["attributes"]
        self._relationships: list[RelationshipResponse] = self._data.pop("relationships", [])
        self.id: str = self._data["id"]
        self.username: str = self._attributes["username"]
        self.version: int = self._attributes["version"]
        self.roles: list[str] = self._attributes["roles"]

    def __repr__(self) -> str:
        return f"<User id='{self.id}' username='{self.username}'>"

    def __str__(self) -> str:
        return self.username

    def __eq__(self, other: User) -> bool:
        return isinstance(other, User) and self.id == other.id

    def __ne__(self, other: User) -> bool:
        return not self.__eq__(other)

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
