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
from .cover import Cover
from .tags import Tag
from .utils import MISSING, require_authentication


if TYPE_CHECKING:
    from .author import Author
    from .chapter import Chapter
    from .http import HTTPClient
    from .tags import QueryTags
    from .types import manga
    from .types.common import ContentRating, LanguageCode, LocalisedString
    from .types.relationship import RelationshipResponse


__all__ = ("Manga",)


class Manga:
    """A class representing a Manga returned from the MangaDex API.

    Attributes
    -----------
    id: :class:`str`
        The UUID associated to this manga.
    alternate_titles: :class:`~hondana.types.LocalisedString`
        The alternative title mapping for the Manga.
        i.e. ``{"en": "Some Other Title"}``
    locked: :class:`bool`
        If the Manga is considered 'locked' or not in the API.
    links: :class:`~hondana.types.MangaLinks`
        The mapping of links the API has attributed to the Manga.
        (see: https://api.mangadex.org/docs.html#section/Static-data/Manga-links-data)
    original_language: :class:`str`
        The language code for the original language of the Manga.
    last_volume: Optional[:class:`str`]
        The last volume attributed to the manga, if any.
    last_chapter: Optional[:class:`str`]
        The last chapter attributed to the manga, if any.
    publication_demographic: Optional[:class:`~hondana.types.PublicationDemographic`]
        The attributed publication demographic(s) for the manga, if any.
    year: Optional[:class:`int`]
        The year the manga was release, if the key exists.
    content_rating: Optional[:class:`~hondana.types.ContentRating`]
        The content rating attributed to the manga, if any.
    version: :class:`int`
        The version revision of this manga.
    """

    __slots__ = (
        "_http",
        "_data",
        "_attributes",
        "_relationships",
        "_title",
        "_description",
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
    )

    def __init__(self, http: HTTPClient, payload: manga.MangaResponse) -> None:
        self._http = http
        self._data = payload
        self._attributes = payload["attributes"]
        self.id: str = payload["id"]
        self._title = self._attributes["title"]
        self._description = self._attributes["description"]
        self.alternate_titles: list[LocalisedString] = self._attributes["altTitles"]
        self.locked: bool = self._attributes.get("isLocked", False)
        self.links: manga.MangaLinks = self._attributes["links"]
        self.original_language: str = self._attributes["originalLanguage"]
        self.last_volume: Optional[str] = self._attributes["lastVolume"]
        self.last_chapter: Optional[str] = self._attributes["lastChapter"]
        self.publication_demographic: Optional[manga.PublicationDemographic] = self._attributes["publicationDemographic"]
        self.year: Optional[int] = self._attributes["year"]
        self.content_rating: Optional[manga.ContentRating] = self._attributes["contentRating"]
        self.version: int = self._attributes["version"]
        self._tags = self._attributes["tags"]
        self._created_at = self._attributes["createdAt"]
        self._updated_at = self._attributes["updatedAt"]
        self._relationships: list[RelationshipResponse] = payload.get("relationships", [])

    def __repr__(self) -> str:
        return f"<Manga id={self.id} title='{self.title}'>"

    def __str__(self) -> str:
        return self.title

    @property
    def url(self) -> str:
        """The URL to this manga."""
        return f"https://mangadex.org/title/{self.id}"

    @property
    def title(self) -> str:
        """The manga's title."""
        return self._title.get("en", next(iter(self._title)))

    @property
    def description(self) -> str:
        """The manga's description/synopsis."""
        return self._description.get("en", next(iter(self._description)))

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
        for relationship in self._relationships:
            if relationship["type"] == "author":
                author = relationship
                break

        if author is None:
            return None

        if "attributes" in author:
            return Author(self._http, author)

        data = await self._http._get_author(author["id"], includes=[])
        return Author(self._http, data["data"])

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

        data = await self._http._get_cover(cover_key["id"], ["manga"])
        return Cover(self._http, data)

    def cover_url(self, /, type: Optional[Literal[256, 512]] = None) -> Optional[str]:
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

        if type == 256:
            fmt = ".256.jpg"
        elif type == 512:
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
            return Artist(self._http, artist)

    @require_authentication
    async def update(
        self,
        *,
        title: Optional[LocalisedString] = None,
        alt_titles: Optional[list[LocalisedString]] = None,
        description: Optional[LocalisedString] = None,
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
        title: Optional[:class:`~hondana.types.LocalisedString`]
            The manga titles in the format of ``language_key: title``
            i.e. ``{"en": "Some Manga Title"}``
        alt_titles: Optional[List[:class:`~hondana.types.LocalisedString`]]
            The alternative titles in the format of ``language_key: title``
            i.e. ``[{"en": "Some Other Title"}, {"fr": "Un Autre Titre"}]``
        description: Optional[:class:`~hondana.types.LocalisedString`]
            The manga description in the format of ``language_key: description``
            i.e. ``{"en": "My amazing manga where x y z happens"}``
        authors: Optional[List[:class:`str`]]
            The list of author UUIDs to credit to this manga.
        artists: Optional[List[:class:`str`]]
            The list of artist UUIDs to credit to this manga.
        links: Optional[:class:`~hondana.types.MangaLinks`]
            The links relevant to the manga.
            See here for more details: https://api.mangadex.org/docs.html#section/Static-data/Manga-links-data
        original_language: Optional[:class:`str`]
            The language key for the original language of the manga.
        last_volume: :class:`str`
            The last volume to attribute to this manga.
        last_chapter: :class:`str`
            The last chapter to attribute to this manga.
        publication_demographic: :class:`hondana.types.PublicationDemographic`
            The target publication demographic of this manga.
        status: :class:`~hondana.types.MangaStatus`
            The status of the manga.
        year: :class:`int`
            The release year of the manga.
        content_rating: Optional[:class:`~hondana.types.ContentRating`]
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
            The update returned an error due to authentication failure.

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

        return self.__class__(self._http, data["data"])

    @require_authentication
    async def delete(self) -> None:
        """|coro|

        This method will delete a Manga from the MangaDex API.

        Raises
        -------
        Forbidden
            The update returned an error due to authentication failure.
        NotFound
            The specified manga does not exist.
        """

        await self._http._delete_manga(self.id)

    @require_authentication
    async def unfollow(self) -> None:
        """|coro|

        This method will unfollow the current Manga for the logged in user in the MangaDex API.

        Raises
        -------
        Forbidden
            The request returned an error due to authentication failure.
        NotFound
            The specified manga does not exist.
        """
        await self._http._unfollow_manga(self.id)

    @require_authentication
    async def follow(self) -> None:
        """|coro|

        This method will follow the current Manga for the logged in user in the MangaDex API.

        Raises
        -------
        Forbidden
            The request returned an error due to authentication failure.
        NotFound
            The specified manga does not exist.
        """
        await self._http._follow_manga(self.id)

    async def feed(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        translated_languages: Optional[list[LanguageCode]] = None,
        original_language: Optional[list[LanguageCode]] = None,
        excluded_original_language: Optional[list[LanguageCode]] = None,
        content_rating: Optional[list[ContentRating]] = None,
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
        translated_languages: List[:class:`str`]
            A list of language codes to filter the returned chapters with.
        content_rating: Optional[List[:class:`~hondana.types.ContentRating`]]
            The content rating to filter the feed by.
        created_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their creation date.
        updated_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their updated at date.
        published_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their published at date.
        order: Optional[:class:`~hondana.types.MangaOrderQuery`]
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
            translated_languages=translated_languages,
            original_language=original_language,
            excluded_original_language=excluded_original_language,
            content_rating=content_rating,
            created_at_since=created_at_since,
            updated_at_since=updated_at_since,
            published_at_since=published_at_since,
            order=order,
            includes=includes,
        )

        return [Chapter(self._http, item) for item in data["results"]]

    @require_authentication
    async def manga_read_markers(self) -> manga.MangaReadMarkersResponse:
        """|coro|

        This method will return the read chapters of the current manga.

        Returns
        --------
        Union[Dict[Literal[``"ok"``], List[:class:`str`]]]
            The raw payload of the API.
            Contains a list of read chapter UUIDs.
        """
        return await self._http._manga_read_markers([self.id], grouped=False)

    @require_authentication
    async def get_reading_status(self) -> manga.MangaReadingStatusResponse:
        """|coro|

        This method will return the current reading status for the current manga.

        Raises
        -------
        Forbidden
            You are not authenticated to perform this action.
        NotFound
            The specified manga does not exist, likely due to an incorrect ID.

        Returns
        --------
        :class:`~hondana.types.MangaReadingStatusResponse`
            The raw payload from the API response.
        """
        return await self._http._get_manga_reading_status(self.id)

    @require_authentication
    async def update_reading_status(self, *, status: Optional[manga.ReadingStatus]) -> None:
        """|coro|

        This method will update your current reading status for the current manga.

        Parameters
        -----------
        status: Optional[:class:`~hondana.types.ReadingStatus`]
            The reading status you wish to update this manga with.


        .. note::
            Leaving ``status`` as the default will remove the manga reading status from the API.
            Please provide a value if you do not wish for this to happen.

        Raises
        -------
        BadRequest
            The query parameters were invalid.
        NotFound
            The specified manga cannot be found, likely due to incorrect ID.
        """

        await self._http._update_manga_reading_status(self.id, status=status)

    @require_authentication
    async def add_to_custom_list(self, *, custom_list_id: str) -> None:
        """|coro|

        This method will add the current manga to the specified custom list.

        Parameters
        -----------
        custom_list_id: :class:`str`
            The UUID associated with the custom list you wish to add the manga to.

        Raises
        -------
        Forbidden
            You are not authorised to add manga to this custom list.
        NotFound
            The specified manga or specified custom list are not found, likely due to an incorrect UUID.
        """

        await self._http._add_manga_to_custom_list(manga_id=self.id, custom_list_id=custom_list_id)

    @require_authentication
    async def remove_from_custom_list(self, *, custom_list_id: str) -> None:
        """|coro|

        This method will remove the current manga from the specified custom list.

        Parameters
        -----------
        custom_list_id: :class:`str`
            THe UUID associated with the custom list you wish to add the manga to.

        Raises
        -------
        Forbidden
            You are not authorised to remove a manga from the specified custom list.
        NotFound
            The specified manga or specified custom list are not found, likely due to an incorrect UUID.
        """

        await self._http._remove_manga_from_custom_list(manga_id=self.id, custom_list_id=custom_list_id)
