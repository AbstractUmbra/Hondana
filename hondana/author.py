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

from .utils import require_authentication


if TYPE_CHECKING:
    from .http import HTTPClient
    from .types.author import AuthorResponse
    from .types.common import LocalisedString

__all__ = ("Author",)


class Author:
    """A class representing an Author returned from the MangaDex API.

    Attributes
    -----------
    id: :class:`str`
        The UUID associated with this author.
    name: :class:`str`
        The author's name.
    image_url: Optional[:class:`str`]
        The author's image url, if any.
    biography: Optional[:class:`str`]
        The author's biography, if any.
    twitter: Optional[:class:`str`]
        The author's Twitter url, if any.
    pixiv: Optional[:class:`str`]
        The author's Pixiv url, if any.
    melon_book: Optional[:class:`str`]
        The author's Melon Book url, if any.
    booth: Optional[:class:`str`]
        The author's Booth url, if any.
    nico_video: Optional[:class:`str`]
        The author's Nico Video url, if any.
    skeb: Optional[:class:`str`]
        The author's Skeb url, if any.
    fantia: Optional[:class:`str`]
        The author's Fantia url, if any.
    tumblr: Optional[:class:`str`]
        The author's Tumblr url, if any.
    youtube: Optional[:class:`str`]
        The author's Youtube url, if any.
    website: Optional[:class:`str`]
        The author's website url, if any.
    version: :class:`int`
        The version revision of this author.
    """

    __slots__ = (
        "_http",
        "_data",
        "_attributes",
        "_relationships",
        "id",
        "name",
        "image_url",
        "biography",
        "twitter",
        "pixiv",
        "melon_book",
        "booth",
        "nico_video",
        "skeb",
        "fantia",
        "tumblr",
        "youtube",
        "website",
        "_created_at",
        "_updated_at",
        "version",
    )

    def __init__(self, http: HTTPClient, payload: AuthorResponse) -> None:
        self._http = http
        self._data = payload
        self._attributes = self._data["attributes"]
        self._relationships = self._data["relationships"]
        self.id: str = self._data["id"]
        self.name: str = self._attributes["name"]
        self.image_url: Optional[str] = self._attributes["imageUrl"]
        self.biography: Optional[LocalisedString] = self._attributes["biography"]
        self.twitter: Optional[str] = self._attributes["twitter"]
        self.pixiv: Optional[str] = self._attributes["pixiv"]
        self.melon_book: Optional[str] = self._attributes["melonBook"]
        self.booth: Optional[str] = self._attributes["booth"]
        self.nico_video: Optional[str] = self._attributes["nicoVideo"]
        self.skeb: Optional[str] = self._attributes["skeb"]
        self.fantia: Optional[str] = self._attributes["fantia"]
        self.tumblr: Optional[str] = self._attributes["tumblr"]
        self.youtube: Optional[str] = self._attributes["youtube"]
        self.website: Optional[str] = self._attributes["website"]
        self.version: int = self._attributes["version"]
        self._created_at = self._attributes["createdAt"]
        self._updated_at = self._attributes["updatedAt"]

    def __repr__(self) -> str:
        return f"<Author id={self.id} name='{self.name}'>"

    def __str__(self) -> str:
        return self.name

    @property
    def created_at(self) -> datetime.datetime:
        """When this author was created."""
        return datetime.datetime.fromisoformat(self._created_at)

    @property
    def updated_at(self) -> datetime.datetime:
        """When this author was last updated."""
        return datetime.datetime.fromisoformat(self._updated_at)

    @require_authentication
    async def update(self, *, name: Optional[str] = None, version: int) -> Author:
        """|coro|

        This method will update the current author on the MangaDex API.

        Parameters
        -----------
        name: Optional[:class:`str`]
            The new name to update the author with.
        version: :class:`int`
            The version revision of this author.

        Raises
        -------
        :exc:`BadRequest`
            The request body was malformed.
        :exc:`Forbidden`
            You are not authorized to update this author.
        :exc:`NotFound`
            The author UUID given was not found.

        Returns
        --------
        :class:`Author`
            The updated author from the API.
        """
        data = await self._http._update_author(self.id, name=name, version=version)
        return Author(self._http, data["data"])

    @require_authentication
    async def delete(self, author_id: str, /) -> None:
        """|coro|

        This method will delete the current author from the MangaDex API.

        Raises
        -------
        :exc:`Forbidden`
            You are not authorized to delete this author.
        :exc:`NotFound`
            The UUID given for the author was not found.
        """
        await self._http._delete_author(author_id)
