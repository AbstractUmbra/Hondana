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
import sys
import weakref
from base64 import b64decode
from os import getenv
from typing import TYPE_CHECKING, Any, Literal, Self, TypeVar, overload

import aiohttp

from . import __version__
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
from .errors import (
    APIException,
    AuthenticationRequired,
    BadRequest,
    Forbidden,
    MangaDexServerError,
    NotFound,
    PreviousAPIVersionRequest,
    RefreshTokenFailure,
    Unauthorized,
)
from .utils import (
    MANGA_TAGS,
    MANGADEX_TIME_REGEX,
    MISSING,
    AuthRoute,
    Route,
    calculate_limits,
    clean_isoformat,
    delta_to_iso,
    from_json,
    get_image_mime_type,
    json_or_text,
    php_query_builder,
    to_json,
)

if TYPE_CHECKING:
    from collections.abc import Coroutine
    from types import TracebackType
    from typing import TypeAlias

    from yarl import URL

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
    from .report import ReportDetails
    from .tags import QueryTags
    from .types_ import (
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
        token,
        upload,
        user,
    )
    from .types_.account import GetAccountAvailable
    from .types_.forums import ForumPayloadResponse
    from .types_.settings import Settings, SettingsPayload
    from .types_.tags import GetTagListResponse
    from .utils import MANGADEX_QUERY_PARAM_TYPE

    T = TypeVar("T")
    Response = Coroutine[Any, Any, T]
    MU = TypeVar("MU", bound="MaybeUnlock")
    BE = TypeVar("BE", bound=BaseException)
    DefaultResponseType: TypeAlias = dict[Literal["result"], Literal["ok", "error"]]


LOGGER: logging.Logger = logging.getLogger(__name__)
TAGS: dict[str, str] = MANGA_TAGS
ALLOWED_IMAGE_FORMATS: set[str] = {"image/png", "image/gif", "image/jpeg", "image/jpg", "image/webp"}


__all__ = []


class Token:
    __slots__ = (
        "_client_secret",
        "_http",
        "client_id",
        "created_at",
        "expires",
        "raw_token",
        "refresh_token",
    )
    created_at: datetime.datetime
    expires: datetime.datetime

    def __init__(
        self,
        token: str,
        /,
        *,
        client_id: str,
        client_secret: str,
        session: aiohttp.ClientSession,
    ) -> None:
        self._http: aiohttp.ClientSession = session
        self._client_secret: str = client_secret
        self.raw_token: str = token
        self.client_id: str = client_id
        self.refresh_token: Token | None = None
        self._parse()

    def __str__(self) -> str:
        return self.raw_token

    @classmethod
    def from_token_response(
        cls,
        *,
        payload: token.GetTokenPayload,
        session: aiohttp.ClientSession,
        client_secret: str,
        client_id: str,
    ) -> Self:
        self = cls(payload["access_token"], session=session, client_id=client_id, client_secret=client_secret)
        self.add_refresh_token(payload["refresh_token"])

        return self

    def _parse(self) -> None:
        _, payload, _ = self.raw_token.split(".")

        padding = len(payload) % 4
        token = payload + ("=" * padding)

        raw = b64decode(token).decode("utf-8")
        parsed: token.TokenPayload = from_json(raw)

        self.expires = datetime.datetime.fromtimestamp(parsed["exp"], tz=datetime.UTC)
        self.created_at = datetime.datetime.fromtimestamp(parsed["iat"], tz=datetime.UTC)

    def has_expired(self) -> bool:
        now = datetime.datetime.now(datetime.UTC)

        return not self.expires > now

    async def refresh(self) -> Self:
        if not self.refresh_token:
            msg = "Current token has no refresh_token."
            raise TypeError(msg)

        route = AuthRoute("POST", "/token")

        data = aiohttp.FormData(
            [
                ("grant_type", "refresh_token"),
                ("refresh_token", self.refresh_token.raw_token),
                ("client_id", self.client_id),
                ("client_secret", self._client_secret),
            ],
        )

        async with self._http.request(route.verb, route.url, data=data) as resp:
            response_data = await resp.json()

            try:
                self.raw_token = response_data["access_token"]
            except KeyError as exc:
                msg = "Failed to refresh token"
                raise RefreshTokenFailure(msg, resp, response_data) from exc

        self._parse()

        self.add_refresh_token(response_data["refresh_token"])
        return self

    def add_refresh_token(self, raw_token: str) -> None:
        self.refresh_token = self.__class__(
            raw_token,
            client_id=self.client_id,
            client_secret=self._client_secret,
            session=self._http,
        )


class MaybeUnlock:
    def __init__(self, lock: asyncio.Lock, /) -> None:
        self.lock: asyncio.Lock = lock
        self._unlock: bool = True

    def __enter__(self: Self) -> Self:
        return self

    def defer(self) -> None:
        self._unlock = False

    def __exit__(
        self,
        exc_type: type[BE] | None,  # noqa: PYI036 # not expanding the typevar
        exc: BE | None,  # noqa: PYI036 # not expanding the typevar
        traceback: TracebackType | None,
    ) -> None:
        if self._unlock:
            self.lock.release()


