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
import logging
import pathlib
import time
from typing import TYPE_CHECKING, Any, AsyncGenerator, Optional, Union

import aiofiles

from .manga import Manga
from .query import MangaIncludes, ScanlatorGroupIncludes
from .scanlator_group import ScanlatorGroup
from .utils import MISSING, CustomRoute, require_authentication


if TYPE_CHECKING:
    from os import PathLike

    from aiohttp import ClientResponse

    from .http import HTTPClient
    from .types.chapter import ChapterResponse, GetAtHomeResponse
    from .types.relationship import RelationshipResponse


__all__ = ("Chapter",)

LOGGER: logging.Logger = logging.getLogger(__name__)


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
        "uploader",
        "version",
        "_created_at",
        "_updated_at",
        "_published_at",
        "_at_home_url",
        "__parent",
        "__scanlator_group",
    )

    def __init__(self, http: HTTPClient, payload: ChapterResponse) -> None:
        self._http = http
        self._data = payload
        self._attributes = self._data["attributes"]
        self._relationships: list[RelationshipResponse] = self._data["relationships"]
        self.id: str = self._data["id"]
        self.title: Optional[str] = self._attributes["title"]
        self.volume: Optional[str] = self._attributes["volume"]
        self.chapter: Optional[str] = self._attributes["chapter"]
        self.translated_language: str = self._attributes["translatedLanguage"]
        self.uploader: Optional[str] = self._attributes.get("uploader")
        self.version: int = self._attributes["version"]
        self._created_at = self._attributes["createdAt"]
        self._updated_at = self._attributes["updatedAt"]
        self._published_at = self._attributes["publishAt"]
        self._at_home_url: Optional[str] = None
        self.__parent: Optional[Manga] = None
        self.__scanlator_group: Optional[ScanlatorGroup] = None

    def __repr__(self) -> str:
        return f"<Chapter id={self.id} title='{self.title}'>"

    def __str__(self) -> str:
        return self.title or "No title for this chapter..."

    def to_dict(self) -> dict[str, Any]:
        """
        Method to dump the chapter to a dictionary.

        Returns
        --------
        Dict[:class:`str`, Any]
        """
        fmt = {}
        names = self.__slots__ if hasattr(self, "__slots__") else self.__dict__
        for name in dir(self):
            if name.startswith("_"):
                continue
            value = getattr(self.__class__, name, None)
            if isinstance(value, property) or name in names:
                fmt[name] = getattr(self, name)
        return fmt

    async def get_at_home(self, ssl: bool = True) -> GetAtHomeResponse:
        """|coro|

        This method returns the @Home data for this chapter.

        Parameters
        ------------
        ssl :class:`bool`
            Wether to obtain an @Home URL for SSL only connections.
            Defaults to ``True``.

        Returns
        --------
        :class:`~hondana.types.GetAtHomeResponse`
        """
        data = await self._http._get_at_home_url(self.id, ssl=ssl)
        return data

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
        Optional[:class:`~hondana.Manga`]
            The manga within the Chapter's payload, usually the parent manga.
        """
        if self.__parent is not None:
            return self.__parent

        if not self._relationships:
            return

        resolved = None
        for relationship in self._relationships:
            if relationship["type"] == "manga":
                resolved = relationship
                break

        if resolved is None or not resolved.get("attributes"):
            return

        return Manga(self._http, resolved)

    @manga.setter
    def manga(self, other: Manga) -> None:
        if isinstance(other, Manga):
            self.__parent = other

    @property
    def scanlator_group(self) -> Optional[ScanlatorGroup]:
        """The Scanlator Group that handled this chapter.

        Returns
        --------
        Optional[:class:`~hondana.ScanlatorGroup`]
            The ScanlatorGroup that handled this chapter.
        """
        if self.__scanlator_group is not None:
            return self.__scanlator_group

        if not self._relationships:
            return

        resolved = None
        for relationship in self._relationships:
            if relationship["type"] == "scanlation_group":
                resolved = relationship
                break

        if resolved is None or not resolved.get("attributes"):
            return

        return ScanlatorGroup(self._http, resolved)

    @scanlator_group.setter
    def scanlator_group(self, other: ScanlatorGroup) -> None:
        if isinstance(other, ScanlatorGroup):
            self.__scanlator_group = other

    async def get_parent_manga(self) -> Optional[Manga]:
        """|coro|

        This method will fetch the parent manga from a chapter's relationships.

        Returns
        --------
        Optional[:class:`~hondana.Manga`]
            The Manga that was fetched from the API.
        """
        manga_id = None
        for relationship in self._relationships:
            if relationship["type"] == "manga":
                manga_id = relationship["id"]
                break

        if manga_id is None:
            return

        manga = await self._http._view_manga(manga_id, includes=MangaIncludes())

        resolved = Manga(self._http, manga["data"])
        self.__parent = resolved
        return self.__parent

    async def get_scanlator_group(self) -> Optional[ScanlatorGroup]:
        """|coro|

        This method will fetch the scanlator group from a chapter's relationships.

        Returns
        --------
        Optional[:class:`~hondana.ScanlatorGroup`]
            The scanlator group that was fetched from the API.
        """
        if self.__scanlator_group is not None:
            return self.__scanlator_group

        if not self._relationships:
            return

        group_id = None
        for relationship in self._relationships:
            if relationship["type"] == "group":
                group_id = relationship["id"]
                break

        if group_id is None:
            return

        group = await self._http._view_scanlation_group(group_id, includes=ScanlatorGroupIncludes())

        resolved = ScanlatorGroup(self._http, group["data"])
        self.__scanlator_group = resolved
        return self.__scanlator_group

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
        :class:`~hondana.Chapter`
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
            The UUID passed for this chapter does not relate to a chapter in the API.
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

    async def _pages(
        self, *, start: int, data_saver: bool, ssl: bool, report: bool
    ) -> AsyncGenerator[tuple[bytes, str], None]:
        at_home_data = await self.get_at_home(ssl=ssl)
        self._at_home_url = at_home_data["baseUrl"]
        chapter_data = at_home_data["chapter"]

        _pages = chapter_data["dataSaver"] if data_saver else chapter_data["data"]
        for i, url in enumerate(_pages[start:], start=1):
            route = CustomRoute(
                "GET",
                self._at_home_url,
                f"/{'data-saver' if data_saver else 'data'}/{chapter_data['hash']}/{url}",
            )
            LOGGER.debug("Attempting to download: %s" % route.url)
            _start = time.monotonic()
            response: tuple[bytes, ClientResponse] = await self._http.request(route)
            data, page_resp = response
            _end = time.monotonic()
            _total = _end - _start
            LOGGER.debug("Downloaded: %s" % route.url)

            if report is True:
                await self._http._at_home_report(
                    route.url,
                    page_resp.status == 200,
                    "X-Cache" in page_resp.headers,
                    (page_resp.content_length or 0),
                    int(_total * 1000),
                )

            if page_resp.status != 200:
                self._at_home_url = None
                break
            else:
                yield data, url.rsplit(".")[-1]

        else:
            return

        async for page in self._pages(start=i, data_saver=data_saver, ssl=ssl, report=report):
            yield page

    async def download(
        self,
        path: Union[PathLike[str], str] = None,
        *,
        start_page: int = 0,
        data_saver: bool = False,
        ssl: bool = False,
        report: bool = True,
    ) -> None:
        """|coro|

        This method will attempt to download a chapter for you using the MangaDex process.

        Parameters
        -----------
        path: Union[:class:`os.PathLike`, :class:`str`]
            The path at which to use (or create) a directory to save the pages of the chapter.
            Defaults to ``"chapter number - chapter title"``
        start_page: :class:`int`
            The page at which to start downloading, leave at 0 (default) to download all.
        data_saver: :class:`bool`
            Whether to use the smaller (and poorer quality) images, if you are on a data budget. Defaults to ``False``.
        ssl: :class:`bool`
            Whether to request an SSL @Home link from MangaDex, this guarantees https as compared to potentially getting a HTTP url.
            Defaults to ``False``.
        report: :class:`bool`
            Whether to report success or failures to MangaDex per page download.
            The API guidelines ask us to do this, so it defaults to ``True``.
        """
        path = path or f"{self.chapter} - {self.title}"
        path_ = pathlib.Path(path)
        if not path_.exists():
            path_.mkdir(parents=True, exist_ok=True)

        idx = 1
        async for page_data, page_ext in self._pages(start=start_page, data_saver=data_saver, ssl=ssl, report=report):
            download_path = f"{path_}/{idx}.{page_ext}"
            async with aiofiles.open(download_path, "wb") as f:
                await f.write(page_data)
                LOGGER.info("Downloaded to: %s", download_path)
            idx += 1
