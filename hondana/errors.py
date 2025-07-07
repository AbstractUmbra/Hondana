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

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import aiohttp

    from .types_.errors import ErrorType

__all__ = (
    "APIException",
    "AuthenticationRequired",
    "BadRequest",
    "Forbidden",
    "MangaDexServerError",
    "NotFound",
    "PreviousAPIVersionRequest",
    "RefreshTokenFailure",
    "TermsOfServiceNotAccepted",
    "Unauthorized",
    "UploadInProgress",
)


class Error:
    """
    Common Error type class representing an error returned from MangaDex.

    Attributes
    ----------
    error_id: :class:`str`
        The UUID representing this error.
    error_status: :class:`int`
        The HTTP status code of this error.
    error_title: :class:`str`
        The title summary of this error.
    error_detail: :class:`str`
        The detailed report of this error.
    """

    __slots__ = (
        "error_detail",
        "error_id",
        "error_status",
        "error_title",
    )

    def __init__(self, error: ErrorType) -> None:
        self.error_id: str = error["id"]
        self.error_status: int = error["status"]
        self.error_title: str = error["title"]
        self.error_detail: str = error["detail"]

    def __repr__(self) -> str:
        return f"<Error status={self.error_status} title={self.error_title!r} detail={self.error_detail!r}>"

    def __str__(self) -> str:
        return f"Error: {self.error_title}: {self.error_detail}"


class AuthenticationRequired(Exception):
    """An exception to be raised when authentication is required to use this endpoint."""


class RefreshTokenFailure(Exception):
    """An exception to be raised when trying to use or access the refresh token fails.

    Attriutes
    ----------
    message: :class:`str`
        The error message.
    response: :class:`aiohttp.ClientResponse`
        The client response the error originated from.
    data: Dict[:class:`str`, :class:`~typing.Any`]
        The data from the error.
    """

    def __init__(self, message: str, /, response: aiohttp.ClientResponse, response_data: dict[str, Any]) -> None:
        self.message = message
        self.response = response
        self.data = response_data

    @property
    def status(self) -> int:
        """The HTTP response code from the error we received.

        Returns
        -------
        :class:`int`
        """
        return self.response.status


class UploadInProgress(Exception):
    """An exception to be raised when an upload in progress is already found for the logged-in user.

    Attributes
    ----------
    message: class:`str`
        The message returned with this error.
    session_id: :class:`str`
        The already existing session ID.
    """

    __slots__ = (
        "message",
        "session_id",
    )

    def __init__(self, message: str, /, *, session_id: str) -> None:
        self.message: str = message
        self.session_id: str = session_id
        super().__init__(self.message, self.session_id)

    def __str__(self) -> str:
        return f"An upload session was already found, it's ID is: {self.session_id}"


class MangaDexServerError(Exception):
    """Generic exception type for when MangaDex is down.

    Attributes
    ----------
    response: :class:`aiohttp.ClientResponse`
        The response object pertaining to this request.
    status_code: :class:`int`
        The HTTP status code for this request.
    """

    __slots__ = (
        "response",
        "status_code",
    )

    def __init__(self, response: aiohttp.ClientResponse, /, *, status_code: int) -> None:
        self.response: aiohttp.ClientResponse = response
        self.status_code: int = status_code
        super().__init__(self.response, self.status_code)


class APIException(Exception):
    """Generic API error when the response code is a non 2xx error.

    Attributes
    ----------
    response: :class:`aiohttp.ClientResponse`
        The response object pertaining to this request.
    status_code: :class:`int`
        The HTTP status code for this request.
    response_id: :class:`str`
        The UUID relating to this failed HTTP request.
        This is to be used when contacting MangaDex about an error.
    errors: List[:class:`~hondana.errors.Error`]
        The list of errors returned from MangaDex.
    """

    __slots__ = (
        "_errors",
        "errors",
        "response",
        "response_id",
        "status_code",
    )

    def __init__(self, response: aiohttp.ClientResponse, /, *, status_code: int, errors: list[ErrorType]) -> None:
        self.response: aiohttp.ClientResponse = response
        self.status_code: int = status_code
        self.response_id: str = response.headers["x-request-id"]
        self._errors: list[ErrorType] = errors
        self.errors: list[Error] = []
        self.errors.extend(Error(item) for item in self._errors)
        super().__init__(self.status_code, self.errors)

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"response_id={self.response_id} "
            f"status_code={self.status_code} "
            f"error_amount: {len(self.errors)}>"
        )

    def __str__(self) -> str:
        return (
            f"HTTP Status: {self.status_code} and response id: {self.response_id} :: "
            f"{', '.join([error.error_detail for error in self.errors])}"
        )


