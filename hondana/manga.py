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
from typing import TYPE_CHECKING, Literal, Optional, Union

from .artist import Artist
from .author import Author
from .collections import ChapterFeed, MangaRelationCollection
from .cover import Cover
from .enums import ContentRating, MangaRelationType, MangaState, MangaStatus, PublicationDemographic, ReadingStatus
from .query import ArtistIncludes, AuthorIncludes, ChapterIncludes, CoverIncludes, FeedOrderQuery, MangaIncludes
from .tags import Tag
from .utils import MISSING, cached_slot_property, relationship_finder, require_authentication


if TYPE_CHECKING:
    from .http import HTTPClient
    from .tags import QueryTags
    from .types_ import manga
    from .types_.artist import ArtistResponse
    from .types_.author import AuthorResponse
    from .types_.common import LanguageCode, LocalizedString
    from .types_.cover import CoverResponse
    from .types_.manga import MangaResponse
    from .types_.relationship import RelationshipResponse
    from .types_.statistics import BatchStatisticsResponse, PersonalMangaRatingsResponse, StatisticsResponse


__all__ = (
    "Manga",
    "MangaRelation",
    "MangaStatistics",
    "MangaRating",
)


class Manga:
    """A class representing a Manga returned from the MangaDex API.

    Attributes
    -----------
    id: :class:`str`
        The UUID associated to this manga.
    relation_type: Optional[:class:`~hondana.MangaRelationType`]
        The type of relation this is, to the parent manga requested.
        Only available when :meth:`get_related_manga` is called.
    alternate_titles: :class:`~hondana.types.common.LocalizedString`
        The alternative title mapping for the Manga.
        i.e. ``{"en": "Some Other Title"}``
    locked: :class:`bool`
        If the Manga is considered 'locked' or not in the API.
    links: :class:`~hondana.types.manga.MangaLinks`
        The mapping of links the API has attributed to the Manga.
        (see: https://api.mangadex.org/docs.html#section/Static-data/Manga-links-data)
    original_language: :class:`str`
        The language code for the original language of the Manga.
    last_volume: Optional[:class:`str`]
        The last volume attributed to the manga, if any.
    last_chapter: Optional[:class:`str`]
        The last chapter attributed to the manga, if any.
    publication_demographic: Optional[:class:`~hondana.PublicationDemographic`]
        The attributed publication demographic(s) for the manga, if any.
    year: Optional[:class:`int`]
        The year the manga was release, if the key exists.
    content_rating: Optional[:class:`~hondana.ContentRating`]
        The content rating attributed to the manga, if any.
    chapter_numbers_reset_on_new_volume: :class:`bool`
        Whether the chapter numbers will reset on a new volume or not.
    latest_uploaded_chapter: :class:`str`
        The ID of the latest uploaded chapter of this manga.
    state: Optional[:class:`~hondana.MangaState`]
        The publication state of the Manga.
    stats: Optional[:class:`~hondana.MangaStatistics`]
        The statistics of the manga.
    version: :class:`int`
        The version revision of this manga.


    .. note::
        The :attr:`stats` is only populated after :meth:`~hondana.Manga.get_statistics` is called.
    """

    __slots__ = (
        "_http",
        "_data",
        "_attributes",
        "_title",
        "_description",
        "id",
        "relation_type",
        "alternate_titles",
        "locked",
        "links",
        "original_language",
        "last_volume",
        "last_chapter",
        "publication_demographic",
        "status",
        "year",
        "content_rating",
        "chapter_numbers_reset_on_new_volume",
        "available_translated_languages",
        "latest_uploaded_chapter",
        "state",
        "stats",
        "version",
        "_tags",
        "_created_at",
        "_updated_at",
        "_artist_relationships",
        "_author_relationships",
        "_related_manga_relationships",
        "_cover_relationship",
        "__authors",
        "__artists",
        "__cover",
        "__related_manga",
        "_cs_tags",
    )

    def __init__(self, http: HTTPClient, payload: manga.MangaResponse) -> None:
        self._http = http
        self._data = payload
        relationships: list[RelationshipResponse] = self._data.pop("relationships", [])
        self._attributes = payload["attributes"]
        self.id: str = payload["id"]
        self._title = self._attributes["title"]
        self._description: LocalizedString = self._attributes["description"]
        _related = payload.get("related", None)
        self.relation_type: Optional[MangaRelationType] = MangaRelationType(_related) if _related else None
        self.alternate_titles: LocalizedString = {k: v for item in self._attributes["altTitles"] for k, v in item.items()}  # type: ignore # this is actually valid but breaks pylance (not pyright...?)? TODO: test in later version
        self.locked: bool = self._attributes.get("isLocked", False)
        self.links: manga.MangaLinks = self._attributes["links"]
        self.original_language: str = self._attributes["originalLanguage"]
        self.last_volume: Optional[str] = self._attributes["lastVolume"]
        self.last_chapter: Optional[str] = self._attributes["lastChapter"]
        self.publication_demographic: Optional[PublicationDemographic] = (
            PublicationDemographic(self._attributes["publicationDemographic"])
            if self._attributes["publicationDemographic"]
            else None
        )
        self.status: Optional[MangaStatus] = MangaStatus(self._attributes["status"])
        self.year: Optional[int] = self._attributes["year"]
        self.content_rating: Optional[ContentRating] = (
            ContentRating(self._attributes["contentRating"]) if self._attributes["contentRating"] else None
        )
        self.chapter_numbers_reset_on_new_volume: bool = self._attributes["chapterNumbersResetOnNewVolume"]
        self.available_translated_languages: list[LanguageCode] = self._attributes["availableTranslatedLanguages"]
        self.latest_uploaded_chapter: str = self._attributes["latestUploadedChapter"]
        self.state: Optional[MangaState] = MangaState(self._attributes["state"]) if self._attributes["state"] else None
        self.stats: Optional[MangaStatistics] = None
        self.version: int = self._attributes["version"]
        self._tags = self._attributes["tags"]
        self._created_at = self._attributes["createdAt"]
        self._updated_at = self._attributes["updatedAt"]
        self._author_relationships: list[AuthorResponse] = relationship_finder(relationships, "author", limit=None)
        self._artist_relationships: list[ArtistResponse] = relationship_finder(relationships, "artist", limit=None)
        self._related_manga_relationships: list[MangaResponse] = relationship_finder(relationships, "manga", limit=None)
        self._cover_relationship: Optional[CoverResponse] = relationship_finder(relationships, "cover_art", limit=1)
        self.__authors: Optional[list[Author]] = None
        self.__artists: Optional[list[Artist]] = None
        self.__cover: Optional[Cover] = None
        self.__related_manga: Optional[list[Manga]] = None

    def __repr__(self) -> str:
        return f"<Manga id={self.id!r} title={self.title!r}>"

    def __str__(self) -> str:
        return self.title

    def __eq__(self, other: Union[Manga, MangaRelation]) -> bool:
        return self.id == other.id

    def __ne__(self, other: Union[Manga, MangaRelation]) -> bool:
        return not self.__eq__(other)

    @property
    def url(self) -> str:
        """The URL to this manga.

        Returns
        --------
        :class:`str`
            The URL of the manga.
        """
        return f"https://mangadex.org/title/{self.id}"

    @property
    def title(self) -> str:
        """The manga's title.

        Returns
        --------
        :class:`str`
            The title of the manga, defaults to the ``en`` key in the titles attribute of the response.
            Attempts to fall back to the manga's default language, and failing that it will
            fall back to the next available key if ``en`` or default language key is not present.
        """
        title = self._title.get("en")
        if title is None:
            key = next(iter(self._title))
            title = self._title.get(self.original_language, self._title[key])

        return title

    @property
    def description(self) -> Optional[str]:
        """The manga's description/synopsis.

        Returns
        --------
        Optional[:class:`str`]
            The description of the manga, defaults to the ``en`` key in the titles.
            Falls back to the next available key if ``en`` is not present. If there is
            no description, returns None.
        """
        desc = self._description.get("en")
        if desc is None:
            if not self._description:
                return None
            key = next(iter(self._description))
            return self._description[key]
        return desc

    @property
    def raw_description(self) -> LocalizedString:
        """The raw description attribute from the manga's payload from the API.

        Returns
        --------
        :class:`~hondana.types.common.LocalizedString`
            The raw object from the manga's api response payload.
            Provides no formatting on its own. Consider :meth:`~hondana.Manga.description` or :meth:`~hondana.Manga.localised_description` instead.
        """
        return self._description

    @property
    def alt_titles(self) -> LocalizedString:
        """The raw alt_titles attribute from the manga's payload from the API.

        Returns
        --------
        :class:`hondana.types.common.LocalizedString`
            The raw object from the manga's payload.
            Provides no formatting on its own. Consider :meth:`~hondana.Manga.localised_title` instead.
        """
        return self.alternate_titles

    @property
    def created_at(self) -> datetime.datetime:
        """The date this manga was created.

        Returns
        --------
        :class:`datetime.datetime`
            The UTC datetime of when this manga was created.
        """
        return datetime.datetime.fromisoformat(self._created_at)

    @property
    def updated_at(self) -> datetime.datetime:
        """The date this manga was last updated.

        Returns
        --------
        :class:`datetime.datetime`
            The UTC datetime of when this manga was last updated.
        """
        return datetime.datetime.fromisoformat(self._updated_at)

    @cached_slot_property("_cs_tags")
    def tags(self) -> list[Tag]:
        """The tags of this Manga.

        Returns
        --------
        List[:class:`~hondana.Tag`]
            The list of tags that this manga is associated with.
        """
        return [Tag(item) for item in self._tags]

    @property
    def artists(self) -> Optional[list[Artist]]:
        """The artists of the parent Manga.


        .. note::
            If the parent manga was **not** requested with the "artist" `includes[]` query parameter
            then this method will return ``None``.

        Returns
        --------
        Optional[List[:class:`~hondana.Artist`]]
            The artists associated with this Manga.
        """
        if self.__artists is not None:
            return self.__artists

        if not self._artist_relationships:
            return

        formatted: list[Artist] = [
            Artist(self._http, artist) for artist in self._artist_relationships if "attributes" in artist
        ]

        if not formatted:
            return None

        self.__artists = formatted
        return self.__artists

    @artists.setter
    def artists(self, value: list[Artist]) -> None:
        self.__artists = [item for item in value if isinstance(item, Artist)]

    @property
    def authors(self) -> Optional[list[Author]]:
        """The artists of the parent Manga.


        .. note::
            If the parent manga was **not** requested with the "artist" `includes[]` query parameter
            then this method will return ``None``.

        Returns
        --------
        Optional[List[:class:`~hondana.Author`]]
            The artists associated with this Manga.

        """
        if self.__authors is not None:
            return self.__authors

        if not self._author_relationships:
            return

        formatted: list[Author] = [
            Author(self._http, author) for author in self._author_relationships if "attributes" in author
        ]

        if not formatted:
            return

        self.__authors = formatted
        return self.__authors

    @authors.setter
    def authors(self, value: list[Author]) -> None:
        self.__authors = [item for item in value if isinstance(item, Author)]

    @property
    def cover(self) -> Optional[Cover]:
        """The cover of the manga.


        .. note::
            If the parent manga was **not** requested with the "cover" `includes[]` query parameter
            then this method will return ``None``.

        Returns
        --------
        Optional[:class:`~hondana.Cover`]
            The cover of the manga.
        """
        if self.__cover is not None:
            return self.__cover

        if not self._cover_relationship:
            return

        if "attributes" in self._cover_relationship:
            self.__cover = Cover(self._http, self._cover_relationship)
            return self.__cover

    @cover.setter
    def cover(self, value: Cover) -> None:
        if isinstance(value, Cover):
            self.__cover = value

    @property
    def related_manga(self) -> Optional[list[Manga]]:
        """The related manga of the parent Manga.

        Returns
        --------
        Optional[List[:class:`~hondana.Manga`]]
            The related manga of the parent manga.
        """
        if self.__related_manga is not None:
            return self.__related_manga

        if not self._related_manga_relationships:
            return

        formatted: list[Manga] = [
            self.__class__(self._http, item) for item in self._related_manga_relationships if "attributes" in item
        ]

        if not formatted:
            return

        self.__related_manga = formatted
        return self.__related_manga

    @related_manga.setter
    def related_manga(self, value: list[Manga]) -> None:
        self.__related_manga = [item for item in value if isinstance(item, self.__class__)]

    async def get_artists(self) -> Optional[list[Artist]]:
        """|coro|

        This method will return the artists of the manga and caches the response.


        .. note::
            If the parent manga was requested with the "artist" `includes[]` query parameter,
            then this method will not make extra API calls to retrieve the artist data.

        Returns
        --------
        Optional[List[:class:`~hondana.Author`]]
            The artists of the manga.
        """
        if self.artists is not None:
            return self.artists

        if not self._artist_relationships:
            return

        ids = [r["id"] for r in self._artist_relationships]

        formatted: list[Artist] = []
        for item in ids:
            data = await self._http._get_artist(item, includes=ArtistIncludes())
            formatted.append(Artist(self._http, data["data"]))

        if not formatted:
            return

        self.artists = formatted
        return formatted

    async def get_authors(self) -> Optional[list[Author]]:
        """|coro|

        This method will return the authors of the manga and caches the response.


        .. note::
            If the parent manga was requested with the "author" `includes[]` query parameter,
            then this method will not make extra API calls to retrieve the author data.

        Returns
        --------
        Optional[List[:class:`~hondana.Author`]]
            The authors of the manga.
        """
        if self.authors is not None:
            return self.authors

        if not self._author_relationships:
            return

        ids = [r["id"] for r in self._related_manga_relationships]

        formatted: list[Author] = []
        for item in ids:
            data = await self._http._get_author(item, includes=AuthorIncludes())
            formatted.append(Author(self._http, data["data"]))

        if not formatted:
            return

        self.authors = formatted
        return formatted

    async def get_cover(self) -> Optional[Cover]:
        """|coro|

        This method will return the cover URL of the parent Manga if it exists and caches the response.

        Returns
        --------
        Optional[:class:`~hondana.Cover`]
            The Cover associated with this Manga.
        """
        if self.cover is not None:
            return self.cover

        if not self._cover_relationship:
            return

        data = await self._http._get_cover(self._cover_relationship["id"], includes=CoverIncludes())
        self.cover = Cover(self._http, data["data"])
        return self.cover

    def cover_url(self, *, size: Optional[Literal[256, 512]] = None) -> Optional[str]:
        """This method will return a direct url to the cover art of the parent Manga.

        If the manga was requested without the ``"cover_art"`` includes[] parameters, then this method will return ``None``.


        .. note::
            For a more stable cover return, try :meth:`~hondana.Manga.get_cover`
        """
        if not self.cover:
            return

        return self.cover.url(size, parent_id=self.id)

    async def get_related_manga(self, *, limit: int = 100, offset: int = 0) -> Optional[list[Manga]]:
        """|coro|

        This method will return all the related manga and cache their response.

        Parameters
        -----------
        limit: :class:`int`
            The amount of manga to fetch. Defaults to ``100``.
        offset: :class:`int`
            The pagination offset. Defaults to ``0``.


        .. note::
            If the parent manga was requested with the "manga" `includes[]` query parameter,
            then this method will not make extra API calls to retrieve manga data.

        Returns
        --------
        Optional[List[:class:`~hondana.Manga`]]
            The related manga of the parent.
        """
        if self.related_manga is not None:
            return self.related_manga

        if not self._related_manga_relationships:
            return

        ids = [r["id"] for r in self._related_manga_relationships]

        data = await self._http._manga_list(
            limit=limit,
            offset=offset,
            title=None,
            author_or_artist=None,
            authors=None,
            artists=None,
            year=None,
            included_tags=None,
            excluded_tags=None,
            status=None,
            original_language=None,
            excluded_original_language=None,
            available_translated_language=None,
            publication_demographic=None,
            ids=ids,
            content_rating=None,
            created_at_since=None,
            updated_at_since=None,
            order=None,
            includes=MangaIncludes(),
            has_available_chapters=None,
            group=None,
        )

        ret: list[Manga] = [Manga(self._http, item) for item in data["data"]]
        if not ret:
            return

        self.related_manga = ret
        return self.related_manga

    @require_authentication
    async def update(
        self,
        *,
        title: Optional[LocalizedString] = None,
        alt_titles: Optional[list[LocalizedString]] = None,
        description: Optional[LocalizedString] = None,
        authors: Optional[list[str]] = None,
        artists: Optional[list[str]] = None,
        links: Optional[manga.MangaLinks] = None,
        original_language: Optional[str] = None,
        last_volume: Optional[str] = MISSING,
        last_chapter: Optional[str] = MISSING,
        publication_demographic: PublicationDemographic = MISSING,
        status: Optional[MangaStatus] = None,
        year: Optional[int] = MISSING,
        content_rating: Optional[ContentRating] = None,
        tags: Optional[QueryTags] = None,
        primary_cover: Optional[str] = MISSING,
        version: int,
    ) -> Manga:
        """|coro|

        This method will update the current Manga within the MangaDex API.

        Parameters
        -----------
        title: Optional[:class:`~hondana.types.common.LocalizedString`]
            The manga titles in the format of ``language_key: title``
            i.e. ``{"en": "Some Manga Title"}``
        alt_titles: Optional[List[:class:`~hondana.types.common.LocalizedString`]]
            The alternative titles in the format of ``language_key: title``
            i.e. ``[{"en": "Some Other Title"}, {"fr": "Un Autre Titre"}]``
        description: Optional[:class:`~hondana.types.common.LocalizedString`]
            The manga description in the format of ``language_key: description``
            i.e. ``{"en": "My amazing manga where x y z happens"}``
        authors: Optional[List[:class:`str`]]
            The list of author UUIDs to credit to this manga.
        artists: Optional[List[:class:`str`]]
            The list of artist UUIDs to credit to this manga.
        links: Optional[:class:`~hondana.types.manga.MangaLinks`]
            The links relevant to the manga.
            See here for more details: https://api.mangadex.org/docs.html#section/Static-data/Manga-links-data
        original_language: Optional[:class:`str`]
            The language key for the original language of the manga.
        last_volume: Optional[:class:`str`]
            The last volume to attribute to this manga.
        last_chapter: Optional[:class:`str`]
            The last chapter to attribute to this manga.
        publication_demographic: Optional[:class:`~hondana.PublicationDemographic`]
            The target publication demographic of this manga.
        status: Optional[:class:`~hondana.MangaStatus`]
            The status of the manga.
        year: Optional[:class:`int`]
            The release year of the manga.
        content_rating: Optional[:class:`~hondana.ContentRating`]
            The content rating of the manga.
        tags: Optional[:class:`QueryTags`]
            The QueryTags instance for the list of tags to attribute to this manga.
        primmary_cover: Optional[:class:`str`]
            The UUID representing the cover that should show for this manga as it's primary.
        version: :class:`int`
            The revision version of this manga.


        .. note::
            The ``last_volume``, ``last_chapter``, ``publication_demographic``, ``year`` and ``primary_cover`` parameters
            are nullable in the API. Pass ``None`` explicitly to do so.

        Raises
        -------
        :exc:`BadRequest`
            The query parameters were not valid.
        :exc:`Forbidden`
            The update returned an error due to authentication failure.
        :exc:`NotFound`
            The specified manga does not exist.

        Returns
        --------
        :class:`~hondana.Manga`
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
            primary_cover=primary_cover,
            version=version,
        )

        return self.__class__(self._http, data["data"])

    @require_authentication
    async def delete(self) -> None:
        """|coro|

        This method will delete a Manga from the MangaDex API.

        Raises
        -------
        :exc:`Forbidden`
            The update returned an error due to authentication failure.
        :exc:`NotFound`
            The specified manga does not exist.
        """

        await self._http._delete_manga(self.id)

    @require_authentication
    async def unfollow(self) -> None:
        """|coro|

        This method will unfollow the current Manga for the logged-in user in the MangaDex API.

        Raises
        -------
        :exc:`Forbidden`
            The request returned an error due to authentication failure.
        :exc:`NotFound`
            The specified manga does not exist.
        """
        await self._http._unfollow_manga(self.id)

    @require_authentication
    async def follow(self, *, set_status: bool = True, status: ReadingStatus = ReadingStatus.reading) -> None:
        """|coro|

        This method will follow the current Manga for the logged-in user in the MangaDex API.

        Parameters
        -----------
        set_status: :class:`bool`
            Whether to set the reading status of the manga you follow.
            Due to the current MangaDex infrastructure, not setting a status will cause the manga to not show up in your lists.
            Defaults to ``True``
        status: :class:`~hondana.ReadingStatus`
            The status to apply to the newly followed manga.
            Irrelevant if ``set_status`` is ``False``.

        Raises
        -------
        :exc:`Forbidden`
            The request returned an error due to authentication failure.
        :exc:`NotFound`
            The specified manga does not exist.
        """
        await self._http._follow_manga(self.id)
        if set_status:
            await self.update_reading_status(status=status)

    def localised_title(self, language_code: LanguageCode, /) -> Optional[str]:
        """
        This method will attempt to return the current manga's title in the provided language code.
        Falling back to the :attr:`title`.

        Aliased to :meth:`~Manga.localized_title`

        Parameters
        -----------
        language_code: :class:`~hondana.types.common.LanguageCode`
            The language code to attempt to return the manga name in.

        Returns
        --------
        Optional[:class:`str`]
            The manga name in the provided language, if found.
        """
        return self.alternate_titles.get(language_code, self.title)

    localized_title = localised_title

    def localised_description(self, language_code: LanguageCode, /) -> Optional[str]:
        """
        This method will attempt to return the current manga's description in the provided language code.
        Falling back to the :attr:`description`.

        Aliased to :meth:`~Manga.localized_description`

        Parameters
        -----------
        language_code: :class:`~hondana.types.common.LanguageCode`
            The language code to attempt to return the manga description in.

        Returns
        --------
        Optional[:class:`str`]
            The manga description in the provided language, if found.
        """
        return self._description.get(language_code, self.description)

    localized_description = localised_description

    async def feed(
        self,
        *,
        limit: Optional[int] = 100,
        offset: int = 0,
        translated_language: Optional[list[LanguageCode]] = None,
        original_language: Optional[list[LanguageCode]] = None,
        excluded_original_language: Optional[list[LanguageCode]] = None,
        content_rating: Optional[list[ContentRating]] = None,
        excluded_groups: Optional[list[str]] = None,
        excluded_uploaders: Optional[list[str]] = None,
        include_future_updates: Optional[bool] = None,
        created_at_since: Optional[datetime.datetime] = None,
        updated_at_since: Optional[datetime.datetime] = None,
        published_at_since: Optional[datetime.datetime] = None,
        order: Optional[FeedOrderQuery] = None,
        includes: Optional[ChapterIncludes] = ChapterIncludes(),
        include_empty_pages: Optional[bool] = None,
        include_future_publish_at: Optional[bool] = None,
        include_external_url: Optional[bool] = None,
    ) -> ChapterFeed:
        """|coro|

        This method returns the current manga's chapter feed.

        Parameters
        -----------
        limit: Optional[:class:`int`]
            Defaults to 100. The maximum amount of chapters to return-in the response.
        offset: :class:`int`
            Defaults to 0. The pagination offset for the request.
        translated_language: List[:class:`str`]
            A list of language codes to filter the returned chapters with.
        original_language: List[:class:`~hondana.types.common.LanguageCode`]
            A list of language codes to filter the original language of the returned chapters with.
        excluded_original_language: List[:class:`~hondana.types.common.LanguageCode`]
            A list of language codes to negate filter the original language of the returned chapters with.
        content_rating: Optional[List[:class:`~hondana.ContentRating`]]
            The content rating to filter the feed by.
        excluded_groups: Optional[List[:class:`str`]]
            The list of scanlator groups to exclude from the response.
        excluded_uploaders: Optional[List[:class:`str`]]
            The list of uploaders to exclude from the response.
        include_future_updates: Optional[:class:`bool`]
            Whether to include future chapters in this feed. Defaults to ``True`` API side.
        created_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their creation date.
        updated_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their updated at date.
        published_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their published at date.
        order: Optional[:class:`~hondana.query.FeedOrderQuery`]
            A query parameter to choose how the responses are ordered.
            i.e. ``{"chapters": "desc"}``
        includes: Optional[:class:`~hondana.query.ChapterIncludes`]
            The list of options to include increased payloads for per chapter.
            Defaults to these values.
        include_empty_pages: Optional[:class:`bool`]
            Whether to show chapters with no pages available.
        include_future_publish_at: Optional[:class:`bool`]
            Whether to show chapters with a publishAt value set in the future.
        includeExternalUrl: Optional[:class:`bool`]
            Whether to show chapters that have an external URL attached to them.


        .. note::
            Passing ``None`` to ``limit`` will attempt to retrieve all items in the chapter feed.

        Raises
        -------
        :exc:`BadRequest`
            The query parameters were malformed.

        Returns
        --------
        :class:`~hondana.ChapterFeed`
            Returns a collection of chapters.
        """

        inner_limit = limit or 100

        chapters = []
        while True:
            data = await self._http._manga_feed(
                self.id,
                limit=inner_limit,
                offset=offset,
                translated_language=translated_language,
                original_language=original_language,
                excluded_original_language=excluded_original_language,
                content_rating=content_rating,
                excluded_groups=excluded_groups,
                excluded_uploaders=excluded_uploaders,
                include_future_updates=include_future_updates,
                created_at_since=created_at_since,
                updated_at_since=updated_at_since,
                published_at_since=published_at_since,
                order=order,
                includes=includes,
                include_empty_pages=include_empty_pages,
                include_future_publish_at=include_future_publish_at,
                include_external_url=include_external_url,
            )

            from .chapter import Chapter

            chapters.extend([Chapter(self._http, item) for item in data["data"]])

            offset += inner_limit
            if not data["data"] or offset >= 10_000 or limit is not None:
                break

        return ChapterFeed(self._http, data, chapters)

    @require_authentication
    async def update_read_markers(self) -> manga.MangaReadMarkersResponse:
        """|coro|

        This method will return the read chapters of the current manga.

        Returns
        --------
        :class:`hondana.types.manga.MangaReadMarkersResponse`
            The raw payload of the API.
            Contains a list of read chapter UUIDs.
        """
        return await self._http._manga_read_markers([self.id], grouped=False)

    @require_authentication
    async def bulk_update_read_markers(
        self, *, update_history: bool = True, read_chapters: Optional[list[str]], unread_chapters: Optional[list[str]]
    ) -> None:
        """|coro|

        This method will batch update your read chapters for a given Manga.

        Parameters
        -----------
        update_history: :class:`bool`
            Whether to show this chapter in the authenticated user's read history.
            Defaults to ``True``.
        read_chapters: Optional[List[:class:`str`]]
            The read chapters for this Manga.
        unread_chapters: Optional[List[:class:`str`]]
            The unread chapters for this Manga.

        Raises
        -------
        :exc:`TypeError`
            You must provide one or both of the parameters `read_chapters` and/or `unread_chapters`.
        """
        if not read_chapters and not unread_chapters:
            raise TypeError("You must provide either `read_chapters` and/or `unread_chapters` to this method.")

        await self._http._manga_read_markers_batch(
            self.id, update_history=update_history, read_chapters=read_chapters, unread_chapters=unread_chapters
        )

    @require_authentication
    async def get_reading_status(self) -> manga.MangaSingleReadingStatusResponse:
        """|coro|

        This method will return the current reading status for the current manga.

        Raises
        -------
        :exc:`Forbidden`
            You are not authenticated to perform this action.
        :exc:`NotFound`
            The specified manga does not exist, likely due to an incorrect ID.

        Returns
        --------
        :class:`~hondana.types.manga.MangaSingleReadingStatusResponse`
            The raw payload from the API response.
        """
        return await self._http._get_manga_reading_status(self.id)

    @require_authentication
    async def update_reading_status(self, *, status: ReadingStatus) -> None:
        """|coro|

        This method will update your current reading status for the current manga.

        Parameters
        -----------
        status: :class:`~hondana.ReadingStatus`
            The reading status you wish to update this manga with.


        .. note::
            Leaving ``status`` as the default will remove the manga reading status from the API.
            Please provide a value if you do not wish for this to happen.

        Raises
        -------
        :exc:`BadRequest`
            The query parameters were invalid.
        :exc:`NotFound`
            The specified manga cannot be found, likely due to incorrect ID.
        """

        await self._http._update_manga_reading_status(self.id, status=status)

    async def get_volumes_and_chapters(
        self,
        *,
        translated_language: Optional[list[LanguageCode]] = None,
        groups: Optional[list[str]] = None,
    ) -> manga.GetMangaVolumesAndChaptersResponse:
        """|coro|

        This endpoint returns the raw relational mapping of a manga's volumes and chapters.

        Parameters
        -----------
        translated_language: Optional[List[:class:`~hondana.types.common.LanguageCode`]]
            The list of language codes you want to limit the search to.
        groups: Optional[List[:class:`str`]]
            A list of scanlator groups to filter the results by.

        Returns
        --------
        :class:`~hondana.types.manga.GetMangaVolumesAndChaptersResponse`
            The raw payload from mangadex. There is no guarantee of the keys here.
        """
        data = await self._http._get_manga_volumes_and_chapters(
            manga_id=self.id, translated_language=translated_language, groups=groups
        )

        return data

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
        :exc:`Forbidden`
            You are not authorised to add manga to this custom list.
        :exc:`NotFound`
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
        :exc:`Forbidden`
            You are not authorised to remove a manga from the specified custom list.
        :exc:`NotFound`
            The specified manga or specified custom list are not found, likely due to an incorrect UUID.
        """

        await self._http._remove_manga_from_custom_list(manga_id=self.id, custom_list_id=custom_list_id)

    async def get_chapters(
        self,
        *,
        limit: Optional[int] = 10,
        offset: int = 0,
        ids: Optional[list[str]] = None,
        title: Optional[str] = None,
        groups: Optional[list[str]] = None,
        uploader: Optional[str] = None,
        volumes: Optional[list[str]] = None,
        chapter: Optional[list[str]] = None,
        translated_language: Optional[list[LanguageCode]] = None,
        original_language: Optional[list[LanguageCode]] = None,
        excluded_original_language: Optional[list[LanguageCode]] = None,
        content_rating: Optional[list[ContentRating]] = None,
        excluded_groups: Optional[list[str]] = None,
        excluded_uploaders: Optional[list[str]] = None,
        include_future_updates: Optional[bool] = None,
        include_empty_pages: Optional[bool] = None,
        include_future_publish_at: Optional[bool] = None,
        include_external_url: Optional[bool] = None,
        created_at_since: Optional[datetime.datetime] = None,
        updated_at_since: Optional[datetime.datetime] = None,
        published_at_since: Optional[datetime.datetime] = None,
        order: Optional[FeedOrderQuery] = None,
        includes: Optional[ChapterIncludes] = ChapterIncludes(),
    ) -> ChapterFeed:
        """|coro|

        This method will return a list of published chapters.

        Parameters
        -----------
        limit: Optional[:class:`int`]
            Defaults to 100. This specifies the amount of chapters to return in one request.
        offset: :class:`int`
            Defaults to 0. This specifies the pagination offset.
        ids: Optional[List[:class:`str`]]
            The list of chapter UUIDs to filter the request with.
        title: Optional[:class:`str`]
            The chapter title query to limit the request with.
        groups: Optional[List[:class:`str`]]
            The scanlation group UUID(s) to limit the request with.
        uploader: Optional[:class:`str`]
            The uploader UUID to limit the request with.
        volumes: Optional[Union[:class:`str`, List[:class:`str`]]]
            The volume UUID or UUIDs to limit the request with.
        chapter: Optional[Union[:class:`str`, List[:class:`str`]]]
            The chapter UUID or UUIDs to limit the request with.
        translated_language: Optional[List[:class:`~hondana.types.common.LanguageCode`]]
            The list of languages codes to filter the request with.
        original_language: Optional[List[:class:`~hondana.types.common.LanguageCode`]]
            The list of languages to specifically target in the request.
        excluded_original_language: Optional[List[:class:`~hondana.types.common.LanguageCode`]]
            The list of original languages to exclude from the request.
        content_rating: Optional[List[:class:`~hondana.ContentRating`]]
            The content rating to filter the feed by.
        excluded_groups: Optional[List[:class:`str`]]
            The list of scanlator groups to exclude from the response.
        excluded_uploaders: Optional[List[:class:`str`]]
            The list of uploaders to exclude from the response.
        include_future_updates: Optional[:class:`bool`]
            Whether to include future chapters in this feed. Defaults to ``True`` API side.
        include_empty_pages: Optional[:class:`bool`]
            Whether to include chapters that have no recorded pages.
        include_future_publish_at: Optional[:class:`bool`]
            Whether to include chapters that have a :attr:`publish_at` set to a time in the future.
        include_external_url: Optional[:class:`bool`]
            Whether to include chapters that have an external url set.
        created_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their creation date.
        updated_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their updated at date.
        published_at_since: Optional[:class:`datetime.datetime`]
            A start point to return chapters from based on their published at date.
        order: Optional[:class:`~hondana.query.FeedOrderQuery`]
            A query parameter to choose how the responses are ordered.
            i.e. ``{"chapters": "desc"}``
        includes: Optional[:class:`~hondana.query.ChapterIncludes`]
            The list of options to include increased payloads for per chapter.
            Defaults to all values.


        .. note::
            Passing ``None`` to ``limit`` will attempt to retrieve all items in the chapter feed.

        .. note::
            If `order` is not specified then the API will return results first based on their creation date,
            which could lead to unexpected results.

        Raises
        -------
        :exc:`BadRequest`
            The query parameters were malformed

        Returns
        --------
        :class:`~hondana.ChapterFeed`
            Returns a collection of chapters.
        """

        inner_limit = limit or 10

        chapters = []
        while True:
            data = await self._http._chapter_list(
                limit=inner_limit,
                offset=offset,
                manga=self.id,
                ids=ids,
                title=title,
                groups=groups,
                uploader=uploader,
                volume=volumes,
                chapter=chapter,
                translated_language=translated_language,
                original_language=original_language,
                excluded_original_language=excluded_original_language,
                content_rating=content_rating,
                excluded_groups=excluded_groups,
                excluded_uploaders=excluded_uploaders,
                include_future_updates=include_future_updates,
                include_empty_pages=include_empty_pages,
                include_future_publish_at=include_future_publish_at,
                include_external_url=include_external_url,
                created_at_since=created_at_since,
                updated_at_since=updated_at_since,
                published_at_since=published_at_since,
                order=order,
                includes=includes,
            )
            from .chapter import Chapter

            chapters.extend([Chapter(self._http, item) for item in data["data"]])

            offset += inner_limit
            if not data["data"] or offset >= 10_000 or limit is not None:
                break

        return ChapterFeed(self._http, data, chapters)

    async def get_draft(self) -> Manga:
        """|coro|

        This method will return a manga draft from MangaDex.

        Returns
        --------
        :class:`~hondana.Manga`
            The Manga returned from the API.
        """
        data = await self._http._get_manga_draft(self.id)
        return self.__class__(self._http, data["data"])

    async def submit_draft(self, *, version: int) -> Manga:
        """|coro|

        This method will submit a draft for a manga.

        Parameters
        -----------
        version: :class:`int`
            The version of the manga we're attributing this submission to.

        Raises
        -------
        :exc:`BadRequest`
            The request parameters were incorrect or malformed.
        :exc:`Forbidden`
            You are not authorised to perform this action.
        :exc:`NotFound`
            The manga was not found.

        Returns
        --------
        :class:`~hondana.Manga`
        """
        data = await self._http._submit_manga_draft(self.id, version=version)
        return self.__class__(self._http, data["data"])

    async def get_relations(self, *, includes: Optional[MangaIncludes] = MangaIncludes()) -> MangaRelationCollection:
        """|coro|

        This method will return a list of all relations to a given manga.

        Parameters
        -----------
        includes: Optional[:class:`~hondana.query.MangaIncludes`]
            The optional parameters for expanded requests to the API.
            Defaults to all possible expansions.

        Raises
        -------
        :exc:`BadRequest`
            The manga ID passed is malformed

        Returns
        --------
        :class:`~hondana.MangaRelationCollection`
        """
        data = await self._http._get_manga_relation_list(self.id, includes=includes)
        fmt = [MangaRelation(self._http, self.id, item) for item in data["data"]]
        return MangaRelationCollection(self._http, data, fmt)

    @require_authentication
    async def upload_cover(
        self, *, cover: bytes, volume: Optional[str] = None, description: str, locale: Optional[LanguageCode] = None
    ) -> Cover:
        """|coro|

        This method will upload a cover to the MangaDex API.

        Parameters
        -----------
        cover: :class:`bytes`
            THe raw bytes of the image.
        volume: Optional[:class:`str`]
            The volume this cover relates to.
        description: :class:`str`
            The description of this cover.
        locale: Optional[:class:`~hondana.types.common.LanguageCode`]
            The locale of this cover.

        Raises
        -------
        :exc:`BadRequest`
            The volume parameter was malformed or the file was a bad format.
        :exc:`Forbidden`
            You are not permitted for this action.

        Returns
        --------
        :class:`~hondana.Cover`
        """
        data = await self._http._upload_cover(self.id, cover=cover, volume=volume, description=description, locale=locale)
        return Cover(self._http, data["data"])

    @require_authentication
    async def create_relation(self, *, target_manga: str, relation_type: MangaRelationType) -> MangaRelation:
        """|coro|

        This method will create a manga relation.

        Parameters
        ------------
        target_manga: :class:`str`
            The manga ID of the related manga.
        relation_type: :class:`~hondana.MangaRelationType`

        Raises
        -------
        :exc:`BadRequest`
            The parameters were malformed
        :exc:`Forbidden`
            You are not authorised for this action.

        Returns
        --------
        :class:`~hondana.MangaRelation`
        """
        data = await self._http._create_manga_relation(self.id, target_manga=target_manga, relation_type=relation_type)
        return MangaRelation(self._http, self.id, data["data"])

    @require_authentication
    async def delete_relation(self, relation_id: str, /) -> None:
        """|coro|

        This method will delete a manga relation.

        Parameters
        -----------
        relation_id: :class:`str`
            The ID of the related manga.
        """
        await self._http._delete_manga_relation(self.id, relation_id)

    @require_authentication
    async def set_rating(self, *, rating: int) -> None:
        """|coro|

        This method will set your rating on the manga.
        This method **overwrites** your previous set rating, if any.

        Parameters
        -----------
        rating: :class:`int`
            The rating value, between 0 and 10.

        Raises
        -------
        :exc:`Forbidden`
            The request returned a response due to authentication failure.
        :exc:`NotFound`
            The specified manga UUID was not found or does not exist.
        """
        await self._http._set_manga_rating(self.id, rating=rating)

    @require_authentication
    async def delete_rating(self) -> None:
        """|coro|

        This method will delete your set rating on the manga.

        Raises
        -------
        :exc:`Forbidden`
            The request returned a response due to authentication failure.
        :exc:`NotFound`
            The specified manga UUID was not found or does not exist.
        """
        await self._http._delete_manga_rating(self.id)

    async def get_statistics(self) -> MangaStatistics:
        """|coro|

        This method will fetch statistics on the current manga, and cache them as the :attr:`stats`

        Returns
        --------
        :class:`~hondana.MangaStatistics`
        """
        data = await self._http._get_manga_statistics(self.id)

        key = next(iter(data["statistics"]))
        stats = MangaStatistics(self._http, self.id, data["statistics"][key])

        self.stats = stats
        return self.stats


