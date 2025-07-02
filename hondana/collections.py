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

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from .author import Author
    from .chapter import Chapter, PreviouslyReadChapter
    from .cover import Cover
    from .custom_list import CustomList
    from .http import HTTPClient
    from .legacy import LegacyItem
    from .manga import Manga, MangaRelation
    from .report import Report, UserReport
    from .scanlator_group import ScanlatorGroup
    from .types_.author import GetMultiAuthorResponse
    from .types_.chapter import ChapterReadHistoryResponse, GetMultiChapterResponse
    from .types_.cover import GetMultiCoverResponse
    from .types_.custom_list import GetMultiCustomListResponse
    from .types_.legacy import GetLegacyMappingResponse
    from .types_.manga import MangaRelationResponse, MangaSearchResponse
    from .types_.report import GetReportReasonResponse, GetUserReportReasonResponse
    from .types_.scanlator_group import GetMultiScanlationGroupResponse
    from .types_.user import GetMultiUserResponse
    from .user import User

__all__ = (
    "AuthorCollection",
    "ChapterFeed",
    "ChapterReadHistoryCollection",
    "CoverCollection",
    "CustomListCollection",
    "LegacyMappingCollection",
    "MangaCollection",
    "MangaRelationCollection",
    "ReportCollection",
    "ScanlatorGroupCollection",
    "UserCollection",
    "UserReportCollection",
)

T = TypeVar("T")


class BaseCollection(ABC, Generic[T]):
    """
    The base class for all collections. This class serves to make it easier to create functions that process
    arbitrary collections without needing to set up ``isinstance()`` checks.

    Attributes
    ----------
    total: :class:`int`
        The total possible results with this query could return.
    offset: :class:`int`
        The offset used in this query.
    limit: :class:`int`
        The limit used in this query.
    """  # noqa: D205

    total: int
    offset: int
    limit: int

    @property
    @abstractmethod
    def items(self) -> list[T]:
        """
        Returns the items in the collection.

        Returns
        -------
        :class:`list`
        """


class MangaCollection(BaseCollection["Manga"]):
    """
    A collection object type to represent manga.

    Attributes
    ----------
    manga: List[:class:`~hondana.Manga`]
        The manga returned from this collection.
    total: :class:`int`
        The total possible results with this query could return.
    offset: :class:`int`
        The offset used in this query.
    limit: :class:`int`
        The limit used in this query.
    """

    __slots__ = (
        "_data",
        "_http",
        "limit",
        "manga",
        "offset",
        "total",
    )

    def __init__(self, http: HTTPClient, payload: MangaSearchResponse, manga: list[Manga]) -> None:
        self._http: HTTPClient = http
        payload.pop("data", [])  # pyright: ignore[reportAssignmentType,reportArgumentType,reportUnknownArgumentType] # can't pop from a TypedDict
        self._data: MangaSearchResponse = payload
        self.manga: list[Manga] = manga
        self.total: int = payload.get("total", 0)
        self.offset: int = payload.get("offset", 0)
        self.limit: int = payload.get("limit", 0)
        super().__init__()

    def __repr__(self) -> str:
        return f"<MangaFeed manga={len(self.manga)} total={self.total} offset={self.offset} limit={self.limit}>"

    @property
    def items(self) -> list[Manga]:
        """
        Returns the mangas in the collection.

        Returns
        -------
        List[:class:`~hondana.Manga`]
        """
        return self.manga


