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

from .types.artist import ArtistResponse


if TYPE_CHECKING:
    from .http import HTTPClient


class Artist:
    __slots__ = ("_http", "id", "name", "image_url", "biography", "_created_at", "_updated_at", "version")

    def __init__(self, http: HTTPClient, payload: ArtistResponse) -> None:
        self._http = http
        self.id = payload["id"]
        attributes = payload["attributes"]
        self.name = attributes["name"]
        self.image_url = attributes["imageUrl"]
        self.biography = attributes["biography"]
        self._created_at = attributes["createdAt"]
        self._updated_at = attributes["updatedAt"]
        self.version = attributes["version"]

    def __repr__(self) -> str:
        return f"<Artist id={self.id} name='{self.name}'>"

    def __str__(self) -> str:
        return self.name

    @property
    def created_at(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._created_at)

    @property
    def updated_at(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._updated_at)
