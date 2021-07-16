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
import sys
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

from . import __version__, utils
from .errors import (
    APIException,
    BadRequest,
    Forbidden,
    LoginError,
    NotFound,
    RefreshError,
    Unauthorized,
)
from .utils import MISSING


if TYPE_CHECKING:
    from .tags import QueryTags
    from .types import manga
    from .types.auth import CheckPayload, LoginPayload, RefreshPayload
    from .types.author import GetAuthorResponse
    from .types.chapter import GetChapterFeedResponse
    from .types.common import LocalisedString
    from .types.cover import GetCoverResponse
    from .types.query import GetUserFeedQuery
    from .types.tags import GetTagListResponse

    T = TypeVar("T")
    Response = Coroutine[Any, Any, T]

__all__ = ("HTTPClient", "Route")

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel("DEBUG")
EPOCH = datetime.datetime.fromtimestamp(0)
TAGS = utils.TAGS


async def json_or_text(response: aiohttp.ClientResponse) -> Union[dict[str, Any], str]:
    text = await response.text(encoding="utf-8")
    try:
        if response.headers["content-type"] == "application/json":
            return json.loads(text)
    except KeyError:
        pass

    return text


def to_iso_format(in_: datetime.datetime) -> str:
    return f"{in_:%Y-%m-%dT%H:%M:%S}"


