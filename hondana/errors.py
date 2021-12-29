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

from typing import TYPE_CHECKING

import aiohttp


if TYPE_CHECKING:
    from .types.errors import ErrorType

__all__ = (
    "AuthenticationRequired",
    "UploadInProgress",
    "MangaDexServerError",
    "APIException",
    "NotFound",
    "BadRequest",
    "Unauthorized",
    "Forbidden",
)


class AuthenticationRequired(Exception):
    """An exception to be raised when authentication is required to use this endpoint."""


class UploadInProgress(Exception):
    """An exception to be raised when an upload in progress is already found for the logged in user."""

    def __init__(self, message: str, /, *, session_id: str) -> None:
        self.message: str = message
        self.session_id: str = session_id
        super().__init__(self.message, self.session_id)

    def __str__(self) -> str:
        return f"An upload session was already found, it's ID is: {self.session_id}"


class MangaDexServerError(Exception):
    """Generic exception type for when MangaDex is down."""

    def __init__(self, response: aiohttp.ClientResponse, /, *, status_code: int) -> None:
        self.response: aiohttp.ClientResponse = response
        self.status_code: int = status_code
        super().__init__(self.response, self.status_code)


class APIException(Exception):
    """Generic API error when the response code is a non 2xx error."""

    def __init__(self, response: aiohttp.ClientResponse, /, *, status_code: int, errors: list[ErrorType]) -> None:
        self.response: aiohttp.ClientResponse = response
        self.status_code: int = status_code
        self.errors: list[ErrorType] = errors
        super().__init__(self.response, self.status_code, self.errors)


class BadRequest(APIException):
    """An error for when the API query was malformed."""

    def __init__(self, response: aiohttp.ClientResponse, /, *, errors: list[ErrorType]) -> None:
        self.response: aiohttp.ClientResponse = response
        self.status_code: int = 400
        self.errors: list[ErrorType] = errors
        super().__init__(response, status_code=self.status_code, errors=errors)


class Unauthorized(APIException):
    """An error for when you are unauthorized on this API endpoint."""

    def __init__(self, response: aiohttp.ClientResponse, /, *, errors: list[ErrorType]) -> None:
        self.response: aiohttp.ClientResponse = response
        self.status_code: int = 401
        self.errors: list[ErrorType] = errors
        super().__init__(response, status_code=self.status_code, errors=errors)


class Forbidden(APIException):
    """An error for when your authorization was rejected."""

    def __init__(self, response: aiohttp.ClientResponse, /, *, errors: list[ErrorType]) -> None:
        self.response: aiohttp.ClientResponse = response
        self.status_code: int = 403
        self.errors: list[ErrorType] = errors
        super().__init__(response, status_code=self.status_code, errors=errors)


class NotFound(APIException):
    """An error for when the requested API item was not found."""

    def __init__(self, response: aiohttp.ClientResponse, /, *, errors: list[ErrorType]) -> None:
        self.response: aiohttp.ClientResponse = response
        self.status_code: int = 404
        self.errors: list[ErrorType] = errors
        super().__init__(response, status_code=self.status_code, errors=errors)
