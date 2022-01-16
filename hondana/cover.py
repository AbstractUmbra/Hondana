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
from typing import TYPE_CHECKING, Literal, Optional

from .utils import MISSING, require_authentication


if TYPE_CHECKING:
    from .http import HTTPClient
    from .types.cover import CoverResponse


__all__ = ("Cover",)


class Cover:
    """A class representing a Cover returned from the MangaDex API.

    Attributes
    -----------
    id: :class:`str`
        The UUID associated with this cover.
    volume: Optional[:class:`str`]
        The volume attributed to this cover, if any.
    file_name: :class:`str`
        The file name of this cover.
    description: :class:`str`
        The description of this cover.
    version: :class:`int`
        The version revision of this Cover.
    """

    __slots__ = (
        "_http",
        "_data",
        "_attributes",
        "_relationships",
        "id",
        "volume",
        "file_name",
        "description",
        "version",
        "_created_at",
        "_updated_at",
    )

    def __init__(self, http: HTTPClient, payload: CoverResponse) -> None:
        self._http = http
        self._data = payload
        self._attributes = self._data["attributes"]
        self._relationships = self._data.pop("relationships", [])
        self.id: str = self._data["id"]
        self.volume: Optional[str] = self._attributes["volume"]
        self.file_name: str = self._attributes["fileName"]
        self.description: str = self._attributes["description"]
        self.version: int = self._attributes["version"]
        self._created_at = self._attributes["createdAt"]
        self._updated_at = self._attributes["updatedAt"]

    def __repr__(self) -> str:
        return f"<Cover id='{self.id}' filename={self.file_name}>"

    def __str__(self) -> str:
        return self.file_name

    def __eq__(self, other: Cover) -> bool:
        return isinstance(other, Cover) and self.id == other.id

    def __ne__(self, other: Cover) -> bool:
        return not self.__eq__(other)

    @property
    def created_at(self) -> datetime.datetime:
        """When this cover was created.

        Returns
        --------
        :class:`datetime.datetime`
            The UTC datetime of when this cover was created.
        """
        return datetime.datetime.fromisoformat(self._created_at)

    @property
    def updated_at(self) -> datetime.datetime:
        """When this cover was last updated.

        Returns
        --------
        :class:`datetime.datetime`
            The UTC datetime of when this cover was last updated.
        """
        return datetime.datetime.fromisoformat(self._updated_at)

    def url(self, type: Optional[Literal[256, 512]] = None, /) -> Optional[str]:
        """Method to return the Cover url.

        Due to the API structure, this will return ``None`` if the parent manga key is missing from the response relationships.

        Parameters
        -----------
        type: Optional[Literal[``256``, ``512``]]
            Defaults to ``None`` to return original quality.
            Specifies the return image dimensions.

        Returns
        --------
        Optional[:class:`str`]
            The Cover url.
        """
        parent_manga = None
        for item in self._relationships:
            if item["type"] == "manga":
                parent_manga = item
                break

        if parent_manga is None:
            return

        parent_manga_id = parent_manga["id"]

        if type == 256:
            fmt = ".256.jpg"
        elif type == 512:
            fmt = ".512.jpg"
        else:
            fmt = ""

        return f"https://uploads.mangadex.org/covers/{parent_manga_id}/{self.file_name}{fmt}"

    @require_authentication
    async def edit_cover(
        self, *, volume: Optional[str] = MISSING, description: Optional[str] = MISSING, version: int
    ) -> Cover:
        """|coro|

        This method will edit the current cover on the MangaDex API.

        Parameters
        -----------
        volume: :class:`str`
            The volume identifier relating the cover will represent.
        description: Optional[:class:`str`]
            The description of the cover.
        version: :class:`int`
            The version revision of the cover.


        .. warning::
            The ``volume`` key is mandatory. You can pass ``None`` to null it in the API, but it must have a value.

        Raises
        -------
        TypeError
            The volume key was not given a value. This is required.
        :exc:`BadRequest`
            The request body was malformed.
        :exc:`Forbidden`
            The request returned an error due to authentication failure.

        Returns
        --------
        :class:`~hondana.Cover`
            The returned cover after the edit.
        """
        data = await self._http._edit_cover(self.id, volume=volume, description=description, version=version)

        return self.__class__(self._http, data["data"])

    @require_authentication
    async def delete(self) -> None:
        """|coro|

        This method will delete the current cover from the MangaDex API.

        Raises
        -------
        :exc:`BadRequest`
            The request payload was malformed.
        :exc:`Forbidden`
            The request returned an error due to authentication.
        """
        await self._http._delete_cover(self.id)
