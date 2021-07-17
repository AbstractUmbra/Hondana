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

from .types.artist import ArtistResponse


if TYPE_CHECKING:
    from .http import HTTPClient
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
    version: :class:`int`
        The version revision of this artist.
    """

    __slots__ = ("_http", "id", "name", "image_url", "biography", "_created_at", "_updated_at", "version")

    def __init__(self, http: HTTPClient, payload: ArtistResponse) -> None:
        attributes = payload["attributes"]
        self._http = http
        self.id: str = payload["id"]
        self.name: str = attributes["name"]
        self.image_url: Optional[str] = attributes["imageUrl"]
        self.biography: Optional[LocalisedString] = attributes["biography"]
        self.version: int = attributes["version"]
        self._created_at = attributes["createdAt"]
        self._updated_at = attributes["updatedAt"]

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
