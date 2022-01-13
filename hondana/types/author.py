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

from typing import TYPE_CHECKING, Literal, Optional, TypedDict


if TYPE_CHECKING:
    from .common import LocalisedString
    from .relationship import RelationshipResponse


__all__ = (
    "AuthorAttributesResponse",
    "AuthorResponse",
    "GetSingleAuthorResponse",
    "GetMultiAuthorResponse",
)


class AuthorAttributesResponse(TypedDict):
    """
    name: :class:`str`

    imageUrl: Optional[:class:`str`]

    biography: Optional[:class:`~hondana.types.LocalisedString`]

    twitter: Optional[:class:`str`]

    pixiv: Optional[:class:`str`]

    melonBook: Optional[:class:`str`]

    fanBox: Optional[:class:`str`]

    booth: Optional[:class:`str`]

    nicoVideo: Optional[:class:`str`]

    skeb: Optional[:class:`str`]

    fantia: Optional[:class:`str`]

    tumblr: Optional[:class:`str`]

    youtube: Optional[:class:`str`]

    weibo: Optional[:class:`str`]

    naver: Optional[:class:`str`]

    website: Optional[:class:`str`]

    version: :class:`int`

    createdAt: :class:`str`

    updatedAt: :class:`str`
    """

    name: str
    imageUrl: Optional[str]
    biography: Optional[LocalisedString]
    twitter: Optional[str]
    pixiv: Optional[str]
    melonBook: Optional[str]
    fanBox: Optional[str]
    booth: Optional[str]
    nicoVideo: Optional[str]
    skeb: Optional[str]
    fantia: Optional[str]
    tumblr: Optional[str]
    youtube: Optional[str]
    weibo: Optional[str]
    naver: Optional[str]
    website: Optional[str]
    version: int
    createdAt: str
    updatedAt: str


class AuthorResponse(TypedDict):
    """
    id: :class:`str`

    type: Literal[``"author"``]

    attributes: :class:`~hondana.types.AuthorAttributesResponse`

    relationships: List[:class:`RelationshipResponse`]
        This key can contain minimal or full data depending on the ``includes[]`` parameter of its request.
        See here for more info: https://api.mangadex.org/docs.html#section/Reference-Expansion
    """

    id: str
    type: Literal["author"]
    attributes: AuthorAttributesResponse
    relationships: list[RelationshipResponse]


class GetSingleAuthorResponse(TypedDict):
    """
    result: Literal[``ok``, ``error``]

    response: Literal[``entity``]

    data: :class:`~hondana.types.AuthorResponse`
    """

    result: Literal["ok", "error"]
    response: Literal["collection"]
    data: AuthorResponse


class GetMultiAuthorResponse(TypedDict):
    """
    result: Literal[``ok``, ``error``]

    response: Literal[``collection``]

    data: List[:class:`~hondana.types.AuthorResponse`]
    """

    result: Literal["ok", "error"]
    response: Literal["collection"]
    data: list[AuthorResponse]
