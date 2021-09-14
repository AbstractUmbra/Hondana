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
    "ChapterIncludes",
    "ChapterOrderQuery",
    "ChapterAttributesResponse",
    "ChapterResponse",
    "GetSingleChapterResponse",
    "GetMultiChapterResponse",
)


ChapterIncludes = Literal["manga", "user", "scanlation_group"]


class ChapterOrderQuery(TypedDict, total=False):
    createdAt: Literal["asc", "desc"]
    updatedAt: Literal["asc", "desc"]
    publishAt: Literal["asc", "desc"]
    volume: Literal["asc", "desc"]
    chapter: Literal["asc", "desc"]


class _ChapterAttributesOptionalResponse(TypedDict, total=False):
    uploader: Optional[str]


class ChapterAttributesResponse(_ChapterAttributesOptionalResponse):
    """
    title: Optional[:class:`str`]

    volume: :class:`str`

    chapter: :class:`str`

    translatedLanguage: :class:`str`

    hash: :class:`str`

    data: List[:class:`str`]

    dataSaver: List[:class:`str`]

    version: :class:`int`

    createdAt: :class:`str`

    updatedAt: :class:`str`

    publishAt: :class:`str`

    uploader: :class:`str`
        This key is optional.
    """

    title: Optional[str]
    volume: str
    chapter: str
    translatedLanguage: str
    hash: str
    data: list[str]
    dataSaver: list[str]
    version: int
    createdAt: str
    updatedAt: str
    publishAt: str


class ChapterResponse(TypedDict):
    """
    id: :class:`str`

    type: Literal[``"chapter"``]

    attributes: :class:`~hondana.types.ChapterAttributesResponse`

    relationships: List[:class:`RelationshipResponse`]
        This key can contain minimal or full data depending on the ``includes[]`` parameter of it's request.
        See here for more info: https://api.mangadex.org/docs.html#section/Reference-Expansion
    """

    id: str
    type: Literal["chapter"]
    attributes: ChapterAttributesResponse
    relationships: list[RelationshipResponse]


class GetSingleChapterResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    response: Literal[``"entity"``]

    data: :class:`~hondana.types.ChapterResponse`
    """

    result: Literal["ok", "error"]
    response: Literal["entity"]
    data: ChapterResponse


class GetMultiChapterResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    response: Literal[``"collection"``]

    data: List[:class:`~hondana.types.ChapterResponse`]
    """

    result: Literal["ok", "error"]
    response: Literal["collection"]
    data: list[ChapterResponse]
