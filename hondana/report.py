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

from typing import Literal

from .http import HTTPClient
from .types.common import LocalisedString
from .types.report import GetReportReasonResponse, ReportCategory


__all__ = ("Report",)


class Report:
    __slots__ = ("_http", "id", "type", "_attributes", "reason", "details_required", "category", "version")

    def __init__(self, http: HTTPClient, payload: GetReportReasonResponse) -> None:
        self._http = http
        self.id: str = payload["id"]
        self.type: Literal["report_reason"] = payload["type"]
        attributes = payload["attributes"]
        self._attributes = attributes
        self.reason: LocalisedString = attributes["reason"]
        self.details_required: bool = attributes["detailsRequired"]
        self.category: ReportCategory = attributes["category"]
        self.version: int = attributes["version"]

    def __repr__(self) -> str:
        return f"<Report id='{self.id}'>"

    def __str__(self) -> str:
        return f"Report for {self.category.title()} and reason: {self.reason}"
