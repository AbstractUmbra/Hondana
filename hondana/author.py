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

from .query import MangaIncludes
from .utils import MISSING, AuthorArtistTag, RelationshipResolver, require_authentication

if TYPE_CHECKING:
    from .http import HTTPClient
    from .manga import Manga
    from .types_.author import AuthorAttributesResponse, AuthorResponse
    from .types_.common import LanguageCode, LocalizedString
    from .types_.manga import MangaResponse
    from .types_.relationship import RelationshipResponse

__all__ = ("Author",)


class Author(AuthorArtistTag):
    """A class representing an Author returned from the MangaDex API.

    Attributes
    ----------
    id: :class:`str`
        The UUID associated with this author.
    name: :class:`str`
        The author's name.
    image_url: Optional[:class:`str`]
        The author's image url, if any.
    twitter: Optional[:class:`str`]
        The author's Twitter url, if any.
    pixiv: Optional[:class:`str`]
        The author's Pixiv url, if any.
    melon_book: Optional[:class:`str`]
        The author's Melon Book url, if any.
    fan_box: Optional[:class:`str`]
        The author's Fan Box url, if any.
    booth: Optional[:class:`str`]
        The author's Booth url, if any.
    nico_video: Optional[:class:`str`]
        The author's Nico Video url, if any.
    skeb: Optional[:class:`str`]
        The author's Skeb url, if any.
    fantia: Optional[:class:`str`]
        The author's Fantia url, if any.
    tumblr: Optional[:class:`str`]
        The author's Tumblr url, if any.
    youtube: Optional[:class:`str`]
        The author's Youtube url, if any.
    weibo: Optional[:class:`str`]
        The author's Weibo url, if any.
    naver: Optional[:class:`str`]
        The author's Naver url, if any.
    namicomi: Optional[:class:`str`]
        The author's Namicomi url, if any.
    website: Optional[:class:`str`]
        The author's website url, if any.
    version: :class:`int`
        The version revision of this author.
    """

    __slots__ = (
        "__manga",
        "_attributes",
        "_biography",
        "_created_at",
        "_data",
        "_http",
        "_manga_relationships",
        "_updated_at",
        "booth",
        "fan_box",
        "fantia",
        "id",
        "image_url",
        "melon_book",
        "name",
        "namicomi",
        "naver",
        "nico_video",
        "pixiv",
        "skeb",
        "tumblr",
        "twitter",
        "version",
        "website",
        "weibo",
        "youtube",
    )

    def __init__(self, http: HTTPClient, payload: AuthorResponse) -> None:
        self._http: HTTPClient = http
        self._data: AuthorResponse = payload
        self._attributes: AuthorAttributesResponse = self._data["attributes"]
        relationships: list[RelationshipResponse] = self._data.pop("relationships", [])
        self.id: str = self._data["id"]
        self.name: str = self._attributes["name"]
        self.image_url: str | None = self._attributes["imageUrl"]
        self.twitter: str | None = self._attributes["twitter"]
        self.pixiv: str | None = self._attributes["pixiv"]
        self.melon_book: str | None = self._attributes["melonBook"]
        self.fan_box: str | None = self._attributes["fanBox"]
        self.booth: str | None = self._attributes["booth"]
        self.nico_video: str | None = self._attributes["nicoVideo"]
        self.skeb: str | None = self._attributes["skeb"]
        self.fantia: str | None = self._attributes["fantia"]
        self.tumblr: str | None = self._attributes["tumblr"]
        self.youtube: str | None = self._attributes["youtube"]
        self.weibo: str | None = self._attributes["weibo"]
        self.naver: str | None = self._attributes["naver"]
        self.namicomi: str | None = self._attributes.get("namicomi")
        self.website: str | None = self._attributes["website"]
        self.version: int = self._attributes["version"]
        self._biography: LocalizedString | None = self._attributes["biography"]
        self._created_at: str = self._attributes["createdAt"]
        self._updated_at: str = self._attributes["updatedAt"]
        self._manga_relationships: list[MangaResponse] = RelationshipResolver(relationships, "manga").resolve(
            with_fallback=False,
            remove_empty=True,
        )
        self.__manga: list[Manga] | None = None

    def __repr__(self) -> str:
        return f"<Author id={self.id!r} name={self.name!r}>"

    def __str__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, AuthorArtistTag) and self.id == other.id

    @property
    def biography(self) -> str | None:
        """The author's biography, if present.

        Returns
        -------
        Optional[:class:`str`]
            The author's biography.
            This property will attempt to get the ``"en"`` key first, and fallback to the first key in the object.
        """
        if not self._biography:
            return None

        biography = self._biography.get("en")
        if biography is None:
            key = next(iter(self._biography))
            return self._biography[key]  # pyright: ignore[reportUnknownVariableType] # this is safe since the key is from the dict

        return biography

    def localised_biography(self, language: LanguageCode) -> str | None:
        """The author's biography in the specified language, if present.

        Parameters
        ----------
        language: :class:`~hondana.types_.common.LanguageCode`
            The language code of the language to return.

        Returns
        -------
        Optional[:class:`str`]
            The author's biography in the specified language.
        """
        if not self._biography:
            return None

        return self._biography.get(language)

    @property
    def created_at(self) -> datetime.datetime:
        """When this author was created.

        Returns
        -------
        :class:`datetime.datetime`
        """
        return datetime.datetime.fromisoformat(self._created_at)

    @property
    def updated_at(self) -> datetime.datetime:
        """When this author was last updated.

        Returns
        -------
        :class:`datetime.datetime`
        """
        return datetime.datetime.fromisoformat(self._updated_at)

    @property
    def url(self) -> str:
        """The URL to this author.

        Returns
        -------
        :class:`str`
            The URL of the author.
        """
        return f"https://mangadex.org/author/{self.id}"

    @property
    def manga(self) -> list[Manga] | None:
        """Returns a list Manga related to this author.

        .. note::
            If the Author was not requested with the ``manga`` includes parameter, this will return None.
            To populate this, consider :meth:`~hondana.Author.get_manga`


        Returns
        -------
        Optional[List[:class:`~hondana.Manga`]]
        """
        if self.__manga is not None:
            return self.__manga

        if not self._manga_relationships:
            return None

        from .manga import Manga  # noqa: PLC0415 # cyclic import cheat

        formatted = [Manga(self._http, item) for item in self._manga_relationships]

        self.__manga = formatted
        return self.__manga

    @manga.setter
    def manga(self, value: list[Manga]) -> None:
        self.__manga = value

    async def get_manga(self) -> list[Manga] | None:
        """|coro|

        This method will return cached manga responses, or attempt to fetch them from the API.
        It also caches the response and populates :attr:`~hondana.Author.manga`.

        .. warning::
            This method will make N API quests for N amount of manga this author is attributed to.
            Consider requesting this object with the ``manga[]`` includes/expansion so save on more API requests.

        Returns
        -------
        Optional[List[:class:`~hondana.Manga`]]
        """
        if self.manga is not None:
            return self.manga

        if not self._manga_relationships:
            return None

        ids = [r["id"] for r in self._manga_relationships]

        formatted: list[Manga] = []
        from .manga import Manga  # noqa: PLC0415 # cyclic import cheat

        for manga_id in ids:
            data = await self._http.get_manga(manga_id, includes=MangaIncludes())
            formatted.append(Manga(self._http, data["data"]))

        if not formatted:
            return None

        self.__manga = formatted
        return self.__manga

    @require_authentication
    async def update_author(
        self,
        /,
        *,
        name: str | None = None,
        biography: LocalizedString | None = None,
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
    ) -> Author:
        """|coro|

        This method will update an author on the MangaDex API.

        Parameters
        ----------
        name: Optional[:class:`str`]
            The new name to update the author with.
        biography: Optional[:class:`~hondana.types_.common.LocalizedString`]
            The biography of the author we are creating.
        twitter: Optional[:class:`str`]
            The twitter URL of the author.
        pixiv: Optional[:class:`str`]
            The pixiv URL of the author.
        melon_book: Optional[:class:`str`]
            The melon book URL of the author.
        fan_box: Optional[:class:`str`]
            The fan box URL of the author.
        booth: Optional[:class:`str`]
            The booth URL of the author.
        nico_video: Optional[:class:`str`]
            The nico video URL of the author.
        skeb: Optional[:class:`str`]
            The skeb URL of the author.
        fantia: Optional[:class:`str`]
            The fantia URL of the author.
        tumblr: Optional[:class:`str`]
            The tumblr URL of the author.
        youtube: Optional[:class:`str`]
            The youtube  URL of the author.
        website: Optional[:class:`str`]
            The website URL of the author.
        version: :class:`int`
            The version revision of this author.

        Raises
        ------
        BadRequest
            The request body was malformed.
        Forbidden
            You are not authorized to update this author.
        NotFound
            The author UUID given was not found.

        Returns
        -------
        :class:`~hondana.Author`
            The updated author from the API.
        """  # noqa: DOC502 # raised in method call
        data = await self._http.update_author(
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
    async def delete(self, author_id: str, /) -> None:
        """|coro|

        This method will delete the current author from the MangaDex API.

        Raises
        ------
        Forbidden
            You are not authorized to delete this author.
        NotFound
            The UUID given for the author was not found.
        """  # noqa: DOC502 # raised in method call
        await self._http.delete_author(author_id)
