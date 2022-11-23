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

import asyncio
import datetime
import logging
import pathlib
import time
from collections.abc import Callable
from types import TracebackType
from typing import TYPE_CHECKING, Any, AsyncGenerator, Optional, Type, TypeVar, Union

import aiohttp

from .errors import NotFound, UploadInProgress
from .manga import Manga
from .query import ChapterIncludes, MangaIncludes, ScanlatorGroupIncludes
from .scanlator_group import ScanlatorGroup
from .user import User
from .utils import (
    MISSING,
    CustomRoute,
    Route,
    as_chunks,
    cached_slot_property,
    clean_isoformat,
    relationship_finder,
    require_authentication,
    upload_file_sort,
)


if TYPE_CHECKING:
    from os import PathLike

    from aiohttp import ClientResponse

    from .http import HTTPClient
    from .types_.chapter import ChapterResponse, GetAtHomeChapterResponse, GetAtHomeResponse, GetSingleChapterResponse
    from .types_.common import LanguageCode
    from .types_.errors import ErrorType
    from .types_.manga import MangaResponse
    from .types_.relationship import RelationshipResponse
    from .types_.scanlator_group import ScanlationGroupResponse
    from .types_.upload import BeginChapterUploadResponse, GetUploadSessionResponse, UploadedChapterResponse
    from .types_.user import UserResponse

ChapterUploadT = TypeVar("ChapterUploadT", bound="ChapterUpload")

