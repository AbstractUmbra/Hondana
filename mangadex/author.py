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
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .http import Client
    from .types.author import AuthorResponse

__all__ = ("Author",)


class Author:
    """A class representing an Author returned from the MangaDex API.

    Attributes
    -----------
    id: :class:`str`
        The UUID associated to this author.
    name: :class:`str`
        The artist's name.
    image_url: Optional[:class:`str`]
        The author's image url, if any.
    biography: Optional[:class:`str`]
        The author's biography, if any.
    version: :class:`int`
        The version revision of this author.
    """

    __slots__ = ("_http", "_data", "id", "name", "image_url", "biography", "version", "_created_at", "_updated_at")

    def __init__(self, http: Client, data: AuthorResponse) -> None:
        self._http = http
        self._data = data
        self.id = data["id"]
        attributes = data["attributes"]
        self.name = attributes["name"]
        self.image_url = attributes["imageUrl"]
        self.biography = attributes["biography"]
        self.version = attributes["version"]
        self._created_at = attributes["createdAt"]
        self._updated_at = attributes["updatedAt"]

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
