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
    "ArtistIncludes",
    "ArtistResponse",
    "ArtistAttributesResponse",
    "GetSingleArtistResponse",
    "GetMultiArtistResponse",
)

ArtistIncludes = Literal["manga"]


class ArtistAttributesResponse(TypedDict):
    """
    name: :class:`str`

    imageUrl: Optional[:class:`str`]

    biography: :class:`~hondana.types.LocalisedString`

    version: :class:`int`

    createdAt: :class:`str`

    updatedAt: :class:`str`
    """

    name: str
    imageUrl: Optional[str]
    biography: LocalisedString
    version: int
    createdAt: str
    updatedAt: str


class ArtistResponse(TypedDict):
    """
    id: :class:`str`

    type: Literal[``"artist"``]

    attributes: :class:`ArtistAttributesResponse`

    relationships: List[:class:`RelationshipResponse`]
        This key can contain minimal or full data depending on the ``includes[]`` parameter of it's request.
        See here for more info: https://api.mangadex.org/docs.html#section/Reference-Expansion
    """

    id: str
    type: Literal["artist"]
    attributes: ArtistAttributesResponse
    relationships: list[RelationshipResponse]


class GetSingleArtistResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    response: Literal[``"entity"``]

    data: List[:class:`ArtistResponse`]
    """

    result: Literal["ok", "error"]
    response: Literal["entity"]
    data: ArtistResponse


class GetMultiArtistResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    response: Literal[``"collection"``]

    data: List[:class:`ArtistResponse`]
    """

    result: Literal["ok", "error"]
    response: Literal["collection"]
    data: list[ArtistResponse]