__all__ = (
    "Chapter",
    "ChapterAtHome",
    "UploadData",
    "ChapterUpload",
    "PreviouslyReadChapter",
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
        "id",
        "title",
        "volume",
        "chapter",
        "pages",
        "translated_language",
        "external_url",
        "version",
        "_created_at",
        "_updated_at",
        "_published_at",
        "_readable_at",
        "_manga_relationship",
        "_scanlator_group_relationships",
        "_uploader_relationship",
        "_at_home_url",
        "__uploader",
        "__parent",
        "__scanlator_groups",
        "_cs_relationships",
    )

    def __init__(self, http: HTTPClient, payload: ChapterResponse) -> None:
        self._http = http
        self._data = payload
        self._attributes = self._data["attributes"]
        relationships: list[RelationshipResponse] = self._data.pop("relationships", [])
        self.id: str = self._data["id"]
        self.title: Optional[str] = self._attributes["title"]
        self.volume: Optional[str] = self._attributes["volume"]
        self.chapter: Optional[str] = self._attributes["chapter"]
        self.pages: int = self._attributes["pages"]
        self.translated_language: str = self._attributes["translatedLanguage"]
        self.external_url: Optional[str] = self._attributes["externalUrl"]
        self.version: int = self._attributes["version"]
        self._created_at = self._attributes["createdAt"]
        self._updated_at = self._attributes["updatedAt"]
        self._published_at = self._attributes["publishAt"]
        self._readable_at = self._attributes["readableAt"]
        self._manga_relationship: Optional[MangaResponse] = relationship_finder(relationships, "manga", limit=1)
        self._scanlator_group_relationships: list[ScanlationGroupResponse] = relationship_finder(
            relationships, "scanlation_group", limit=None
        )
        self._uploader_relationship: UserResponse = relationship_finder(relationships, "user", limit=1)
        self._at_home_url: Optional[str] = None
        self.__uploader: Optional[User] = None
        self.__parent: Optional[Manga] = None
        self.__scanlator_groups: Optional[list[ScanlatorGroup]] = None

    def __repr__(self) -> str:
        return f"<Chapter id={self.id!r} title={self.title!r}>"

    def __str__(self) -> str:
        return self.title or f"No title for this chapter, with ID: {self.id!r}"

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
            Whether to obtain an @Home URL for SSL only connections.
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
    def readable_at(self) -> datetime.datetime:
        """When this chapter is readable.

        Returns
        --------
        :class:`datetime.datetime`
            The UTC datetime of when this chapter becomes readable.
        """
        return datetime.datetime.fromisoformat(self._readable_at)

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

        if not self._manga_relationship:
            return

        if "attributes" in self._manga_relationship:
            manga = Manga(self._http, self._manga_relationship)
            self.__parent = manga
            return self.__parent

    @manga.setter
    def manga(self, other: Manga) -> None:
        self.__parent = other

    @property
    def manga_id(self) -> Optional[str]:
        """The parent manga id of this chapter.


        .. note::
            This can be ``None`` if the chapter has no relationships key.
            Or in the almost impossible situation that it has no ``"manga"`` relationship.

        Returns
        --------
        :class:`str`
            The manga id.
        """

        return self._manga_relationship["id"] if self._manga_relationship else None

    @property
    def scanlator_groups(self) -> Optional[list[ScanlatorGroup]]:
        """The Scanlator Group that handled this chapter.

        Returns
        --------
        Optional[List[:class:`~hondana.ScanlatorGroup`]]
            The groups that handled this chapter's scanlation and upload.
        """
        if self.__scanlator_groups is not None:
            return self.__scanlator_groups

        if not self._scanlator_group_relationships:
            return

        fmt = [
            ScanlatorGroup(self._http, payload) for payload in self._scanlator_group_relationships if "attributes" in payload
        ]

        if not fmt:
            return

        self.__scanlator_groups = fmt
        return self.__scanlator_groups

    @scanlator_groups.setter
    def scanlator_groups(self, other: list[ScanlatorGroup]) -> None:
        self.__scanlator_groups = other

    @property
    def uploader(self) -> Optional[User]:
        """The uploader who uploaded this chapter.

        Returns
        --------
        Optional[:class:`~hondana.User`]
            The user that handled this chapter's upload.
        """
        if self.__uploader is not None:
            return self.__uploader

        if not self._uploader_relationship:
            return

        if "attributes" in self._uploader_relationship:
            self.__uploader = User(self._http, self._uploader_relationship)
            return self.__uploader

    async def get_parent_manga(self) -> Optional[Manga]:
        """|coro|

        This method will fetch the parent manga from a chapter's relationships and cache the response.

        Returns
        --------
        Optional[:class:`~hondana.Manga`]
            The Manga that was fetched from the API.
        """
        if self.manga is not None:
            return self.manga

        if not self._manga_relationship:
            return

        if self.manga_id is None:
            return

        manga = await self._http._get_manga(self.manga_id, includes=MangaIncludes())

        resolved = Manga(self._http, manga["data"])
        self.__parent = resolved
        return self.__parent

    async def get_scanlator_groups(self) -> Optional[list[ScanlatorGroup]]:
        """|coro|

        This method will fetch the scanlator group from a chapter's relationships.

        .. warning::
            It is recommended to request this Chapter with the ``scanlator_group`` reference expansion,
            as this method will make an API call to request this data.

        Returns
        --------
        Optional[List[:class:`~hondana.ScanlatorGroup`]]
            The scanlator group that was fetched from the API.
        """
        if self.scanlator_groups is not None:
            return self.scanlator_groups

        if not self._scanlator_group_relationships:
            return

        ids = [item["id"] for item in self._scanlator_group_relationships]

        groups = await self._http._scanlation_group_list(
            limit=100,
            offset=0,
            ids=ids,
            name=None,
            focused_language=None,
            includes=ScanlatorGroupIncludes(),
            order=None,
        )

        resolved_groups = [ScanlatorGroup(self._http, item) for item in groups["data"]]
        self.__scanlator_groups = resolved_groups
        return self.__scanlator_groups

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
        groups: Optional[List[:class:`str`]]
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
    async def mark_as_read(self, update_history: bool = True) -> None:
        """|coro|

        This method will mark the current chapter as read for the current authenticated user in the MangaDex API.

        Parameters
        -----------
        update_history: :class:`bool`
            Whether to include this chapter in the authenticated user's read history.
        """
        if self.manga_id:
            await self._http._manga_read_markers_batch(
                self.manga_id, update_history=update_history, read_chapters=[self.id], unread_chapters=None
            )

    @require_authentication
    async def mark_as_unread(self, update_history: bool = True) -> None:
        """|coro|

        This method will mark the current chapter as unread for the current authenticated user in the MangaDex API.

        Parameters
        -----------
        update_history: :class:`bool`
            Whether to include this chapter in the authenticated user's read history.
        """
        if self.manga_id:
            await self._http._manga_read_markers_batch(
                self.manga_id, update_history=update_history, read_chapters=None, unread_chapters=[self.id]
            )

    async def _pages(
        self, *, start: int, end: Optional[int], data_saver: bool, ssl: bool, report: bool
    ) -> AsyncGenerator[tuple[bytes, str], None]:
        at_home_data = await self.get_at_home(ssl=ssl)
        self._at_home_url = at_home_data.base_url

        _pages = at_home_data.data_saver if data_saver else at_home_data.data
        _actual_pages = _pages[start:] if end is None else _pages[start:end]
        for i, url in enumerate(_actual_pages, start=1):
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

            if report and self._at_home_url != "https://uploads.mangadex.org":
                await self._http._at_home_report(
                    url=route.url,
                    success=page_resp.status == 200,
                    cached=("X-Cache" in page_resp.headers and page_resp.headers["X-Cache"].upper().startswith("HIT")),
                    size=(page_resp.content_length or 0),
                    duration=int(_total * 1000),
                )

            if page_resp.status != 200:
                self._at_home_url = None
                break
            else:
                yield data, url.rsplit(".")[-1]

        else:
            return

        # This code path will only be reached if there was an error downloading any of the pages.
        # It basically restarts the entire process starting from the page with errors.
        async for page in self._pages(start=i, end=end, data_saver=data_saver, ssl=ssl, report=report):
            yield page

    async def download(
        self,
        path: Optional[Union[PathLike[str], str]] = None,
        *,
        start_page: int = 0,
        end_page: Optional[int] = None,
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
        end_page: Optional[:class:`int`]
            The page at which to stop downloading, leave at ``None`` to download all pages after the start page.
        data_saver: :class:`bool`
            Whether to use the smaller (and poorer quality) images, if you are on a data budget. Defaults to ``False``.
        ssl: :class:`bool`
            Whether to request an SSL @Home link from MangaDex, this guarantees https as compared to potentially getting an HTTP url.
            Defaults to ``False``.
        report: :class:`bool`
            Whether to report success or failures to MangaDex per page download.
            The API guidelines ask us to do this, so it defaults to ``True``.
            Does not count towards your (user) rate-limits.
        """
        path = path or f"{self.chapter} - {self.title}"
        path_ = pathlib.Path(path)
        if not path_.exists():
            path_.mkdir(parents=True, exist_ok=True)

        idx = 1
        async for page_data, page_ext in self._pages(
            start=start_page, end=end_page, data_saver=data_saver, ssl=ssl, report=report
        ):
            download_path = path_ / f"{idx}.{page_ext}"
            with open(download_path, "wb") as f:
                f.write(page_data)
                LOGGER.info("Downloaded to: %s", download_path)
                await asyncio.sleep(0)
            idx += 1

    async def download_bytes(
        self,
        *,
        start_page: int = 0,
        end_page: Optional[int] = None,
        data_saver: bool = False,
        ssl: bool = False,
        report: bool = True,
    ) -> AsyncGenerator[bytes, None]:
        """|coro|

        This method will attempt to download a chapter for you using the MangaDex process, and return the bytes
        of each page. This is similar to :meth:`.download`, but instead of writing to a directory it returns
        the bytes directly.

        Parameters
        -----------
        start_page: :class:`int`
            The page at which to start downloading, leave at 0 (default) to download all.
        end_page: Optional[:class:`int`]
            The page at which to stop downloading, leave at ``None`` to download all pages after the start page.
        data_saver: :class:`bool`
            Whether to use the smaller (and poorer quality) images, if you are on a data budget. Defaults to
            ``False``.
        ssl: :class:`bool`
            Whether to request an SSL @Home link from MangaDex, this guarantees https as compared to
            potentially getting an HTTP url.
            Defaults to ``False``.
        report: :class:`bool`
            Whether to report success or failures to MangaDex per page download.
            The API guidelines ask us to do this, so it defaults to ``True``.

        Yields
        -------
        :class:`bytes`
            The bytes of each page.
        """
        async for page_data, _ in self._pages(start=start_page, end=end_page, data_saver=data_saver, ssl=ssl, report=report):
            yield page_data


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
        chapter: GetAtHomeChapterResponse = payload.pop("chapter")  # type: ignore # can't pop from a TypedDict
        self.hash: str = chapter["hash"]
        self.data: list[str] = chapter["data"]
        self.data_saver: list[str] = chapter["dataSaver"]

    def __repr__(self) -> str:
        return f"<ChapterAtHome hash={self.hash!r}>"

    def __eq__(self, other: ChapterAtHome) -> bool:
        return isinstance(other, ChapterAtHome) and self.hash == other.hash


class UploadData:
    """
    A small helper object to store the upload data for each upload session and holds respective responses and errors.

    Attributes
    -----------
    succeeded: List[:class:`~hondana.types.upload.UploadedChapterResponse`]
        The succeeded responses from the upload session.
    errors: List[:class:`~hondana.types.errors.ErrorType`]
        The errors from the upload session.
    has_failures: :class:`bool`
        The upload has errors.
    """

    __slots__ = (
        "succeeded",
        "errors",
        "has_failures",
        "_filenames",
        "_cs_errored_files",
    )

    def __init__(self, succeeded: list[UploadedChapterResponse], errors: list[ErrorType], /, *, filenames: set[str]) -> None:
        self.succeeded: list[UploadedChapterResponse] = succeeded
        self.errors: list[ErrorType] = errors
        self.has_failures: bool = len(errors) > 0
        self._filenames: set[str] = filenames

    def __repr__(self) -> str:
        return f"<UploadData success_count={len(self.succeeded)} error_count={len(self.errors)}>"

    def __str__(self) -> str:
        return f"UploadData with {len(self.succeeded)} succeeded and {len(self.errors)} errors."

    @cached_slot_property("_cs_errored_files")
    def errored_files(self) -> set[str]:
        """A property that returns a set of filenames that failed to upload.

        Returns
        --------
        Set[:class:`str`]
            The filenames of the failed uploads.
        """
        _succeeded: set[str] = set()
        for item in self.succeeded:
            for data in item["data"]:
                _succeeded.add(data["attributes"]["originalFileName"])

        return self._filenames ^ _succeeded


class ChapterUpload:
    """
    A context manager for handling the uploading of chapters to the MangaDex API.

    Parameters
    -----------
    manga: :class:`~hondana.Manga`
        The manga we are uploading a chapter for.
    volume: Optional[:class:`str`]
        The volume name/number this chapter is/for.
        Defaults to ``None``.
    chapter: :class:`str`
        The chapter name/number.
    chapter_to_edit: Optional[Union[:class:`~hondana.Chapter`, :class:`str`]]
        The chapter we are editing, if we are editing a chapter.
        Defaults to ``None``.
    title: Optional[:class:`str`]
        The chapter's title.
        Defaults to ``None``.
    translated_language: :class:`~hondana.types.common.LanguageCode`
        The language this chapter is translated in.
    external_url: Optional[:class:`str`]
        The external link to this chapter, if any.
        Using this parameter requires an explicit permission MD side.
    publish_at: Optional[:class:`datetime.datetime`]
        The future date at which to publish this chapter (and pages) to MangaDex.
    scanlator_groups: List[:class:`str`]
        The list of scanlator group IDs to attribute to this chapter.
    existing_upload_session_id: :class:`str`
        If you already have an open upload session and wish to resume there, please pass the ID to this attribute.
    version: Optional[:class:`int`]
        The version you are updating a chapter to.
        Parameter is ignored if ``chapter_to_edit`` is ``None``.

    Raises
    -------
    :exc:`TypeError`
        If you provide more than 10 ScanlatorGroups.
    :exc:`TypeError`
        If you provide a chapter to edit but do not specify the version.
    """

    __slots__ = (
        "_http",
        "manga",
        "volume",
        "chapter",
        "chapter_to_edit",
        "title",
        "translated_language",
        "external_url",
        "publish_at",
        "scanlator_groups",
        "uploaded",
        "upload_errors",
        "upload_session_id",
        "version",
        "_uploaded_filenames",
        "__committed",
    )

    def __init__(
        self,
        http: HTTPClient,
        manga: Union[Manga, str],
        /,
        *,
        chapter: str,
        chapter_to_edit: Optional[Union[Chapter, str]] = None,
        volume: Optional[str] = None,
        title: Optional[str] = None,
        translated_language: LanguageCode,
        scanlator_groups: list[str],
        external_url: Optional[str] = None,
        publish_at: Optional[datetime.datetime] = None,
        existing_upload_session_id: Optional[str] = None,
        version: Optional[int] = None,
    ) -> None:
        if len(scanlator_groups) > 10:
            raise ValueError("You can only attribute up to 10 scanlator groups per upload.")

        if chapter_to_edit and not version:
            raise ValueError("You must specify a version if you are editing a chapter.")

        self._http: HTTPClient = http
        self.manga: Union[Manga, str] = manga
        self.volume: Optional[str] = volume
        self.chapter: str = chapter
        self.chapter_to_edit: Optional[Union[Chapter, str]] = chapter_to_edit
        self.title: Optional[str] = title
        self.translated_language: LanguageCode = translated_language
        self.external_url: Optional[str] = external_url
        self.publish_at: Optional[datetime.datetime] = publish_at
        self.scanlator_groups: list[str] = scanlator_groups
        self.uploaded: list[str] = []
        self.upload_errors: list[ErrorType] = []
        self.upload_session_id: Optional[str] = existing_upload_session_id
        self.version: Optional[int] = version
        self._uploaded_filenames: set[str] = set()
        self.__committed: bool = False

    def __repr__(self) -> str:
        return f"<ChapterUpload id={self.upload_session_id!r} current_uploads={len(self.uploaded)}>"

    async def _check_for_session(self) -> None:
        route = Route("GET", "/upload")
        try:
            data: GetUploadSessionResponse = await self._http.request(route)
        except NotFound:
            LOGGER.info("No upload session found, continuing.")
        else:
            raise UploadInProgress(
                f"You already have an existing session, please terminate it: {data['data']['id']}",
                session_id=data["data"]["id"],
            )

    @require_authentication
    async def open_session(self) -> BeginChapterUploadResponse:
        """|coro|

        Opens an upload session and retrieves the session ID.

        Returns
        --------
        :class:`~hondana.types.upload.BeginChapterUploadResponse`
        """
        manga_id = self.manga.id if isinstance(self.manga, Manga) else self.manga
        if self.chapter_to_edit is not None:
            chapter_id = self.chapter_to_edit.id if isinstance(self.chapter_to_edit, Chapter) else self.chapter_to_edit
            return await self._http._open_upload_session(
                manga_id, scanlator_groups=self.scanlator_groups, chapter_id=chapter_id, version=self.version
            )
        return await self._http._open_upload_session(
            manga_id, scanlator_groups=self.scanlator_groups, chapter_id=None, version=None
        )

    @require_authentication
    async def upload_images(
        self,
        images: list[pathlib.Path],
        *,
        sort: bool = True,
        sorting_key: Optional[Callable[[pathlib.Path], Any]] = None,
    ) -> UploadData:
        """|coro|

        This method will take a list of bytes and upload them to the MangaDex API.

        Parameters
        -----------
        images: List[:class:`pathlib.Path`]
            A list of images files as their Path objects.
        sort: :class:`bool`
            A bool to toggle if we sort the list of Paths alphabetically.
        sorting_key: Optional[Callable[[:class:`pathlib.Path`], Any]]
            A key to use in the sorting of the list of above paths.
            This callable is passed to the ``key`` parameter of the ``sorted`` builtin.
            If ``None``, the default sorting key is used.

        Returns
        --------
        :class:`~hondana.chapter.UploadData`
            The upload data object of this upload session.


        .. note::
            If ``sort`` is set to ``True`` then the library will sort the list of image paths alphabetically.
            This means that ``1.png``, ``11.png``, and ``2.png`` will be sorted to ``1.png``, ``2.png``, and ``11.png``.

            The autosort the library provides only supports the following filename formats:
                - ``1.png``
                - ``1-something.png``


        .. note::
            If ``sorting_key`` is provided, then it must be a callable that takes a single parameter of ``pathlib.Path`` and returns a sortable value.
            This means that the return value of ``sorting_key`` must be richly comparable, with ``__lt__`` and ``__gt__``.
        """
        route = Route("POST", "/upload/{session_id}", session_id=self.upload_session_id)
        success: list[UploadedChapterResponse] = []

        if sort:
            sort_key = sorting_key or upload_file_sort
            images = sorted(images, key=sort_key)

        chunks = as_chunks(images, 10)
        outer_idx = 1
        for batch in chunks:
            form = aiohttp.FormData()
            for _, item in enumerate(batch, start=outer_idx):
                with item.open("rb") as f:
                    data = f.read()

                form.add_field(name=item.name, value=data)
                self._uploaded_filenames.add(item.name)
                outer_idx += 1

            response: UploadedChapterResponse = await self._http.request(route, data=form)
            for item in response["data"]:
                self.uploaded.append(item["id"])

            # check for errors in upload
            if response["errors"]:
                self.upload_errors.extend(response["errors"])

            success.append(response)

        data = UploadData(success, self.upload_errors, filenames=self._uploaded_filenames)

        return data

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
            payload["chapterDraft"]["publishAt"] = clean_isoformat(self.publish_at)

        route = Route("POST", "/upload/{session_id}/commit", session_id=self.upload_session_id)
        data: GetSingleChapterResponse = await self._http.request(route, json=payload)

        self.__committed = True
        return Chapter(self._http, data["data"])

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


class PreviouslyReadChapter:
    """
    A richer interface for chapter read histories.

    Attributes
    -----------
    chapter_id: :class:`str`
        The previously read chapter's ID.
    read_date: :class:`datetime.datetime`
        The datetime (in UTC) when this chapter was marked as read.
    """

    def __init__(self, http: HTTPClient, data: tuple[str, str]) -> None:
        self._http = http
        self.chapter_id: str = data[0]
        dt = datetime.datetime.strptime(data[1], "%Y-%m-%dT%H:%M:%S.%fZ")
        dt.replace(tzinfo=datetime.timezone.utc)
        self.read_date: datetime.datetime = dt

    async def fetch_chapter(self, *, includes: ChapterIncludes = ChapterIncludes()) -> Chapter:
        """|coro|

        This method will fetch the chapter from the ID in the read payload.

        Returns
        ---------
        :class:`~hondana.Chapter`
        """
        data = await self._http._get_chapter(self.chapter_id, includes=includes)
        return Chapter(self._http, data["data"])