class MangaRelationCollection(BaseCollection["MangaRelation"]):
    """
    A collection object type to represent manga relations.

    Attributes
    ----------
    relations: List[:class:`~hondana.MangaRelation`]
        The manga relations returned from this collection.
    total: :class:`int`
        The total possible results with this query could return.
    offset: :class:`int`
        The offset used in this query.
    limit: :class:`int`
        The limit used in this query.
    """

    __slots__ = (
        "_data",
        "_http",
        "limit",
        "offset",
        "relations",
        "total",
    )

    def __init__(self, http: HTTPClient, payload: MangaRelationResponse, relations: list[MangaRelation]) -> None:
        self._http: HTTPClient = http
        payload.pop("data", [])  # pyright: ignore[reportAssignmentType,reportArgumentType,reportUnknownArgumentType] # can't pop from a TypedDict
        self._data = payload
        self.relations: list[MangaRelation] = relations
        self.total: int = payload.get("total", 0)
        self.offset: int = payload.get("offset", 0)
        self.limit: int = payload.get("limit", 0)
        super().__init__()

    def __repr__(self) -> str:
        return (
            "<MangaRelationCollection "
            f"authors={len(self.relations)} "
            f"total={self.total} "
            f"offset={self.offset} "
            f"limit={self.limit}>"
        )

    @property
    def items(self) -> list[MangaRelation]:
        """
        Returns the manga relations in the collection.

        Returns
        -------
        List[:class:`~hondana.MangaRelation`]
        """
        return self.relations


class ChapterFeed(BaseCollection["Chapter"]):
    """
    A collection object type to represent chapters.

    Attributes
    ----------
    chapters: List[:class:`~hondana.Chapter`]
        The chapters returned from this collection.
    total: :class:`int`
        The total possible results with this query could return.
    offset: :class:`int`
        The offset used in this query.
    limit: :class:`int`
        The limit used in this query.
    """

    __slots__ = (
        "_data",
        "_http",
        "chapters",
        "limit",
        "offset",
        "total",
    )

    def __init__(self, http: HTTPClient, payload: GetMultiChapterResponse, chapters: list[Chapter]) -> None:
        self._http: HTTPClient = http
        payload.pop("data", [])  # pyright: ignore[reportAssignmentType,reportArgumentType,reportUnknownArgumentType] # can't pop from a TypedDict
        self._data: GetMultiChapterResponse = payload
        self.chapters: list[Chapter] = chapters
        self.total: int = payload.get("total", 0)
        self.offset: int = payload.get("offset", 0)
        self.limit: int = payload.get("limit", 0)
        super().__init__()

    def __repr__(self) -> str:
        return f"<ChapterFeed chapters={len(self.chapters)} total={self.total} offset={self.offset} limit={self.limit}>"

    @property
    def items(self) -> list[Chapter]:
        """
        Returns the chapters in the collection.

        Returns
        -------
        List[:class:`~hondana.Chapter`]
        """
        return self.chapters


class AuthorCollection(BaseCollection["Author"]):
    """
    A collection object type to represent authors.

    Attributes
    ----------
    authors: List[:class:`~hondana.Author`]
        The authors returned from this collection.
    total: :class:`int`
        The total possible results with this query could return.
    offset: :class:`int`
        The offset used in this query.
    limit: :class:`int`
        The limit used in this query.
    """

    __slots__ = (
        "_data",
        "_http",
        "authors",
        "limit",
        "offset",
        "total",
    )

    def __init__(self, http: HTTPClient, payload: GetMultiAuthorResponse, authors: list[Author]) -> None:
        self._http: HTTPClient = http
        payload.pop("data", [])  # pyright: ignore[reportAssignmentType,reportArgumentType,reportUnknownArgumentType] # can't pop from a TypedDict
        self._data: GetMultiAuthorResponse = payload
        self.authors: list[Author] = authors
        self.total: int = payload.get("total", 0)
        self.offset: int = payload.get("offset", 0)
        self.limit: int = payload.get("limit", 0)
        super().__init__()

    def __repr__(self) -> str:
        return f"<ArtistCollection authors={len(self.authors)} total={self.total} offset={self.offset} limit={self.limit}>"

    @property
    def items(self) -> list[Author]:
        """
        Returns the authors in the collection.

        Returns
        -------
        List[:class:`~hondana.Author`]
        """
        return self.authors


