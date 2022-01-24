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

from typing import TYPE_CHECKING, Literal


if TYPE_CHECKING:
    from .author import Author
    from .chapter import Chapter
    from .cover import Cover
    from .custom_list import CustomList
    from .http import HTTPClient
    from .legacy import LegacyItem
    from .manga import Manga, MangaRelation
    from .report import Report, UserReport
    from .scanlator_group import ScanlatorGroup
    from .types.author import GetMultiAuthorResponse
    from .types.chapter import GetMultiChapterResponse
    from .types.cover import GetMultiCoverResponse
    from .types.custom_list import GetMultiCustomListResponse
    from .types.legacy import GetLegacyMappingResponse
    from .types.manga import MangaRelationResponse, MangaSearchResponse
    from .types.report import GetReportReasonResponse, GetUserReportReasonResponse
    from .types.scanlator_group import GetMultiScanlationGroupResponse
    from .types.user import GetMultiUserResponse
    from .user import User

__all__ = (
    "MangaCollection",
    "MangaRelationCollection",
    "ChapterFeed",
    "AuthorCollection",
    "CoverCollection",
    "ScanlatorGroupCollection",
    "ReportCollection",
    "UserReportCollection",
    "UserCollection",
    "CustomListCollection",
    "LegacyMappingCollection",
)


class _Collection:
    def __init__(self) -> None:
        self.type: Literal["collection"] = "collection"


class MangaCollection(_Collection):
    """
    A collection object type to represent manga.

    Attributes
    -----------
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
        "_http",
        "_data",
        "manga",
        "total",
        "limit",
        "offset",
    )

    def __init__(self, http: HTTPClient, payload: MangaSearchResponse, manga: list[Manga]) -> None:
        self._http: HTTPClient = http
        payload.pop("data", [])
        self._data: MangaSearchResponse = payload
        self.manga: list[Manga] = manga
        self.total: int = payload.get("total", 0)
        self.offset: int = payload.get("offset", 0)
        self.limit: int = payload.get("limit", 0)
        super().__init__()

    def __repr__(self) -> str:
        return f"<MangaFeed manga={len(self.manga)} total={self.total} offset={self.offset} limit={self.limit}>"


class MangaRelationCollection(_Collection):
    """
    A collection object type to represent manga relations.

    Attributes
    -----------
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
        "_http",
        "_data",
        "relations",
        "total",
        "offset",
        "limit",
    )

    def __init__(self, http: HTTPClient, payload: MangaRelationResponse, relations: list[MangaRelation]) -> None:
        self._http: HTTPClient = http
        payload.pop("data", [])
        self._data = payload
        self.relations: list[MangaRelation] = relations
        self.total: int = payload.get("total", 0)
        self.offset: int = payload.get("offset", 0)
        self.limit: int = payload.get("limit", 0)
        super().__init__()


class ChapterFeed(_Collection):
    """
    A collection object type to represent chapters.

    Attributes
    -----------
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
        "_http",
        "_data",
        "chapters",
        "total",
        "limit",
        "offset",
    )

    def __init__(self, http: HTTPClient, payload: GetMultiChapterResponse, chapters: list[Chapter]) -> None:
        self._http: HTTPClient = http
        payload.pop("data", [])
        self._data: GetMultiChapterResponse = payload
        self.chapters: list[Chapter] = chapters
        self.total: int = payload.get("total", 0)
        self.offset: int = payload.get("offset", 0)
        self.limit: int = payload.get("limit", 0)
        super().__init__()

    def __repr__(self) -> str:
        return f"<ChapterFeed chapters={len(self.chapters)} total={self.total} offset={self.offset} limit={self.limit}>"


class AuthorCollection:
    """
    A collection object type to represent authors.

    Attributes
    -----------
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
        "_http",
        "_data",
        "authors",
        "total",
        "limit",
        "offset",
    )

    def __init__(self, http: HTTPClient, payload: GetMultiAuthorResponse, authors: list[Author]) -> None:
        self._http: HTTPClient = http
        payload.pop("data", [])
        self._data: GetMultiAuthorResponse = payload
        self.authors: list[Author] = authors
        self.total: int = payload.get("total", 0)
        self.offset: int = payload.get("offset", 0)
        self.limit: int = payload.get("limit", 0)
        super().__init__()

    def __repr__(self) -> str:
        return f"<ArtistCollection authors={len(self.authors)} total={self.total} offset={self.offset} limit={self.limit}>"


