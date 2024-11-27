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
    from hondana.enums import ReportStatus

    from .common import LocalizedString
    from .relationship import RelationshipResponse


__all__ = (
    "GetReportReasonAttributesResponse",
    "GetReportReasonResponse",
    "ReportReasonResponse",
)


_ReportCategory = Literal["manga", "chapter", "scanlation_group", "user", "author"]


class GetReportReasonAttributesResponse(TypedDict):
    """
    reason: :class:`~hondana.types_.common.LocalizedString`

    detailsRequired: :class:`bool`

    category: :class:`~hondana.ReportCategory`

    version: :class:`int`
    """

    reason: LocalizedString
    detailsRequired: bool
    category: _ReportCategory
    version: int


class GetUserReportReasonAttributesResponse(TypedDict):
    """
    details: :class:`str`

    objectId: :class:`str`

    status: :class:`~hondana.ReportStatus`

    createdAt: :class:`str`
    """

    details: str
    objectId: str
    status: ReportStatus
    createdAt: str


class ReportReasonResponse(TypedDict):
    """
    id: :class:`str`

    type: Literal[``"report_reason"``]

    attributes: :class:`~hondana.types_.report.GetReportReasonAttributesResponse`
    """

    id: str
    type: Literal["report_reason"]
    attributes: GetReportReasonAttributesResponse


class UserReportReasonResponse(TypedDict):
    """
    id: :class:`str`

    type: Literal[``"report"``]

    attributes: :class:`~hondana.types_.report.GetUserReportReasonAttributesResponse`

    relationships: List[:class:`~hondana.types_.relationship.RelationshipResponse`]
        This key is Optional.
    """

    id: str
    type: Literal["report"]
    attributes: GetUserReportReasonAttributesResponse
    relationships: list[RelationshipResponse]


class GetReportReasonResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    response: Literal[``"collection"``]

    data: List[:class:`~hondana.types_.report.ReportReasonResponse`]

    limit: :class:`int`

    offset: :class:`int`

    total: :class:`int`
    """

    result: Literal["ok", "error"]
    response: Literal["collection"]
    data: list[ReportReasonResponse]
    limit: int
    offset: int
    total: int


class GetUserReportReasonResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    response: Literal[``"collection"``]

    data: List[:class:`~hondana.types_.user.UserReportReasonResponse`]

    limit: :class:`int`

    offset: :class:`int`

    total: :class:`int`
    """

    result: Literal["ok", "error"]
    response: Literal["collection"]
    data: list[UserReportReasonResponse]
    limit: int
    offset: int
    total: int
