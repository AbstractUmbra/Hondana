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
import weakref
from base64 import b64decode
from typing import (
    TYPE_CHECKING,
    Any,
    Coroutine,
    Literal,
    Optional,
    Type,
    TypeVar,
    Union,
    overload,
)

import aiohttp

from . import __version__
from .enums import (
    ContentRating,
    CustomListVisibility,
    MangaRelationType,
    MangaState,
    MangaStatus,
    PublicationDemographic,
    ReadingStatus,
    ReportCategory,
)
from .errors import (
    APIException,
    BadRequest,
    Forbidden,
    MangaDexServerError,
    NotFound,
    Unauthorized,
)
from .utils import (
    MANGA_TAGS,
    MANGADEX_TIME_REGEX,
    MISSING,
    CustomRoute,
    Route,
    delta_to_iso,
    get_image_mime_type,
    json_or_text,
    php_query_builder,
    to_iso_format,
    to_json,
)


if TYPE_CHECKING:
    from types import TracebackType

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
        ScanlatorGroupIncludes,
        ScanlatorGroupListOrderQuery,
        UserListOrderQuery,
    )
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
        statistics,
        upload,
        user,
    )
    from .types.auth import CheckPayload
    from .types.tags import GetTagListResponse
    from .types.token import TokenPayload
    from .utils import CustomRoute

    T = TypeVar("T")
    Response = Coroutine[Any, Any, T]
    MU = TypeVar("MU", bound="MaybeUnlock")
    BE = TypeVar("BE", bound=BaseException)


LOGGER = logging.getLogger(__name__)
TAGS = MANGA_TAGS
MAX_DEPTH = 10_000


__all__ = ("HTTPClient",)


def calculate_limits(limit: int, offset: int, *, max_limit: int = 100) -> tuple[int, int]:
    """A helper function that will calculate the offset and limit parameters for API endpoints.

    Parameters
    -----------
    limit: :class:`int`
        The limit (or amount) of objects you are requesting.
    offset: :class:`int`
        The offset (or pagination start point) for the objects you are requesting.
    max_limit: :class:`int`
        The maximum limit value for the API Endpoint.

    Returns
    --------
    Tuple[:class:`int`, :class:`int`]
    """
    if offset == MAX_DEPTH:
        raise ValueError(f"An offset of {MAX_DEPTH} will not return results.")

    offset = max(offset, 0)

    difference = MAX_DEPTH - offset
    if difference <= max_limit:
        new_limit = difference
        new_offset = MAX_DEPTH - new_limit
        return new_limit, new_offset

    new_limit = min(max(1, limit), max_limit)
    new_offset = min(max(0, offset), MAX_DEPTH - new_limit)

    return new_limit, new_offset


class MaybeUnlock:
    def __init__(self, lock: asyncio.Lock) -> None:
        self.lock: asyncio.Lock = lock
        self._unlock: bool = True

    def __enter__(self: MU) -> MU:
        return self

    def defer(self) -> None:
        self._unlock = False

    def __exit__(
        self,
        exc_type: Optional[Type[BE]],
        exc: Optional[BE],
        traceback: Optional[TracebackType],
    ) -> None:
        if self._unlock:
            self.lock.release()


