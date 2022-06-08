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
from typing import TYPE_CHECKING, Optional, Union

from .utils import MISSING, iso_to_delta, relationship_finder, require_authentication


if TYPE_CHECKING:
    from .http import HTTPClient
    from .types.common import LanguageCode
    from .types.relationship import RelationshipResponse
    from .types.scanlator_group import ScanlationGroupResponse
    from .types.user import UserResponse
    from .user import User

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
    focused_languages: Optional[List[str]]
        The scanlator group's focused languages, if any.
    contact_email: :class:`str`
        The contact email for this scanlator group.
    description: :class:`str`
        The description of this scanlator group.
    twitter: Optional[:class:`str`]
        The twitter URL of the group, if any.
    manga_updates: Optional[:class:`str`]
        The URL where the group posts their updates, if any.
    locked: :class:`bool`
        If this scanlator group is considered 'locked' or not.
    official: :class:`bool`
        Whether the group is official or not.
    verified: :class:`bool`
        Whether this group is verified or not.
    inactive: :class:`bool`
        Whether this group is inactive or not.
    version: :class:`int`
        The version revision of this scanlator group.
    """

    __slots__ = (
        "_http",
        "_data",
        "_attributes",
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
        "manga_updates",
        "locked",
        "official",
        "verified",
        "inactive",
        "version",
        "_created_at",
        "_updated_at",
        "_publish_delay",
        "_leader_relationship",
        "_member_relationships",
        "__leader",
        "__members",
    )

    def __init__(self, http: HTTPClient, payload: ScanlationGroupResponse) -> None:
        self._http = http
        self._data = payload
        self._attributes = self._data["attributes"]
        self.id: str = self._data["id"]
        relationships: list[RelationshipResponse] = self._data.pop("relationships", [])
        self.name: str = self._attributes["name"]
        self.alt_names: list[str] = self._attributes["altNames"]
        self.website: Optional[str] = self._attributes["website"]
        self.irc_server: Optional[str] = self._attributes["ircServer"]
        self.irc_channel: Optional[str] = self._attributes["ircServer"]
        self.discord: Optional[str] = self._attributes["discord"]
        self.focused_languages: Optional[list[str]] = self._attributes.get("focusedLanguages")
        self.contact_email: Optional[str] = self._attributes["contactEmail"]
        self.description: Optional[str] = self._attributes["description"]
        self.twitter: Optional[str] = self._attributes["twitter"]
        self.manga_updates: Optional[str] = self._attributes["mangaUpdates"]
        self.locked: bool = self._attributes.get("locked", False)
        self.official: bool = self._attributes["official"]
        self.verified: bool = self._attributes["verified"]
        self.inactive: bool = self._attributes["inactive"]
        self.version: int = self._attributes["version"]
        self._created_at = self._attributes["createdAt"]
        self._updated_at = self._attributes["updatedAt"]
        self._publish_delay: str = self._attributes["publishDelay"]
        self._leader_relationship: Optional[UserResponse] = relationship_finder(relationships, "leader", limit=1)
        self._member_relationships: list[UserResponse] = relationship_finder(relationships, "member", limit=None)
        self.__leader: Optional[User] = None
        self.__members: Optional[list[User]] = None

    def __repr__(self) -> str:
        return f"<ScanlatorGroup id={self.id!r} name={self.name!r}>"

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: ScanlatorGroup) -> bool:
        return isinstance(other, ScanlatorGroup) and self.id == other.id

    def __ne__(self, other: ScanlatorGroup) -> bool:
        return not self.__eq__(other)

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

    @property
    def url(self) -> str:
        """The URL to this scanlator group.

        Returns
        --------
        :class:`str`
            The URL of the scanlator group.
        """
        return f"https://mangadex.org/group/{self.id}"

    @property
    def publish_delay(self) -> Optional[datetime.timedelta]:
        """The publishing delay of this scanlation group.

        Returns
        --------
        Optional[:class:`datetime.timedelta`]
            The default timedelta offset at which this group releases their chapters, if any.
        """
        if self._publish_delay:
            return iso_to_delta(self._publish_delay)

    @property
    def leader(self) -> Optional[User]:
        """The leader of this scanlation group, if any.

        Returns
        --------
        Optional[:class:`~hondana.User`]
            The leader of the scanlation group.
        """
        if self.__leader is not None:
            return self.__leader

        if not self._leader_relationship:
            return

        if "attributes" in self._leader_relationship:
            from .user import User

            user = User(self._http, self._leader_relationship)
            self.__leader = user
            return self.__leader

    @leader.setter
    def leader(self, other: User) -> None:
        if isinstance(other, User):
            self.__leader = other

    @property
    def members(self) -> Optional[list[User]]:
        """The members of this scanlation group, if any.

        Returns
        --------
        Optional[List[:class:`~hondana.User`]]
            The members of the scanlation group.
        """
        if self.__members is not None:
            return self.__members

        if not self._member_relationships:
            return

        fmt: list[User] = []

        for relationship in self._member_relationships:
            from .user import User

            if "attributes" in relationship:
                fmt.append(User(self._http, relationship))

        if not fmt:
            return

        self.__members = fmt
        return self.__members

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
        if self.leader is not None:
            return self.leader

        if not self._leader_relationship:
            return

        leader_id = self._leader_relationship["id"]
        data = await self._http._get_user(leader_id)

        from .user import User

        leader = User(self._http, data["data"])
        self.__leader = leader
        return self.__leader

    async def get_members(self) -> Optional[list[User]]:
        """|coro|

        This method will return a list of members of the scanlation group, if present.

        .. note::
            If the ScanlatorGroup was requested with the ``member`` includes, this method will not make API calls.


        .. note::
            If this object was created as part of another object's ``includes`` then this will return None.
            This is due to having no relationship data.

        Returns
        --------
        Optional[List[User]]
            The list of members of the scanlation group.
        """
        if self.members is not None:
            return self.members

        if not self._member_relationships:
            return

        ids = [r["id"] for r in self._member_relationships]

        data = await self._http._user_list(limit=100, offset=0, ids=ids, username=None, order=None)

        self.__members = [User(self._http, payload) for payload in data["data"]]
        return self.__members

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

    @require_authentication
    async def update(
        self,
        *,
        name: Optional[str] = None,
        leader: Optional[str] = None,
        members: Optional[list[str]] = None,
        website: Optional[str] = MISSING,
        irc_server: Optional[str] = MISSING,
        irc_channel: Optional[str] = MISSING,
        discord: Optional[str] = MISSING,
        contact_email: Optional[str] = MISSING,
        description: Optional[str] = MISSING,
        twitter: Optional[str] = MISSING,
        manga_updates: Optional[str] = MISSING,
        focused_languages: list[LanguageCode] = MISSING,
        inactive: Optional[bool] = None,
        locked: Optional[bool] = None,
        publish_delay: Optional[Union[str, datetime.timedelta]] = MISSING,
        version: int,
    ) -> ScanlatorGroup:
        """|coro|

        This method will update a scanlation group within the MangaDex API.

        Parameters
        -----------
        name: Optional[:class:`str`]
            The name to update the group with.
        leader: Optional[:class:`str`]
            The UUID of the leader to update the group with.
        members: Optional[:class:`str`]
            A list of UUIDs relating to the members to update the group with.
        website: Optional[:class:`str`]
            The website to update the group with.
        irc_server: Optional[:class:`str`]
            The IRC Server to update the group with.
        irc_channel: Optional[:class:`str`]
            The IRC Channel to update the group with.
        discord: Optional[:class:`str`]
            The discord server to update the group with.
        contact_email: Optional[:class:`str`]
            The contact email to update the group with.
        description: Optional[:class:`str`]
            The new description to update the group with.
        twitter: Optional[:class:`str`]
            The new twitter url to update the group with.
        manga_updates: Optional[:class:`str`]
            The URL for this group's manga updates page, if any.
        focused_languages: Optional[List[:class:`~hondana.types.common.LanguageCode`]]
            The new list of language codes to update the group with.
        inactive: Optional[:class:`bool`]
            If the group is inactive or not.
        locked: Optional[:class:`bool`]
            Update the lock status of this scanlator group.
        publish_delay: Optional[Union[:class:`str`, :class:`datetime.timedelta`]]
            The publishing delay to add to all group releases.
        version: :class:`int`
            The version revision of this scanlator group.


        .. note::
            The ``website``, ``irc_server``, ``irc_channel``, ``discord``, ``contact_email``, ``description``, ``twitter``, ``manga_updates``, ``focused_language`` and ``publish_delay``
            keys are all nullable in the API. To do so pass ``None`` explicitly to these keys.

        .. note::
            The ``publish_delay`` parameter must match the :class:`hondana.utils.MANGADEX_TIME_REGEX` pattern
            or be a valid ``datetime.timedelta``.

        Raises
        -------
        :exc:`BadRequest`
            The request body was malformed
        :exc:`Forbidden`
            You are not authorized to update this scanlation group.
        :exc:`NotFound`
            The passed scanlation group ID cannot be found.

        Returns
        --------
        :class:`ScanlatorGroup`
            The group returned from the API after its update.
        """
        data = await self._http._update_scanlation_group(
            self.id,
            name=name,
            leader=leader,
            members=members,
            website=website,
            irc_server=irc_server,
            irc_channel=irc_channel,
            discord=discord,
            contact_email=contact_email,
            description=description,
            twitter=twitter,
            manga_updates=manga_updates,
            focused_languages=focused_languages,
            inactive=inactive,
            locked=locked,
            publish_delay=publish_delay,
            version=version,
        )

        return self.__class__(self._http, data["data"])