class CoverCollection(BaseCollection["Cover"]):
    """
    A collection object type to represent covers.

    Attributes
    ----------
    covers: List[:class:`~hondana.Cover`]
        The covers returned from this collection.
    total: :class:`int`
        The total possible results with this query could return.
    offset: :class:`int`
        The offset used in this query.
    limit: :class:`int`
        The limit used in this query.
    """

    __slots__ = (
        "_data",
        "_http",
        "covers",
        "limit",
        "offset",
        "total",
    )

    def __init__(self, http: HTTPClient, payload: GetMultiCoverResponse, covers: list[Cover]) -> None:
        self._http: HTTPClient = http
        payload.pop("data", [])  # pyright: ignore[reportAssignmentType,reportArgumentType,reportUnknownArgumentType] # can't pop from a TypedDict
        self._data: GetMultiCoverResponse = payload
        self.covers: list[Cover] = covers
        self.total: int = payload.get("total", 0)
        self.offset: int = payload.get("offset", 0)
        self.limit: int = payload.get("limit", 0)
        super().__init__()

    def __repr__(self) -> str:
        return f"<CoverCollection covers={len(self.covers)} total={self.total} offset={self.offset} limit={self.limit}>"

    @property
    def items(self) -> list[Cover]:
        """
        Returns the covers in the collection.

        Returns
        -------
        List[:class:`~hondana.Cover`]
        """
        return self.covers


class ScanlatorGroupCollection(BaseCollection["ScanlatorGroup"]):
    """
    A collection object type to represent scanlator groups.

    Attributes
    ----------
    groups: List[:class:`~hondana.ScanlatorGroup`]
        The groups returned from this collection.
    total: :class:`int`
        The total possible results with this query could return.
    offset: :class:`int`
        The offset used in this query.
    limit: :class:`int`
        The limit used in this query.
    """

    __slots__ = (
        "_data",
        "_http",
        "groups",
        "limit",
        "offset",
        "total",
    )

    def __init__(self, http: HTTPClient, payload: GetMultiScanlationGroupResponse, groups: list[ScanlatorGroup]) -> None:
        self._http: HTTPClient = http
        payload.pop("data", [])  # pyright: ignore[reportAssignmentType,reportArgumentType,reportUnknownArgumentType] # can't pop from a TypedDict
        self._data: GetMultiScanlationGroupResponse = payload
        self.groups: list[ScanlatorGroup] = groups
        self.total: int = payload.get("total", 0)
        self.limit: int = payload.get("limit", 0)
        self.offset: int = payload.get("offset", 0)
        super().__init__()

    def __repr__(self) -> str:
        return (
            "<ScanlatorGroupCollection "
            f"groups={len(self.groups)} "
            f"total={self.total} "
            f"offset={self.offset} "
            f"limit={self.limit}>"
        )

    @property
    def items(self) -> list[ScanlatorGroup]:
        """
        Returns the groups in the collection.

        Returns
        -------
        List[:class:`~hondana.ScanlatorGroup`]
        """
        return self.groups


class ReportCollection(BaseCollection["Report"]):
    """
    A collection object type to represent reports.

    Attributes
    ----------
    reports: List[:class:`~hondana.Report`]
        The reports returned from this collection.
    total: :class:`int`
        The total possible results with this query could return.
    offset: :class:`int`
        The offset used in this query.
    limit: :class:`int`
        The limit used in this query.
    """

    __slots__ = (
        "_data",
        "_http",
        "limit",
        "offset",
        "reports",
        "total",
    )

    def __init__(self, http: HTTPClient, payload: GetReportReasonResponse, reports: list[Report]) -> None:
        self._http: HTTPClient = http
        payload.pop("data", [])  # pyright: ignore[reportAssignmentType,reportArgumentType,reportUnknownArgumentType] # can't pop from a TypedDict
        self._data: GetReportReasonResponse = payload
        self.reports: list[Report] = reports
        self.total: int = payload.get("total", 0)
        self.limit: int = payload.get("limit", 0)
        self.offset: int = payload.get("offset", 0)
        super().__init__()

    def __repr__(self) -> str:
        return f"<ReportCollection reports={len(self.reports)} total={self.total} offset={self.offset} limit={self.limit}>"

    @property
    def items(self) -> list[Report]:
        """
        Returns the reports in the collection.

        Returns
        -------
        List[:class:`~hondana.Report`]
        """
        return self.reports


