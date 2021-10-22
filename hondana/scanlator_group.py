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

from .user import User
from .utils import require_authentication


if TYPE_CHECKING:
    from .http import HTTPClient
    from .types.relationship import RelationshipResponse
    from .types.scanlator_group import ScanlationGroupResponse
    from .types.user import UserResponse

__all__ = ("ScanlatorGroup",)


class ScanlatorGroup:
    """
    A class representing a Scanlator Group from the MangaDex API.

    Attributes
    -----------
    id: :class:`str`
        The UUID relating to this scanlator group.
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
        "name",
        "alt_names",
        "website",
        "irc_server",
        "irc_channel",
        "discord",
        "focused_languages",
        "contact_email",
        "description",
        "twitter",
        "locked",
        "official",
        "verified",
        "version",
        "_created_at",
        "_updated_at",
    )

    def __init__(self, http: HTTPClient, payload: ScanlationGroupResponse) -> None:
        self._http = http
        self._data = payload
        self._attributes = self._data["attributes"]
        self.id: str = self._data["id"]
        self._relationships: Optional[list[RelationshipResponse]] = self._data.get("relationships")
        self.name: str = self._attributes["name"]
        self.alt_names: list[str] = self._attributes["altNames"]
        self.website: Optional[str] = self._attributes["website"]
        self.irc_server: Optional[str] = self._attributes["ircServer"]
        self.irc_channel: Optional[str] = self._attributes["ircServer"]
        self.discord: Optional[str] = self._attributes["discord"]
        self.focused_languages: Optional[list[str]] = self._attributes.get("focusedLanguages")
        self.contact_email: Optional[str] = self._attributes["contactEmail"]
        self.description: Optional[str] = self._attributes["description"]
        self.twitter: Optional[str] = self._attributes.get("twitter")  # TODO: Make a key lookup when the data exists.
        self.locked: bool = self._attributes.get("locked", False)
        self.official: bool = self._attributes["official"]
        self.verified: bool = self._attributes["verified"]
        self.version: int = self._attributes["version"]
        self._created_at = self._attributes["createdAt"]
        self._updated_at = self._attributes["updatedAt"]

    def __repr__(self) -> str:
        return f"<ScanlatorGroup id='{self.id}' name='{self.name}'>"

    def __str__(self) -> str:
        return self.name

    @property
    def created_at(self) -> datetime.datetime:
        """
        Returns the time when the ScanlatorGroup was created.

        Returns
        ---------
        :class:`datetime.datetime`
        """
        return datetime.datetime.fromisoformat(self._created_at)

    @property
    def updated_at(self) -> datetime.datetime:
        """
        Returns the time when the ScanlatorGroup was last updated.

        Returns
        ---------
        :class:`datetime.datetime`
        """
        return datetime.datetime.fromisoformat(self._updated_at)

    async def get_leader(self) -> Optional[User]:
        """|coro|

        This method will return the User representing the leader of the scanlation group.

        .. note::
            If the ScanlatorGroup was requested with the `leader` includes, then this method will not make an API call.


        .. note::
            If this object was created as part of another object's ``includes`` then this will return None.
            This is due to having no relationship data.


        Returns
        --------
        Optional[User]
            The leader of the ScanlatorGroup, if present.
        """
        if not self._relationships:
            return

        leader_key = None
        for relationship in self._relationships:
            if relationship["type"] == "leader":
                leader_key = relationship
                break

        if leader_key is None:
            return

        if "attributes" in leader_key:
            return User(self._http, leader_key)

        leader_id = leader_key["id"]
        leader = await self._http._get_user(leader_id)
        return User(self._http, leader["data"])

    async def get_members(self) -> Optional[list[User]]:
        """|coro|

        This method will return a list of members of the scanlation group, if present.

        .. note::
            If the ScanlatorGroup was requested with the ``member`` includes, this method will not make API calls.


        .. note::
            If this object was created as part of another object's ``includes`` then this will return None.
            This is due to having no relationship data.


        .. danger::
            Due to the nature of this request, this is N many API calls depending on the amount of members.
            It is *strongly* suggested you request the ScanlatorGroup with the ``member`` includes.


        Returns
        --------
        Optional[List[User]]
            The list of members of the scanlation group.
        """
        if not self._relationships:
            return

        members: list[User] = []
        _keys: list[UserResponse] = []

        for relationship in self._relationships:
            if relationship["type"] == "member":
                _keys.append(relationship)

        if not _keys:
            return None

        for key in _keys:
            if "attributes" in key:
                members.append(User(self._http, key))

        if members:
            return members

        for key in _keys:
            user = await self._http._get_user(key["id"])
            members.append(User(self._http, user["data"]))

        return members

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
