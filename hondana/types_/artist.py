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

from typing import TYPE_CHECKING, Literal, TypedDict

if TYPE_CHECKING:
    from typing import NotRequired

    from .common import LocalizedString
    from .relationship import RelationshipResponse


__all__ = (
    "ArtistResponse",
    "ArtistAttributesResponse",
    "GetSingleArtistResponse",
    "GetMultiArtistResponse",
)


class ArtistAttributesResponse(TypedDict):
    """
    name: :class:`str`

    imageUrl: Optional[:class:`str`]

    biography: :class:`~hondana.types_.common.LocalizedString`

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

    namicomi: Optional[:class:`str`]

    website: Optional[:class:`str`]

    version: :class:`int`

    createdAt: :class:`str`

    updatedAt: :class:`str`
    """

    name: str
    imageUrl: str | None
    biography: LocalizedString
    twitter: str | None
    pixiv: str | None
    melonBook: str | None
    fanBox: str | None
    booth: str | None
    nicoVideo: str | None
    skeb: str | None
    fantia: str | None
    tumblr: str | None
    youtube: str | None
    weibo: str | None
    naver: str | None
    namicomi: str | None
    website: str | None
    version: int
    createdAt: str
    updatedAt: str


class ArtistResponse(TypedDict):
    """
    id: :class:`str`

    type: Literal[``"artist"``]

    attributes: :class:`~hondana.types_.artist.ArtistAttributesResponse`

    relationships: List[:class:`~hondana.types_.relationship.RelationshipResponse`]
        This key is optional, in the event this payload is gotten from the "relationships" of another object.

        This key can contain minimal or full data depending on the ``includes[]`` parameter of its request.
        See here for more info: https://api.mangadex.org/docs.html#section/Reference-Expansion
    """

    id: str
    type: Literal["artist"]
    attributes: ArtistAttributesResponse
    relationships: NotRequired[list[RelationshipResponse]]


class GetSingleArtistResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    response: Literal[``"entity"``]

    data: List[:class:`~hondana.types_.artist.ArtistResponse`]
    """

    result: Literal["ok", "error"]
    response: Literal["entity"]
    data: ArtistResponse


class GetMultiArtistResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    response: Literal[``"collection"``]

    data: List[:class:`~hondana.types_.artist.ArtistResponse`]

    limit: :class:`int`

    offset: :class:`int`

    total: :class:`int`
    """

    result: Literal["ok", "error"]
    response: Literal["collection"]
    data: list[ArtistResponse]
    limit: int
    offset: int
    total: int
