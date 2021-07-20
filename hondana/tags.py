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
from typing import Literal, Optional

from .types.common import LocalisedString
from .types.tags import TagResponse
from .utils import TAGS


__all__ = ("Tag", "QueryTags")


class Tag:
    """A class representing a single Tag from MangaDex.

    Attributes
    -----------
    id: :class:`str`
        The UUID associated with this tag.
    type: Literal[:class:`str`]
        The type of the object, literally "tag".
    description: List[:class:`~hondana.types.LocalisedString`]
        The description(s) of the tag.
    group: :class:`str`
        The group (or kind) of tag.
        e.g. if it is a genre specification, or theme.
    version: :class:`int`
        Version revision of this tag.


    .. note::
        The tag descriptions are currently empty, but seemingly they will be localised descriptions of each one.
        i.e. ``[{"en": "some tag description"}]``

    .. note::
        All tag names currently only have the ``"en"`` key attributed to their localization, so we return this by default.
    """

    __slots__ = ("_data", "_name", "id", "type", "description", "group", "version")

    def __init__(self, payload: TagResponse) -> None:
        self._data = payload
        attributes = payload["attributes"]
        self._name = attributes["name"]
        self.id: str = payload["id"]
        self.type: Literal["tag"] = "tag"
        self.description: list[LocalisedString] = attributes["description"]
        self.group: str = attributes["group"]
        self.version: int = attributes["version"]

    def __repr__(self) -> str:
        return f"<Tag id='{self.id}' name='{self.name}'>"

    def __str__(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        return self._name.get("en", next(iter(self._name)))


class QueryTags:
    """Utility class for creating a Tag based query.

    Attributes
    -----------
    tags: :class:`str`
        The tag names you are going to query.
    mode: :class:`str`
        The logical operation for the tags.
        i.e. ``"AND"`` or ``"OR"``

    Raises
    -------
    TypeError
        The mode specified for the builder is not one of "and" or "or"

    ValueError
        The tags passed did not align with MangaDex tags.


    .. note::
        The tags passed need to match the *local* cache of the tags.
        If you feel this is out of date, you can try the helper method :meth:`~hondana.Client.update_tags`
    """

    def __init__(self, *tags: str, mode: str = "AND"):
        self._tags = list(tags)
        self.tags: Optional[list[str]] = None
        self.mode: str = mode.upper()
        if self.mode not in {"AND", "OR"}:
            raise TypeError("Tags mode has to be 'AND' or 'OR'.")
        self.set_tags()

    def __repr__(self) -> str:
        return f"<Tags mode={self.mode}>"

    def set_tags(self) -> list[str]:
        tags = []
        for tag in self._tags:
            tags.append(TAGS.get(tag.title()))

        if not tags:
            raise ValueError("No tags passed matched any valid MangaDex tags.")

        self.tags = tags
        return self.tags