class CoverCollection(_Collection):
    """
    A collection object type to represent covers.

    Attributes
    -----------
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
        "_http",
        "_data",
        "covers",
        "total",
        "limit",
        "offset",
    )

    def __init__(self, http: HTTPClient, payload: GetMultiCoverResponse, covers: list[Cover]) -> None:
        self._http: HTTPClient = http
        payload.pop("data", [])
        self._data: GetMultiCoverResponse = payload
        self.covers: list[Cover] = covers
        self.total: int = payload.get("total", 0)
        self.offset: int = payload.get("offset", 0)
        self.limit: int = payload.get("limit", 0)
        super().__init__()

    def __repr__(self) -> str:
        return f"<CoverCollection covers={len(self.covers)} total={self.total} offset={self.offset} limit={self.limit}>"


class ScanlatorGroupCollection(_Collection):
    """
    A collection object type to represent scanlator groups.

    Attributes
    -----------
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
        "_http",
        "_data",
        "groups",
        "total",
        "limit",
        "offset",
    )

    def __init__(self, http: HTTPClient, payload: GetMultiScanlationGroupResponse, groups: list[ScanlatorGroup]) -> None:
        self._http: HTTPClient = http
        payload.pop("data", [])
        self._data: GetMultiScanlationGroupResponse = payload
        self.groups: list[ScanlatorGroup] = groups
        self.total: int = payload.get("total", 0)
        self.limit: int = payload.get("limit", 0)
        self.offset: int = payload.get("offset", 0)
        super().__init__()

    def __repr__(self) -> str:
        return f"<ScanlatorGroupCollection groups={len(self.groups)} total={self.total} offset={self.offset} limit={self.limit}>"


class ReportCollection(_Collection):
    """
    A collection object type to represent reports.

    Attributes
    -----------
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
        "_http",
        "_data",
        "reports",
        "total",
        "limit",
        "offset",
    )

    def __init__(self, http: HTTPClient, payload: GetReportReasonResponse, reports: list[Report]) -> None:
        self._http: HTTPClient = http
        payload.pop("data", [])
        self._data: GetReportReasonResponse = payload
        self.reports: list[Report] = reports
        self.total: int = payload.get("total", 0)
        self.limit: int = payload.get("limit", 0)
        self.offset: int = payload.get("offset", 0)
        super().__init__()

    def __repr__(self) -> str:
        return f"<ReportCollection reports={len(self.reports)} total={self.total} offset={self.offset} limit={self.limit}>"


class UserReportCollection(_Collection):
    """
    A collection object type to represent reports.

    Attributes
    -----------
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
        "_http",
        "_data",
        "reports",
        "total",
        "limit",
        "offset",
    )

    def __init__(self, http: HTTPClient, payload: GetUserReportReasonResponse, reports: list[UserReport]) -> None:
        self._http: HTTPClient = http
        payload.pop("data", [])
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


class UserCollection(_Collection):
    """
    A collection object type to represent users.

    Attributes
    -----------
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
        "_http",
        "_data",
        "users",
        "total",
        "limit",
        "offset",
    )

    def __init__(self, http: HTTPClient, payload: GetMultiUserResponse, users: list[User]) -> None:
        self._http: HTTPClient = http
        payload.pop("data", [])
        self._data: GetMultiUserResponse = payload
        self.users: list[User] = users
        self.total: int = payload.get("total", 0)
        self.limit: int = payload.get("limit", 0)
        self.offset: int = payload.get("offset", 0)
        super().__init__()

    def __repr__(self) -> str:
        return f"<UserCollection users={len(self.users)} total={self.total} offset={self.offset} limit={self.limit}>"


class CustomListCollection(_Collection):
    """
    A collection object type to represent custom lists.

    Attributes
    -----------
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
        "_http",
        "_data",
        "lists",
        "total",
        "limit",
        "offset",
    )

    def __init__(self, http: HTTPClient, payload: GetMultiCustomListResponse, lists: list[CustomList]) -> None:
        self._http: HTTPClient = http
        payload.pop("data", [])
        self._data: GetMultiCustomListResponse = payload
        self.lists: list[CustomList] = lists
        self.total: int = payload.get("total", 0)
        self.limit: int = payload.get("limit", 0)
        self.offset: int = payload.get("offset", 0)
        super().__init__()

    def __repr__(self) -> str:
        return f"<CustomListCollection lists={len(self.lists)} total={self.total} offset={self.offset} limit={self.limit}>"


class LegacyMappingCollection(_Collection):
    """
    A collection object type to represent custom lists.

    Attributes
    -----------
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
        "_http",
        "_data",
        "legacy_mappings",
        "total",
        "limit",
        "offset",
    )

    def __init__(self, http: HTTPClient, payload: GetLegacyMappingResponse, mappings: list[LegacyItem]) -> None:
        self._http: HTTPClient = http
        payload.pop("data", [])
        self._data: GetLegacyMappingResponse = payload
        self.legacy_mappings: list[LegacyItem] = mappings
        self.total: int = payload.get("total", 0)
        self.limit: int = payload.get("limit", 0)
        self.offset: int = payload.get("offset", 0)
        super().__init__()

    def __repr__(self) -> str:
        return f"<LegacyMappingCollection legacy_mappings={len(self.legacy_mappings)} total={self.total} offset={self.offset} limit={self.limit}>"
