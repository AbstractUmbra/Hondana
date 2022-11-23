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

from typing_extensions import NotRequired


if TYPE_CHECKING:
    from .common import LanguageCode
    from .relationship import RelationshipResponse


__all__ = (
    "CoverResponse",
    "CoverAttributesResponse",
    "GetSingleCoverResponse",
    "GetMultiCoverResponse",
)


class CoverAttributesResponse(TypedDict):
    """
    volume: Optional[:class:`str`]

    fileName: :class:`str`

    description: Optional[:class:`str`]

    locale: Optional[:class:`~hondana.types.common.LanguageCode`]

    version: :class:`int`

    createdAt: :class:`str`

    updatedAt: :class:`str`
    """

    volume: Optional[str]
    fileName: str
    description: Optional[str]
    locale: Optional[LanguageCode]
    version: int
    createdAt: str
    updatedAt: str


class CoverResponse(TypedDict):
    """
    id: :class:`str`

    type: Literal[``"cover_art"``]

    attributes: :class:`~hondana.types.cover.CoverAttributesResponse`

    relationships: List[:class:`~hondana.types.relationship.RelationshipResponse`]
        This key is optional, in the event this payload is gotten from the "relationships" of another object.

        This key can contain minimal or full data depending on the ``includes[]`` parameter of its request.
        See here for more info: https://api.mangadex.org/docs.html#section/Reference-Expansion
    """

    id: str
    type: Literal["cover_art"]
    attributes: CoverAttributesResponse
    relationships: NotRequired[list[RelationshipResponse]]


class GetSingleCoverResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    response: Literal[``"entity"``]

    data: :class:`~hondana.types.cover.CoverResponse`
    """

    result: Literal["ok", "error"]
    response: Literal["collection"]
    data: CoverResponse


class GetMultiCoverResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    response: Literal[``"collection"``]

    data: List[:class:`~hondana.types.cover.CoverResponse`]

    limit: :class:`int`

    offset: :class:`int`

    total: :class:`int`
    """

    result: Literal["ok", "error"]
    response: Literal["collection"]
    data: list[CoverResponse]
    limit: int
    offset: int
    total: int
