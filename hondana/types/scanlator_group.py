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
    "ScanlationGroupAttributesResponse",
    "ScanlationGroupResponse",
    "GetSingleScanlationGroupResponse",
    "GetMultiScanlationGroupResponse",
)


class ScanlationGroupAttributesResponse(TypedDict):
    """
    name: :class:`str`

    altNames: List[:class:`str`]

    website: Optional[:class:`str`]

    ircServer: Optional[:class:`str`]

    ircChannel: Optional[:class:`str`]

    discord: Optional[:class:`str`]

    contactEmail: Optional[:class:`str`]

    description: Optional[:class:`str`]

    twitter: Optional[:class:`str`]

    focusedLanguage: Optional[List[:class:`str`]]

    locked: :class:`bool`

    official: :class:`bool`

    verified: :class:`bool`

    version: :class:`int`

    createdAt: :class:`str`

    updatedAt: :class:`str`
    """

    name: str
    altNames: list[str]
    website: Optional[str]
    ircServer: Optional[str]
    ircChannel: Optional[str]
    discord: Optional[str]
    contactEmail: Optional[str]
    description: Optional[str]
    twitter: Optional[str]
    focusedLanguage: Optional[list[str]]
    locked: bool
    official: bool
    verified: bool
    version: int
    createdAt: str
    updatedAt: str


class ScanlationGroupResponse(TypedDict):
    """
    id: :class:`str`

    type: Literal[``"scanlation_group"``]

    attributes: :class:`~hondana.types.ScanlationGroupAttributesResponse`

    relationships: List[:class:`~hondana.types.RelationshipResponse`]
        This key can contain minimal or full data depending on the ``includes[]`` parameter of its request.
        See here for more info: https://api.mangadex.org/docs.html#section/Reference-Expansion
    """

    id: str
    type: Literal["scanlation_group"]
    attributes: ScanlationGroupAttributesResponse
    relationships: list[RelationshipResponse]


class GetSingleScanlationGroupResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    response: Literal[``"entity"``]

    data: :class:`~hondana.types.ScanlationGroupResponse`
    """

    result: Literal["ok", "error"]
    response: Literal["collection"]
    data: ScanlationGroupResponse


class GetMultiScanlationGroupResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    response: Literal[``"collection"``]

    data: List[:class:`~hondana.types.ScanlationGroupResponse`]
    """

    result: Literal["ok", "error"]
    response: Literal["collection"]
    data: list[ScanlationGroupResponse]