class UserReportCollection(BaseCollection["UserReport"]):
    """
    A collection object type to represent reports.

    Attributes
    ----------
    reports: List[:class:`~hondana.UserReport`]
        The reports returned from this collection.
    total: :class:`int`
        The total possible results with this query could return.
    offset: :class:`int`
        The offset used in this query.
    limit: :class:`int`
        The limit used in this query.
    """

    __slots__ = (
        "_data",
        "_http",
        "limit",
        "offset",
        "reports",
        "total",
    )

    def __init__(self, http: HTTPClient, payload: GetUserReportReasonResponse, reports: list[UserReport]) -> None:
        self._http: HTTPClient = http
        payload.pop("data", [])  # pyright: ignore[reportAssignmentType,reportArgumentType,reportUnknownArgumentType] # can't pop from a TypedDict
        self._data: GetUserReportReasonResponse = payload
        self.reports: list[UserReport] = reports
        self.total: int = payload.get("total", 0)
        self.limit: int = payload.get("limit", 0)
        self.offset: int = payload.get("offset", 0)
        super().__init__()

    def __repr__(self) -> str:
        return (
            f"<UserReportCollection reports={len(self.reports)} total={self.total} offset={self.offset} limit={self.limit}>"
        )

    @property
    def items(self) -> list[UserReport]:
        """
        Returns the reports in the collection.

        Returns
        -------
        List[:class:`~hondana.UserReport`]
        """
        return self.reports


class UserCollection(BaseCollection["User"]):
    """
    A collection object type to represent users.

    Attributes
    ----------
    users: List[:class:`~hondana.User`]
        The users returned from this collection.
    total: :class:`int`
        The total possible results with this query could return.
    offset: :class:`int`
        The offset used in this query.
    limit: :class:`int`
        The limit used in this query.
    """

    __slots__ = (
        "_data",
        "_http",
        "limit",
        "offset",
        "total",
        "users",
    )

    def __init__(self, http: HTTPClient, payload: GetMultiUserResponse, users: list[User]) -> None:
        self._http: HTTPClient = http
        payload.pop("data", [])  # pyright: ignore[reportAssignmentType,reportArgumentType,reportUnknownArgumentType] # can't pop from a TypedDict
        self._data: GetMultiUserResponse = payload
        self.users: list[User] = users
        self.total: int = payload.get("total", 0)
        self.limit: int = payload.get("limit", 0)
        self.offset: int = payload.get("offset", 0)
        super().__init__()

    def __repr__(self) -> str:
        return f"<UserCollection users={len(self.users)} total={self.total} offset={self.offset} limit={self.limit}>"

    @property
    def items(self) -> list[User]:
        """
        Returns the users in the collection.

        Returns
        -------
        List[:class:`~hondana.User`]
        """
        return self.users


class CustomListCollection(BaseCollection["CustomList"]):
    """
    A collection object type to represent custom lists.

    Attributes
    ----------
    lists: List[:class:`~hondana.CustomList`]
        The custom lists returned from this collection.
    total: :class:`int`
        The total possible results with this query could return.
    offset: :class:`int`
        The offset used in this query.
    limit: :class:`int`
        The limit used in this query.
    """

    __slots__ = (
        "_data",
        "_http",
        "limit",
        "lists",
        "offset",
        "total",
    )

    def __init__(self, http: HTTPClient, payload: GetMultiCustomListResponse, lists: list[CustomList]) -> None:
        self._http: HTTPClient = http
        payload.pop("data", [])  # pyright: ignore[reportAssignmentType,reportArgumentType,reportUnknownArgumentType] # can't pop from a TypedDict
        self._data: GetMultiCustomListResponse = payload
        self.lists: list[CustomList] = lists
        self.total: int = payload.get("total", 0)
        self.limit: int = payload.get("limit", 0)
        self.offset: int = payload.get("offset", 0)
        super().__init__()

    def __repr__(self) -> str:
        return f"<CustomListCollection lists={len(self.lists)} total={self.total} offset={self.offset} limit={self.limit}>"

    @property
    def items(self) -> list[CustomList]:
        """
        Returns the custom lists in the collection.

        Returns
        -------
        List[:class:`~hondana.CustomList`]
        """
        return self.lists