class HTTPClient:  # not part of the public API
    __slots__ = (
        "_auth_token",
        "_authenticated",
        "_client_secret",
        "_locks",
        "_oauth_scopes",
        "_password",
        "_refresh_token",
        "_session",
        "_token_lock",
        "client_id",
        "user_agent",
        "username",
    )

    def __init__(
        self,
        *,
        session: aiohttp.ClientSession | None = None,
        dev_api: bool = False,
        username: str | None = None,
        password: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
    ) -> None:
        self._session: aiohttp.ClientSession | None = session
        self._locks: weakref.WeakValueDictionary[str, asyncio.Lock] = weakref.WeakValueDictionary()
        self._token_lock: asyncio.Lock = asyncio.Lock()
        user_agent = "Hondana (https://github.com/AbstractUmbra/Hondana {0}) Python/{1[0]}.{1[1]} aiohttp/{2}"
        self.user_agent: str = user_agent.format(__version__, sys.version_info, aiohttp.__version__)
        self.username: str | None = username
        self._password: str | None = password
        self.client_id: str | None = client_id
        self._client_secret: str | None = client_secret
        self._auth_token: Token | None = None
        self._refresh_token: Token | None = None
        self._authenticated: bool = all([username, password, client_id, client_secret])
        self._resolve_api_type(dev_api=dev_api)
        if any([username, password, client_id, client_secret]) and not self._authenticated:
            msg = "You must pass all required login attributes: `username`, `password`, `client_id`, `client_secret`"
            raise RuntimeError(msg)

    def _resolve_api_type(self, *, dev_api: bool) -> None:
        if dev_api is True or getenv("HONDANA_API_DEV"):
            Route.API_BASE_URL = Route.API_DEV_BASE_URL
            AuthRoute.API_BASE_URL = AuthRoute.API_DEV_BASE_URL

    async def _generate_session(self) -> aiohttp.ClientSession:
        """|coro|

        Creates an :class:`aiohttp.ClientSession` for use in the http client.

        Returns
        -------
        :class:`aiohttp.ClientSession`
            The underlying client session we use.

        .. note::
            This method must be a coroutine to avoid the deprecation warning of Python 3.9+.
        """
        self._session = aiohttp.ClientSession(cookie_jar=aiohttp.DummyCookieJar())
        return self._session

    async def close(self) -> None:
        """|coro|

        This method will close the internal client session to ensure a clean exit.
        """
        if self._session is not None:
            await self._session.close()

    async def get_token(self) -> Token:
        if not self.client_id or not self._client_secret:
            msg = "You must pass the correct OAuth2 details to use authentication."
            raise AuthenticationRequired(msg)

        if self._auth_token and not self._auth_token.has_expired():
            return self._auth_token

        if (
            self._auth_token
            and self._auth_token.has_expired()
            and (self._auth_token.refresh_token and not self._auth_token.refresh_token.has_expired())
        ):
            try:
                await self._auth_token.refresh()
            except RefreshTokenFailure as exc:
                LOGGER.exception(
                    "Failed to refresh token. Will attempt the login flow again. Errored payload:\n%s",
                    exc.data,
                    exc_info=exc,
                )

        route = AuthRoute("POST", "/token")

        data = aiohttp.FormData(
            [
                ("grant_type", "password"),
                ("username", self.username),
                ("password", self._password),
                ("client_id", self.client_id),
                ("client_secret", self._client_secret),
            ],
        )

        if not self._session:
            self._session = await self._generate_session()

        # to prevent circular we handle this logic manually, not the request method
        async with self._session.request(route.verb, route.url, data=data) as resp:
            if 200 <= resp.status < 300:
                response_data: token.GetTokenPayload = await resp.json()
            else:
                raise APIException(resp, status_code=resp.status, errors=[])

        self._auth_token = Token.from_token_response(
            payload=response_data,
            client_id=self.client_id,
            client_secret=self._client_secret,
            session=self._session,
        )

        return self._auth_token

    async def request(
        self,
        route: Route | AuthRoute,
        *,
        params: MANGADEX_QUERY_PARAM_TYPE | None = None,
        json: Any | None = None,
        **kwargs: Any,
    ) -> Any:
        """|coro|

        This performs the HTTP request, handling authentication tokens when doing it.

        Parameters
        ----------
        route: Union[:class:`Route`, :class:`AuthRoute`]
            The route describes the http verb and endpoint to hit.
            The request is the one that takes in the query params or request body.

        Raises
        ------
        BadRequest
            A request was malformed
        Unauthorized
            You attempted to use an endpoint you have no authorization for.
        Forbidden
            Your auth was not sufficient to perform this action.
        NotFound
            The specified item, endpoint or resource was not found.
        MangaDexServerError
            A generic exception raised when the HTTP responde code is 5xx.
        APIException
            A generic exception raised when the HTTP response code is non 2xx.

        Returns
        -------
        Any
            The potential response data we got from the request.
        """  # noqa: DOC501 # unreachable error
        if self._session is None:
            self._session = await self._generate_session()

        bucket = route.path
        lock = self._locks.get(bucket)
        if lock is None:
            lock = asyncio.Lock()
            self._locks[bucket] = lock

        headers = kwargs.pop("headers", {})
        headers["User-Agent"] = self.user_agent

        if self._authenticated and route.auth:
            token = await self.get_token()
            headers["Authorization"] = f"Bearer {token}"
            LOGGER.debug(
                "Current auth token's start and end is: '%s :: %s'",
                headers["Authorization"][:20],
                headers["Authorization"][-20:],
            )

        if json:
            headers["Content-Type"] = "application/json"
            kwargs["data"] = to_json(json)
            LOGGER.debug("Current json body is: %s", str(kwargs["data"]))

        if params:
            resolved_params = php_query_builder(params)
            kwargs["params"] = resolved_params

        kwargs["headers"] = headers

        response: aiohttp.ClientResponse | None = None
        await lock.acquire()
        with MaybeUnlock(lock) as maybe_lock:
            for tries in range(5):
                try:
                    async with self._session.request(route.verb, route.url, **kwargs) as response:
                        LOGGER.debug("Current request url: %s", response.url.human_repr())
                        # Requests remaining before ratelimit
                        remaining = response.headers.get("x-ratelimit-remaining", None)
                        LOGGER.debug("remaining is: %s", remaining)
                        # Timestamp for when current ratelimit session(?) expires
                        retry = response.headers.get("x-ratelimit-retry-after", None)
                        LOGGER.debug("retry is: %s", retry)
                        if retry is not None:
                            retry = datetime.datetime.fromtimestamp(int(retry), datetime.UTC)
                        # The total ratelimit session hits
                        limit = response.headers.get("x-ratelimit-limit", None)
                        LOGGER.debug("limit is: %s", limit)

                        if remaining == "0" and response.status != 429:
                            if not retry:
                                break  # unreachable
                            delta = retry - datetime.datetime.now(datetime.UTC)
                            sleep = delta.total_seconds() + 1
                            LOGGER.warning("A ratelimit has been exhausted, sleeping for: %d", sleep)
                            maybe_lock.defer()
                            loop = asyncio.get_running_loop()
                            loop.call_later(sleep, lock.release)

                        if response.content_type in ALLOWED_IMAGE_FORMATS:
                            data = (await response.read(), response)
                        else:
                            try:
                                data = await json_or_text(response)
                            except aiohttp.ClientResponseError:
                                continue

                        if 300 > response.status >= 200:
                            return data

                        if response.status == 429:
                            if not retry:
                                break  # unreachable

                            delta = retry - datetime.datetime.now(datetime.UTC)
                            sleep = delta.total_seconds() + 1
                            LOGGER.warning("A ratelimit has been hit, sleeping for: %d", sleep)
                            await asyncio.sleep(sleep)
                            continue

                        if response.status in {500, 502, 503, 504}:
                            sleep_ = 1 + tries * 2
                            LOGGER.warning("Hit an API error, trying again in: %d", sleep_)
                            await asyncio.sleep(sleep_)
                            continue

                        if not isinstance(data, dict):
                            if isinstance(data, str):
                                raise PreviousAPIVersionRequest(response)
                            break  # unreachable

                        if response.status == 400:
                            raise BadRequest(response, errors=data["errors"])
                        if response.status == 401:
                            raise Unauthorized(response, errors=data["errors"])
                        if response.status == 403:
                            raise Forbidden(response, errors=data["errors"])
                        if response.status == 404:
                            raise NotFound(response, errors=data["errors"])
                        LOGGER.error("Unhandled HTTP error occurred: %s -> %s", response.status, data)
                        raise APIException(
                            response,
                            status_code=response.status,
                            errors=data["errors"],
                        )
                except (aiohttp.ServerDisconnectedError, aiohttp.ServerTimeoutError):
                    LOGGER.exception("Network error occurred:-")
                    await asyncio.sleep(5)
                    continue

            if response is not None:
                if response.status >= 500:
                    raise MangaDexServerError(response, status_code=response.status)

                raise APIException(response, status_code=response.status, errors=[])

            msg = "Unreachable code in HTTP handling."
            raise RuntimeError(msg)

    def account_available(self, username: str) -> Response[GetAccountAvailable]:
        route = Route("GET", "/account/available/{username}", username=username)
        return self.request(route)

    def update_tags(self) -> Response[GetTagListResponse]:
        route = Route("GET", "/manga/tag")
        return self.request(route)

    def manga_list(
        self,
        *,
        limit: int,
        offset: int,
        title: str | None,
        author_or_artist: str | None,
        authors: list[str] | None,
        artists: list[str] | None,
        year: int | None,
        included_tags: QueryTags | None,
        excluded_tags: QueryTags | None,
        status: list[MangaStatus] | None,
        original_language: list[common.LanguageCode] | None,
        excluded_original_language: list[common.LanguageCode] | None,
        available_translated_language: list[common.LanguageCode] | None,
        publication_demographic: list[PublicationDemographic] | None,
        ids: list[str] | None,
        content_rating: list[ContentRating] | None,
        created_at_since: datetime.datetime | None,
        updated_at_since: datetime.datetime | None,
        order: MangaListOrderQuery | None,
        includes: MangaIncludes | None,
        has_available_chapters: bool | None,
        has_unavailable_chapters: bool | None,
        group: str | None,
    ) -> Response[manga.MangaSearchResponse]:
        route = Route("GET", "/manga")

        limit, offset = calculate_limits(limit, offset, max_limit=100)

        query: MANGADEX_QUERY_PARAM_TYPE = {"limit": limit, "offset": offset}

        if title:
            query["title"] = title

        if author_or_artist:
            query["authorOrArtist"] = author_or_artist

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
            query["status"] = [s.value for s in status]

        if original_language:
            query["originalLanguage"] = original_language

        if excluded_original_language:
            query["excludedOriginalLanguage"] = excluded_original_language

        if available_translated_language:
            query["availableTranslatedLanguage"] = available_translated_language

        if publication_demographic:
            query["publicationDemographic"] = [demo.value for demo in publication_demographic]

        if ids:
            query["ids"] = ids

        if content_rating:
            query["contentRating"] = [cr.value for cr in content_rating]

        if created_at_since:
            query["createdAtSince"] = clean_isoformat(created_at_since)

        if updated_at_since:
            query["updatedAtSince"] = clean_isoformat(updated_at_since)

        if order:
            query["order"] = order.to_dict()

        if includes:
            query["includes"] = includes.to_query()

        if has_available_chapters is not None:
            query["hasAvailableChapters"] = has_available_chapters

        if has_unavailable_chapters is not None:
            query["hasUnavailableChapters"] = has_unavailable_chapters

        if group:
            query["group"] = group

        return self.request(route, params=query)

    def create_manga(
        self,
        *,
        title: common.LocalizedString,
        alt_titles: list[common.LocalizedString] | None,
        description: common.LocalizedString | None,
        authors: list[str] | None,
        artists: list[str] | None,
        links: manga.MangaLinks | None,
        original_language: str | None,
        last_volume: str | None,
        last_chapter: str | None,
        publication_demographic: PublicationDemographic | None,
        status: MangaStatus | None,
        year: int | None,
        content_rating: ContentRating,
        tags: QueryTags | None,
        mod_notes: str | None,
    ) -> Response[manga.GetMangaResponse]:
        route = Route("POST", "/manga", authenticate=True)

        query: dict[str, Any] = {"title": title}

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

    def get_manga_volumes_and_chapters(
        self,
        *,
        manga_id: str,
        translated_language: list[common.LanguageCode] | None,
        groups: list[str] | None,
    ) -> Response[manga.GetMangaVolumesAndChaptersResponse]:
        route = Route("GET", "/manga/{manga_id}/aggregate", manga_id=manga_id)

        query: MANGADEX_QUERY_PARAM_TYPE = {}

        if translated_language:
            query["translatedLanguage"] = translated_language

        if groups:
            query["groups"] = groups

        return self.request(route, params=query) if query else self.request(route)

    def get_manga(self, manga_id: str, /, *, includes: MangaIncludes | None) -> Response[manga.GetMangaResponse]:
        route = Route("GET", "/manga/{manga_id}", manga_id=manga_id)

        if includes:
            query: MANGADEX_QUERY_PARAM_TYPE = {"includes": includes.to_query()}
            return self.request(route, params=query)
        return self.request(route)

    def update_manga(
        self,
        manga_id: str,
        /,
        *,
        title: common.LocalizedString | None,
        alt_titles: list[common.LocalizedString] | None,
        description: common.LocalizedString | None,
        authors: list[str] | None,
        artists: list[str] | None,
        links: manga.MangaLinks | None,
        original_language: str | None,
        last_volume: str | None,
        last_chapter: str | None,
        publication_demographic: PublicationDemographic | None,
        status: MangaStatus | None,
        year: int | None,
        content_rating: ContentRating | None,
        tags: QueryTags | None,
        primary_cover: str | None,
        version: int,
    ) -> Response[manga.GetMangaResponse]:
        route = Route("PUT", "/manga/{manga_id}", manga_id=manga_id, authenticate=True)

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

    def manga_feed(
        self,
        manga_id: str | None,
        /,
        *,
        limit: int,
        offset: int,
        translated_language: list[common.LanguageCode] | None,
        original_language: list[common.LanguageCode] | None,
        excluded_original_language: list[common.LanguageCode] | None,
        content_rating: list[ContentRating] | None,
        excluded_groups: list[str] | None,
        excluded_uploaders: list[str] | None,
        include_future_updates: bool | None,
        created_at_since: datetime.datetime | None,
        updated_at_since: datetime.datetime | None,
        published_at_since: datetime.datetime | None,
        order: FeedOrderQuery | None,
        includes: ChapterIncludes | None,
        include_empty_pages: bool | None,
        include_future_publish_at: bool | None,
        include_external_url: bool | None,
        include_unavailable: bool | None,
    ) -> Response[chapter.GetMultiChapterResponse]:
        if manga_id is None:
            route = Route("GET", "/user/follows/manga/feed", authenticate=True)
        else:
            route = Route("GET", "/manga/{manga_id}/feed", manga_id=manga_id)

        limit, offset = calculate_limits(limit, offset, max_limit=500)

        query: MANGADEX_QUERY_PARAM_TYPE = {"limit": limit, "offset": offset}

        if translated_language:
            query["translatedLanguage"] = translated_language

        if original_language:
            query["originalLanguage"] = original_language

        if excluded_original_language:
            query["excludedOriginalLanguage"] = excluded_original_language

        if content_rating:
            query["contentRating"] = [cr.value for cr in content_rating]

        if excluded_groups:
            query["excludedGroups"] = excluded_groups

        if excluded_uploaders:
            query["excludedUploaders"] = excluded_uploaders

        if include_future_updates:
            resolved = str(int(include_future_updates))
            query["includeFutureUpdates"] = resolved

        if created_at_since:
            query["createdAtSince"] = clean_isoformat(created_at_since)

        if updated_at_since:
            query["updatedAtSince"] = clean_isoformat(updated_at_since)

        if published_at_since:
            query["publishAtSince"] = clean_isoformat(published_at_since)

        if order:
            query["order"] = order.to_dict()

        if includes:
            query["includes"] = includes.to_query()

        if include_empty_pages:
            query["includeEmptyPages"] = include_empty_pages

        if include_future_publish_at:
            query["includeFuturePublishAt"] = include_future_publish_at

        if include_external_url:
            query["includeExternalUrl"] = include_external_url

        if include_unavailable:
            query["includeUnavailable"] = str(int(include_unavailable))

        return self.request(route, params=query)

    def delete_manga(self, manga_id: str, /) -> Response[DefaultResponseType]:
        route = Route("DELETE", "/manga/{manga_id}", manga_id=manga_id, authenticate=True)
        return self.request(route)

    def unfollow_manga(self, manga_id: str, /) -> Response[DefaultResponseType]:
        route = Route("DELETE", "/manga/{manga_id}/follow", manga_id=manga_id, authenticate=True)
        return self.request(route)

    def follow_manga(self, manga_id: str, /) -> Response[DefaultResponseType]:
        route = Route("POST", "/manga/{manga_id}/follow", manga_id=manga_id, authenticate=True)
        return self.request(route)

    def get_random_manga(
        self,
        *,
        includes: MangaIncludes | None,
        content_rating: list[ContentRating] | None,
        included_tags: QueryTags | None,
        excluded_tags: QueryTags | None,
    ) -> Response[manga.GetMangaResponse]:
        route = Route("GET", "/manga/random")

        query: MANGADEX_QUERY_PARAM_TYPE = {}

        if includes:
            query["includes"] = includes.to_query()

        if content_rating:
            query["contentRating"] = [cr.value for cr in content_rating]

        if included_tags:
            query["includedTags"] = included_tags.tags
            query["includedTagsMode"] = included_tags.mode

        if excluded_tags:
            query["excludedTags"] = excluded_tags.tags
            query["excludedTagsMode"] = excluded_tags.mode

        return self.request(route, params=query)

    @overload
    def manga_read_markers(
        self,
        manga_ids: list[str],
        /,
        *,
        grouped: Literal[False],
    ) -> Response[manga.MangaReadMarkersResponse]: ...

    @overload
    def manga_read_markers(
        self,
        manga_ids: list[str],
        /,
        *,
        grouped: Literal[True],
    ) -> Response[manga.MangaGroupedReadMarkersResponse]: ...

    def manga_read_markers(
        self,
        manga_ids: list[str],
        /,
        *,
        grouped: bool = False,
    ) -> Response[manga.MangaReadMarkersResponse | manga.MangaGroupedReadMarkersResponse]:
        if not grouped:
            if len(manga_ids) != 1:
                msg = "If `grouped` is False, then `manga_ids` should be a single length list."
                raise ValueError(msg)

            id_ = manga_ids[0]
            route = Route("GET", "/manga/{manga_id}/read", manga_id=id_, authenticate=True)
            return self.request(route)

        route = Route("GET", "/manga/read", authenticate=True)
        query: MANGADEX_QUERY_PARAM_TYPE = {"ids": manga_ids, "grouped": True}
        return self.request(route, params=query)

    def manga_read_markers_batch(
        self,
        manga_id: str,
        /,
        *,
        update_history: bool,
        read_chapters: list[str] | None,
        unread_chapters: list[str] | None,
    ) -> Response[DefaultResponseType]:
        route = Route("POST", "/manga/{manga_id}/read", manga_id=manga_id, authenticate=True)

        body: dict[Any, Any] = {}
        query: MANGADEX_QUERY_PARAM_TYPE | None = {"updateHistory": update_history} if update_history else None

        if read_chapters:
            body["chapterIdsRead"] = read_chapters

        if unread_chapters:
            body["chapterIdsUnread"] = unread_chapters

        if query:
            return self.request(route, json=body, params=query)
        return self.request(route, json=body)

    def get_all_manga_reading_status(
        self,
        *,
        status: ReadingStatus | None = None,
    ) -> Response[manga.MangaMultipleReadingStatusResponse]:
        route = Route("GET", "/manga/status", authenticate=True)
        if status:
            query: MANGADEX_QUERY_PARAM_TYPE = {"status": status.value}
            return self.request(route, params=query)
        return self.request(route)

    def get_manga_reading_status(self, manga_id: str, /) -> Response[manga.MangaSingleReadingStatusResponse]:
        route = Route("GET", "/manga/{manga_id}/status", manga_id=manga_id, authenticate=True)
        return self.request(route)

    def update_manga_reading_status(self, manga_id: str, /, status: ReadingStatus) -> Response[DefaultResponseType]:
        route = Route("POST", "/manga/{manga_id}/status", manga_id=manga_id, authenticate=True)
        query: dict[str, Any] = {"status": status.value}
        return self.request(route, json=query)

    def get_manga_draft(self, manga_id: str, /) -> Response[manga.GetMangaResponse]:
        route = Route("GET", "/manga/draft/{manga_id}", manga_id=manga_id, authenticate=True)
        return self.request(route)

    def submit_manga_draft(self, manga_id: str, /, *, version: int) -> Response[manga.GetMangaResponse]:
        route = Route("POST", "/manga/draft/{manga_id}/commit", manga_id=manga_id, authenticate=True)
        query: dict[str, Any] = {"version": version}
        return self.request(route, json=query)

    def get_manga_draft_list(
        self,
        *,
        limit: int,
        offset: int,
        state: MangaState | None = None,
        order: MangaDraftListOrderQuery | None = None,
        includes: MangaIncludes | None,
    ) -> Response[manga.GetMangaResponse]:
        route = Route("GET", "/manga/draft", authenticate=True)

        limit, offset = calculate_limits(limit, offset, max_limit=100)

        query: MANGADEX_QUERY_PARAM_TYPE = {"limit": limit, "offset": offset}

        if state:
            query["state"] = state.value

        if order:
            query["order"] = order.to_dict()

        if includes:
            query["includes"] = includes.to_query()

        return self.request(route, params=query)

    def get_manga_relation_list(
        self,
        manga_id: str,
        /,
        *,
        includes: MangaIncludes | None,
    ) -> Response[manga.MangaRelationResponse]:
        route = Route("GET", "/manga/{manga_id}/relation", manga_id=manga_id)

        if includes:
            query: MANGADEX_QUERY_PARAM_TYPE = {"includes": includes.to_query()}
            return self.request(route, params=query)

        return self.request(route)

    def create_manga_relation(
        self,
        manga_id: str,
        /,
        *,
        target_manga: str,
        relation_type: MangaRelationType,
    ) -> Response[manga.MangaRelationCreateResponse]:
        route = Route("POST", "/manga/{manga_id}/relation", manga_id=manga_id, authenticate=True)
        query: dict[str, Any] = {"targetManga": target_manga, "relation": relation_type.value}
        return self.request(route, json=query)

    def delete_manga_relation(self, manga_id: str, relation_id: str, /) -> Response[DefaultResponseType]:
        route = Route(
            "DELETE",
            "/manga/{manga_id}/relation/{relation_id}",
            manga_id=manga_id,
            relation_id=relation_id,
            authenticate=True,
        )
        return self.request(route)

    def chapter_list(
        self,
        *,
        limit: int,
        offset: int,
        ids: list[str] | None,
        title: str | None,
        groups: list[str] | None,
        uploader: str | list[str] | None,
        manga: str | None,
        volume: str | list[str] | None,
        chapter: str | list[str] | None,
        translated_language: list[common.LanguageCode] | None,
        original_language: list[common.LanguageCode] | None,
        excluded_original_language: list[common.LanguageCode] | None,
        content_rating: list[ContentRating] | None,
        excluded_groups: list[str] | None,
        excluded_uploaders: list[str] | None,
        include_future_updates: bool | None,
        include_empty_pages: bool | None,
        include_future_publish_at: bool | None,
        include_external_url: bool | None,
        include_unavailable: bool | None,
        created_at_since: datetime.datetime | None,
        updated_at_since: datetime.datetime | None,
        published_at_since: datetime.datetime | None,
        order: FeedOrderQuery | None,
        includes: ChapterIncludes | None,
    ) -> Response[chapter.GetMultiChapterResponse]:
        route = Route("GET", "/chapter")

        limit, offset = calculate_limits(limit, offset, max_limit=100)

        query: MANGADEX_QUERY_PARAM_TYPE = {"limit": limit, "offset": offset}

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
            query["contentRating"] = [cr.value for cr in content_rating]

        if excluded_groups:
            query["excludedGroups"] = excluded_groups

        if excluded_uploaders:
            query["excludedUploaders"] = excluded_uploaders

        if include_future_updates:
            resolved = str(int(include_future_updates))
            query["includeFutureUpdates"] = resolved

        if include_empty_pages:
            resolved = str(int(include_empty_pages))
            query["includeEmptyPages"] = resolved

        if include_future_publish_at:
            resolved = str(int(include_future_publish_at))
            query["includeFuturePublishAt"] = resolved

        if include_external_url:
            resolved = str(int(include_external_url))
            query["includeExternalUrl"] = resolved

        if include_unavailable:
            resolved = str(int(include_unavailable))
            query["includeUnavailable"] = resolved

        if created_at_since:
            query["createdAtSince"] = clean_isoformat(created_at_since)

        if updated_at_since:
            query["updatedAtSince"] = clean_isoformat(updated_at_since)

        if published_at_since:
            query["publishAtSince"] = clean_isoformat(published_at_since)

        if order:
            query["order"] = order.to_dict()

        if includes:
            query["includes"] = includes.to_query()

        return self.request(route, params=query)

    def get_chapter(
        self,
        chapter_id: str,
        /,
        *,
        includes: ChapterIncludes | None,
    ) -> Response[chapter.GetSingleChapterResponse]:
        route = Route("GET", "/chapter/{chapter_id}", chapter_id=chapter_id)

        if includes:
            return self.request(route, params={"includes": includes.to_query()})
        return self.request(route)

    def update_chapter(
        self,
        chapter_id: str,
        /,
        *,
        title: str | None,
        volume: str | None,
        chapter: str | None,
        translated_language: str | None,
        groups: list[str] | None,
        version: int,
    ) -> Response[chapter.GetSingleChapterResponse]:
        route = Route("PUT", "/chapter/{chapter_id}", chapter_id=chapter_id, authenticate=True)

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

    def delete_chapter(self, chapter_id: str, /) -> Response[DefaultResponseType]:
        route = Route("DELETE", "/chapter/{chapter_id}", chapter_id=chapter_id, authenticate=True)
        return self.request(route)

    def user_read_history(self) -> Response[chapter.ChapterReadHistoryResponse]:
        route = Route("GET", "/user/history", authenticate=True)
        return self.request(route)

    def cover_art_list(
        self,
        *,
        limit: int = 10,
        offset: int = 0,
        manga: list[str] | None,
        ids: list[str] | None,
        uploaders: list[str] | None,
        locales: list[common.LanguageCode] | None,
        order: CoverArtListOrderQuery | None,
        includes: CoverIncludes | None,
    ) -> Response[cover.GetMultiCoverResponse]:
        route = Route("GET", "/cover")

        limit, offset = calculate_limits(limit, offset, max_limit=100)

        query: MANGADEX_QUERY_PARAM_TYPE = {"limit": limit, "offset": offset}

        if manga:
            query["manga"] = manga

        if ids:
            query["ids"] = ids

        if uploaders:
            query["uploaders"] = uploaders

        if locales:
            query["locales"] = locales

        if order:
            query["order"] = order.to_dict()

        if includes:
            query["includes"] = includes.to_query()

        return self.request(route, params=query)

    def upload_cover(
        self,
        manga_id: str,
        /,
        *,
        cover: bytes,
        volume: str | None,
        description: str,
        locale: common.LanguageCode | None,
    ) -> Response[cover.GetSingleCoverResponse]:
        route = Route("POST", "/cover/{manga_id}", manga_id=manga_id, authenticate=True)

        content_type = get_image_mime_type(cover)
        ext = content_type.split("/")[-1]
        form_data = aiohttp.FormData()
        form_data.add_field(name="file", filename=f"cover.{ext}", value=cover, content_type=content_type)
        form_data.add_field(name="volume", value=volume)
        form_data.add_field(name="locale", value=locale)
        if description:
            form_data.add_field(name="description", value=description)

        return self.request(route, data=form_data)

    def get_cover(self, cover_id: str, /, *, includes: CoverIncludes | None) -> Response[cover.GetSingleCoverResponse]:
        route = Route("GET", "/cover/{cover_id}", cover_id=cover_id)

        if includes:
            query: MANGADEX_QUERY_PARAM_TYPE = {"includes": includes.to_query()}
            return self.request(route, params=query)

        return self.request(route)

    def edit_cover(
        self,
        cover_id: str,
        /,
        *,
        volume: str | None = MISSING,
        description: str | None = MISSING,
        locale: str | None = MISSING,
        version: int,
    ) -> Response[cover.GetSingleCoverResponse]:
        route = Route("PUT", "/cover/{cover_id}", cover_id=cover_id, authenticate=True)

        query: dict[str, Any] = {"version": version}

        if volume is MISSING:
            msg = "`volume` key must be a value of `str` or `NoneType`."
            raise TypeError(msg)

        query["volume"] = volume

        if description is not MISSING:
            query["description"] = description

        if locale is not MISSING:
            query["locale"] = locale

        return self.request(route, json=query)

    def delete_cover(self, cover_id: str, /) -> Response[DefaultResponseType]:
        route = Route("DELETE", "/cover/{cover_id}", cover_id=cover_id, authenticate=True)
        return self.request(route)

    def scanlation_group_list(
        self,
        *,
        limit: int,
        offset: int,
        ids: list[str] | None,
        name: str | None,
        focused_language: common.LanguageCode | None,
        includes: ScanlatorGroupIncludes | None,
        order: ScanlatorGroupListOrderQuery | None,
    ) -> Response[scanlator_group.GetMultiScanlationGroupResponse]:
        route = Route("GET", "/group")

        limit, offset = calculate_limits(limit, offset, max_limit=100)

        query: MANGADEX_QUERY_PARAM_TYPE = {"limit": limit, "offset": offset}

        if ids:
            query["ids"] = ids

        if name:
            query["name"] = name

        if focused_language:
            query["focusedLanguage"] = focused_language

        if includes:
            query["includes"] = includes.to_query()

        if order:
            query["order"] = order.to_dict()

        return self.request(route, params=query)

    def user_list(
        self,
        *,
        limit: int,
        offset: int,
        ids: list[str] | None,
        username: str | None,
        order: UserListOrderQuery | None,
    ) -> Response[user.GetMultiUserResponse]:
        route = Route("GET", "/user", authenticate=True)

        limit, offset = calculate_limits(limit, offset, max_limit=100)

        query: MANGADEX_QUERY_PARAM_TYPE = {"limit": limit, "offset": offset}

        if ids:
            query["ids"] = ids

        if username:
            query["username"] = username

        if order:
            query["order"] = order.to_dict()

        return self.request(route, params=query)

    def get_user(self, user_id: str, /) -> Response[user.GetSingleUserResponse]:
        route = Route("GET", "/user/{user_id}", user_id=user_id)
        return self.request(route)

    def delete_user(self, user_id: str, /) -> Response[DefaultResponseType]:
        route = Route("DELETE", "/user/{user_id}", user_id=user_id, authenticate=True)
        return self.request(route)

    def approve_user_deletion(self, approval_code: str, /) -> Response[DefaultResponseType]:
        route = Route("POST", "/user/delete/{approval_code}", approval_code=approval_code, authenticate=True)
        return self.request(route)

    def update_user_password(self, *, old_password: str, new_password: str) -> Response[DefaultResponseType]:
        route = Route("POST", "/user/password")
        query: dict[str, Any] = {"oldPassword": old_password, "newPassword": new_password}
        return self.request(route, json=query)

    def update_user_email(self, email: str, /) -> Response[DefaultResponseType]:
        route = Route("POST", "/user/email")
        query: dict[str, Any] = {"email": email}
        return self.request(route, json=query)

    def get_my_details(self) -> Response[user.GetSingleUserResponse]:
        route = Route("GET", "/user/me", authenticate=True)
        return self.request(route)

    def follow_user(self, user_id: str) -> Response[DefaultResponseType]:
        route = Route("POST", "/user/{user_id}/follow", user_id=user_id)
        return self.request(route)

    def unfollow_user(self, user_id: str) -> Response[DefaultResponseType]:
        route = Route("DELETE", "/user/{user_id}/follow", user_id=user_id)
        return self.request(route)

    def get_my_followed_groups(
        self,
        *,
        limit: int,
        offset: int,
    ) -> Response[scanlator_group.GetMultiScanlationGroupResponse]:
        route = Route("GET", "/user/follows/group", authenticate=True)

        limit, offset = calculate_limits(limit, offset, max_limit=100)

        query: MANGADEX_QUERY_PARAM_TYPE = {"limit": limit, "offset": offset}
        return self.request(route, params=query)

    def is_group_followed(self, group_id: str, /) -> Response[DefaultResponseType]:
        route = Route("GET", "/user/follows/group/{group_id}", group_id=group_id, authenticate=True)
        return self.request(route)

    def get_my_followed_users(self, *, limit: int, offset: int) -> Response[user.GetMultiUserResponse]:
        route = Route("GET", "/user/follows/user", authenticate=True)

        limit, offset = calculate_limits(limit, offset, max_limit=100)

        query: MANGADEX_QUERY_PARAM_TYPE = {"limit": limit, "offset": offset}

        return self.request(route, params=query)

    def is_user_followed(self, user_id: str, /) -> Response[DefaultResponseType]:
        route = Route("GET", "/user/follows/user/{user_id}", user_id=user_id, authenticate=True)
        return self.request(route)

    def get_user_custom_list_follows(self, limit: int, offset: int) -> Response[custom_list.GetMultiCustomListResponse]:
        route = Route("GET", "/user/follows/list", authenticate=True)

        limit, offset = calculate_limits(limit, offset, max_limit=100)
        query: MANGADEX_QUERY_PARAM_TYPE = {"limit": limit, "offset": offset}

        return self.request(route, params=query)

    def is_custom_list_followed(self, custom_list_id: str, /) -> Response[DefaultResponseType]:
        route = Route("GET", "/user/follows/list/{custom_list_id}", custom_list_id=custom_list_id, authenticate=True)
        return self.request(route)

    def get_user_followed_manga(
        self,
        limit: int,
        offset: int,
        includes: MangaIncludes | None,
    ) -> Response[manga.MangaSearchResponse]:
        route = Route("GET", "/user/follows/manga", authenticate=True)

        query: MANGADEX_QUERY_PARAM_TYPE = {"limit": limit, "offset": offset}

        if includes:
            query["includes"] = includes.to_query()

        return self.request(route, params=query)

    def is_manga_followed(self, manga_id: str, /) -> Response[DefaultResponseType]:
        route = Route("GET", "/user/follows/manga/{manga_id}", manga_id=manga_id, authenticate=True)
        return self.request(route)

    def create_account(self, *, username: str, password: str, email: str) -> Response[user.GetSingleUserResponse]:
        route = Route("POST", "/account/create")
        query: dict[str, Any] = {"username": username, "password": password, "email": email}
        return self.request(route, json=query)

    def activate_account(self, activation_code: str, /) -> Response[DefaultResponseType]:
        route = Route("POST", "/account/activate/{activation_code}", activation_code=activation_code)
        return self.request(route)

    def resend_activation_code(self, email: str, /) -> Response[DefaultResponseType]:
        route = Route("POST", "/account/activate/resend")
        query: dict[str, Any] = {"email": email}
        return self.request(route, json=query)

    def recover_account(self, email: str, /) -> Response[DefaultResponseType]:
        route = Route("POST", "/account/recover")
        query: dict[str, Any] = {"email": email}
        return self.request(route, json=query)

    def complete_account_recovery(self, recovery_code: str, /, *, new_password: str) -> Response[DefaultResponseType]:
        route = Route("POST", "/account/recover/{recovery_code}", recovery_code=recovery_code)
        query: dict[str, Any] = {"newPassword": new_password}
        return self.request(route, json=query)

    def ping_the_server(self) -> Response[str]:
        route = Route("GET", "/ping")
        return self.request(route)

    def legacy_id_mapping(
        self,
        mapping_type: legacy.LegacyMappingType,
        /,
        *,
        item_ids: list[int],
    ) -> Response[legacy.GetLegacyMappingResponse]:
        route = Route("POST", "/legacy/mapping")
        query: dict[str, Any] = {"type": mapping_type, "ids": item_ids}
        return self.request(route, json=query)

    def get_at_home_url(self, chapter_id: str, /, *, ssl: bool) -> Response[chapter.GetAtHomeResponse]:
        route = Route("GET", "/at-home/server/{chapter_id}", chapter_id=chapter_id)
        query: MANGADEX_QUERY_PARAM_TYPE = {"forcePort443": ssl}
        return self.request(route, params=query)

    def create_custom_list(
        self,
        *,
        name: str,
        visibility: CustomListVisibility | None,
        manga: list[str] | None,
    ) -> Response[custom_list.GetSingleCustomListResponse]:
        route = Route("POST", "/list", authenticate=True)

        query: dict[str, Any] = {"name": name}

        if visibility:
            query["visibility"] = visibility.value

        if manga:
            query["manga"] = manga

        return self.request(route, json=query)

    def get_custom_list(
        self,
        custom_list_id: str,
        /,
        *,
        includes: CustomListIncludes | None,
    ) -> Response[custom_list.GetSingleCustomListResponse]:
        route = Route("GET", "/list/{custom_list_id}", custom_list_id=custom_list_id)

        if includes:
            query: MANGADEX_QUERY_PARAM_TYPE = {"includes": includes.to_query()}
            return self.request(route, params=query)
        return self.request(route)

    def update_custom_list(
        self,
        custom_list_id: str,
        /,
        *,
        name: str | None,
        visibility: CustomListVisibility | None,
        manga: list[str] | None,
        version: int,
    ) -> Response[custom_list.GetSingleCustomListResponse]:
        route = Route("PUT", "/list/{custom_list_id}", custom_list_id=custom_list_id, authenticate=True)

        query: dict[str, Any] = {"version": version}

        if name:
            query["name"] = name

        if visibility:
            query["visibility"] = visibility.value

        if manga:
            query["manga"] = manga

        return self.request(route, json=query)

    def delete_custom_list(self, custom_list_id: str, /) -> Response[DefaultResponseType]:
        route = Route("DELETE", "/list/{custom_list_id}", custom_list_id=custom_list_id, authenticate=True)
        return self.request(route)

    def follow_custom_list(self, custom_list_id: str, /) -> Response[DefaultResponseType]:
        route = Route("POST", "/list/{custom_list_id}/follow", custom_list_id=custom_list_id, authenticate=True)
        return self.request(route)

    def unfollow_custom_list(self, custom_list_id: str, /) -> Response[DefaultResponseType]:
        route = Route("DELETE", "/list/{custom_list_id}/follow", custom_list_id=custom_list_id, authenticate=True)
        return self.request(route)

    def add_manga_to_custom_list(self, custom_list_id: str, /, *, manga_id: str) -> Response[DefaultResponseType]:
        route = Route(
            "POST",
            "/manga/{manga_id}/list/{custom_list_id}",
            manga_id=manga_id,
            custom_list_id=custom_list_id,
            authenticate=True,
        )
        return self.request(route)

    def remove_manga_from_custom_list(self, custom_list_id: str, /, *, manga_id: str) -> Response[DefaultResponseType]:
        route = Route(
            "DELETE",
            "/manga/{manga_id}/list/{custom_list_id}",
            manga_id=manga_id,
            custom_list_id=custom_list_id,
            authenticate=True,
        )
        return self.request(route)

    def get_my_custom_lists(self, limit: int, offset: int) -> Response[custom_list.GetMultiCustomListResponse]:
        route = Route("GET", "/user/list", authenticate=True)

        query: MANGADEX_QUERY_PARAM_TYPE = {"limit": limit, "offset": offset}

        return self.request(route, params=query)

    def get_users_custom_lists(
        self,
        user_id: str,
        /,
        *,
        limit: int,
        offset: int,
    ) -> Response[custom_list.GetMultiCustomListResponse]:
        route = Route("GET", "/user/{user_id}/list", user_id=user_id)

        query: MANGADEX_QUERY_PARAM_TYPE = {"limit": limit, "offset": offset}

        return self.request(route, params=query)

    def custom_list_manga_feed(
        self,
        custom_list_id: str,
        /,
        *,
        limit: int,
        offset: int,
        translated_language: list[common.LanguageCode] | None,
        original_language: list[common.LanguageCode] | None,
        excluded_original_language: list[common.LanguageCode] | None,
        content_rating: list[ContentRating] | None,
        excluded_groups: list[str] | None,
        excluded_uploaders: list[str] | None,
        include_future_updates: bool | None,
        created_at_since: datetime.datetime | None,
        updated_at_since: datetime.datetime | None,
        published_at_since: datetime.datetime | None,
        order: FeedOrderQuery | None,
        includes: ChapterIncludes | None,
        include_empty_pages: bool | None,
        include_future_publish_at: bool | None,
        include_external_url: bool | None,
    ) -> Response[chapter.GetMultiChapterResponse]:
        route = Route("GET", "/list/{custom_list_id}/feed", custom_list_id=custom_list_id)

        limit, offset = calculate_limits(limit, offset, max_limit=500)

        query: MANGADEX_QUERY_PARAM_TYPE = {"limit": limit, "offset": offset}

        if translated_language:
            query["translatedLanguage"] = translated_language

        if original_language:
            query["originalLanguage"] = original_language

        if excluded_original_language:
            query["excludedOriginalLanguage"] = excluded_original_language

        if content_rating:
            query["contentRating"] = [cr.value for cr in content_rating]

        if excluded_groups:
            query["excludedGroups"] = excluded_groups

        if excluded_uploaders:
            query["excludedUploaders"] = excluded_uploaders

        if include_future_updates:
            resolved = str(int(include_future_updates))
            query["includeFutureUpdates"] = resolved

        if created_at_since:
            query["createdAtSince"] = clean_isoformat(created_at_since)

        if updated_at_since:
            query["updatedAtSince"] = clean_isoformat(updated_at_since)

        if published_at_since:
            query["publishAtSince"] = clean_isoformat(published_at_since)

        if order:
            query["order"] = order.to_dict()

        if includes:
            query["includes"] = includes.to_query()

        if include_empty_pages:
            query["includeEmptyPages"] = include_empty_pages

        if include_future_publish_at:
            query["includeFuturePublishAt"] = include_future_publish_at

        if include_external_url:
            query["includeExternalUrl"] = include_external_url

        return self.request(route, params=query)

    def create_scanlation_group(
        self,
        *,
        name: str,
        website: str | None,
        irc_server: str | None,
        irc_channel: str | None,
        discord: str | None,
        contact_email: str | None,
        description: str | None,
        twitter: str | None,
        manga_updates: str | None,
        inactive: bool | None,
        publish_delay: str | datetime.timedelta | None,
    ) -> Response[scanlator_group.GetSingleScanlationGroupResponse]:
        route = Route("POST", "/group", authenticate=True)

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

        if manga_updates:
            query["mangaUpdates"] = manga_updates

        if isinstance(inactive, bool):
            query["inactive"] = inactive

        if publish_delay:
            if isinstance(publish_delay, datetime.timedelta):
                publish_delay = delta_to_iso(publish_delay)

            if not MANGADEX_TIME_REGEX.fullmatch(publish_delay):
                msg = "The `publish_delay` parameter must match the regex format."
                raise ValueError(msg)

            query["publishDelay"] = publish_delay

        return self.request(route, json=query)

    def view_scanlation_group(
        self,
        scanlation_group_id: str,
        /,
        *,
        includes: ScanlatorGroupIncludes | None,
    ) -> Response[scanlator_group.GetSingleScanlationGroupResponse]:
        route = Route("GET", "/group/{scanlation_group_id}", scanlation_group_id=scanlation_group_id)

        if includes:
            query: MANGADEX_QUERY_PARAM_TYPE = {"includes": includes.to_query()}
            return self.request(route, params=query)
        return self.request(route)

    def update_scanlation_group(
        self,
        scanlation_group_id: str,
        /,
        *,
        name: str | None,
        leader: str | None,
        members: list[str] | None,
        website: str | None,
        irc_server: str | None,
        irc_channel: str | None,
        discord: str | None,
        contact_email: str | None,
        description: str | None,
        twitter: str | None,
        manga_updates: str | None,
        focused_languages: list[common.LanguageCode] | None,
        inactive: bool | None,
        locked: bool | None,
        publish_delay: str | datetime.timedelta | None,
        version: int,
    ) -> Response[scanlator_group.GetSingleScanlationGroupResponse]:
        route = Route("PUT", "/group/{scanlation_group_id}", scanlation_group_id=scanlation_group_id, authenticate=True)

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

        if manga_updates is not MISSING:
            query["mangaUpdates"] = manga_updates

        if focused_languages is not MISSING:
            query["focusedLanguages"] = focused_languages

        if publish_delay:
            if isinstance(publish_delay, datetime.timedelta):
                publish_delay = delta_to_iso(publish_delay)

            if not MANGADEX_TIME_REGEX.fullmatch(publish_delay):
                msg = "The `publish_delay` parameter's string must match the regex pattern."
                raise ValueError(msg)

            query["publishDelay"] = publish_delay

        if isinstance(inactive, bool):
            query["inactive"] = inactive

        if isinstance(locked, bool):
            query["locked"] = locked

        return self.request(route, json=query)

    def delete_scanlation_group(self, scanlation_group_id: str, /) -> Response[DefaultResponseType]:
        route = Route("DELETE", "/group/{scanlation_group_id}", scanlation_group_id=scanlation_group_id, authenticate=True)
        return self.request(route)

    def follow_scanlation_group(self, scanlation_group_id: str, /) -> Response[DefaultResponseType]:
        route = Route(
            "POST",
            "/group/{scanlation_group_id}/follow",
            scanlation_group_id=scanlation_group_id,
            authenticate=True,
        )
        return self.request(route)

    def unfollow_scanlation_group(self, scanlation_group_id: str, /) -> Response[DefaultResponseType]:
        route = Route(
            "DELETE",
            "/group/{scanlation_group_id}/follow",
            scanlation_group_id=scanlation_group_id,
            authenticate=True,
        )
        return self.request(route)

    def author_list(
        self,
        *,
        limit: int,
        offset: int,
        ids: list[str] | None,
        name: str | None,
        order: AuthorListOrderQuery | None,
        includes: AuthorIncludes | None,
    ) -> Response[author.GetMultiAuthorResponse]:
        route = Route("GET", "/author")

        limit, offset = calculate_limits(limit, offset, max_limit=100)

        query: MANGADEX_QUERY_PARAM_TYPE = {"limit": limit, "offset": offset}

        if ids:
            query["ids"] = ids

        if name:
            query["name"] = name

        if order:
            query["order"] = order.to_dict()

        if includes:
            query["includes"] = includes.to_query()

        return self.request(route, params=query)

    def create_author(
        self,
        *,
        name: str,
        biography: common.LocalizedString | None,
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
    ) -> Response[author.GetSingleAuthorResponse]:
        route = Route("POST", "/author", authenticate=True)

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

        return self.request(route, json=query)

    def get_author(self, author_id: str, /, *, includes: AuthorIncludes | None) -> Response[author.GetSingleAuthorResponse]:
        route = Route("GET", "/author/{author_id}", author_id=author_id)

        if includes:
            query: MANGADEX_QUERY_PARAM_TYPE = {"includes": includes.to_query()}
            return self.request(route, params=query)

        return self.request(route)

    def update_author(
        self,
        author_id: str,
        *,
        name: str | None,
        biography: common.LocalizedString | None,
        twitter: str | None,
        pixiv: str | None,
        melon_book: str | None,
        fan_box: str | None,
        booth: str | None,
        nico_video: str | None,
        skeb: str | None,
        fantia: str | None,
        tumblr: str | None,
        youtube: str | None,
        website: str | None,
        version: int | None,
    ) -> Response[author.GetSingleAuthorResponse]:
        route = Route("PUT", "/author/{author_id}", author_id=author_id, authenticate=True)

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

    def delete_author(self, author_id: str, /) -> Response[DefaultResponseType]:
        route = Route("DELETE", "/author/{author_id}", author_id=author_id, authenticate=True)
        return self.request(route)

    def get_artist(self, artist_id: str, /, *, includes: ArtistIncludes | None) -> Response[artist.GetSingleArtistResponse]:
        route = Route("GET", "/author/{artist_id}", artist_id=artist_id)

        if includes:
            query: MANGADEX_QUERY_PARAM_TYPE = {"includes": includes.to_query()}
            return self.request(route, params=query)
        return self.request(route)

    def update_artist(
        self,
        author_id: str,
        *,
        name: str | None,
        biography: common.LocalizedString | None,
        twitter: str | None,
        pixiv: str | None,
        melon_book: str | None,
        fan_box: str | None,
        booth: str | None,
        nico_video: str | None,
        skeb: str | None,
        fantia: str | None,
        tumblr: str | None,
        youtube: str | None,
        website: str | None,
        version: int | None,
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

    def delete_artist(self, artist_id: str, /) -> Response[DefaultResponseType]:
        route = Route("DELETE", "/author/{artist_id}", artist_id=artist_id)
        return self.request(route)

    def get_report_reason_list(self, report_category: ReportCategory, /) -> Response[report.GetReportReasonResponse]:
        route = Route("GET", "/report/reasons/{report_category}", report_category=report_category.value, authenticate=True)
        return self.request(route)

    def get_reports_current_user(
        self,
        *,
        limit: int = 10,
        offset: int = 0,
        object_id: str | None,
        reason: ReportReason | None,
        category: ReportCategory | None,
        status: ReportStatus | None,
        order: ReportListOrderQuery | None,
        includes: UserReportIncludes | None,
    ) -> Response[report.GetUserReportReasonResponse]:
        limit, offset = calculate_limits(limit, offset, max_limit=100)

        route = Route("GET", "/report", authenticate=True)

        query: MANGADEX_QUERY_PARAM_TYPE = {"limit": limit, "offset": offset}

        if object_id:
            query["objectId"] = object_id

        if reason:
            query["reasonId"] = reason.value

        if category:
            query["category"] = category.value

        if status:
            query["status"] = status.value

        if order:
            query["order"] = order.to_dict()

        if includes:
            query["includes"] = includes.to_query()

        return self.request(route, params=query)

    def at_home_report(self, *, url: URL, success: bool, cached: bool, size: int, duration: int) -> Response[None]:
        route = Route("POST", "/report", base="https://api.mangadex.network")

        query: dict[str, Any] = {
            "url": str(url),
            "success": success,
            "cached": cached,
            "bytes": size,
            "duration": duration,
        }

        return self.request(route, json=query)

    def create_report(self, *, details: ReportDetails) -> Response[DefaultResponseType]:
        route = Route("POST", "/report", authenticate=True)

        query: dict[str, Any] = {
            "category": details.category.value,
            "reason": details.reason.value,
            "objectId": details.target_id,
            "details": details.details,
        }

        return self.request(route, json=query)

    def get_my_ratings(self, manga_ids: list[str], /) -> Response[statistics.GetPersonalMangaRatingsResponse]:
        route = Route("GET", "/rating", authenticate=True)

        query: MANGADEX_QUERY_PARAM_TYPE = {"manga": manga_ids}

        return self.request(route, params=query)

    def set_manga_rating(self, manga_id: str, /, *, rating: int) -> Response[Literal["ok", "error"]]:
        route = Route("POST", "/rating/{manga_id}", manga_id=manga_id, authenticate=True)

        query: dict[str, Any] = {"rating": rating}

        return self.request(route, json=query)

    def delete_manga_rating(self, manga_id: str, /) -> Response[Literal["ok", "error"]]:
        route = Route("DELETE", "/rating/{manga_id}", manga_id=manga_id, authenticate=True)

        return self.request(route)

    def get_chapter_statistics(
        self,
        chapter_id: str | None,
        chapter_ids: str | None,
    ) -> Response[statistics.GetCommentsStatisticsResponse]:
        if chapter_id:
            route = Route("GET", "/statistics/chapter/{chapter_id}", chapter_id=chapter_id, authenticate=True)
            return self.request(route)
        if chapter_ids:
            route = Route("GET", "/statistics/chapter", authenticate=True)
            return self.request(route, params={"chapter": chapter_ids})

        msg = "Either chapter_id or chapter_ids is required."
        raise ValueError(msg)

    def get_scanlation_group_statistics(
        self,
        scanlation_group_id: str | None,
        scanlation_group_ids: str | None,
    ) -> Response[statistics.GetCommentsStatisticsResponse]:
        if scanlation_group_id:
            route = Route(
                "GET",
                "/statistics/group/{scanlation_group_id}",
                scanlation_group_id=scanlation_group_ids,
                authenticate=True,
            )
            return self.request(route)
        if scanlation_group_ids:
            route = Route("GET", "/statistics/group", authenticate=True)
            return self.request(route, params={"group": scanlation_group_ids})

        msg = "Either chapter_id or chapter_ids is required."
        raise ValueError(msg)

    def get_manga_statistics(
        self,
        manga_id: str | None,
        manga_ids: list[str] | None,
        /,
    ) -> Response[statistics.GetMangaStatisticsResponse]:
        if manga_id:
            route = Route("GET", "/statistics/manga/{manga_id}", manga_id=manga_id, authenticate=True)
            return self.request(route)
        if manga_ids:
            route = Route("GET", "/statistics/manga", authenticate=True)
            query: MANGADEX_QUERY_PARAM_TYPE = {"manga": manga_ids}
            return self.request(route, params=query)

        msg = "Either `manga_id` or `manga_ids` must be passed."
        raise ValueError(msg)

    def open_upload_session(
        self,
        manga_id: str,
        /,
        *,
        scanlator_groups: list[str],
        chapter_id: str | None,
        version: int | None,
    ) -> Response[upload.BeginChapterUploadResponse]:
        query: dict[str, Any] = {"manga": manga_id, "groups": scanlator_groups}
        if chapter_id is not None:
            route = Route("POST", "/upload/begin/{chapter_id}", chapter_id=chapter_id, authenticate=True)
            query["version"] = version
        else:
            route = Route("POST", "/upload/begin", authenticate=True)

        return self.request(route, json=query)

    def abandon_upload_session(self, session_id: str, /) -> Response[None]:
        route = Route("DELETE", "/upload/{session_id}", session_id=session_id, authenticate=True)

        return self.request(route)

    def get_latest_settings_template(self) -> Response[dict[str, Any]]:
        route = Route("GET", "/settings/template", authenticate=True)

        return self.request(route)

    def get_specific_template_version(self, version: str) -> Response[dict[str, Any]]:
        route = Route("GET", "/settings/template/{version}", version=version, authenticate=True)

        return self.request(route)

    def get_user_settings(self) -> Response[SettingsPayload]:
        route = Route("GET", "/settings", authenticate=True)

        return self.request(route)

    def upsert_user_settings(self, settings: Settings, updated_at: datetime.datetime) -> Response[SettingsPayload]:
        route = Route("POST", "/settings", authenticate=True)

        query: dict[str, Any] = {
            "settings": settings,
            "updatedAt": clean_isoformat(updated_at),
        }

        return self.request(route, json=query)

    def create_forum_thread(self, thread_type: ForumThreadType, resource_id: str) -> Response[ForumPayloadResponse]:
        route = Route("POST", "/forums/thread", authenticate=True)

        query: dict[str, str] = {"type": thread_type.value, "id": resource_id}

        return self.request(route, json=query)

    def check_approval_required(
        self,
        manga_id: str,
        locale: common.LanguageCode,
    ) -> Response[upload.GetCheckApprovalRequired]:
        route = Route("POST", "/upload/check-approval-required", authenticate=True)

        query: dict[str, Any] = {"manga": manga_id, "locale": locale}

        return self.request(route, json=query)
