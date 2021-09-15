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
import json
import logging
import sys
from base64 import b64decode
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Coroutine,
    Literal,
    Optional,
    TypeVar,
    Union,
    overload,
)
from urllib.parse import quote as _uriquote

import aiohttp

from . import __version__
from .errors import (
    APIException,
    BadRequest,
    Forbidden,
    LoginError,
    NotFound,
    RefreshError,
    Unauthorized,
)
from .utils import MISSING, TAGS, php_query_builder, to_iso_format, to_json


if TYPE_CHECKING:
    from .tags import QueryTags
    from .types import (
        artist,
        author,
        chapter,
        common,
        cover,
        custom_list,
        legacy,
        manga,
        report,
        scanlator_group,
        user,
    )
    from .types.auth import CheckPayload, LoginPayload, RefreshPayload
    from .types.query import OrderQuery
    from .types.tags import GetTagListResponse
    from .types.token import TokenPayload

    T = TypeVar("T")
    Response = Coroutine[Any, Any, T]


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel("DEBUG")
EPOCH = datetime.datetime.fromtimestamp(0)
TAGS = TAGS

__all__ = ("json_or_text", "Route", "HTTPClient")


async def json_or_text(response: aiohttp.ClientResponse) -> Union[dict[str, Any], str]:
    text = await response.text(encoding="utf-8")
    try:
        if response.headers["content-type"] == "application/json":
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass
    except KeyError:
        pass

    return text


class Route:
    """A helper class for instantiating a HTTP method to MangaDex.

    Parameters
    -----------
    verb: :class:`str`
        The HTTP verb you wish to perform, e.g. ``"POST"``
    path: :class:`str`
        The prepended path to the API endpoint you with to target.
        e.g. ``"/manga/{manga_id}"``
    parameters: Any
        This is a special cased kwargs. Anything passed to these will substitute it's key to value in the `path`.
        E.g. if your `path` is ``"/manga/{manga_id}"``, and your parameters are ``manga_id="..."``, then it will expand into the path
        making ``"manga/..."``
    """

    BASE: ClassVar[str] = "https://api.mangadex.org"

    def __init__(self, verb: str, path: str, **parameters: Any) -> None:
        self.verb: str = verb
        self.path: str = path
        url = self.BASE + self.path
        if parameters:
            url = url.format_map({k: _uriquote(v) if isinstance(v, str) else v for k, v in parameters.items()})
        self.url: str = url


