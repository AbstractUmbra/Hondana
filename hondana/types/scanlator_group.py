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
from .user import GetUserResponse


__all__ = (
    "ScanlatorGroupIncludes",
    "ScanlationGroupAttributesResponse",
    "ScanlationGroupResponse",
    "GetScanlationGroupResponse",
    "GetScanlationGroupListResponse",
)

ScanlatorGroupIncludes = Literal["user"]


class ScanlationGroupAttributesResponse(TypedDict):
    """
    name: :class:`str`

    leader: Optional[:class:`~hondana.types.GetUserResponse`]

    members: Optional[List[:class:`~hondana.types.GetUserResponse`]]

    website: Optional[:class:`str`]

    ircServer: Optional[:class:`str`]

    ircChannel: Optional[:class:`str`]

    discord: Optional[:class:`str`]

    contactEmail: Optional[:class:`str`]

    description: Optional[:class:`str`]

    locked: :class:`bool`

    official: :class:`bool`

    version: :class:`int`

    createdAt: :class:`str`

    updatedAt: :class:`str`
    """

    name: str
    leader: Optional[GetUserResponse]  # thanks api
    members: Optional[list[GetUserResponse]]  # thanks api
    website: Optional[str]
    ircServer: Optional[str]
    ircChannel: Optional[str]
    discord: Optional[str]
    contactEmail: Optional[str]
    description: Optional[str]
    locked: bool
    official: bool
    version: int
    createdAt: str
    updatedAt: str


class ScanlationGroupResponse(TypedDict):
    """
    id: :class:`str`

    type: Literal[``"scanlation_group"``]

    attributes: :class:`~hondana.types.ScanlationGroupAttributesResponse`
    """

    id: str
    type: Literal["scanlation_group"]
    attributes: ScanlationGroupAttributesResponse
    relationships: list[RelationshipResponse]


class GetScanlationGroupResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    data: :class:`~hondana.types.ScanlationGroupResponse`

    relationships: List[:class:`~hondana.types.RelationshipResponse`]
    """

    result: Literal["ok", "error"]
    data: ScanlationGroupResponse


class GetScanlationGroupListResponse(TypedDict):
    """
    results: List[:class:`GetScanlationGroupResponse`]

    limit: :class:`int`

    offset: :class:`int`

    total: :class:`int`
    """

    results: list[GetScanlationGroupResponse]
    limit: int
    offset: int
    total: int
