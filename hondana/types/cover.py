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

    attributes: :class:`~hondana.types.CoverAttributesResponse`
    """

    id: str
    type: Literal["cover_art"]
    attributes: CoverAttributesResponse
    relationships: list[RelationshipResponse]


class GetSingleCoverResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    response: Literal[``"entity"``]

    data: :class:`~hondana.types.CoverResponse`
    """

    result: Literal["ok", "error"]
    response: Literal["collection"]
    data: CoverResponse


class GetMultiCoverResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    response: Literal[``"collection"``]

    data: List[:class:`~hondana.types.CoverResponse`]
    """

    result: Literal["ok", "error"]
    response: Literal["collection"]
    data: list[CoverResponse]
