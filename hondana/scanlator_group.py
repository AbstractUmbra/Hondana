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
    from .types.scanlator_group import ScanlationGroupResponse

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
    alt_names: List[:class:`str`]
        The alternate names for this group, if any.
    website: :class:`str`
        The website of this scanlator group.
    irc_server: :class:`str`
        The IRC server for this scanlator group.
    irc_channel: :class:`str`
        The IRC channel for this scanlator group.
    discord: :class:`str`
        The Discord server for this scanlator group.
    focused_language: Optional[List[str]]
        The scanlator group's focused languages, if any.
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
        "_data",
        "_attributes",
        "_relationships",
        "id",
        "type",
        "name",
        "alt_names",
        "_leader",
        "_members",
        "website",
        "irc_server",
        "irc_channel",
        "discord",
        "focused_language",
        "contact_email",
        "description",
        "locked",
        "official",
        "version",
        "_created_at",
        "_updated_at",
    )

    def __init__(self, http: HTTPClient, payload: ScanlationGroupResponse) -> None:
        self._http = http
        self._data = payload
        self._attributes = self._data["attributes"]
        relationships = self._data["relationships"]
        self.id: str = self._data["id"]
        self.type: Literal["scanlation_group"] = self._data["type"]
        self._relationships = relationships
        self.name: str = self._attributes["name"]
        self.alt_names: list[str] = self._attributes["altNames"]
        self._leader = self._attributes.get("leader", None)
        self._members = self._attributes.get("members", None)
        self.website: Optional[str] = self._attributes["website"]
        self.irc_server: Optional[str] = self._attributes["ircServer"]
        self.irc_channel: Optional[str] = self._attributes["ircServer"]
        self.discord: Optional[str] = self._attributes["discord"]
        self.focused_language: Optional[list[str]] = self._attributes["focusedLanguage"]
        self.contact_email: Optional[str] = self._attributes["contactEmail"]
        self.description: Optional[str] = self._attributes["description"]
        self.locked: bool = self._attributes.get("locked", False)
        self.official: bool = self._attributes["official"]
        self.version: int = self._attributes["version"]
        self._created_at = self._attributes["createdAt"]
        self._updated_at = self._attributes["updatedAt"]

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
            return User(self._http, self._leader["data"])
        return None

    @property
    def members(self) -> Optional[list[User]]:
        if self._members:
            return [User(self._http, payload["data"]) for payload in self._members]
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
