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

from .artist import Artist
from .chapter import Chapter
from .cover import Cover
from .tags import Tag
from .utils import MISSING


if TYPE_CHECKING:
    from .author import Author
    from .http import Client
    from .tags import QueryTags
    from .types import manga


__all__ = ("Manga",)


class Manga:
    """A class representing a Manga returned from the MangaDex API.

    Attributes
    -----------
    id: :class:`str`
        The UUID associated to this manga.
    alternative_titles: Dict[:class:`str`, :class:`str`]
        The alternative title mapping for the Manga.
        i.e. ``{"en": "Some Other Title"}``
    locked: :class:`bool`
        If the Manga is considered 'locked' or not in the API.
    links: Dict[:class:`str`, Any]
        The mapping of links the API has attributed to the Manga.
        (see: https://api.mangadex.org/docs.html#section/Static-data/Manga-links-data)
    original_language: :class:`str`
        The language code for the original language of the Manga.
    last_volume: Optional[:class:`str`]
        The last volume attributed to the manga, if any.
    last_chapter: Optional[:class:`str`]
        The last chapter attributed to the manga, if any.
    publication_demographic: Optional[Dict[:class:`str`, Any]]
        The attributed publication demographic(s) for the manga, if any.
    year: Optional[:class:`int`]
        The year the manga was release, if the key exists.
    content_rating: Optional[Dict[:class:`str`, Any]]
        The content rating attributed to the manga, if any.
    version: :class:`int`
        The version revision of this manga.
    """

    __slots__ = (
        "_http",
        "_data",
        "_title",
        "alternate_titles",
        "locked",
        "links",
        "original_language",
        "last_volume",
        "last_chapter",
        "publication_demographic",
        "year",
        "content_rating",
        "_tags",
        "version",
        "_created_at",
        "_updated_at",
        "id",
        "_relationships",
    )

    def __init__(self, http: Client, payload: manga.ViewMangaResponse) -> None:
        self._http = http
        data = payload["data"]
        attributes = data["attributes"]
        self.id = data["id"]
        self._data = data
        self._title = attributes["title"]
        self.alternate_titles = attributes["altTitles"]
        self.locked = attributes.get("isLocked", False)
        self.links = attributes["links"]
        self.original_language = attributes["originalLanguage"]
        self.last_volume = attributes["lastVolume"]
        self.last_chapter = attributes["lastChapter"]
        self.publication_demographic = attributes["publicationDemographic"]
        self.year = attributes["year"]
        self.content_rating = attributes["contentRating"]
        self._tags = attributes["tags"]
        self.version = attributes["version"]
        self._created_at = attributes["createdAt"]
        self._updated_at = attributes["updatedAt"]
        self._relationships = payload["relationships"]

    def __repr__(self) -> str:
        return f"<Manga id={self.id} title='{self.title}'>"

    def __str__(self) -> str:
        return self.title

    @property
    def title(self) -> str:
        """The manga's title."""
        return self._title.get("en", next(iter(self._title)))

    @property
    def tags(self) -> list[Tag]:
        """The tags associated with this manga."""
        return [Tag(tag) for tag in self._tags]

    @property
    def created_at(self) -> datetime.datetime:
        """The date this manga was created."""
        return datetime.datetime.fromisoformat(self._created_at)

    @property
    def updated_at(self) -> datetime.datetime:
        """The date this manga was last updated."""
        return datetime.datetime.fromisoformat(self._updated_at)

    async def get_author(self) -> Optional[Author]:
        """|coro|

        This method will return the author of the manga.

        Returns
        --------
        Optional[:class:`Author`]
            The author of the manga.


        .. note::
            If the parent manga was requested with the "author" `includes[]` query parameter,
            then this method will not make an extra API call to retrieve the Author data.
        """
        author = None
        for item in self._relationships:
            if item["type"] == "author":
                author = item
                break

        if author is None:
            return None

        if "attributes" in author:
            return Author(self._http, author)  # type: ignore #TODO: typing.Protocol or abcs here.

        return await self._http.get_author(author["id"])

    async def get_cover(self) -> Optional[Cover]:
        """|coro|

        This method will return the cover URL of the parent Manga if it exists.

        Returns
        --------
        Optional[:class:`Cover`]
            The Cover associated with this Manga.

        """
        cover_key = None
        for item in self._relationships:
            if item["type"] == "cover_art":
                cover_key = item
                break

        if cover_key is None:
            return None

        return await self._http.get_cover(cover_key["id"])

    def cover_url(self, type: Optional[Literal["256", "512"]] = None) -> Optional[str]:
        """This method will return a direct url to the cover art of the parent Manga.

        If the manga was requested without the ``"cover_art"`` includes[] parameters, then this method will return ``None``.


        .. note::
            For a more stable cover return, try :meth:`Manga.get_cover`
        """
        cover = None
        for item in self._relationships:
            if item["type"] == "cover_art":
                cover = item
                break

        if cover is None:
            return

        if type == "256":
            fmt = ".256.jpg"
        elif type == "512":
            fmt = ".512.jpg"
        else:
            fmt = ""

        attributes = cover.get("attributes", None)
        if attributes is None:
            return None

        return f"https://uploads.mangadex.org/covers/{self.id}/{attributes['fileName']}{fmt}"

    def get_artist(self) -> Optional[Artist]:
        """This method will return the artist of the parent Manga.

        Returns
        --------
        Optional[:class:`Artist`]
            The artist associated with this Manga.


        .. note::
            If the parent manga was **not** requested with the "artist" `includes[]` query parameter
            then this method will return ``None``.
        """

        artist = None
        for item in self._relationships:
            if item["type"] == "artist":
                artist = item
                break

        if artist is None:
            return None

        if "attributes" in artist:
            return Artist(self._http, artist)  # type: ignore #TODO: Investigate typing.Protocol or abcs here.

    async def update(
        self,
        *,
        title: Optional[dict[str, str]] = None,
        alt_titles: Optional[list[dict[str, str]]] = None,
        description: Optional[dict[str, str]] = None,
        authors: Optional[list[str]] = None,
        artists: Optional[list[str]] = None,
        links: Optional[manga.MangaLinks] = None,
        original_language: Optional[str] = None,
        last_volume: str = MISSING,
        last_chapter: str = MISSING,
        publication_demographic: manga.PublicationDemographic = MISSING,
        status: manga.MangaStatus = MISSING,
        year: int = MISSING,
        content_rating: Optional[manga.ContentRating] = None,
        tags: Optional[QueryTags] = None,
        mod_notes: str = MISSING,
        version: int,
    ) -> Manga:
        """|coro|

        This method will update the current Manga within the MangaDex API.

        Parameters
        -----------
        title: Optional[Dict[:class:`str`, :class:`str`]]
            The manga titles in the format of ``language_key: title``
            i.e. ``{"en": "Some Manga Title"}``
        alt_titles: Optional[List[Dict[:class:`str`, :class:`str`]]]
            The alternative titles in the format of ``language_key: title``
            i.e. ``[{"en": "Some Other Title"}, {"fr": "Un Autre Titre"}]``
        description: Optional[Dict[:class:`str`, :class:`str`]]
            The manga description in the format of ``language_key: description``
            i.e. ``{"en": "My amazing manga where x y z happens"}``
        authors: Optional[List[:class:`str`]]
            The list of author UUIDs to credit to this manga.
        artists: Optional[List[:class:`str`]]
            The list of artist UUIDs to credit to this manga.
        links: Optional[Dict[str, Any]]
            The links relevant to the manga.
            See here for more details: https://api.mangadex.org/docs.html#section/Static-data/Manga-links-data
        original_language: Optional[:class:`str`]
            The language key for the original language of the manga.
        last_volume: :class:`str`
            The last volume to attribute to this manga.
        last_chapter: :class:`str`
            The last chapter to attribute to this manga.
        publication_demographic: Literal[``"shounen"``, ``"shoujo"``, ``"josei"``, ``"seinen"``]
            The target publication demographic of this manga.
        status: Literal[``"ongoing"``, ``"completed"``, ``"hiatus"``, ``"cancelled"``]
            The status of the manga.
        year: :class:`int`
            The release year of the manga.
        content_rating: Optional[Literal[``"safe"``, ``"suggestive"``, ``"erotica"``, ``"pornographic"``]]
            The content rating of the manga.
        tags: Optional[:class:`QueryTags`]
            The QueryTags instance for the list of tags to attribute to this manga.
        mod_notes: :class:`str`
            The moderator notes to add to this Manga.
        version: :class:`int`
            The revision version of this manga.


        .. note::
            The ``mod_notes`` parameter requires the logged in user to be a MangaDex moderator.
            Leave this as the default unless you fit this criteria.

        .. note::
            With the ``last_volume``, ``last_chapter``, ``publication_demographic``, ``status``, ``year`` and ``mod_notes`` parameters
            if you leave these values as their default, they will instead be cast to ``None`` (null) in the API.
            Provide values for these unless you want to nullify them.

        Raises
        -------
        BadRequest
            The query parameters were not valid.

        Forbidden
            The update errored due to authentication failure.

        NotFound
            The specified manga does not exist.

        Returns
        --------
        :class:`Manga`
            The manga that was returned after creation.
        """
        data = await self._http._update_manga(
            self.id,
            title=title,
            alt_titles=alt_titles,
            description=description,
            authors=authors,
            artists=artists,
            links=links,
            original_language=original_language,
            last_volume=last_volume,
            last_chapter=last_chapter,
            publication_demographic=publication_demographic,
            status=status,
            year=year,
            content_rating=content_rating,
            tags=tags,
            mod_notes=mod_notes,
            version=version,
        )

        return self.__class__(self._http, data)

    async def delete(self) -> dict[str, Literal["ok", "error"]]:
        """|coro|

        This method will delete a Manga from the MangaDex API.

        Parameters
        -----------
        manga_id: :class:`str`
            The UUID of the manga to delete.

        Raises
        -------
        Forbidden
            The update errored due to authentication failure.
        NotFound
            The specified manga does not exist.

        Returns
        --------
        Dict[str, Literal[``"ok"``, ``"error"``]]:
            The response payload.
        """

        return await self._http._delete_manga(self.id)

    async def unfollow(self) -> dict[str, Literal["ok", "error"]]:
        """|coro|

        This method will unfollow the current Manga for the logged in user in the MangaDex API.

        Parameters
        -----------
        manga_id: :class:`str`
            The UUID of the manga to unfollow.

        Raises
        -------
        Forbidden
            The request errored due to authentication failure.
        NotFound
            The specified manga does not exist.

        Returns
        --------
        Dict[str, Literal[``"ok"``, ``"error"``]]
            The response payload.
        """
        return await self._http._unfollow_manga(self.id)

    async def follow(self) -> dict[str, Literal["ok", "error"]]:
        """|coro|

        This method will follow the current Manga for the logged in user in the MangaDex API.

        Parameters
        -----------
        manga_id: :class:`str`
            The UUID of the manga to unfollow.

        Raises
        -------
        Forbidden
            The request errored due to authentication failure.
        NotFound
            The specified manga does not exist.

        Returns
        --------
        Dict[str, Literal[``"ok"``, ``"error"``]]
            The response payload.
        """
        return await self._http._follow_manga(self.id)

    async def feed(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        created_at_since: Optional[datetime.datetime] = None,
        updated_at_since: Optional[datetime.datetime] = None,
        published_at_since: Optional[datetime.datetime] = None,
        order: Optional[manga.MangaOrderQuery] = None,
        includes: Optional[list[manga.MangaIncludes]] = ["author", "artist", "cover_art"],
    ) -> list[Chapter]:
        """|coro|

        This method returns the current manga's chapter feed.

        Parameters
        -----------
        limit: :class:`int`
            Defaults to 100. The maximum amount of chapters to return in the response.
        offset: :class:`int`
            Defaults to 0. The pagination offset for the request.
        created_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their creation date.
        updated_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their updated at date.
        published_at_since: Optional[:class:`datedate.datetime`]
            A start point to return chapters from based on their published at date.
        order: Optional[Dict[Literal[``"volume"``, ``"chapter"``], Literal[``"asc"``, ``"desc"``]]]
            A query parameter to choose how the responses are ordered.
            i.e. ``{"chapters": "desc"}``
        includes: Optional[List[Literal[``"author"``, ``"artist"``, ``"cover_art"``]]]
            The list of options to include increased payloads for per chapter.
            Defaults to these values.

        Raises
        -------
        BadRequest
            The query parameters were malformed.

        Returns
        --------
        List[:class:`Chapter`]
            The list of chapters returned from this request.
        """
        data = await self._http._manga_feed(
            self.id,
            limit=limit,
            offset=offset,
            created_at_since=created_at_since,
            updated_at_since=updated_at_since,
            published_at_since=published_at_since,
            order=order,
            includes=includes,
        )

        return [Chapter(self._http, item) for item in data["results"]]
