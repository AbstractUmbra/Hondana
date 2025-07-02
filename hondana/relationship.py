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

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Mapping

    from .types_.relationship import RelationshipResponse


__all__ = ("Relationship",)


class Relationship:
    """
    An open container type representing an arbitrary relationship within MangaDex.

    .. note::
        Relationships are similar to full objects, except they store no relationships of their own.
        Each "object" retrieved here will be a partial variant.

    Attributes
    ----------
    id: :class:`str`
        The ID relating to this relationship.
    type: :class:`str`
        The type of relationship.
    attributes: Mapping[:class:`str`, Any]
        The attributes of this relationship.
    """

    __slots__ = (
        "_data",
        "attributes",
        "id",
        "type",
    )

    def __init__(self, payload: RelationshipResponse) -> None:
        self._data: RelationshipResponse = payload
        self.id: str = self._data["id"]
        self.type: str = self._data["type"]
        self.attributes: Mapping[str, Any] = self._data.pop("attributes", {})  # pyright: ignore[reportAttributeAccessIssue,reportCallIssue,reportArgumentType] # can't pop from a TypedDict

    def __repr__(self) -> str:
        return f"<Relationship id={self.id!r} type={self.type!r}>"
