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

__all__ = ("APIException", "LoginError", "RefreshError")


class APIException(Exception):
    """Generic API error when the response code is a non 2xx error."""

    def __init__(self, message: str, response_code: int) -> None:
        self.message = message
        self.response_code = response_code
        super().__init__()


class LoginError(APIException):
    """An error during the login process."""


class RefreshError(APIException):
    """An error during the token refresh process."""

    def __init__(self, message: str, response_code: int, last_refresh: datetime.datetime) -> None:
        self.message = message
        self.response_code = response_code
        self.last_refresh = last_refresh
        super().__init__(message, response_code)
