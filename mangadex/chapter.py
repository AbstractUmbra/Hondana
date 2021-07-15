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
    from .types.chapter import GetChapterResponse


__all__ = ("Chapter",)


class Chapter:
    __slots__ = (
        "_http",
        "id",
        "title",
        "volume",
        "chapter",
        "translated_language",
        "hash",
        "data",
        "data_saver",
        "uploader",
        "version",
        "_created_at",
        "_updated_at",
        "_published_at",
    )

    def __init__(self, http: Client, payload: GetChapterResponse) -> None:
        self._http = http
        data = payload["data"]
        attributes = data["attributes"]
        self.id = data["id"]
        self.title = attributes["title"]
        self.volume = attributes["volume"]
        self.chapter = attributes["chapter"]
        self.translated_language = attributes["translatedLanguage"]
        self.hash = attributes["hash"]
        self.data = attributes["data"]
        self.data_saver = attributes["dataSaver"]
        self.uploader = attributes.get("uploader", None)
        self.version = attributes["version"]
        self._created_at = attributes["createdAt"]
        self._updated_at = attributes["updatedAt"]
        self._published_at = attributes["publishAt"]

    def __repr__(self) -> str:
        return f"<Chapter id={self.id} title='{self.title}'>"

    def __str__(self) -> str:
        return self.title or "No title for this chapter..."

    @property
    def created_at(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._created_at)

    @property
    def updated_at(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._updated_at)

    @property
    def published_at(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._published_at)
