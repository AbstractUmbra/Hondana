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

from .manga import Manga
from .utils import MISSING, require_authentication


if TYPE_CHECKING:
    from .http import HTTPClient
    from .types.chapter import ChapterResponse


__all__ = ("Chapter",)


class Chapter:
    """A class representing a Chapter returned from the MangaDex API.

    Attributes
    -----------
    id: :class:`str`
        The UUID associated with this chapter.
    title: Optional[:class:`str`]
        The manga's title.
        Interestingly enough, this can sometimes be ``None``.
    volume: Optional[:class:`str`]
        The volume UUID this chapter is associated with this chapter, if any.
    chapter: Optional[:class:`str`]
        The chapter identifier (e.g. '001') associated with this chapter, if any.
    translated_language: :class:`str`
        The language code that this chapter was translated to.
    hash: :class:`str`
        The hash associated with this chapter.
    data: List[:class:`str`]
        A list of chapter page URLs (original quality).
    data_saver: List[:class:`str`]
        A list of chapter page URLs (data saver quality).
    uploader: Optional[:class:`str`]
        The UUID of the uploader attributed to this chapter, if any.
    version: :class:`int`
        The revision version of this chapter.
    """

    __slots__ = (
        "_http",
        "_data",
        "_attributes",
        "_relationships",
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

    def __init__(self, http: HTTPClient, payload: ChapterResponse) -> None:
        self._http = http
        self._data = payload
        self._attributes = self._data["attributes"]
        self._relationships = self._data["relationships"]
        self.id: str = self._data["id"]
        self.title: Optional[str] = self._attributes["title"]
        self.volume: Optional[str] = self._attributes["volume"]
        self.chapter: Optional[str] = self._attributes["chapter"]
        self.translated_language: str = self._attributes["translatedLanguage"]
        self.hash: str = self._attributes["hash"]
        self.data: list[str] = self._attributes["data"]
        self.data_saver: list[str] = self._attributes["dataSaver"]
        self.uploader: Optional[str] = self._attributes.get("uploader", None)
        self.version: int = self._attributes["version"]
        self._created_at = self._attributes["createdAt"]
        self._updated_at = self._attributes["updatedAt"]
        self._published_at = self._attributes["publishAt"]

    def __repr__(self) -> str:
        return f"<Chapter id={self.id} title='{self.title}'>"

    def __str__(self) -> str:
        return self.title or "No title for this chapter..."

    @property
    def url(self) -> str:
        """The URL to this chapter.

        Returns
        --------
        :class:`str`
            The URL of the chapter.
        """
        return f"https://mangadex.org/chapter/{self.id}"

    @property
    def created_at(self) -> datetime.datetime:
        """When this chapter was created.

        Returns
        --------
        :class:`datetime.datetime`
            The UTC timestamp of when this chapter was created.
        """
        return datetime.datetime.fromisoformat(self._created_at)

    @property
    def updated_at(self) -> datetime.datetime:
        """When this chapter was last updated.

        Returns
        --------
        :class:`datetime.datetime`
            The UTC timestamp of when this chapter was last updated.
        """
        return datetime.datetime.fromisoformat(self._updated_at)

    @property
    def published_at(self) -> datetime.datetime:
        """When this chapter was published.

        Returns
        --------
        :class:`datetime.datetime`
            The UTC timestamp of when this chapter was published.
        """
        return datetime.datetime.fromisoformat(self._published_at)

    @property
    def manga(self) -> Optional[Manga]:
        """The parent Manga of the chapter.

        Returns
        --------
        Optional[:class:`Manga`]
            The manga within the Chapter's payload, usually the parent manga.
        """
        if not self._relationships:
            return

        resolved = None
        for relationship in self._relationships:
            if relationship["type"] == "manga" and relationship.get("attributes", False):
                resolved = relationship
                break

        if resolved is None:
            return

        return Manga(self._http, resolved)

    async def get_parent_manga(self) -> Optional[Manga]:
        """|coro|

        This method will fetch the parent manga from a chapter's relationships.

        Returns
        --------
        Optional[:class:`Manga`]
            The Manga that was fetched from the API.
        """
        manga_id = None
        for item in self._relationships:
            if item["type"] == "manga":
                manga_id = item["id"]
                break

        if manga_id is None:
            return

        manga = await self._http._view_manga(manga_id, includes=["author", "artist", "cover_art"])

        return Manga(self._http, manga["data"])

    @require_authentication
    async def update(
        self,
        *,
        title: Optional[str] = None,
        volume: str = MISSING,
        chapter: str = MISSING,
        translated_language: Optional[str] = None,
        groups: Optional[list[str]] = None,
        version: int,
    ) -> Chapter:
        """|coro|

        This method will update the current chapter in the MangaDex API.

        Parameters
        -----------
        title: Optional[:class:`str`]
            The title to rename the chapter to, if given.
        volume: Optional[:class:`str`]
            The volume identity that this chapter belongs to, if any.
        chapter: Optional[:class:`str`]
            The chapter identity marking this chapter, if any.
        translated_language: Optional[:class:`str`]
            The language code this chapter is translated to.
        groups: Optional[:class:`str`]
            The UUIDs representing credited scanlation groups for this chapter.
        version: :class:`int`
            The version revision of this chapter.


        .. note::
            The ``volume`` and ``chapter`` keys are nullable,
            pass ``None`` to them to send ``null`` to the API

        Raises
        -------
        BadRequest
            The request body was malformed.
        Forbidden
            You are not authorized to update this chapter.
        NotFound
            One or more UUIDs given were not found.

        Returns
        --------
        :class:`Chapter`
            The chapter after being updated.
        """
        data = await self._http._update_chapter(
            self.id,
            title=title,
            volume=volume,
            chapter=chapter,
            translated_language=translated_language,
            groups=groups,
            version=version,
        )

        return self.__class__(self._http, data["data"])

    @require_authentication
    async def delete(self) -> None:
        """|coro|

        This method will delete the current chapter from the MangaDex API.

        Raises
        -------
        BadRequest
            The query was malformed.
        Forbidden
            You are not authorized to delete this chapter.
        NotFound
            The UUID passed for this chapter does not related to a chapter in the API.
        """
        await self._http._delete_chapter(self.id)

    @require_authentication
    async def mark_as_read(self) -> None:
        """|coro|

        This method will mark the current chapter as read for the current authenticated user in the MangaDex API.
        """
        await self._http._mark_chapter_as_read(self.id)

    @require_authentication
    async def mark_chapter_as_unread(self) -> None:
        """|coro|

        This method will mark the current chapter as unread for the current authenticated user in the MangaDex API.
        """
        await self._http._mark_chapter_as_unread(self.id)
