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
from typing import TYPE_CHECKING, Literal, Optional

from .user import User
from .utils import require_authentication


if TYPE_CHECKING:
    from .http import HTTPClient
    from .types import scanlator_group

__all__ = ("ScanlatorGroup",)


class ScanlatorGroup:
    """
    A class representing a Scanlator Group from the MangaDex API.

    Attributes
    -----------
    id: :class:`str`
        The UUID relating to this scanlator group.
    type: Literal[``"scanlation_group"``]
        The raw type of item from the API.
    name: :class:`str`
        The name of the scanlator group.
    website: :class:`str`
        The website of this scanlator group.
    irc_server: :class:`str`
        The IRC server for this scanlator group.
    irc_channel: :class:`str`
        The IRC channel for this scanlator group.
    discord: :class:`str`
        The Discord server for this scanlator group.
    contact_email: :class:`str`
        The contact email for this scanlator group.
    description: :class:`str`
        The description of this scanlator group.
    locked: :class:`bool`
        If this scanlator group is considered 'locked' or not.
    version: :class:`int`
        The version revision of this scanlator group.
    """

    __slots__ = (
        "_http",
        "id",
        "type",
        "_data",
        "_attributes",
        "_relationships",
        "name",
        "_leader",
        "_members",
        "website",
        "irc_server",
        "irc_channel",
        "discord",
        "contact_email",
        "description",
        "locked",
        "official",
        "version",
        "_created_at",
        "_updated_at",
    )

    def __init__(self, http: HTTPClient, payload: scanlator_group.GetScanlationGroupResponse) -> None:
        self._http = http
        data = payload["data"]
        attributes = data["attributes"]
        relationships = data["relationships"]
        self.id: str = data["id"]
        self.type: Literal["scanlation_group"] = data["type"]
        self._data = data
        self._attributes = attributes
        self._relationships = relationships
        self.name: str = attributes["name"]
        self._leader = attributes.get("leader", None)
        self._members = attributes.get("members", None)
        self.website: Optional[str] = attributes["website"]
        self.irc_server: Optional[str] = attributes["ircServer"]
        self.irc_channel: Optional[str] = attributes["ircServer"]
        self.discord: Optional[str] = attributes["discord"]
        self.contact_email: Optional[str] = attributes["contactEmail"]
        self.description: Optional[str] = attributes["description"]
        self.locked: bool = attributes.get("locked", False)
        self.official: bool = attributes["official"]
        self.version: int = attributes["version"]
        self._created_at = attributes["createdAt"]
        self._updated_at = attributes["updatedAt"]

    def __repr__(self) -> str:
        return f"<ScanlatorGroup id='{self.id}' name='{self.name}'>"

    def __str__(self) -> str:
        return self.name

    @property
    def created_at(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._created_at)

    @property
    def updated_at(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._updated_at)

    @property
    def leader(self) -> Optional[User]:
        if self._leader:
            return User(self._http, self._leader)
        return None

    @property
    def members(self) -> Optional[list[User]]:
        if self._members:
            return [User(self._http, payload) for payload in self._members]
        return None

    @require_authentication
    async def delete(self) -> None:
        """|coro|

        This method will delete the current scanlation group.

        Raises
        -------
        :exc:`Forbidden`
            You are not authorized to delete this scanlation group.
        :exc:`NotFound`
            The scanlation group cannot be found, likely due to an incorrect ID.
        """
        await self._http._delete_scanlation_group(self.id)

    @require_authentication
    async def follow(self) -> None:
        """|coro|

        This method will follow the current scanlation group.

        Raises
        -------
        :exc:`NotFound`
            The scanlation group cannot be found, likely due to an incorrect ID.
        """
        await self._http._follow_scanlation_group(self.id)

    @require_authentication
    async def unfollow(self) -> None:
        """|coro|

        This method will unfollow the current scanlation group.

        Raises
        -------
        :exc:`NotFound`
            The scanlation group cannot be found, likely due to an incorrect ID.
        """
        await self._http._unfollow_scanlation_group(self.id)
