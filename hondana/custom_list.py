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

from .enums import CustomListVisibility
from .manga import Manga
from .query import MangaIncludes
from .user import User
from .utils import RelationshipResolver, require_authentication

if TYPE_CHECKING:
    from .http import HTTPClient
    from .types_.custom_list import CustomListResponse
    from .types_.manga import MangaResponse
    from .types_.relationship import RelationshipResponse
    from .types_.user import UserResponse


__all__ = ("CustomList",)


class CustomList:
    """A class representing a CustomList returned from the MangaDex API.

    Attributes
    ----------
    id: :class:`str`
        The UUID relating to this custom list.
    name: :class:`str`
        The name of this custom list.
    visibility: :class:`~hondana.CustomListVisibility`
        The visibility of this custom list.
    pinned: :class:`bool`
        Whether this custom list is pinned or not.
        Defaults to ``False`` as this key is not always present.
    version: :class:`int`
        The version revision of this custom list.
    """

    __slots__ = (
        "__manga",
        "__owner",
        "_attributes",
        "_data",
        "_http",
        "_manga_relationships",
        "_owner_relationship",
        "id",
        "name",
        "pinned",
        "version",
        "visibility",
    )

    def __init__(self, http: HTTPClient, payload: CustomListResponse) -> None:
        self._http = http
        self._data = payload
        self._attributes = self._data["attributes"]
        relationships: list[RelationshipResponse] = self._data.pop("relationships", [])  # pyright: ignore[reportAssignmentType,reportArgumentType,reportUnknownArgumentType] # can't pop from a TypedDict
        self.id: str = self._data["id"]
        self.name: str = self._attributes["name"]
        self.visibility: CustomListVisibility = CustomListVisibility(self._attributes["visibility"])
        self.pinned: bool = self._attributes.get("pinned", False)
        self.version: int = self._attributes["version"]
        self._owner_relationship: UserResponse | None = RelationshipResolver["UserResponse"](relationships, "user").pop(
            with_fallback=True,
        )
        self._manga_relationships: list[MangaResponse] = RelationshipResolver["MangaResponse"](
            relationships,
            "manga",
        ).resolve()
        self.__owner: User | None = None
        self.__manga: list[Manga] | None = None

    def __repr__(self) -> str:
        return f"<CustomList id={self.id!r} name={self.name!r}>"

    def __str__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, CustomList) and self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @property
    def url(self) -> str:
        """The URL to this custom list.

        Returns
        -------
        :class:`str`
            The URL of the custom list.
        """
        return f"https://mangadex.org/list/{self.id}"

    @property
    def owner(self) -> User | None:
        """Returns the owner of this custom list.

        Returns
        -------
        Optional[:class:`~hondana.User`]
            The owner of this list, if any.
        """
        if self.__owner is not None:
            return self.__owner

        if not self._owner_relationship:
            return None

        if "attributes" in self._owner_relationship:
            self.__owner = User(self._http, self._owner_relationship)
            return self.__owner

        return None

    @owner.setter
    def owner(self, other: User) -> None:
        self.__owner = other

    @property
    def manga(self) -> list[Manga] | None:
        """Returns the of manga present in this custom list, if any.

        Returns
        -------
        Optional[List[:class:`~hondana.Manga`]]
            The list of manga present, if any.
        """
        if self.__manga is not None:
            return self.__manga

        if not self._manga_relationships:
            return None

        if fmt := [Manga(self._http, manga) for manga in self._manga_relationships if "attributes" in manga]:
            return fmt

        return None

    @manga.setter
    def manga(self, other: list[Manga]) -> None:
        self.__manga = other

    async def get_owner(self) -> User | None:
        """|coro|

        This method will make an API request to get the owner of a Custom List.

        Returns
        -------
        Optional[:class:`~hondana.User`]
            The owner of this list, if any.
        """
        if self.owner is not None:
            return self.owner

        if not self._owner_relationship:
            return None

        data = await self._http.get_user(self._owner_relationship["id"])
        self.__owner = User(self._http, data["data"])
        return self.__owner

    async def get_manga(self, *, limit: int | None = 100, offset: int = 0) -> list[Manga] | None:
        """|coro|

        This method will attempt to fetch the manga that are members of this custom list.

        Parameters
        ----------
        limit: Optional[:class:`int`]
            The amount of manga to fetch per request, defaults to ``100``.
        offset: :class:`int`
            The pagination offset to begin at. Defaults to ``0``.

        Returns
        -------
        Optional[List[:class:`~hondana.Manga`]]
        """
        if self.manga is not None:
            return self.manga

        if not self._manga_relationships:
            return None

        ids = [r["id"] for r in self._manga_relationships]

        data = await self._http.manga_list(
            limit=limit or 100,
            offset=offset,
            title=None,
            author_or_artist=None,
            authors=None,
            artists=None,
            year=None,
            included_tags=None,
            excluded_tags=None,
            status=None,
            original_language=None,
            excluded_original_language=None,
            available_translated_language=None,
            publication_demographic=None,
            ids=ids,
            content_rating=None,
            created_at_since=None,
            updated_at_since=None,
            order=None,
            includes=MangaIncludes(),
            has_available_chapters=None,
            has_unavailable_chapters=None,
            group=None,
        )

        if ret := [Manga(self._http, item) for item in data["data"]]:
            return ret

        return None

    @require_authentication
    async def update(
        self,
        *,
        name: str | None = None,
        visibility: CustomListVisibility | None = None,
        manga: list[str] | None = None,
        version: int,
    ) -> CustomList:
        """|coro|

        This method will update the current custom list within the MangaDex API.

        Parameters
        ----------
        name: Optional[:class:`str`]
            The name we wish to edit the custom list with.
        visibility: Optional[:class:`~hondana.CustomListVisibility`]
            The visibility we wish to edit the custom list with.
        manga: Optional[List[:class:`str`]]
            The list of manga IDs to edit this custom list with.
        version: :class:`int`
            The version revision of this custom list.


        .. note::
            Updating a custom list is an atomic action.
            Passing the ``manga`` key here will overwrite the manga in this custom list.

        Raises
        ------
        BadRequest
            The request body was malformed.
        Forbidden
            You are not authorized to edit this custom list.
        NotFound
            The custom list was not found, or one of the manga passed was not found.

        Returns
        -------
        :class:`CustomList`
            The returned custom list after it was updated.
        """  # noqa: DOC502 # raised in method call
        data = await self._http.update_custom_list(self.id, name=name, visibility=visibility, manga=manga, version=version)

        return self.__class__(self._http, data["data"])

    @require_authentication
    async def delete_custom_list(self) -> None:
        """|coro|

        This method will delete the current custom list from the MangaDex API.

        Raises
        ------
        Forbidden
            You are not authorized to delete this custom list.
        NotFound
            The custom list with this UUID was not found.
        """  # noqa: DOC502 # raised in method call
        await self._http.delete_custom_list(self.id)

    @require_authentication
    async def follow(self) -> None:
        """|coro|

        The method will follow a custom list within the MangaDex API.

        Raises
        ------
        Forbidden
            You are not authorized to follow this custom list.
        NotFound
            The specified custom list does not exist.
        """  # noqa: DOC502 # raised in method call
        await self._http.follow_custom_list(self.id)

    @require_authentication
    async def unfollow(self) -> None:
        """|coro|

        The method will unfollow a custom list within the MangaDex API.

        Raises
        ------
        Forbidden
            You are not authorized to unfollow this custom list.
        NotFound
            The specified custom list does not exist.
        """  # noqa: DOC502 # raised in method call
        await self._http.unfollow_custom_list(self.id)
