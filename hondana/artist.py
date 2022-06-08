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
from typing import TYPE_CHECKING, Optional, Union

from .query import MangaIncludes
from .utils import MISSING, relationship_finder, require_authentication


if TYPE_CHECKING:
    from .author import Author
    from .http import HTTPClient
    from .manga import Manga
    from .types.artist import ArtistResponse
    from .types.common import LanguageCode, LocalizedString
    from .types.manga import MangaResponse
    from .types.relationship import RelationshipResponse


__all__ = ("Artist",)


class Artist:
    """A class representing an Artist returns from the MangaDex API.

    Attributes
    -----------
    id: :class:`str`
        The UUID associated with this artist.
    name: :class:`str`
        The artist's name.
    image_url: Optional[:class:`str`]
        The artist's image url, if any.
    twitter: Optional[:class:`str`]
        The artist's Twitter url, if any.
    pixiv: Optional[:class:`str`]
        The artist's Pixiv url, if any.
    melon_book: Optional[:class:`str`]
        The artist's Melon Book url, if any.
    fan_box: Optional[:class:`str`]
        The artist's Fan Box url, if any.
    booth: Optional[:class:`str`]
        The artist's Booth url, if any.
    nico_video: Optional[:class:`str`]
        The artist's Nico Video url, if any.
    skeb: Optional[:class:`str`]
        The artist's Skeb url, if any.
    fantia: Optional[:class:`str`]
        The artist's Fantia url, if any.
    tumblr: Optional[:class:`str`]
        The artist's Tumblr url, if any.
    youtube: Optional[:class:`str`]
        The artist's Youtube url, if any.
    weibo: Optional[:class:`str`]
        The artist's Weibo url, if any.
    naver: Optional[:class:`str`]
        The artist's Naver url, if any.
    website: Optional[:class:`str`]
        The artist's website url, if any.
    version: :class:`int`
        The version revision of this artist.
    """

    __slots__ = (
        "_http",
        "_data",
        "_attributes",
        "_relationships",
        "id",
        "name",
        "image_url",
        "twitter",
        "pixiv",
        "melon_book",
        "fan_box",
        "booth",
        "nico_video",
        "skeb",
        "fantia",
        "tumblr",
        "youtube",
        "weibo",
        "naver",
        "website",
        "version",
        "_biography",
        "_created_at",
        "_updated_at",
        "_manga_relationships",
        "__manga",
    )

    def __init__(self, http: HTTPClient, payload: ArtistResponse) -> None:
        self._http = http
        self._data = payload
        self._attributes = self._data["attributes"]
        relationships: list[RelationshipResponse] = self._data.pop("relationships", [])
        self.id: str = self._data["id"]
        self.name: str = self._attributes["name"]
        self.image_url: Optional[str] = self._attributes["imageUrl"]
        self.twitter: Optional[str] = self._attributes["twitter"]
        self.pixiv: Optional[str] = self._attributes["pixiv"]
        self.melon_book: Optional[str] = self._attributes["melonBook"]
        self.fan_box: Optional[str] = self._attributes["fanBox"]
        self.booth: Optional[str] = self._attributes["booth"]
        self.nico_video: Optional[str] = self._attributes["nicoVideo"]
        self.skeb: Optional[str] = self._attributes["skeb"]
        self.fantia: Optional[str] = self._attributes["fantia"]
        self.tumblr: Optional[str] = self._attributes["tumblr"]
        self.youtube: Optional[str] = self._attributes["youtube"]
        self.weibo: Optional[str] = self._attributes.get("weibo")
        self.naver: Optional[str] = self._attributes.get("naver")
        self.website: Optional[str] = self._attributes["website"]
        self.version: int = self._attributes["version"]
        self._biography: Optional[LocalizedString] = self._attributes["biography"] or {}
        self._created_at: str = self._attributes["createdAt"]
        self._updated_at: str = self._attributes["updatedAt"]
        self._manga_relationships: list[MangaResponse] = relationship_finder(relationships, "manga", limit=None)
        self.__manga: Optional[list[Manga]] = None

    def __repr__(self) -> str:
        return f"<Artist id={self.id!r} name={self.name!r}>"

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: Union[Author, Artist]) -> bool:
        return self.id == other.id

    @property
    def biography(self) -> Optional[str]:
        """The artist's biography, if present.

        Returns
        -------
        Optional[:class:`str`]
            The artist's biography.
            This property will attempt to get the ``"en"`` key first, and fallback to the first key in the object.
        """
        if not self._biography:
            return

        key = self._biography.get("en", next(iter(self._biography)))
        return self._biography[key]

    def localised_biography(self, language: LanguageCode) -> Optional[str]:
        """The artist's biography in the specified language, if present.

        Parameters
        ----------
        language: :class:`~LanguageCode`
            The language code of the language to return.

        Returns
        -------
        Optional[:class:`str`]
            The artist's biography in the specified language.
        """
        if not self._biography:
            return

        return self._biography.get(language)

    @property
    def created_at(self) -> datetime.datetime:
        """When this artist was created.

        Returns
        --------
        :class:`datetime.datetime`
        """
        return datetime.datetime.fromisoformat(self._created_at)

    @property
    def updated_at(self) -> datetime.datetime:
        """When this artist was last updated.

        Returns
        --------
        :class:`datetime.datetime`
        """
        return datetime.datetime.fromisoformat(self._updated_at)

    @property
    def url(self) -> str:
        """The URL to this artist.

        Returns
        --------
        :class:`str`
            The URL of the artist.
        """
        return f"https://mangadex.org/author/{self.id}"

    @property
    def manga(self) -> Optional[list[Manga]]:
        """Returns a list Manga related to this artist.


        .. note::
            If the Artist was not requested with the ``manga`` includes parameter, this will return None.
            To populate this, consider :meth:`~hondana.Artist.get_manga`


        Returns
        --------
        Optional[List[:class:`~hondana.Manga`]]
        """
        if self.__manga is not None:
            return self.__manga

        if not self._manga_relationships:
            return None

        formatted: list[Manga] = []
        from .manga import Manga

        formatted.extend(Manga(self._http, item) for item in self._manga_relationships if "attributes" in item)

        if not formatted:
            return

        self.__manga = formatted
        return self.__manga

    @manga.setter
    def manga(self, value: list[Manga]) -> None:
        self.__manga = [item for item in value if isinstance(item, Manga)]

    async def get_manga(self) -> Optional[list[Manga]]:
        """|coro|

        This method will return cached manga responses, or attempt to fetch them from the API.
        It also caches the response and populates :attr:`~hondana.Artist.manga`.

        .. warning::
            This method will make N API quests for N amount of manga this artist is attributed to.
            Consider requesting this object with the ``manga[]`` includes/expansion to save on more API requests.

        Returns
        --------
        Optional[List[:class:`~hondana.Manga`]]
        """
        if self.manga is not None:
            return self.manga

        if not self._manga_relationships:
            return

        ids = [r["id"] for r in self._manga_relationships]

        formatted: list[Manga] = []
        from .manga import Manga

        for manga_id in ids:
            data = await self._http._get_manga(manga_id, includes=MangaIncludes())
            formatted.append(Manga(self._http, data["data"]))

        if not formatted:
            return

        self.__manga = formatted
        return self.__manga

    @require_authentication
    async def update_author(
        self,
        /,
        *,
        name: Optional[str] = None,
        biography: Optional[LocalizedString] = None,
        twitter: str = MISSING,
        pixiv: str = MISSING,
        melon_book: str = MISSING,
        fan_box: str = MISSING,
        booth: str = MISSING,
        nico_video: str = MISSING,
        skeb: str = MISSING,
        fantia: str = MISSING,
        tumblr: str = MISSING,
        youtube: str = MISSING,
        website: str = MISSING,
        version: int,
    ) -> Artist:
        """|coro|

        This method will update an artist on the MangaDex API.

        Parameters
        -----------
        name: Optional[:class:`str`]
            The new name to update the artist with.
        biography: Optional[:class:`~hondana.types.common.LocalizedString`]
            The biography of the artist we are creating.
        twitter: Optional[:class:`str`]
            The twitter URL of the artist.
        pixiv: Optional[:class:`str`]
            The pixiv URL of the artist.
        melon_book: Optional[:class:`str`]
            The melon book URL of the artist.
        fan_box: Optional[:class:`str`]
            The fan box URL of the artist.
        booth: Optional[:class:`str`]
            The booth URL of the artist.
        nico_video: Optional[:class:`str`]
            The nico video URL of the artist.
        skeb: Optional[:class:`str`]
            The skeb URL of the artist.
        fantia: Optional[:class:`str`]
            The fantia URL of the artist.
        tumblr: Optional[:class:`str`]
            The tumblr URL of the artist.
        youtube: Optional[:class:`str`]
            The youtube  URL of the artist.
        website: Optional[:class:`str`]
            The website URL of the artist.
        version: :class:`int`
            The version revision of this artist.

        Raises
        -------
        :exc:`BadRequest`
            The request body was malformed.
        :exc:`Forbidden`
            You are not authorized to update this artist.
        :exc:`NotFound`
            The artist UUID given was not found.

        Returns
        --------
        :class:`~hondana.Artist`
            The updated artist from the API.
        """
        data = await self._http._update_artist(
            self.id,
            name=name,
            biography=biography,
            twitter=twitter,
            pixiv=pixiv,
            melon_book=melon_book,
            fan_box=fan_box,
            booth=booth,
            nico_video=nico_video,
            skeb=skeb,
            fantia=fantia,
            tumblr=tumblr,
            youtube=youtube,
            website=website,
            version=version,
        )
        return self.__class__(self._http, data["data"])

    @require_authentication
    async def delete(self) -> None:
        """|coro|

        This method will delete the current author from the MangaDex API.

        Raises
        -------
        :exc:`Forbidden`
            You are not authorized to delete this author.
        :exc:`NotFound`
            The UUID given for the author was not found.
        """
        await self._http._delete_author(self.id)
