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
import pathlib
from base64 import b64decode
from os import PathLike
from typing import TYPE_CHECKING, Any, Literal, Optional, Union, overload

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
    MangaRelationType,
    MangaState,
    MangaStatus,
    PublicationDemographic,
    ReadingStatus,
    ReportCategory,
    ReportReason,
    ReportStatus,
)
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
from .token import Permissions
from .user import User
from .utils import MISSING, require_authentication


if TYPE_CHECKING:
    from aiohttp import ClientSession

    from .tags import QueryTags
    from .types import common, legacy, manga
    from .types.settings import Settings, SettingsPayload
    from .types.token import TokenPayload

_PROJECT_DIR = pathlib.Path(__file__)

__all__ = ("Client",)


class Client:
    """User Client for interfacing with the MangaDex API.

    Attributes
    -----------
    username: Optional[:class:`str`]
        Your login username for the API / site. Used in conjunction with your password to generate an authentication token.
    email: Optional[:class:`str`]
        Your login email for the API / site. Used in conjunction with your password to generate an authentication token.
    password: Optional[:class:`str`]
        Your login password for the API / site. Used in conjunction with your username to generate an authentication token.
    session: Optional[:class:`aiohttp.ClientSession`]
        A aiohttp ClientSession to use instead of creating one.
    refresh_token: Optional[:class:`str`]
        Your last refresh token to use if you want to skip the login stage.


    .. note::
        The Client will work without authentication, and all authenticated endpoints will fail before attempting a request.

    .. note::
        The :class:`aiohttp.ClientSession` passed via constructor will have headers and authentication set.
        Do not pass one you plan to re-use for other things, lest you leak your login data.


    Raises
    -------
    ValueError
        You failed to pass appropriate login information (login/email and password).
    """

    __slots__ = ("_http",)

    @overload
    def __init__(
        self,
        *,
        username: None = ...,
        email: None = ...,
        password: None = ...,
        session: Optional[ClientSession] = ...,
        refresh_token: None = ...,
    ) -> None:
        ...

    @overload
    def __init__(
        self,
        *,
        username: None = ...,
        email: str = ...,
        password: str = ...,
        session: Optional[ClientSession] = ...,
        refresh_token: None = ...,
    ) -> None:
        ...

    @overload
    def __init__(
        self,
        *,
        username: None = ...,
        email: str = ...,
        password: str = ...,
        session: Optional[ClientSession] = ...,
        refresh_token: str = ...,
    ) -> None:
        ...

    @overload
    def __init__(
        self,
        *,
        username: str = ...,
        email: None = ...,
        password: str = ...,
        session: Optional[ClientSession] = ...,
        refresh_token: None = ...,
    ) -> None:
        ...

    @overload
    def __init__(
        self,
        *,
        username: str = ...,
        email: None = ...,
        password: str = ...,
        session: Optional[ClientSession] = ...,
        refresh_token: str = ...,
    ) -> None:
        ...

    @overload
    def __init__(
        self,
        *,
        username: None = ...,
        email: None = ...,
        password: None = ...,
        session: Optional[ClientSession] = ...,
        refresh_token: str = ...,
    ) -> None:
        ...

    def __init__(
        self,
        *,
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        session: Optional[ClientSession] = None,
        refresh_token: Optional[str] = None,
    ) -> None:
        self._http = HTTPClient(
            username=username, email=email, password=password, session=session, refresh_token=refresh_token
        )

    def __repr__(self) -> str:
        return f"<Client authenticated={self._http._authenticated}>"

    @overload
    def login(self, *, username: str = ..., email: None = ..., password: str, refresh_token: None = ...) -> None:
        ...

    @overload
    def login(self, *, username: None = ..., email: str = ..., password: str, refresh_token: None = ...) -> None:
        ...

    @overload
    def login(self, *, username: str = ..., email: None = ..., password: str, refresh_token: str = ...) -> None:
        ...

    @overload
    def login(self, *, username: None = ..., email: str = ..., password: str, refresh_token: str = ...) -> None:
        ...

    @overload
    def login(self, *, username: None = ..., email: None = ..., password: None = ..., refresh_token: str = ...) -> None:
        ...

    def login(
        self,
        *,
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        refresh_token: Optional[str] = None,
    ) -> None:
        """A method to add authentication details to the client post-creation.

        Parameters
        -----------
        username: Optional[:class:`str`]
            The login username to authenticate to the API.
        email: Optional[:class:`str`]
            The login email to authenticate to the API.
        password: Optional[:class:`str`]
            The password to authenticate to the API.
        refresh_token: Optional[:class:`str`]
            The refresh token to use in place of auth.
        """
        if (username is None and email is None) and refresh_token is None:
            raise ValueError("An email or username must be passed or a refresh token must be provided.")

        self._http.username = username
        self._http.email = email
        self._http.password = password
        self._http._refresh_token = refresh_token
        self._http._authenticated = True

    async def static_login(self) -> None:
        """|coro|

        This method simply logs into the API and assigns a token to the client.
        """
        await self._http._try_token()

    @property
    def permissions(self) -> Optional[Permissions]:
        """
        This attribute will return a permissions instance for the current logged-in user.

        You must be authenticated to access this, and logged in.

        If you wish to just check permissions without making an api request, consider :meth:`~hondana.Client.static_login`

        Returns
        --------
        :class:`~hondana.Permissions`
        """
        if not self._http._authenticated:
            return None

        token = self._http._token
        if token is None:
            return None

        # The JWT stores payload in the second block
        payload = token.split(".")[1]
        padding = len(payload) % 4
        payload += "=" * padding
        parsed_payload: TokenPayload = json.loads(b64decode(payload))

        return Permissions(parsed_payload)

    @require_authentication
    def dump_refresh_token(
        self,
        *,
        file: bool = True,
        path: Union[PathLike[str], str] = ".hondana-refresh-token",
        mode: Literal["a", "a+", "w", "w+"] = "w",
    ) -> str:
        """
        This method will dump your current refresh token to a file for later re-use in the login process in future client initialisations.

        Parameters
        -----------
        file: :class:`bool`
            Whether to dump to a file, or not.
        path: Union[:class:`os.PathLike`, :class:`str`]
            The path to dump the file. Defaults to ``".hondana-refresh-token"``.
        mode: Literal[``"a"``, ``"a+"``, ``"w"``, ``"w+"``]
            The mode in which to open the file. Defaults to ``"w"``.

        Returns
        --------
        :class:`str`
            The current refresh token.
        """
        if self._http._refresh_token is None:
            raise TypeError(
                "Authentication is set but there is no refresh token available, perhaps you haven't logged in yet?"
            )
        if file:
            with open(path, mode) as fp:
                fp.write(self._http._refresh_token)

        return self._http._refresh_token

    @require_authentication
    async def logout(self) -> None:
        """|coro|

        Logs the client out. This process will invalidate the current authorization token in the process.
        """

        return await self._http._logout()

    async def close(self) -> None:
        """|coro|

        Logs the client out of the API and closes the internal http session.
        """

        return await self._http._close()

    async def check_username_available(self, username: str) -> bool:
        """|coro|

        This method will check if the username supplied is available for use on MangaDex.

        Parameters
        -----------
        username: :class:`str`
            The username to check for.

        Raises
        -------
        :exc:`Forbidden`
            The request failed due to authorization.

        Returns
        --------
        :class:`bool`
            If the username is available or not.
        """
        data = await self._http._account_available(username)
        return data["available"]

    async def update_tags(self) -> dict[str, str]:
        """|coro|

        Convenience method for updating the local cache of tags.

        This should ideally not need to be called by the end user but nevertheless it exists in the event MangaDex
        add a new tag or similar.

        Returns
        --------
        Dict[:class:`str`, :class:`str`]
            The new tags from the API.
        """
        tags = await self.get_tags()

        pre_fmt = {tag.name: tag.id for tag in tags}
        fmt = dict(sorted(pre_fmt.items(), key=lambda t: t[0]))

        path = _PROJECT_DIR.parent / "extras" / "tags.json"
        with open(path, "w") as fp:
            json.dump(fmt, fp, indent=4)

        return fmt

    async def update_report_reasons(self) -> dict[str, dict[str, str]]:
        """|coro|

        Convenience method for updating the local cache of report reasons.

        This should ideally not need to be called by the end user but nevertheless it exists in the event MangaDex
        add a new report reasons or similar.

        Returns
        --------
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
            data = await self._http._get_report_reason_list(category)
            ret[category.value] = {}
            for inner in data["data"]:
                key_name = (
                    inner["attributes"]["reason"]["en"].lower().replace("-", "").replace("/", " or ").replace(" ", "_")  # type: ignore # always in en apparently
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
        --------
        List[:class:`~hondana.Tag`]
            The list of tags.
        """
        data = await self._http._update_tags()

        return [Tag(item) for item in data["data"]]

    @require_authentication
    async def get_my_feed(
        self,
        *,
        limit: Optional[int] = 100,
        offset: int = 0,
        translated_language: Optional[list[common.LanguageCode]] = None,
        original_language: Optional[list[common.LanguageCode]] = None,
        excluded_original_language: Optional[list[common.LanguageCode]] = None,
        content_rating: Optional[list[ContentRating]] = None,
        excluded_groups: Optional[list[str]] = None,
        excluded_uploaders: Optional[list[str]] = None,
        include_future_updates: Optional[bool] = None,
        created_at_since: Optional[datetime.datetime] = None,
        updated_at_since: Optional[datetime.datetime] = None,
        published_at_since: Optional[datetime.datetime] = None,
        order: Optional[FeedOrderQuery] = None,
        includes: Optional[ChapterIncludes] = ChapterIncludes(),
        include_empty_pages: Optional[bool] = None,
        include_future_publish_at: Optional[bool] = None,
        include_external_url: Optional[bool] = None,
    ) -> ChapterFeed:
        """|coro|

        This method will retrieve the logged-in user's followed manga chapter feed.

        Parameters
        -----------
        limit: :class:`int`
            Defaults to 100. This is the limit of manga that is returned in this request,
            it is clamped at 500 as that is the max in the API.
        offset: :class:`int`
            Defaults to 0. This is the pagination offset, the number must be greater than 0.
            If set lower than 0 then it is set to 0.
        translated_language: List[:class:`~hondana.types.common.LanguageCode`]
            A list of language codes to filter the returned chapters with.
        original_language: List[:class:`~hondana.types.common.LanguageCode`]
            A list of language codes to filter the original language of the returned chapters with.
        excluded_original_language: List[:class:`~hondana.types.common.LanguageCode`]
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
        includeExternalUrl: Optional[:class:`bool`]
            Whether to show chapters that have an external URL attached to them.


        .. note::
            If no start point is given with the `created_at_since`, `updated_at_since` or `published_at_since` parameters,
            then the API will return oldest first based on creation date.

        Raises
        -------
        :exc:`BadRequest`
            The query parameters were not valid.

        Returns
        --------
        :class:`~hondana.ChapterFeed`
            Returns a collection of chapters.
        """
        inner_limit = limit or 100

        chapters = []
        while True:
            data = await self._http._manga_feed(
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
                includes=includes,
                include_empty_pages=include_empty_pages,
                include_future_publish_at=include_future_publish_at,
                include_external_url=include_external_url,
            )

            chapters.extend([Chapter(self._http, item) for item in data["data"]])

            offset += inner_limit
            if not data["data"] or offset >= 10_000 or limit is not None:
                break

        return ChapterFeed(self._http, data, chapters)

    async def manga_list(
        self,
        *,
        limit: Optional[int] = 100,
        offset: int = 0,
        title: Optional[str] = None,
        authors: Optional[list[str]] = None,
        artists: Optional[list[str]] = None,
        year: Optional[int] = None,
        included_tags: Optional[QueryTags] = None,
        excluded_tags: Optional[QueryTags] = None,
        status: Optional[list[MangaStatus]] = None,
        original_language: Optional[list[common.LanguageCode]] = None,
        excluded_original_language: Optional[list[common.LanguageCode]] = None,
        available_translated_language: Optional[list[common.LanguageCode]] = None,
        publication_demographic: Optional[list[PublicationDemographic]] = None,
        ids: Optional[list[str]] = None,
        content_rating: Optional[list[ContentRating]] = None,
        created_at_since: Optional[datetime.datetime] = None,
        updated_at_since: Optional[datetime.datetime] = None,
        order: Optional[MangaListOrderQuery] = None,
        includes: Optional[MangaIncludes] = MangaIncludes(),
        has_available_chapters: Optional[bool] = None,
        group: Optional[str] = None,
    ) -> MangaCollection:
        """|coro|

        This method will perform a search based on the passed query parameters for manga.

        Parameters
        -----------
        limit: Optional[:class:`int`]
            Defaults to 100. This is the limit of manga that is returned in this request,
            it is clamped at 500 as that is the max in the API.
        offset: :class:`int`
            Defaults to 0. This is the pagination offset, the number must be greater than 0.
            If set lower than 0 then it is set to 0.
        title: Optional[:class:`str`]
            The manga title or partial title to include in the search.
        authors: Optional[List[:class:`str`]]
            The author(s) UUIDs to include in the search.
        artists: Optional[List[:class:`str`]]
            The artist(s) UUIDs to include in the search.
        year: Optional[:class:`int`]
            The release year of the manga to include in the search.
        included_tags: Optional[:class:`QueryTags`]
            An instance of :class:`hondana.QueryTags` to include in the search.
        excluded_tags: Optional[:class:`QueryTags`]
            An instance of :class:`hondana.QueryTags` to include in the search.
        status: Optional[List[:class:`~hondana.MangaStatus`]]
            The status(es) of manga to include in the search.
        original_language: Optional[List[:class:`~hondana.types.common.LanguageCode`]]
            A list of language codes to include for the manga's original language.
            i.e. ``["en"]``
        excluded_original_language: Optional[List[:class:`~hondana.types.common.LanguageCode`]]
            A list of language codes to exclude for the manga's original language.
            i.e. ``["en"]``
        available_translated_language: Optional[List[:class:`~hondana.types.common.LanguageCode`]]
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
        group: Optional[:class:`str`]
            Filter the manga list to only those uploaded by this group.


        .. note::
            Passing ``None`` to ``limit`` will attempt to retrieve all items in the manga list.

        Raises
        -------
        :exc:`BadRequest`
            The query parameters were not valid.

        Returns
        --------
        :class:`~hondana.MangaCollection`
            Returns a collection of Manga.
        """
        inner_limit = limit or 100

        manga = []
        while True:
            data = await self._http._manga_list(
                limit=inner_limit,
                offset=offset,
                title=title,
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
                includes=includes,
                has_available_chapters=has_available_chapters,
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
        alt_titles: Optional[list[common.LocalizedString]] = None,
        description: Optional[common.LocalizedString] = None,
        authors: Optional[list[str]] = None,
        artists: Optional[list[str]] = None,
        links: Optional[manga.MangaLinks] = None,
        original_language: str,
        last_volume: Optional[str] = None,
        last_chapter: Optional[str] = None,
        publication_demographic: Optional[PublicationDemographic] = None,
        status: MangaStatus,
        year: Optional[int] = None,
        content_rating: ContentRating,
        tags: Optional[QueryTags] = None,
        mod_notes: Optional[str] = None,
    ) -> Manga:
        """|coro|

        This method will create a Manga within the MangaDex API for you.

        Parameters
        -----------
        title: :class:`~hondana.types.common.LocalizedString`
            The manga titles in the format of ``language_key: title``
            i.e. ``{"en": "Some Manga Title"}``
        alt_titles: Optional[List[:class:`~hondana.types.common.LocalizedString`]]
            The alternative titles in the format of ``language_key: title``
            i.e. ``[{"en": "Some Other Title"}, {"fr": "Un Autre Titre"}]``
        description: Optional[:class:`~hondana.types.common.LocalizedString`]
            The manga description in the format of ``language_key: description``
            i.e. ``{"en": "My amazing manga where x y z happens"}``
        authors: Optional[List[:class:`str`]]
            The list of author UUIDs to credit to this manga.
        artists: Optional[List[:class:`str`]]
            The list of artist UUIDs to credit to this manga.
        links: Optional[:class:`~hondana.types.manga.MangaLinks`]
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
        -------
        :exc:`BadRequest`
            The query parameters were not valid.
        :exc:`Forbidden`
            The query failed due to authorization failure.

        Returns
        --------
        :class:`~hondana.Manga`
            The manga that was returned after creation.
        """

        data = await self._http._create_manga(
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
        translated_language: Optional[list[common.LanguageCode]] = None,
        groups: Optional[list[str]] = None,
    ) -> manga.GetMangaVolumesAndChaptersResponse:
        """|coro|

        This endpoint returns the raw relational mapping of a manga's volumes and chapters.

        Parameters
        -----------
        manga_id: :class:`str`
            The manga UUID we are querying against.
        translated_language: Optional[List[:class:`~hondana.types.common.LanguageCode`]]
            The list of language codes you want to limit the search to.
        groups: Optional[List[:class:`str`]]
            A list of scanlator groups to filter the results by.

        Returns
        --------
        :class:`~hondana.types.manga.GetMangaVolumesAndChaptersResponse`
            The raw payload from mangadex. There is no guarantee of the keys here.
        """
        data = await self._http._get_manga_volumes_and_chapters(
            manga_id=manga_id, translated_language=translated_language, groups=groups
        )

        return data

    async def get_manga(self, manga_id: str, /, *, includes: Optional[MangaIncludes] = MangaIncludes()) -> Manga:
        """|coro|

        The method will fetch a Manga from the MangaDex API.

        Parameters
        -----------
        manga_id: :class:`str`
            The UUID of the manga to view.
        includes: Optional[:class:`~hondana.query.MangaIncludes`]
            The includes query parameter for this manga.
            If not given, it defaults to all possible reference expansions.

        Raises
        -------
        :exc:`Forbidden`
            The query failed due to authorization failure.
        :exc:`NotFound`
            The passed manga ID was not found, likely due to an incorrect ID.

        Returns
        --------
        :class:`~hondana.Manga`
            The Manga that was returned from the API.

        .. versionadded:: 2.0.11
        """
        data = await self._http._get_manga(manga_id, includes=includes)

        return Manga(self._http, data["data"])

    @require_authentication
    async def update_manga(
        self,
        manga_id: str,
        /,
        *,
        title: Optional[common.LocalizedString] = None,
        alt_titles: Optional[list[common.LocalizedString]] = None,
        description: Optional[common.LocalizedString] = None,
        authors: Optional[list[str]] = None,
        artists: Optional[list[str]] = None,
        links: Optional[manga.MangaLinks] = None,
        original_language: Optional[str] = None,
        last_volume: Optional[str] = MISSING,
        last_chapter: Optional[str] = MISSING,
        publication_demographic: Optional[PublicationDemographic] = MISSING,
        status: Optional[MangaStatus],
        year: Optional[int] = MISSING,
        content_rating: Optional[ContentRating] = None,
        tags: Optional[QueryTags] = None,
        primary_cover: Optional[str] = MISSING,
        version: int,
    ) -> Manga:
        """|coro|

        This method will update a Manga within the MangaDex API.

        Parameters
        -----------
        manga_id: :class:`str`
            The UUID of the manga to update.
        title: Optional[:class:`~hondana.types.common.LocalizedString`]
            The manga titles in the format of ``language_key: title``
        alt_titles: Optional[List[:class:`~hondana.types.common.LocalizedString`]]
            The alternative titles in the format of ``language_key: title``
        description: Optional[:class:`~hondana.types.common.LocalizedString`]
            The manga description in the format of ``language_key: description``
        authors: Optional[List[:class:`str`]]
            The list of author UUIDs to credit to this manga.
        artists: Optional[List[:class:`str`]]
            The list of artist UUIDs to credit to this manga.
        links: Optional[:class:`~hondana.types.manga.MangaLinks`]
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
        -------
        :exc:`BadRequest`
            The query parameters were not valid.
        :exc:`Forbidden`
            The returned an error due to authentication failure.
        :exc:`NotFound`
            The specified manga does not exist.

        Returns
        --------
        :class:`~hondana.Manga`
            The manga that was returned after creation.
        """
        data = await self._http._update_manga(
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
        -----------
        manga_id: :class:`str`
            The ID of the manga we are deleting.

        Raises
        -------
        :exc:`Forbidden`
            The request returned an error due to authentication failure.
        :exc:`NotFound`
            The specified manga doesn't exist.
        """
        await self._http._delete_manga(manga_id)

    @require_authentication
    async def unfollow_manga(self, manga_id: str, /) -> None:
        """|coro|

        This method will unfollow a Manga for the logged-in user in the MangaDex API.

        Parameters
        -----------
        manga_id: :class:`str`
            The UUID of the manga to unfollow.

        Raises
        -------
        :exc:`Forbidden`
            The request returned an error due to authentication failure.
        :exc:`NotFound`
            The specified manga does not exist.
        """
        await self._http._unfollow_manga(manga_id)

    @require_authentication
    async def follow_manga(
        self, manga_id: str, /, *, set_status: bool = True, status: ReadingStatus = ReadingStatus.reading
    ) -> None:
        """|coro|

        This method will follow a Manga for the logged-in user in the MangaDex API.

        Parameters
        -----------
        manga_id: :class:`str`
            The UUID of the manga to follow.
        set_status: :class:`bool`
            Whether to set the reading status of the manga you follow.
            Due to the current MangaDex infrastructure, not setting a status will cause the manga to not show up in your lists.
            Defaults to ``True``
        status: :class:`~hondana.ReadingStatus`
            The status to apply to the newly followed manga.
            Irrelevant if ``set_status`` is ``False``.

        Raises
        -------
        :exc:`Forbidden`
            The request returned an error due to authentication failure.
        :exc:`NotFound`
            The specified manga does not exist.
        """
        await self._http._follow_manga(manga_id)
        if set_status:
            await self._http._update_manga_reading_status(manga_id, status=status)

    async def manga_feed(
        self,
        manga_id: str,
        /,
        *,
        limit: Optional[int] = 100,
        offset: int = 0,
        translated_language: Optional[list[common.LanguageCode]] = None,
        original_language: Optional[list[common.LanguageCode]] = None,
        excluded_original_language: Optional[list[common.LanguageCode]] = None,
        content_rating: Optional[list[ContentRating]] = None,
        excluded_groups: Optional[list[str]] = None,
        excluded_uploaders: Optional[list[str]] = None,
        include_future_updates: Optional[bool] = None,
        created_at_since: Optional[datetime.datetime] = None,
        updated_at_since: Optional[datetime.datetime] = None,
        published_at_since: Optional[datetime.datetime] = None,
        order: Optional[FeedOrderQuery] = None,
        includes: Optional[ChapterIncludes] = ChapterIncludes(),
        include_empty_pages: Optional[bool] = None,
        include_future_publish_at: Optional[bool] = None,
        include_external_url: Optional[bool] = None,
    ) -> ChapterFeed:
        """|coro|

        This method returns the specified manga's chapter feed.

        Parameters
        -----------
        manga_id: :class:`str`
            The UUID of the manga whose feed we are requesting.
        limit: Optional[:class:`int`]
            Defaults to 100. The maximum amount of chapters to return in the response.
        offset: :class:`int`
            Defaults to 0. The pagination offset for the request.
        translated_language: List[:class:`~hondana.types.common.LanguageCode`]
            A list of language codes to filter the returned chapters with.
        original_language: List[:class:`~hondana.types.common.LanguageCode`]
            A list of language codes to filter the original language of the returned chapters with.
        excluded_original_language: List[:class:`~hondana.types.common.LanguageCode`]
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
        includeExternalUrl: Optional[:class:`bool`]
            Whether to show chapters that have an external URL attached to them.


        .. note::
            Passing ``None`` to ``limit`` will attempt to retrieve all items in the chapter feed.

        Raises
        -------
        :exc:`BadRequest`
            The query parameters were malformed.

        Returns
        --------
        :class:`~hondana.ChapterFeed`
            Returns a collection of chapters.
        """
        inner_limit = limit or 100

        chapters = []
        while True:
            data = await self._http._manga_feed(
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
                includes=includes,
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
    async def manga_read_markers(
        self, *, manga_ids: list[str]
    ) -> Union[manga.MangaReadMarkersResponse, manga.MangaGroupedReadMarkersResponse]:
        """|coro|

        This method will return the read chapters of the passed manga if singular, or all manga if plural.

        Parameters
        -----------
        manga_ids: List[:class:`str`]
            A list of a single manga UUID or a list of many manga UUIDs.

        Returns
        --------
        Union[:class:`~hondana.types.manga.MangaReadMarkersResponse`, :class:`~hondana.types.manga.MangaGroupedReadMarkersResponse`]
        """
        if len(manga_ids) == 1:
            return await self._http._manga_read_markers(manga_ids, grouped=False)
        return await self._http._manga_read_markers(manga_ids, grouped=True)

    @require_authentication
    async def batch_update_manga_read_markers(
        self,
        manga_id: str,
        /,
        *,
        update_history: bool = True,
        read_chapters: Optional[list[str]] = None,
        unread_chapters: Optional[list[str]] = None,
    ) -> None:
        """|coro|

        This method will batch update your read chapters for a given Manga.

        Parameters
        -----------
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
        -------
        :exc:`TypeError`
            You must provide one or both of the parameters `read_chapters` and/or `unread_chapters`.
        """
        if not read_chapters and not unread_chapters:
            raise TypeError("You must provide either `read_chapters` and/or `unread_chapters` to this method.")

        await self._http._manga_read_markers_batch(
            manga_id, update_history=update_history, read_chapters=read_chapters, unread_chapters=unread_chapters
        )

    async def get_random_manga(
        self,
        *,
        includes: Optional[MangaIncludes] = MangaIncludes(),
        content_rating: Optional[list[ContentRating]] = None,
        included_tags: Optional[QueryTags] = None,
        excluded_tags: Optional[QueryTags] = None,
    ) -> Manga:
        """|coro|

        This method will return a random manga from the MangaDex API.

        Parameters
        -----------
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
        --------
        :class:`~hondana.Manga`
            The random Manga that was returned.
        """
        data = await self._http._get_random_manga(
            includes=includes, content_rating=content_rating, included_tags=included_tags, excluded_tags=excluded_tags
        )

        return Manga(self._http, data["data"])

    @require_authentication
    async def get_my_followed_manga(
        self,
        *,
        limit: Optional[int] = 100,
        offset: int = 0,
        includes: Optional[MangaIncludes] = MangaIncludes(),
    ) -> MangaCollection:
        """|coro|

        This method will return an object containing all the followed manga from the currently logged-in user.

        Parameters
        -----------
        limit: Optional[:class:`int`]
            The amount of items we are requesting.
        offset: :class:`int`
            The pagination offset for the items we are requesting.
        includes: Optional[:class:`~hondana.query.MangaIncludes`]
            The optional includes to add to the api responses.


        .. note::
            Passing ``None`` to ``limit`` will attempt to retrieve all items in the followed manga list.

        Returns
        --------
        :class:`~hondana.MangaCollection`
            Returns a collection of manga.
        """
        inner_limit = limit or 100

        manga = []
        while True:
            data = await self._http._get_user_followed_manga(limit=inner_limit, offset=offset, includes=includes)
            manga.extend([Manga(self._http, item) for item in data["data"]])

            offset += inner_limit
            if not data["data"] or offset >= 10_000 or limit is not None:
                break

        return MangaCollection(self._http, data, manga)

    @require_authentication
    async def get_all_manga_reading_status(
        self, *, status: Optional[ReadingStatus] = None
    ) -> manga.MangaMultipleReadingStatusResponse:
        """|coro|

        This method will return the current reading status of all manga in the logged-in user's library.

        Parameters
        -----------
        status: Optional[:class:`~hondana.ReadingStatus`]
            The reading status to filter the response with.

        Returns
        --------
        :class:`~hondana.types.manga.MangaMultipleReadingStatusResponse`
            The payload returned from MangaDex.
        """
        return await self._http._get_all_manga_reading_status(status=status)

    @require_authentication
    async def get_manga_reading_status(self, manga_id: str, /) -> manga.MangaSingleReadingStatusResponse:
        """|coro|

        This method will return the current reading status for the specified manga.

        Parameters
        -----------
        manga_id: :class:`str`
            The UUID associated with the manga you wish to query.

        Raises
        -------
        :exc:`Forbidden`
            You are not authenticated to perform this action.
        :exc:`NotFound`
            The specified manga does not exist, likely due to an incorrect ID.

        Returns
        --------
        :class:`~hondana.types.manga.MangaSingleReadingStatusResponse`
            The raw response from the API on the request.
        """
        return await self._http._get_manga_reading_status(manga_id)

    @require_authentication
    async def update_manga_reading_status(self, manga_id: str, /, *, status: ReadingStatus) -> None:
        """|coro|

        This method will update your current reading status for the specified manga.

        Parameters
        -----------
        manga_id: :class:`str`
            The UUID associated with the manga you wish to update.
        status: Optional[:class:`~hondana.ReadingStatus`]
            The reading status you wish to update this manga with.


        .. note::
            Leaving ``status`` as the default will remove the manga reading status from the API.
            Please provide a value if you do not wish for this to happen.

        Raises
        -------
        :exc:`BadRequest`
            The query parameters were invalid.
        :exc:`NotFound`
            The specified manga cannot be found, likely due to incorrect ID.
        """

        await self._http._update_manga_reading_status(manga_id, status=status)

    async def get_manga_draft(self, manga_id: str, /) -> Manga:
        """|coro|

        This method will return a manga draft from MangaDex.

        Parameters
        -----------
        manga_id: :class:`str`
            The ID relation to the manga draft.

        Returns
        --------
        :class:`~hondana.Manga`
            The Manga returned from the API.
        """
        data = await self._http._get_manga_draft(manga_id)
        return Manga(self._http, data["data"])

    @require_authentication
    async def submit_manga_draft(self, manga_id: str, /, *, version: int) -> Manga:
        """|coro|

        This method will submit a draft for a manga.

        Parameters
        -----------
        manga_id: :class:`str`
            The ID relating to the manga we are submitting to.
        version: :class:`int`
            The version of the manga we're attributing this submission to.

        Returns
        --------
        :class:`~hondana.Manga`

        Raises
        -------
        :exc:`BadRequest`
            The request parameters were incorrect or malformed.
        :exc:`Forbidden`
            You are not authorised to perform this action.
        :exc:`NotFound`
            The manga was not found.
        """
        data = await self._http._submit_manga_draft(manga_id, version=version)
        return Manga(self._http, data["data"])

    @require_authentication
    async def get_manga_draft_list(
        self,
        *,
        limit: int = 10,
        offset: int = 0,
        state: Optional[MangaState] = None,
        order: Optional[MangaDraftListOrderQuery] = None,
        includes: Optional[MangaIncludes] = MangaIncludes(),
    ) -> Manga:
        """|coro|

        This method will return all drafts for a given manga.

        Parameters
        -----------
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
        --------
        :class:`~hondana.Manga`
        """
        data = await self._http._get_manga_draft_list(
            limit=limit, offset=offset, state=state, order=order, includes=includes
        )
        return Manga(self._http, data["data"])

    async def get_manga_relation_list(
        self, manga_id: str, /, *, includes: Optional[MangaIncludes] = MangaIncludes()
    ) -> MangaRelationCollection:
        """|coro|

        This method will return a list of all relations to a given manga.

        Parameters
        -----------
        manga_id: :class:`str`
            The ID for the manga we wish to query against.
        includes: Optional[:class:`~hondana.query.MangaIncludes`]
            The optional parameters for expanded requests to the API.
            Defaults to all possible expansions.

        Returns
        --------
        :class:`~hondana.MangaRelationCollection`

        Raises
        -------
        :exc:`BadRequest`
            The manga ID passed is malformed
        """
        data = await self._http._get_manga_relation_list(manga_id, includes=includes)
        fmt = [MangaRelation(self._http, manga_id, item) for item in data["data"]]
        return MangaRelationCollection(self._http, data, fmt)

    @require_authentication
    async def create_manga_relation(
        self, manga_id: str, /, *, target_manga: str, relation_type: MangaRelationType
    ) -> MangaRelation:
        """|coro|

        This method will create a manga relation.

        Parameters
        ------------
        manga_id: :class:`str`
            The manga ID we are creating a relation to.
        target_manga: :class:`str`
            The manga ID of the related manga.
        relation_type: :class:`~hondana.MangaRelationType`
            The relation type we are creating.

        Returns
        --------
        :class:`~hondana.MangaRelation`

        Raises
        -------
        :exc:`BadRequest`
            The parameters were malformed
        :exc:`Forbidden`
            You are not authorised for this action.
        """
        data = await self._http._create_manga_relation(manga_id, target_manga=target_manga, relation_type=relation_type)
        return MangaRelation(self._http, manga_id, data["data"])

    @require_authentication
    async def delete_manga_relation(self, manga_id: str, relation_id: str, /) -> None:
        """|coro|

        This method will delete a manga relation.

        Parameters
        -----------
        manga_id: :class:`str`
            The ID of the source manga.
        relation_id: :class:`str`
            The ID of the related manga.
        """
        await self._http._delete_manga_relation(manga_id, relation_id)

    @require_authentication
    async def add_manga_to_custom_list(self, manga_id: str, /, *, custom_list_id: str) -> None:
        """|coro|

        This method will add the specified manga to the specified custom list.

        Parameters
        -----------
        manga_id: :class:`str`
            The UUID associated with the manga you wish to add to the custom list.
        custom_list_id: :class:`str`
            The UUID associated with the custom list you wish to add the manga to.

        Raises
        -------
        :exc:`Forbidden`
            You are not authorised to add manga to this custom list.
        :exc:`NotFound`
            The specified manga or specified custom list are not found, likely due to an incorrect UUID.
        """

        await self._http._add_manga_to_custom_list(manga_id=manga_id, custom_list_id=custom_list_id)

    @require_authentication
    async def remove_manga_from_custom_list(self, manga_id: str, /, *, custom_list_id: str) -> None:
        """|coro|

        This method will remove the specified manga from the specified custom list.

        Parameters
        -----------
        manga_id: :class:`str`
            The UUID associated with the manga you wish to remove from the specified custom list.
        custom_list_id: :class:`str`
            THe UUID associated with the custom list you wish to add the manga to.

        Raises
        -------
        :exc:`Forbidden`
            You are not authorised to remove a manga from the specified custom list.
        :exc:`NotFound`
            The specified manga or specified custom list are not found, likely due to an incorrect UUID.
        """

        await self._http._remove_manga_from_custom_list(manga_id=manga_id, custom_list_id=custom_list_id)

    async def chapter_list(
        self,
        *,
        limit: Optional[int] = 100,
        offset: int = 0,
        ids: Optional[list[str]] = None,
        title: Optional[str] = None,
        groups: Optional[list[str]] = None,
        uploader: Optional[Union[str, list[str]]] = None,
        manga: Optional[str] = None,
        volume: Optional[Union[str, list[str]]] = None,
        chapter: Optional[Union[str, list[str]]] = None,
        translated_language: Optional[list[common.LanguageCode]] = None,
        original_language: Optional[list[common.LanguageCode]] = None,
        excluded_original_language: Optional[list[common.LanguageCode]] = None,
        content_rating: Optional[list[ContentRating]] = None,
        excluded_groups: Optional[list[str]] = None,
        excluded_uploaders: Optional[list[str]] = None,
        include_future_updates: Optional[bool] = None,
        created_at_since: Optional[datetime.datetime] = None,
        updated_at_since: Optional[datetime.datetime] = None,
        published_at_since: Optional[datetime.datetime] = None,
        order: Optional[FeedOrderQuery] = None,
        includes: Optional[ChapterIncludes] = ChapterIncludes(),
    ) -> ChapterFeed:
        """|coro|

        This method will return a list of published chapters.

        Parameters
        -----------
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
        translated_language: Optional[List[:class:`~hondana.types.common.LanguageCode`]]
            The list of languages codes to filter the request with.
        original_language: Optional[List[:class:`~hondana.types.common.LanguageCode`]]
            The list of languages to specifically target in the request.
        excluded_original_language: Optional[List[:class:`~hondana.types.common.LanguageCode`]]
            The list of original languages to exclude from the request.
        content_rating: Optional[List[:class:`~hondana.ContentRating`]]
            The content rating to filter the feed by.
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
        includes: Optional[:class:`~hondana.query.ChapterIncludes`]
            The list of options to include increased payloads for per chapter.
            Defaults to all possible expansions.


        .. note::
            Passing ``None`` to ``limit`` will attempt to retrieve all items in the chapter feed.

        .. note::
            If `order` is not specified then the API will return results first based on their creation date,
            which could lead to unexpected results.

        Raises
        -------
        :exc:`BadRequest`
            The query parameters were malformed
        :exc:`Forbidden`
            The request returned an error due to authentication failure.

        Returns
        --------
        :class:`~hondana.ChapterFeed`
            Returns a collection of chapters.
        """
        inner_limit = limit or 100

        chapters = []
        while True:
            data = await self._http._chapter_list(
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
                created_at_since=created_at_since,
                updated_at_since=updated_at_since,
                published_at_since=published_at_since,
                order=order,
                includes=includes,
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
        includes: Optional[ChapterIncludes] = ChapterIncludes(),
        fetch_full_manga: bool = False,
    ) -> Chapter:
        """|coro|

        This method will retrieve a single chapter from the MangaDex API.

        Parameters
        -----------
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
        --------
        :class:`~hondana.Chapter`
            The Chapter we fetched from the API.
        """
        data = await self._http._get_chapter(chapter_id, includes=includes)

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
        title: Optional[str] = None,
        volume: str = MISSING,
        chapter: str = MISSING,
        translated_language: Optional[str] = None,
        groups: Optional[list[str]] = None,
        version: int,
    ) -> Chapter:
        """|coro|

        This method will update a chapter in the MangaDex API.

        Parameters
        -----------
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
        -----------
        chapter_id: :class:`str`
            The UUID of the chapter you wish to delete.

        Raises
        -------
        :exc:`BadRequest`
            The query was malformed.
        :exc:`Forbidden`
            You are not authorized to delete this chapter.
        :exc:`NotFound`
            The UUID passed for this chapter does not relate to a chapter in the API.
        """
        await self._http._delete_chapter(chapter_id)

    @require_authentication
    async def my_chapter_read_history(self) -> ChapterReadHistoryCollection:
        """|coro|

        This method will return the last 30 chapters of read history for the currently logged in user.

        Raises
        -------
        :exc:`Forbidden`
            You are not authorized to access this endpoint.
        :exc:`NotFound`
            You do not have any read history.

        Returns
        --------
        :class:`~hondana.ChapterReadHistoryCollection`
            A rich type around the returned data.
        """
        data = await self._http._user_read_history()

        history: list[PreviouslyReadChapter] = []
        for payload in data["data"]:
            history.append(PreviouslyReadChapter(self._http, (payload["chapterId"], payload["readDate"])))

        return ChapterReadHistoryCollection(self._http, data, history)

    async def cover_art_list(
        self,
        *,
        limit: Optional[int] = 10,
        offset: int = 0,
        manga: Optional[list[str]] = None,
        ids: Optional[list[str]] = None,
        uploaders: Optional[list[str]] = None,
        locales: Optional[list[common.LanguageCode]] = None,
        order: Optional[CoverArtListOrderQuery] = None,
        includes: Optional[CoverIncludes] = CoverIncludes(),
    ) -> CoverCollection:
        """|coro|

        This method will fetch a list of cover arts from the MangaDex API.

        Parameters
        -----------
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
        locales: Optional[List[:class:`~hondana.types.common.LanguageCode`]]
            The locales to filter this search by.
        order: Optional[:class:`~hondana.query.CoverArtListOrderQuery`]
            A query parameter to choose how the responses are ordered.
        includes: Optional[:class:`~hondana.query.CoverIncludes`]
            The optional includes to request increased payloads during the request.

        Raises
        -------
        :exc:`BadRequest`
            The request parameters were malformed.
        :exc:`Forbidden`
            The request returned an error due to authentication failure.

        Returns
        --------
        :class:`~hondana.CoverCollection`
            Returns a collection of covers.
        """
        inner_limit = limit or 10

        covers = []

        while True:
            data = await self._http._cover_art_list(
                limit=inner_limit,
                offset=offset,
                manga=manga,
                ids=ids,
                uploaders=uploaders,
                locales=locales,
                order=order,
                includes=includes,
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
        volume: Optional[str] = None,
        description: str,
        locale: Optional[common.LanguageCode] = None,
    ) -> Cover:
        """|coro|

        This method will upload a cover to the MangaDex API.

        Parameters
        -----------
        manga_id: :class:`str`
            The ID relating to the manga this cover belongs to.
        cover: :class:`bytes`
            THe raw bytes of the image.
        volume: Optional[:class:`str`]
            The volume this cover relates to.
        description: :class:`str`
            The description of this cover.
        locale: Optional[:class:`~hondana.types.common.LanguageCode`]
            The locale of this cover.

        Raises
        -------
        :exc:`BadRequest`
            The volume parameter was malformed or the file was a bad format.
        :exc:`Forbidden`
            You are not permitted for this action.

        Returns
        --------
        :class:`~hondana.Cover`
        """
        data = await self._http._upload_cover(manga_id, cover=cover, volume=volume, description=description, locale=locale)

        return Cover(self._http, data["data"])

    async def get_cover(self, cover_id: str, /, *, includes: Optional[CoverIncludes] = CoverIncludes()) -> Cover:
        """|coro|

        The method will fetch a Cover from the MangaDex API.

        Parameters
        -----------
        cover_id: :class:`str`
            The id of the cover we are fetching from the API.
        includes: Optional[:class:`~hondana.query.CoverIncludes`]
            A list of the additional information to gather related to the Cover.


        .. note::
            If you do not include the ``"manga"`` includes, then we will not be able to get the cover url.

        Raises
        -------
        :exc:`NotFound`
            The passed cover ID was not found, likely due to an incorrect ID.

        Returns
        --------
        :class:`~hondana.Cover`
            The Cover returned from the API.
        """
        data = await self._http._get_cover(cover_id, includes=includes)

        return Cover(self._http, data["data"])

    @require_authentication
    async def edit_cover(
        self, cover_id: str, /, *, volume: str = MISSING, description: str = MISSING, version: int
    ) -> Cover:
        """|coro|

        This method will edit a cover on the MangaDex API.

        Parameters
        -----------
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
        -------
        :exc:`TypeError`
            The volume key was not given a value. This is required.
        :exc:`BadRequest`
            The request body was malformed.
        :exc:`Forbidden`
            The request returned an error due to authentication failure.

        Returns
        --------
        :class:`~hondana.Cover`
            The returned cover after the edit.
        """
        data = await self._http._edit_cover(cover_id, volume=volume, description=description, version=version)

        return Cover(self._http, data["data"])

    @require_authentication
    async def delete_cover(self, cover_id: str, /) -> None:
        """|coro|

        This method will delete a cover from the MangaDex API.

        Parameters
        -----------
        cover_id: :class:`str`
            The UUID relating to the cover you wish to delete.

        Raises
        -------
        :exc:`BadRequest`
            The request payload was malformed.
        :exc:`Forbidden`
            The request returned an error due to authentication.
        """
        await self._http._delete_cover(cover_id)

    async def scanlation_group_list(
        self,
        *,
        limit: Optional[int] = 10,
        offset: int = 0,
        ids: Optional[list[str]] = None,
        name: Optional[str] = None,
        focused_language: Optional[common.LanguageCode] = None,
        order: Optional[ScanlatorGroupListOrderQuery] = None,
        includes: Optional[ScanlatorGroupIncludes] = ScanlatorGroupIncludes(),
    ) -> ScanlatorGroupCollection:
        """|coro|

        This method will return a list of scanlator groups from the MangaDex API.

        Parameters
        -----------
        limit: Optional[:class:`int`]
            Defaults to 10. This specifies the amount of scanlator groups to return in one request.
        offset: :class:`int`
            Defaults to 0. The pagination offset.
        ids: Optional[List[:class:`str`]]
            A list of scanlator group UUID(s) to limit the request to.
        name: Optional[:class:`str`]
            A name to limit the request to.
        focused_language: Optional[:class:`~hondana.types.common.LanguageCode`]
            A focused language to limit the request to.
        order: Optional[:class:`~hondana.query.ScanlatorGroupListOrderQuery`]
            An ordering statement for the request.
        includes: Optional[:class:`~hondana.query.ScanlatorGroupIncludes`]
            An optional list of includes to request increased payloads during the request.


        .. note::
            Passing ``None`` to ``limit`` will attempt to retrieve all items in the chapter feed.

        Raises
        -------
        :exc:`BadRequest`
            The query parameters were malformed
        :exc:`Forbidden`
            The request returned an error due to authentication failure.

        Returns
        --------
        :class:`ScanlatorGroupCollection`
            A returned collection of scanlation groups.
        """
        inner_limit = limit or 10

        groups = []

        while True:
            data = await self._http._scanlation_group_list(
                limit=inner_limit,
                offset=offset,
                ids=ids,
                name=name,
                focused_language=focused_language,
                order=order,
                includes=includes,
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
        limit: Optional[int] = 10,
        offset: int = 0,
        ids: Optional[list[str]] = None,
        username: Optional[str] = None,
        order: Optional[UserListOrderQuery] = None,
    ) -> UserCollection:
        """|coro|

        This method will return a list of Users from the MangaDex API.

        Parameters
        -----------
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
        -------
        :exc:`BadRequest`
            The request parameters were malformed
        :exc:`Forbidden`
            The request returned an error due to authentication failure.

        Returns
        --------
        :class:`UserCollection`
            A returned collection of users.
        """
        inner_limit = limit or 10

        users = []

        while True:
            data = await self._http._user_list(limit=inner_limit, offset=offset, ids=ids, username=username, order=order)
            users.extend([User(self._http, item) for item in data["data"]])

            offset += inner_limit
            if not data["data"] or offset >= 10_000 or limit is not None:
                break

        return UserCollection(self._http, data, users)

    async def get_user(self, user_id: str, /) -> User:
        """|coro|

        This method will fetch a user from the MangaDex API.

        Parameters
        -----------
        user_id: :class:`str`
            The UUID of the user you wish to fetch

        Returns
        --------
        :class:`User`
            The user returned from the API.
        """
        data = await self._http._get_user(user_id)

        return User(self._http, data["data"])

    @require_authentication
    async def delete_user(self, user_id: str, /) -> None:
        """|coro|

        This method will initiate the deletion of a user from the MangaDex API.

        Parameters
        -----------
        user_id: :class:`str`
            The UUID of the user you wish to delete.

        Raises
        -------
        :exc:`Forbidden`
            The response returned an error due to authentication failure.
        :exc:`NotFound`
            The user specified cannot be found.
        """

        await self._http._delete_user(user_id)

    async def approve_user_deletion(self, approval_code: str, /) -> None:
        """|coro|

        This method will approve a user deletion in the MangaDex API.

        Parameters
        -----------
        approval_code: :class:`str`
            The UUID representing the approval code to delete the user.
        """

        await self._http._approve_user_deletion(approval_code)

    @require_authentication
    async def update_user_password(self, *, old_password: str, new_password: str) -> None:
        """|coro|

        This method will change the current authenticated user's password.

        Parameters
        -----------
        old_password: :class:`str`
            The current (old) password we will be changing from.
        new_password: :class:`str`
            The new password we will be changing to.

        Raises
        -------
        :exc:`Forbidden`
            The request returned an error due to an authentication issue.
        """

        await self._http._update_user_password(old_password=old_password, new_password=new_password)

    @require_authentication
    async def update_user_email(self, email: str, /) -> None:
        """|coro|

        This method will update the current authenticated user's email.

        Parameters
        -----------
        email: :class:`str`
            The new email address to change to.

        Raises
        -------
        :exc:`Forbidden`
            The API returned an error due to authentication failure.
        """

        await self._http._update_user_email(email)

    @require_authentication
    async def get_my_details(self) -> User:
        """|coro|

        This method will return the current authenticated user's details.

        Raises
        -------
        :exc:`Forbidden`
            The request returned an error due to authentication failure.

        Returns
        --------
        :class:`~hondana.User`
            Your current user details returned from the API.
        """
        data = await self._http._get_my_details()

        return User(self._http, data["data"])

    @require_authentication
    async def get_my_followed_groups(self, limit: int = 10, offset: int = 0) -> list[ScanlatorGroup]:
        """|coro|

        This method will return a list of scanlation groups the current authenticated user follows.

        Parameters
        -----------
        limit: :class:`int`
            Defaults to 10. The amount of groups to return in one request.
        offset: :class:`int`
            Defaults to 0. The pagination offset.

        Raises
        -------
        :exc:`Forbidden`
            The request returned an error due to authentication failure.

        Returns
        --------
        List[:class:`ScanlatorGroup`]
            The list of groups that are being followed.
        """
        data = await self._http._get_my_followed_groups(limit=limit, offset=offset)

        return [ScanlatorGroup(self._http, item) for item in data["data"]]

    @require_authentication
    async def check_if_following_group(self, group_id: str, /) -> bool:
        """|coro|

        This method will check if the current authenticated user is following a scanlation group.

        Parameters
        -----------
        group_id: :class:`str`
            The UUID representing the scanlation group you wish to check.

        Returns
        --------
        :class:`bool`
            Whether the passed scanlation group is followed or not.
        """

        try:
            await self._http._check_if_following_group(group_id)
        except errors.NotFound:
            return False
        else:
            return True

    @require_authentication
    async def get_my_followed_users(self, *, limit: Optional[int] = 10, offset: int = 0) -> UserCollection:
        """|coro|

        This method will return the current authenticated user's followed users.

        Parameters
        -----------
        limit: Optional[:class:`int`]
            Defaults to 10. The amount of users to return in one request.
        offset: :class:`int`
            Defaults to 0. The pagination offset.


        .. note::
            Passing ``None`` to ``limit`` will attempt to retrieve all items in the chapter feed.

        Raises
        -------
        :exc:`Forbidden`
            The request returned an error due to authentication failure.

        Returns
        --------
        :class:`~hondana.UserCollection`
            A returned collection of users.
        """
        inner_limit = limit or 10

        users = []

        while True:
            data = await self._http._get_my_followed_users(limit=inner_limit, offset=offset)
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
        -----------
        user_id: :class:`str`
            The UUID relating to the user you wish to query against.

        Raises
        -------
        :exc:`Forbidden`
            The requested returned an error due to authentication failure.

        Returns
        --------
        :class:`bool`
            Whether the target user is followed or not.
        """

        try:
            await self._http._check_if_following_user(user_id)
        except errors.NotFound:
            return False
        else:
            return True

    @require_authentication
    async def check_if_following_manga(self, manga_id: str, /) -> bool:
        """|coro|

        This method will check if the current authenticated user is following the specified manga.

        Parameters
        -----------
        manga_id: :class:`str`
            The UUID relating to the manga you wish to query against.

        Raises
        -------
        :exc:`Forbidden`
            The request returned an error due to authentication failure.

        Returns
        --------
        :class:`bool`
            Whether the target manga is followed or not.
        """

        try:
            await self._http._check_if_following_manga(manga_id)
        except errors.NotFound:
            return False
        else:
            return True

    @require_authentication
    async def get_my_custom_list_follows(self, limit: int = 10, offset: int = 0) -> list[CustomList]:
        """|coro|

        This method will return the current authenticated user's custom list follows.

        Returns
        --------
        list[:class:`CustomList`]
            The list of custom lists you follow.
        """
        data = await self._http._get_user_custom_list_follows(limit=limit, offset=offset)

        return [CustomList(self._http, item) for item in data["data"]]

    @require_authentication
    async def check_if_following_custom_list(self, custom_list_id: str, /) -> bool:
        """|coro|

        This method will check if the current authenticated user is following the specified custom list.

        Returns
        --------
        :class:`bool`
            Whether you follow this custom list or not.
        """
        try:
            await self._http._check_if_following_list(custom_list_id)
        except errors.NotFound:
            return False
        else:
            return True

    async def create_account(self, *, username: str, password: str, email: str) -> User:
        """|coro|

        This method will create an account with the passed parameters within the MangaDex API.

        Parameters
        -----------
        username: :class:`str`
            The username you wish to use in the new account.
        password: :class:`str`
            The password to use in the new account.
        email: :class:`str`
            The email address to use in the new account.


        .. note::
            The created account will still need to be activated.

        Raises
        -------
        :exc:`BadRequest`
            The parameters passed were malformed.

        Returns
        --------
        :class:`User`
            The created user.
        """
        data = await self._http._create_account(username=username, password=password, email=email)
        return User(self._http, data["data"])

    async def activate_account(self, activation_code: str, /) -> None:
        """|coro|

        This method will activate an account on the MangaDex API.

        Parameters
        -----------
        activation_code: :class:`str`
            The activation code for the account.

        Raises
        -------
        :exc:`BadRequest`
            The query was malformed.
        :exc:`NotFound`
            The activation code passed was not a valid one.
        """
        await self._http._activate_account(activation_code)

    async def resend_activation_code(self, email: str, /) -> None:
        """|coro|

        This method will resend an activation code to the specified email.

        Parameters
        -----------
        email: :class:`str`
            The email to resend the activation code to.

        Raises
        -------
        :exc:`BadRequest`
            The email passed is not pending activation.
        """
        await self._http._resend_activation_code(email)

    async def recover_account(self, email: str, /) -> None:
        """|coro|

        This method will start an account recovery process on the given account.
        Effectively triggering the "forgotten password" email to be sent.

        Parameters
        -----------
        email: :class:`str`
            The email address belonging to the account you wish to recover.

        Raises
        -------
        :exc:`BadRequest`
            The email does not belong to a matching account.
        """
        await self._http._recover_account(email)

    async def complete_account_recovery(self, recovery_code: str, /, *, new_password: str) -> None:
        """|coro|

        This method will complete an account recovery process.

        Parameters
        -----------
        recovery_code: :class:`str`
            The recovery code given during the recovery process.
        new_password: :class:`str`
            The new password to use for the recovered account.

        Raises
        -------
        :exc:`BadRequest`
            The recovery code given was not found or the password was greater than 1024 characters.
        """
        await self._http._complete_account_recovery(recovery_code, new_password=new_password)

    async def ping_the_server(self) -> bool:
        """|coro|

        This method will return a simple 'pong' response from the API.
        Mainly a small endpoint to check the API is alive and responding.

        Returns
        --------
        :class:`bool`
            Whether and 'pong' response was received.
        """
        data = await self._http._ping_the_server()
        return data == "pong"

    async def legacy_id_mapping(self, type: legacy.LegacyMappingType, /, *, item_ids: list[int]) -> LegacyMappingCollection:
        """|coro|

        This method will return a small response from the API to retrieve a legacy MangaDex's new details.

        Parameters
        -----------
        type: :class:`~hondana.types.legacy.LegacyMappingType`
            The type of the object we are querying.
        item_ids: List[:class:`int`]
            The legacy integer IDs of MangaDex items.

        Raises
        --------
        :exc:`BadRequest`
            The query was malformed.

        Returns
        ---------
        :class:`LegacyMappingCollection`
            The list of returned items from this query.
        """
        data = await self._http._legacy_id_mapping(type, item_ids=item_ids)
        items = [LegacyItem(self._http, item) for item in data["data"]]
        return LegacyMappingCollection(self._http, data, items)

    async def get_at_home_url(self, chapter_id: str, /, *, ssl: bool = True) -> str:
        """|coro|

        This method will retrieve a MangaDex@Home URL for accessing a chapter.

        Parameters
        -----------
        chapter_id: :class:`str`
            The UUID of the chapter we are retrieving a URL for.
        ssl: :class:`bool`
            Defaults to ``True``. Whether to require the MangaDex @ Home node be available on port 443.
            If ``False`` is selected, then the MD@H node we request may be available on a non-standard port.

        Raises
        -------
        :exc:`NotFound`
            The specified chapter ID was not found.

        Returns
        --------
        :class:`str`
            Returns the URL we requested.
        """
        data = await self._http._get_at_home_url(chapter_id, ssl=ssl)
        return data["baseUrl"]

    @require_authentication
    async def create_custom_list(
        self,
        *,
        name: str,
        visibility: Optional[CustomListVisibility] = None,
        manga: Optional[list[str]] = None,
    ) -> CustomList:
        """|coro|

        This method will create a custom list within the MangaDex API.

        Parameters
        -----------
        name: :class:`str`
            The name of this custom list.
        visibility: Optional[:class:`~hondana.CustomListVisibility`]
            The visibility of this custom list.
        manga: Optional[List[:class:`str`]]
            A list of manga IDs to add to this custom list.

        Raises
        -------
        :exc:`BadRequest`
            The payload was malformed.
        :exc:`NotFound`
            One of the passed Manga IDs was not found.

        Returns
        --------
        :class:`~hondana.CustomList`
            The custom list that was created.
        """
        data = await self._http._create_custom_list(name=name, visibility=visibility, manga=manga)

        return CustomList(self._http, data["data"])

    async def get_custom_list(
        self,
        custom_list_id: str,
        /,
        *,
        includes: Optional[CustomListIncludes] = CustomListIncludes(),
    ) -> CustomList:
        """|coro|

        This method will retrieve a custom list from the MangaDex API.

        Parameters
        -----------
        custom_list_id: :class:`str`
            The UUID associated with the custom list we wish to retrieve.
        includes: Optional[:class:`~hondana.query.CustomListIncludes`]
            The list of additional data to request in the payload.

        Raises
        -------
        :exc:`NotFound`
            The custom list with this ID was not found.

        Returns
        --------
        :class:`~hondana.CustomList`
            The retrieved custom list.
        """
        data = await self._http._get_custom_list(custom_list_id, includes=includes)

        return CustomList(self._http, data["data"])

    @require_authentication
    async def update_custom_list(
        self,
        custom_list_id: str,
        /,
        *,
        name: Optional[str] = None,
        visibility: Optional[CustomListVisibility] = None,
        manga: Optional[list[str]] = None,
        version: int,
    ) -> CustomList:
        """|coro|

        This method will update a custom list within the MangaDex API.

        Parameters
        -----------
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
        -------
        :exc:`BadRequest`
            The request body was malformed.
        :exc:`Forbidden`
            You are not authorized to edit this custom list.
        :exc:`NotFound`
            The custom list was not found, or one of the manga passed was not found.

        Returns
        --------
        :class:`~hondana.CustomList`
            The returned custom list after it was updated.
        """
        data = await self._http._update_custom_list(
            custom_list_id, name=name, visibility=visibility, manga=manga, version=version
        )

        return CustomList(self._http, data["data"])

    @require_authentication
    async def delete_custom_list(self, custom_list_id: str, /) -> None:
        """|coro|

        This method will delete a custom list from the MangaDex API.

        Parameters
        -----------
        custom_list_id: :class:`str`
            The UUID relating to the custom list we wish to delete.

        Raises
        -------
        :exc:`Forbidden`
            You are not authorized to delete this custom list.
        :exc:`NotFound`
            The custom list with this UUID was not found.
        """
        await self._http._delete_custom_list(custom_list_id)

    @require_authentication
    async def follow_custom_list(self, custom_list_id: str, /) -> None:
        """|coro|

        This method will follow a custom list within the MangaDex API.

        Parameters
        -----------
        custom_list_id: :class:`str`
            The UUID relating to the custom list we wish to follow.

        Raises
        -------
        :exc:`BadRequest`
            The request was malformed.
        :exc:`Forbidden`
            You are not authorized to follow this custom list.
        :exc:`NotFound`
            The specified custom list does not exist.
        """
        await self._http._follow_custom_list(custom_list_id)

    @require_authentication
    async def unfollow_custom_list(self, custom_list_id: str, /) -> None:
        """|coro|

        The method will unfollow a custom list within the MangaDex API.

        Parameters
        -----------
        custom_list_id: :class:`str`
            The UUID relating to the custom list we wish to unfollow.

        Raises
        -------
        :exc:`Forbidden`
            You are not authorized to unfollow this custom list.
        :exc:`NotFound`
            The specified custom list does not exist.
        """
        await self._http._unfollow_custom_list(custom_list_id)

    @require_authentication
    async def get_my_custom_lists(self, *, limit: Optional[int] = 10, offset: int = 0) -> CustomListCollection:
        """|coro|

        This method will get the current authenticated user's custom list.

        Parameters
        -----------
        limit: Optional[:class:`int`]
            Defaults to 10. The amount of custom lists to return in one request.
        offset: :class:`int`
            Defaults to 0. The pagination offset.


        .. note::
            Passing ``None`` to ``limit`` will attempt to retrieve all items in the chapter feed.

        Raises
        -------
        :exc:`Forbidden`
            The request returned an error due to authentication failure.

        Returns
        --------
        :class:`~hondana.CustomListCollection`
            A returned collection of custom lists.
        """
        inner_limit = limit or 10

        lists = []

        while True:
            data = await self._http._get_my_custom_lists(limit=inner_limit, offset=offset)
            lists.extend([CustomList(self._http, item) for item in data["data"]])

            offset += inner_limit
            if not data["data"] or offset >= 10_000 or limit is not None:
                break

        return CustomListCollection(self._http, data, lists)

    @require_authentication
    async def get_users_custom_lists(
        self, user_id: str, /, *, limit: Optional[int] = 10, offset: int = 0
    ) -> CustomListCollection:
        """|coro|

        This method will retrieve another user's custom lists.

        Parameters
        -----------
        user_id: :class:`str`
            The UUID of the user whose lists we wish to retrieve.
        limit: Optional[:class:`int`]
            Defaults to 10. The amount of custom lists to return in one request.
        offset: :class:`int`
            Defaults to 0. The pagination offset.


        .. note::
            Passing ``None`` to ``limit`` will attempt to retrieve all items in the chapter feed.

        Raises
        -------
        :exc:`Forbidden`
            The request returned an error due to authentication failure.

        Returns
        --------
        :class:`~hondana.CustomListCollection`
            A returned collection of custom lists.
        """
        inner_limit = limit or 10

        lists = []

        while True:
            data = await self._http._get_users_custom_lists(user_id, limit=inner_limit, offset=offset)
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
        limit: Optional[int] = 100,
        offset: int = 0,
        translated_language: Optional[list[common.LanguageCode]] = None,
        original_language: Optional[list[common.LanguageCode]] = None,
        excluded_original_language: Optional[list[common.LanguageCode]] = None,
        content_rating: Optional[list[ContentRating]] = None,
        excluded_groups: Optional[list[str]] = None,
        excluded_uploaders: Optional[list[str]] = None,
        include_future_updates: Optional[bool] = None,
        created_at_since: Optional[datetime.datetime] = None,
        updated_at_since: Optional[datetime.datetime] = None,
        published_at_since: Optional[datetime.datetime] = None,
        order: Optional[FeedOrderQuery] = None,
        includes: Optional[ChapterIncludes] = ChapterIncludes(),
        include_empty_pages: Optional[bool] = None,
        include_future_publish_at: Optional[bool] = None,
        include_external_url: Optional[bool] = None,
    ) -> ChapterFeed:
        """|coro|

        This method returns the specified manga's chapter feed.

        Parameters
        -----------
        custom_list_id: :class:`str`
            The UUID of the custom list whose feed we are requesting.
        limit: Optional[:class:`int`]
            Defaults to 100. The maximum amount of chapters to return in the response.
        offset: :class:`int`
            Defaults to 0. The pagination offset for the request.
        translated_language: List[:class:`~hondana.types.common.LanguageCode`]
            A list of language codes to filter the returned chapters with.
        original_language: List[:class:`~hondana.types.common.LanguageCode`]
            A list of language codes to filter the original language of the returned chapters with.
        excluded_original_language: List[:class:`~hondana.types.common.LanguageCode`]
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
        -------
        :exc:`BadRequest`
            The query parameters were malformed.
        :exc:`Unauthorized`
            The request was performed with no authorization.
        :exc:`Forbidden`
            You are not authorized to request this feed.
        :exc:`NotFound`
            The specified custom list was not found.

        Returns
        --------
        :class:`~hondana.ChapterFeed`
            Returns a collections of chapters.
        """
        inner_limit = limit or 100

        chapters = []

        while True:
            data = await self._http._custom_list_manga_feed(
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
                includes=includes,
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
        website: Optional[str] = None,
        irc_server: Optional[str] = None,
        irc_channel: Optional[str] = None,
        discord: Optional[str] = None,
        contact_email: Optional[str] = None,
        description: Optional[str] = None,
        twitter: Optional[str] = None,
        manga_updates: Optional[str] = None,
        inactive: Optional[bool] = None,
        publish_delay: Optional[Union[str, datetime.timedelta]] = None,
    ) -> ScanlatorGroup:
        """|coro|

        This method will create a scanlation group within the MangaDex API.

        Parameters
        -----------
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
        -------
        :exc:`BadRequest`
            The request body was malformed.
        :exc:`Forbidden`
            You are not authorized to create scanlation groups.

        Returns
        --------
        :class:`~hondana.ScanlatorGroup`
            The group returned from the API on creation.
        """
        data = await self._http._create_scanlation_group(
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
        includes: Optional[ScanlatorGroupIncludes] = ScanlatorGroupIncludes(),
    ) -> ScanlatorGroup:
        """|coro|

        This method will get a scanlation group from the MangaDex API.

        Parameters
        -----------
        scanlation_group_id: :class:`str`
            The UUID relating to the scanlation group you wish to fetch.
        includes: Optional[:class:`~hondana.query.ScanlatorGroupIncludes`]
            The list of optional includes we request the data for.
            Defaults to all possible expansions

        Raises
        -------
        :exc:`Forbidden`
            You are not authorized to view this scanlation group.
        :exc:`NotFound`
            The scanlation group was not found.

        Returns
        --------
        :class:`~hondana.ScanlatorGroup`
            The group returned from the API.
        """
        data = await self._http._view_scanlation_group(scanlation_group_id, includes=includes)
        return ScanlatorGroup(self._http, data["data"])

    @require_authentication
    async def update_scanlation_group(
        self,
        scanlation_group_id: str,
        /,
        *,
        name: Optional[str] = None,
        leader: Optional[str] = None,
        members: Optional[list[str]] = None,
        website: Optional[str] = MISSING,
        irc_server: Optional[str] = MISSING,
        irc_channel: Optional[str] = MISSING,
        discord: Optional[str] = MISSING,
        contact_email: Optional[str] = MISSING,
        description: Optional[str] = MISSING,
        twitter: Optional[str] = MISSING,
        manga_updates: Optional[str] = MISSING,
        focused_languages: list[common.LanguageCode] = MISSING,
        inactive: Optional[bool] = None,
        locked: Optional[bool] = None,
        publish_delay: Optional[Union[str, datetime.timedelta]] = None,
        version: int,
    ) -> ScanlatorGroup:
        """|coro|

        This method will update a scanlation group within the MangaDex API.

        Parameters
        -----------
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
        focused_languages: Optional[List[:class:`~hondana.types.common.LanguageCode`]]
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
            The ``website``, ``irc_server``, ``irc_channel``, ``discord``, ``contact_email``, ``description``, ``twitter``, ``manga_updates`` and ``focused_language``
            keys are all nullable in the API. To do so please pass ``None`` explicitly to these keys.

        .. note::
            The ``publish_delay`` parameter must match the :class:`hondana.utils.MANGADEX_TIME_REGEX` pattern
            or be a valid ``datetime.timedelta``.

        Raises
        -------
        :exc:`BadRequest`
            The request body was malformed
        :exc:`Forbidden`
            You are not authorized to update this scanlation group.
        :exc:`NotFound`
            The passed scanlation group ID cannot be found.

        Returns
        --------
        :class:`ScanlatorGroup`
            The group returned from the API after its update.
        """
        data = await self._http._update_scanlation_group(
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
        -----------
        scanlation_group_id: :class:`str`
            The UUID relating to the scanlation group you wish to delete.

        Raises
        -------
        :exc:`Forbidden`
            You are not authorized to delete this scanlation group.
        :exc:`NotFound`
            The scanlation group cannot be found, likely due to an incorrect ID.
        """
        await self._http._delete_scanlation_group(scanlation_group_id)

    @require_authentication
    async def follow_scanlation_group(self, scanlation_group_id: str, /) -> None:
        """|coro|

        This method will delete a scanlation group.

        Parameters
        -----------
        scanlation_group_id: :class:`str`
            The UUID relating to the scanlation group you wish to follow.

        Raises
        -------
        :exc:`NotFound`
            The scanlation group cannot be found, likely due to an incorrect ID.
        """
        await self._http._follow_scanlation_group(scanlation_group_id)

    @require_authentication
    async def unfollow_scanlation_group(self, scanlation_group_id: str, /) -> None:
        """|coro|

        This method will delete a scanlation group.

        Parameters
        -----------
        scanlation_group_id: :class:`str`
            The UUID relating to the scanlation group you wish to unfollow.

        Raises
        -------
        :exc:`NotFound`
            The scanlation group cannot be found, likely due to an incorrect ID.
        """
        await self._http._unfollow_scanlation_group(scanlation_group_id)

    async def author_list(
        self,
        *,
        limit: Optional[int] = 10,
        offset: int = 0,
        ids: Optional[list[str]] = None,
        name: Optional[str] = None,
        order: Optional[AuthorListOrderQuery] = None,
        includes: Optional[AuthorIncludes] = AuthorIncludes(),
    ) -> AuthorCollection:
        """|coro|

        This method will fetch a list of authors from the MangaDex API.

        Parameters
        -----------
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
        -------
        :exc:`BadRequest`
            The request payload was malformed.
        :exc:`Forbidden`
            The request failed due to authentication failure.

        Returns
        --------
        :class:`~hondana.AuthorCollection`
            A returned collection of authors.
        """
        inner_limit = limit or 10

        authors = []

        while True:
            data = await self._http._author_list(
                limit=inner_limit, offset=offset, ids=ids, name=name, order=order, includes=includes
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
        biography: Optional[common.LocalizedString] = None,
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
        -----------
        name: :class:`str`
            The name of the author we are creating.
        biography: Optional[:class:`~hondana.types.common.LocalizedString`]
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
        -------
        :exc:`BadRequest`
            The request body was malformed.
        :exc:`Forbidden`
            You are not authorized to create authors.

        Returns
        --------
        :class:`~hondana.Author`
            The author created within the API.
        """
        data = await self._http._create_author(
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

    async def get_author(self, author_id: str, /, *, includes: Optional[AuthorIncludes] = AuthorIncludes()) -> Author:
        """|coro|

        The method will fetch an Author from the MangaDex API.


        .. note::
            MangaDex does not differentiate types of Artist/Author. The endpoint is the same for both.

        Parameters
        -----------
        author_id: :class:`str`
            The ID of the author we are fetching.
        includes: Optional[:class:`~hondana.query.AuthorIncludes`]
            The optional extra data we are requesting from the API.
            Defaults to all possible expansions.

        Raises
        -------
        :exc:`NotFound`
            The passed author ID was not found, likely due to an incorrect ID.

        Returns
        --------
        :class:`~hondana.Author`
            The Author returned from the API.
        """
        data = await self._http._get_author(author_id, includes=includes)

        return Author(self._http, data["data"])

    async def get_artist(self, artist_id: str, /, *, includes: Optional[ArtistIncludes] = ArtistIncludes()) -> Artist:
        """|coro|

        The method will fetch an artist from the MangaDex API.


        .. note::
            MangaDex does not differentiate types of Artist/Author. The endpoint is the same for both.

        Parameters
        -----------
        artist_id: :class:`str`
            The ID of the author we are fetching.
        includes: Optional[:class:`~hondana.query.AuthorIncludes`]
            The optional extra data we are requesting from the API.
            Defaults to all possible expansions.

        Raises
        -------
        :exc:`NotFound`
            The passed artist ID was not found, likely due to an incorrect ID.

        Returns
        --------
        :class:`~hondana.Artist`
            The Author returned from the API.
        """
        data = await self._http._get_artist(artist_id, includes=includes)

        return Artist(self._http, data["data"])

    @require_authentication
    async def update_author(
        self,
        author_id: str,
        /,
        *,
        name: Optional[str] = None,
        biography: Optional[common.LocalizedString] = None,
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
        -----------
        author_id: :class:`str`
            The UUID relating to the author we wish to update.
        name: Optional[:class:`str`]
            The new name to update the author with.
        biography: Optional[:class:`~hondana.types.common.LocalizedString`]
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
        -------
        :exc:`BadRequest`
            The request body was malformed.
        :exc:`Forbidden`
            You are not authorized to update this author.
        :exc:`NotFound`
            The author UUID given was not found.

        Returns
        --------
        :class:`~hondana.Author`
            The updated author from the API.
        """
        data = await self._http._update_author(
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
        -----------
        author_id: :class:`str`
            The UUID relating the author you wish to delete.

        Raises
        -------
        :exc:`Forbidden`
            You are not authorized to delete this author.
        :exc:`NotFound`
            The UUID given for the author was not found.
        """
        await self._http._delete_author(author_id)

    @require_authentication
    async def get_my_reports(
        self,
        *,
        limit: int = 10,
        offset: int = 0,
        object_id: Optional[str] = None,
        reason: Optional[ReportReason] = None,
        category: Optional[ReportCategory] = None,
        status: Optional[ReportStatus] = None,
        order: Optional[ReportListOrderQuery] = None,
        includes: Optional[UserReportIncludes] = None,
    ) -> UserReportCollection:
        data = await self._http._get_reports_current_user(
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
        -----------
        details: :class:`~hondana.ReportDetails`
            The details of the report.

        Raises
        -------
        :exc:`BadRequest`
            The request body was malformed.
        :exc:`Forbidden`
            The request returned a response due to authentication failure.
        :exc:`NotFound`
            The specified report UUID or object UUID does not exist.
        """
        await self._http._create_report(details=details)

    @require_authentication
    async def get_my_manga_ratings(self, manga_ids: list[str], /) -> list[MangaRating]:
        """|coro|

        This method will return your personal manga ratings for the given manga.

        Parameters
        -----------
        manga_ids: List[:class:`str`]
            The IDs of the manga you wish to fetch your ratings for.

        Raises
        -------
        :exc:`Forbidden`
            Failed response due to authentication failure.
        :exc:`NotFound`
            A given manga id was not found or does not exist.

        Returns
        --------
        List[:class:`~hondana.MangaRating`]
        """
        data = await self._http._get_my_ratings(manga_ids)

        ratings = data["ratings"]

        return [MangaRating(self._http, id_, stats) for id_, stats in ratings.items()]

    @require_authentication
    async def set_manga_rating(self, manga_id: str, /, *, rating: int) -> None:
        """|coro|

        This method will set your rating on the passed manga.
        This method **overwrites** your previous set rating, if any.

        Parameters
        -----------
        manga_id: :class:`str`
            The manga you are setting the rating for.
        rating: :class:`int`
            The rating value, between 1 and 10.

        Raises
        -------
        :exc:`Forbidden`
            The request returned a response due to authentication failure.
        :exc:`NotFound`
            The specified manga UUID was not found or does not exist.
        """
        await self._http._set_manga_rating(manga_id, rating=rating)

    @require_authentication
    async def delete_manga_rating(self, manga_id: str, /) -> None:
        """|coro|

        This method will delete your set rating on the passed manga.

        Parameters
        -----------
        manga_id: :class:`str`
            The manga you wish to delete the rating for.

        Raises
        -------
        :exc:`Forbidden`
            The request returned a response due to authentication failure.
        :exc:`NotFound`
            The specified manga UUID was not found or does not exist.
        """
        await self._http._delete_manga_rating(manga_id)

    async def get_manga_statistics(self, manga_id: str, /) -> MangaStatistics:
        """|coro|

        This method will return the statistics for the passed manga.

        Parameters
        -----------
        manga_id: :class:`str`
            The manga id to fetch the statistics for.

        Returns
        ---------
        :class:`~hondana.MangaStatistics`
        """
        data = await self._http._get_manga_statistics(manga_id)

        key = next(iter(data["statistics"]))
        return MangaStatistics(self._http, key, data["statistics"][key])

    async def find_manga_statistics(self, manga_ids: list[str], /) -> list[MangaStatistics]:
        """|coro|

        This method will return the statistics for the passed manga.

        Parameters
        -----------
        manga_ids: List[:class:`str`]
            The list of manga IDs to fetch the statistics for.

        Returns
        ---------
        List[:class:`~hondana.MangaStatistics`]
        """
        data = await self._http._find_manga_statistics(manga_ids)

        return [MangaStatistics(self._http, id_, stats) for id_, stats in data["statistics"].items()]

    @require_authentication
    async def abandon_upload_session(self, session_id: str, /) -> None:
        """|coro|

        This method will abandon an existing upload session.

        Parameters
        -----------
        session_id: :class:`str`
            The upload
        """
        await self._http._abandon_upload_session(session_id)

    @require_authentication
    def upload_session(
        self,
        manga: Union[Manga, str],
        /,
        *,
        chapter: str,
        chapter_to_edit: Optional[Union[Chapter, str]] = None,
        volume: Optional[str] = None,
        title: Optional[str] = None,
        translated_language: common.LanguageCode,
        scanlator_groups: list[str],
        external_url: Optional[str] = None,
        publish_at: Optional[datetime.datetime] = None,
        existing_upload_session_id: Optional[str] = None,
        version: Optional[int] = None,
    ) -> ChapterUpload:
        """
        This method will return an async `context manager <https://realpython.com/python-with-statement/>`_ to handle some upload session management.


        Examples
        ---------

        Using the async context manager: ::

            async with Client.upload_session(
                manga,
                chapter=chapter,
                volume=volume,
                title=title,
                translated_language=translated_language,
                scanlator_groups=scanlator_groups
            ) as session:
                await session.upload_images(your_list_of_bytes)


        Parameters
        -----------
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
        translated_language: :class:`~hondana.types.common.LanguageCode`
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


        .. note::
            The ``external_url`` parameter requires an explicit permission on MangaDex to set.

        Returns
        --------
        :class:`~hondana.ChapterUpload`
        """
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
        )

    @require_authentication
    async def upload_chapter(
        self,
        manga: Union[Manga, str],
        /,
        *,
        chapter: str,
        chapter_to_edit: Optional[Union[Chapter, str]] = None,
        volume: Optional[str] = None,
        title: Optional[str] = None,
        translated_language: common.LanguageCode,
        scanlator_groups: list[str],
        external_url: Optional[str] = None,
        publish_at: Optional[datetime.datetime] = None,
        existing_upload_session_id: Optional[str] = None,
        version: Optional[int] = None,
        images: list[pathlib.Path],
    ) -> Chapter:
        """|coro|

        This method will perform the chapter upload for you, providing a list of images.

        Parameters
        -----------
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
        translated_language: :class:`~hondana.types.common.LanguageCode`
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
        images: List[:class:`pathlib.Path`]
            The list of images to upload as their Paths.


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
            I personally advise the `context manager <https://realpython.com/python-with-statement/>`_ method as it allows more control over your upload session.
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
            version=version,
        ) as session:
            await session.upload_images(images)
            new_chapter = await session.commit()

        return new_chapter

    @require_authentication
    async def get_latest_settings_template(self) -> dict[str, Any]:
        """|coro|

        This method will return the json object of the latest settings template.

        Currently, there is no formatting done on this key as the api has not documented it.

        Returns
        --------
        Dict[:class:`str`, :class:`Any`]
            The settings template.
        """

        return await self._http._get_latest_settings_template()

    @require_authentication
    async def get_specific_template_version(self, version: str) -> dict[str, Any]:
        """|coro|

        This method will return a specific setting template version.

        Parameters
        -----------
        version: :class:`str`
            The UUID relating to the specified template.

        Raises
        -------
        :exc:`Forbidden`
            The request failed due to authentication issues.
        :exc:`NotFound`
            The specified template was not found.

        Returns
        --------
        Dict[:class:`str`, :class:`Any`]
            The returned settings template.
        """

        data = await self._http._get_specific_template_version(version)

        return data

    @require_authentication
    async def get_my_settings(self) -> SettingsPayload:
        """|coro|

        This method will return the current logged-in user's settings.

        Raises
        -------
        :exc:`Forbidden`
            The request failed due to authentication issues.
        :exc:`NotFound`
            The logged-in user's settings were not found.

        Returns
        --------
        :class:`hondana.types.settings.SettingsPayload`
            The user's settings.
        """
        data = await self._http._get_user_settings()

        return data

    @require_authentication
    async def upsert_user_settings(
        self, payload: Settings, updated_at: Optional[datetime.datetime] = None
    ) -> SettingsPayload:
        """|coro|

        This method will update or create user settings based on a formatted settings templates.

        Parameters
        -----------
        payload: :class:`hondana.types.settings.Settings`
            A payload representing the settings.
        updated_at: :class:`datetime.datetime`
            The datetime at which you updated the settings.
            Defaults to a UTC datetime for "now".

        Raises
        -------
        :exc:`Forbidden`
            The request failed due to authentication issues.
        :exc:`NotFound`
            The logged-in user's settings were not found.

        Returns
        --------
        :class:`~hondana.types.settings.SettingsPayload`
            The returned (and created) payload.
        """

        time = updated_at or datetime.datetime.now(datetime.timezone.utc)
        data = await self._http._upsert_user_settings(payload, updated_at=time)

        return data
