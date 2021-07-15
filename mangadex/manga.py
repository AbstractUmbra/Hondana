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

from .artist import Artist
from .cover import Cover
from .tags import Tag


if TYPE_CHECKING:
    from .author import Author
    from .http import Client
    from .types.manga import ViewMangaResponse


__all__ = ("Manga",)


class Manga:
    """A class representing a Manga returned from the MangaDex API.

    Attributes
    -----------
    id: :class:`str`
        The UUID associated to this manga.
    alternative_titles: Dict[:class:`str`, :class:`str`]
        The alternative title mapping for the Manga.
        i.e. ``{"en": "Some Other Title"}``
    locked: :class:`bool`
        If the Manga is considered 'locked' or not in the API.
    links: Dict[:class:`str`, Any]
        The mapping of links the API has attributed to the Manga.
        (see: https://api.mangadex.org/docs.html#section/Static-data/Manga-links-data)
    original_language: :class:`str`
        The language code for the original language of the Manga.
    last_volume: Optional[:class:`str`]
        The last volume attributed to the manga, if any.
    last_chapter: Optional[:class:`str`]
        The last chapter attributed to the manga, if any.
    publication_demographic: Optional[Dict[:class:`str`, Any]]
        The attributed publication demographic(s) for the manga, if any.
    year: Optional[:class:`int`]
        The year the manga was release, if the key exists.
    content_rating: Optional[Dict[:class:`str`, Any]]
        The content rating attributed to the manga, if any.
    version: :class:`int`
        The version revision of this manga.
    """

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
        "_tags",
        "version",
        "_created_at",
        "_updated_at",
        "id",
        "_relationships",
    )

    def __init__(self, http: Client, payload: ViewMangaResponse) -> None:
        self._http = http
        data = payload["data"]
        attributes = data["attributes"]
        self.id = data["id"]
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
        self._tags = attributes["tags"]
        self.version = attributes["version"]
        self._created_at = attributes["createdAt"]
        self._updated_at = attributes["updatedAt"]
        self._relationships = payload["relationships"]

    def __repr__(self) -> str:
        return f"<Manga id={self.id} title='{self.title}'>"

    def __str__(self) -> str:
        return self.title

    @property
    def title(self) -> str:
        """The manga's title."""
        return self._title.get("en", next(iter(self._title)))

    @property
    def tags(self) -> list[Tag]:
        """The tags associated with this manga."""
        return [Tag(tag) for tag in self._tags]

    @property
    def created_at(self) -> datetime.datetime:
        """The date this manga was created."""
        return datetime.datetime.fromisoformat(self._created_at)

    @property
    def updated_at(self) -> datetime.datetime:
        """The date this manga was last updated."""
        return datetime.datetime.fromisoformat(self._updated_at)

    async def get_author(self) -> Optional[Author]:
        """|coro|

        This method will return the author of the manga.

        Returns
        --------
        Optional[:class:`Author`]
            The author of the manga.


        .. note::
            If the parent manga was requested with the "author" `includes[]` query parameter,
            then this method will not make an extra API call to retrieve the Author data.
        """
        author = None
        for item in self._relationships:
            if item["type"] == "author":
                author = item
                break

        if author is None:
            return None

        if "attributes" in author:
            return Author(self._http, author, author["attributes"])  # type: ignore #TODO: typing.Protocol or abcs here.

        return await self._http.get_author(author["id"])

    async def cover_url(self) -> Optional[Cover]:
        """|coro|

        This method will return the cover URL of the parent Manga.

        Returns
        --------
        Optional[:class:`Cover`]
            The Cover associated with this Manga.


        .. note::
            If the parent manga was requested with the "cover_art" `includes[]` query parameter,
            then this method will not make an extra API call to retrieve the Cover data.
        """
        cover_key = None
        for item in self._relationships:
            if item["type"] == "cover_art":
                cover_key = item
                break

        if cover_key is None:
            return None

        if "attributes" not in cover_key:
            return await self._http.get_cover(cover_key["id"])
        return Cover(self._http, cover_key["attributes"])  # type: ignore

    def get_artist(self) -> Optional[Artist]:
        """This method will return the artist of the parent Manga.

        Returns
        --------
        Optional[:class:`Artist`]
            The artist associated with this Manga.


        .. note::
            If the parent manga was **not** requested with the "artist" `includes[]` query parameter
            then this method will return ``None``.
        """

        artist = None
        for item in self._relationships:
            if item["type"] == "artist":
                artist = item
                break

        if artist is None:
            return None

        if "attributes" in artist:
            return Artist(self._http, artist)  # type: ignore #TODO: Investigate typing.Protocol or abcs here.
