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
    "ChapterAttributesResponse",
    "ChapterReadHistoryResponse",
    "ChapterReadResponse",
    "ChapterResponse",
    "GetAtHomeChapterResponse",
    "GetAtHomeResponse",
    "GetMultiChapterResponse",
    "GetSingleChapterResponse",
)


class ChapterAttributesResponse(TypedDict):
    """
    title: Optional[:class:`str`]

    volume: :class:`str`

    chapter: :class:`str`

    pages: :class:`int`

    translatedLanguage: :class:`str`

    externalUrl: Optional[:class:`str`]

    version: :class:`int`

    createdAt: :class:`str`

    updatedAt: :class:`str`

    publishAt: :class:`str`

    readableAt: :class:`str`

    isUnavailable: :class:`bool`
    """

    title: str | None
    volume: str
    chapter: str
    pages: int
    translatedLanguage: str
    externalUrl: str | None
    isUnavailable: bool
    version: int
    createdAt: str
    updatedAt: str
    publishAt: str
    readableAt: str
    isUnavailable: bool


class ChapterResponse(TypedDict):
    """
    id: :class:`str`

    type: Literal[``"chapter"``]

    attributes: :class:`~hondana.types_.chapter.ChapterAttributesResponse`

    relationships: List[:class:`~hondana.types_.relationship.RelationshipResponse`]
        This key is optional, in the event this payload is gotten from the "relationships" of another object.

        This key can contain minimal or full data depending on the ``includes[]`` parameter of its request.
        See here for more info: https://api.mangadex.org/docs.html#section/Reference-Expansion
    """

    id: str
    type: Literal["chapter"]
    attributes: ChapterAttributesResponse
    relationships: NotRequired[list[RelationshipResponse]]


class GetSingleChapterResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    response: Literal[``"entity"``]

    data: :class:`~hondana.types_.chapter.ChapterResponse`
    """

    result: Literal["ok", "error"]
    response: Literal["entity"]
    data: ChapterResponse


class GetMultiChapterResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    response: Literal[``"collection"``]

    data: List[:class:`~hondana.types_.chapter.ChapterResponse`]

    limit: :class:`int`

    offset: :class:`int`

    total: :class:`int`
    """

    result: Literal["ok", "error"]
    response: Literal["collection"]
    data: list[ChapterResponse]
    limit: int
    offset: int
    total: int


class GetAtHomeResponse(TypedDict):
    """
    result: Literal[``"ok"``]

    baseUrl: :class:`str`

    chapter: :class`~hondana.types_.GetAtHomeChapterResponse`
    """

    result: Literal["ok"]
    baseUrl: str
    chapter: GetAtHomeChapterResponse


class GetAtHomeChapterResponse(TypedDict):
    """
    hash: :class:`str`

    data: List[:class:`str`]

    dataSaver: List[:class:`str`]
    """

    hash: str
    data: list[str]
    dataSaver: list[str]


class ChapterReadResponse(TypedDict):
    """
    chapterId: :class:`str`

    readDate: :class:`str`
    """

    chapterId: str
    readDate: str  # utc timezone


class ChapterReadHistoryResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    response: Literal[``"collection"``]

    data: List[:class:`~hondana.types_.chapter.ChapterReadResponse`]

    limit: :class:`int`

    offset: :class:`int`

    total: :class:`int`
    """

    result: Literal["ok", "error"]
    response: Literal["collection"]
    data: list[ChapterReadResponse]
    limit: int
    offset: int
    total: int
