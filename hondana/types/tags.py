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
    from .common import LocalisedString
    from .relationship import RelationshipResponse


__all__ = (
    "TagResponse",
    "GetTagListResponse",
    "TagAttributesResponse",
)


class TagAttributesResponse(TypedDict):
    """
    name: :class:`~hondana.types.LocalisedString`

    description: List[:class:`~hondana.types.LocalisedString`]

    group: :class:`str`

    version: :class:`int`
    """

    name: LocalisedString
    description: list[LocalisedString]
    group: str
    version: int


class TagResponse(TypedDict):
    """
    id: :class:`str`

    type: Literal[``"tag"``]

    attributes: :class:`~hondana.types.TagAttributesResponse`

    relationships: List[:class:`~hondana.types.RelationshipResponse`]
        This key can contain minimal or full data depending on the ``includes[]`` parameter of its request.
        See here for more info: https://api.mangadex.org/docs.html#section/Reference-Expansion
    """

    id: str
    type: Literal["tag"]
    attributes: TagAttributesResponse
    relationships: list[RelationshipResponse]


class GetTagListResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    response: Literal[``"collection"``]

    data: List[:class:`~hondana.types.TagResponse`]

    limit: :class:`int`

    offset: :class:`int`

    total: :class:`int`
    """

    result: Literal["ok", "error"]
    response: Literal["collection"]
    data: list[TagResponse]
    limit: int
    offset: int
    total: int