class HTTPClient:
    __slots__ = (
        "username",
        "email",
        "password",
        "_authenticated",
        "__session",
        "_locks",
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
        self.__session: Optional[aiohttp.ClientSession] = session
        self._locks: weakref.WeakValueDictionary = weakref.WeakValueDictionary()
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

    async def _get_token(self) -> str:
        """|coro|

        This private method will log in to MangaDex with the login username and password to retrieve a JWT auth token.

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
            data = await response.json()

        if response.status == 400:
            raise BadRequest(response, errors=data["errors"])
        elif response.status == 401:
            raise Unauthorized(response, errors=data["errors"])

        token = data["token"]["session"]
        refresh_token = data["token"]["refresh"]
        self.__last_refresh = self._get_expiry(token)
        self.__refresh_token = refresh_token
        return token

    def _get_expiry(self, token: str) -> datetime.datetime:
        payload = token.split(".")[1]
        padding = len(payload) % 4
        payload = b64decode(payload + "=" * padding)
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
            data = await response.json()

        assert self.__last_refresh is not None  # this will 100% be a `datetime` here, but type checker was crying

        if 400 <= response.status <= 510:
            if response.status == 400:
                raise BadRequest(response, errors=data["errors"])
            elif response.status == 401:
                raise Unauthorized(response, errors=data["errors"])
            elif response.status == 403:
                raise Forbidden(response, errors=data["errors"])
            else:
                raise APIException(response, status_code=response.status, errors=data["errors"])

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
            data: CheckPayload = await response.json()

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
            data = await response.json()

        if not (300 > response.status >= 200) or data["result"] != "ok":
            raise APIException(response, status_code=503, errors=data["errors"])

        self._authenticated = False

    async def request(self, route: Union[Route, CustomRoute], **kwargs: Any) -> Any:
        """|coro|

        This performs the HTTP request, handling authentication tokens when doing it.

        Parameters
        -----------
        route: Union[:class:`Route`, :class:`DownloadRoute`]
            The route describes the http verb and endpoint to hit.
            The request is the one that takes in the query params or request body.

        Raises
        -------
        :exc:`BadRequest`
            A request was malformed
        Unauthorized
            You attempted to use an endpoint you have no authorization for.
        :exc:`Forbidden`
            Your auth was not sufficient to perform this action.
        :exc:`NotFound`
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

        bucket = route.path
        lock = self._locks.get(bucket)
        if lock is None:
            lock = asyncio.Lock()
            self._locks[bucket] = lock

        headers = kwargs.pop("headers", {})
        token = await self._try_token() if self._authenticated else None

        if token is not None:
            headers["Authorization"] = f"Bearer {token}"
        headers["User-Agent"] = self.user_agent

        if "json" in kwargs:
            headers["Content-Type"] = "application/json"
            kwargs["data"] = to_json(kwargs.pop("json"))

        if "params" in kwargs:
            params = kwargs["params"]
            resolved_params = php_query_builder(params)
            kwargs["params"] = resolved_params

        kwargs["headers"] = headers

        LOGGER.debug("Current request headers: %s", headers)
        LOGGER.debug("Current request url: %s", route.url)
        if "params" in kwargs:
            LOGGER.debug("Current request parameters: %s", kwargs["params"])
        if "data" in kwargs:
            LOGGER.debug("Current json body is: %s", str(kwargs["data"]))

        response: Optional[aiohttp.ClientResponse] = None
        await lock.acquire()
        with MaybeUnlock(lock) as maybe_lock:
            for tries in range(5):
                try:
                    async with self.__session.request(route.verb, route.url, **kwargs) as response:
                        # Requests remaining before ratelimit
                        remaining = response.headers.get("x-ratelimit-remaining", None)
                        LOGGER.debug("remaining is: %s", remaining)
                        # Timestamp for when current ratelimit session(?) expires
                        retry = response.headers.get("x-ratelimit-retry-after", None)
                        LOGGER.debug("retry is: %s", retry)
                        if retry is not None:
                            retry = datetime.datetime.fromtimestamp(int(retry))
                        # The total ratelimit session hits
                        limit = response.headers.get("x-ratelimit-limit", None)
                        LOGGER.debug("limit is: %s", limit)

                        if remaining == "0" and response.status != 429:
                            assert retry is not None
                            delta = retry - datetime.datetime.now()
                            sleep = delta.total_seconds() + 1
                            LOGGER.warning("A ratelimit has been exhausted, sleeping for: %d", sleep)
                            maybe_lock.defer()
                            loop = asyncio.get_running_loop()
                            loop.call_later(sleep, lock.release)

                        if response.content_type in {"image/png", "image/gif", "image/jpeg", "image/jpg"}:
                            data = (await response.read(), response)
                        else:
                            data = await json_or_text(response)

                        if 300 > response.status >= 200:
                            return data

                        if response.status == 429:
                            assert retry is not None
                            delta = retry - datetime.datetime.now()
                            sleep = delta.total_seconds() + 1
                            LOGGER.warning("A ratelimit has been hit, sleeping for: %d", sleep)
                            await asyncio.sleep(sleep)
                            continue

                        if response.status == 412:
                            assert retry is not None
                            captcha = response.headers.get("x-captcha-sitekey")
                            if captcha is not None:
                                LOGGER.warning("Captcha required, key is: %s - trying now.", captcha)
                                kwargs["headers"]["X-Captcha-Result"] = captcha
                                continue

                        if response.status in {500, 502, 504}:
                            sleep_ = 1 + tries * 2
                            LOGGER.warning("Hit an API error, trying again in: %d", sleep_)
                            await asyncio.sleep(sleep_)
                            continue

                        assert isinstance(data, dict)
                        if response.status == 400:
                            raise BadRequest(response, errors=data["errors"])
                        elif response.status == 401:
                            raise Unauthorized(response, errors=data["errors"])
                        elif response.status == 403:
                            raise Forbidden(response, errors=data["errors"])
                        elif response.status == 404:
                            raise NotFound(response, errors=data["errors"])
                        raise APIException(
                            response,
                            status_code=response.status,
                            errors=data["errors"],
                        )
                except (aiohttp.ServerDisconnectedError, aiohttp.ServerTimeoutError) as error:
                    LOGGER.exception("Network error occurred: %s", error)
                    await asyncio.sleep(5)
                    continue

            if response is not None:
                if response.status >= 500:
                    raise MangaDexServerError(response, status_code=response.status)

                raise APIException(response, status_code=response.status, errors=[])

            raise RuntimeError("Unreachable code in HTTP handling.")

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
        status: Optional[list[MangaStatus]],
        original_language: Optional[list[common.LanguageCode]],
        excluded_original_language: Optional[list[common.LanguageCode]],
        available_translated_language: Optional[list[common.LanguageCode]],
        publication_demographic: Optional[list[PublicationDemographic]],
        ids: Optional[list[str]],
        content_rating: Optional[list[ContentRating]],
        created_at_since: Optional[datetime.datetime],
        updated_at_since: Optional[datetime.datetime],
        order: Optional[MangaListOrderQuery],
        includes: Optional[MangaIncludes],
        has_available_chapters: Optional[bool],
        group: Optional[str],
    ) -> Response[manga.MangaSearchResponse]:
        route = Route("GET", "/manga")

        limit, offset = calculate_limits(limit, offset, max_limit=100)

        query: dict[str, Any] = {"limit": limit, "offset": offset}

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
            query["order"] = order._to_dict()

        if includes:
            query["includes"] = includes.to_query()

        if has_available_chapters is not None:
            query["hasAvailableChapters"] = has_available_chapters

        if group:
            query["group"] = group

        return self.request(route, params=query)

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
        publication_demographic: Optional[PublicationDemographic],
        status: Optional[MangaStatus],
        year: Optional[int],
        content_rating: ContentRating,
        tags: Optional[QueryTags],
        mod_notes: Optional[str],
        version: int,
    ) -> Response[manga.GetMangaResponse]:
        route = Route("POST", "/manga")

        query: dict[str, Any] = {"title": title, "version": version}

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
            query["publicationDemographic"] = publication_demographic.value

        if status:
            query["status"] = status.value

        if year:
            query["year"] = year

        if content_rating:
            query["contentRating"] = content_rating.value

        if tags:
            query["tags"] = tags.tags

        if mod_notes:
            query["modNotes"] = mod_notes

        return self.request(route, json=query)

    def _get_manga_volumes_and_chapters(
        self,
        *,
        manga_id: str,
        translated_language: Optional[list[str]],
        groups: Optional[list[str]],
    ) -> Response[manga.GetMangaVolumesAndChaptersResponse]:
        route = Route("GET", "/manga/{manga_id}/aggregate", manga_id=manga_id)

        query: dict[str, Any] = {}

        if translated_language:
            query["translatedLanguage"] = translated_language

        if groups:
            query["groups"] = groups

        if query:
            return self.request(route, params=query)
        return self.request(route)

    def _view_manga(self, manga_id: str, /, *, includes: Optional[MangaIncludes]) -> Response[manga.GetMangaResponse]:
        route = Route("GET", "/manga/{manga_id}", manga_id=manga_id)

        if includes:
            query: dict[str, list[str]] = {"includes": includes.to_query()}
            return self.request(route, params=query)
        return self.request(route)

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
        publication_demographic: Optional[PublicationDemographic],
        status: Optional[MangaStatus],
        year: Optional[int],
        content_rating: Optional[ContentRating],
        tags: Optional[QueryTags],
        primary_cover: Optional[str],
        version: int,
    ) -> Response[manga.GetMangaResponse]:
        route = Route("PUT", "/manga/{manga_id}", manga_id=manga_id)

        query: dict[str, Any] = {"version": version}

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
            if isinstance(publication_demographic, PublicationDemographic):
                query["publicationDemographic"] = publication_demographic.value
            else:
                query["publicationDemographic"] = publication_demographic

        if status:
            query["status"] = status

        if year is not MISSING:
            query["year"] = year

        if content_rating:
            query["contentRating"] = content_rating.value

        if tags:
            query["tags"] = tags.tags

        if primary_cover is not MISSING:
            query["primaryCover"] = primary_cover

        return self.request(route, json=query)

    def _manga_feed(
        self,
        manga_id: Optional[str],
        /,
        *,
        limit: int,
        offset: int,
        translated_language: Optional[list[common.LanguageCode]],
        original_language: Optional[list[common.LanguageCode]],
        excluded_original_language: Optional[list[common.LanguageCode]],
        content_rating: Optional[list[ContentRating]],
        excluded_groups: Optional[list[str]],
        excluded_uploaders: Optional[list[str]],
        include_future_updates: Optional[bool],
        created_at_since: Optional[datetime.datetime],
        updated_at_since: Optional[datetime.datetime],
        published_at_since: Optional[datetime.datetime],
        order: Optional[FeedOrderQuery],
        includes: Optional[ChapterIncludes],
    ) -> Response[chapter.GetMultiChapterResponse]:
        if manga_id is None:
            route = Route("GET", "/user/follows/manga/feed")
        else:
            route = Route("GET", "/manga/{manga_id}/feed", manga_id=manga_id)

        limit, offset = calculate_limits(limit, offset, max_limit=500)

        query: dict[str, Any] = {"limit": limit, "offset": offset}

        if translated_language:
            query["translatedLanguage"] = translated_language

        if original_language:
            query["originalLanguage"] = original_language

        if excluded_original_language:
            query["excludedOriginalLanguage"] = excluded_original_language

        if content_rating:
            query["contentRating"] = content_rating

        if excluded_groups:
            query["excludedGroups"] = excluded_groups

        if excluded_uploaders:
            query["excludedUploaders"] = excluded_uploaders

        if include_future_updates:
            resolved = str(int(include_future_updates))
            query["includeFutureUpdates"] = resolved

        if created_at_since:
            query["createdAtSince"] = to_iso_format(created_at_since)

        if updated_at_since:
            query["updatedAtSince"] = to_iso_format(updated_at_since)

        if published_at_since:
            query["publishAtSince"] = to_iso_format(published_at_since)

        if order:
            query["order"] = order._to_dict()

        if includes:
            query["includes"] = includes.to_query()

        return self.request(route, params=query)

    def _delete_manga(self, manga_id: str, /) -> Response[dict[str, Literal["ok", "error"]]]:
        route = Route("DELETE", "/manga/{manga_id}", manga_id=manga_id)
        return self.request(route)

    def _unfollow_manga(self, manga_id: str, /) -> Response[dict[str, Literal["ok", "error"]]]:
        route = Route("DELETE", "/manga/{manga_id}/follow", manga_id=manga_id)
        return self.request(route)

    def _follow_manga(self, manga_id: str, /) -> Response[dict[str, Literal["ok", "error"]]]:
        route = Route("POST", "/manga/{manga_id}/follow", manga_id=manga_id)
        return self.request(route)

    def _get_random_manga(self, *, includes: Optional[MangaIncludes]) -> Response[manga.GetMangaResponse]:
        route = Route("GET", "/manga/random")

        if includes:
            query: dict[str, list[str]] = {"includes": includes.to_query()}
            return self.request(route, params=query)
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
        query: dict[str, Any] = {"ids": manga_ids, "grouped": True}
        return self.request(route, params=query)

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

    def _get_all_manga_reading_status(
        self, *, status: Optional[ReadingStatus] = None
    ) -> Response[manga.MangaMultipleReadingStatusResponse]:
        route = Route("GET", "/manga/status")
        if status:
            query: dict[str, Any] = {"status": status.value}
            return self.request(route, params=query)
        return self.request(route)

    def _get_manga_reading_status(self, manga_id: str, /) -> Response[manga.MangaSingleReadingStatusResponse]:
        route = Route("GET", "/manga/{manga_id}/status", manga_id=manga_id)
        return self.request(route)

    def _update_manga_reading_status(
        self, manga_id: str, /, status: ReadingStatus
    ) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("POST", "/manga/{manga_id}/status", manga_id=manga_id)
        query: dict[str, Any] = {"status": status.value}
        return self.request(route, params=query)

    def _get_manga_draft(self, manga_id: str, /) -> Response[manga.GetMangaResponse]:
        route = Route("GET", "/manga/draft/{manga_id}", manga_id=manga_id)
        return self.request(route)

    def _submit_manga_draft(self, manga_id: str, /, version: Optional[int]) -> Response[manga.GetMangaResponse]:
        route = Route("POST", "/manga/draft/{manga_id}/commit", manga_id=manga_id)
        query: dict[str, Any] = {"version": version}
        return self.request(route, json=query)

    def _get_manga_draft_list(
        self,
        *,
        limit: int,
        offset: int,
        state: Optional[MangaState] = None,
        order: Optional[MangaDraftListOrderQuery] = None,
        includes: Optional[MangaIncludes],
    ) -> Response[manga.GetMangaResponse]:
        route = Route("GET", "/manga/draft")

        limit, offset = calculate_limits(limit, offset, max_limit=100)

        query: dict[str, Any] = {"limit": limit, "offset": offset}

        if state:
            query["state"] = state.value

        if order:
            query["order"] = order._to_dict()

        if includes:
            query["includes"] = includes.to_query()

        return self.request(route, params=query)

    def _get_manga_relation_list(
        self, manga_id: str, /, *, includes: Optional[MangaIncludes]
    ) -> Response[manga.MangaRelationResponse]:
        route = Route("GET", "/manga/{manga_id}/relation", manga_id=manga_id)

        if includes:
            query: dict[str, Any] = {"includes": includes.to_query()}
            return self.request(route, params=query)

        return self.request(route)

    def _create_manga_relation(
        self, manga_id: str, /, *, target_manga: str, relation_type: MangaRelationType
    ) -> Response[manga.MangaRelationCreateResponse]:
        route = Route("POST", "/manga/{manga_id}/relation", manga_id=manga_id)
        query: dict[str, Any] = {"targetManga": target_manga, "relation": relation_type.value}
        return self.request(route, json=query)

    def _delete_manga_relation(self, manga_id: str, relation_id: str, /) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("DELETE", "/manga/{manga_id}/relation/{relation_id}", manga_id=manga_id, relation_id=relation_id)
        return self.request(route)

    def _chapter_list(
        self,
        *,
        limit: int,
        offset: int,
        ids: Optional[list[str]],
        title: Optional[str],
        groups: Optional[list[str]],
        uploader: Optional[Union[str, list[str]]],
        manga: Optional[str],
        volume: Optional[Union[str, list[str]]],
        chapter: Optional[Union[str, list[str]]],
        translated_language: Optional[list[common.LanguageCode]],
        original_language: Optional[list[common.LanguageCode]],
        excluded_original_language: Optional[list[common.LanguageCode]],
        content_rating: Optional[list[ContentRating]],
        excluded_groups: Optional[list[str]],
        excluded_uploaders: Optional[list[str]],
        include_future_updates: Optional[bool],
        created_at_since: Optional[datetime.datetime],
        updated_at_since: Optional[datetime.datetime],
        published_at_since: Optional[datetime.datetime],
        order: Optional[FeedOrderQuery],
        includes: Optional[ChapterIncludes],
    ) -> Response[chapter.GetMultiChapterResponse]:
        route = Route("GET", "/chapter")

        limit, offset = calculate_limits(limit, offset, max_limit=100)

        query: dict[str, Any] = {"limit": limit, "offset": offset}

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

        if excluded_groups:
            query["excludedGroups"] = excluded_groups

        if excluded_uploaders:
            query["excludedUploaders"] = excluded_uploaders

        if include_future_updates:
            resolved = str(int(include_future_updates))
            query["includeFutureUpdates"] = resolved

        if created_at_since:
            query["createdAtSince"] = to_iso_format(created_at_since)

        if updated_at_since:
            query["updatedAtSince"] = to_iso_format(updated_at_since)

        if published_at_since:
            query["publishedAtSince"] = to_iso_format(published_at_since)

        if order:
            query["order"] = order._to_dict()

        if includes:
            query["includes"] = includes.to_query()

        return self.request(route, params=query)

    def _get_chapter(
        self, chapter_id: str, /, *, includes: Optional[ChapterIncludes]
    ) -> Response[chapter.GetSingleChapterResponse]:
        route = Route("GET", "/chapter/{chapter_id}", chapter_id=chapter_id)

        if includes:
            return self.request(route, params={"includes": includes})
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

        query: dict[str, Any] = {"version": version}

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
        order: Optional[CoverArtListOrderQuery],
        includes: Optional[CoverIncludes],
    ) -> Response[cover.GetMultiCoverResponse]:
        route = Route("GET", "/cover")

        limit, offset = calculate_limits(limit, offset, max_limit=100)

        query: dict[str, Any] = {"limit": limit, "offset": offset}

        if manga:
            query["manga"] = manga

        if ids:
            query["ids"] = ids

        if uploaders:
            query["uploaders"] = uploaders

        if order:
            query["order"] = order._to_dict()

        if includes:
            query["includes"] = includes.to_query()

        return self.request(route, params=query)

    def _upload_cover(
        self, manga_id: str, /, *, cover: bytes, volume: Optional[str], description: Optional[str]
    ) -> Response[cover.GetSingleCoverResponse]:
        route = Route("POST", "/cover/{manga_id}", manga_id=manga_id)
        content_type = get_image_mime_type(cover)
        ext = content_type.split("/")[-1]
        form_data = aiohttp.FormData()
        form_data.add_field(name="file", filename=f"cover.{ext}", value=cover, content_type=content_type)
        form_data.add_field(name="volume", value=volume)
        form_data.add_field(name="description", value=description)
        return self.request(route, data=form_data)

    def _get_cover(self, cover_id: str, /, *, includes: Optional[CoverIncludes]) -> Response[cover.GetSingleCoverResponse]:
        route = Route("GET", "/cover/{cover_id}", cover_id=cover_id)

        if includes:
            query: dict[str, list[str]] = {"includes": includes.to_query()}
            return self.request(route, params=query)
        return self.request(route)

    def _edit_cover(
        self, cover_id: str, /, *, volume: Optional[str] = MISSING, description: Optional[str], version: int
    ) -> Response[cover.GetSingleCoverResponse]:
        route = Route("PUT", "/cover/{cover_id}", cover_id=cover_id)

        query: dict[str, Any] = {"version": version}

        if volume is MISSING:
            raise TypeError("`volume` key must be a value of `str` or `NoneType`.")

        query["volume"] = volume

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
        focused_language: Optional[common.LanguageCode],
        includes: Optional[ScanlatorGroupIncludes],
        order: Optional[ScanlatorGroupListOrderQuery],
    ) -> Response[scanlator_group.GetMultiScanlationGroupResponse]:
        route = Route("GET", "/group")

        limit, offset = calculate_limits(limit, offset, max_limit=100)

        query: dict[str, Any] = {"limit": limit, "offset": offset}

        if ids:
            query["ids"] = ids

        if name:
            query["name"] = name

        if focused_language:
            query["focusedLanguage"] = focused_language

        if includes:
            query["includes"] = includes.to_query()

        if order:
            query["order"] = order._to_dict()

        return self.request(route, params=query)

    def _user_list(
        self,
        *,
        limit: int,
        offset: int,
        ids: Optional[list[str]],
        username: Optional[str],
        order: Optional[UserListOrderQuery],
    ) -> Response[user.GetMultiUserResponse]:
        route = Route("GET", "/user")

        limit, offset = calculate_limits(limit, offset, max_limit=100)

        query: dict[str, Any] = {"limit": limit, "offset": offset}

        if ids:
            query["ids"] = ids

        if username:
            query["username"] = username

        if order:
            query["order"] = order._to_dict()

        return self.request(route, params=query)

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
        query: dict[str, Any] = {"oldPassword": old_password, "newPassword": new_password}
        return self.request(route, json=query)

    def _update_user_email(self, email: str, /) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("POST", "/user/email")
        query: dict[str, Any] = {"email": email}
        return self.request(route, json=query)

    def _get_my_details(self) -> Response[user.GetSingleUserResponse]:
        route = Route("GET", "/user/me")
        return self.request(route)

    def _get_my_followed_groups(
        self, *, limit: int, offset: int
    ) -> Response[scanlator_group.GetMultiScanlationGroupResponse]:
        route = Route("GET", "/user/follows/group")

        limit, offset = calculate_limits(limit, offset, max_limit=100)

        query: dict[str, Any] = {"limit": limit, "offset": offset}
        return self.request(route, params=query)

    def _check_if_following_group(self, group_id: str, /) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("GET", "/user/follows/group/{group_id}", group_id=group_id)
        return self.request(route)

    def _get_my_followed_users(self, *, limit: int, offset: int) -> Response[user.GetMultiUserResponse]:
        route = Route("GET", "/user/follows/user")

        limit, offset = calculate_limits(limit, offset, max_limit=100)

        query: dict[str, Any] = {"limit": limit, "offset": offset}

        return self.request(route, params=query)

    def _check_if_following_user(self, user_id: str, /) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("GET", "/user/follows/user/{user_id}", user_id=user_id)
        return self.request(route)

    def _check_if_following_manga(self, manga_id: str, /) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("GET", "/user/follows/manga/{manga_id}", manga_id=manga_id)
        return self.request(route)

    def _get_user_followed_manga(
        self, limit: int, offset: int, includes: Optional[MangaIncludes]
    ) -> Response[manga.MangaSearchResponse]:
        route = Route("GET", "/user/follows/manga")

        query: dict[str, Any] = {"limit": limit, "offset": offset}

        if includes:
            query["includes"] = includes.to_query()

        return self.request(route, params=query)

    def _create_account(self, *, username: str, password: str, email: str) -> Response[user.GetSingleUserResponse]:
        route = Route("POST", "/account/create")
        query: dict[str, Any] = {"username": username, "password": password, "email": email}
        return self.request(route, json=query)

    def _activate_account(self, activation_code: str, /) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("POST", "/account/activate/{activation_code}", activation_code=activation_code)
        return self.request(route)

    def _resend_activation_code(self, email: str, /) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("POST", "/account/activate/resend")
        query: dict[str, Any] = {"email": email}
        return self.request(route, json=query)

    def _recover_account(self, email: str, /) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("POST", "/account/recover")
        query: dict[str, Any] = {"email": email}
        return self.request(route, json=query)

    def _complete_account_recovery(
        self, recovery_code: str, /, *, new_password: str
    ) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("POST", "/account/recover/{recovery_code}", recovery_code=recovery_code)
        query: dict[str, Any] = {"newPassword": new_password}
        return self.request(route, json=query)

    def _ping_the_server(self) -> Response[str]:
        route = Route("GET", "/ping")
        return self.request(route)

    def _legacy_id_mapping(
        self, type: legacy.LegacyMappingType, /, *, item_ids: list[int]
    ) -> Response[legacy.GetLegacyMappingResponse]:
        route = Route("POST", "/legacy/mapping")
        query: dict[str, Any] = {"type": type, "ids": item_ids}
        return self.request(route, json=query)

    def _get_at_home_url(self, chapter_id: str, /, *, ssl: bool) -> Response[chapter.GetAtHomeResponse]:
        route = Route("GET", "/at-home/server/{chapter_id}", chapter_id=chapter_id)
        query: dict[str, Any] = {"forcePort443": str(ssl).lower()}
        return self.request(route, params=query)

    def _create_custom_list(
        self,
        *,
        name: str,
        visibility: Optional[CustomListVisibility],
        manga: Optional[list[str]],
        version: Optional[int],
    ) -> Response[custom_list.GetSingleCustomListResponse]:
        route = Route("POST", "/list")

        query: dict[str, Any] = {"name": name}

        if visibility:
            query["visibility"] = visibility.value

        if manga:
            query["manga"] = manga

        if version:
            query["version"] = version

        return self.request(route, json=query)

    def _get_custom_list(
        self, custom_list_id: str, /, *, includes: Optional[CustomListIncludes]
    ) -> Response[custom_list.GetSingleCustomListResponse]:
        route = Route("GET", "/list/{custom_list_id}", custom_list_id=custom_list_id)

        if includes:
            query: dict[str, list[str]] = {"includes": includes.to_query()}
            return self.request(route, params=query)
        return self.request(route)

    def _update_custom_list(
        self,
        custom_list_id,
        /,
        *,
        name: Optional[str],
        visibility: Optional[CustomListVisibility],
        manga: Optional[list[str]],
        version: int,
    ) -> Response[custom_list.GetSingleCustomListResponse]:
        route = Route("POST", "/list/{custom_list_id}", custom_list_id=custom_list_id)

        query: dict[str, Any] = {"version": version}

        if name:
            query["name"] = name

        if visibility:
            query["visibility"] = visibility.value

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

        query: dict[str, Any] = {"limit": limit, "offset": offset}

        return self.request(route, params=query)

    def _get_users_custom_lists(
        self, user_id: str, /, *, limit: int, offset: int
    ) -> Response[custom_list.GetMultiCustomListResponse]:
        route = Route("GET", "/user/{user_id}/list", user_id=user_id)

        query: dict[str, Any] = {"limit": limit, "offset": offset}

        return self.request(route, params=query)

    def _custom_list_manga_feed(
        self,
        custom_list_id: str,
        /,
        *,
        limit: int,
        offset: int,
        translated_language: Optional[list[common.LanguageCode]],
        original_language: Optional[list[common.LanguageCode]],
        excluded_original_language: Optional[list[common.LanguageCode]],
        content_rating: Optional[list[ContentRating]],
        excluded_groups: Optional[list[str]],
        excluded_uploaders: Optional[list[str]],
        include_future_updates: Optional[bool],
        created_at_since: Optional[datetime.datetime],
        updated_at_since: Optional[datetime.datetime],
        published_at_since: Optional[datetime.datetime],
        order: Optional[FeedOrderQuery],
    ) -> Response[chapter.GetMultiChapterResponse]:
        route = Route("GET", "/list/{custom_list_id}/feed", custom_list_id=custom_list_id)

        limit, offset = calculate_limits(limit, offset, max_limit=500)

        query: dict[str, Any] = {"limit": limit, "offset": offset}

        if translated_language:
            query["translatedLanguage"] = translated_language

        if original_language:
            query["originalLanguage"] = original_language

        if excluded_original_language:
            query["excludedOriginalLanguage"] = excluded_original_language

        if content_rating:
            query["contentRating"] = content_rating

        if excluded_groups:
            query["excludedGroups"] = excluded_groups

        if excluded_uploaders:
            query["excludedUploaders"] = excluded_uploaders

        if include_future_updates:
            resolved = str(int(include_future_updates))
            query["includeFutureUpdates"] = resolved

        if created_at_since:
            query["createdAtSince"] = to_iso_format(created_at_since)

        if updated_at_since:
            query["updatedAtSince"] = to_iso_format(updated_at_since)

        if published_at_since:
            query["publishAtSince"] = to_iso_format(published_at_since)

        if order:
            query["order"] = order._to_dict()

        return self.request(route, params=query)

    def _create_scanlation_group(
        self,
        *,
        name: str,
        website: Optional[str],
        irc_server: Optional[str],
        irc_channel: Optional[str],
        discord: Optional[str],
        contact_email: Optional[str],
        description: Optional[str],
        twitter: Optional[str],
        inactive: Optional[bool],
        publish_delay: Optional[Union[str, datetime.timedelta]],
    ) -> Response[scanlator_group.GetSingleScanlationGroupResponse]:
        route = Route("POST", "/group")

        query: dict[str, Any] = {"name": name}

        if website:
            query["website"] = website

        if irc_server:
            query["ircServer"] = irc_server

        if irc_channel:
            query["ircChannel"] = irc_channel

        if discord:
            query["discord"] = discord

        if contact_email:
            query["contactEmail"] = contact_email

        if description:
            query["description"] = description

        if twitter:
            query["twitter"] = twitter

        if isinstance(inactive, bool):
            query["inactive"] = inactive

        if publish_delay:
            if isinstance(publish_delay, datetime.timedelta):
                publish_delay = delta_to_iso(publish_delay)

            if not MANGADEX_TIME_REGEX.fullmatch(publish_delay):
                raise ValueError("The `publish_delay` parameter must match the regex format.")

            query["publishDelay"] = publish_delay

        return self.request(route, json=query)

    def _view_scanlation_group(
        self, scanlation_group_id: str, /, *, includes: Optional[ScanlatorGroupIncludes]
    ) -> Response[scanlator_group.GetSingleScanlationGroupResponse]:
        route = Route("GET", "/group/{scanlation_group_id}", scanlation_group_id=scanlation_group_id)

        if includes:
            query: dict[str, list[str]] = {"includes": includes.to_query()}
            return self.request(route, params=query)
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
        twitter: Optional[str],
        focused_languages: Optional[list[common.LanguageCode]],
        inactive: Optional[bool],
        locked: Optional[bool],
        publish_delay: Optional[Union[str, datetime.timedelta]],
        version: int,
    ) -> Response[scanlator_group.GetSingleScanlationGroupResponse]:
        route = Route("PUT", "/group/{scanlation_group_id}", scanlation_group_id=scanlation_group_id)

        query: dict[str, Any] = {"version": version}

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

        if twitter is not MISSING:
            query["twitter"] = twitter

        if focused_languages is not MISSING:
            query["focusedLanguages"] = focused_languages

        if publish_delay:
            if isinstance(publish_delay, datetime.timedelta):
                publish_delay = delta_to_iso(publish_delay)

            if not MANGADEX_TIME_REGEX.fullmatch(publish_delay):
                raise ValueError("The `publish_at` parameter's string must match the regex pattern.")

            query["publishDelay"] = publish_delay

        if isinstance(inactive, bool):
            query["inactive"] = inactive

        if isinstance(locked, bool):
            query["locked"] = locked

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
        order: Optional[AuthorListOrderQuery],
        includes: Optional[AuthorIncludes],
    ) -> Response[author.GetMultiAuthorResponse]:
        route = Route("GET", "/author")

        limit, offset = calculate_limits(limit, offset, max_limit=100)

        query: dict[str, Any] = {"limit": limit, "offset": offset}

        if ids:
            query["ids"] = ids

        if name:
            query["name"] = name

        if order:
            query["order"] = order._to_dict()

        if includes:
            query["includes"] = includes.to_query()

        return self.request(route, params=query)

    def _create_author(
        self,
        *,
        name: str,
        biography: Optional[common.LocalisedString],
        twitter: str,
        pixiv: str,
        melon_book: str,
        fan_box: str,
        booth: str,
        nico_video: str,
        skeb: str,
        fantia: str,
        tumblr: str,
        youtube: str,
        website: str,
        version: Optional[int],
    ) -> Response[author.GetSingleAuthorResponse]:
        route = Route("POST", "/author")

        query: dict[str, Any] = {"name": name}

        if biography is not None:
            query["biography"] = biography

        if twitter is not MISSING:
            query["twitter"] = twitter

        if pixiv is not MISSING:
            query["pixiv"] = pixiv

        if melon_book is not MISSING:
            query["melonBook"] = melon_book

        if fan_box is not MISSING:
            query["fanBox"] = fan_box

        if booth is not MISSING:
            query["booth"] = booth

        if nico_video is not MISSING:
            query["nicoVideo"] = nico_video

        if skeb is not MISSING:
            query["skeb"] = skeb

        if fantia is not MISSING:
            query["fantia"] = fantia

        if tumblr is not MISSING:
            query["tumblr"] = tumblr

        if youtube is not MISSING:
            query["youtube"] = youtube

        if website is not MISSING:
            query["website"] = website

        if version:
            query["version"] = version

        return self.request(route, json=query)

    def _get_author(
        self, author_id: str, /, *, includes: Optional[AuthorIncludes]
    ) -> Response[author.GetSingleAuthorResponse]:
        route = Route("GET", "/author/{author_id}", author_id=author_id)

        if includes:
            query: dict[str, list[str]] = {"includes": includes.to_query()}
            return self.request(route, params=query)

        return self.request(route)

    def _update_author(
        self,
        author_id: str,
        *,
        name: Optional[str],
        biography: Optional[common.LocalisedString],
        twitter: Optional[str],
        pixiv: Optional[str],
        melon_book: Optional[str],
        fan_box: Optional[str],
        booth: Optional[str],
        nico_video: Optional[str],
        skeb: Optional[str],
        fantia: Optional[str],
        tumblr: Optional[str],
        youtube: Optional[str],
        website: Optional[str],
        version: Optional[int],
    ) -> Response[author.GetSingleAuthorResponse]:
        route = Route("PUT", "/author/{author_id}", author_id=author_id)

        query: dict[str, Any] = {"name": name}

        if name is not None:
            query["name"] = name

        if biography is not None:
            query["biography"] = biography

        if twitter is not MISSING:
            query["twitter"] = twitter

        if pixiv is not MISSING:
            query["pixiv"] = pixiv

        if melon_book is not MISSING:
            query["melonBook"] = melon_book

        if fan_box is not MISSING:
            query["fanBox"] = fan_box

        if booth is not MISSING:
            query["booth"] = booth

        if nico_video is not MISSING:
            query["nicoVideo"] = nico_video

        if skeb is not MISSING:
            query["skeb"] = skeb

        if fantia is not MISSING:
            query["fantia"] = fantia

        if tumblr is not MISSING:
            query["tumblr"] = tumblr

        if youtube is not MISSING:
            query["youtube"] = youtube

        if website is not MISSING:
            query["website"] = website

        if version:
            query["version"] = version

        return self.request(route, json=query)

    def _delete_author(self, author_id: str, /) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("DELETE", "/author/{author_id}", author_id=author_id)
        return self.request(route)

    def _get_artist(
        self, artist_id: str, /, *, includes: Optional[ArtistIncludes]
    ) -> Response[artist.GetSingleArtistResponse]:
        route = Route("GET", "/author/{artist_id}", artist_id=artist_id)

        if includes:
            query: dict[str, list[str]] = {"includes": includes.to_query()}
            return self.request(route, params=query)
        return self.request(route)

    def _update_artist(
        self,
        author_id: str,
        *,
        name: Optional[str],
        biography: Optional[common.LocalisedString],
        twitter: Optional[str],
        pixiv: Optional[str],
        melon_book: Optional[str],
        fan_box: Optional[str],
        booth: Optional[str],
        nico_video: Optional[str],
        skeb: Optional[str],
        fantia: Optional[str],
        tumblr: Optional[str],
        youtube: Optional[str],
        website: Optional[str],
        version: Optional[int],
    ) -> Response[artist.GetSingleArtistResponse]:
        route = Route("POST", "/author/{author_id}", author_id=author_id)

        query: dict[str, Any] = {"name": name}

        if name is not None:
            query["name"] = name

        if biography is not None:
            query["biography"] = biography

        if twitter is not MISSING:
            query["twitter"] = twitter

        if pixiv is not MISSING:
            query["pixiv"] = pixiv

        if melon_book is not MISSING:
            query["melonBook"] = melon_book

        if fan_box is not MISSING:
            query["fanBox"] = fan_box

        if booth is not MISSING:
            query["booth"] = booth

        if nico_video is not MISSING:
            query["nicoVideo"] = nico_video

        if skeb is not MISSING:
            query["skeb"] = skeb

        if fantia is not MISSING:
            query["fantia"] = fantia

        if tumblr is not MISSING:
            query["tumblr"] = tumblr

        if youtube is not MISSING:
            query["youtube"] = youtube

        if website is not MISSING:
            query["website"] = website

        if version:
            query["version"] = version

        return self.request(route, json=query)

    def _delete_artist(self, artist_id: str, /) -> Response[dict[Literal["result"], Literal["ok"]]]:
        route = Route("DELETE", "/author/{artist_id}", artist_id=artist_id)
        return self.request(route)

    def _get_report_reason_list(self, report_category: ReportCategory, /) -> Response[report.GetReportReasonResponse]:
        route = Route("GET", "/report/reasons/{report_category}", report_category=report_category.value)
        return self.request(route)

    def _at_home_report(self, url: str, success: bool, cached: bool, size: int, duration: int) -> Response[None]:
        route = CustomRoute("POST", "https://api.mangadex.network", "/report")

        query: dict[str, Any] = {"url": url, "success": success, "cached": cached, "bytes": size, "duration": duration}

        return self.request(route, json=query)

    def _create_report(
        self,
        *,
        report_category: ReportCategory,
        reason: str,
        object_id: str,
        details: str,
    ) -> Response[dict[Literal["result"], Literal["ok", "error"]]]:
        route = Route("POST", "/report")

        query: dict[str, Any] = {
            "category": report_category.value,
            "reason": reason,
            "objectId": object_id,
            "details": details,
        }

        return self.request(route, json=query)

    def _get_my_ratings(self, manga_ids: list[str], /) -> Response[statistics.GetPersonalMangaRatingsResponse]:
        route = Route("GET", "/rating")

        query: dict[str, Any] = {"manga": manga_ids}

        return self.request(route, params=query)

    def _set_manga_rating(self, manga_id: str, /, *, rating: int) -> Response[Literal["ok", "error"]]:
        route = Route("POST", "/rating/{manga_id}", manga_id=manga_id)

        query: dict[str, Any] = {"rating": rating}

        return self.request(route, json=query)

    def _delete_manga_rating(self, manga_id: str, /) -> Response[Literal["ok", "error"]]:
        route = Route("DELETE", "/rating/{manga_id}", manga_id=manga_id)

        return self.request(route)

    def _get_manga_statistics(self, manga_id: str, /) -> Response[statistics.GetStatisticsResponse]:
        route = Route("GET", "/statistics/manga/{manga_id}", manga_id=manga_id)

        return self.request(route)

    def _find_manga_statistics(self, manga_ids: list[str], /) -> Response[statistics.BatchGetStatisticsResponse]:
        route = Route("GET", "/statistics/manga")

        query: dict[str, Any] = {"manga": manga_ids}

        return self.request(route, params=query)

    def _open_upload_session(
        self, manga_id: str, /, *, scanlator_groups: list[str]
    ) -> Response[upload.BeginChapterUploadResponse]:
        route = Route("POST", "/upload/begin")

        query: dict[str, Any] = {}
        query["manga"] = manga_id
        query["groups"] = scanlator_groups

        return self.request(route, json=query)

    def _abandon_upload_session(self, session_id: str, /) -> Response[None]:
        route = Route("DELETE", "/upload/{session_id}", session_id=session_id)

        return self.request(route)