class MangaRelation:
    """A class representing a MangaRelation returned from the MangaDex API.

    Attributes
    -----------
    source_manga_id: :class:`str`
        The UUID associated to the parent manga of this relation.
    id: :class:`str`
        The UUID associated to this manga relation.
    version: :class:`int`
        The version revision of this manga relation.
    relation_type: :class:`~hondana.MangaRelationType`
        The type of relationship to the source manga.
    """

    __slots__ = (
        "_http",
        "_data",
        "_attributes",
        "_relationships",
        "source_manga_id",
        "id",
        "version",
        "relation_type",
    )

    def __init__(self, http: HTTPClient, parent_id: str, payload: manga.MangaRelation, /) -> None:
        self._http = http
        self._data = payload
        self._attributes = self._data["attributes"]
        self._relationships = self._data.pop("relationships", [])
        self.source_manga_id: str = parent_id
        self.id: str = self._data["id"]
        self.version: int = self._attributes["version"]
        self.relation_type: MangaRelationType = MangaRelationType(self._attributes["relation"])

    def __repr__(self) -> str:
        return f"<MangaRelation id={self.id!r} source_manga_id={self.source_manga_id!r}>"

    def __eq__(self, other: Union[MangaRelation, Manga]) -> bool:
        return self.id == other.id or self.source_manga_id == other.id

    def __ne__(self, other: Union[MangaRelation, Manga]) -> bool:
        return not self.__eq__(other)