class BadRequest(APIException):
    """An error for when the API query was malformed.

    Attributes
    ----------
    response: :class:`aiohttp.ClientResponse`
        The response object pertaining to this request.
    status_code: Literal[``400``]
        The HTTP status code for this request.
    response_id: :class:`str`
        The UUID relating to this failed HTTP request.
        This is to be used when contacting MangaDex about an error.
    errors: List[:class:`~hondana.errors.Error`]
        The list of errors returned from MangaDex.
    """

    def __init__(self, response: aiohttp.ClientResponse, /, *, errors: list[ErrorType]) -> None:
        super().__init__(response, status_code=400, errors=errors)


class PreviousAPIVersionRequest(BadRequest):
    """
    An error for when the API query matches the criteria of an older API version.

    Attributes
    ----------
    response: :class:`aiohttp.ClientResponse`
        The response object pertaining to this request.
    status_code: Literal[``400``]
        The HTTP status code for this request.
    response_id: :class:`str`
        The UUID relating to this failed HTTP request.
        This is to be used when contacting MangaDex about an error.
    errors: List[:class:`~hondana.errors.Error`]
        The list of errors returned from MangaDex.
    """

    def __init__(self, response: aiohttp.ClientResponse, /) -> None:
        super().__init__(response, errors=[])

    def __str__(self) -> str:
        return (
            f"HTTP Status: {self.status_code} and response id: {self.response_id} :: "
            "Your API request matches the critera for MangaDex API version <5."
        )


class Unauthorized(APIException):
    """An error for when you are unauthorized on this API endpoint.

    Attributes
    ----------
    response: :class:`aiohttp.ClientResponse`
        The response object pertaining to this request.
    status_code: Literal[``401``]
        The HTTP status code for this request.
    response_id: :class:`str`
        The UUID relating to this failed HTTP request.
        This is to be used when contacting MangaDex about an error.
    errors: List[:class:`~hondana.errors.Error`]
        The list of errors returned from MangaDex.
    """

    def __init__(self, response: aiohttp.ClientResponse, /, *, errors: list[ErrorType]) -> None:
        super().__init__(response, status_code=401, errors=errors)


class Forbidden(APIException):
    """An error for when your authorization was rejected.

    Attributes
    ----------
    response: :class:`aiohttp.ClientResponse`
        The response object pertaining to this request.
    status_code: Literal[``403``]
        The HTTP status code for this request.
    response_id: :class:`str`
        The UUID relating to this failed HTTP request.
        This is to be used when contacting MangaDex about an error.
    errors: List[:class:`~hondana.errors.Error`]
        The list of errors returned from MangaDex.
    """

    def __init__(self, response: aiohttp.ClientResponse, /, *, errors: list[ErrorType]) -> None:
        super().__init__(response, status_code=403, errors=errors)


class NotFound(APIException):
    """An error for when the requested API item was not found."

    Attributes
    ----------
    response: :class:`aiohttp.ClientResponse`
        The response object pertaining to this request.
    status_code: Literal[``404``]
        The HTTP status code for this request.
    response_id: :class:`str`
        The UUID relating to this failed HTTP request.
        This is to be used when contacting MangaDex about an error.
    errors: List[:class:`~hondana.errors.Error`]
        The list of errors returned from MangaDex.
    """

    def __init__(self, response: aiohttp.ClientResponse, /, *, errors: list[ErrorType]) -> None:
        super().__init__(response, status_code=404, errors=errors)


class TermsOfServiceNotAccepted(Exception):
    """An error for when the ToS is not accepted prior to a chapter upload."""
