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

import logging
from typing import TYPE_CHECKING, Literal, Optional

from .relationship import Relationship
from .utils import MANGA_TAGS, cached_slot_property


if TYPE_CHECKING:
    from .types.common import LocalizedString
    from .types.relationship import RelationshipResponse
    from .types.tags import TagResponse


__all__ = (
    "Tag",
    "QueryTags",
)

logger: logging.Logger = logging.getLogger("hondana")


class Tag:
    """A class representing a single Tag from MangaDex.

    Attributes
    -----------
    id: :class:`str`
        The UUID associated with this tag.
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

    __slots__ = (
        "_data",
        "_attributes",
        "_relationships",
        "_name",
        "_description",
        "id",
        "group",
        "version",
        "_cs_relationships",
    )

    def __init__(self, payload: TagResponse) -> None:
        self._data = payload
        self._attributes = payload["attributes"]
        self._relationships: list[RelationshipResponse] = self._data.pop(  # type: ignore # can't pop from a TypedDict
            "relationships", []  # type: ignore # can't pop from a TypedDict
        )  # TODO: remove this when they have relationships to be in line.
        self._name = self._attributes["name"]
        self.id: str = payload["id"]
        self._description: LocalizedString = self._attributes["description"]
        self.group: str = self._attributes["group"]
        self.version: int = self._attributes["version"]

    def __repr__(self) -> str:
        return f"<Tag id={self.id!r} name={self.name!r}>"

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: Tag) -> bool:
        return isinstance(other, Tag) and self.id == other.id

    def __ne__(self, other: Tag) -> bool:
        return not self.__eq__(other)

    @property
    def name(self) -> str:
        """The name of the tag.

        Returns
        --------
        :class:`str`
        """
        name = self._name.get("en")
        if name is None:
            key = next(iter(self._name))
            return self._name[key]
        return name

    @property
    def description(self) -> str | None:
        """The description of the tag, if any.

        Returns
        --------
        Optional[:class:`str`]
        """
        if not self._description:
            return None

        description = self._description.get("en")
        if description is None:
            key = next(iter(self._description))
            return self._description[key]
        return description

    @property
    def url(self) -> str:
        """The URL to this tag.
        Allows browsing all manga attributed to this tag

        Returns
        --------
        :class:`str`
            The URL of the tag.
        """
        return f"https://mangadex.org/tag/{self.id}"

    @cached_slot_property("_cs_relationships")
    def relationships(self) -> list[Relationship]:
        """The relationships of this Tag.

        Returns
        --------
        List[:class:`~hondana.Relationship`]
            The list of relationships this tag has.
        """
        return [Relationship(item) for item in self._relationships]


class QueryTags:
    """Utility class for creating a Tag based query.

    Attributes
    -----------
    tags: List[:class:`str`]
        The tag names you are going to query.
    mode: Literal[``"AND"``, ``"OR"``]
        The logical operation for the tags.

    Raises
    -------
    :exc:`TypeError`
        The mode specified for the builder is not one of "AND" or "OR"
    :exc:`ValueError`
        The tags passed did not align with MangaDex tags.


    .. note::
        The tags passed need to match the *local* cache of the tags.
        If you feel this is out of date, you can try the helper method :meth:`~hondana.Client.update_tags`
    """

    def __init__(self, *tags: str, mode: Literal["AND", "OR"] = "AND"):
        self._tags = tags
        self.tags: Optional[list[str]] = None
        self.mode: str = mode.upper()
        if self.mode not in {"AND", "OR"}:
            raise TypeError("Tags mode has to be 'AND' or 'OR'.")
        self._set_tags()

    def __repr__(self) -> str:
        return f"<Tags mode={self.mode} number_of_tags={len(self._tags)}>"

    def _set_tags(self) -> list[str]:
        tags = []
        for tag in self._tags:
            if tag_ := MANGA_TAGS.get(tag.title()):
                tags.append(tag_)
            else:
                logger.warning("Tag '%s' cannot be found in the local tag cache, skipping.", tag)

        if not tags:
            raise ValueError("No tags passed matched any valid MangaDex tags.")

        self.tags = tags
        return self.tags
