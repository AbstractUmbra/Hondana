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


if TYPE_CHECKING:
    from .http import HTTPClient
    from .types.artist import ArtistResponse
    from .types.common import LocalisedString


__all__ = ("Artist",)


class Artist:
    """A class representing an Artist returns from the MangaDex API.

    Attributes
    -----------
    id: :class:`str`
        The UUID associated with this artist.
    name: :class:`str`
        The artist's name.
    image_url: Optional[:class:`str`]
        The artist's image url, if any.
    biography: Optional[:class:`str`]
        The artist's biography, if any.
    twitter: Optional[:class:`str`]
        The artist's Twitter url, if any.
    pixiv: Optional[:class:`str`]
        The artist's Pixiv url, if any.
    melon_book: Optional[:class:`str`]
        The artist's Melon Book url, if any.
    booth: Optional[:class:`str`]
        The artist's Booth url, if any.
    nico_video: Optional[:class:`str`]
        The artist's Nico Video url, if any.
    skeb: Optional[:class:`str`]
        The artist's Skeb url, if any.
    fantia: Optional[:class:`str`]
        The artist's Fantia url, if any.
    tumblr: Optional[:class:`str`]
        The artist's Tumblr url, if any.
    youtube: Optional[:class:`str`]
        The artist's Youtube url, if any.
    website: Optional[:class:`str`]
        The artist's website url, if any.
    version: :class:`int`
        The version revision of this artist.
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

    def __init__(self, http: HTTPClient, payload: ArtistResponse) -> None:
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
        return f"<Artist id={self.id} name='{self.name}'>"

    def __str__(self) -> str:
        return self.name

    @property
    def created_at(self) -> datetime.datetime:
        """When this artist was created."""
        return datetime.datetime.fromisoformat(self._created_at)

    @property
    def updated_at(self) -> datetime.datetime:
        """When this artist was last updated."""
        return datetime.datetime.fromisoformat(self._updated_at)