class MangaStatistics:
    """
    A small object to house manga statistics.

    Attributes
    -----------
    follows: :class:`int`
        The number of follows this manga has.
    parent_id: :class:`str`
        The manga these statistics belong to.
    average: Optional[:class:`float`]
        The average mean score of the manga ratings.
    bayesian: Optional[:class:`float`]
        The bayesian average score of the manga ratings.
    distribution: Optional[Dict[:class:`str`, :class:`int`]]
        The scoring distribution of the manga.
        Keys are 1-10 and values are total amount of ratings per key.


    .. note::
        The :attr:`distribution` attribute will be None unless this object was created with :meth:`~hondana.Client.get_manga_statistics` or :meth:`~hondana.Manga.get_statistics`
    """

    __slots__ = (
        "_http",
        "_data",
        "_rating",
        "follows",
        "parent_id",
        "average",
        "bayesian",
        "distribution",
    )

    def __init__(
        self, http: HTTPClient, parent_id: str, payload: Union[StatisticsResponse, BatchStatisticsResponse]
    ) -> None:
        self._http = http
        self._data = payload
        self._rating = payload["rating"]
        self.follows: int = payload["follows"]
        self.parent_id: str = parent_id
        self.average: Optional[float] = self._rating["average"]
        self.bayesian: Optional[float] = self._rating["bayesian"]
        self.distribution: Optional[dict[str, int]] = self._rating.get("distribution")

    def __repr__(self) -> str:
        return f"<MangaStatistics for={self.parent_id!r}>"


class MangaRating:
    """
    A small object to encompass your personal manga ratings.

    Attributes
    -----------
    parent_id: :class:`str`
        The parent manga this rating belongs to.
    rating: :class:`int`
        Your personal rating for this manga, between 1 and 10.
    created_at: :class:`datetime.datetime`
        When you created the rating, as a UTC aware datetime.
    """

    __slots__ = (
        "_http",
        "_data",
        "parent_id",
        "rating",
        "created_at",
    )

    def __init__(self, http: HTTPClient, parent_id: str, payload: PersonalMangaRatingsResponse) -> None:
        self._http = http
        self._data = payload
        self.parent_id: str = parent_id
        self.rating: int = self._data["rating"]
        self.created_at: datetime.datetime = datetime.datetime.fromisoformat(self._data["createdAt"])

    def __repr__(self) -> str:
        return f"<MangaRating parent_id={self.parent_id!r}>"
