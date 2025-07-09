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
import json
import logging
import operator
import pathlib
from typing import TYPE_CHECKING, Any, TypeVar, overload

from . import errors
from .artist import Artist
from .author import Author
from .chapter import Chapter, ChapterUpload, PreviouslyReadChapter
from .collections import (
    AuthorCollection,
    ChapterFeed,
    ChapterReadHistoryCollection,
    CoverCollection,
    CustomListCollection,
    LegacyMappingCollection,
    MangaCollection,
    MangaRelationCollection,
    ScanlatorGroupCollection,
    UserCollection,
    UserReportCollection,
)
from .cover import Cover
from .custom_list import CustomList
from .enums import (
    ContentRating,
    CustomListVisibility,
    ForumThreadType,
    MangaRelationType,
    MangaState,
    MangaStatus,
    PublicationDemographic,
    ReadingStatus,
    ReportCategory,
    ReportReason,
    ReportStatus,
)
from .forums import ForumThread
from .http import HTTPClient
from .legacy import LegacyItem
from .manga import Manga, MangaRating, MangaRelation, MangaStatistics
from .query import (
    ArtistIncludes,
    AuthorIncludes,
    AuthorListOrderQuery,
    ChapterIncludes,
    CoverArtListOrderQuery,
    CoverIncludes,
    CustomListIncludes,
    FeedOrderQuery,
    MangaDraftListOrderQuery,
    MangaIncludes,
    MangaListOrderQuery,
    ReportListOrderQuery,
    ScanlatorGroupIncludes,
    ScanlatorGroupListOrderQuery,
    UserListOrderQuery,
    UserReportIncludes,
)
from .report import ReportDetails, UserReport
from .scanlator_group import ScanlatorGroup
from .tags import Tag
from .user import User
from .utils import MISSING, deprecated, require_authentication

if TYPE_CHECKING:
    from types import TracebackType
    from typing import Self

    from aiohttp import ClientSession

    from .tags import QueryTags
    from .types_ import common, legacy, manga
    from .types_.settings import Settings, SettingsPayload

    T = TypeVar("T")
    BE = TypeVar("BE", bound=BaseException)

_PROJECT_DIR = pathlib.Path(__file__)
LOGGER: logging.Logger = logging.getLogger(__name__)

__all__ = ("Client",)


