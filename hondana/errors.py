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

import aiohttp


__all__ = (
    "AuthenticationRequired",
    "APIException",
    "LoginError",
    "RefreshError",
    "NotFound",
    "BadRequest",
    "Unauthorized",
    "Forbidden",
    "UploadInProgress",
    "UploadMangaNotFound",
)


class AuthenticationRequired(Exception):
    """An exception to be raised when authentication is required to use this endpoint."""


class APIException(Exception):
    """Generic API error when the response code is a non 2xx error."""

    def __init__(self, response: aiohttp.ClientResponse, message: str, response_code: int) -> None:
        self.response: aiohttp.ClientResponse = response
        self.message: str = message
        self.response_code: int = response_code
        super().__init__(self.response, self.message, self.response_code)


class LoginError(APIException):
    """An error during the login process."""


class RefreshError(APIException):
    """An error during the token refresh process."""

    def __init__(
        self, response: aiohttp.ClientResponse, message: str, response_code: int, last_refresh: datetime.datetime
    ) -> None:
        self.response: aiohttp.ClientResponse = response
        self.message: str = message
        self.response_code: int = response_code
        self.last_refresh: datetime.datetime = last_refresh
        super().__init__(response, message, response_code)


class NotFound(APIException):
    """An error for when the requested API item was not found."""

    def __init__(self, response: aiohttp.ClientResponse, message: str) -> None:
        self.response: aiohttp.ClientResponse = response
        self.message: str = message
        super().__init__(response, message, 404)


class BadRequest(APIException):
    """An error for when the API query was malformed."""

    def __init__(self, response: aiohttp.ClientResponse, message: str) -> None:
        self.response: aiohttp.ClientResponse = response
        self.message: str = message
        super().__init__(response, message, 400)


class Unauthorized(APIException):
    """An error for when you are unauthorized on this API endpoint."""

    def __init__(self, response: aiohttp.ClientResponse, message: str) -> None:
        self.response: aiohttp.ClientResponse = response
        self.message: str = message
        super().__init__(response, message, 401)


class Forbidden(APIException):
    """An error for when your authorization was rejected."""

    def __init__(self, response: aiohttp.ClientResponse, message: str) -> None:
        self.response: aiohttp.ClientResponse = response
        self.message: str = message
        super().__init__(response, message, 403)


class UploadInProgress(Exception):
    def __init__(self, message: str) -> None:
        self.message: str = message

    def __str__(self) -> str:
        return self.message


class UploadMangaNotFound(Exception):
    def __init__(self, message: str) -> None:
        self.message: str = message

    def __str__(self) -> str:
        return self.message
