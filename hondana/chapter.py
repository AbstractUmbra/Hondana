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
from types import TracebackType
from typing import TYPE_CHECKING, Any, AsyncGenerator, Optional, Type, TypeVar, Union

import aiofiles
import aiohttp

from .errors import NotFound, UploadInProgress
from .manga import Manga
from .query import MangaIncludes, ScanlatorGroupIncludes
from .scanlator_group import ScanlatorGroup
from .utils import (
    MISSING,
    CustomRoute,
    Route,
    as_chunks,
    require_authentication,
    to_iso_format,
)


if TYPE_CHECKING:
    from os import PathLike

    from aiohttp import ClientResponse

    from .http import HTTPClient
    from .types.chapter import ChapterResponse, GetAtHomeResponse
    from .types.common import LanguageCode
    from .types.relationship import RelationshipResponse
    from .types.upload import (
        BeginChapterUploadResponse,
        GetUploadSessionResponse,
        UploadedChapterResponse,
    )

ChapterUploadT = TypeVar("ChapterUploadT", bound="ChapterUpload")

__all__ = (
    "Chapter",
    "ChapterAtHome",
    "ChapterUpload",
)

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
        The volume identifier (e.g. '1') this chapter is associated with, if any.
    chapter: Optional[:class:`str`]
        The chapter identifier (e.g. '001') associated with this chapter, if any.
    pages: :class:`int`
        The number of pages this chapter has.
    translated_language: :class:`str`
        The language code that this chapter was translated to.
    uploader: Optional[:class:`str`]
        The UUID of the uploader attributed to this chapter, if any.
    external_url: Optional[:class:`str`]
        The chapter's external url, if any.
    version: :class:`int`
        The revision version of this chapter.


    .. warning::
        THe :attr:`manga` and :meth:`get_parent_manga` will both return a :class:`~hondana.Manga` with minimal data if this Chapter was requested as part of a feed.
        The reason is that the ``Chapter.relationships["manga"].relationships`` key is null the API response during feed requests to avoid potential recursive data.
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
        "pages",
        "translated_language",
        "uploader",
        "external_url",
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
        self._relationships: list[RelationshipResponse] = self._data.pop("relationships", [])
        self.id: str = self._data["id"]
        self.title: Optional[str] = self._attributes["title"]
        self.volume: Optional[str] = self._attributes["volume"]
        self.chapter: Optional[str] = self._attributes["chapter"]
        self.pages: int = self._attributes["pages"]
        self.translated_language: str = self._attributes["translatedLanguage"]
        self.uploader: Optional[str] = self._attributes.get("uploader")
        self.external_url: Optional[str] = self._attributes["externalUrl"]
        self.version: int = self._attributes["version"]
        self._created_at = self._attributes["createdAt"]
        self._updated_at = self._attributes["updatedAt"]
        self._published_at = self._attributes["publishAt"]
        self._at_home_url: Optional[str] = None
        self.__parent: Optional[Manga] = None
        self.__scanlator_group: Optional[ScanlatorGroup] = None

    def __repr__(self) -> str:
        return f"<Chapter id='{self.id}' title='{self.title}'>"

    def __str__(self) -> str:
        return self.title or "No title for this chapter..."

    def __eq__(self, other: Chapter) -> bool:
        return isinstance(other, Chapter) and self.id == other.id

    def __ne__(self, other: Chapter) -> bool:
        return not self.__eq__(other)

    def to_dict(self) -> dict[str, Any]:
        """
        Method to dump the chapter to a dictionary.


        .. warning::
            The dumped dictionary is not standard ``json`` spec compliant.

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

    async def get_at_home(self, ssl: bool = True) -> ChapterAtHome:
        """|coro|

        This method returns the @Home data for this chapter.

        Parameters
        ------------
        ssl :class:`bool`
            Wether to obtain an @Home URL for SSL only connections.
            Defaults to ``True``.

        Returns
        --------
        :class:`~hondana.ChapterAtHome`
            The returned details to reach a MD@H node for this chapter.
        """
        data = await self._http._get_at_home_url(self.id, ssl=ssl)
        return ChapterAtHome(self._http, data)

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
            The UTC datetime of when this chapter was created.
        """
        return datetime.datetime.fromisoformat(self._created_at)

    @property
    def updated_at(self) -> datetime.datetime:
        """When this chapter was last updated.

        Returns
        --------
        :class:`datetime.datetime`
            The UTC datetime of when this chapter was last updated.
        """
        return datetime.datetime.fromisoformat(self._updated_at)

    @property
    def published_at(self) -> datetime.datetime:
        """When this chapter was published.

        Returns
        --------
        :class:`datetime.datetime`
            The UTC datetime of when this chapter was published.
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
            The ScanlatorGroup that handled this chapter's scanlation and upload.
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
        :exc:`BadRequest`
            The request body was malformed.
        :exc:`Forbidden`
            You are not authorized to update this chapter.
        :exc:`NotFound`
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
        :exc:`BadRequest`
            The query was malformed.
        :exc:`Forbidden`
            You are not authorized to delete this chapter.
        :exc:`NotFound`
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
        self._at_home_url = at_home_data.base_url

        _pages = at_home_data.data_saver if data_saver else at_home_data.data
        for i, url in enumerate(_pages[start:], start=1):
            route = CustomRoute(
                "GET",
                self._at_home_url,
                f"/{'data-saver' if data_saver else 'data'}/{at_home_data.hash}/{url}",
            )
            LOGGER.debug("Attempting to download: %s", route.url)
            _start = time.monotonic()
            response: tuple[bytes, ClientResponse] = await self._http.request(route)
            data, page_resp = response
            _end = time.monotonic()
            _total = _end - _start
            LOGGER.debug("Downloaded: %s", route.url)

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
        path: Optional[Union[PathLike[str], str]] = None,
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
        path: Optional[Union[:class:`os.PathLike`, :class:`str`]]
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


class ChapterAtHome:
    """
    A small helper object for the MD@H responses from the API.

    Attributes
    -----------
    base_url: :class:`str`
        The base url for the MD@H connection
    hash: :class:`str`
        The hash of this chapter.
    data: List[:class:`str`]
        A list of page hashes for this chapter, for download/reading.
    data_saver: List[:class:`str`]
        A list of page hashes for this chapter, for download/reading.
        These pages are of "data saver" quality, compared to full quality :attr:`data`
    """

    __slots__ = (
        "_http",
        "_data",
        "base_url",
        "hash",
        "data",
        "data_saver",
    )

    def __init__(self, http: HTTPClient, payload: GetAtHomeResponse) -> None:
        self._http: HTTPClient = http
        self._data: GetAtHomeResponse = payload
        self.base_url: str = payload["baseUrl"]
        chapter = payload["chapter"]
        self.hash: str = chapter["hash"]
        self.data: list[str] = chapter["data"]
        self.data_saver: list[str] = chapter["dataSaver"]

    def __repr__(self) -> str:
        return f"<ChapterAtHome hash='{self.hash}'>"

    def __eq__(self, other: ChapterAtHome) -> bool:
        return isinstance(other, ChapterAtHome) and self.hash == other.hash


class ChapterUpload:
    """

    A context manager for handling the uploading of chapters to the MangaDex API.

    Parameters
    -----------
    manga: :class:`~hondana.Manga`
        The manga we are uploading a chapter for.
    volume: :class:`str`
        The volume name/number this chapter is/for.
    chapter: :class:`str`
        The chapter name/number.
    title: :class:`str`
        The chapter's title.
    translated_language: :class:`~hondana.types.LanguageCode`
        The language this chapter is translated in.
    external_url: Optional[:class:`str`]
        The external link to this chapter, if any.
    publish_at: Optional[:class:`datetime.datetime`]
        The future date at which to publish this chapter.
    scanlator_groups: List[:class:`str`]
        The list of scanlator group IDs to attribute to this chapter.
    existing_upload_session_id: :class:`str`
        If you already have an open upload session and wish to resume there, please pass the ID to this attribute.
    """

    __slots__ = (
        "_http",
        "manga",
        "volume",
        "chapter",
        "title",
        "translated_language",
        "external_url",
        "publish_at",
        "scanlator_groups",
        "uploaded",
        "upload_session_id",
        "__committed",
    )

    def __init__(
        self,
        http: HTTPClient,
        manga: Union[Manga, str],
        /,
        *,
        volume: str,
        chapter: str,
        title: str,
        translated_language: LanguageCode,
        scanlator_groups: list[str],
        external_url: Optional[str] = None,
        publish_at: Optional[datetime.datetime] = None,
        existing_upload_session_id: Optional[str] = None,
    ) -> None:
        self._http: HTTPClient = http
        self.manga: Union[Manga, str] = manga
        self.volume: str = volume
        self.chapter: str = chapter
        self.title: str = title
        self.translated_language: LanguageCode = translated_language
        self.external_url: Optional[str] = external_url
        self.publish_at: Optional[datetime.datetime] = publish_at
        self.scanlator_groups: list[str] = scanlator_groups
        self.uploaded: list[str] = []
        self.upload_session_id: Optional[str] = existing_upload_session_id
        self.__committed: bool = False

    def __repr__(self) -> str:
        return f"<ChapterUpload id='{self.upload_session_id}' current_uploads={len(self.uploaded)}>"

    async def _check_for_session(self) -> None:
        route = Route("GET", "/upload")
        try:
            data: GetUploadSessionResponse = await self._http.request(route)
        except NotFound:
            LOGGER.info("No upload session found, continuing.")
        else:
            raise UploadInProgress("You already have an existing session, please terminate it.", session_id=data["id"])

    @require_authentication
    async def open_session(self) -> BeginChapterUploadResponse:
        """|coro|

        Opens an upload session and retrieves the session ID.

        Returns
        --------
        :class:`~hondana.types.BeginChapterUploadResponse`
        """
        if isinstance(self.manga, Manga):
            manga_id = self.manga.id
        else:
            manga_id = self.manga

        return await self._http._open_upload_session(manga_id, scanlator_groups=self.scanlator_groups)

    @require_authentication
    async def upload_images(self, images: list[bytes]) -> list[UploadedChapterResponse]:
        """|coro|

        This method will take a list of bytes and upload them to the MangaDex API.

        Parameters
        -----------
        images: List[:class:`bytes`]
            A list of images as bytes.

        Returns
        --------
        List[:class:`~hondana.types.UploadedChapterResponse`]


        .. warning::
            The list of bytes must be ordered, this is the order they will be presented in the frontend.
        """
        route = Route("POST", "/upload/{session_id}", session_id=self.upload_session_id)
        ret = []

        chunks = as_chunks(images, 10)
        outer_idx = 1
        for batch in chunks:
            form = aiohttp.FormData()
            for idx, item in enumerate(batch, start=outer_idx):
                form.add_field(name=f"{idx}", value=item)
                outer_idx += 1

            response: UploadedChapterResponse = await self._http.request(route, data=form)
            for item in response["data"]:
                self.uploaded.append(item["id"])
            ret.append(response)

        return ret

    @require_authentication
    async def delete_images(self, image_ids: list[str], /) -> None:
        """|coro|

        This method will delete image(s) from the pending upload session.

        Parameters
        -----------
        image_ids: List[:class:`str`]
            A list of pending image IDs.


        .. note::
            If you need these IDs during an existing context manager, you can access ``uploaded`` and find it from there.
        """
        if len(image_ids) == 1:
            image_id = image_ids[0]
            route = Route("DELETE", "/upload/{session_id}/{image_id}", session_id=self.upload_session_id, image_id=image_id)
            await self._http.request(route)
            return

        route = Route("DELETE", "/upload/{session_id}/batch", session_id=self.upload_session_id)
        await self._http.request(route, json=image_ids)

        if self.uploaded:
            self.uploaded = [item for item in self.uploaded if item not in image_ids]

    @require_authentication
    async def abandon(self, session_id: Optional[str] = None, /) -> None:
        """|coro|

        This method will abandon your current (or passed) upload session.

        Parameters
        -----------
        session_id: Optional[:class:`str`]
            The session id which to abandon.
            Will default to the current instance's session.
        """

        session = session_id or self.upload_session_id
        if session is None:
            return

        if session == self.upload_session_id:
            self.__committed = True

        await self._http._abandon_upload_session(session)

    @require_authentication
    async def commit(self) -> Chapter:
        """|coro|

        This method will commit the pending upload session and return the valid chapter.

        Returns
        --------
        :class:`~hondana.Chapter`
        """
        payload: dict[str, Any] = {"chapterDraft": {}, "pageOrder": self.uploaded}

        payload["chapterDraft"]["volume"] = self.volume
        payload["chapterDraft"]["chapter"] = self.chapter
        payload["chapterDraft"]["title"] = self.title
        payload["chapterDraft"]["translatedLanguage"] = self.translated_language

        if self.external_url:
            payload["chapterDraft"]["externalUrl"] = self.external_url

        if self.publish_at:
            payload["chapterDraft"]["publishAt"] = to_iso_format(self.publish_at)

        route = Route("POST", "/upload/{session_id}/commit", session_id=self.upload_session_id)
        data: ChapterResponse = await self._http.request(route, json=payload)

        self.__committed = True
        return Chapter(self._http, data)

    @require_authentication
    async def __aenter__(self: ChapterUploadT) -> ChapterUploadT:
        if self.upload_session_id is None:
            await self._check_for_session()

        session_data = await self.open_session()
        self.upload_session_id = session_data["data"]["id"]

        return self

    async def __aexit__(
        self, exc_type: Optional[Type[BaseException]], exc_value: Optional[BaseException], traceback: Optional[TracebackType]
    ) -> None:
        if self.__committed is False:
            await self.commit()
