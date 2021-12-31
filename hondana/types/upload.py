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
    from .errors import ErrorType
    from .relationship import RelationshipResponse


__all__ = (
    "UploadSessionAttributes",
    "GetUploadSessionResponse",
    "ChapterUploadAttributes",
    "ChapterUploadData",
    "BeginChapterUploadResponse",
    "UploadedChapterPageAttributes",
    "UploadedChapterDataResponse",
    "UploadedChapterResponse",
)


class UploadSessionAttributes(TypedDict):
    """
    isCommitted: :class:`bool`

    isProcessed: :class:`bool`

    isDeleted: :class:`bool`

    version: :class:`int`

    createdAt: :class:`str`

    updatedAt: :class:`str`
    """

    isCommitted: bool
    isProcessed: bool
    isDeleted: bool
    version: int
    createdAt: str
    updatedAt: str


class GetUploadSessionResponse(TypedDict):
    """
    id: :class:`str`

    type: Literal[``"upload_session"``]

    attributes: :class:`~hondana.types.UploadSessionAttributes`
    """

    id: str
    type: Literal["upload_session"]
    attributes: UploadSessionAttributes


class ChapterUploadAttributes(TypedDict):
    """
    isCommitted :class:`bool`

    isProcessed: :class:`bool`

    isDeleted: :class:`bool`
    """

    isCommitted: bool
    isProcessed: bool
    isDeleted: bool


class ChapterUploadData(TypedDict):
    """
    id: :class:`str`

    type: Literal[``"upload_session"``]

    attributes: :class:`~hondana.types.ChapterUploadAttributes`

    relationships: List[:class:`~hondana.types.RelationshipResponse`]
    """

    id: str
    type: Literal["upload_session"]
    attributes: ChapterUploadAttributes
    relationships: list[RelationshipResponse]


class BeginChapterUploadResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    data: :class:`~hondana.types.ChapterUploadData`
    """

    result: Literal["ok", "error"]
    data: ChapterUploadData


class UploadedChapterPageAttributes(TypedDict):
    """
    originalFileName: :class:`str`

    fileHash: :class:`str`

    fileSize: :class:`int`

    mimeType: :class:`str`

    version: :class:`int`
    """

    originalFileName: str
    fileHash: str
    fileSize: int
    mimeType: str
    version: int


class UploadedChapterDataResponse(TypedDict):
    """
    id: :class:`str`

    type: Literal[``"upload_session_file"``]

    attributes: :class:`~hondana.types.UploadedChapterPageAttributes`
    """

    id: str
    type: Literal["upload_session_file"]
    attributes: UploadedChapterPageAttributes


class UploadedChapterResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    errors: List[:class:`~hondana.types.ErrorType`]

    data: List[:class:`~hondana.types.UploadedChapterDataResponse`]
    """

    result: Literal["ok", "error"]
    errors: list[ErrorType]
    data: list[UploadedChapterDataResponse]
