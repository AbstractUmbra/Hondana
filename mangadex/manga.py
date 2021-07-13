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
from typing import TYPE_CHECKING, Literal, Optional

from .artist import Artist


if TYPE_CHECKING:
    from .author import Author
    from .http import HTTPClient
    from .types.manga import ViewMangaResponse


__all__ = ("Manga",)


class Manga:
    __slots__ = (
        "_http",
        "_data",
        "_title",
        "alternate_titles",
        "locked",
        "links",
        "original_language",
        "last_volume",
        "last_chapter",
        "publication_demographic",
        "year",
        "content_rating",
        "tags",
        "version",
        "_created_at",
        "_updated_at",
        "id",
        "relationships",
    )

    def __init__(self, http: HTTPClient, payload: ViewMangaResponse) -> None:
        self._http = http
        data = payload["data"]
        attributes = data["attributes"]
        self._data = data
        self._title = attributes["title"]
        self.alternate_titles = attributes["altTitles"]
        self.locked = attributes.get("isLocked", False)
        self.links = attributes["links"]
        self.original_language = attributes["originalLanguage"]
        self.last_volume = attributes["lastVolume"]
        self.last_chapter = attributes["lastChapter"]
        self.publication_demographic = attributes["publicationDemographic"]
        self.year = attributes["year"]
        self.content_rating = attributes["contentRating"]
        self.tags = attributes["tags"]
        self.version = attributes["version"]
        self._created_at = attributes["createdAt"]
        self._updated_at = attributes["updatedAt"]
        self.id = data["id"]
        self.relationships = payload["relationships"]

    def __repr__(self) -> str:
        return f"<Manga id={self.id} title='{self.title}'>"

    def __str__(self) -> str:
        return self.title

    @property
    def title(self) -> str:
        return self._title["en"]

    @property
    def created_at(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._created_at)

    @property
    def updated_at(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._updated_at)

    async def get_author(self) -> Optional[Author]:
        """|coro|

        This method will return the author of the manga.

        .. note::
            If the parent manga was requested with the "author" `includes[]` query parameter,
            then this method will not make an extra API call to retrieve the Author data.
        """
        author = None
        for item in self.relationships:
            if item["type"] == "author":
                author = item
                break

        if author is None:
            return None

        if "attributes" in author:
            return Author(self._http, author, author["attributes"])  # type: ignore #TODO: Investigate typing.Protocol or abcs here.

        return await self._http.get_author(author["id"])

    async def cover_url(self, type: Optional[Literal["512", "256"]] = None) -> Optional[str]:
        """|coro|

        This method will return the cover URL of the parent Manga.

        Parameters
        -----------
        type: Optional[Literal["512", "256"]]
            The size of the image to return. If no type is passed, it will return the original quality url.

        .. note::
            If the parent manga was requested with the "cover_art" `includes[]` query parameter,
            then this method will not make an extra API call to retrieve the Cover data.
        """
        cover_key = None
        for item in self.relationships:
            if item["type"] == "cover_art":
                cover_key = item
                break

        if cover_key is None:
            return None

        if "attributes" not in cover_key:
            cover_id = await self._http.get_cover(cover_key["id"])
        else:
            cover_id = cover_key["attributes"].get("fileName", None)
            if cover_id is None:
                return None

        if type == "512":
            fmt = ".512.jpg"
        elif type == "256":
            fmt = ".256.jpg"
        else:
            fmt = ""

        return f"https://uploads.mangadex.org/covers/{self.id}/{cover_id}{fmt}"

    def get_artist(self) -> Optional[Artist]:
        """This method will return the artist of the parent Manga.

        .. note::
            If the parent manga was **not** requested with the "artist" `includes[]` query parameter then this method will return ``None``.
        """

        artist = None
        for item in self.relationships:
            if item["type"] == "artist":
                artist = item
                break

        if artist is None:
            return None

        if "attributes" in artist:
            return Artist(self._http, artist)  # type: ignore #TODO: Investigate typing.Protocol or abcs here.