class HTTPClient:
    __slots__ = (
        "username",
        "email",
        "password",
        "_authenticated",
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
        username: Optional[str],
        email: Optional[str],
        password: Optional[str],
        session: Optional[aiohttp.ClientSession] = None,
    ) -> None:
        self._authenticated = bool(((username or email) and password))
        self.username: Optional[str] = username
        self.email: Optional[str] = email
        self.password: Optional[str] = password
        self.__session = session
        self._token: Optional[str] = None
        self.__refresh_token: Optional[str] = None
        self.__last_refresh: Optional[datetime.datetime] = None
        user_agent = "Hondana (https://github.com/AbstractUmbra/Hondana {0}) Python/{1[0]}.{1[1]} aiohttp/{2}"
        self.user_agent: str = user_agent.format(__version__, sys.version_info, aiohttp.__version__)

    @staticmethod
    async def _generate_session() -> aiohttp.ClientSession:
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

    async def _close(self) -> None:
        """|coro|

        This method will close the internal client session to ensure a clean exit.
        """

        if self.__session is not None:
            if self._authenticated:
                await self._logout()
            await self.__session.close()

    async def _handle_ratelimits(self, response: aiohttp.ClientResponse) -> None:
        """|coro|

        A private method to fetch the potential ratelimits on a request, and sleep until they end.
        """
        headers = response.headers

        # Requests remaining before ratelimit
        remaining = headers.get("x-ratelimit-remaining", None)
        # Time until current ratelimit session(?) expires
        retry = headers.get("x-ratelimit-remaining", None)
        # The total ratelimit session hits
        limit = headers.get("x-ratelimit-limit", None)

        if remaining == "0":
            assert retry is not None
            LOGGER.warning("Hit a ratelimit, sleeping for: %d", retry)
            await asyncio.sleep(int(retry))

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

        if self.username:
            auth = {"username": self.username, "password": self.password}
        elif self.email:
            auth = {"email": self.email, "password": self.password}
        else:
            raise ValueError("No authentication methods set before attempting an API request.")

        route = Route("POST", "/auth/login")
        async with self.__session.post(route.url, json=auth) as response:
            await self._handle_ratelimits(response)
            data: LoginPayload = await response.json()

        if data["result"] == "error":
            text = await response.text()
            raise LoginError(response, text, response.status)

        token = data["token"]["session"]
        refresh_token = data["token"]["refresh"]
        self.__last_refresh = self._get_expiry(token)
        self.__refresh_token = refresh_token
        return token

    def _get_expiry(self, token: str) -> datetime.datetime:
        payload = token.split(".")[1]
        payload = b64decode(payload)
        data: TokenPayload = json.loads(payload)
        timestamp = data["exp"]

        expires = datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc)
        return expires

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
            await self._handle_ratelimits(response)
            data: RefreshPayload = await response.json()

        assert self.__last_refresh is not None  # this will 100% be a `datetime` here, but type checker was crying

        if not (300 > response.status >= 200):
            text = await response.text()
            LOGGER.debug("Error (code %d) when trying to refresh a token: %s", text, response.status)
            raise RefreshError(response, text, response.status, self.__last_refresh)

        if data["result"] == "error":
            raise RefreshError(response, "The API reported an error when refreshing the token", 200, self.__last_refresh)

        self._token = data["token"]["session"]
        self.__last_refresh = datetime.datetime.now(datetime.timezone.utc)
        return self._token

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
            now = datetime.datetime.now(datetime.timezone.utc)
            # To avoid a race condition we're gonna check this for 14 minutes, since it can re-auth anytime, but post 15m it will error
            if now > self.__last_refresh:
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
            await self._handle_ratelimits(response)
            data: CheckPayload = await response.json()

        if not (300 > response.status >= 200) or data["result"] == "error":
            text = await response.text()
            LOGGER.debug("Hit an error (code %d) when checking token auth: %s", text, response.status)
            raise APIException(response, text, response.status)

        if data["isAuthenticated"] is True:
            LOGGER.debug("Token is still valid: %s", self._token[:20])
            return self._token

        self._token = await self._get_token()
        LOGGER.debug("Token fetched: %s", self._token[:20])
        return self._token

    async def _logout(self) -> None:
        """|coro|

        This performs the logout request, also done in :meth:`Client.close` for convenience.
        """
        if self.__session is None:
            self.__session = await self._generate_session()

        route = Route("POST", "/auth/logout")
        async with self.__session.request(route.verb, route.url) as response:
            data: dict[str, str] = await response.json()

        if not (300 > response.status >= 200) or data["result"] != "ok":
            raise APIException(response, "Unable to logout", response.status)

        self._authenticated = False

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
        BadRequest
            A request was malformed
        Unauthorized
            You attempted to use an endpoint you have no authorization for.
        Forbidden
            Your auth was not sufficient to perform this action.
        NotFound
            The specified item, endpoint or resource was not found.
        APIException
            A generic exception raised when the HTTP response code is non 2xx.

        Returns
        --------
        Any
            The potential response data we got from the request.
        """
        if self.__session is None:
            self.__session = await self._generate_session()

        headers = kwargs.pop("headers", {})
        token = await self._try_token() if self._authenticated else None

        if token is not None:
            headers["Authorization"] = f"Bearer {token}"
        headers["User-Agent"] = self.user_agent

        if "json" in kwargs:
            headers["Content-Type"] = "application/json"
            kwargs["data"] = to_json(kwargs.pop("json"))
        kwargs["headers"] = headers

        LOGGER.debug("Current request headers: %s", headers)
        LOGGER.debug("Current request url and params: %s", route.url)

        async with self.__session.request(route.verb, route.url, **kwargs) as response:
            await self._handle_ratelimits(response)
            data = await json_or_text(response)

            if 300 > response.status >= 200:
                return data

            if response.status == 400:
                raise BadRequest(response, str(data))
            elif response.status == 401:
                raise Unauthorized(response, str(data))
            elif response.status == 403:
                raise Forbidden(response, str(data))
            elif response.status == 404:
                raise NotFound(response, str(data))
            raise APIException(response, str(data), response.status)

    def _update_tags(self) -> Response[GetTagListResponse]:
        route = Route("GET", "/manga/tag")
        return self.request(route)

    def _manga_list(
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
        original_language: Optional[list[common.LanguageCode]],
        excluded_original_language: Optional[list[common.LanguageCode]],
        available_translated_language: Optional[list[common.LanguageCode]],
        publication_demographic: Optional[list[manga.PublicationDemographic]],
        ids: Optional[list[str]],
        content_rating: Optional[list[manga.ContentRating]],
        created_at_since: Optional[datetime.datetime],
        updated_at_since: Optional[datetime.datetime],
        order: Optional[manga.MangaOrderQuery],
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

        if excluded_original_language:
            query["excludedOriginalLanguage"] = excluded_original_language

        if available_translated_language:
            query["availableTranslatedLanguage"] = available_translated_language

        if publication_demographic:
            query["publicationDemographic"] = publication_demographic

        if ids:
            query["ids"] = ids

        if content_rating:
            query["contentRating"] = content_rating

        if created_at_since:
            query["createdAtSince"] = to_iso_format(created_at_since)

        if updated_at_since:
            query["updatedAtSince"] = to_iso_format(updated_at_since)

        if order:
            query["order"] = order

        if includes:
            query["includes"] = includes

        resolved_query = php_query_builder(query)

        LOGGER.debug(resolved_query)

        return self.request(route, params=resolved_query)

    def _create_manga(
        self,
        *,
        title: common.LocalisedString,
        alt_titles: Optional[list[common.LocalisedString]],
        description: Optional[common.LocalisedString],
        authors: Optional[list[str]],
        artists: Optional[list[str]],
        links: Optional[manga.MangaLinks],
        original_language: Optional[str],
        last_volume: Optional[str],
        last_chapter: Optional[str],
        publication_demographic: Optional[manga.PublicationDemographic],
        status: Optional[manga.MangaStatus],
        year: Optional[int],
        content_rating: manga.ContentRating,
        tags: Optional[QueryTags],
        mod_notes: Optional[str],
        version: int,
    ) -> Response[manga.GetMangaResponse]:

        query = {}
        query["title"] = title
        query["version"] = version

        if alt_titles:
            query["altTitles"] = alt_titles

        if description:
            query["description"] = description

        if authors:
            query["authors"] = authors

        if artists:
            query["artists"] = artists

        if links:
            query["links"] = links

        if original_language:
            query["originalLanguage"] = original_language

        if last_volume:
            query["lastVolume"] = last_volume

        if last_chapter:
            query["lastChapter"] = last_chapter

        if publication_demographic:
            query["publicationDemographic"] = publication_demographic

        if status:
            query["status"] = status

        if year:
            query["year"] = year

        if content_rating:
            query["contentRating"] = content_rating

        if tags:
            query["tags"] = tags.tags

        if mod_notes:
            query["modNotes"] = mod_notes

        route = Route("POST", "/manga")
        return self.request(route, json=query)

    def _get_manga_volumes_and_chapters(
        self, *, manga_id: str, translated_languages: Optional[list[str]] = None
    ) -> Response[manga.GetMangaVolumesAndChaptersResponse]:
        ...

        route = Route("GET", "/manga/{manga_id}/aggregate", manga_id=manga_id)

        if translated_languages:
            query = php_query_builder({"translatedLanguage": translated_languages})
            return self.request(route, params=query)
        return self.request(route)

    def _view_manga(self, manga_id: str, /, *, includes: Optional[list[str]]) -> Response[manga.GetMangaResponse]:
        route = Route("GET", "/manga/{manga_id}", manga_id=manga_id)

        includes = includes or ["artist", "cover_url", "author"]
        query = php_query_builder({"includes": includes})
        data = self.request(route, params=query)

        return data

    def _update_manga(
        self,
        manga_id: str,
        /,
        *,
        title: Optional[common.LocalisedString],
        alt_titles: Optional[list[common.LocalisedString]],
        description: Optional[common.LocalisedString],
        authors: Optional[list[str]],
        artists: Optional[list[str]],
        links: Optional[manga.MangaLinks],
        original_language: Optional[str],
        last_volume: Optional[str],
        last_chapter: Optional[str],
        publication_demographic: Optional[manga.PublicationDemographic],
        status: manga.MangaStatus,
        year: Optional[int],
        content_rating: Optional[manga.ContentRating],
        tags: Optional[QueryTags],
        mod_notes: Optional[str],
        version: int,
    ) -> Response[manga.GetMangaResponse]:
        route = Route("PUT", "/manga/{manga_id}", manga_id=manga_id)

        query = {}
        query["version"] = version
        query["status"] = status

        if title:
            query["title"] = title

        if alt_titles:
            query["altTitles"] = alt_titles

        if description:
            query["description"] = description

        if authors:
            query["authors"] = authors

        if artists:
            query["artists"] = artists

        if links:
            query["links"] = links

        if original_language:
            query["originalLanguage"] = original_language

        if last_volume is not MISSING:
            query["lastVolume"] = last_volume

        if last_chapter is not MISSING:
            query["lastChapter"] = last_chapter

        if publication_demographic is not MISSING:
            query["publicationDemographic"] = publication_demographic

        if year is not MISSING:
            query["year"] = year

        if content_rating:
            query["contentRating"] = content_rating

        if tags:
            query["tags"] = tags.tags

        if mod_notes is not MISSING:
            query["modNotes"] = mod_notes

        return self.request(route, json=query)

    def _delete_manga(self, manga_id: str, /) -> Response[dict[str, Literal["ok", "error"]]]:
        route = Route("DELETE", "/manga/{manga_id}", manga_id=manga_id)
        return self.request(route)

    def _manga_feed(
        self,
        manga_id: Optional[str],
        /,
        *,
        limit: int,
        offset: int,
        translated_languages: Optional[list[common.LanguageCode]],
        original_language: Optional[list[common.LanguageCode]],
        excluded_original_language: Optional[list[common.LanguageCode]],
        content_rating: Optional[list[common.ContentRating]],
        include_future_updates: Optional[bool],
        created_at_since: Optional[datetime.datetime],
        updated_at_since: Optional[datetime.datetime],
        published_at_since: Optional[datetime.datetime],
        order: Optional[manga.MangaOrderQuery],
        includes: Optional[list[manga.MangaIncludes]],
    ) -> Response[chapter.GetMultiChapterResponse]:
        if manga_id is None:
            route = Route("GET", "/user/follows/manga/feed")
        else:
            route = Route("GET", "/manga/{manga_id}/feed", manga_id=manga_id)

        query = {}
        query["limit"] = limit
        query["offset"] = offset

        if translated_languages:
            query["translatedLanguage"] = translated_languages

        if original_language:
            query["originalLanguage"] = original_language

        if excluded_original_language:
            query["excludedOriginalLanguage"] = excluded_original_language

        if content_rating:
            query["contentRating"] = content_rating

        if include_future_updates:
            resolved = str(include_future_updates).lower()
            query["includeFutureUpdates"] = resolved

        if created_at_since:
            query["createdAtSince"] = to_iso_format(created_at_since)

        if updated_at_since:
            query["updatedAtSince"] = to_iso_format(updated_at_since)

        if published_at_since:
            query["publishAtSince"] = to_iso_format(published_at_since)

        if order:
            query["order"] = order

        if includes:
            query["includes"] = includes

        resolved_query = php_query_builder(query)

        return self.request(route, params=resolved_query)

    def _unfollow_manga(self, manga_id: str, /) -> Response[dict[str, Literal["ok", "error"]]]:
        route = Route("DELETE", "/manga/{manga_id}/follow", manga_id=manga_id)
        return self.request(route)

    def _follow_manga(self, manga_id: str, /) -> Response[dict[str, Literal["ok", "error"]]]:
        route = Route("POST", "/manga/{manga_id}/follow", manga_id=manga_id)
        return self.request(route)

    def _get_random_manga(self, *, includes: Optional[list[manga.MangaIncludes]]) -> Response[manga.GetMangaResponse]:
        route = Route("GET", "/manga/random")

        if includes:
            query = {"includes": includes}
            resolved_query = php_query_builder(query)
            return self.request(route, params=resolved_query)

        return self.request(route)

    @overload
    def _manga_read_markers(
        self, manga_ids: list[str], /, *, grouped: Literal[False]
    ) -> Response[manga.MangaReadMarkersResponse]:
        ...

    @overload
    def _manga_read_markers(
        self, manga_ids: list[str], /, *, grouped: Literal[True]
    ) -> Response[manga.MangaGroupedReadMarkersResponse]:
        ...

    def _manga_read_markers(self, manga_ids: list[str], /, *, grouped: bool = False):
        if grouped is False:
            if len(manga_ids) != 1:
                raise ValueError("If `grouped` is False, then `manga_ids` should be a single length list.")

            id_ = manga_ids[0]
            route = Route("GET", "/manga/{manga_id}/read", manga_id=id_)
            return self.request(route)

        route = Route("GET", "/manga/read")
        query = {"ids": manga_ids, "grouped": True}
        resolved_query = php_query_builder(query)
        return self.request(route, params=resolved_query)

    def _manga_read_markers_batch(
        self, manga_id: str, /, *, read_chapters: Optional[list[str]], unread_chapters: Optional[list[str]]
    ) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("POST", "/manga/{manga_id}/read", manga_id=manga_id)

        body = {}

        if read_chapters:
            body["chapterIdsRead"] = read_chapters

        if unread_chapters:
            body["chapterIdsUnread"] = unread_chapters

        return self.request(route, json=body)

    def _get_manga_reading_status(self, manga_id: str, /) -> Response[manga.MangaReadingStatusResponse]:
        route = Route("GET", "/manga/{manga_id}/status", manga_id=manga_id)
        return self.request(route)

    def _update_manga_reading_status(
        self, manga_id: str, /, status: Optional[manga.ReadingStatus]
    ) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("POST", "/manga/{manga_id}/status", manga_id=manga_id)
        resolved_query = php_query_builder({"status": status})
        return self.request(route, params=resolved_query)

    def _chapter_list(
        self,
        *,
        limit: int,
        offset: int,
        ids: Optional[list[str]],
        title: Optional[str],
        groups: Optional[list[str]],
        uploader: Optional[str],
        manga: Optional[str],
        volume: Optional[Union[str, list[str]]],
        chapter: Optional[Union[str, list[str]]],
        translated_language: Optional[list[common.LanguageCode]],
        original_language: Optional[list[common.LanguageCode]],
        excluded_original_language: Optional[list[common.LanguageCode]],
        content_rating: Optional[list[common.ContentRating]],
        include_future_updates: Optional[bool],
        created_at_since: Optional[datetime.datetime],
        updated_at_since: Optional[datetime.datetime],
        published_at_since: Optional[datetime.datetime],
        order: Optional[chapter.ChapterOrderQuery],
        includes: Optional[list[chapter.ChapterIncludes]],
    ) -> Response[chapter.GetMultiChapterResponse]:
        route = Route("GET", "/chapter")

        query = {}
        query["limit"] = limit
        query["offset"] = offset

        if ids:
            query["ids"] = ids

        if title:
            query["title"] = title

        if groups:
            query["groups"] = groups

        if uploader:
            query["uploader"] = uploader

        if manga:
            query["manga"] = manga

        if volume:
            query["volume"] = volume

        if chapter:
            query["chapter"] = chapter

        if translated_language:
            query["translatedLanguage"] = translated_language

        if original_language:
            query["originalLanguage"] = original_language

        if excluded_original_language:
            query["excludedOriginalLanguage"] = excluded_original_language

        if content_rating:
            query["contentRating"] = content_rating

        if include_future_updates:
            resolved = str(include_future_updates).lower()
            query["includeFutureUpdates"] = resolved

        if created_at_since:
            query["createdAtSince"] = to_iso_format(created_at_since)

        if updated_at_since:
            query["updatedAtSince"] = to_iso_format(updated_at_since)

        if published_at_since:
            query["publishedAtSince"] = to_iso_format(published_at_since)

        if order:
            query["order"] = order

        if includes:
            query["includes"] = includes

        resolved_query = php_query_builder(query)

        return self.request(route, params=resolved_query)

    def _get_chapter(
        self, chapter_id: str, /, *, includes: Optional[list[chapter.ChapterIncludes]]
    ) -> Response[chapter.GetSingleChapterResponse]:
        route = Route("GET", "/chapter/{chapter_id}", chapter_id=chapter_id)

        if includes:
            return self.request(route, params=php_query_builder({"includes": includes}))
        return self.request(route)

    def _update_chapter(
        self,
        chapter_id: str,
        /,
        *,
        title: Optional[str],
        volume: Optional[str],
        chapter: Optional[str],
        translated_language: Optional[str],
        groups: Optional[list[str]],
        version: int,
    ) -> Response[chapter.GetSingleChapterResponse]:
        route = Route("PUT", "/chapter/{chapter_id}", chapter_id=chapter_id)

        query = {}
        query["version"] = version

        if title:
            query["title"] = title

        if volume is not MISSING:
            query["volume"] = volume

        if chapter is not MISSING:
            query["chapter"] = chapter

        if translated_language:
            query["translatedLanguage"] = translated_language

        if groups:
            query["groups"] = groups

        return self.request(route, json=query)

    def _delete_chapter(self, chapter_id: str, /) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("DELETE", "/chapter/{chapter_id}", chapter_id=chapter_id)
        return self.request(route)

    def _mark_chapter_as_read(self, chapter_id: str, /) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("POST", "/chapter/{chapter_id}/read", chapter_id=chapter_id)
        return self.request(route)

    def _mark_chapter_as_unread(self, chapter_id: str, /) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("DELETE", "/chapter/{chapter_id}/read", chapter_id=chapter_id)
        return self.request(route)

    def _cover_art_list(
        self,
        *,
        limit: int = 10,
        offset: int = 0,
        manga: Optional[list[str]],
        ids: Optional[list[str]],
        uploaders: Optional[list[str]],
        order: Optional[cover.CoverOrderQuery],
        includes: Optional[list[cover.CoverIncludes]],
    ) -> Response[cover.GetMultiCoverResponse]:
        route = Route("GET", "/cover")

        query = {}
        query["limit"] = limit
        query["offset"] = offset

        if manga:
            query["manga"] = manga

        if ids:
            query["ids"] = ids

        if uploaders:
            query["uploaders"] = uploaders

        if order:
            query["order"] = order

        if includes:
            query["includes"] = includes

        resolved_query = php_query_builder(query)

        return self.request(route, params=resolved_query)

    def _get_cover(self, cover_id: str, /, includes: list[str]) -> Response[cover.GetSingleCoverResponse]:
        route = Route("GET", "/cover/{cover_id}", cover_id=cover_id)

        query = {"includes": includes}
        resolved_query = php_query_builder(query)

        return self.request(route, params=resolved_query)

    def _edit_cover(
        self, cover_id: str, /, *, volume: Optional[str] = MISSING, description: Optional[str], version: int
    ) -> Response[cover.GetSingleCoverResponse]:
        route = Route("PUT", "/cover/{cover_id}", cover_id=cover_id)

        query = {}
        query["version"] = version

        if volume is not MISSING:
            query["volume"] = volume
        elif volume is MISSING:
            raise TypeError("`volume` key must be a value of some sort.")

        if description is not MISSING:
            query["description"] = description

        return self.request(route, json=query)

    def _delete_cover(self, cover_id: str, /) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("DELETE", "/cover/{cover_id}", cover_id=cover_id)
        return self.request(route)

    def _scanlation_group_list(
        self,
        *,
        limit: int,
        offset: int,
        ids: Optional[list[str]],
        name: Optional[str],
        includes: Optional[list[scanlator_group.ScanlatorGroupIncludes]],
    ) -> Response[scanlator_group.GetMultiScanlationGroupResponse]:
        route = Route("GET", "/group")

        query = {}
        query["limit"] = limit
        query["offset"] = offset

        if ids:
            query["ids"] = ids

        if name:
            query["name"] = name

        if includes:
            query["includes"] = includes

        return self.request(route)

    def _user_list(
        self,
        *,
        limit: int,
        offset: int,
        ids: Optional[list[str]],
        username: Optional[str],
        order: Optional[user.UserOrderQuery],
    ) -> Response[user.GetMultiUserResponse]:
        route = Route("GET", "/user")

        query = {}
        query["limit"] = limit
        query["offset"] = offset

        if ids:
            query["ids"] = ids

        if username:
            query["username"] = username

        if order:
            query["order"] = order

        resolved_query = php_query_builder(query)

        return self.request(route, params=resolved_query)

    def _get_user(self, user_id: str, /) -> Response[user.GetSingleUserResponse]:
        route = Route("GET", "/user/{user_id}", user_id=user_id)
        return self.request(route)

    def _delete_user(self, user_id: str, /) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("DELETE", "/user/{user_id}", user_id=user_id)
        return self.request(route)

    def _approve_user_deletion(self, approval_code: str, /) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("POST", "/user/delete/{approval_code}", approval_code=approval_code)
        return self.request(route)

    def _update_user_password(
        self, *, old_password: str, new_password: str
    ) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("POST", "/user/password")
        query = {"oldPassword": old_password, "newPassword": new_password}
        return self.request(route, json=query)

    def _update_user_email(self, email: str, /) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("POST", "/user/email")
        query = {"email": email}
        return self.request(route, json=query)

    def _get_my_details(self) -> Response[user.GetSingleUserResponse]:
        route = Route("GET", "/user/me")
        return self.request(route)

    def _get_my_followed_groups(
        self, *, limit: int, offset: int
    ) -> Response[scanlator_group.GetMultiScanlationGroupResponse]:
        route = Route("GET", "/user/follows/group")
        query = php_query_builder({"limit": limit, "offset": offset})
        return self.request(route, params=query)

    def _check_if_following_group(self, group_id: str, /) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("GET", "/user/follows/group/{group_id}", group_id=group_id)
        return self.request(route)

    def _get_my_followed_users(self, *, limit: int, offset: int) -> Response[user.GetMultiUserResponse]:
        route = Route("GET", "/user/follows/user")
        query = php_query_builder({"limit": limit, "offset": offset})
        return self.request(route, params=query)

    def _check_if_following_user(self, user_id: str, /) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("GET", "/user/follows/user/{user_id}", user_id=user_id)
        return self.request(route)

    def _check_if_following_manga(self, manga_id: str, /) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("GET", "/user/follows/manga/{manga_id}", manga_id=manga_id)
        return self.request(route)

    def _create_account(self, *, username: str, password: str, email: str) -> Response[user.GetSingleUserResponse]:
        route = Route("POST", "/account/create")
        query = {"username": username, "password": password, "email": email}
        return self.request(route, json=query)

    def _activate_account(self, activation_code: str, /) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("POST", "/account/activate/{activation_code}", activation_code=activation_code)
        return self.request(route)

    def _resend_activation_code(self, email: str, /) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("POST", "/account/activate/resend")
        query = {"email": email}
        return self.request(route, json=query)

    def _recover_account(self, email: str, /) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("POST", "/account/recover")
        query = {"email": email}
        return self.request(route, json=query)

    def _complete_account_recovery(
        self, recovery_code: str, /, *, new_password: str
    ) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("POST", "/account/recover/{recovery_code}", recovery_code=recovery_code)
        query = {"newPassword": new_password}
        return self.request(route, json=query)

    def _ping_the_server(self) -> Response[str]:
        route = Route("GET", "/ping")
        return self.request(route)

    def _legacy_id_mapping(
        self, type: legacy.LegacyMappingType, /, *, item_ids: list[int]
    ) -> Response[legacy.GetLegacyMappingResponse]:
        route = Route("POST", "/legacy/mapping")
        query = {"type": type, "ids": item_ids}
        return self.request(route, json=query)

    def _get_at_home_url(self, chapter_id: str, /, *, ssl: bool) -> Response[dict[Literal["baseUrl"], str]]:
        route = Route("GET", "/at-home/server/{chapter_id}", chapter_id=chapter_id)
        query = php_query_builder({"forcePort443": str(ssl).lower()})
        return self.request(route, params=query)

    def _create_custom_list(
        self,
        *,
        name: str,
        visibility: Optional[custom_list.CustomListVisibility],
        manga: Optional[list[str]],
        version: Optional[int],
    ) -> Response[custom_list.GetSingleCustomListResponse]:
        route = Route("POST", "/list")

        query = {}
        query["name"] = name

        if visibility:
            query["visibility"] = visibility

        if manga:
            query["manga"] = manga

        if version:
            query["version"] = version

        return self.request(route, json=query)

    def _get_custom_list(
        self, custom_list_id: str, /, *, includes: list[custom_list.CustomListIncludes]
    ) -> Response[custom_list.GetSingleCustomListResponse]:
        route = Route("GET", "/list/{custom_list_id}", custom_list_id=custom_list_id)

        query = {}

        if includes:
            query["includes"] = includes

        resolved_query = php_query_builder(query)

        return self.request(route, params=resolved_query)

    def _update_custom_list(
        self,
        custom_list_id,
        /,
        *,
        name: Optional[str],
        visibility: Optional[custom_list.CustomListVisibility],
        manga: Optional[list[str]],
        version: int,
    ) -> Response[custom_list.GetSingleCustomListResponse]:
        route = Route("POST", "/list/{custom_list_id}", custom_list_id=custom_list_id)

        query = {}
        query["version"] = version

        if name:
            query["name"] = name

        if visibility:
            query["visibility"] = visibility

        if manga:
            query["manga"] = manga

        return self.request(route, json=query)

    def _delete_custom_list(self, custom_list_id: str, /) -> Response[dict[Literal["result"], Literal["ok", "error"]]]:
        route = Route("DELETE", "/list/{custom_list_id}", custom_list_id=custom_list_id)
        return self.request(route)

    def _add_manga_to_custom_list(
        self, *, custom_list_id: str, manga_id: str
    ) -> Response[dict[Literal["result"], Literal["ok", "error"]]]:
        route = Route("POST", "/manga/{manga_id}/list/{custom_list_id}", manga_id=manga_id, custom_list_id=custom_list_id)
        return self.request(route)

    def _remove_manga_from_custom_list(
        self, *, manga_id: str, custom_list_id: str
    ) -> Response[dict[Literal["result"], Literal["ok", "error"]]]:
        route = Route("DELETE", "/manga/{manga_id}/list/{custom_list_id}", manga_id=manga_id, custom_list_id=custom_list_id)
        return self.request(route)

    def _get_my_custom_lists(self, limit: int, offset: int) -> Response[custom_list.GetMultiCustomListResponse]:
        route = Route("GET", "/user/list")
        query = {"limit": limit, "offset": offset}
        resolved_query = php_query_builder(query)
        return self.request(route, params=resolved_query)

    def _get_users_custom_lists(
        self, user_id: str, /, *, limit: int, offset: int
    ) -> Response[custom_list.GetMultiCustomListResponse]:
        route = Route("GET", "/user/{user_id}/list", user_id=user_id)
        query = {"limit": limit, "offset": offset}
        resolved_query = php_query_builder(query)
        return self.request(route, params=resolved_query)

    def _custom_list_manga_feed(
        self,
        custom_list_id: str,
        /,
        *,
        limit: int,
        offset: int,
        translated_languages: Optional[list[common.LanguageCode]],
        original_language: Optional[list[common.LanguageCode]],
        excluded_original_language: Optional[list[common.LanguageCode]],
        content_rating: Optional[list[common.ContentRating]],
        include_future_updates: Optional[bool],
        created_at_since: Optional[datetime.datetime],
        updated_at_since: Optional[datetime.datetime],
        published_at_since: Optional[datetime.datetime],
        order: Optional[OrderQuery],
    ) -> Response[chapter.GetMultiChapterResponse]:
        route = Route("GET", "/list/{custom_list_id}/feed", custom_list_id=custom_list_id)

        query = {}
        query["limit"] = limit
        query["offset"] = offset

        if translated_languages:
            query["translatedLanguage"] = translated_languages

        if original_language:
            query["originalLanguage"] = original_language

        if excluded_original_language:
            query["excludedOriginalLanguage"] = excluded_original_language

        if content_rating:
            query["contentRating"] = content_rating

        if include_future_updates:
            resolved = str(include_future_updates).lower()
            query["includeFutureUpdates"] = resolved

        if created_at_since:
            query["createdAtSince"] = to_iso_format(created_at_since)

        if updated_at_since:
            query["updatedAtSince"] = to_iso_format(updated_at_since)

        if published_at_since:
            query["publishAtSince"] = to_iso_format(published_at_since)

        if order:
            query["order"] = order

        resolved_query = php_query_builder(query)

        return self.request(route, params=resolved_query)

    def _create_scanlation_group(
        self, *, name: str, leader: Optional[str], members: Optional[list[str]], version: Optional[int]
    ) -> Response[scanlator_group.GetSingleScanlationGroupResponse]:
        route = Route("POST", "/group")

        query = {}
        query["name"] = name

        if leader:
            query["leader"] = leader

        if members:
            query["members"] = members

        if version:
            query["version"] = version

        return self.request(route, json=query)

    def _view_scanlation_group(
        self, scanlation_group_id: str, /
    ) -> Response[scanlator_group.GetSingleScanlationGroupResponse]:
        route = Route("GET", "/group/{scanlation_group_id}", scanlation_group_id=scanlation_group_id)
        return self.request(route)

    def _update_scanlation_group(
        self,
        scanlation_group_id: str,
        /,
        *,
        name: Optional[str],
        leader: Optional[str],
        members: Optional[list[str]],
        website: Optional[str],
        irc_server: Optional[str],
        irc_channel: Optional[str],
        discord: Optional[str],
        contact_email: Optional[str],
        description: Optional[str],
        locked: Optional[bool],
        version: int,
    ) -> Response[scanlator_group.GetSingleScanlationGroupResponse]:
        route = Route("PUT", "/group/{scanlation_group_id}", scanlation_group_id=scanlation_group_id)

        query = {}
        query["version"] = version

        if name:
            query["name"] = name

        if leader:
            query["leader"] = leader

        if members:
            query["members"] = members

        if website is not MISSING:
            query["website"] = website

        if irc_server is not MISSING:
            query["ircServer"] = irc_server

        if irc_channel is not MISSING:
            query["ircChannel"] = irc_channel

        if discord is not MISSING:
            query["discord"] = discord

        if contact_email is not MISSING:
            query["contactEmail"] = contact_email

        if description is not MISSING:
            query["description"] = description

        if locked:
            query["locked"] = str(locked).lower()

        return self.request(route, json=query)

    def _delete_scanlation_group(self, scanlation_group_id: str, /) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("DELETE", "/group/{scanlation_group_id}", scanlation_group_id=scanlation_group_id)
        return self.request(route)

    def _follow_scanlation_group(self, scanlation_group_id: str, /) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("POST", "/group/{scanlation_group_id}/follow", scanlation_group_id=scanlation_group_id)
        return self.request(route)

    def _unfollow_scanlation_group(self, scanlation_group_id: str, /) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("DELETE", "/group/{scanlation_group_id}/follow", scanlation_group_id=scanlation_group_id)
        return self.request(route)

    def _author_list(
        self,
        *,
        limit: int,
        offset: int,
        ids: Optional[list[str]],
        name: Optional[str],
        order: Optional[author.AuthorOrderQuery],
        includes: Optional[list[author.AuthorIncludes]],
    ) -> Response[author.GetMultiAuthorResponse]:
        route = Route("GET", "/author")

        query = {}
        query["limit"] = limit
        query["offset"] = offset

        if ids:
            query["ids"] = ids

        if name:
            query["name"] = name

        if order:
            query["order"] = order

        if includes:
            query["includes"] = includes

        resolved_query = php_query_builder(query)

        return self.request(route, params=resolved_query)

    def _create_author(self, *, name: str, version: Optional[int]) -> Response[author.GetSingleAuthorResponse]:
        route = Route("POST", "/author")
        query = {}

        query["name"] = name
        if version:
            query["version"] = version

        return self.request(route, json=query)

    def _get_author(
        self, author_id: str, /, *, includes: Optional[list[author.AuthorIncludes]]
    ) -> Response[author.GetSingleAuthorResponse]:
        route = Route("GET", "/author/{author_id}", author_id=author_id)

        query = {}

        if includes:
            query["includes"] = includes

        resolved_query = php_query_builder(query)

        return self.request(route, params=resolved_query)

    def _get_artist(
        self, author_id: str, /, *, includes: Optional[list[artist.ArtistIncludes]]
    ) -> Response[artist.GetSingleArtistResponse]:
        route = Route("GET", "/author/{author_id}", author_id=author_id)

        query = {}

        if includes:
            query["includes"] = includes

        resolved_query = php_query_builder(query)

        return self.request(route, params=resolved_query)

    def _update_author(self, author_id, /, *, name: Optional[str], version: int) -> Response[author.GetSingleAuthorResponse]:
        route = Route("PUT", "/author/{author_id}", author_id=author_id)

        query = {}
        query["version"] = version

        if name:
            query["name"] = name

        return self.request(route, json=query)

    def _delete_author(self, author_id: str, /) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("DELETE", "/author/{author_id}", author_id=author_id)
        return self.request(route)

    def _get_report_reason_list(
        self, report_category: report.ReportCategory, /
    ) -> Response[report.GetReportReasonListResponse]:
        route = Route("GET", "/report/reasons/{report_category}", report_category=report_category)
        return self.request(route)

    def _create_report(
        self,
        *,
        report_category: Optional[report.ReportCategory],
        reason: Optional[str],
        object_id: Optional[str],
        details: Optional[str],
    ) -> Response[dict[Literal["result"], Literal["ok", "error"]]]:
        route = Route("POST", "/report")

        query = {}

        if report_category:
            query["category"] = report_category

        if reason:
            query["reason"] = reason

        if object_id:
            query["objectId"] = object_id

        if details:
            query["details"] = details

        return self.request(route, json=query)
