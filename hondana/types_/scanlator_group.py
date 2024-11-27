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

    from .relationship import RelationshipResponse


__all__ = (
    "GetMultiScanlationGroupResponse",
    "GetSingleScanlationGroupResponse",
    "ScanlationGroupAttributesResponse",
    "ScanlationGroupResponse",
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

    mangaUpdates: Optional[:class:`str`]

    focusedLanguage: Optional[List[:class:`str`]]

    locked: :class:`bool`

    official: :class:`bool`

    verified: :class:`bool`

    inactive: :class:`bool`

    exLicensed: :class:`bool`
        This key may not be present.

    publishDelay: :class:`str`

    version: :class:`int`

    createdAt: :class:`str`

    updatedAt: :class:`str`
    """

    name: str
    altNames: list[str]
    website: str | None
    ircServer: str | None
    ircChannel: str | None
    discord: str | None
    contactEmail: str | None
    description: str | None
    twitter: str | None
    mangaUpdates: str | None
    focusedLanguage: list[str] | None
    locked: bool
    official: bool
    verified: bool
    inactive: bool
    exLicensed: NotRequired[bool]
    publishDelay: str
    version: int
    createdAt: str
    updatedAt: str


class ScanlationGroupResponse(TypedDict):
    """
    id: :class:`str`

    type: Literal[``"scanlation_group"``]

    attributes: :class:`~hondana.types_.scanlator_group.ScanlationGroupAttributesResponse`

    relationships: List[:class:`~hondana.types_.relationship.RelationshipResponse`]
        This key is optional, in the event this payload is gotten from the "relationships" of another object.

        This key can contain minimal or full data depending on the ``includes[]`` parameter of its request.
        See here for more info: https://api.mangadex.org/docs.html#section/Reference-Expansion
    """

    id: str
    type: Literal["scanlation_group"]
    attributes: ScanlationGroupAttributesResponse
    relationships: NotRequired[list[RelationshipResponse]]


class GetSingleScanlationGroupResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    response: Literal[``"entity"``]

    data: :class:`~hondana.types_.scanlator_group.ScanlationGroupResponse`
    """

    result: Literal["ok", "error"]
    response: Literal["collection"]
    data: ScanlationGroupResponse


class GetMultiScanlationGroupResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    response: Literal[``"collection"``]

    data: List[:class:`~hondana.types_.scanlator_group.ScanlationGroupResponse`]

    limit: :class:`int`

    offset: :class:`int`

    total: :class:`int`
    """

    result: Literal["ok", "error"]
    response: Literal["collection"]
    data: list[ScanlationGroupResponse]
    limit: int
    offset: int
    total: int
