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

import datetime
from typing import TYPE_CHECKING

from .enums import ReportCategory, ReportStatus
from .http import HTTPClient


if TYPE_CHECKING:
    from .types.common import LocalisedString
    from .types.report import ReportReasonResponse, UserReportReasonResponse


__all__ = (
    "Report",
    "UserReport",
)


class Report:
    """
    Attributes
    -----------
    id: :class:`str`
        The UUID of this report.
    reason: :class:`str`
        The reason for this report.
    details_required: :class:`bool`
        If details are required for this report.
    category: :class:`~hondana.ReportCategory`
        The category this report falls under.
    version: :class:`int`
        The version revision of this report.
    """

    __slots__ = (
        "_http",
        "_data",
        "_attributes",
        "id",
        "reason",
        "details_required",
        "category",
        "version",
    )

    def __init__(self, http: HTTPClient, payload: ReportReasonResponse) -> None:
        self._http = http
        self._data = payload
        self.id: str = self._data["id"]
        self._attributes = self._data["attributes"]
        self.reason: LocalisedString = self._attributes["reason"]
        self.details_required: bool = self._attributes["detailsRequired"]
        self.category: ReportCategory = ReportCategory(self._attributes["category"])
        self.version: int = self._attributes["version"]

    def __repr__(self) -> str:
        return f"<Report id='{self.id}'>"

    def __str__(self) -> str:
        return f"Report for {str(self.category).title()} and reason: {self.reason}"

    def __eq__(self, other: Report) -> bool:
        return isinstance(other, Report) and self.id == other.id

    def __ne__(self, other: Report) -> bool:
        return not self.__eq__(other)


class UserReport:
    """
    A user generated report on MangaDex.

    Attributes
    -----------
    id: :class:`str`
        This report's ID.
    details: :class:`str`
        The report's details
    object_id: :class:`str`
        The target object's ID.
    status: :class:`~hondana.ReportStatus`
        The current status of the report.
    """

    __slots__ = (
        "_http",
        "_data",
        "_attributes",
        "id",
        "details",
        "object_id",
        "status",
        "_created_at",
    )

    def __init__(self, http: HTTPClient, payload: UserReportReasonResponse) -> None:
        self._http: HTTPClient = http
        self._data: UserReportReasonResponse = payload
        self.id: str = self._data["id"]
        self._attributes = self._data["attributes"]
        self.details: str = self._attributes["details"]
        self.object_id: str = self._attributes["objectId"]
        self.status: ReportStatus = ReportStatus(self._attributes["status"])
        self._created_at: str = self._attributes["createdAt"]

    def __repr__(self) -> str:
        return f"<UserReport id='{self.id}' status={self.status.value}>"

    def __eq__(self, other: UserReport) -> bool:
        return isinstance(other, self.__class__) and self.id == other.id

    @property
    def created_at(self) -> datetime.datetime:
        """Returns the date this report was created in UTC.

        Returns
        --------
        :class:`datetime.datetime`
            The date this report was created.
        """
        return datetime.datetime.fromisoformat(self._created_at)
