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
import pathlib
import sys
from typing import TYPE_CHECKING, Any, ClassVar, Coroutine, Optional, TypeVar, Union
from urllib.parse import quote as _uriquote

import aiohttp

from . import __version__, utils
from .author import Author
from .chapter import Chapter
from .cover import Cover
from .errors import APIException, BadRequest, LoginError, NotFound, RefreshError
from .manga import Manga


if TYPE_CHECKING:
    from .tags import QueryTags
    from .types import manga
    from .types.author import GetAuthorResponse
    from .types.chapter import GetChapterFeedResponse
    from .types.cover import GetCoverResponse
    from .types.payloads import CheckPayload, LoginPayload, RefreshPayload
    from .types.query import GetUserFeedQuery
    from .types.tags import GetTagListResponse

    T = TypeVar("T")
    Response = Coroutine[Any, Any, T]

__all__ = ("HTTPClient", "Route")

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel("DEBUG")
EPOCH = datetime.datetime.fromtimestamp(0)
TAGS = utils.TAGS

_PROJECT_DIR = pathlib.Path(__file__)


async def json_or_text(response: aiohttp.ClientResponse) -> Union[dict[str, Any], str]:
    text = await response.text(encoding="utf-8")
    try:
        if response.headers["content-type"] == "application/json":
            return json.loads(text)
    except KeyError:
        pass

    return text


def fmt(in_: datetime.datetime) -> str:
    return f"{in_:%Y-%m-%dT%H:%M:%S}"


class Route:
    """"""

    BASE: ClassVar[str] = "https://api.mangadex.org"

    def __init__(self, verb: str, path: str, **parameters: Any) -> None:
        self.verb: str = verb
        self.path: str = path
        url = self.BASE + self.path
        if parameters:
            url = url.format_map({k: _uriquote(v) if isinstance(v, str) else v for k, v in parameters.items()})
        self.url: str = url


