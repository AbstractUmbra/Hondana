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
from typing import TYPE_CHECKING, Optional, Union, overload

from aiohttp import ClientSession

from . import errors
from .author import Author
from .chapter import Chapter
from .cover import Cover
from .http import HTTPClient
from .legacy import LegacyItem
from .manga import Manga
from .scanlator_group import ScanlatorGroup
from .user import User
from .utils import MISSING, require_authentication


if TYPE_CHECKING:
    from .tags import QueryTags
    from .types import (
        author,
        chapter,
        common,
        cover,
        legacy,
        manga,
        scanlator_group,
        user,
    )
    from .types.query import OrderQuery

_PROJECT_DIR = pathlib.Path(__file__)


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
    ) -> None:
        ...

    def __init__(
        self,
        *,
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        session: Optional[ClientSession] = None,
    ) -> None:
        self._http = HTTPClient(username=username, email=email, password=password, session=session)

    @overload
    def login(self, *, username: str = ..., email: None = ..., password: str) -> None:
        ...

    @overload
    def login(self, *, username: None = ..., email: str = ..., password: str) -> None:
        ...

    def login(self, *, username: Optional[str] = None, email: Optional[str] = None, password: str) -> None:
        """A method to add authentication details to the client post-creation.

        Parameters
        -----------
        login: Optional[:class:`str`]
            The login username to authenticate to the API.
        email: Optional[:class:`str`]
            The login email to authenticate to the API.
        password: :class:`str`
            The password to authenticate to the API.
        """
        if username is None and email is None:
            raise ValueError("An email or username must be passed.")

        self._http.username = username
        self._http.email = email
        self._http.password = password
        self._http._authenticated = True

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
        data = await self._http._update_tags()

        tags: dict[str, str] = {}

        for tag in data:
            name_key = tag["data"]["attributes"]["name"]
            name = name_key.get("en", next(iter(name_key))).title()
            tags[name] = tag["data"]["id"]

        path = _PROJECT_DIR.parent / "extras" / "tags.json"
        with open(path, "w") as fp:
            json.dump(tags, fp, indent=4)

        return tags

    async def get_author(self, author_id: str) -> Author:
        """|coro|

        The method will fetch an Author from the MangaDex API.

        Raises
        -------
        NotFound
            The passed author ID was not found, likely due to an incorrect ID.

        Returns
        --------
        :class:`Author`
            The Author returned from the API.
        """
        data = await self._http._get_author(author_id)

        return Author(self._http, data)

    @require_authentication
    async def get_my_feed(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        translated_languages: Optional[list[str]] = None,
        created_at_since: Optional[datetime.datetime] = None,
        updated_at_since: Optional[datetime.datetime] = None,
        published_at_since: Optional[datetime.datetime] = None,
        order: Optional[OrderQuery] = None,
    ) -> list[Chapter]:
        """|coro|

        This method will retrieve the logged in user's followed manga chapter feed.

        Parameters
        -----------
        limit: :class:`int`
            Defaults to 100. This is the limit of manga that is returned in this request,
            it is clamped at 500 as that is the max in the API.
        offset: :class:`int`
            Defaults to 0. This is the pagination offset, the number must be greater than 0.
            If set lower than 0 then it is set to 0.
        translated_languages: Optional[list[:class:`str`]]
            A list of language codes to return chapters for.
        created_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their creation date.
        updated_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their update date.
        published_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their published date.
        order: Optional[:class:`~hondana.types.OrderQuery`]
            A query parameter to choose the 'order by' response from the API.


        .. note::
            If no start point is given with the `created_at_since`, `updated_at_since` or `published_at_since` parameters,
            then the API will return oldest first based on creation date.

        Raises
        -------
        BadRequest
            The query parameters were not valid.

        Returns
        --------
        List[:class:`Chapter`]
            Returns a list of Chapter instances.
        """

        limit = min(max(1, limit), 500)
        if offset < 0:
            offset = 0

        data = await self._http._manga_feed(
            None,
            limit=limit,
            offset=offset,
            translated_languages=translated_languages,
            created_at_since=created_at_since,
            updated_at_since=updated_at_since,
            published_at_since=published_at_since,
            order=order,
            includes=None,
        )

        chapters: list[Chapter] = []
        for item in data["results"]:
            chapters.append(Chapter(self._http, item))

        return chapters

    async def manga_list(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        title: Optional[str] = None,
        authors: Optional[list[str]] = None,
        artists: Optional[list[str]] = None,
        year: Optional[int] = None,
        included_tags: Optional[QueryTags] = None,
        excluded_tags: Optional[QueryTags] = None,
        status: Optional[list[manga.MangaStatus]] = None,
        original_language: Optional[list[str]] = None,
        publication_demographic: Optional[list[manga.PublicationDemographic]] = None,
        ids: Optional[list[str]] = None,
        content_rating: Optional[list[manga.ContentRating]] = None,
        created_at_since: Optional[datetime.datetime] = None,
        updated_at_since: Optional[datetime.datetime] = None,
        order: Optional[OrderQuery] = None,
        includes: Optional[list[manga.MangaIncludes]] = ["author", "artist", "cover_art"],
    ) -> list[Manga]:
        """|coro|

        This method will perform a search based on the passed query parameters for manga.

        Parameters
        -----------
        limit: :class:`int`
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
        status: Optional[List[:class:`~hondana.types.MangaStatus`]]
            The status(es) of manga to include in the search.
        original_language: Optional[:class:`str`]
            A list of language codes to include for the manga's original language.
            i.e. ``["en"]``
        publication_demographic: Optional[List[:class:`~hondana.types.PublicationDemographic`]]
            The publication demographic(s) to limit the search to.
        ids: Optional[:class:`str`]
            A list of manga UUID(s) to limit the search to.
        content_rating: Optional[List[:class:`~hondana.types.ContentRating`]]
            The content rating(s) to filter the search to.
        created_at_since: Optional[datetime.datetime]
            A (naive UTC) datetime instance we specify for searching.
            Used for returning manga created *after* this date.
        updated_at_since: Optional[datetime.datetime]
            A (naive UTC) datetime instance we specify for searching.
            Used for returning manga updated *after* this date.
        order: Optional[:class:`~hondana.types.OrderQuery`]
            A query parameter to choose the ordering of the response
            i.e. ``{"createdAt": "desc"}``
        includes: Optional[List[:class:`~hondana.types.MangaIncludes`]]
            A list of things to include in the returned manga response payloads.
            i.e. ``["author", "cover_art", "artist"]``
            Defaults to these values.

        Raises
        -------
        BadRequest
            The query parameters were not valid.

        Returns
        --------
        List[Manga]
            Returns a list of Manga instances.
        """
        limit = min(max(1, limit), 500)
        if offset < 0:
            offset = 0

        data = await self._http._manga_list(
            limit=limit,
            offset=offset,
            title=title,
            authors=authors,
            artists=artists,
            year=year,
            included_tags=included_tags,
            excluded_tags=excluded_tags,
            status=status,
            original_language=original_language,
            publication_demographic=publication_demographic,
            ids=ids,
            content_rating=content_rating,
            created_at_since=created_at_since,
            updated_at_since=updated_at_since,
            order=order,
            includes=includes,
        )

        manga: list[Manga] = []
        for item in data["results"]:
            manga.append(Manga(self._http, item))

        return manga

    @require_authentication
    async def create_manga(
        self,
        *,
        title: common.LocalisedString,
        alt_titles: Optional[list[common.LocalisedString]] = None,
        description: Optional[common.LocalisedString] = None,
        authors: Optional[list[str]] = None,
        artists: Optional[list[str]] = None,
        links: Optional[manga.MangaLinks] = None,
        original_language: Optional[str] = None,
        last_volume: Optional[str] = None,
        last_chapter: Optional[str] = None,
        publication_demographic: Optional[manga.PublicationDemographic] = None,
        status: Optional[manga.MangaStatus] = None,
        year: Optional[int] = None,
        content_rating: manga.ContentRating,
        tags: Optional[QueryTags] = None,
        mod_notes: Optional[str] = None,
        version: int,
    ) -> Manga:
        """|coro|

        This method will create a Manga within the MangaDex API for you.

        Parameters
        -----------
        title: :class:`~hondana.types.LocalisedString`
            The manga titles in the format of ``language_key: title``
            i.e. ``{"en": "Some Manga Title"}``
        alt_titles: Optional[List[:class:`~hondana.types.LocalisedString`]]
            The alternative titles in the format of ``language_key: title``
            i.e. ``[{"en": "Some Other Title"}, {"fr": "Un Autre Titre"}]``
        description: Optional[:class:`~hondana.types.LocalisedString`]
            The manga description in the format of ``language_key: description``
            i.e. ``{"en": "My amazing manga where x y z happens"}``
        authors: Optional[List[:class:`str`]]
            The list of author UUIDs to credit to this manga.
        artists: Optional[List[:class:`str`]]
            The list of artist UUIDs to credit to this manga.
        links: Optional[:class:`~hondana.types.MangaLinks`]
            The links relevant to the manga.
            See here for more details: https://api.mangadex.org/docs.html#section/Static-data/Manga-links-data
        original_language: Optional[:class:`str`]
            The language key for the original language of the manga.
        last_volume: Optional[:class:`str`]
            The last volume to attribute to this manga.
        last_chapter: Optional[:class:`str`]
            The last chapter to attribute to this manga.
        publication_demographic: Optional[:class:`~hondana.types.PublicationDemographic`]
            The target publication demographic of this manga.
        status: Optional[:class:`~hondana.types.MangaStatus`]
            The status of the manga.
        year: Optional[:class:`int`]
            The release year of the manga.
        content_rating: :class:`~hondana.types.ContentRating`
            The content rating of the manga.
        tags: Optional[:class:`QueryTags`]
            The QueryTags instance for the list of tags to attribute to this manga.
        mod_notes: Optional[:class:`str`]
            The moderator notes to add to this Manga.
        version: :class:`int`
            The revision version of this manga.


        .. note::
            The ``mod_notes`` parameter requires the logged in user to be a MangaDex moderator.
            Leave this as ``None`` unless you fit this criteria.

        Raises
        -------
        BadRequest
            The query parameters were not valid.
        Forbidden
            The query failed due to authorization failure.

        Returns
        --------
        :class:`Manga`
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
            version=version,
        )

        return Manga(self._http, data)

    async def get_manga_volumes_and_chapters(
        self, *, manga_id: str, translated_language: Optional[list[str]] = None
    ) -> manga.GetMangaVolumesAndChaptersResponse:
        """|coro|

        This endpoint returns the raw relational mapping of a manga's volumes and chapters.

        Parameters
        -----------
        manga_id: :class:`str`
            The manga UUID we are querying against.
        translated_language: Optional[List[:class:`str`]]
            The list of language codes you want to limit the search to.

        Returns
        --------
        :class:`hondana.types.GetMangaVolumesAndChaptersResponse`
            The raw payload from mangadex. There is not guarantee of the keys here.
        """
        data = await self._http._get_manga_volumes_and_chapters(manga_id=manga_id, translated_languages=translated_language)

        return data

    async def view_manga(
        self, manga_id: str, includes: Optional[list[manga.MangaIncludes]] = ["author", "artist", "cover_art"]
    ) -> Manga:
        """|coro|

        The method will fetch a Manga from the MangaDex API.

        Parameters
        -----------
        includes: Optional[Literal[``"author"``, ``"artist"``, ``"cover_art"``]]
            This is a list of items to include in the query.
            Be default we request all optionals (artist, cover_art and author).
            Pass a new list of these strings to overwrite it.

        Raises
        -------
        Forbidden
            The query failed due to authorization failure.
        NotFound
            The passed manga ID was not found, likely due to an incorrect ID.

        Returns
        --------
        :class:`Manga`
            The Manga that was returned from the API.
        """
        data = await self._http._view_manga(manga_id, includes)

        return Manga(self._http, data)

    @require_authentication
    async def update_manga(
        self,
        manga_id: str,
        *,
        title: Optional[common.LocalisedString] = None,
        alt_titles: Optional[list[common.LocalisedString]] = None,
        description: Optional[common.LocalisedString] = None,
        authors: Optional[list[str]] = None,
        artists: Optional[list[str]] = None,
        links: Optional[manga.MangaLinks] = None,
        original_language: Optional[str] = None,
        last_volume: Optional[str] = MISSING,
        last_chapter: Optional[str] = MISSING,
        publication_demographic: Optional[manga.PublicationDemographic] = MISSING,
        status: Optional[manga.MangaStatus] = MISSING,
        year: Optional[int] = MISSING,
        content_rating: Optional[manga.ContentRating] = None,
        tags: Optional[QueryTags] = None,
        mod_notes: Optional[str] = MISSING,
        version: int,
    ) -> Manga:
        """|coro|

        This method will update a Manga within the MangaDex API.

        Parameters
        -----------
        manga_id: :class:`str`
            The UUID of the manga to update.
        title: Optional[:class:`~hondana.types.LocalisedString`]
            The manga titles in the format of ``language_key: title``
        alt_titles: Optional[List[:class:`~hondana.types.LocalisedString`]]
            The alternative titles in the format of ``language_key: title``
        description: Optional[:class:`~hondana.types.LocalisedString`]
            The manga description in the format of ``language_key: description``
        authors: Optional[List[:class:`str`]]
            The list of author UUIDs to credit to this manga.
        artists: Optional[List[:class:`str`]]
            The list of artist UUIDs to credit to this manga.
        links: Optional[:class:`~hondana.types.MangaLinks`]
            The links relevant to the manga.
        original_language: Optional[:class:`str`]
            The language key for the original language of the manga.
        last_volume: Optional[:class:`str`]
            The last volume to attribute to this manga.
        last_chapter: Optional[:class:`str`]
            The last chapter to attribute to this manga.
        publication_demographic: :class:`~hondana.types.PublicationDemographic`
            The target publication demographic of this manga.
        status: Optional[:class:`~hondana.types.MangaStatus`]
            The status of the manga.
        year: Optional[:class:`int`]
            The release year of the manga.
        content_rating: Optional[:class:`~hondana.types.ContentRating`]
            The content rating of the manga.
        tags: Optional[:class:`QueryTags`]
            The QueryTags instance for the list of tags to attribute to this manga.
        mod_notes: Optional[:class:`str`]
            The moderator notes to add to this Manga.
        version: :class:`int`
            The revision version of this manga.


        .. note::
            The ``mod_notes`` parameter requires the logged in user to be a MangaDex moderator.
            Leave this as the default unless you fit this criteria.

        .. note::
            The ``last_volume``, ``last_chapter``, ``publication_demographic``, ``status``, ``year`` and ``mod_notes`` parameters
            are nullable in the API, to do this please pass ``None``.

        Raises
        -------
        BadRequest
            The query parameters were not valid.
        Forbidden
            The returned an error due to authentication failure.
        NotFound
            The specified manga does not exist.

        Returns
        --------
        :class:`Manga`
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
            mod_notes=mod_notes,
            version=version,
        )

        return Manga(self._http, data)

    @require_authentication
    async def unfollow_manga(self, manga_id: str, /) -> None:
        """|coro|

        This method will unfollow a Manga for the logged in user in the MangaDex API.

        Parameters
        -----------
        manga_id: :class:`str`
            The UUID of the manga to unfollow.

        Raises
        -------
        Forbidden
            The request returned an error due to authentication failure.
        NotFound
            The specified manga does not exist.
        """
        await self._http._unfollow_manga(manga_id)

    @require_authentication
    async def follow_manga(self, manga_id: str, /) -> None:
        """|coro|

        This method will follow a Manga for the logged in user in the MangaDex API.

        Parameters
        -----------
        manga_id: :class:`str`
            The UUID of the manga to unfollow.

        Raises
        -------
        Forbidden
            The request returned an error due to authentication failure.
        NotFound
            The specified manga does not exist.
        """
        await self._http._follow_manga(manga_id)

    async def manga_feed(
        self,
        manga_id: str,
        /,
        *,
        limit: int = 100,
        offset: int = 0,
        translated_languages: Optional[list[str]] = None,
        created_at_since: Optional[datetime.datetime] = None,
        updated_at_since: Optional[datetime.datetime] = None,
        published_at_since: Optional[datetime.datetime] = None,
        order: Optional[manga.MangaOrderQuery] = None,
        includes: Optional[list[manga.MangaIncludes]] = ["author", "artist", "cover_art"],
    ) -> list[Chapter]:
        """|coro|

        This method returns the specified manga's chapter feed.

        Parameters
        -----------
        manga_id: :class:`str`
            The UUID of the manga whose feed we are requesting.
        limit: :class:`int`
            Defaults to 100. The maximum amount of chapters to return in the response.
        offset: :class:`int`
            Defaults to 0. The pagination offset for the request.
        translated_langauges: List[:class:`str`]
            A list of language codes to filter the returned chapters with.
        created_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their creation date.
        updated_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their updated at date.
        published_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their published at date.
        order: Optional[:class:`~hondana.types.MangaOrderQuery`]
            A query parameter to choose how the responses are ordered.
            i.e. ``{"chapters": "desc"}``
        includes: Optional[List[:class:`~hondana.types.MangaIncludes`]]
            The list of options to include increased payloads for per chapter.
            Defaults to these values.

        Raises
        -------
        BadRequest
            The query parameters were malformed.

        Returns
        --------
        List[:class:`Chapter`]
            The list of chapters returned from this request.
        """
        data = await self._http._manga_feed(
            manga_id,
            limit=limit,
            offset=offset,
            translated_languages=translated_languages,
            created_at_since=created_at_since,
            updated_at_since=updated_at_since,
            published_at_since=published_at_since,
            order=order,
            includes=includes,
        )

        return [Chapter(self._http, item) for item in data["results"]]

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
        Union[:class:`~hondana.types.MangaReadMarkersResponse`, :class:`~hondana.types.MangaGroupedReadMarkersResponse`]
        """
        if len(manga_ids) == 1:
            return await self._http._manga_read_markers(manga_ids, grouped=False)
        return await self._http._manga_read_markers(manga_ids, grouped=True)

    async def get_random_manga(
        self, *, includes: Optional[list[manga.MangaIncludes]] = ["author", "artist", "cover_art"]
    ) -> Manga:
        """|coro|

        This method will return a random manga from the MangaDex API.

        Parameters
        -----------
        includes: Optional[List[Literal[``"author"``, ``"artist"``, ``"cover_art"``]]]
            The optional includes for the manga payload.
            Defaults to all three.
        """
        data = await self._http._get_random_manga(includes=includes)

        return Manga(self._http, data)

    @require_authentication
    async def get_manga_reading_status(self, manga_id: str, /) -> manga.MangaReadingStatusResponse:
        """|coro|

        This method will return the current reading status for the specified manga.

        Parameters
        -----------
        manga_id: :class:`str`
            The UUID associated with the manga you wish to query.

        Raises
        -------
        Forbidden
            You are not authenticated to perform this action.
        NotFound
            The specified manga does not exist, likely due to an incorrect ID.

        Returns
        --------
        :class:`~hondana.types.MangaReadingStatusResponse`
            The raw response from the API on the request.
        """
        return await self._http._get_manga_reading_status(manga_id)

    @require_authentication
    async def update_manga_reading_status(self, manga_id: str, /, *, status: Optional[manga.ReadingStatus]) -> None:
        """|coro|

        This method will update your current reading status for the specified manga.

        Parameters
        -----------
        manga_id: :class:`str`
            The UUID associated with the manga you wish to update.
        status: Optional[:class:`~hondana.types.ReadingStatus`]
            The reading status you wish to update this manga with.


        .. note::
            Leaving ``status`` as the default will remove the manga reading status from the API.
            Please provide a value if you do not wish for this to happen.

        Raises
        -------
        BadRequest
            The query parameters were invalid.
        NotFound
            The specified manga cannot be found, likely due to incorrect ID.
        """

        await self._http._update_manga_reading_status(manga_id, status=status)

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
        Forbidden
            You are not authorised to add manga to this custom list.
        NotFound
            The specified manga or specified custom list are not found, likely due to an incorrect UUID.
        """

        await self._http._add_manga_to_custom_list(manga_id, custom_list_id=custom_list_id)

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
        Forbidden
            You are not authorised to remove a manga from the specified custom list.
        NotFound
            The specified manga or specified custom list are not found, likely due to an incorrect UUID.
        """

        await self._http._remove_manga_from_custom_list(manga_id, custom_list_id=custom_list_id)

    async def chapter_list(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        ids: Optional[list[str]] = None,
        title: Optional[str] = None,
        groups: Optional[list[str]] = None,
        uploader: Optional[str] = None,
        manga: Optional[str] = None,
        volume: Optional[Union[str, list[str]]] = None,
        chapter: Optional[Union[str, list[str]]] = None,
        translated_language: Optional[list[str]] = None,
        created_at_since: Optional[datetime.datetime] = None,
        updated_at_since: Optional[datetime.datetime] = None,
        published_at_since: Optional[datetime.datetime] = None,
        order: Optional[chapter.ChapterOrderQuery] = None,
        includes: Optional[list[manga.MangaIncludes]] = None,
    ) -> list[Chapter]:
        """|coro|

        This method will return a list of published chapters.

        Parameters
        -----------
        limit: :class:`int`
            Defaults to 100. This specifies the amount of chapters to return in one request.
        offset: :class:`int`
            Defaults to 0. This specifies the pagination offset.
        ids: Optional[List[:class:`str`]]
            The list of chapter UUIDs to filter the request with.
        title: Optional[:class:`str`]
            The chapter title query to limit the request with.
        groups: Optional[List[:class:`str`]]
            The scanlation group UUID(s) to limit the request with.
        uploader: Optional[:class:`str`]
            The uploader UUID to limit the request with.
        manga: Optional[:class:`str`]
            The manga UUID to limit the request with.
        volume: Optional[Union[:class:`str`, List[:class:`str`]]]
            The volume UUID or UUIDs to limit the request with.
        chapter: Optional[Union[:class:`str`, List[:class:`str`]]]
            The chapter UUID or UUIDs to limit the request with.
        translated_language: Optional[List[:class:`str`]]
            The list of languages codes to filter the request with.
        created_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their creation date.
        updated_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their updated at date.
        published_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their published at date.
        order: Optional[:class:`~hondana.types.OrderQuery`]
            A query parameter to choose how the responses are ordered.
            i.e. ``{"chapters": "desc"}``
        includes: Optional[List[:class:`~hondana.types.ChapterIncludes`]]
            The list of options to include increased payloads for per chapter.
            Defaults to these values.


        .. note::
            If `order` is not specified then the API will return results first based on their creation date,
            which could lead to unexpected results.

        Raises
        -------
        BadRequest
            The query parameters were malformed
        Forbidden
            The request returned an error to due authentication failure.

        Returns
        --------
        List[:class:`Chapter`]
            The returned chapters from the endpoint.
        """

        data = await self._http._chapter_list(
            limit=limit,
            offset=offset,
            ids=ids,
            title=title,
            groups=groups,
            uploader=uploader,
            manga=manga,
            volume=volume,
            chapter=chapter,
            translated_language=translated_language,
            created_at_since=created_at_since,
            updated_at_since=updated_at_since,
            published_at_since=published_at_since,
            order=order,
            includes=includes,
        )

        return [Chapter(self._http, payload) for payload in data["results"]]

    async def get_chapter(self, chapter_id: str, /, *, includes: Optional[list[chapter.ChapterIncludes]] = None) -> Chapter:
        data = await self._http._get_chapter(chapter_id, includes=includes)

        return Chapter(self._http, data)

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
            chapter_id,
            title=title,
            volume=volume,
            chapter=chapter,
            translated_language=translated_language,
            groups=groups,
            version=version,
        )

        return Chapter(self._http, data)

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
        BadRequest
            The query was malformed.
        Forbidden
            You are not authorized to delete this chapter.
        NotFound
            The UUID passed for this chapter does not related to a chapter in the API.
        """
        await self._http._delete_chapter(chapter_id)

    @require_authentication
    async def mark_chapter_as_read(self, chapter_id: str, /) -> None:
        """|coro|

        This method will mark a chapter as read for the current authenticated user in the MangaDex API.

        Parameters
        -----------
        chapter_id: :class:`str`
            The UUID of the chapter you wish to mark as read.
        """
        await self._http._mark_chapter_as_read(chapter_id)

    @require_authentication
    async def mark_chapter_as_unread(self, chapter_id: str, /) -> None:
        """|coro|

        This method will mark a chapter as unread for the current authenticated user in the MangaDex API.

        Parameters
        -----------
        chapter_id: :class:`str`
            The UUID of the chapter you wish to mark as unread.
        """
        await self._http._mark_chapter_as_unread(chapter_id)

    async def cover_art_list(
        self,
        *,
        limit: int = 10,
        offset: int = 0,
        manga: Optional[list[str]] = None,
        ids: Optional[list[str]] = None,
        uploaders: Optional[list[str]] = None,
        order: Optional[cover.CoverOrderQuery] = None,
        includes: Optional[list[cover.CoverIncludes]] = None,
    ) -> list[Cover]:
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
        order: Optional[:class:`~hondana.types.CoverOrderQuery`]
            A query parameter to choose how the responses are ordered.
        includes: Optional[List[:class:`~hondana.types.CoverIncludes`]]
            An optional list of includes to request increased payloads during the request.

        Raises
        -------
        BadRequest
            The request parameters were malformed.
        Forbidden
            The request returned an error due to authentication failure.

        Returns
        --------
        List[:class:`Cover`]
            A list of Cover instances returned from the API.
        """
        limit = min(max(1, limit), 10)
        if offset < 0:
            offset = 0

        data = await self._http._cover_art_list(
            limit=limit, manga=manga, ids=ids, uploaders=uploaders, order=order, includes=includes
        )

        return [Cover(self._http, payload) for payload in data["results"]]

    async def get_cover(self, cover_id: str, includes: list[str] = ["manga"]) -> Cover:
        """|coro|

        The method will fetch a Cover from the MangaDex API.

        Parameters
        -----------
        cover_id: :class:`str`
            The id of the cover we are fetching from the API.
        includes: List[:class:`str`]
            A list of the additional information to gather related to the Cover.
            defaults to ``["manga"]``


        .. note::
            If you do not include the ``"manga"`` includes, then we will not be able to get the cover url.

        Raises
        -------
        NotFound
            The passed cover ID was not found, likely due to an incorrect ID.

        Returns
        --------
        :class:`Cover`
            The Cover returned from the API.
        """
        data = await self._http._get_cover(cover_id, includes=includes)

        return Cover(self._http, data)

    @require_authentication
    async def edit_cover(
        self, cover_id: str, /, *, volume: Optional[str] = MISSING, description: Optional[str] = MISSING, version: int
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
            The ``volume`` key is mandatory. You can pass ``None`` to null it in the API but it must have a value.

        Raises
        -------
        TypeError
            The volume key was not given a value. This is required.
        BadRequest
            The request body was malformed.
        Forbidden
            The request returned an error due to authentication failure.

        Returns
        --------
        :class:`Cover`
            The returned cover after the edit.
        """
        data = await self._http._edit_cover(cover_id, volume=volume, description=description, version=version)

        return Cover(self._http, data)

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
        BadRequest
            The request payload was malformed.
        Forbidden
            The request returned an error due to authentication.
        """
        await self._http._delete_cover(cover_id)

    async def scanlation_group_list(
        self,
        *,
        limit: int = 10,
        offset: int = 0,
        ids: Optional[list[str]] = None,
        name: Optional[str] = None,
        includes: Optional[list[scanlator_group.ScanlatorGroupIncludes]] = None,
    ) -> list[ScanlatorGroup]:
        """|coro|

        This method will return a list of scanlator groups from the MangaDex API.

        Parameters
        -----------
        limit: :class:`int`
            Defaults to 10. This specifies the amount of scanlator groups to return in one request.
        offset: :class:`int`
            Defaults to 0. The pagination offset.
        ids: Optional[List[:class:`str`]]
            A list of scanlator group UUID(s) to limit the request to.
        name: Optional[:class:`str`]
            A name to limit the request to.
        includes: Optional[List[:class:`~hondana.types.ScanlatorGroupIncludes`]]
            An optional list of includes to request increased payloads during the request.

        Raises
        -------
        BadRequest
            The query parameters were malformed
        Forbidden
            The request returned an error due to authentication failure.

        Returns
        --------
        List[:class:`ScanlatorGroup`]
            A list of scanlator groups returned in the request.
        """
        limit = min(max(1, limit), 100)
        if offset < 0:
            offset = 0

        data = await self._http._scanlation_group_list(limit=limit, offset=offset, ids=ids, name=name, includes=includes)

        return [ScanlatorGroup(self._http, payload) for payload in data["results"]]

    async def author_list(
        self,
        *,
        limit: int = 10,
        offset: int = 0,
        ids: Optional[list[str]] = None,
        name: Optional[str] = None,
        order: Optional[author.AuthorOrderQuery],
        includes: Optional[list[author.AuthorIncludes]],
    ) -> list[Author]:
        """|coro|

        This method will fetch a list of authors from the MangaDex API.

        Parameters
        -----------
        limit: :class:`int`
            Defaults to 10. This specifies the amount of scanlator groups to return in one request.
        offset: :class:`int`
            Defaults to 0. The pagination offset.
        ids: Optional[List[:class:`str`]]
            A list of author UUID(s) to limit the request to.
        name: Optional[:class:`str`]
            A name to limit the request to.
        order: Optional[:class:`~hondana.types.AuthorOrderQuery`]
            A query parameter to choose how the responses are ordered.
        includes: Optional[List[:class:`~hondana.types.AuthorIncludes`]]
            An optional list of includes to request increased payloads during the request.
        """
        data = await self._http._author_list(limit=limit, offset=offset, ids=ids, name=name, order=order, includes=includes)

        return [Author(self._http, payload) for payload in data["results"]]

    @require_authentication
    async def user_list(
        self,
        *,
        limit: int = 10,
        offset: int = 0,
        ids: Optional[list[str]] = None,
        username: Optional[str] = None,
        order: Optional[user.UserOrderQuery] = None,
    ) -> list[User]:
        """|coro|

        This method will return a list of Users from the MangaDex API.

        Parameters
        -----------
        limit: :class:`int`
            Defaults to 10. This specifies the amount of users to return in one request.
        offset: :class:`int`
            Defaults to 0. The pagination offset.
        ids: Optional[List[:class:`str`]]
            A list of User UUID(s) to limit the request to.
        username: Optional[:class:`str`]
            The username to limit this request to.
        order: Optional[:class:`~hondana.types.UserOrderQuery`]
            The optional query param on how the response will be ordered.

        Raises
        -------
        BadRequest
            The request parameters were malformed
        Forbidden
            The request returned an error due to authentication failure.

        Returns
        --------
        List[:class:`User`]
            The list of users returned via this request.
        """
        limit = min(max(1, limit), 100)
        if offset < 0:
            offset = 0

        data = await self._http._user_list(limit=limit, offset=offset, ids=ids, username=username, order=order)

        return [User(self._http, payload) for payload in data["results"]]

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

        return User(self._http, data)

    @require_authentication
    async def delete_user(self, user_id: str, /) -> None:
        """|coro|

        This method will delete a user from the MangaDex API.

        Parameters
        -----------
        user_id: :class:`str`
            The UUID of the user you wish to delete.

        Raises
        -------
        Forbidden
            The response returned an error due to authentication failure.
        NotFound
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
        Forbidden
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
        Forbidden
            The API returned an error due to authentication failure.
        """

        await self._http._update_user_email(email)

    @require_authentication
    async def get_my_details(self) -> User:
        """|coro|

        This method will return the current authenticated user's details.

        Raises
        -------
        Forbidden
            The request returned an error due to authentication failure.
        """
        data = await self._http._get_my_details()

        return User(self._http, data)

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
        Forbidden
            The request returned an error due to authentication failure.

        Returns
        --------
        List[:class:`ScanlatorGroup`]
            The list of groups that are being followed.
        """

        limit = min(max(1, limit), 100)
        if offset < 0:
            offset = 0

        data = await self._http._get_my_followed_groups(limit=limit, offset=offset)

        return [ScanlatorGroup(self._http, payload) for payload in data["results"]]

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
    async def get_my_followed_users(self, *, limit: int = 10, offset: int = 0) -> list[User]:
        """|coro|

        This method will return the current authenticated user's followed users.

        Parameters
        -----------
        limit: :class:`int`
            Defaults to 10. The amount of users to return in one request.
        offset: :class:`int`
            Defaults to 0. The pagination offset.

        Raises
        -------
        Forbidden
            The request returned an error due to authentication failure.

        Returns
        --------
        List[:class:`User`]
            The list of groups that are being followed.
        """

        limit = min(max(1, limit), 100)
        if offset < 0:
            offset = 0

        data = await self._http._get_my_followed_users(limit=limit, offset=offset)

        return [User(self._http, payload) for payload in data["results"]]

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
        Forbidden
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
        Forbidden
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
        BadRequest
            The parameters passed were malformed.

        Returns
        --------
        :class:`User`
            The created user.
        """
        data = await self._http._create_account(username=username, password=password, email=email)
        return User(self._http, data)

    async def activate_account(self, activation_code: str, /) -> None:
        """|coro|

        This method will activate an account on the MangaDex API.

        Parameters
        -----------
        activation_code: :class:`str`
            The activation code for the account.

        Raises
        -------
        BadRequest
            The query was malformed.
        NotFound
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
        BadRequest
            The email passed is not pending activation.
        """
        await self._http._resend_activation_code(email)

    async def recover_account(self, email: str, /) -> None:
        """|coro|

        This method will start an account recovery process on the given account.

        Parameters
        -----------
        email: :class:`str`
            The email address belonging to the account you wish to recover.

        Raises
        -------
        BadRequest
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
        BadRequest
            The recovery code given was not found or the password was greater than 1024 characters.
        """
        await self._http._complete_account_recovery(recovery_code, new_password=new_password)

    async def ping_the_server(self) -> bool:
        data = await self._http._ping_the_server()
        if data == "pong":
            return True

        return False

    async def legacy_id_mapping(self, type: legacy.LegacyMappingType, /, *, item_ids: list[int]) -> list[LegacyItem]:
        data = await self._http._legacy_id_mapping(type, item_ids=item_ids)
        return [LegacyItem(self._http, payload["data"]) for payload in data]