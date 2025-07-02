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
from typing import TYPE_CHECKING, Literal

from .user import User
from .utils import MISSING, RelationshipResolver, Route, require_authentication

if TYPE_CHECKING:
    from .http import HTTPClient
    from .types_.common import LanguageCode
    from .types_.cover import CoverResponse
    from .types_.manga import MangaResponse
    from .types_.user import UserResponse


__all__ = ("Cover",)


class Cover:
    """A class representing a Cover returned from the MangaDex API.

    Attributes
    ----------
    id: :class:`str`
        The UUID associated with this cover.
    volume: Optional[:class:`str`]
        The volume attributed to this cover, if any.
    file_name: :class:`str`
        The file name of this cover.
    description: :class:`str`
        The description of this cover.
    version: :class:`int`
        The version revision of this Cover.
    """

    __slots__ = (
        "_attributes",
        "_created_at",
        "_data",
        "_http",
        "_manga_relationship",
        "_updated_at",
        "_uploader_relationship",
        "description",
        "file_name",
        "id",
        "locale",
        "version",
        "volume",
    )

    def __init__(self, http: HTTPClient, payload: CoverResponse) -> None:
        self._http = http
        self._data = payload
        self._attributes = self._data["attributes"]
        relationships = self._data.pop("relationships", [])
        self.id: str = self._data["id"]
        self.volume: str | None = self._attributes["volume"]
        self.file_name: str = self._attributes["fileName"]
        self.description: str | None = self._attributes["description"]
        self.locale: LanguageCode | None = self._attributes["locale"]
        self.version: int = self._attributes["version"]
        self._created_at = self._attributes["createdAt"]
        self._updated_at = self._attributes["updatedAt"]
        self._manga_relationship: MangaResponse | None = RelationshipResolver(relationships, "manga").pop(
            with_fallback=True,
        )
        self._uploader_relationship: UserResponse | None = RelationshipResolver(relationships, "user").pop(
            with_fallback=True,
        )

    def __repr__(self) -> str:
        return f"<Cover id={self.id!r} filename={self.file_name!r}>"

    def __str__(self) -> str:
        return self.file_name

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Cover) and self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @property
    def created_at(self) -> datetime.datetime:
        """When this cover was created.

        Returns
        -------
        :class:`datetime.datetime`
            The UTC datetime of when this cover was created.
        """
        return datetime.datetime.fromisoformat(self._created_at)

    @property
    def updated_at(self) -> datetime.datetime:
        """When this cover was last updated.

        Returns
        -------
        :class:`datetime.datetime`
            The UTC datetime of when this cover was last updated.
        """
        return datetime.datetime.fromisoformat(self._updated_at)

    @property
    def uploader(self) -> User | None:
        """The user who uploaded this cover.

        .. note::
            This is only populated if the Cover has populated relationships.

        Returns
        -------
        Optional[:class:`~hondana.User`]
            The user who uploaded this cover, if present.
        """
        if not self._uploader_relationship:
            return None

        if "attributes" in self._uploader_relationship:
            return User(self._http, self._uploader_relationship)

        return None

    def url(self, image_size: Literal[256, 512] | None = None, /, parent_id: str | None = None) -> str | None:
        """Method to return the Cover url.

        Due to the API structure, this will return ``None`` if the parent manga key is missing from the
        response relationships.

        Parameters
        ----------
        image_size: Optional[Literal[``256``, ``512``]]
            Defaults to ``None`` to return original quality.
            Specifies the return image dimensions.
        parent_id: Optional[:class:`str`]
            Parameter where you can potentially set or override the parent manga to skip relationship lookup.
            Useful for when Cover is part of something else's relationships, holding none of it's own.

        Returns
        -------
        Optional[:class:`str`]
            The Cover url.
        """
        manga_id = parent_id or (self._manga_relationship["id"] if self._manga_relationship else None)
        if manga_id is None:
            return None

        if image_size == 256:
            fmt = ".256.jpg"
        elif image_size == 512:
            fmt = ".512.jpg"
        else:
            fmt = ""

        return f"https://uploads.mangadex.org/covers/{manga_id}/{self.file_name}{fmt}"

    async def fetch_image(self, size: Literal[256, 512] | None = None, /) -> bytes | None:
        """|coro|

        This method depends on :attr:`url`, as such, it can return None.

        Parameters
        ----------
        size: Optional[Literal[``256``, ``512``]]
            Defaults to ``None`` to return original quality.
            Specifies the returned image size.

        Returns
        -------
        :class:`bytes`
            The raw image bytes.
        """
        url = self.url(size)
        if url is None:
            return None

        route = Route("GET", url)
        return await self._http.request(route)

    @require_authentication
    async def edit_cover(self, *, volume: str | None = MISSING, description: str | None = MISSING, version: int) -> Cover:
        """|coro|

        This method will edit the current cover on the MangaDex API.

        Parameters
        ----------
        volume: :class:`str`
            The volume identifier relating the cover will represent.
        description: Optional[:class:`str`]
            The description of the cover.
        version: :class:`int`
            The version revision of the cover.


        .. warning::
            The ``volume`` key is mandatory. You can pass ``None`` to null it in the API, but it must have a value.

        Raises
        ------
        TypeError
            The volume key was not given a value. This is required.
        BadRequest
            The request body was malformed.
        Forbidden
            The request returned an error due to authentication failure.

        Returns
        -------
        :class:`~hondana.Cover`
            The returned cover after the edit.
        """  # noqa: DOC502 # raised in method call
        data = await self._http.edit_cover(self.id, volume=volume, description=description, version=version)

        return self.__class__(self._http, data["data"])

    @require_authentication
    async def delete(self) -> None:
        """|coro|

        This method will delete the current cover from the MangaDex API.

        Raises
        ------
        BadRequest
            The request payload was malformed.
        Forbidden
            The request returned an error due to authentication.
        """  # noqa: DOC502 # raised in method call
        await self._http.delete_cover(self.id)