class Client:
    """Underlying HTTP Client for the MangaDex API.

    Attributes
    -----------
    login: :class:`str`
        Your login username for the API. Used in conjunction with your password to generate an authentication token.
    password: :class:`str`
        Your login password for the API. Used in conjunction with your username to generate an authentication token.
    session: Optional[:class:`aiohttp.ClientSession`]
        A aiohttp ClientSession to use instead of creating one.


    .. note::
        If you do not pass a login and password then we cannot actually login and will error.

    .. note::
        The :class:`aiohttp.ClientSession` passed via constructor will have headers and authentication set.
        Do not pass one you plan to re-use for other things, lest you leak your login data.


    Raises
    -------
    ValueError
        You failed to pass appropriate login information (login and password, or a token).
    """

    __slots__ = (
        "login",
        "password",
        "__session",
        "_token",
        "__refresh_token",
        "__last_refresh",
        "user_agent",
        "_connection",
    )

    def __init__(
        self,
        *,
        login: str,
        password: str,
        session: Optional[aiohttp.ClientSession] = None,
    ) -> None:
        if not (login and password):
            raise ValueError(
                "You did not provide appropriate login information, a login (username) and password combination is required."
            )

        self.login = login
        self.password = password
        self.__session = session
        self._token: Optional[str] = None
        self.__refresh_token: Optional[str] = None
        self.__last_refresh: Optional[datetime.datetime] = None
        user_agent = "MangaDex.py (https://github.com/AbstractUmbra/mangadex.py {0}) Python/{1[0]}.{1[1]} aiohttp/{2}"
        self.user_agent: str = user_agent.format(__version__, sys.version_info, aiohttp.__version__)

    async def _generate_session(self) -> aiohttp.ClientSession:
        """|coro|

        Creates an :class:`aiohttp.ClientSession` for use in the http client.

        Returns
        --------
        :class:`aiohttp.ClientSession`
            The underlying client session we use.

        .. note::
            This method must be a coroutine to avoid the deprecation warning of Python 3.9+.
        """
        return aiohttp.ClientSession()

    async def close(self) -> None:
        """|coro|

        This method will close the internal client session to ensure a clean exit.
        """

        if self.__session is not None:
            await self.logout()
            await self.__session.close()

    async def _get_token(self) -> str:
        """|coro|

        This private method will login to MangaDex with the login username and password to retrieve a JWT auth token.

        Raises
        -------
        LoginError
            The passed username and password are incorrect.

        Returns
        --------
        :class:`str`
            The authentication token we will use.

        .. note::
            This does not use :meth:`HTTPClient.request` due to circular usage of request > generate token.
        """

        if self.__session is None:
            self.__session = await self._generate_session()

        route = Route("POST", "/auth/login")
        async with self.__session.post(route.url, json={"username": self.login, "password": self.password}) as response:
            data: LoginPayload = await response.json()

        if data["result"] == "error":
            text = await response.text()
            raise LoginError(text, response.status)

        token = data["token"]["session"]
        refresh_token = data["token"]["refresh"]
        self.__last_refresh = datetime.datetime.utcnow() - datetime.timedelta(seconds=30)
        self.__refresh_token = refresh_token
        return token

    async def _refresh_token(self) -> str:
        """|coro|

        This private method will refresh the current set token (:attr:`._auth`)

        Raises
        -------
        RefreshError
            We were unable to refresh the token.

        Returns
        --------
        :class:`str`
            The authentication token we just refreshed.

        .. note::
            This does not use :meth:`HTTPClient.request` due to circular usage of request > generate token.
        """
        LOGGER.debug("Token is older than 15 minutes, attempting a refresh.")

        if self.__session is None:
            self.__session = await self._generate_session()

        route = Route("POST", "/auth/refresh")
        async with self.__session.post(route.url, json={"token": self.__refresh_token}) as response:
            data: RefreshPayload = await response.json()

        assert self.__last_refresh is not None  # this will 100% be a `datetime` here, but type checker was crying

        if not (300 > response.status >= 200):
            text = await response.text()
            LOGGER.debug("Error (code %d) when trying to refresh a token: %s", text, response.status)
            raise RefreshError(text, response.status, self.__last_refresh)

        if self._token is not None and self._token == data["token"]["session"]:
            LOGGER.debug("Token refreshed successfully and matches.")
            return self._token

        # Theoretically unreachable
        raise RefreshError("Token was refreshed but a new token was given?", 200, self.__last_refresh)

    async def _try_token(self) -> str:
        """|coro|

        This private method will try and use the existing :attr:`_auth` to authenticate to the API.
        If this is unset, or returns a non-2xx response code, we will refresh the JWT / request another one.

        Raises
        -------
        APIError
            Something went wrong with testing our authentication against the API.

        Returns
        --------
        :class:`str`
            The authentication token we generated, refreshed or already had that is still valid.

        .. note::
            This does not use :meth:`Client.request` due to circular usage of request > generate token.
        """
        if self._token is None:
            LOGGER.debug("No jwt set yet, will attempt to generate one.")
            self._token = await self._get_token()
            return self._token

        if self.__last_refresh is not None:
            now = datetime.datetime.utcnow()
            if (now - datetime.timedelta(minutes=15)) > self.__last_refresh:
                refreshed = await self._refresh_token()
                if refreshed:
                    return self._token
            else:
                LOGGER.debug("Within the same 15m span of token generation, reusing it.")
                return self._token

        LOGGER.debug("Attempting to validate token: %s", self._token[:20])
        route = Route("GET", "/auth/check")

        if self.__session is None:
            self.__session = await self._generate_session()

        async with self.__session.get(route.url, headers={"Authorization": f"Bearer {self._token}"}) as response:
            data: CheckPayload = await response.json()

        if not (300 > response.status >= 200) or data["result"] == "error":
            text = await response.text()
            LOGGER.debug("Hit an error (code %d) when checking token auth: %s", text, response.status)
            raise APIException(text, response.status)

        if data["isAuthenticated"] is True:
            LOGGER.debug("Token is still valid: %s", self._token[:20])
            return self._token

        self._token = await self._get_token()
        LOGGER.debug("Token fetched: %s", self._token[:20])
        return self._token

    async def logout(self) -> None:
        """|coro|

        This performs the logout request, also done in :meth:`Client.close` for convenience.
        """
        if self.__session is None:
            self.__session = await self._generate_session()

        route = Route("POST", "/auth/logout")
        async with self.__session.request(route.verb, route.url) as response:
            data: dict[str, str] = await response.json()

        if not (300 > response.status >= 200) or data["result"] != "ok":
            raise APIException("Unable to logout", response.status)

    async def request(self, route: Route, **kwargs: Any) -> Any:
        """|coro|

        This performs the HTTP request, handling authentication tokens when doing it.

        Parameters
        -----------
        route: :class:`Route`
            The route describes the http verb and endpoint to hit.
            The request is the one that takes in the query params or request body.

        Raises
        -------
        APIException
            A generic exception raised when the HTTP response code is non 2xx.

        Returns
        --------
        Any
            The potential response data we got from the request.
        """
        if self.__session is None:
            self.__session = await self._generate_session()

        token = await self._try_token()
        headers = kwargs.pop("headers", None) or {"Authorization": f"Bearer {token}"}
        headers["User-Agent"] = self.user_agent

        if "json" in kwargs:
            headers["Content-Type"] = "application/json"
            kwargs["data"] = utils.to_json(kwargs.pop("json"))
        kwargs["headers"] = headers

        LOGGER.debug("Current request headers: %s", headers)

        async with self.__session.request(route.verb, route.url, **kwargs) as response:
            data = await json_or_text(response)

            if 300 > response.status >= 200:
                return data
            raise APIException(str(data), response.status)

    def _update_tags(self) -> Response[list[GetTagListResponse]]:
        route = Route("GET", "/manga/tag")
        return self.request(route)

    async def update_tags(self) -> None:
        """|coro|

        Convenience method for updating the local cache of tags.

        This should ideally not need to be called by the end user but nevertheless it exists in the event MangaDex
        add a new tag or similar."""
        data = await self._update_tags()

        tags: dict[str, str] = {}

        for tag in data:
            name_key = tag["data"]["attributes"]["name"]
            name = name_key.get("en", next(iter(name_key))).title()
            tags[name] = tag["data"]["id"]

        path = _PROJECT_DIR.parent / "extras" / "tags.json"
        with open(path, "w") as fp:
            json.dump(tags, fp, indent=4)

    def _get_manga(self, manga_id: str, includes: Optional[list[str]]) -> Response[manga.ViewMangaResponse]:
        route = Route("GET", "/manga/{manga_id}", manga_id=manga_id)

        includes = includes or ["artist", "cover_url", "author"]
        query = utils.php_query_builder({"includes": includes})
        data = self.request(route, params=query)

        return data

    async def get_manga(self, manga_id: str, includes: Optional[list[manga.MangaIncludes]] = None) -> Manga:
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
        NotFound
            The passed manga ID was not found, likely due to an incorrect ID.

        Returns
        --------
        :class:`Manga`
            The Manga that was returned from the API.
        """
        data = await self._get_manga(manga_id, includes)

        if data["result"] == "error":
            raise NotFound(f"Manga with the ID {manga_id} could not be found")

        return Manga(self, data)

    def _get_author(self, author_id: str) -> Response[GetAuthorResponse]:
        route = Route("GET", "/author/{author_id}", author_id=author_id)
        return self.request(route)

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
        data = await self._get_author(author_id)

        if data["result"] == "error":
            raise NotFound(f"Author with the ID {author_id} could not be found.")

        author_data = data["data"]
        attributes = author_data["attributes"]

        return Author(self, author_data, attributes)

    def _get_cover(self, cover_id: str, includes: list[str]) -> Response[GetCoverResponse]:
        route = Route("GET", "/cover/{cover_id}", cover_id=cover_id)

        query = {"includes": includes}
        resolved_query = utils.php_query_builder(query)

        return self.request(route, params=resolved_query)

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
        data = await self._get_cover(cover_id, includes=includes)

        if data["result"] == "error":
            raise NotFound(f"A Cover with the ID {cover_id} could not be found.")

        return Cover(self, data)

    def _get_my_feed(
        self,
        *,
        limit: int,
        offset: int,
        translated_languages: Optional[list[str]] = None,
        created_at_since: Optional[datetime.datetime] = None,
        updated_at_since: Optional[datetime.datetime] = None,
        published_at_since: Optional[datetime.datetime] = None,
        order: Optional[GetUserFeedQuery] = None,
    ) -> Response[GetChapterFeedResponse]:
        route = Route("GET", "/user/follows/manga/feed")

        query = {}
        query["limit"] = limit
        query["offset"] = offset
        if translated_languages:
            query["translatedLanguage"] = translated_languages

        if created_at_since:
            query["createdAtSince"] = fmt(created_at_since)

        if updated_at_since:
            query["updatedAtSince"] = fmt(updated_at_since)

        if published_at_since:
            query["publishAtSince"] = fmt(published_at_since)

        if order:
            query["order"] = order

        resolved_query = utils.php_query_builder(query)

        return self.request(route, params=resolved_query)

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
            The parameters were invalid and the API request failed.

        Returns
        --------
        List[:class:`Chapter`]
            Returns a list of Chapter instances.
        """

        limit = min(max(1, limit), 500)
        if offset < 0:
            offset = 0

        data = await self._get_my_feed(
            limit=limit,
            offset=offset,
            translated_languages=translated_languages,
            created_at_since=created_at_since,
            updated_at_since=updated_at_since,
            published_at_since=published_at_since,
            order=order,
        )

        if data.get("result", None) == "error":
            raise BadRequest("The api query was malformed")

        chapters: list[Chapter] = []
        for item in data["results"]:
            chapters.append(Chapter(self, item))

        return chapters

    def _search_manga(
        self,
        *,
        limit: int,
        offset: int,
        title: Optional[str],
        authors: Optional[list[str]],
        artists: Optional[list[str]],
        year: Optional[int],
        included_tags: Optional[QueryTags],
        excluded_tags: Optional[QueryTags],
        status: Optional[list[manga.MangaStatus]],
        original_language: Optional[list[str]],
        publication_demographic: Optional[list[manga.PublicationDemographic]],
        ids: Optional[list[str]],
        content_rating: Optional[list[manga.ContentRating]],
        created_at_since: Optional[datetime.datetime],
        updated_at_since: Optional[datetime.datetime],
        order: Optional[GetUserFeedQuery],
        includes: Optional[list[manga.MangaIncludes]],
    ) -> Response[manga.MangaSearchResponse]:
        route = Route("GET", "/manga")

        query = {}

        query["limit"] = limit
        query["offset"] = offset
        if title:
            query["title"] = title

        if authors:
            query["authors"] = authors

        if artists:
            query["artist"] = artists

        if year:
            query["year"] = year

        if included_tags:
            query["includedTags"] = included_tags.tags
            query["includedTagsMode"] = included_tags.mode

        if excluded_tags:
            query["excludedTags"] = excluded_tags.tags
            query["excludedTagsMode"] = excluded_tags.mode

        if status:
            query["status"] = status

        if original_language:
            query["originalLanguage"] = original_language

        if publication_demographic:
            query["publicationDemographic"] = publication_demographic

        if ids:
            query["ids"] = ids

        if content_rating:
            query["contentRating"] = content_rating

        if created_at_since:
            query["createdAtSince"] = fmt(created_at_since)

        if updated_at_since:
            query["updatedAtSince"] = fmt(updated_at_since)

        if order:
            query["order"] = order

        if includes:
            query["includes"] = includes

        resolved_query = utils.php_query_builder(query)

        LOGGER.debug(resolved_query)

        return self.request(route, params=resolved_query)

    async def search_manga(
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
        includes: Optional[list[manga.MangaIncludes]] = None,
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
            An instance of mangadex.Tags to include in the search.
        excluded_tags: Optional[:class:`QueryTags`]
            An instance of mangadex.Tags to include in the search.
        status: Optional[list[Dict[:class:`str`, Any]]]
            The status(es) of manga to include in the search.
        original_language: Optional[:class:`str`]
            A list of language codes to include for the Manga's original language.
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

        Raises
        -------
        BadRequest
            The parameters were invalid and the API request failed.

        Returns
        --------
        List[Manga]
            Returns a list of Manga instances.
        """
        limit = min(max(1, limit), 500)
        if offset < 0:
            offset = 0

        data = await self._search_manga(
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

        if data.get("result", None) == "error":
            raise BadRequest("The API query for search was malformed.")

        manga: list[Manga] = []
        for item in data["results"]:
            manga.append(Manga(self, item))

        return manga
