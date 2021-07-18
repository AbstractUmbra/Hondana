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
import datetime
import json
import pathlib
from typing import Literal, Optional, Union

from aiohttp import ClientSession

from .author import Author
from .chapter import Chapter
from .cover import Cover
from .http import HTTPClient
from .manga import Manga
from .tags import QueryTags
from .types import manga
from .types.common import LocalisedString
from .types.query import GetUserFeedQuery
from .utils import MISSING


_PROJECT_DIR = pathlib.Path(__file__)


class Client:
    """User Client for interfacing with the MangaDex API.

    Attributes
    -----------
    login: :class:`str`
        Your login username for the API / site. Used in conjunction with your password to generate an authentication token.
    email: :class:`str`
        Your login email for the API / site. Used in conjunction with your password to generate an authentication token.
    password: :class:`str`3
        Your login password for the API / site. Used in conjunction with your username to generate an authentication token.
    session: Optional[:class:`aiohttp.ClientSession`]
        A aiohttp ClientSession to use instead of creating one.


    .. note::
        If you do not pass a login/email and password then we cannot actually login and will error.

    .. note::
        The :class:`aiohttp.ClientSession` passed via constructor will have headers and authentication set.
        Do not pass one you plan to re-use for other things, lest you leak your login data.


    Raises
    -------
    ValueError
        You failed to pass appropriate login information (login/email and password).
    """

    __slots__ = ("_http",)

    def __init__(
        self,
        *,
        login: Optional[str] = None,
        email: Optional[str] = None,
        password: str,
        session: Optional[ClientSession] = None,
    ) -> None:
        self._http = HTTPClient(login=login, email=email, password=password, session=session)

    async def logout(self) -> None:
        """|coro|

        Logs the client out. This process will invalidate the current authorization token in the process.
        """

        return await self._http._close()

    async def close(self) -> None:
        """|coro|

        An alias for :meth:`Client.logout`.
        """

        return await self.logout()

    async def update_tags(self) -> None:
        """|coro|

        Convenience method for updating the local cache of tags.

        This should ideally not need to be called by the end user but nevertheless it exists in the event MangaDex
        add a new tag or similar."""
        data = await self._http._update_tags()

        tags: dict[str, str] = {}

        for tag in data:
            name_key = tag["data"]["attributes"]["name"]
            name = name_key.get("en", next(iter(name_key))).title()
            tags[name] = tag["data"]["id"]

        path = _PROJECT_DIR.parent / "extras" / "tags.json"
        with open(path, "w") as fp:
            json.dump(tags, fp, indent=4)

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

        author_data = data["data"]

        return Author(self._http, author_data)

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

    async def get_my_feed(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        translated_languages: Optional[list[str]] = None,
        created_at_since: Optional[datetime.datetime] = None,
        updated_at_since: Optional[datetime.datetime] = None,
        published_at_since: Optional[datetime.datetime] = None,
        order: Optional[GetUserFeedQuery] = None,
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
        order: Optional[Dict[:class:`str`, :class:`str`]]
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
        order: Optional[GetUserFeedQuery] = None,
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
        status: Optional[list[Dict[:class:`str`, Any]]]
            The status(es) of manga to include in the search.
        original_language: Optional[:class:`str`]
            A list of language codes to include for the manga's original language.
            i.e. ``["en"]``
        publication_demographic: Optional[List[Dict[:class:`str`, Any]]]
            The publication demographic(s) to limit the search to.
        ids: Optional[:class:`str`]
            A list of manga UUID(s) to limit the search to.
        content_rating: Optional[list[Dict[:class:`str`, Any]]]
            The content rating(s) to filter the search to.
        created_at_since: Optional[datetime.datetime]
            A (naive UTC) datetime instance we specify for searching.
            Used for returning manga created *after* this date.
        updated_at_since: Optional[datetime.datetime]
            A (naive UTC) datetime instance we specify for searching.
            Used for returning manga updated *after* this date.
        order: Optional[]
            A query parameter to choose the ordering of the response
            i.e. ``{"createdAt": "desc"}``
        includes: Optional[List[Dict[:class:`str`, Any]]]
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

    async def create_manga(
        self,
        *,
        title: LocalisedString,
        alt_titles: Optional[list[LocalisedString]] = None,
        description: Optional[LocalisedString] = None,
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
        links: Optional[Dict[str, Any]]
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
        translated_language: Optional[Dict[:class:`str`, List[:class:`str`]]]
            The list of language codes you want to limit the search to.

        Returns
        --------
        Dict[str, Any]
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

    async def update_manga(
        self,
        manga_id: str,
        *,
        title: Optional[LocalisedString] = None,
        alt_titles: Optional[list[LocalisedString]] = None,
        description: Optional[LocalisedString] = None,
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
        links: Optional[Dict[str, Any]]
            The links relevant to the manga.
            See here for more details: https://api.mangadex.org/docs.html#section/Static-data/Manga-links-data
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
        order: Optional[Dict[Literal[``"volume"``, ``"chapter"``], Literal[``"asc"``, ``"desc"``]]]
            A query parameter to choose how the responses are ordered.
            i.e. ``{"chapters": "desc"}``
        includes: Optional[List[Literal[``"author"``, ``"artist"``, ``"cover_art"``]]]
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
