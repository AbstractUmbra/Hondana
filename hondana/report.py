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

from typing import TYPE_CHECKING

from .http import HTTPClient


if TYPE_CHECKING:
    from .types.common import LocalisedString
    from .types.report import GetReportReasonResponse, ReportCategory


__all__ = ("Report",)


class Report:
    __slots__ = (
        "_http",
        "_attributes",
        "id",
        "reason",
        "details_required",
        "category",
        "version",
    )

    def __init__(self, http: HTTPClient, payload: GetReportReasonResponse) -> None:
        self._http = http
        self.id: str = payload["id"]
        self._attributes = payload["attributes"]
        self.reason: LocalisedString = self._attributes["reason"]
        self.details_required: bool = self._attributes["detailsRequired"]
        self.category: ReportCategory = self._attributes["category"]
        self.version: int = self._attributes["version"]

    def __repr__(self) -> str:
        return f"<Report id='{self.id}'>"

    def __str__(self) -> str:
        return f"Report for {self.category.title()} and reason: {self.reason}"
