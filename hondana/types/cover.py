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

from typing import Literal, Optional, TypedDict

from .relationship import RelationshipResponse


__all__ = (
    "CoverIncludes",
    "CoverOrderQuery",
    "GetCoverResponse",
    "CoverResponse",
    "CoverAttributesResponse",
    "GetCoverListResponse",
)

CoverIncludes = Literal["manga", "user"]


class CoverOrderQuery(TypedDict, total=False):
    """
    createdAt: Literal[``"asc"``, ``"desc"``]

    updatedAt: Literal[``"asc"``, ``"desc"``]

    volume: Literal[``"asc"``, ``"desc"``]
    """

    createdAt: Literal["asc", "desc"]
    updatedAt: Literal["asc", "desc"]
    volume: Literal["asc", "desc"]


class CoverAttributesResponse(TypedDict):
    """
    volume: Optional[:class:`str`]

    fileName: :class:`str`

    description: :class:`str`

    version: :class:`int`

    createdAt: :class:`str`

    updatedAt: :class:`str`
    """

    volume: Optional[str]
    fileName: str
    description: str
    version: int
    createdAt: str
    updatedAt: str


class CoverResponse(TypedDict):
    """
    id: :class:`str`

    type: Literal[``"cover_art"``]

    attributes: :class:`CoverAttributesResponse`
    """

    id: str
    type: Literal["cover_art"]
    attributes: CoverAttributesResponse
    relationships: list[RelationshipResponse]


class GetCoverResponse(TypedDict):
    """
    result: :class:`str`

    data: :class:`CoverResponse`

    relationships: List[:class:`RelationshipResponse`]
        This key can contain minimal or full data depending on the ``includes[]`` parameter of it's request.
        See here for more info: https://api.mangadex.org/docs.html#section/Reference-Expansion
    """

    result: str
    data: CoverResponse


class GetCoverListResponse(TypedDict):
    """
    results: List[:class:`GetCoverResponse`]

    limit: :class:`int`

    offset: :class:`int`

    total: :class:`int`
    """

    results: list[GetCoverResponse]
    limit: int
    offset: int
    total: int