class Client:
    """User Client for interfacing with the MangaDex API.

    Parameters
    ----------
    session: :class:`aiohttp.ClientSession` | None
        An optional ClientSession to pass to the client for internal use.
    username: :class:`str` | None
        The username of the account to use.
    password: :class:`str` | None
        The password of the account to use.
    client_id: :class:`str` | None
        The OAuth2 Client ID to use.
    client_secret: :class:`str` | None
        The OAuth2 Client Secret to use.
    dev_api: :class:`bool`
        If you want to use the Dev api instead of production.
        Defaults to ``False``.


    .. note::
        The Client will work without authentication, but all authenticated endpoints will fail before attempting a request.
    """

    __slots__ = ("_http",)

    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(
        self,
        *,
        session: ClientSession | None = ...,
        username: str,
        password: str,
        client_id: str,
        client_secret: str,
        dev_api: bool = ...,
    ) -> None: ...

    @overload
    def __init__(self, *, session: ClientSession) -> None: ...

    @overload
    def __init__(self, *, dev_api: bool) -> None: ...

    def __init__(
        self,
        *,
        session: ClientSession | None = None,
        username: str | None = None,
        password: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        dev_api: bool = False,
    ) -> None:
        self._http: HTTPClient = HTTPClient(
            session=session,
            username=username,
            password=password,
            client_id=client_id,
            client_secret=client_secret,
            dev_api=dev_api,
        )

    async def __aenter__(self) -> Self:
        try:
            await self.login()
        except RuntimeError:
            # we haven't set credentials so just a warning
            LOGGER.warning("No OAuth2 credentials set, so not logging in.")

        return self

    async def __aexit__(self, type_: type[BE] | None, value: BE, traceback: TracebackType) -> None:  # noqa: PYI036 # not expanding the typevar
        await self.close()

    async def login(self) -> None:
        """|coro|

        A standalone method to log in to the API with the provided credentials.

        This method is usually implicily called for you by the library.

        Raises
        ------
        RuntimeError
            No login credentials were supplied to the client before attempting to log in.
        """
        if not self._http._authenticated:  # pyright: ignore[reportPrivateUsage] # noqa: SLF001 # sanity reasons
            msg = "Cannot login as no OAuth2 credentials are set."
            raise RuntimeError(msg)

        await self._http.get_token()

    async def close(self) -> None:
        """|coro|

        Logs the client out of the API and closes the internal http session.
        """
        return await self._http.close()

    async def check_username_available(self, username: str) -> bool:
        """|coro|

        This method will check if the username supplied is available for use on MangaDex.

        Parameters
        ----------
        username: :class:`str`
            The username to check for.

        Raises
        ------
        Forbidden
            The request failed due to authorization.

        Returns
        -------
        :class:`bool`
            If the username is available or not.
        """  # noqa: DOC502 # raised in method call
        data = await self._http.account_available(username)
        return data["available"]

    async def update_tags(self) -> dict[str, str]:
        """|coro|

        Convenience method for updating the local cache of tags.

        This should ideally not need to be called by the end user but nevertheless it exists in the event MangaDex
        add a new tag or similar.

        Returns
        -------
        Dict[:class:`str`, :class:`str`]
            The new tags from the API.
        """
        tags = await self.get_tags()

        pre_fmt = {tag.name: tag.id for tag in tags}
        fmt = dict(sorted(pre_fmt.items(), key=operator.itemgetter(0)))

        path = _PROJECT_DIR.parent / "extras" / "tags.json"
        with path.open("w") as fp:
            json.dump(fmt, fp, indent=4)

        return fmt

    async def update_report_reasons(self) -> dict[str, dict[str, str]]:
        """|coro|

        Convenience method for updating the local cache of report reasons.

        This should ideally not need to be called by the end user but nevertheless it exists in the event MangaDex
        add a new report reasons or similar.

        Returns
        -------
        Dict[:class:`str`, Dict[:class:`str`, :class:`str`]]
            The new report reasons from the API.


        .. warning::
            This method makes 5 API requests, which if called unnecessarily could result in a ratelimit.
        """
        ret: dict[str, dict[str, str]] = {}

        categories_ = [
            ReportCategory.author,
            ReportCategory.chapter,
            ReportCategory.scanlation_group,
            ReportCategory.manga,
            ReportCategory.user,
        ]

        for category in categories_:
            data = await self._http.get_report_reason_list(category)
            ret[category.value] = {}
            for inner in data["data"]:
                key_name = (
                    inner["attributes"]["reason"]["en"].lower().replace("-", "").replace("/", " or ").replace(" ", "_")  # pyright: ignore[reportTypedDictNotRequiredAccess] # these will always be in the `en` key.
                )
                ret[category.value][key_name] = inner["id"]

        for clean_data, values in ret.items():
            ret[clean_data] = dict(sorted(values.items()))

        path = _PROJECT_DIR.parent / "extras" / "report_reasons.json"
        with path.open("w") as fp:
            json.dump(ret, fp, indent=4)

        return ret

    async def get_tags(self) -> list[Tag]:
        """|coro|

        This method will retrieve the current list of tags on MangaDex.

        Returns
        -------
        List[:class:`~hondana.Tag`]
            The list of tags.
        """
        data = await self._http.update_tags()

        return [Tag(item) for item in data["data"]]

    @require_authentication
    async def get_my_feed(
        self,
        *,
        limit: int | None = 100,
        offset: int = 0,
        translated_language: list[common.LanguageCode] | None = None,
        original_language: list[common.LanguageCode] | None = None,
        excluded_original_language: list[common.LanguageCode] | None = None,
        content_rating: list[ContentRating] | None = None,
        excluded_groups: list[str] | None = None,
        excluded_uploaders: list[str] | None = None,
        include_future_updates: bool | None = None,
        created_at_since: datetime.datetime | None = None,
        updated_at_since: datetime.datetime | None = None,
        published_at_since: datetime.datetime | None = None,
        order: FeedOrderQuery | None = None,
        includes: ChapterIncludes | None = None,
        include_empty_pages: bool | None = None,
        include_future_publish_at: bool | None = None,
        include_external_url: bool | None = None,
        include_unavailable: bool | None = None,
    ) -> ChapterFeed:
        """|coro|

        This method will retrieve the logged-in user's followed manga chapter feed.

        Parameters
        ----------
        limit: :class:`int`
            Defaults to 100. This is the limit of manga that is returned in this request,
            it is clamped at 500 as that is the max in the API.
        offset: :class:`int`
            Defaults to 0. This is the pagination offset, the number must be greater than 0.
            If set lower than 0 then it is set to 0.
        translated_language: List[:class:`~hondana.types_.common.LanguageCode`]
            A list of language codes to filter the returned chapters with.
        original_language: List[:class:`~hondana.types_.common.LanguageCode`]
            A list of language codes to filter the original language of the returned chapters with.
        excluded_original_language: List[:class:`~hondana.types_.common.LanguageCode`]
            A list of language codes to negate filter the original language of the returned chapters with.
        content_rating: Optional[List[:class:`~hondana.ContentRating`]]
            The content rating to filter the feed by.
        excluded_groups: Optional[List[:class:`str`]]
            The list of scanlator groups to exclude from the response.
        excluded_uploaders: Optional[List[:class:`str`]]
            The list of uploaders to exclude from the response.
        include_future_updates: Optional[:class:`bool`]
            Whether to include future release chapters from the feeds, defaults to ``"1"`` API side.
        created_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their creation date.
        updated_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their update date.
        published_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their published date.
        order: Optional[:class:`~hondana.query.FeedOrderQuery`]
            A query parameter to choose the 'order by' response from the API.
        includes: Optional[:class:`~hondana.query.ChapterIncludes`]
            The optional data to include in the response.
        include_empty_pages: Optional[:class:`bool`]
            Whether to show chapters with no pages available.
        include_future_publish_at: Optional[:class:`bool`]
            Whether to show chapters with a publishAt value set in the future.
        include_external_url: Optional[:class:`bool`]
            Whether to show chapters that have an external URL attached to them.
        include_unavailable: Optional[:class:`bool`]
            Whether to show chapters that are marked as unavailable.


        .. note::
            If no start point is given with the `created_at_since`, `updated_at_since` or `published_at_since` parameters,
            then the API will return oldest first based on creation date.

        Raises
        ------
        BadRequest
            The query parameters were not valid.

        Returns
        -------
        :class:`~hondana.ChapterFeed`
            Returns a collection of chapters.
        """  # noqa: DOC502 # raised in method call
        inner_limit = limit or 100

        chapters: list[Chapter] = []
        while True:
            data = await self._http.manga_feed(
                None,
                limit=inner_limit,
                offset=offset,
                translated_language=translated_language,
                original_language=original_language,
                excluded_original_language=excluded_original_language,
                content_rating=content_rating,
                excluded_groups=excluded_groups,
                excluded_uploaders=excluded_uploaders,
                include_future_updates=include_future_updates,
                created_at_since=created_at_since,
                updated_at_since=updated_at_since,
                published_at_since=published_at_since,
                order=order,
                includes=includes or ChapterIncludes(),
                include_empty_pages=include_empty_pages,
                include_future_publish_at=include_future_publish_at,
                include_external_url=include_external_url,
                include_unavailable=include_unavailable,
            )

            chapters.extend([Chapter(self._http, item) for item in data["data"]])

            offset += inner_limit
            if not data["data"] or offset >= 10_000 or limit is not None:
                break

        return ChapterFeed(self._http, data, chapters)

    subscription_feed = get_my_feed

    async def manga_list(
        self,
        *,
        limit: int | None = 100,
        offset: int = 0,
        title: str | None = None,
        author_or_artist: str | None = None,
        authors: list[str] | None = None,
        artists: list[str] | None = None,
        year: int | None = MISSING,
        included_tags: QueryTags | None = None,
        excluded_tags: QueryTags | None = None,
        status: list[MangaStatus] | None = None,
        original_language: list[common.LanguageCode] | None = None,
        excluded_original_language: list[common.LanguageCode] | None = None,
        available_translated_language: list[common.LanguageCode] | None = None,
        publication_demographic: list[PublicationDemographic] | None = None,
        ids: list[str] | None = None,
        content_rating: list[ContentRating] | None = None,
        created_at_since: datetime.datetime | None = None,
        updated_at_since: datetime.datetime | None = None,
        order: MangaListOrderQuery | None = None,
        includes: MangaIncludes | None = None,
        has_available_chapters: bool | None = None,
        has_unavailable_chapters: bool | None = None,
        group: str | None = None,
    ) -> MangaCollection:
        """|coro|

        This method will perform a search based on the passed query parameters for manga.

        Parameters
        ----------
        limit: Optional[:class:`int`]
            Defaults to 100. This is the limit of manga that is returned in this request,
            it is clamped at 500 as that is the max in the API.
        offset: :class:`int`
            Defaults to 0. This is the pagination offset, the number must be greater than 0.
            If set lower than 0 then it is set to 0.
        title: Optional[:class:`str`]
            The manga title or partial title to include in the search.
        author_or_artist: Optional[:class:`str`]
            A uuid to filter the manga list that represents an author or artist.
        authors: Optional[List[:class:`str`]]
            The author(s) UUIDs to include in the search.
        artists: Optional[List[:class:`str`]]
            The artist(s) UUIDs to include in the search.
        year: Optional[:class:`int`]
            The release year of the manga to include in the search. Allows passing of ``None`` to
            search for manga with no year specified.
        included_tags: Optional[:class:`QueryTags`]
            An instance of :class:`hondana.QueryTags` to include in the search.
        excluded_tags: Optional[:class:`QueryTags`]
            An instance of :class:`hondana.QueryTags` to include in the search.
        status: Optional[List[:class:`~hondana.MangaStatus`]]
            The status(es) of manga to include in the search.
        original_language: Optional[List[:class:`~hondana.types_.common.LanguageCode`]]
            A list of language codes to include for the manga's original language.
            i.e. ``["en"]``
        excluded_original_language: Optional[List[:class:`~hondana.types_.common.LanguageCode`]]
            A list of language codes to exclude for the manga's original language.
            i.e. ``["en"]``
        available_translated_language: Optional[List[:class:`~hondana.types_.common.LanguageCode`]]
            A list of language codes to filter they available translation languages in.
            i.e. ``["en"]``
        publication_demographic: Optional[List[:class:`~hondana.PublicationDemographic`]]
            The publication demographic(s) to limit the search to.
        ids: Optional[:class:`str`]
            A list of manga UUID(s) to limit the search to.
        content_rating: Optional[List[:class:`~hondana.ContentRating`]]
            The content rating(s) to filter the search to.
        created_at_since: Optional[datetime.datetime]
            A (naive UTC) datetime instance we specify for searching.
            Used for returning manga created *after* this date.
        updated_at_since: Optional[datetime.datetime]
            A (naive UTC) datetime instance we specify for searching.
            Used for returning manga updated *after* this date.
        order: Optional[:class:`~hondana.query.MangaListOrderQuery`]
            A query parameter to choose the ordering of the response.
        includes: Optional[:class:`~hondana.query.MangaIncludes`]
            A list of things to include in the returned manga response payloads.
            i.e. ``["author", "cover_art", "artist"]``
            Defaults to these values.
        has_available_chapters: Optional[:class:`bool`]
            Filter the manga list to only those that have chapters.
        has_unavailable_chapters: Optional[:class:`bool`]
            Filter the manga list to only those that have chapters marked as unavailable.
        group: Optional[:class:`str`]
            Filter the manga list to only those uploaded by this group.


        .. note::
            Passing ``None`` to ``limit`` will attempt to retrieve all items in the manga list.

        Raises
        ------
        BadRequest
            The query parameters were not valid.

        Returns
        -------
        :class:`~hondana.MangaCollection`
            Returns a collection of Manga.
        """  # noqa: DOC502 # raised in method call
        inner_limit = limit or 100

        manga: list[Manga] = []
        while True:
            data = await self._http.manga_list(
                limit=inner_limit,
                offset=offset,
                title=title,
                author_or_artist=author_or_artist,
                authors=authors,
                artists=artists,
                year=year,
                included_tags=included_tags,
                excluded_tags=excluded_tags,
                status=status,
                original_language=original_language,
                excluded_original_language=excluded_original_language,
                available_translated_language=available_translated_language,
                publication_demographic=publication_demographic,
                ids=ids,
                content_rating=content_rating,
                created_at_since=created_at_since,
                updated_at_since=updated_at_since,
                order=order,
                includes=includes or MangaIncludes(),
                has_available_chapters=has_available_chapters,
                has_unavailable_chapters=has_unavailable_chapters,
                group=group,
            )

            manga.extend([Manga(self._http, item) for item in data["data"]])

            offset += inner_limit
            if not data["data"] or offset >= 10_000 or limit is not None:
                break

        return MangaCollection(self._http, data, manga)

    @require_authentication
    async def create_manga(
        self,
        *,
        title: common.LocalizedString,
        alt_titles: list[common.LocalizedString] | None = None,
        description: common.LocalizedString | None = None,
        authors: list[str] | None = None,
        artists: list[str] | None = None,
        links: manga.MangaLinks | None = None,
        original_language: str,
        last_volume: str | None = None,
        last_chapter: str | None = None,
        publication_demographic: PublicationDemographic | None = None,
        status: MangaStatus,
        year: int | None = None,
        content_rating: ContentRating,
        tags: QueryTags | None = None,
        mod_notes: str | None = None,
    ) -> Manga:
        """|coro|

        This method will create a Manga within the MangaDex API for you.

        Parameters
        ----------
        title: :class:`~hondana.types_.common.LocalizedString`
            The manga titles in the format of ``language_key: title``
            i.e. ``{"en": "Some Manga Title"}``
        alt_titles: Optional[List[:class:`~hondana.types_.common.LocalizedString`]]
            The alternative titles in the format of ``language_key: title``
            i.e. ``[{"en": "Some Other Title"}, {"fr": "Un Autre Titre"}]``
        description: Optional[:class:`~hondana.types_.common.LocalizedString`]
            The manga description in the format of ``language_key: description``
            i.e. ``{"en": "My amazing manga where x y z happens"}``
        authors: Optional[List[:class:`str`]]
            The list of author UUIDs to credit to this manga.
        artists: Optional[List[:class:`str`]]
            The list of artist UUIDs to credit to this manga.
        links: Optional[:class:`~hondana.types_.manga.MangaLinks`]
            The links relevant to the manga.
            See here for more details: https://api.mangadex.org/docs.html#section/Static-data/Manga-links-data
        original_language: :class:`str`
            The language key for the original language of the manga.
        last_volume: Optional[:class:`str`]
            The last volume to attribute to this manga.
        last_chapter: Optional[:class:`str`]
            The last chapter to attribute to this manga.
        publication_demographic: Optional[:class:`~hondana.PublicationDemographic`]
            The target publication demographic of this manga.
        status: :class:`~hondana.MangaStatus`
            The status of the manga.
        year: Optional[:class:`int`]
            The release year of the manga.
        content_rating: :class:`~hondana.ContentRating`
            The content rating of the manga.
        tags: Optional[:class:`QueryTags`]
            The QueryTags instance for the list of tags to attribute to this manga.
        mod_notes: Optional[:class:`str`]
            The moderator notes to add to this Manga.


        .. note::
            The ``mod_notes`` parameter requires the logged-in user to be a MangaDex moderator.
            Leave this as ``None`` unless you fit these criteria.

        Raises
        ------
        BadRequest
            The query parameters were not valid.
        Forbidden
            The query failed due to authorization failure.

        Returns
        -------
        :class:`~hondana.Manga`
            The manga that was returned after creation.
        """  # noqa: DOC502 # raised in method call
        data = await self._http.create_manga(
            title=title,
            alt_titles=alt_titles,
            description=description,
            authors=authors,
            artists=artists,
            links=links,
            original_language=original_language,
            last_volume=last_volume,
            last_chapter=last_chapter,
            publication_demographic=publication_demographic,
            status=status,
            year=year,
            content_rating=content_rating,
            tags=tags,
            mod_notes=mod_notes,
        )

        return Manga(self._http, data["data"])

    async def get_manga_volumes_and_chapters(
        self,
        manga_id: str,
        /,
        *,
        translated_language: list[common.LanguageCode] | None = None,
        groups: list[str] | None = None,
    ) -> manga.GetMangaVolumesAndChaptersResponse:
        """|coro|

        This endpoint returns the raw relational mapping of a manga's volumes and chapters.

        Parameters
        ----------
        manga_id: :class:`str`
            The manga UUID we are querying against.
        translated_language: Optional[List[:class:`~hondana.types_.common.LanguageCode`]]
            The list of language codes you want to limit the search to.
        groups: Optional[List[:class:`str`]]
            A list of scanlator groups to filter the results by.

        Returns
        -------
        :class:`~hondana.types_.manga.GetMangaVolumesAndChaptersResponse`
            The raw payload from mangadex. There is no guarantee of the keys here.
        """
        return await self._http.get_manga_volumes_and_chapters(
            manga_id=manga_id,
            translated_language=translated_language,
            groups=groups,
        )

    async def get_manga(self, manga_id: str, /, *, includes: MangaIncludes | None = None) -> Manga:
        """|coro|

        The method will fetch a Manga from the MangaDex API.

        Parameters
        ----------
        manga_id: :class:`str`
            The UUID of the manga to view.
        includes: Optional[:class:`~hondana.query.MangaIncludes`]
            The includes query parameter for this manga.
            If not given, it defaults to all possible reference expansions.

        Raises
        ------
        Forbidden
            The query failed due to authorization failure.
        NotFound
            The passed manga ID was not found, likely due to an incorrect ID.

        Returns
        -------
        :class:`~hondana.Manga`
            The Manga that was returned from the API.

        .. versionadded:: 2.0.11
        """  # noqa: DOC502 # raised in method call
        data = await self._http.get_manga(manga_id, includes=includes or MangaIncludes())

        return Manga(self._http, data["data"])

    @require_authentication
    async def update_manga(
        self,
        manga_id: str,
        /,
        *,
        title: common.LocalizedString | None = None,
        alt_titles: list[common.LocalizedString] | None = None,
        description: common.LocalizedString | None = None,
        authors: list[str] | None = None,
        artists: list[str] | None = None,
        links: manga.MangaLinks | None = None,
        original_language: str | None = None,
        last_volume: str | None = MISSING,
        last_chapter: str | None = MISSING,
        publication_demographic: PublicationDemographic | None = MISSING,
        status: MangaStatus | None,
        year: int | None = MISSING,
        content_rating: ContentRating | None = None,
        tags: QueryTags | None = None,
        primary_cover: str | None = MISSING,
        version: int,
    ) -> Manga:
        """|coro|

        This method will update a Manga within the MangaDex API.

        Parameters
        ----------
        manga_id: :class:`str`
            The UUID of the manga to update.
        title: Optional[:class:`~hondana.types_.common.LocalizedString`]
            The manga titles in the format of ``language_key: title``
        alt_titles: Optional[List[:class:`~hondana.types_.common.LocalizedString`]]
            The alternative titles in the format of ``language_key: title``
        description: Optional[:class:`~hondana.types_.common.LocalizedString`]
            The manga description in the format of ``language_key: description``
        authors: Optional[List[:class:`str`]]
            The list of author UUIDs to credit to this manga.
        artists: Optional[List[:class:`str`]]
            The list of artist UUIDs to credit to this manga.
        links: Optional[:class:`~hondana.types_.manga.MangaLinks`]
            The links relevant to the manga.
        original_language: Optional[:class:`str`]
            The language key for the original language of the manga.
        last_volume: Optional[:class:`str`]
            The last volume to attribute to this manga.
        last_chapter: Optional[:class:`str`]
            The last chapter to attribute to this manga.
        publication_demographic: :class:`~hondana.PublicationDemographic`
            The target publication demographic of this manga.
        status: Optional[:class:`~hondana.MangaStatus`]
            The status of the manga.
        year: Optional[:class:`int`]
            The release year of the manga.
        content_rating: Optional[:class:`~hondana.ContentRating`]
            The content rating of the manga.
        tags: Optional[:class:`~hondana.QueryTags`]
            The QueryTags instance for the list of tags to attribute to this manga.
        primary_cover: Optional[:class:`str`]
            The primary cover for this Manga.
        version: :class:`int`
            The revision version of this manga.


        .. note::
            The ``last_volume``, ``last_chapter``, ``publication_demographic``, ``year`` and ``primary_cover`` parameters
            are nullable in the API, pass ``None`` explicitly to do this.

        Raises
        ------
        BadRequest
            The query parameters were not valid.
        Forbidden
            The returned an error due to authentication failure.
        NotFound
            The specified manga does not exist.

        Returns
        -------
        :class:`~hondana.Manga`
            The manga that was returned after creation.
        """  # noqa: DOC502 # raised in method call
        data = await self._http.update_manga(
            manga_id,
            title=title,
            alt_titles=alt_titles,
            description=description,
            authors=authors,
            artists=artists,
            links=links,
            original_language=original_language,
            last_volume=last_volume,
            last_chapter=last_chapter,
            publication_demographic=publication_demographic,
            status=status,
            year=year,
            content_rating=content_rating,
            tags=tags,
            primary_cover=primary_cover,
            version=version,
        )

        return Manga(self._http, data["data"])

    @require_authentication
    async def delete_manga(self, manga_id: str, /) -> None:
        """|coro|

        This method will delete a manga within the MangaDex API.

        Parameters
        ----------
        manga_id: :class:`str`
            The ID of the manga we are deleting.

        Raises
        ------
        Forbidden
            The request returned an error due to authentication failure.
        NotFound
            The specified manga doesn't exist.
        """  # noqa: DOC502 # raised in method call
        await self._http.delete_manga(manga_id)

    @require_authentication
    async def unfollow_manga(self, manga_id: str, /) -> None:
        """|coro|

        This method will unfollow a Manga for the logged-in user in the MangaDex API.

        Parameters
        ----------
        manga_id: :class:`str`
            The UUID of the manga to unfollow.

        Raises
        ------
        Forbidden
            The request returned an error due to authentication failure.
        NotFound
            The specified manga does not exist.
        """  # noqa: DOC502 # raised in method call
        await self._http.unfollow_manga(manga_id)

    @require_authentication
    async def follow_manga(
        self,
        manga_id: str,
        /,
        *,
        set_status: bool = True,
        status: ReadingStatus = ReadingStatus.reading,
    ) -> None:
        """|coro|

        This method will follow a Manga for the logged-in user in the MangaDex API.

        Parameters
        ----------
        manga_id: :class:`str`
            The UUID of the manga to follow.
        set_status: :class:`bool`
            Whether to set the reading status of the manga you follow.
            Due to the current MangaDex infrastructure, not setting a status will cause
            the manga to not show up in your lists.
            Defaults to ``True``
        status: :class:`~hondana.ReadingStatus`
            The status to apply to the newly followed manga.
            Irrelevant if ``set_status`` is ``False``. Defaults to :attr:`ReadingStatus.reading`.

        Raises
        ------
        Forbidden
            The request returned an error due to authentication failure.
        NotFound
            The specified manga does not exist.
        """  # noqa: DOC502 # raised in method call
        await self._http.follow_manga(manga_id)
        if set_status:
            await self._http.update_manga_reading_status(manga_id, status=status)

    async def manga_feed(
        self,
        manga_id: str,
        /,
        *,
        limit: int | None = 100,
        offset: int = 0,
        translated_language: list[common.LanguageCode] | None = None,
        original_language: list[common.LanguageCode] | None = None,
        excluded_original_language: list[common.LanguageCode] | None = None,
        content_rating: list[ContentRating] | None = None,
        excluded_groups: list[str] | None = None,
        excluded_uploaders: list[str] | None = None,
        include_future_updates: bool | None = None,
        created_at_since: datetime.datetime | None = None,
        updated_at_since: datetime.datetime | None = None,
        published_at_since: datetime.datetime | None = None,
        order: FeedOrderQuery | None = None,
        includes: ChapterIncludes | None = None,
        include_empty_pages: bool | None = None,
        include_future_publish_at: bool | None = None,
        include_external_url: bool | None = None,
        include_unavailable: bool | None = None,
    ) -> ChapterFeed:
        """|coro|

        This method returns the specified manga's chapter feed.

        Parameters
        ----------
        manga_id: :class:`str`
            The UUID of the manga whose feed we are requesting.
        limit: Optional[:class:`int`]
            Defaults to 100. The maximum amount of chapters to return in the response.
        offset: :class:`int`
            Defaults to 0. The pagination offset for the request.
        translated_language: List[:class:`~hondana.types_.common.LanguageCode`]
            A list of language codes to filter the returned chapters with.
        original_language: List[:class:`~hondana.types_.common.LanguageCode`]
            A list of language codes to filter the original language of the returned chapters with.
        excluded_original_language: List[:class:`~hondana.types_.common.LanguageCode`]
            A list of language codes to negate filter the original language of the returned chapters with.
        content_rating: Optional[List[:class:`~hondana.ContentRating`]]
            The content rating to filter the feed by.
        excluded_groups: Optional[List[:class:`str`]]
            The list of scanlator groups to exclude from the response.
        excluded_uploaders: Optional[List[:class:`str`]]
            The list of uploaders to exclude from the response.
        include_future_updates: Optional[:class:`bool`]
            Whether to include future chapters from this feed. Defaults to ``"1"`` API side.
        created_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their creation date.
        updated_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their updated at date.
        published_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their published at date.
        order: Optional[:class:`~hondana.query.FeedOrderQuery`]
            A query parameter to choose how the responses are ordered.
        includes: Optional[:class:`~hondana.query.ChapterIncludes`]
            The options to include increased payloads for per chapter.
            Defaults to all values.
        include_empty_pages: Optional[:class:`bool`]
            Whether to show chapters with no pages available.
        include_future_publish_at: Optional[:class:`bool`]
            Whether to show chapters with a publishAt value set in the future.
        include_external_url: Optional[:class:`bool`]
            Whether to show chapters that have an external URL attached to them.
        include_unavailable: Optional[:class:`bool`]
            Whether to show chapters that are marked as unavailable.


        .. note::
            Passing ``None`` to ``limit`` will attempt to retrieve all items in the chapter feed.

        Raises
        ------
        BadRequest
            The query parameters were malformed.

        Returns
        -------
        :class:`~hondana.ChapterFeed`
            Returns a collection of chapters.
        """  # noqa: DOC502 # raised in method call
        inner_limit = limit or 100

        chapters: list[Chapter] = []
        while True:
            data = await self._http.manga_feed(
                manga_id,
                limit=inner_limit,
                offset=offset,
                translated_language=translated_language,
                original_language=original_language,
                excluded_original_language=excluded_original_language,
                content_rating=content_rating,
                excluded_groups=excluded_groups,
                excluded_uploaders=excluded_uploaders,
                include_future_updates=include_future_updates,
                created_at_since=created_at_since,
                updated_at_since=updated_at_since,
                published_at_since=published_at_since,
                order=order,
                includes=includes or ChapterIncludes(),
                include_empty_pages=include_empty_pages,
                include_future_publish_at=include_future_publish_at,
                include_external_url=include_external_url,
                include_unavailable=include_unavailable,
            )

            chapters.extend([Chapter(self._http, item) for item in data["data"]])

            offset += inner_limit
            if not data["data"] or offset >= 10_000 or limit is not None:
                break

        return ChapterFeed(self._http, data, chapters)

    @require_authentication
    async def manga_read_markers(
        self,
        *,
        manga_ids: list[str],
    ) -> manga.MangaReadMarkersResponse | manga.MangaGroupedReadMarkersResponse:
        """|coro|

        This method will return the read chapters of the passed manga if singular, or all manga if plural.

        Parameters
        ----------
        manga_ids: List[:class:`str`]
            A list of a single manga UUID or a list of many manga UUIDs.

        Returns
        -------
        Union[:class:`~hondana.types_.manga.MangaReadMarkersResponse`, :class:`~hondana.types_.manga.MangaGroupedReadMarkersResponse`]
        """  # noqa: E501 # required for formatting
        if len(manga_ids) == 1:
            return await self._http.manga_read_markers(manga_ids, grouped=False)
        return await self._http.manga_read_markers(manga_ids, grouped=True)

    @require_authentication
    async def batch_update_manga_read_markers(
        self,
        manga_id: str,
        /,
        *,
        update_history: bool = True,
        read_chapters: list[str] | None = None,
        unread_chapters: list[str] | None = None,
    ) -> None:
        """|coro|

        This method will batch update your read chapters for a given Manga.

        Parameters
        ----------
        manga_id: :class:`str`
            The Manga we are updating read chapters for.
        update_history: :class:`bool`
            Whether to show this chapter in the authenticated user's read history.
            Defaults to ``True``.
        read_chapters: Optional[List[:class:`str`]]
            The read chapters for this Manga.
        unread_chapters: Optional[List[:class:`str`]]
            The unread chapters for this Manga.

        Raises
        ------
        TypeError
            You must provide one or both of the parameters `read_chapters` and/or `unread_chapters`.
        """
        if read_chapters or unread_chapters:
            await self._http.manga_read_markers_batch(
                manga_id,
                update_history=update_history,
                read_chapters=read_chapters,
                unread_chapters=unread_chapters,
            )
            return
        msg = "You must provide either `read_chapters` and/or `unread_chapters` to this method."
        raise TypeError(msg)

    async def get_random_manga(
        self,
        *,
        includes: MangaIncludes | None = None,
        content_rating: list[ContentRating] | None = None,
        included_tags: QueryTags | None = None,
        excluded_tags: QueryTags | None = None,
    ) -> Manga:
        """|coro|

        This method will return a random manga from the MangaDex API.

        Parameters
        ----------
        includes: Optional[:class:`~hondana.query.MangaIncludes`]
            The optional includes for the manga payload.
            Defaults to all possible reference expansions.
        content_rating: Optional[List[:class:`~hondana.ContentRating`]]
            The content ratings to filter the random manga by
        included_tags: Optional[:class:`~hondana.QueryTags`]
            The tags and search mode to use for inclusion.
        excluded_tags: Optional[:class:`~hondana.QueryTags`]
            The tags and search mode to use for exclusion.

        Returns
        -------
        :class:`~hondana.Manga`
            The random Manga that was returned.
        """
        data = await self._http.get_random_manga(
            includes=includes or MangaIncludes(),
            content_rating=content_rating,
            included_tags=included_tags,
            excluded_tags=excluded_tags,
        )

        return Manga(self._http, data["data"])

    @require_authentication
    async def get_my_followed_manga(
        self,
        *,
        limit: int | None = 100,
        offset: int = 0,
        includes: MangaIncludes | None = None,
    ) -> MangaCollection:
        """|coro|

        This method will return an object containing all the followed manga from the currently logged-in user.

        Parameters
        ----------
        limit: Optional[:class:`int`]
            The amount of items we are requesting.
        offset: :class:`int`
            The pagination offset for the items we are requesting.
        includes: Optional[:class:`~hondana.query.MangaIncludes`]
            The optional includes to add to the api responses.


        .. note::
            Passing ``None`` to ``limit`` will attempt to retrieve all items in the followed manga list.

        Returns
        -------
        :class:`~hondana.MangaCollection`
            Returns a collection of manga.
        """
        inner_limit = limit or 100

        manga: list[Manga] = []
        while True:
            data = await self._http.get_user_followed_manga(
                limit=inner_limit,
                offset=offset,
                includes=includes or MangaIncludes(),
            )
            manga.extend([Manga(self._http, item) for item in data["data"]])

            offset += inner_limit
            if not data["data"] or offset >= 10_000 or limit is not None:
                break

        return MangaCollection(self._http, data, manga)

    @require_authentication
    async def get_all_manga_reading_status(
        self,
        *,
        status: ReadingStatus | None = None,
    ) -> manga.MangaMultipleReadingStatusResponse:
        """|coro|

        This method will return the current reading status of all manga in the logged-in user's library.

        Parameters
        ----------
        status: Optional[:class:`~hondana.ReadingStatus`]
            The reading status to filter the response with.

        Returns
        -------
        :class:`~hondana.types_.manga.MangaMultipleReadingStatusResponse`
            The payload returned from MangaDex.
        """
        return await self._http.get_all_manga_reading_status(status=status)

    @require_authentication
    async def get_manga_reading_status(self, manga_id: str, /) -> manga.MangaSingleReadingStatusResponse:
        """|coro|

        This method will return the current reading status for the specified manga.

        Parameters
        ----------
        manga_id: :class:`str`
            The UUID associated with the manga you wish to query.

        Raises
        ------
        Forbidden
            You are not authenticated to perform this action.
        NotFound
            The specified manga does not exist, likely due to an incorrect ID.

        Returns
        -------
        :class:`~hondana.types_.manga.MangaSingleReadingStatusResponse`
            The raw response from the API on the request.
        """  # noqa: DOC502 # raised in method call
        return await self._http.get_manga_reading_status(manga_id)

    @require_authentication
    async def update_manga_reading_status(self, manga_id: str, /, *, status: ReadingStatus) -> None:
        """|coro|

        This method will update your current reading status for the specified manga.

        Parameters
        ----------
        manga_id: :class:`str`
            The UUID associated with the manga you wish to update.
        status: Optional[:class:`~hondana.ReadingStatus`]
            The reading status you wish to update this manga with.


        .. note::
            Leaving ``status`` as the default will remove the manga reading status from the API.
            Please provide a value if you do not wish for this to happen.

        Raises
        ------
        BadRequest
            The query parameters were invalid.
        NotFound
            The specified manga cannot be found, likely due to incorrect ID.
        """  # noqa: DOC502 # raised in method call
        await self._http.update_manga_reading_status(manga_id, status=status)

    async def get_manga_draft(self, manga_id: str, /) -> Manga:
        """|coro|

        This method will return a manga draft from MangaDex.

        Parameters
        ----------
        manga_id: :class:`str`
            The ID relation to the manga draft.

        Returns
        -------
        :class:`~hondana.Manga`
            The Manga returned from the API.
        """
        data = await self._http.get_manga_draft(manga_id)
        return Manga(self._http, data["data"])

    @require_authentication
    async def submit_manga_draft(self, manga_id: str, /, *, version: int) -> Manga:
        """|coro|

        This method will submit a draft for a manga.

        Parameters
        ----------
        manga_id: :class:`str`
            The ID relating to the manga we are submitting to.
        version: :class:`int`
            The version of the manga we're attributing this submission to.

        Returns
        -------
        :class:`~hondana.Manga`

        Raises
        ------
        BadRequest
            The request parameters were incorrect or malformed.
        Forbidden
            You are not authorised to perform this action.
        NotFound
            The manga was not found.
        """  # noqa: DOC502 # raised in method call
        data = await self._http.submit_manga_draft(manga_id, version=version)
        return Manga(self._http, data["data"])

    @require_authentication
    async def get_manga_draft_list(
        self,
        *,
        limit: int = 10,
        offset: int = 0,
        state: MangaState | None = None,
        order: MangaDraftListOrderQuery | None = None,
        includes: MangaIncludes | None = None,
    ) -> Manga:
        """|coro|

        This method will return all drafts for a given manga.

        Parameters
        ----------
        limit: :class:`int`
            The limit of objects to return.
            Defaults to 10.
        offset: :class:`int`
            The pagination offset.
            Defaults to 0.
        state: Optional[:class:`~hondana.MangaState`]
            The state of the submission to filter by.
        order: Optional[:class:`~hondana.query.MangaDraftListOrderQuery`]
            The order parameter for order the responses.
        includes: Optional[:class:`~hondana.query.MangaIncludes`]
            The optional includes to request in the responses.

        Returns
        -------
        :class:`~hondana.Manga`
        """
        data = await self._http.get_manga_draft_list(
            limit=limit,
            offset=offset,
            state=state,
            order=order,
            includes=includes or MangaIncludes(),
        )
        return Manga(self._http, data["data"])

    async def get_manga_relation_list(
        self,
        manga_id: str,
        /,
        *,
        includes: MangaIncludes | None = None,
    ) -> MangaRelationCollection:
        """|coro|

        This method will return a list of all relations to a given manga.

        Parameters
        ----------
        manga_id: :class:`str`
            The ID for the manga we wish to query against.
        includes: Optional[:class:`~hondana.query.MangaIncludes`]
            The optional parameters for expanded requests to the API.
            Defaults to all possible expansions.

        Returns
        -------
        :class:`~hondana.MangaRelationCollection`

        Raises
        ------
        BadRequest
            The manga ID passed is malformed
        """  # noqa: DOC502 # raised in method call
        data = await self._http.get_manga_relation_list(manga_id, includes=includes or MangaIncludes())
        fmt = [MangaRelation(self._http, manga_id, item) for item in data["data"]]
        return MangaRelationCollection(self._http, data, fmt)

    @require_authentication
    async def create_manga_relation(
        self,
        manga_id: str,
        /,
        *,
        target_manga: str,
        relation_type: MangaRelationType,
    ) -> MangaRelation:
        """|coro|

        This method will create a manga relation.

        Parameters
        ----------
        manga_id: :class:`str`
            The manga ID we are creating a relation to.
        target_manga: :class:`str`
            The manga ID of the related manga.
        relation_type: :class:`~hondana.MangaRelationType`
            The relation type we are creating.

        Returns
        -------
        :class:`~hondana.MangaRelation`

        Raises
        ------
        BadRequest
            The parameters were malformed
        Forbidden
            You are not authorised for this action.
        """  # noqa: DOC502 # raised in method call
        data = await self._http.create_manga_relation(manga_id, target_manga=target_manga, relation_type=relation_type)
        return MangaRelation(self._http, manga_id, data["data"])

    @require_authentication
    async def delete_manga_relation(self, manga_id: str, relation_id: str, /) -> None:
        """|coro|

        This method will delete a manga relation.

        Parameters
        ----------
        manga_id: :class:`str`
            The ID of the source manga.
        relation_id: :class:`str`
            The ID of the related manga.
        """
        await self._http.delete_manga_relation(manga_id, relation_id)

    @require_authentication
    async def add_manga_to_custom_list(self, manga_id: str, /, *, custom_list_id: str) -> None:
        """|coro|

        This method will add the specified manga to the specified custom list.

        Parameters
        ----------
        manga_id: :class:`str`
            The UUID associated with the manga you wish to add to the custom list.
        custom_list_id: :class:`str`
            The UUID associated with the custom list you wish to add the manga to.

        Raises
        ------
        Forbidden
            You are not authorised to add manga to this custom list.
        NotFound
            The specified manga or specified custom list are not found, likely due to an incorrect UUID.
        """  # noqa: DOC502 # raised in method call
        await self._http.add_manga_to_custom_list(custom_list_id, manga_id=manga_id)

    @require_authentication
    async def remove_manga_from_custom_list(self, manga_id: str, /, *, custom_list_id: str) -> None:
        """|coro|

        This method will remove the specified manga from the specified custom list.

        Parameters
        ----------
        manga_id: :class:`str`
            The UUID associated with the manga you wish to remove from the specified custom list.
        custom_list_id: :class:`str`
            THe UUID associated with the custom list you wish to add the manga to.

        Raises
        ------
        Forbidden
            You are not authorised to remove a manga from the specified custom list.
        NotFound
            The specified manga or specified custom list are not found, likely due to an incorrect UUID.
        """  # noqa: DOC502 # raised in method call
        await self._http.remove_manga_from_custom_list(custom_list_id, manga_id=manga_id)

    async def chapter_list(
        self,
        *,
        limit: int | None = 100,
        offset: int = 0,
        ids: list[str] | None = None,
        title: str | None = None,
        groups: list[str] | None = None,
        uploader: str | list[str] | None = None,
        manga: str | None = None,
        volume: str | list[str] | None = None,
        chapter: str | list[str] | None = None,
        translated_language: list[common.LanguageCode] | None = None,
        original_language: list[common.LanguageCode] | None = None,
        excluded_original_language: list[common.LanguageCode] | None = None,
        content_rating: list[ContentRating] | None = None,
        excluded_groups: list[str] | None = None,
        excluded_uploaders: list[str] | None = None,
        include_future_updates: bool | None = None,
        include_empty_pages: bool | None = None,
        include_future_publish_at: bool | None = None,
        include_external_url: bool | None = None,
        include_unavailable: bool | None = None,
        created_at_since: datetime.datetime | None = None,
        updated_at_since: datetime.datetime | None = None,
        published_at_since: datetime.datetime | None = None,
        order: FeedOrderQuery | None = None,
        includes: ChapterIncludes | None = None,
    ) -> ChapterFeed:
        """|coro|

        This method will return a list of published chapters.

        Parameters
        ----------
        limit: Optional[:class:`int`]
            Defaults to 100. This specifies the amount of chapters to return in one request.
        offset: :class:`int`
            Defaults to 0. This specifies the pagination offset.
        ids: Optional[List[:class:`str`]]
            The list of chapter UUIDs to filter the request with.
        title: Optional[:class:`str`]
            The chapter title query to limit the request with.
        groups: Optional[List[:class:`str`]]
            The scanlation group UUID(s) to limit the request with.
        uploader: Optional[Union[:class:`str`, List[:class:`str`]]]
            The uploader UUID to limit the request with.
        manga: Optional[:class:`str`]
            The manga UUID to limit the request with.
        volume: Optional[Union[:class:`str`, List[:class:`str`]]]
            The volume UUID or UUIDs to limit the request with.
        chapter: Optional[Union[:class:`str`, List[:class:`str`]]]
            The chapter UUID or UUIDs to limit the request with.
        translated_language: Optional[List[:class:`~hondana.types_.common.LanguageCode`]]
            The list of languages codes to filter the request with.
        original_language: Optional[List[:class:`~hondana.types_.common.LanguageCode`]]
            The list of languages to specifically target in the request.
        excluded_original_language: Optional[List[:class:`~hondana.types_.common.LanguageCode`]]
            The list of original languages to exclude from the request.
        content_rating: Optional[List[:class:`~hondana.ContentRating`]]
            The content rating to filter the feed by.
        excluded_groups: Optional[List[:class:`str`]]
            The list of scanlator groups to exclude from the response.
        excluded_uploaders: Optional[List[:class:`str`]]
            The list of uploaders to exclude from the response.
        include_future_updates: Optional[:class:`bool`]
            Whether to include future chapters in this feed. Defaults to ``True`` API side.
        include_empty_pages: Optional[:class:`bool`]
            Whether to include chapters that have no recorded pages.
        include_future_publish_at: Optional[:class:`bool`]
            Whether to include chapters that have their publish time set to a time in the future.
        include_external_url: Optional[:class:`bool`]
            Whether to include chapters that have an external url set.
        include_unavailable: Optional[:class:`bool`]
            Whether to show chapters that are marked as unavailable.
        created_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their creation date.
        updated_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their updated at date.
        published_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their published at date.
        order: Optional[:class:`~hondana.query.FeedOrderQuery`]
            A query parameter to choose how the responses are ordered.
        includes: Optional[:class:`~hondana.query.ChapterIncludes`]
            The list of options to include increased payloads for per chapter.
            Defaults to all possible expansions.


        .. note::
            Passing ``None`` to ``limit`` will attempt to retrieve all items in the chapter feed.

        .. note::
            If `order` is not specified then the API will return results first based on their creation date,
            which could lead to unexpected results.

        Raises
        ------
        BadRequest
            The query parameters were malformed
        Forbidden
            The request returned an error due to authentication failure.

        Returns
        -------
        :class:`~hondana.ChapterFeed`
            Returns a collection of chapters.
        """  # noqa: DOC502 # raised in method call
        inner_limit = limit or 100

        chapters: list[Chapter] = []
        while True:
            data = await self._http.chapter_list(
                limit=inner_limit,
                offset=offset,
                ids=ids,
                title=title,
                groups=groups,
                uploader=uploader,
                manga=manga,
                volume=volume,
                chapter=chapter,
                translated_language=translated_language,
                original_language=original_language,
                excluded_original_language=excluded_original_language,
                content_rating=content_rating,
                excluded_groups=excluded_groups,
                excluded_uploaders=excluded_uploaders,
                include_future_updates=include_future_updates,
                include_empty_pages=include_empty_pages,
                include_future_publish_at=include_future_publish_at,
                include_external_url=include_external_url,
                include_unavailable=include_unavailable,
                created_at_since=created_at_since,
                updated_at_since=updated_at_since,
                published_at_since=published_at_since,
                order=order,
                includes=includes or ChapterIncludes(),
            )

            chapters.extend([Chapter(self._http, item) for item in data["data"]])

            offset += inner_limit
            if not data["data"] or offset >= 10_000 or limit is not None:
                break

        return ChapterFeed(self._http, data, chapters)

    async def get_chapter(
        self,
        chapter_id: str,
        /,
        *,
        includes: ChapterIncludes | None = None,
        fetch_full_manga: bool = False,
    ) -> Chapter:
        """|coro|

        This method will retrieve a single chapter from the MangaDex API.

        Parameters
        ----------
        chapter_id: :class:`str`
            The UUID representing the chapter we are fetching.
        includes: Optional[:class:`~hondana.query.ChapterIncludes`]
            The reference expansion includes we are requesting with this payload.
            Defaults to all possible expansions.
        fetch_full_manga: :class:`bool`
            This parameter will fetch the full manga object with the chapter if set to ``True``.
            Defaults to ``False``.


        .. note::
            ``fetch_full_manga`` when True will result in an extra API request to fetch the full manga data.

        Returns
        -------
        :class:`~hondana.Chapter`
            The Chapter we fetched from the API.
        """
        data = await self._http.get_chapter(chapter_id, includes=includes or ChapterIncludes())

        chapter = Chapter(self._http, data["data"])

        if fetch_full_manga:
            if chapter.manga_id is None:
                return chapter

            manga = await self.get_manga(chapter.manga_id)
            chapter.manga = manga
            return chapter

        return chapter

    @require_authentication
    async def update_chapter(
        self,
        chapter_id: str,
        /,
        *,
        title: str | None = None,
        volume: str = MISSING,
        chapter: str = MISSING,
        translated_language: str | None = None,
        groups: list[str] | None = None,
        version: int,
    ) -> Chapter:
        """|coro|

        This method will update a chapter in the MangaDex API.

        Parameters
        ----------
        chapter_id: :class:`str`
            The UUID representing the chapter we are going to update.
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
        ------
        BadRequest
            The request body was malformed.
        Forbidden
            You are not authorized to update this chapter.
        NotFound
            One or more UUIDs given were not found.

        Returns
        -------
        :class:`~hondana.Chapter`
            The chapter after being updated.
        """  # noqa: DOC502 # raised in method call
        data = await self._http.update_chapter(
            chapter_id,
            title=title,
            volume=volume,
            chapter=chapter,
            translated_language=translated_language,
            groups=groups,
            version=version,
        )

        return Chapter(self._http, data["data"])

    @require_authentication
    async def delete_chapter(self, chapter_id: str, /) -> None:
        """|coro|

        This method will delete a chapter from the MangaDex API.

        Parameters
        ----------
        chapter_id: :class:`str`
            The UUID of the chapter you wish to delete.

        Raises
        ------
        BadRequest
            The query was malformed.
        Forbidden
            You are not authorized to delete this chapter.
        NotFound
            The UUID passed for this chapter does not relate to a chapter in the API.
        """  # noqa: DOC502 # raised in method call
        await self._http.delete_chapter(chapter_id)

    @require_authentication
    async def my_chapter_read_history(self) -> ChapterReadHistoryCollection:
        """|coro|

        This method will return the last 30 chapters of read history for the currently logged in user.

        Raises
        ------
        Forbidden
            You are not authorized to access this endpoint.
        NotFound
            You do not have any read history.

        Returns
        -------
        :class:`~hondana.ChapterReadHistoryCollection`
            A rich type around the returned data.
        """  # noqa: DOC502 # raised in method call
        data = await self._http.user_read_history()

        history: list[PreviouslyReadChapter] = [
            PreviouslyReadChapter(self._http, (payload["chapterId"], payload["readDate"])) for payload in data["data"]
        ]
        return ChapterReadHistoryCollection(self._http, data, history)

    async def cover_art_list(
        self,
        *,
        limit: int | None = 10,
        offset: int = 0,
        manga: list[str] | None = None,
        ids: list[str] | None = None,
        uploaders: list[str] | None = None,
        locales: list[common.LanguageCode] | None = None,
        order: CoverArtListOrderQuery | None = None,
        includes: CoverIncludes | None = None,
    ) -> CoverCollection:
        """|coro|

        This method will fetch a list of cover arts from the MangaDex API.

        Parameters
        ----------
        limit: :class:`int`
            Defaults to 10. This specifies the amount of scanlator groups to return in one request.
        offset: :class:`int`
            Defaults to 0. The pagination offset.
        manga: Optional[List[:class:`str`]]
            A list of manga UUID(s) to limit the request to.
        ids: Optional[List[:class:`str`]]
            A list of cover art UUID(s) to limit the request to.
        uploaders: Optional[List[:class:`str`]]
            A list of uploader UUID(s) to limit the request to.
        locales: Optional[List[:class:`~hondana.types_.common.LanguageCode`]]
            The locales to filter this search by.
        order: Optional[:class:`~hondana.query.CoverArtListOrderQuery`]
            A query parameter to choose how the responses are ordered.
        includes: Optional[:class:`~hondana.query.CoverIncludes`]
            The optional includes to request increased payloads during the request.

        Raises
        ------
        BadRequest
            The request parameters were malformed.
        Forbidden
            The request returned an error due to authentication failure.

        Returns
        -------
        :class:`~hondana.CoverCollection`
            Returns a collection of covers.
        """  # noqa: DOC502 # raised in method call
        inner_limit = limit or 10

        covers: list[Cover] = []
        while True:
            data = await self._http.cover_art_list(
                limit=inner_limit,
                offset=offset,
                manga=manga,
                ids=ids,
                uploaders=uploaders,
                locales=locales,
                order=order,
                includes=includes or CoverIncludes(),
            )

            covers.extend([Cover(self._http, item) for item in data["data"]])

            offset += inner_limit
            if not data["data"] or offset >= 10_000 or limit is not None:
                break

        return CoverCollection(self._http, data, covers)

    @require_authentication
    async def upload_cover(
        self,
        manga_id: str,
        /,
        *,
        cover: bytes,
        volume: str | None = None,
        description: str,
        locale: common.LanguageCode | None = None,
    ) -> Cover:
        """|coro|

        This method will upload a cover to the MangaDex API.

        Parameters
        ----------
        manga_id: :class:`str`
            The ID relating to the manga this cover belongs to.
        cover: :class:`bytes`
            THe raw bytes of the image.
        volume: Optional[:class:`str`]
            The volume this cover relates to.
        description: :class:`str`
            The description of this cover.
        locale: Optional[:class:`~hondana.types_.common.LanguageCode`]
            The locale of this cover.

        Raises
        ------
        BadRequest
            The volume parameter was malformed or the file was a bad format.
        Forbidden
            You are not permitted for this action.

        Returns
        -------
        :class:`~hondana.Cover`
        """  # noqa: DOC502 # raised in method call
        data = await self._http.upload_cover(manga_id, cover=cover, volume=volume, description=description, locale=locale)

        return Cover(self._http, data["data"])

    async def get_cover(self, cover_id: str, /, *, includes: CoverIncludes | None = None) -> Cover:
        """|coro|

        The method will fetch a Cover from the MangaDex API.

        Parameters
        ----------
        cover_id: :class:`str`
            The id of the cover we are fetching from the API.
        includes: Optional[:class:`~hondana.query.CoverIncludes`]
            A list of the additional information to gather related to the Cover.


        .. note::
            If you do not include the ``"manga"`` includes, then we will not be able to get the cover url.

        Raises
        ------
        NotFound
            The passed cover ID was not found, likely due to an incorrect ID.

        Returns
        -------
        :class:`~hondana.Cover`
            The Cover returned from the API.
        """  # noqa: DOC502 # raised in method call
        data = await self._http.get_cover(cover_id, includes=includes or CoverIncludes())

        return Cover(self._http, data["data"])

    @require_authentication
    async def edit_cover(
        self,
        cover_id: str,
        /,
        *,
        volume: str = MISSING,
        description: str = MISSING,
        version: int,
    ) -> Cover:
        """|coro|

        This method will edit a cover on the MangaDex API.

        Parameters
        ----------
        cover_id: :class:`str`
            The UUID relating to the cover you wish to edit.
        volume: :class:`str`
            The volume identifier relating the cover will represent.
        description: Optional[:class:`str`]
            The description of the cover.
        version: :class:`int`
            The version revision of the cover.


        .. note::
            The ``volume`` key is mandatory. You can pass ``None`` to null it in the API, but it must have a value.

        Raises
        ------
        TypeError
            The volume key was not given a value. This is required.
        BadRequest
            The request body was malformed.
        Forbidden
            The request returned an error due to authentication failure.

        Returns
        -------
        :class:`~hondana.Cover`
            The returned cover after the edit.
        """  # noqa: DOC502 # raised in method call
        data = await self._http.edit_cover(cover_id, volume=volume, description=description, version=version)

        return Cover(self._http, data["data"])

    @require_authentication
    async def delete_cover(self, cover_id: str, /) -> None:
        """|coro|

        This method will delete a cover from the MangaDex API.

        Parameters
        ----------
        cover_id: :class:`str`
            The UUID relating to the cover you wish to delete.

        Raises
        ------
        BadRequest
            The request payload was malformed.
        Forbidden
            The request returned an error due to authentication.
        """  # noqa: DOC502 # raised in method call
        await self._http.delete_cover(cover_id)

    async def scanlation_group_list(
        self,
        *,
        limit: int | None = 10,
        offset: int = 0,
        ids: list[str] | None = None,
        name: str | None = None,
        focused_language: common.LanguageCode | None = None,
        order: ScanlatorGroupListOrderQuery | None = None,
        includes: ScanlatorGroupIncludes | None = None,
    ) -> ScanlatorGroupCollection:
        """|coro|

        This method will return a list of scanlator groups from the MangaDex API.

        Parameters
        ----------
        limit: Optional[:class:`int`]
            Defaults to 10. This specifies the amount of scanlator groups to return in one request.
        offset: :class:`int`
            Defaults to 0. The pagination offset.
        ids: Optional[List[:class:`str`]]
            A list of scanlator group UUID(s) to limit the request to.
        name: Optional[:class:`str`]
            A name to limit the request to.
        focused_language: Optional[:class:`~hondana.types_.common.LanguageCode`]
            A focused language to limit the request to.
        order: Optional[:class:`~hondana.query.ScanlatorGroupListOrderQuery`]
            An ordering statement for the request.
        includes: Optional[:class:`~hondana.query.ScanlatorGroupIncludes`]
            An optional list of includes to request increased payloads during the request.


        .. note::
            Passing ``None`` to ``limit`` will attempt to retrieve all items in the chapter feed.

        Raises
        ------
        BadRequest
            The query parameters were malformed
        Forbidden
            The request returned an error due to authentication failure.

        Returns
        -------
        :class:`ScanlatorGroupCollection`
            A returned collection of scanlation groups.
        """  # noqa: DOC502 # raised in method call
        inner_limit = limit or 10

        groups: list[ScanlatorGroup] = []
        while True:
            data = await self._http.scanlation_group_list(
                limit=inner_limit,
                offset=offset,
                ids=ids,
                name=name,
                focused_language=focused_language,
                order=order,
                includes=includes or ScanlatorGroupIncludes(),
            )

            groups.extend([ScanlatorGroup(self._http, item) for item in data["data"]])

            offset += inner_limit
            if not data["data"] or offset >= 10_000 or limit is not None:
                break

        return ScanlatorGroupCollection(self._http, data, groups)

    @require_authentication
    async def user_list(
        self,
        *,
        limit: int | None = 10,
        offset: int = 0,
        ids: list[str] | None = None,
        username: str | None = None,
        order: UserListOrderQuery | None = None,
    ) -> UserCollection:
        """|coro|

        This method will return a list of Users from the MangaDex API.

        Parameters
        ----------
        limit: Optional[:class:`int`]
            Defaults to 10. This specifies the amount of users to return in one request.
        offset: :class:`int`
            Defaults to 0. The pagination offset.
        ids: Optional[List[:class:`str`]]
            A list of User UUID(s) to limit the request to.
        username: Optional[:class:`str`]
            The username to limit this request to.
        order: Optional[:class:`~hondana.query.UserListOrderQuery`]
            The optional query param on how the response will be ordered.


        .. note::
            Passing ``None`` to ``limit`` will attempt to retrieve all items in the chapter feed.

        Raises
        ------
        BadRequest
            The request parameters were malformed
        Forbidden
            The request returned an error due to authentication failure.

        Returns
        -------
        :class:`UserCollection`
            A returned collection of users.
        """  # noqa: DOC502 # raised in method call
        inner_limit = limit or 10

        users: list[User] = []
        while True:
            data = await self._http.user_list(limit=inner_limit, offset=offset, ids=ids, username=username, order=order)
            users.extend([User(self._http, item) for item in data["data"]])

            offset += inner_limit
            if not data["data"] or offset >= 10_000 or limit is not None:
                break

        return UserCollection(self._http, data, users)

    async def get_user(self, user_id: str, /) -> User:
        """|coro|

        This method will fetch a user from the MangaDex API.

        Parameters
        ----------
        user_id: :class:`str`
            The UUID of the user you wish to fetch

        Returns
        -------
        :class:`User`
            The user returned from the API.
        """
        data = await self._http.get_user(user_id)

        return User(self._http, data["data"])

    @require_authentication
    async def delete_user(self, user_id: str, /) -> None:
        """|coro|

        This method will initiate the deletion of a user from the MangaDex API.

        Parameters
        ----------
        user_id: :class:`str`
            The UUID of the user you wish to delete.

        Raises
        ------
        Forbidden
            The response returned an error due to authentication failure.
        NotFound
            The user specified cannot be found.
        """  # noqa: DOC502 # raised in method call
        await self._http.delete_user(user_id)

    async def approve_user_deletion(self, approval_code: str, /) -> None:
        """|coro|

        This method will approve a user deletion in the MangaDex API.

        Parameters
        ----------
        approval_code: :class:`str`
            The UUID representing the approval code to delete the user.
        """
        await self._http.approve_user_deletion(approval_code)

    @require_authentication
    async def update_user_password(self, *, old_password: str, new_password: str) -> None:
        """|coro|

        This method will change the current authenticated user's password.

        Parameters
        ----------
        old_password: :class:`str`
            The current (old) password we will be changing from.
        new_password: :class:`str`
            The new password we will be changing to.

        Raises
        ------
        Forbidden
            The request returned an error due to an authentication issue.
        """  # noqa: DOC502 # raised in method call
        await self._http.update_user_password(old_password=old_password, new_password=new_password)

    @require_authentication
    async def update_user_email(self, email: str, /) -> None:
        """|coro|

        This method will update the current authenticated user's email.

        Parameters
        ----------
        email: :class:`str`
            The new email address to change to.

        Raises
        ------
        Forbidden
            The API returned an error due to authentication failure.
        """  # noqa: DOC502 # raised in method call
        await self._http.update_user_email(email)

    @require_authentication
    async def get_my_details(self) -> User:
        """|coro|

        This method will return the current authenticated user's details.

        Raises
        ------
        Forbidden
            The request returned an error due to authentication failure.

        Returns
        -------
        :class:`~hondana.User`
            Your current user details returned from the API.
        """  # noqa: DOC502 # raised in method call
        data = await self._http.get_my_details()

        return User(self._http, data["data"])

    @require_authentication
    async def get_my_followed_groups(self, limit: int = 10, offset: int = 0) -> list[ScanlatorGroup]:
        """|coro|

        This method will return a list of scanlation groups the current authenticated user follows.

        Parameters
        ----------
        limit: :class:`int`
            Defaults to 10. The amount of groups to return in one request.
        offset: :class:`int`
            Defaults to 0. The pagination offset.

        Raises
        ------
        Forbidden
            The request returned an error due to authentication failure.

        Returns
        -------
        List[:class:`ScanlatorGroup`]
            The list of groups that are being followed.
        """  # noqa: DOC502 # raised in method call
        data = await self._http.get_my_followed_groups(limit=limit, offset=offset)

        return [ScanlatorGroup(self._http, item) for item in data["data"]]

    @require_authentication
    async def check_if_following_group(self, group_id: str, /) -> bool:
        """|coro|

        This method will check if the current authenticated user is following a scanlation group.

        Parameters
        ----------
        group_id: :class:`str`
            The UUID representing the scanlation group you wish to check.

        Returns
        -------
        :class:`bool`
            Whether the passed scanlation group is followed or not.
        """
        try:
            await self._http.is_group_followed(group_id)
        except errors.NotFound:
            return False
        return True

    @require_authentication
    async def check_if_following_manga(self, manga_id: str, /) -> bool:
        """|coro|

        This method will check if the currently logged in user is following the supplied Manga.

        Parameters
        ----------
        manga_id: :class:`str`
            The manga to check if we're following.

        Returns
        -------
        :class:`bool`
        """
        try:
            await self._http.is_manga_followed(manga_id)
        except errors.NotFound:
            return False
        return True

    @require_authentication
    async def get_my_followed_users(self, *, limit: int | None = 10, offset: int = 0) -> UserCollection:
        """|coro|

        This method will return the current authenticated user's followed users.

        Parameters
        ----------
        limit: Optional[:class:`int`]
            Defaults to 10. The amount of users to return in one request.
        offset: :class:`int`
            Defaults to 0. The pagination offset.


        .. note::
            Passing ``None`` to ``limit`` will attempt to retrieve all items in the chapter feed.

        Raises
        ------
        Forbidden
            The request returned an error due to authentication failure.

        Returns
        -------
        :class:`~hondana.UserCollection`
            A returned collection of users.
        """  # noqa: DOC502 # raised in method call
        inner_limit = limit or 10

        users: list[User] = []
        while True:
            data = await self._http.get_my_followed_users(limit=inner_limit, offset=offset)
            users.extend([User(self._http, item) for item in data["data"]])

            offset += inner_limit
            if not data["data"] or offset >= 10_000 or limit is not None:
                break

        return UserCollection(self._http, data, users)

    @require_authentication
    async def check_if_following_user(self, user_id: str, /) -> bool:
        """|coro|

        This method will check if the current authenticated user is following the specified user.

        Parameters
        ----------
        user_id: :class:`str`
            The UUID relating to the user you wish to query against.

        Raises
        ------
        Forbidden
            The requested returned an error due to authentication failure.

        Returns
        -------
        :class:`bool`
            Whether the target user is followed or not.
        """  # noqa: DOC502 # raised in method call
        try:
            await self._http.is_user_followed(user_id)
        except errors.NotFound:
            return False
        else:
            return True

    @require_authentication
    async def get_my_custom_list_follows(self, limit: int = 10, offset: int = 0) -> list[CustomList]:
        """|coro|

        This method will return the current authenticated user's custom list follows.

        Returns
        -------
        list[:class:`CustomList`]
            The list of custom lists you follow.
        """
        data = await self._http.get_user_custom_list_follows(limit=limit, offset=offset)

        return [CustomList(self._http, item) for item in data["data"]]

    @require_authentication
    async def check_if_following_custom_list(self, custom_list_id: str, /) -> bool:
        """|coro|

        This method will check if the current authenticated user is following the specified custom list.

        Returns
        -------
        :class:`bool`
            Whether you follow this custom list or not.
        """
        try:
            await self._http.is_custom_list_followed(custom_list_id)
        except errors.NotFound:
            return False
        else:
            return True

    async def create_account(self, *, username: str, password: str, email: str) -> User:
        """|coro|

        This method will create an account with the passed parameters within the MangaDex API.

        Parameters
        ----------
        username: :class:`str`
            The username you wish to use in the new account.
        password: :class:`str`
            The password to use in the new account.
        email: :class:`str`
            The email address to use in the new account.


        .. note::
            The created account will still need to be activated.

        Raises
        ------
        BadRequest
            The parameters passed were malformed.

        Returns
        -------
        :class:`User`
            The created user.
        """  # noqa: DOC502 # raised in method call
        data = await self._http.create_account(username=username, password=password, email=email)
        return User(self._http, data["data"])

    async def activate_account(self, activation_code: str, /) -> None:
        """|coro|

        This method will activate an account on the MangaDex API.

        Parameters
        ----------
        activation_code: :class:`str`
            The activation code for the account.

        Raises
        ------
        BadRequest
            The query was malformed.
        NotFound
            The activation code passed was not a valid one.
        """  # noqa: DOC502 # raised in method call
        await self._http.activate_account(activation_code)

    async def resend_activation_code(self, email: str, /) -> None:
        """|coro|

        This method will resend an activation code to the specified email.

        Parameters
        ----------
        email: :class:`str`
            The email to resend the activation code to.

        Raises
        ------
        BadRequest
            The email passed is not pending activation.
        """  # noqa: DOC502 # raised in method call
        await self._http.resend_activation_code(email)

    async def recover_account(self, email: str, /) -> None:
        """|coro|

        This method will start an account recovery process on the given account.
        Effectively triggering the "forgotten password" email to be sent.

        Parameters
        ----------
        email: :class:`str`
            The email address belonging to the account you wish to recover.

        Raises
        ------
        BadRequest
            The email does not belong to a matching account.
        """  # noqa: DOC502 # raised in method call
        await self._http.recover_account(email)

    async def complete_account_recovery(self, recovery_code: str, /, *, new_password: str) -> None:
        """|coro|

        This method will complete an account recovery process.

        Parameters
        ----------
        recovery_code: :class:`str`
            The recovery code given during the recovery process.
        new_password: :class:`str`
            The new password to use for the recovered account.

        Raises
        ------
        BadRequest
            The recovery code given was not found or the password was greater than 1024 characters.
        """  # noqa: DOC502 # raised in method call
        await self._http.complete_account_recovery(recovery_code, new_password=new_password)

    async def ping_the_server(self) -> bool:
        """|coro|

        This method will return a simple 'pong' response from the API.
        Mainly a small endpoint to check the API is alive and responding.

        Returns
        -------
        :class:`bool`
            Whether and 'pong' response was received.
        """
        data = await self._http.ping_the_server()
        return data == "pong"

    async def legacy_id_mapping(
        self,
        mapping_type: legacy.LegacyMappingType,
        /,
        *,
        item_ids: list[int],
    ) -> LegacyMappingCollection:
        """|coro|

        This method will return a small response from the API to retrieve a legacy MangaDex's new details.

        Parameters
        ----------
        mapping_type: :class:`~hondana.types_.legacy.LegacyMappingType`
            The type of the object we are querying.
        item_ids: List[:class:`int`]
            The legacy integer IDs of MangaDex items.

        Raises
        ------
        BadRequest
            The query was malformed.

        Returns
        -------
        :class:`LegacyMappingCollection`
            The list of returned items from this query.
        """  # noqa: DOC502 # raised in method call
        data = await self._http.legacy_id_mapping(mapping_type, item_ids=item_ids)
        items = [LegacyItem(self._http, item) for item in data["data"]]
        return LegacyMappingCollection(self._http, data, items)

    async def get_at_home_url(self, chapter_id: str, /, *, ssl: bool = True) -> str:
        """|coro|

        This method will retrieve a MangaDex@Home URL for accessing a chapter.

        Parameters
        ----------
        chapter_id: :class:`str`
            The UUID of the chapter we are retrieving a URL for.
        ssl: :class:`bool`
            Defaults to ``True``. Whether to require the MangaDex @ Home node be available on port 443.
            If ``False`` is selected, then the MD@H node we request may be available on a non-standard port.

        Raises
        ------
        NotFound
            The specified chapter ID was not found.

        Returns
        -------
        :class:`str`
            Returns the URL we requested.
        """  # noqa: DOC502 # raised in method call
        data = await self._http.get_at_home_url(chapter_id, ssl=ssl)
        return data["baseUrl"]

    @require_authentication
    async def create_custom_list(
        self,
        *,
        name: str,
        visibility: CustomListVisibility | None = None,
        manga: list[str] | None = None,
    ) -> CustomList:
        """|coro|

        This method will create a custom list within the MangaDex API.

        Parameters
        ----------
        name: :class:`str`
            The name of this custom list.
        visibility: Optional[:class:`~hondana.CustomListVisibility`]
            The visibility of this custom list.
        manga: Optional[List[:class:`str`]]
            A list of manga IDs to add to this custom list.

        Raises
        ------
        BadRequest
            The payload was malformed.
        NotFound
            One of the passed Manga IDs was not found.

        Returns
        -------
        :class:`~hondana.CustomList`
            The custom list that was created.
        """  # noqa: DOC502 # raised in method call
        data = await self._http.create_custom_list(name=name, visibility=visibility, manga=manga)

        return CustomList(self._http, data["data"])

    async def get_custom_list(
        self,
        custom_list_id: str,
        /,
        *,
        includes: CustomListIncludes | None = None,
    ) -> CustomList:
        """|coro|

        This method will retrieve a custom list from the MangaDex API.

        Parameters
        ----------
        custom_list_id: :class:`str`
            The UUID associated with the custom list we wish to retrieve.
        includes: Optional[:class:`~hondana.query.CustomListIncludes`]
            The list of additional data to request in the payload.

        Raises
        ------
        NotFound
            The custom list with this ID was not found.

        Returns
        -------
        :class:`~hondana.CustomList`
            The retrieved custom list.
        """  # noqa: DOC502 # raised in method call
        data = await self._http.get_custom_list(custom_list_id, includes=includes or CustomListIncludes())

        return CustomList(self._http, data["data"])

    @require_authentication
    async def update_custom_list(
        self,
        custom_list_id: str,
        /,
        *,
        name: str | None = None,
        visibility: CustomListVisibility | None = None,
        manga: list[str] | None = None,
        version: int,
    ) -> CustomList:
        """|coro|

        This method will update a custom list within the MangaDex API.

        Parameters
        ----------
        custom_list_id: :class:`str`
            The custom list ID we wish to update.
        name: Optional[:class:`str`]
            The name we wish to edit the custom list with.
        visibility: Optional[:class:`~hondana.CustomListVisibility`]
            The visibility we wish to edit the custom list with.
        manga: Optional[List[:class:`str`]]
            The list of manga IDs to edit this custom list with.
        version: :class:`int`
            The version revision of this custom list.


        .. note::
            Updating a custom list is an atomic action.
            Passing the ``manga`` key here will overwrite the manga in this custom list.

        Raises
        ------
        BadRequest
            The request body was malformed.
        Forbidden
            You are not authorized to edit this custom list.
        NotFound
            The custom list was not found, or one of the manga passed was not found.

        Returns
        -------
        :class:`~hondana.CustomList`
            The returned custom list after it was updated.
        """  # noqa: DOC502 # raised in method call
        data = await self._http.update_custom_list(
            custom_list_id,
            name=name,
            visibility=visibility,
            manga=manga,
            version=version,
        )

        return CustomList(self._http, data["data"])

    @require_authentication
    async def delete_custom_list(self, custom_list_id: str, /) -> None:
        """|coro|

        This method will delete a custom list from the MangaDex API.

        Parameters
        ----------
        custom_list_id: :class:`str`
            The UUID relating to the custom list we wish to delete.

        Raises
        ------
        Forbidden
            You are not authorized to delete this custom list.
        NotFound
            The custom list with this UUID was not found.
        """  # noqa: DOC502 # raised in method call
        await self._http.delete_custom_list(custom_list_id)

    @require_authentication
    @deprecated("bookmark_custom_list")
    async def follow_custom_list(self, custom_list_id: str, /) -> None:
        """|coro|

        This method will follow a custom list within the MangaDex API.

        Parameters
        ----------
        custom_list_id: :class:`str`
            The UUID relating to the custom list we wish to follow.

        Raises
        ------
        BadRequest
            The request was malformed.
        Forbidden
            You are not authorized to follow this custom list.
        NotFound
            The specified custom list does not exist.
        """  # noqa: DOC502 # raised in method call
        await self._http.follow_custom_list(custom_list_id)

    bookmark_custom_list = follow_custom_list

    @require_authentication
    @deprecated("unbookmark_custom_list")
    async def unfollow_custom_list(self, custom_list_id: str, /) -> None:
        """|coro|

        The method will unbookmark a custom list within the MangaDex API.

        Parameters
        ----------
        custom_list_id: :class:`str`
            The UUID relating to the custom list we wish to unbookmark.

        Raises
        ------
        Forbidden
            You are not authorized to unbookmark this custom list.
        NotFound
            The specified custom list does not exist.
        """  # noqa: DOC502 # raised in method call
        await self._http.unfollow_custom_list(custom_list_id)

    unbookmark_custom_list = unfollow_custom_list

    @require_authentication
    async def get_my_custom_lists(self, *, limit: int | None = 10, offset: int = 0) -> CustomListCollection:
        """|coro|

        This method will get the current authenticated user's custom list.

        Parameters
        ----------
        limit: Optional[:class:`int`]
            Defaults to 10. The amount of custom lists to return in one request.
        offset: :class:`int`
            Defaults to 0. The pagination offset.


        .. note::
            Passing ``None`` to ``limit`` will attempt to retrieve all items in the chapter feed.

        Raises
        ------
        Forbidden
            The request returned an error due to authentication failure.

        Returns
        -------
        :class:`~hondana.CustomListCollection`
            A returned collection of custom lists.
        """  # noqa: DOC502 # raised in method call
        inner_limit = limit or 10

        lists: list[CustomList] = []
        while True:
            data = await self._http.get_my_custom_lists(limit=inner_limit, offset=offset)
            lists.extend([CustomList(self._http, item) for item in data["data"]])

            offset += inner_limit
            if not data["data"] or offset >= 10_000 or limit is not None:
                break

        return CustomListCollection(self._http, data, lists)

    @require_authentication
    async def get_users_custom_lists(
        self,
        user_id: str,
        /,
        *,
        limit: int | None = 10,
        offset: int = 0,
    ) -> CustomListCollection:
        """|coro|

        This method will retrieve another user's custom lists.

        Parameters
        ----------
        user_id: :class:`str`
            The UUID of the user whose lists we wish to retrieve.
        limit: Optional[:class:`int`]
            Defaults to 10. The amount of custom lists to return in one request.
        offset: :class:`int`
            Defaults to 0. The pagination offset.


        .. note::
            Passing ``None`` to ``limit`` will attempt to retrieve all items in the chapter feed.

        Raises
        ------
        Forbidden
            The request returned an error due to authentication failure.

        Returns
        -------
        :class:`~hondana.CustomListCollection`
            A returned collection of custom lists.
        """  # noqa: DOC502 # raised in method call
        inner_limit = limit or 10

        lists: list[CustomList] = []
        while True:
            data = await self._http.get_users_custom_lists(user_id, limit=inner_limit, offset=offset)
            lists.extend([CustomList(self._http, item) for item in data["data"]])

            offset += inner_limit
            if not data["data"] or offset >= 10_000 or limit is not None:
                break

        return CustomListCollection(self._http, data, lists)

    @require_authentication
    async def get_custom_list_manga_feed(
        self,
        custom_list_id: str,
        /,
        *,
        limit: int | None = 100,
        offset: int = 0,
        translated_language: list[common.LanguageCode] | None = None,
        original_language: list[common.LanguageCode] | None = None,
        excluded_original_language: list[common.LanguageCode] | None = None,
        content_rating: list[ContentRating] | None = None,
        excluded_groups: list[str] | None = None,
        excluded_uploaders: list[str] | None = None,
        include_future_updates: bool | None = None,
        created_at_since: datetime.datetime | None = None,
        updated_at_since: datetime.datetime | None = None,
        published_at_since: datetime.datetime | None = None,
        order: FeedOrderQuery | None = None,
        includes: ChapterIncludes | None = None,
        include_empty_pages: bool | None = None,
        include_future_publish_at: bool | None = None,
        include_external_url: bool | None = None,
    ) -> ChapterFeed:
        """|coro|

        This method returns the specified manga's chapter feed.

        Parameters
        ----------
        custom_list_id: :class:`str`
            The UUID of the custom list whose feed we are requesting.
        limit: Optional[:class:`int`]
            Defaults to 100. The maximum amount of chapters to return in the response.
        offset: :class:`int`
            Defaults to 0. The pagination offset for the request.
        translated_language: List[:class:`~hondana.types_.common.LanguageCode`]
            A list of language codes to filter the returned chapters with.
        original_language: List[:class:`~hondana.types_.common.LanguageCode`]
            A list of language codes to filter the original language of the returned chapters with.
        excluded_original_language: List[:class:`~hondana.types_.common.LanguageCode`]
            A list of language codes to negate filter the original language of the returned chapters with.
        content_rating: Optional[List[:class:`~hondana.ContentRating`]]
            The content rating to filter this query with.
        excluded_groups: Optional[List[:class:`str`]]
            The list of scanlator groups to exclude from the response.
        excluded_uploaders: Optional[List[:class:`str`]]
            The list of uploaders to exclude from the response.
        include_future_updates: Optional[:class:`bool`]
            Whether to include future chapters in this feed. Defaults to ``True`` API side.
        created_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their creation date.
        updated_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their updated at date.
        published_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their published at date.
        order: Optional[:class:`~hondana.query.FeedOrderQuery`]
            A query parameter to choose how the responses are ordered.
            i.e. ``{"chapters": "desc"}``
        includes: Optional[:class:`~hondana.query.ChapterIncludes`]
            The list of optional includes we request the data for.
            Defaults to all possible expansions.
        include_empty_pages: Optional[:class:`bool`]
            Whether to show chapters with no pages available.
        include_future_publish_at: Optional[:class:`bool`]
            Whether to show chapters with a publishAt value set in the future.
        includeExternalUrl: Optional[:class:`bool`]
            Whether to show chapters that have an external URL attached to them.

        Raises
        ------
        BadRequest
            The query parameters were malformed.
        Unauthorized
            The request was performed with no authorization.
        Forbidden
            You are not authorized to request this feed.
        NotFound
            The specified custom list was not found.

        Returns
        -------
        :class:`~hondana.ChapterFeed`
            Returns a collections of chapters.
        """  # noqa: DOC502 # raised in method call
        inner_limit = limit or 100

        chapters: list[Chapter] = []
        while True:
            data = await self._http.custom_list_manga_feed(
                custom_list_id,
                limit=inner_limit,
                offset=offset,
                translated_language=translated_language,
                original_language=original_language,
                excluded_original_language=excluded_original_language,
                content_rating=content_rating,
                excluded_groups=excluded_groups,
                excluded_uploaders=excluded_uploaders,
                include_future_updates=include_future_updates,
                created_at_since=created_at_since,
                updated_at_since=updated_at_since,
                published_at_since=published_at_since,
                order=order,
                includes=includes or ChapterIncludes(),
                include_empty_pages=include_empty_pages,
                include_future_publish_at=include_future_publish_at,
                include_external_url=include_external_url,
            )

            chapters.extend([Chapter(self._http, item) for item in data["data"]])

            offset += inner_limit
            if not data["data"] or offset >= 10_000 or limit is not None:
                break

        return ChapterFeed(self._http, data, chapters)

    @require_authentication
    async def create_scanlation_group(
        self,
        *,
        name: str,
        website: str | None = None,
        irc_server: str | None = None,
        irc_channel: str | None = None,
        discord: str | None = None,
        contact_email: str | None = None,
        description: str | None = None,
        twitter: str | None = None,
        manga_updates: str | None = None,
        inactive: bool | None = None,
        publish_delay: str | datetime.timedelta | None = None,
    ) -> ScanlatorGroup:
        """|coro|

        This method will create a scanlation group within the MangaDex API.

        Parameters
        ----------
        name: :class:`str`
            The name of the scanlation group.
        website: Optional[:class:`str`]
            The scanlation group's website, if any.
        irc_server: Optional[:class:`str`]
            The scanlation group's irc server, if any.
        irc_channel: Optional[:class:`str`]
            The scanlation group's irc channel, if any.
        discord: Optional[:class:`str`]
            The scanlation group's discord server, if any.
        contact_email: Optional[:class:`str`]
            The scanlation group's email, if any.
        description: Optional[:class:`str`]
            The scanlation group's description, if any.
        twitter: Optional[:class:`str`]
            The scanlation group's twitter url, if any.
        manga_updates: Optional[:class:`str`]
            The group's page where they post manga updates, if any.
        inactive: Optional[:class:`bool`]
            If the scanlation group is inactive or not.
        publish_delay: Optional[Union[:class:`str`, :class:`datetime.timedelta`]]
            If the scanlation group's releases are published on a delay.


        .. note::
            The ``publish_delay`` parameter must match the :class:`hondana.utils.MANGADEX_TIME_REGEX` pattern
            or be a valid ``datetime.timedelta``.


        Raises
        ------
        BadRequest
            The request body was malformed.
        Forbidden
            You are not authorized to create scanlation groups.

        Returns
        -------
        :class:`~hondana.ScanlatorGroup`
            The group returned from the API on creation.
        """  # noqa: DOC502 # raised in method call
        data = await self._http.create_scanlation_group(
            name=name,
            website=website,
            irc_server=irc_server,
            irc_channel=irc_channel,
            discord=discord,
            contact_email=contact_email,
            description=description,
            twitter=twitter,
            manga_updates=manga_updates,
            inactive=inactive,
            publish_delay=publish_delay,
        )
        return ScanlatorGroup(self._http, data["data"])

    async def get_scanlation_group(
        self,
        scanlation_group_id: str,
        /,
        *,
        includes: ScanlatorGroupIncludes | None = None,
    ) -> ScanlatorGroup:
        """|coro|

        This method will get a scanlation group from the MangaDex API.

        Parameters
        ----------
        scanlation_group_id: :class:`str`
            The UUID relating to the scanlation group you wish to fetch.
        includes: Optional[:class:`~hondana.query.ScanlatorGroupIncludes`]
            The list of optional includes we request the data for.
            Defaults to all possible expansions

        Raises
        ------
        Forbidden
            You are not authorized to view this scanlation group.
        NotFound
            The scanlation group was not found.

        Returns
        -------
        :class:`~hondana.ScanlatorGroup`
            The group returned from the API.
        """  # noqa: DOC502 # raised in method call
        data = await self._http.view_scanlation_group(scanlation_group_id, includes=includes or ScanlatorGroupIncludes())
        return ScanlatorGroup(self._http, data["data"])

    @require_authentication
    async def update_scanlation_group(
        self,
        scanlation_group_id: str,
        /,
        *,
        name: str | None = None,
        leader: str | None = None,
        members: list[str] | None = None,
        website: str | None = MISSING,
        irc_server: str | None = MISSING,
        irc_channel: str | None = MISSING,
        discord: str | None = MISSING,
        contact_email: str | None = MISSING,
        description: str | None = MISSING,
        twitter: str | None = MISSING,
        manga_updates: str | None = MISSING,
        focused_languages: list[common.LanguageCode] = MISSING,
        inactive: bool | None = None,
        locked: bool | None = None,
        publish_delay: str | datetime.timedelta | None = None,
        version: int,
    ) -> ScanlatorGroup:
        """|coro|

        This method will update a scanlation group within the MangaDex API.

        Parameters
        ----------
        scanlation_group_id: :class:`str`
            The UUID relating to the scanlation group we are updating.
        name: Optional[:class:`str`]
            The name to update the group with.
        leader: Optional[:class:`str`]
            The UUID of the leader to update the group with.
        members: Optional[:class:`str`]
            A list of UUIDs relating to the members to update the group with.
        website: Optional[:class:`str`]
            The website to update the group with.
        irc_server: Optional[:class:`str`]
            The IRC Server to update the group with.
        irc_channel: Optional[:class:`str`]
            The IRC Channel to update the group with.
        discord: Optional[:class:`str`]
            The discord server to update the group with.
        contact_email: Optional[:class:`str`]
            The contact email to update the group with.
        description: Optional[:class:`str`]
            The new description to update the group with.
        twitter: Optional[:class:`str`]
            The new twitter url to update the group with.
        manga_updates: Optional[:class:`str`]
            The URL to the group's page where they post updates, if any.
        focused_languages: Optional[List[:class:`~hondana.types_.common.LanguageCode`]]
            The new list of language codes to update the group with.
        inactive: Optional[:class:`bool`]
            If the group is inactive or not.
        locked: Optional[:class:`bool`]
            Update the lock status of this scanlator group.
        publish_delay: Optional[Union[:class:`str`, :class:`datetime.timedelta`]]
            The publishing delay to add to all group releases.
        version: :class:`int`
            The version revision of this scanlator group.


        .. note::
            The ``website``, ``irc_server``, ``irc_channel``, ``discord``, ``contact_email``, ``description``,
            ``twitter``, ``manga_updates`` and ``focused_language``
            keys are all nullable in the API. To do so please pass ``None`` explicitly to these keys.

        .. note::
            The ``publish_delay`` parameter must match the :class:`hondana.utils.MANGADEX_TIME_REGEX` pattern
            or be a valid ``datetime.timedelta``.

        Raises
        ------
        BadRequest
            The request body was malformed
        Forbidden
            You are not authorized to update this scanlation group.
        NotFound
            The passed scanlation group ID cannot be found.

        Returns
        -------
        :class:`ScanlatorGroup`
            The group returned from the API after its update.
        """  # noqa: DOC502 # raised in method call
        data = await self._http.update_scanlation_group(
            scanlation_group_id,
            name=name,
            leader=leader,
            members=members,
            website=website,
            irc_server=irc_server,
            irc_channel=irc_channel,
            discord=discord,
            contact_email=contact_email,
            description=description,
            twitter=twitter,
            manga_updates=manga_updates,
            focused_languages=focused_languages,
            inactive=inactive,
            locked=locked,
            publish_delay=publish_delay,
            version=version,
        )

        return ScanlatorGroup(self._http, data["data"])

    @require_authentication
    async def delete_scanlation_group(self, scanlation_group_id: str, /) -> None:
        """|coro|

        This method will delete a scanlation group.

        Parameters
        ----------
        scanlation_group_id: :class:`str`
            The UUID relating to the scanlation group you wish to delete.

        Raises
        ------
        Forbidden
            You are not authorized to delete this scanlation group.
        NotFound
            The scanlation group cannot be found, likely due to an incorrect ID.
        """  # noqa: DOC502 # raised in method call
        await self._http.delete_scanlation_group(scanlation_group_id)

    @require_authentication
    @deprecated("bookmark_scanlation_group")
    async def follow_scanlation_group(self, scanlation_group_id: str, /) -> None:
        """|coro|

        This method will delete a scanlation group.

        Parameters
        ----------
        scanlation_group_id: :class:`str`
            The UUID relating to the scanlation group you wish to follow.

        Raises
        ------
        NotFound
            The scanlation group cannot be found, likely due to an incorrect ID.
        """  # noqa: DOC502 # raised in method call
        await self._http.follow_scanlation_group(scanlation_group_id)

    bookmark_scanlation_group = follow_scanlation_group

    @require_authentication
    @deprecated("unbookmark_scanlation_group")
    async def unfollow_scanlation_group(self, scanlation_group_id: str, /) -> None:
        """|coro|

        This method will delete a scanlation group.

        Parameters
        ----------
        scanlation_group_id: :class:`str`
            The UUID relating to the scanlation group you wish to unfollow.

        Raises
        ------
        NotFound
            The scanlation group cannot be found, likely due to an incorrect ID.
        """  # noqa: DOC502 # raised in method call
        await self._http.unfollow_scanlation_group(scanlation_group_id)

    unbookmark_scanlation_group = unfollow_scanlation_group

    async def author_list(
        self,
        *,
        limit: int | None = 10,
        offset: int = 0,
        ids: list[str] | None = None,
        name: str | None = None,
        order: AuthorListOrderQuery | None = None,
        includes: AuthorIncludes | None = None,
    ) -> AuthorCollection:
        """|coro|

        This method will fetch a list of authors from the MangaDex API.

        Parameters
        ----------
        limit: Optional[:class:`int`]
            Defaults to 10. This specifies the amount of scanlator groups to return in one request.
        offset: :class:`int`
            Defaults to 0. The pagination offset.
        ids: Optional[List[:class:`str`]]
            A list of author UUID(s) to limit the request to.
        name: Optional[:class:`str`]
            A name to limit the request to.
        order: Optional[:class:`~hondana.query.AuthorListOrderQuery`]
            A query parameter to choose how the responses are ordered.
        includes: Optional[:class:`~hondana.query.AuthorIncludes`]
            An optional list of includes to request increased payloads during the request.
            Defaults to all possible expansions.


        .. note::
            Passing ``None`` to ``limit`` will attempt to retrieve all items in the author collection.

        Raises
        ------
        BadRequest
            The request payload was malformed.
        Forbidden
            The request failed due to authentication failure.

        Returns
        -------
        :class:`~hondana.AuthorCollection`
            A returned collection of authors.
        """  # noqa: DOC502 # raised in method call
        inner_limit = limit or 10

        authors: list[Author] = []
        while True:
            data = await self._http.author_list(
                limit=inner_limit,
                offset=offset,
                ids=ids,
                name=name,
                order=order,
                includes=includes or AuthorIncludes(),
            )

            authors.extend([Author(self._http, item) for item in data["data"]])

            offset += inner_limit
            if not data["data"] or offset >= 10_000 or limit is not None:
                break

        return AuthorCollection(self._http, data, authors)

    @require_authentication
    async def create_author(
        self,
        *,
        name: str,
        biography: common.LocalizedString | None = None,
        twitter: str = MISSING,
        pixiv: str = MISSING,
        melon_book: str = MISSING,
        fan_box: str = MISSING,
        booth: str = MISSING,
        nico_video: str = MISSING,
        skeb: str = MISSING,
        fantia: str = MISSING,
        tumblr: str = MISSING,
        youtube: str = MISSING,
        website: str = MISSING,
    ) -> Author:
        """|coro|

        This method will create an author within the MangaDex API.

        Parameters
        ----------
        name: :class:`str`
            The name of the author we are creating.
        biography: Optional[:class:`~hondana.types_.common.LocalizedString`]
            The biography of the author we are creating.
        twitter: Optional[:class:`str`]
            The twitter URL of the author.
        pixiv: Optional[:class:`str`]
            The pixiv URL of the author.
        melon_book: Optional[:class:`str`]
            The melon book URL of the author.
        fan_box: Optional[:class:`str`]
            The fan box URL of the author.
        booth: Optional[:class:`str`]
            The booth URL of the author.
        nico_video: Optional[:class:`str`]
            The nico video URL of the author.
        skeb: Optional[:class:`str`]
            The skeb URL of the author.
        fantia: Optional[:class:`str`]
            The fantia URL of the author.
        tumblr: Optional[:class:`str`]
            The tumblr URL of the author.
        youtube: Optional[:class:`str`]
            The youtube  URL of the author.
        website: Optional[:class:`str`]
            The website URL of the author.

        Raises
        ------
        BadRequest
            The request body was malformed.
        Forbidden
            You are not authorized to create authors.

        Returns
        -------
        :class:`~hondana.Author`
            The author created within the API.
        """  # noqa: DOC502 # raised in method call
        data = await self._http.create_author(
            name=name,
            biography=biography,
            twitter=twitter,
            pixiv=pixiv,
            melon_book=melon_book,
            fan_box=fan_box,
            booth=booth,
            nico_video=nico_video,
            skeb=skeb,
            fantia=fantia,
            tumblr=tumblr,
            youtube=youtube,
            website=website,
        )
        return Author(self._http, data["data"])

    async def get_author(self, author_id: str, /, *, includes: AuthorIncludes | None = None) -> Author:
        """|coro|

        The method will fetch an Author from the MangaDex API.


        .. note::
            MangaDex does not differentiate types of Artist/Author. The endpoint is the same for both.

        Parameters
        ----------
        author_id: :class:`str`
            The ID of the author we are fetching.
        includes: Optional[:class:`~hondana.query.AuthorIncludes`]
            The optional extra data we are requesting from the API.
            Defaults to all possible expansions.

        Raises
        ------
        NotFound
            The passed author ID was not found, likely due to an incorrect ID.

        Returns
        -------
        :class:`~hondana.Author`
            The Author returned from the API.
        """  # noqa: DOC502 # raised in method call
        data = await self._http.get_author(author_id, includes=includes or AuthorIncludes())

        return Author(self._http, data["data"])

    async def get_artist(self, artist_id: str, /, *, includes: ArtistIncludes | None = None) -> Artist:
        """|coro|

        The method will fetch an artist from the MangaDex API.


        .. note::
            MangaDex does not differentiate types of Artist/Author. The endpoint is the same for both.

        Parameters
        ----------
        artist_id: :class:`str`
            The ID of the author we are fetching.
        includes: Optional[:class:`~hondana.query.AuthorIncludes`]
            The optional extra data we are requesting from the API.
            Defaults to all possible expansions.

        Raises
        ------
        NotFound
            The passed artist ID was not found, likely due to an incorrect ID.

        Returns
        -------
        :class:`~hondana.Artist`
            The Author returned from the API.
        """  # noqa: DOC502 # raised in method call
        data = await self._http.get_artist(artist_id, includes=includes or ArtistIncludes())

        return Artist(self._http, data["data"])

    @require_authentication
    async def update_author(
        self,
        author_id: str,
        /,
        *,
        name: str | None = None,
        biography: common.LocalizedString | None = None,
        twitter: str = MISSING,
        pixiv: str = MISSING,
        melon_book: str = MISSING,
        fan_box: str = MISSING,
        booth: str = MISSING,
        nico_video: str = MISSING,
        skeb: str = MISSING,
        fantia: str = MISSING,
        tumblr: str = MISSING,
        youtube: str = MISSING,
        website: str = MISSING,
        version: int,
    ) -> Author:
        """|coro|

        This method will update an author on the MangaDex API.

        Parameters
        ----------
        author_id: :class:`str`
            The UUID relating to the author we wish to update.
        name: Optional[:class:`str`]
            The new name to update the author with.
        biography: Optional[:class:`~hondana.types_.common.LocalizedString`]
            The biography of the author we are creating.
        twitter: Optional[:class:`str`]
            The twitter URL of the author.
        pixiv: Optional[:class:`str`]
            The pixiv URL of the author.
        melon_book: Optional[:class:`str`]
            The melon book URL of the author.
        fan_box: Optional[:class:`str`]
            The fan box URL of the author.
        booth: Optional[:class:`str`]
            The booth URL of the author.
        nico_video: Optional[:class:`str`]
            The nico video URL of the author.
        skeb: Optional[:class:`str`]
            The skeb URL of the author.
        fantia: Optional[:class:`str`]
            The fantia URL of the author.
        tumblr: Optional[:class:`str`]
            The tumblr URL of the author.
        youtube: Optional[:class:`str`]
            The youtube  URL of the author.
        website: Optional[:class:`str`]
            The website URL of the author.
        version: :class:`int`
            The version revision of this author.

        Raises
        ------
        BadRequest
            The request body was malformed.
        Forbidden
            You are not authorized to update this author.
        NotFound
            The author UUID given was not found.

        Returns
        -------
        :class:`~hondana.Author`
            The updated author from the API.
        """  # noqa: DOC502 # raised in method call
        data = await self._http.update_author(
            author_id,
            name=name,
            biography=biography,
            twitter=twitter,
            pixiv=pixiv,
            melon_book=melon_book,
            fan_box=fan_box,
            booth=booth,
            nico_video=nico_video,
            skeb=skeb,
            fantia=fantia,
            tumblr=tumblr,
            youtube=youtube,
            website=website,
            version=version,
        )
        return Author(self._http, data["data"])

    @require_authentication
    async def delete_author(self, author_id: str, /) -> None:
        """|coro|

        This method will delete an author from the MangaDex API.

        Parameters
        ----------
        author_id: :class:`str`
            The UUID relating the author you wish to delete.

        Raises
        ------
        Forbidden
            You are not authorized to delete this author.
        NotFound
            The UUID given for the author was not found.
        """  # noqa: DOC502 # raised in method call
        await self._http.delete_author(author_id)

    @require_authentication
    async def get_my_reports(
        self,
        *,
        limit: int = 10,
        offset: int = 0,
        object_id: str | None = None,
        reason: ReportReason | None = None,
        category: ReportCategory | None = None,
        status: ReportStatus | None = None,
        order: ReportListOrderQuery | None = None,
        includes: UserReportIncludes | None = None,
    ) -> UserReportCollection:
        """|coro|

        This method will get any reports submitted by the logged in user.

        Parameters
        ----------
        limit:  :class:`int`
            The amount of items to fetch per query. Defaults to ``10``.
        offset: :class:`int`
            The pagination offset to begin fetching from. Defaults to ``0``.
        object_id: Optional[:class:`str`]
            The id of the object to fetch reports for. Defaults to ``None``.
        reason: Optional[:class:`hondana.ReportReason`]
            The reason for the reports to filter by, if any.
        category: Optional[:class:`hondana.ReportCategory`]
            The category of the reports to filter by, if any.
        status: Optional[:class:`hondana.ReportStatus`]
            The status of the reports to filter by, if any.
        order: Optional[:class:`hondana.ReportListOrderQuery`]
            The order of the query, if any.
        includes: Optional[:class:`hondana.UserReportIncludes`]
            The data to include with each report, if any.
            Defaults to all optional data.

        Raises
        ------
        BadRequest
            The query data was not in an acceptable format.
        Forbidden
            There is invalid or no login credentials supplied.
        NotFound
            The requested data cannot be found.

        Returns
        -------
        :class:`hondana.UserReportCollection`
        """  # noqa: DOC502 # raised by method call
        data = await self._http.get_reports_current_user(
            limit=limit,
            offset=offset,
            object_id=object_id,
            reason=reason,
            category=category,
            status=status,
            order=order,
            includes=includes,
        )

        reports = [UserReport(self._http, item) for item in data["data"]]

        return UserReportCollection(self._http, data, reports)

    @require_authentication
    async def create_report(self, details: ReportDetails, /) -> None:
        """|coro|

        This method will create a report for moderator review in the MangaDex API.

        Parameters
        ----------
        details: :class:`~hondana.ReportDetails`
            The details of the report.

        Raises
        ------
        BadRequest
            The request body was malformed.
        Forbidden
            The request returned a response due to authentication failure.
        NotFound
            The specified report UUID or object UUID does not exist.
        """  # noqa: DOC502 # raised in method call
        await self._http.create_report(details=details)

    @require_authentication
    async def get_my_manga_ratings(self, manga_ids: list[str], /) -> list[MangaRating]:
        """|coro|

        This method will return your personal manga ratings for the given manga.

        Parameters
        ----------
        manga_ids: List[:class:`str`]
            The IDs of the manga you wish to fetch your ratings for.

        Raises
        ------
        Forbidden
            Failed response due to authentication failure.
        NotFound
            A given manga id was not found or does not exist.

        Returns
        -------
        List[:class:`~hondana.MangaRating`]
        """  # noqa: DOC502 # raised in method call
        data = await self._http.get_my_ratings(manga_ids)

        ratings = data["ratings"]

        return [MangaRating(self._http, id_, stats) for id_, stats in ratings.items()]

    @require_authentication
    async def set_manga_rating(self, manga_id: str, /, *, rating: int) -> None:
        """|coro|

        This method will set your rating on the passed manga.
        This method **overwrites** your previous set rating, if any.

        Parameters
        ----------
        manga_id: :class:`str`
            The manga you are setting the rating for.
        rating: :class:`int`
            The rating value, between 1 and 10.

        Raises
        ------
        Forbidden
            The request returned a response due to authentication failure.
        NotFound
            The specified manga UUID was not found or does not exist.
        """  # noqa: DOC502 # raised in method call
        await self._http.set_manga_rating(manga_id, rating=rating)

    @require_authentication
    async def delete_manga_rating(self, manga_id: str, /) -> None:
        """|coro|

        This method will delete your set rating on the passed manga.

        Parameters
        ----------
        manga_id: :class:`str`
            The manga you wish to delete the rating for.

        Raises
        ------
        Forbidden
            The request returned a response due to authentication failure.
        NotFound
            The specified manga UUID was not found or does not exist.
        """  # noqa: DOC502 # raised in method call
        await self._http.delete_manga_rating(manga_id)

    async def get_manga_statistics(
        self,
        manga_id: str | None = None,
        manga_ids: list[str] | None = None,
        /,
    ) -> MangaStatistics:
        """|coro|

        This method will return the statistics for the passed manga, singular or plural.

        Parameters
        ----------
        manga_id: Optional[:class:`str`]
            The manga id to fetch the statistics for.
        manga_ids: Optional[List[:class:`str`]]
            The list of manga IDs to fetch the statistics for.

        Returns
        -------
        :class:`~hondana.MangaStatistics`
        """
        data = await self._http.get_manga_statistics(manga_id, manga_ids)
        key = next(iter(data["statistics"]))

        return MangaStatistics(self._http, key, data["statistics"][key])

    @require_authentication
    async def abandon_upload_session(self, session_id: str, /) -> None:
        """|coro|

        This method will abandon an existing upload session.

        Parameters
        ----------
        session_id: :class:`str`
            The upload
        """
        await self._http.abandon_upload_session(session_id)

    @require_authentication
    def upload_session(
        self,
        manga: Manga | str,
        /,
        *,
        chapter: str,
        chapter_to_edit: Chapter | str | None = None,
        volume: str | None = None,
        title: str | None = None,
        translated_language: common.LanguageCode,
        scanlator_groups: list[str],
        external_url: str | None = None,
        publish_at: datetime.datetime | None = None,
        existing_upload_session_id: str | None = None,
        version: int | None = None,
        accept_tos: bool,
    ) -> ChapterUpload:
        """
        This method will return an async `context manager <https://realpython.com/python-with-statement/>`_
        to handle some upload session management.


        Examples
        --------
        Using the async context manager: ::

            async with Client.upload_session(
                manga,
                chapter=chapter,
                volume=volume,
                title=title,
                translated_language=translated_language,
                scanlator_groups=scanlator_groups,
                accept_tos=True,
            ) as session:
                await session.upload_images(your_list_of_bytes)


        Parameters
        ----------
        manga: Union[:class:`~hondana.Manga`, :class:`str`]
            The manga we will be uploading a chapter for.
        chapter: :class:`str`
            The chapter we are uploading.
            Typically, this is a numerical identifier.
        chapter_to_edit: Optional[Union[:class:`~hondana.Chapter`, :class:`str`]]
            The chapter you intend to edit.
            Defaults to ``None``.
        volume: Optional[:class:`str`]
            The volume we are uploading a chapter for.
            Typically, this is a numerical identifier.
            Defaults to ``None`` in the API.
        title: Optional[:class:`str`]
            The chapter's title.
            Defaults to ``None``.
        translated_language: :class:`~hondana.types_.common.LanguageCode`
            The language this chapter is translated in.
        scanlator_groups: List[:class:`str`]
            The list of scanlator groups to attribute to this chapter's scanlation.
            Only 5 are allowed on a given chapter.
        external_url: Optional[:class:`str`]
            The external URL of this chapter.
            Defaults to ``None``.
        publish_at: Optional[:class:`datetime.datetime`]
            When to publish this chapter (and pages) on MangaDex, represented as a *UTC* datetime.
            This must be a future date.
        existing_upload_session_id: Optional[:class:`str`]
            Pass this parameter if you wish to resume an existing upload session.
        version: Optional[:class:`int`]
            The new version of the chapter you are editing.
            Only necessary if ``chapter_to_edit`` is not ``None``.
        accept_tos: :class:`bool`
            Whether you accept the `MangaDex Terms of Service <https://mangadex.org/compliance>`_ by uploading this chapter.


        .. note::
            The ``external_url`` parameter requires an explicit permission on MangaDex to set.

        Returns
        -------
        :class:`~hondana.ChapterUpload`
        """  # noqa: D205, D404
        return ChapterUpload(
            self._http,
            manga,
            chapter=chapter,
            chapter_to_edit=chapter_to_edit,
            volume=volume,
            title=title,
            translated_language=translated_language,
            scanlator_groups=scanlator_groups,
            external_url=external_url,
            publish_at=publish_at,
            existing_upload_session_id=existing_upload_session_id,
            version=version,
            accept_tos=accept_tos,
        )

    @require_authentication
    async def upload_chapter(
        self,
        manga: Manga | str,
        /,
        *,
        chapter: str,
        chapter_to_edit: Chapter | str | None = None,
        volume: str | None = None,
        title: str | None = None,
        translated_language: common.LanguageCode,
        scanlator_groups: list[str],
        external_url: str | None = None,
        publish_at: datetime.datetime | None = None,
        existing_upload_session_id: str | None = None,
        version: int | None = None,
        accept_tos: bool,
        images: list[pathlib.Path],
    ) -> Chapter:
        """|coro|

        This method will perform the chapter upload for you, providing a list of images.

        Parameters
        ----------
        manga: Union[:class:`~hondana.Manga`, :class:`str`]
            The manga we will be uploading a chapter for.
        chapter: :class:`str`
            The chapter we are uploading.
            Typically, this is a numerical identifier.
        chapter_to_edit: Optional[Union[:class:`~hondana.Chapter`, :class:`str`]]
            The chapter you intend to edit.
            Defaults to ``None``.
        volume: Optional[:class:`str`]
            The volume we are uploading a chapter for.
            Typically, this is a numerical identifier.
            Defaults to ``None``.
        title: Optional[:class:`str`]
            The chapter's title.
            Defaults to ``None``.
        translated_language: :class:`~hondana.types_.common.LanguageCode`
            The language this chapter is translated in.
        scanlator_groups: List[:class:`str`]
            The list of scanlator groups to attribute to this chapter's scanlation.
            Only 5 are allowed on a given chapter.
        external_url: Optional[:class:`str`]
            The external URL of this chapter.
            Defaults to ``None``.
        publish_at: Optional[:class:`datetime.datetime`]
            When to publish this chapter (and pages) on MangaDex, represented as a *UTC* datetime.
            This must be a future date.
        existing_upload_session_id: Optional[:class:`str`]
            Pass this parameter if you wish to resume an existing upload session.
        version: Optional[:class:`int`]
            The new version of the chapter you are editing.
            Only necessary if ``chapter_to_edit`` is not ``None``.
        accept_tos: :class:`bool`
            Whether you accept the `MangaDex Terms of Service <https://mangadex.org/compliance>`_ by uploading this chapter.
        images: List[:class:`pathlib.Path`]
            The list of images to upload as their Paths.

        Returns
        -------
        :class:`hondana.Chapter`
            The chapter we created.


        .. note::
            The ``external_url`` parameter requires an explicit permission on MangaDex to set.

        .. warning::
            The ``images`` parameter MUST be ordered how you would expect the images to be shown in the frontend.
            E.g. ``list[0]`` would be page 1, and so on.
            The upload method will sort them alphabetically for you by default, to which I recommend naming the files
            ``1.png``, ``2.png``, etc.

        .. warning::
            This method is for ease of use, but offers little control over the upload session.
            If you need more control, such as to delete images from the existing session.
            I suggest using :meth:`~hondana.Client.upload_session` instead for greater control.

        .. note::
            I personally advise the `context manager <https://realpython.com/python-with-statement/>`_
            method as it allows more control over your upload session.
        """
        async with ChapterUpload(
            self._http,
            manga,
            chapter=chapter,
            chapter_to_edit=chapter_to_edit,
            volume=volume,
            title=title,
            translated_language=translated_language,
            publish_at=publish_at,
            scanlator_groups=scanlator_groups,
            external_url=external_url,
            existing_upload_session_id=existing_upload_session_id,
            accept_tos=accept_tos,
            version=version,
        ) as session:
            await session.upload_images(images)
            return await session.commit()

    @require_authentication
    async def get_latest_settings_template(self) -> dict[str, Any]:
        """|coro|

        This method will return the json object of the latest settings template.

        Currently, there is no formatting done on this key as the api has not documented it.

        Returns
        -------
        Dict[:class:`str`, :class:`Any`]
            The settings template.
        """
        return await self._http.get_latest_settings_template()

    @require_authentication
    async def get_specific_template_version(self, version: str) -> dict[str, Any]:
        """|coro|

        This method will return a specific setting template version.

        Parameters
        ----------
        version: :class:`str`
            The UUID relating to the specified template.

        Raises
        ------
        Forbidden
            The request failed due to authentication issues.
        NotFound
            The specified template was not found.

        Returns
        -------
        Dict[:class:`str`, :class:`Any`]
            The returned settings template.
        """  # noqa: DOC502 # raised in method call
        return await self._http.get_specific_template_version(version)

    @require_authentication
    async def get_my_settings(self) -> SettingsPayload:
        """|coro|

        This method will return the current logged-in user's settings.

        Raises
        ------
        Forbidden
            The request failed due to authentication issues.
        NotFound
            The logged-in user's settings were not found.

        Returns
        -------
        :class:`hondana.types_.settings.SettingsPayload`
            The user's settings.
        """  # noqa: DOC502 # raised in method call
        return await self._http.get_user_settings()

    @require_authentication
    async def upsert_user_settings(self, payload: Settings, updated_at: datetime.datetime | None = None) -> SettingsPayload:
        """|coro|

        This method will update or create user settings based on a formatted settings templates.

        Parameters
        ----------
        payload: :class:`hondana.types_.settings.Settings`
            A payload representing the settings.
        updated_at: :class:`datetime.datetime`
            The datetime at which you updated the settings.
            Defaults to a UTC datetime for "now".

        Raises
        ------
        Forbidden
            The request failed due to authentication issues.
        NotFound
            The logged-in user's settings were not found.

        Returns
        -------
        :class:`~hondana.types_.settings.SettingsPayload`
            The returned (and created) payload.
        """  # noqa: DOC502 # raised in method call
        time = updated_at or datetime.datetime.now(datetime.UTC)
        return await self._http.upsert_user_settings(payload, updated_at=time)

    @require_authentication
    async def create_forum_thread(self, thread_type: ForumThreadType, resource_id: str) -> ForumThread:
        """|coro|

        This method will create a forum thread.

        Parameters
        ----------
        thread_type: :class:`hondana.ForumThreadType`
            Which type of thread to create.
        resouces_id: :class:`str`
            The id of the item we're creating the thread around, e.g. a Manga id.

        Raises
        ------
        NotFound
            The resource ID was not found.
        BadRequest
            Parameters were not in an acceptable format.

        Returns
        -------
        :class:`hondana.ForumThread`
        """  # noqa: DOC502 # raised in method call.
        data = await self._http.create_forum_thread(thread_type=thread_type, resource_id=resource_id)

        return ForumThread(self._http, data["data"])

    @require_authentication
    async def check_upload_approval_required(self, *, manga_id: str, locale: common.LanguageCode) -> bool:
        """|coro|

        This method will check if moderator approval will be required for uploading to a manga.

        Parameters
        ----------
        manga_id: :class:`str`
            The ID of the manga we will be checking against.
        locale: :class:`hondana.types_.common.LanguageCode`
            The locale we will be uploading.

        Returns
        -------
        :class:`bool`
        """
        data = await self._http.check_approval_required(manga_id, locale)
        return data["requiresApproval"]