class LegacyMappingCollection(BaseCollection["LegacyItem"]):
    """
    A collection object type to represent custom lists.

    Attributes
    ----------
    legacy_mappings: List[:class:`~hondana.LegacyItem`]
        The legacy mappings returned from this collection.
    total: :class:`int`
        The total possible results with this query could return.
    offset: :class:`int`
        The offset used in this query.
    limit: :class:`int`
        The limit used in this query.
    """

    __slots__ = (
        "_data",
        "_http",
        "legacy_mappings",
        "limit",
        "offset",
        "total",
    )

    def __init__(self, http: HTTPClient, payload: GetLegacyMappingResponse, mappings: list[LegacyItem]) -> None:
        self._http: HTTPClient = http
        payload.pop("data", [])  # pyright: ignore[reportAssignmentType,reportArgumentType,reportUnknownArgumentType] # can't pop from a TypedDict
        self._data: GetLegacyMappingResponse = payload
        self.legacy_mappings: list[LegacyItem] = mappings
        self.total: int = payload.get("total", 0)
        self.limit: int = payload.get("limit", 0)
        self.offset: int = payload.get("offset", 0)
        super().__init__()

    def __repr__(self) -> str:
        return (
            "<LegacyMappingCollection "
            f"legacy_mappings={len(self.legacy_mappings)} "
            f"total={self.total} "
            f"offset={self.offset} "
            f"limit={self.limit}>"
        )

    @property
    def items(self) -> list[LegacyItem]:
        """
        Returns the legacy mappings in the collection.

        Returns
        -------
        List[:class:`~hondana.LegacyItem`]
        """
        return self.legacy_mappings


class ChapterReadHistoryCollection(BaseCollection["PreviouslyReadChapter"]):
    """
    A collection object type to represent chapter read history.

    Attributes
    ----------
    chapter_read_histories: List[:class:`~hondana.PreviouslyReadChapter`]
        The chapter read histories returned from this collection.
    total: :class:`int`
        The total possible results with this query could return.
    offset: :class:`int`
        The offset used in this query.
    limit: :class:`int`
        The limit used in this query.
    """

    __slots__ = (
        "_data",
        "_http",
        "chapter_read_histories",
        "limit",
        "offset",
        "total",
    )

    def __init__(self, http: HTTPClient, payload: ChapterReadHistoryResponse, history: list[PreviouslyReadChapter]) -> None:
        self._http: HTTPClient = http
        payload.pop("data", [])  # pyright: ignore[reportAssignmentType,reportArgumentType,reportUnknownArgumentType] # can't pop from a TypedDict
        self._data = payload
        self.history: list[PreviouslyReadChapter] = history
        self.total: int = payload.get("total", 0)
        self.limit: int = payload.get("limit", 0)
        self.offset: int = payload.get("offset", 0)
        super().__init__()

    def __repr__(self) -> str:
        return (
            "<ChapterReadHistoryCollection "
            f"history={len(self.history)} "
            f"total={self.total} "
            f"offset={self.offset} "
            f"limit={self.limit}>"
        )

    @property
    def items(self) -> list[PreviouslyReadChapter]:
        """
        Returns the legacy mappings in the collection.

        Returns
        -------
        List[:class:`~hondana.PreviouslyReadChapter`]
        """
        return self.history
