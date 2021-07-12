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
import logging
import sys
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Union
from urllib.parse import quote as _uriquote

import aiohttp

from . import __version__, utils
from .errors import APIException, LoginError, RefreshError

if TYPE_CHECKING:
    from .types.payloads import LoginPayload, RefreshPayload

__all__ = ("HTTPClient", "Route")

LOGGER = logging.getLogger(__name__)


async def json_or_text(response: aiohttp.ClientResponse) -> Union[dict[str, Any], str]:
    text = await response.text(encoding="utf-8")
    try:
        if response.headers["content-type"] == "application/json":
            return json.loads(text)
    except KeyError:
        pass

    return text


class Route:
    BASE: ClassVar[str] = "https://api.mangadex.org"

    def __init__(self, verb: str, path: str, **parameters: Any) -> None:
        self.verb: str = verb
        self.path: str = path
        url = self.BASE + self.path
        if parameters:
            url = url.format_map({k: _uriquote(v) if isinstance(v, str) else v for k, v in parameters.items()})
        self.url: str = url


class HTTPClient:
    """Underlying HTTP Client for the Mangadex API.

    Attributes
    -----------
    login: :class:`str`
        Your login username for the API. Used in conjuction with your password to generate an authentication token.
    password: :class:`str`
        Your login password for the API. Used in conjuction with your username to generate an authentication token.
    session: Optional[:class:`aiohttp.ClientSession`]
        A aiohttp ClientSession to use instead of creating one.

    .. note::
        If you do not pass a login and password then we cannot actually login and will error.

    .. note::
        The :class:`aiohttp.ClientSession` passed via constructor will have headers and authentication set. Do not pass one you plan to re-use for other things, lest you leak your login data.

    Raises
    -------
    ValueError
        You failed to pass appropriate login information (login and password, or a token).
    """

    __slots__ = ("login", "password", "__session", "_token", "__refresh_token", "__last_refresh", "user_agent")

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
        user_agent = "Mangadex.py (https://github.com/AbstractUmbra/mangadex.py {0}) Python/{1[0]}.{1[1]} aiohttp/{2}"
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

    async def _get_token(self) -> str:
        """|coro|

        This private method will login to Mangadex with the login username and password to retrieve a JWT auth token.

        Returns
        --------
        :class:`str`
            The authentication token we will use.

        Raises
        -------
        LoginError
            The passed username and password are incorrect.

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

        Returns
        --------
        :class:`str`
            The authentication token we just refreshed.

        Raises
        -------
        RefreshError
            We were unable to refresh the token.

        .. note::
            This does not use :meth:`HTTPClient.request` due to circular usage of request > generate token.
        """
        LOGGER.debug("Token is older than 15 minutes, attempting a refresh.")

        if self.__session is None:
            self.__session = await self._generate_session()

        route = Route("POST", "/auth/refresh")
        async with self.__session.post(route.url, json={"token": self._token}) as response:
            data: RefreshPayload = await response.json()

        if 300 > response.status >= 200:
            text = await response.text()
            LOGGER.debug("Error (code %d) when trying to refresh a token: %s", text, response.status)
            raise RefreshError(text, response.status, self.__last_refresh)

        if self._token == data["token"]["session"]:
            LOGGER.debug("Token refreshed successfully and matches.")
            return self._token

        raise RefreshError("Token was refreshed but a new token was given?", 200, self.__last_refresh)

    async def _try_token(self) -> str:
        """|coro|

        This private method will try and use the existing :attr:`_auth` to authenticate to the API.
        If this is unset, or returns a non-2xx response code, we will refresh the JWT / request another one.

        Returns
        --------
        :class:`str`
            The authentication token we generated, refreshed or already had that is still valid.

        Raises
        -------
        APIError
            Something went wrong with testing our authentication against the API.

        .. note::
            This does not use :meth:`HTTPClient.request` due to circular usage of request > generate token.
        """
        if self._token is None:
            LOGGER.debug("No jwt set yet, will attempt to generate one.")
            token = await self._get_token()
            return token

        if self.__last_refresh is not None:
            now = datetime.datetime.utcnow()
            if (now - datetime.timedelta(minutes=15)) > self.__last_refresh:
                refreshed = await self._refresh_token()
                if refreshed:
                    return self._token

        LOGGER.debug("Attempting to validate token: %s", self._token)
        route = Route("GET", "/auth/check")

        if self.__session is None:
            self.__session = await self._generate_session()

        async with self.__session.get(route.url, headers={"Authorization": f"Bearer {self._token}"}) as response:
            data = await response.json()

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

    async def request(self, route: Route, **kwargs: Any) -> Optional[Union[dict[Any, Any], str]]:
        """|coro|

        This performs the HTTP request, handling authentication tokens when doing it.

        Parameters
        -----------
        route: :class:`Route`
            The route describes the http verb and endpoint to hit, the request is the one that takes in the query params or request body.

        Returns
        --------
        Optional[Union[dict[Any, Any], str]]
            The potential response data we got from the request.

        Raises
        -------
        APIException
            Something went wrong with this request.

        Raises
        -------
        APIException
            A generic exception raised when the HTTP response code is non 2xx.
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

            if 300 >> response.status >= 200:
                return data
            raise APIException(str(data), response.status)
