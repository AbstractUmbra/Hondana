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
import webbrowser
from secrets import token_urlsafe
from typing import TYPE_CHECKING, Literal, Optional, TypedDict, Union, final

import yarl
from aiohttp import web as aiohttp_web

from .utils import MISSING, AuthRoute, php_query_builder


if TYPE_CHECKING:
    from .http import HTTPClient
    from .utils import MANGADEX_QUERY_PARAM_TYPE

LOGGER = logging.getLogger("hondana.oauth2")

OAuthTokenPayload = TypedDict(
    "OAuthTokenPayload",
    {
        "access_token": str,
        "expires_in": int,
        "refresh_expires_in": int,
        "refresh_token": str,
        "token_type": Literal["Bearer"],
        "id_token": str,
        "not-before-policy": int,
        "session_state": str,
        "scope": str,
    },
)


@final
class OAuth2Handler:
    given_state: str
    code: str
    sent_state: str
    access_token: str
    access_expires: datetime.datetime
    refresh_token: str
    refresh_expires: datetime.datetime
    token_type: Literal["Bearer"]
    id_token: str
    _scope: str

    __slots__ = (
        "given_state",
        "session_state",
        "code",
        "sent_state",
        "access_token",
        "access_expires",
        "refresh_token",
        "refresh_expires",
        "token_type",
        "id_token",
        "_scope",
    )

    def __init__(self) -> None:
        self.given_state = MISSING
        self.code = MISSING
        self.sent_state = MISSING
        self.access_token = MISSING
        self.access_expires = MISSING
        self.refresh_token = MISSING
        self.refresh_expires = MISSING
        self.token_type = MISSING
        self.id_token = MISSING
        self._scope = MISSING

    @property
    def scope(self) -> list[str]:
        return self._scope.split(" ")

    @scope.setter
    def scope(self, other: Union[str, list[str]]) -> None:
        if isinstance(other, list):
            self._scope = " ".join(other)
            return
        self._scope = other

    def update_with_token_payload(self, data: OAuthTokenPayload) -> None:
        self.access_token = data["access_token"]
        self.access_expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=data["expires_in"])
        self.refresh_token = data["refresh_token"]
        self.refresh_expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            seconds=data["refresh_expires_in"]
        )
        self.token_type = data["token_type"]
        self.id_token = data["id_token"]
        self._scope = data["scope"]


