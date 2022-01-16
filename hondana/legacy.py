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

from typing import TYPE_CHECKING, Literal

from .http import HTTPClient


if TYPE_CHECKING:
    from .types.legacy import LegacyMappingResponse, LegacyMappingType


__all__ = ("LegacyItem",)


class LegacyItem:
    """A generic class representing a legacy ID mapping from the previous MangaDex API to the new.

    Attributes
    -----------
    id: :class:`str`
        The legacy mapping UUID (NOT the new item UUID).
    type: Literal[``"mapping_id"``]
        The raw type from the API.
    obj_new_id: :class:`str`
        The target item's new UUID.
    obj_legacy_id: :class:`int`
        The target item's old API integer ID.
    obj_type: :class:`~hondana.types.LegacyMappingType`
        The type of the legacy item we resolved.
    """

    __slots__ = (
        "_http",
        "_data",
        "id",
        "type",
        "_attributes",
        "obj_new_id",
        "obj_legacy_id",
        "obj_type",
    )

    def __init__(self, http: HTTPClient, payload: LegacyMappingResponse):
        self._http = http
        self._data = payload
        self.id: str = self._data["id"]
        self.type: Literal["mapping_id"] = self._data["type"]
        self._attributes = self._data["attributes"]
        self.obj_new_id: str = self._attributes["newId"]
        self.obj_legacy_id: int = self._attributes["legacyId"]
        self.obj_type: LegacyMappingType = self._attributes["type"]

    def __repr__(self) -> str:
        return f"<CustomList id='{self.id}' type='{self.type}'>"

    def __eq__(self, other: LegacyItem) -> bool:
        return isinstance(other, LegacyItem) and self.id == other.id

    def __ne__(self, other: LegacyItem) -> bool:
        return not self.__eq__(other)
