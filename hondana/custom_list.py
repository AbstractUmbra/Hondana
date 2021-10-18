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

from .user import User
from .utils import require_authentication


if TYPE_CHECKING:
    from .http import HTTPClient
    from .types.custom_list import CustomListResponse, CustomListVisibility


__all__ = ("CustomList",)


class CustomList:
    """A class representing a CustomList returned from the MangaDex API.

    Attributes
    -----------
    id: :class:`str`
        The UUID relating to this custom list.
    name: :class:`str`
        The name of this custom list.
    visibility: :class:`~hondana.types.CustomListVisibility`
        The visibility of this custom list.
    version: :class:`int`
        The version revision of this custom list.
    """

    __slots__ = (
        "_http",
        "_data",
        "_attributes",
        "_relationships",
        "id",
        "name",
        "visibility",
        "version",
    )

    def __init__(self, http: HTTPClient, payload: CustomListResponse) -> None:
        self._http = http
        self._data = payload
        self._attributes = self._data["attributes"]
        self._relationships = self._data["relationships"]
        self.id: str = self._data["id"]
        self.name: str = self._attributes["name"]
        self.visibility: CustomListVisibility = self._attributes["visibility"]
        self.version: int = self._attributes["version"]

    def __repr__(self) -> str:
        return f"<CustomList id='{self.id}' name='{self.name}'>"

    def __str__(self) -> str:
        return self.name

    async def get_owner(self) -> Optional[User]:
        owner_key = None
        for relationship in self._relationships:
            if relationship["type"] == "user":
                owner_key = relationship
                break

        if owner_key is None:
            return None

        if "attributes" in owner_key:
            return User(self._http, owner_key)

        data = await self._http._get_user(owner_key["id"])
        return User(self._http, data["data"])

    @require_authentication
    async def update(
        self,
        *,
        name: Optional[str] = None,
        visibility: Optional[CustomListVisibility] = None,
        manga: Optional[list[str]] = None,
        version: int,
    ) -> CustomList:
        """|coro|

        This method will update the current custom list within the MangaDex API.

        Parameters
        -----------
        name: Optional[:class:`str`]
            The name we wish to edit the custom list with.
        visibility: Optional[:class:`~hondana.types.CustomListVisibility`]
            The visibility we wish to edit the custom list with.
        manga: Optional[List[:class:`str`]]
            The list of manga IDs to edit this custom list with.
        version: :class:`int`
            The version revision of this custom list.


        .. note::
            Updating a custom list is an atomic action.
            Passing the ``manga`` key here will overwrite the manga in this custom list.

        Raises
        -------
        :exc:`BadRequest`
            The request body was malformed.
        :exc:`Forbidden`
            You are not authorized to edit this custom list.
        :exc:`NotFound`
            The custom list was not found, or one of the manga passed was not found.

        Returns
        --------
        :class:`CustomList`
            The returned custom list after it was updated.
        """
        data = await self._http._update_custom_list(self.id, name=name, visibility=visibility, manga=manga, version=version)

        return self.__class__(self._http, data["data"])

    @require_authentication
    async def delete_custom_list(self) -> None:
        """|coro|

        This method will delete the current custom list from the MangaDex API.

        Raises
        -------
        :exc:`Forbidden`
            You are not authorized to delete this custom list.
        :exc:`NotFound`
            The custom list with this UUID was not found.
        """
        await self._http._delete_custom_list(self.id)
