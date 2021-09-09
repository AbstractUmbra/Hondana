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

from typing import Literal, TypedDict


__all__ = ("TokenPayload",)


class TokenPayload(TypedDict):
    """
    type: Literal[``session``]

    iss: Literal[``mangadex.org``]

    aud: Literal[``mangadex.org``]

    iat: :class:`int`

    nbf: :class:`int`

    exp: :class:`int`

    uid: :class:`str`

    rol: List[:class:`str`]

    prm: List[:class:`str`]

    sid: :class:`str`
    """

    typ: Literal["session"]
    iss: Literal["mangadex.org"]
    aud: Literal["mangadex.org"]
    iat: int
    nbf: int
    exp: int
    uid: str
    rol: list[str]
    prm: list[str]
    sid: str