class OAuth2Client:
    __slots__ = (
        "client_id",
        "client_secret",
        "app",
        "_client",
        "_site",
        "_redirect_uri",
        "_has_auth_data",
        "_has_token_data",
        "__auth_handler",
    )

    def __init__(
        self,
        client: HTTPClient,
        /,
        *,
        redirect_uri: str,
        client_id: str,
        client_secret: Optional[str] = None,
        webapp: Optional[aiohttp_web.Application] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        self._client: HTTPClient = client
        self._redirect_uri: str = redirect_uri
        self.client_id: str = client_id
        self.client_secret: Optional[str] = client_secret
        if webapp:
            self.app: aiohttp_web.Application = webapp
        else:
            self.app = self.create_webapp()
        self.add_routes()
        self._site: Optional[aiohttp_web.AppRunner] = None
        self._has_auth_data: asyncio.Event = asyncio.Event()
        self._has_token_data: asyncio.Event = asyncio.Event()
        self.__auth_handler: OAuth2Handler = OAuth2Handler()

    @property
    def scopes(self) -> list[str]:
        """The OAuth2 Client's scopes for requesting access."""
        return self.__auth_handler.scope

    @scopes.setter
    def scopes(self, other: Union[str, list[str]]) -> None:
        self.__auth_handler.scope = other

    @property
    def redirect_uri(self) -> str:
        """The Oauth2 Client's redirect uri."""
        return self._redirect_uri

    @redirect_uri.setter
    def redirect_uri(self, other: str) -> None:
        self._redirect_uri = other

    @property
    def access_token(self) -> str:
        return self.__auth_handler.access_token

    @property
    def access_token_expires(self) -> datetime.datetime:
        return self.__auth_handler.access_expires

    def access_token_has_expired(self) -> bool:
        now = datetime.datetime.now(datetime.timezone.utc)

        return now > self.__auth_handler.access_expires

    @property
    def refresh_token(self) -> str:
        return self.__auth_handler.refresh_token

    @property
    def refresh_token_expires(self) -> datetime.datetime:
        return self.__auth_handler.refresh_expires

    def app_is_running(self) -> bool:
        if self._site:
            return bool(self._site.server)

        return False

    def refresh_token_has_expired(self) -> bool:
        now = datetime.datetime.now(datetime.timezone.utc)

        return now > self.refresh_token_expires

    async def close(self) -> None:
        if self._site:
            await self._site.shutdown()
        if self._has_auth_data.is_set():
            self._has_auth_data.clear()
        if self._has_token_data.is_set():
            self._has_token_data.clear()

    async def wait_for_auth_response(self, timeout: Optional[float] = None) -> None:
        await asyncio.wait_for(self._has_auth_data.wait(), timeout=timeout)
        self._has_auth_data.clear()

    async def wait_for_token_response(self, timeout: Optional[float] = None) -> None:
        await asyncio.wait_for(self._has_token_data.wait(), timeout=timeout)
        self._has_token_data.clear()

    @staticmethod
    def create_webapp() -> aiohttp_web.Application:
        return aiohttp_web.Application(logger=LOGGER)

    def add_routes(self) -> None:
        self.app.add_routes([aiohttp_web.get("/auth_code", self.auth_code)])

    async def run_app(self) -> None:
        uri = yarl.URL(self.redirect_uri)
        runner = aiohttp_web.AppRunner(self.app)
        await runner.setup()
        site = aiohttp_web.TCPSite(runner, host="localhost", port=3000)
        await site.start()

        LOGGER.info("Webserver now running at '%s' on port '%d'", uri.host, uri.port)

        self._site = runner

    async def auth_code(self, request: aiohttp_web.Request) -> aiohttp_web.Response:
        session_state = request.rel_url.query["session_state"]
        state = request.rel_url.query["state"]
        code = request.rel_url.query["code"]

        await self.request_auth_token(session_state, state, code)

        return aiohttp_web.Response(body=f"State: {state}\nCode: {code}")

    async def request_auth_token(self, session_state: str, state: str, code: str, /) -> None:
        self.__auth_handler.session_state = session_state
        self.__auth_handler.code = code
        self.__auth_handler.given_state = state

        route = AuthRoute("POST", "/token")

        params: MANGADEX_QUERY_PARAM_TYPE = {
            "grant_type": "authorization_code",
            "code": self.__auth_handler.code,
            "redirect_uri": f"{self.redirect_uri}/auth_code",
            "client_id": self.client_id,
        }

        data: OAuthTokenPayload = await self._client.request(
            route, data=params, headers={"Content-Type": "application/x-www-form-urlencoded"}, bypass=True
        )

        self.__auth_handler.update_with_token_payload(data)
        self._has_auth_data.set()

    async def perform_token_refresh(self, *, oauth_scopes: list[str]) -> None:
        route = AuthRoute("POST", "/token")

        params: MANGADEX_QUERY_PARAM_TYPE = {
            "grant_type": "refresh_token",
            "refresh_token": self.__auth_handler.refresh_token,
            "scope": " ".join(oauth_scopes),
            "client_id": self.client_id,
        }

        data: OAuthTokenPayload = await self._client.request(
            route, data=params, headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        self.__auth_handler.update_with_token_payload(data)
        self._has_token_data.set()

    def generate_auth_url(self, *, oauth_scopes: list[str], open: bool = False) -> yarl.URL:
        route = AuthRoute("GET", "/auth")

        state_secret = token_urlsafe(16)
        params: MANGADEX_QUERY_PARAM_TYPE = {
            "scope": " ".join(oauth_scopes),
            "client_id": self.client_id,
            "grant_type": "authorization_code",
            "response_type": "code",
            "redirect_uri": f"{self.redirect_uri}/auth_code",
            "state": state_secret,
        }

        url = yarl.URL(route.url).with_query(php_query_builder(params))
        self.__auth_handler.sent_state = state_secret

        if open:
            print(
                "Now trying to open the authorization URL in your browser. "
                "Sign in as normal and you will then have an authorization code displayed and sent to this app.\n"
                f"If opening the URL fails, copy and paste this into your browser:-\n'{url}'"
            )
            webbrowser.open(str(url))

        return url