class Route:
    """A helper class for instanciating a HTTP method to MangaDex.

    Parameters
    -----------
    verb: :class:`str`
        The HTTP verb you wish to perform, e.g. ``"POST"``
    path: :class:`str`
        The prepended path to the API endpoing you with to target.
        e.g. ``"/manga/{manga_id}"``
    parameters: Any
        This is a special cased kwargs. Anything passed to these will substitude it's key to value in the `path`.
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

    async def _close(self) -> None:
        """|coro|

        This method will close the internal client session to ensure a clean exit.
        """

        if self.__session is not None:
            await self._logout()
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
            raise LoginError(response, text, response.status)

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
            raise RefreshError(response, text, response.status, self.__last_refresh)

        if data["result"] == "error":
            raise RefreshError(response, "The API reported an error when refreshing the token", 200, self.__last_refresh)

        self._token = data["token"]["session"]
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

            if response.status == 400:
                raise BadRequest(response, str(data))
            elif response.status == 401:
                raise Unauthorized(response, str(data))
            elif response.status == 403:
                raise Forbidden(response, str(data))
            elif response.status == 404:
                raise NotFound(response, str(data))
            raise APIException(response, str(data), response.status)

    def _update_tags(self) -> Response[list[GetTagListResponse]]:
        route = Route("GET", "/manga/tag")
        return self.request(route)

    def _get_author(self, author_id: str) -> Response[GetAuthorResponse]:
        route = Route("GET", "/author/{author_id}", author_id=author_id)
        return self.request(route)

    def _get_cover(self, cover_id: str, includes: list[str]) -> Response[GetCoverResponse]:
        route = Route("GET", "/cover/{cover_id}", cover_id=cover_id)

        query = {"includes": includes}
        resolved_query = utils.php_query_builder(query)

        return self.request(route, params=resolved_query)

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
            query["createdAtSince"] = to_iso_format(created_at_since)

        if updated_at_since:
            query["updatedAtSince"] = to_iso_format(updated_at_since)

        if published_at_since:
            query["publishAtSince"] = to_iso_format(published_at_since)

        if order:
            query["order"] = order

        resolved_query = utils.php_query_builder(query)

        return self.request(route, params=resolved_query)

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
            query["createdAtSince"] = to_iso_format(created_at_since)

        if updated_at_since:
            query["updatedAtSince"] = to_iso_format(updated_at_since)

        if order:
            query["order"] = order

        if includes:
            query["includes"] = includes

        resolved_query = utils.php_query_builder(query)

        LOGGER.debug(resolved_query)

        return self.request(route, params=resolved_query)

    def _create_manga(
        self,
        *,
        title: LocalisedString,
        alt_titles: Optional[list[LocalisedString]],
        description: Optional[LocalisedString],
        authors: Optional[list[str]],
        artists: Optional[list[str]],
        links: Optional[manga.MangaLinks],
        original_language: Optional[str],
        last_volume: Optional[str],
        last_chapter: Optional[str],
        publication_demographic: Optional[manga.PublicationDemographic],
        status: Optional[manga.MangaStatus],
        year: Optional[int],
        content_rating: Optional[manga.ContentRating],
        tags: Optional[QueryTags],
        mod_notes: Optional[str],
        version: int,
    ) -> Response[manga.ViewMangaResponse]:

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

        resolved_query = utils.php_query_builder(query)

        route = Route("POST", "/manga")
        return self.request(route, params=resolved_query)

    def _get_manga_volumes_and_chapters(
        self, *, manga_id: str, translated_languages: Optional[list[str]] = None
    ) -> Response[manga.GetMangaVolumesAndChaptersResponse]:
        ...

        route = Route("GET", "/manga/{manga_id}/aggregate", manga_id=manga_id)

        if translated_languages:
            query = utils.php_query_builder({"translatedLanguage": translated_languages})
            return self.request(route, params=query)
        return self.request(route)

    def _view_manga(self, manga_id: str, includes: Optional[list[str]]) -> Response[manga.ViewMangaResponse]:
        route = Route("GET", "/manga/{manga_id}", manga_id=manga_id)

        includes = includes or ["artist", "cover_url", "author"]
        query = utils.php_query_builder({"includes": includes})
        data = self.request(route, params=query)

        return data

    def _update_manga(
        self,
        manga_id: str,
        *,
        title: Optional[LocalisedString],
        alt_titles: Optional[list[LocalisedString]],
        description: Optional[LocalisedString],
        authors: Optional[list[str]],
        artists: Optional[list[str]],
        links: Optional[manga.MangaLinks],
        original_language: Optional[str],
        last_volume: Optional[str],
        last_chapter: Optional[str],
        publication_demographic: Optional[manga.PublicationDemographic],
        status: Optional[manga.MangaStatus],
        year: Optional[int],
        content_rating: Optional[manga.ContentRating],
        tags: Optional[QueryTags],
        mod_notes: Optional[str],
        version: int,
    ) -> Response[manga.ViewMangaResponse]:
        route = Route("PUT", "/manga/{manga_id}", manga_id=manga_id)

        query = {}
        query["version"] = version

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

        if status is not MISSING:
            query["status"] = status

        if year is not MISSING:
            query["year"] = year

        if content_rating:
            query["contentRating"] = content_rating

        if tags:
            query["tags"] = tags.tags

        if mod_notes is not MISSING:
            query["modNotes"] = mod_notes

        resolved_query = utils.php_query_builder(query)

        return self.request(route, json=resolved_query)

    def _delete_manga(self, manga_id: str, /) -> Response[dict[str, Literal["ok", "error"]]]:
        route = Route("DELETE", "/manga/{manga_id}", manga_id=manga_id)
        return self.request(route)

    async def delete_manga(self, manga_id: str, /) -> dict[str, Literal["ok", "error"]]:
        """|coro|

        This method will delete a Manga from the MangaDex API.

        Parameters
        -----------
        manga_id: :class:`str`
            The UUID of the manga to delete.

        Raises
        -------
        Forbidden
            The update errored due to authentication failure.
        NotFound
            The specified manga does not exist.

        Returns
        --------
        Dict[str, Literal[``"ok"``, ``"error"``]]:
            The response payload.
        """
        data = await self._delete_manga(manga_id)

        return data

    def _unfollow_manga(self, manga_id: str, /) -> Response[dict[str, Literal["ok", "error"]]]:
        route = Route("DELETE", "/manga/{manga_id}/follow", manga_id=manga_id)
        return self.request(route)

    def _follow_manga(self, manga_id: str, /) -> Response[dict[str, Literal["ok", "error"]]]:
        route = Route("POST", "/manga/{manga_id}/follow", manga_id=manga_id)
        return self.request(route)

    def _manga_feed(
        self,
        manga_id: str,
        /,
        *,
        limit: int,
        offset: int,
        translated_languages: Optional[list[str]],
        created_at_since: Optional[datetime.datetime],
        updated_at_since: Optional[datetime.datetime],
        published_at_since: Optional[datetime.datetime],
        order: Optional[manga.MangaOrderQuery],
        includes: Optional[list[manga.MangaIncludes]],
    ) -> Response[GetChapterFeedResponse]:
        route = Route("GET", "/manga/{manga_id}/feed", manga_id=manga_id)

        query = {}
        query["limit"] = limit
        query["offset"] = offset

        if translated_languages:
            query["translatedLanguage"] = translated_languages

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

        resolved_query = utils.php_query_builder(query)

        return self.request(route, params=resolved_query)

    def _get_random_manga(self, *, includes: Optional[list[manga.MangaIncludes]]) -> Response[manga.ViewMangaResponse]:
        route = Route("GET", "/manga/random")

        if includes:
            query = {"includes": includes}
            resolved_query = utils.php_query_builder(query)
            return self.request(route, params=resolved_query)

        return self.request(route)

    @overload
    def _manga_read_markers(
        self, manga_ids: list[str], /, *, grouped: Literal[True]
    ) -> Response[manga.MangaGroupedReadMarkersResponse]:
        ...

    @overload
    def _manga_read_markers(
        self, manga_ids: list[str], /, *, grouped: Literal[False]
    ) -> Response[manga.MangaReadMarkersResponse]:
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
        resolved_query = utils.php_query_builder(query)
        return self.request(route, params=resolved_query)

    def _get_manga_reading_status(self, manga_id: str, /) -> Response[manga.MangaReadingStatusResponse]:
        route = Route("GET", "/manga/{manga_id}/status", manga_id=manga_id)
        return self.request(route)

    def _update_manga_reading_status(
        self, manga_id: str, /, status: Optional[manga.ReadingStatus]
    ) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("POST", "/manga/{manga_id}/status", manga_id=manga_id)
        resolved_query = utils.php_query_builder({"status": status})
        return self.request(route, params=resolved_query)
