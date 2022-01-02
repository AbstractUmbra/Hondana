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

from typing import TYPE_CHECKING, Literal, Optional, TypedDict


if TYPE_CHECKING:
    from .common import ContentRating, LocalisedString, PublicationDemographic
    from .relationship import RelationshipResponse
    from .tags import TagResponse


__all__ = (
    "MangaStatus",
    "MangaIncludes",
    "ReadingStatus",
    "MangaState",
    "MangaRelationType",
    "MangaRelated",
    "MangaLinks",
    "MangaAttributesResponse",
    "MangaRelationAttributesResponse",
    "MangaResponse",
    "GetMangaResponse",
    "MangaRelationCreateResponse",
    "MangaSearchResponse",
    "MangaRelation",
    "MangaRelationResponse",
    "ChaptersResponse",
    "VolumesAndChaptersResponse",
    "GetMangaVolumesAndChaptersResponse",
    "MangaReadMarkersResponse",
    "MangaGroupedReadMarkersResponse",
    "MangaSingleReadingStatusResponse",
    "MangaMultipleReadingStatusResponse",
)


MangaStatus = Literal["ongoing", "completed", "hiatus", "cancelled"]
MangaIncludes = Literal["author", "artist", "cover_art", "manga"]
ReadingStatus = Literal["reading", "on_hold", "plan_to_read", "dropped", "re_reading", "completed"]
MangaState = Literal["draft", "submitted", "published", "rejected"]
MangaRelationType = Literal[
    "monochrome",
    "main_story",
    "adapted_from",
    "based_on",
    "prequel",
    "side_story",
    "doujinshi",
    "same_franchise",
    "shared_universe",
    "sequel",
    "spin_off",
    "alternate_story",
    "preserialization",
    "colored",
    "serialization",
]
MangaRelated = Literal[
    "monochrome",
    "main_story",
    "adapted_from",
    "based_on",
    "prequel",
    "side_story",
    "doujinshi",
    "same_franchise",
    "shared_universe",
    "sequel",
    "spin_off",
    "alternate_story",
    "preserialization",
    "colored",
    "serialization",
]


class MangaLinks(TypedDict, total=False):
    """
    Please see here for more explicit info on these:-
        https://api.mangadex.org/docs.html#section/Static-data/Manga-links-data


    al: Optional[:class:`str`]

    ap: Optional[:class:`str`]

    bw: Optional[:class:`str`]

    mu: Optional[:class:`str`]

    nu: Optional[:class:`str`]

    kt: Optional[:class:`str`]

    amz: Optional[:class:`str`]

    ebj: Optional[:class:`str`]

    mal: Optional[:class:`str`]

    raw: Optional[:class:`str`]

    engtl: Optional[:class:`str`]
    """

    al: Optional[str]
    ap: Optional[str]
    bw: Optional[str]
    mu: Optional[str]
    nu: Optional[str]
    kt: Optional[str]
    amz: Optional[str]
    ebj: Optional[str]
    mal: Optional[str]
    raw: Optional[str]
    engtl: Optional[str]


class MangaAttributesResponse(TypedDict):
    """
    title: :class:`~hondana.types.LocalisedString`

    altTitle: List[:class:`~hondana.types.LocalisedString`]

    description: :class:`~hondana.types.LocalisedString`

    isLocked: :class:`bool`

    links: :class:`~hondana.types.MangaLinks`

    originalLanguage: :class:`str`

    lastVolume: Optional[:class:`str`]

    lastChapter: Optional[:class:`str`]

    publicationDemographic: Optional[:class:`~hondana.types.PublicationDemographic`]

    status: Optional[:class:`~hondana.types.MangaStatus`]

    year: Optional[:class:`int`]

    contentRating: Optional[:class:`~hondana.types.ContentRating`]

    tags: List[:class:`~hondana.types.TagResponse`]

    state: :class:`~hondana.types.MangaState`

    version: :class:`int`

    createdAt: :class:`str`

    updatedAt: :class:`str`

    isLocked: Optional[:class:`bool`]
        This key is optional
    """

    title: LocalisedString
    altTitles: list[LocalisedString]
    description: LocalisedString
    isLocked: bool
    links: MangaLinks
    originalLanguage: str
    lastVolume: Optional[str]
    lastChapter: Optional[str]
    publicationDemographic: Optional[PublicationDemographic]
    status: Optional[MangaStatus]
    year: Optional[int]
    contentRating: Optional[ContentRating]
    tags: list[TagResponse]
    state: MangaState
    version: int
    createdAt: str
    updatedAt: str


class MangaRelationAttributesResponse(TypedDict):
    """
    relation: :class:`~hondana.types.MangaRelationType`

    version: int
    """

    relation: MangaRelationType
    version: int


class _OptionalMangaResponse(TypedDict, total=False):
    relationships: list[RelationshipResponse]
    related: MangaRelationType


class MangaResponse(_OptionalMangaResponse):
    """
    id: :class:`str`

    type: Literal[``"manga"``]

    attributes: :class:`~hondana.types.MangaAttributesResponse`

    relationships: List[:class:`~hondana.types.RelationshipResponse`]
        This key is optional.

    related: :class:`~hondana.types.MangaRelationType`
        This key is optional.
    """

    id: str
    type: Literal["manga"]
    attributes: MangaAttributesResponse


class GetMangaResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    response: Literal[``"entity"``]

    data: :class:`~hondana.types.MangaResponse`
    """

    result: Literal["ok", "error"]
    response: Literal["entity"]
    data: MangaResponse


class MangaRelationCreateResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    response: Literal[``"entity"``]

    data: :class:`~hondana.types.MangaRelation`
    """

    result: Literal["ok", "error"]
    response: Literal["entity"]
    data: MangaRelation


class MangaSearchResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    response: Literal[``"collection"``]

    data: List[:class:`~hondana.types.MangaResponse`]

    limit: :class:`int`

    offset: :class:`int`

    total: :class:`int`
    """

    result: Literal["ok", "error"]
    response: Literal["collection"]
    data: list[MangaResponse]
    limit: int
    offset: int
    total: int


class MangaRelation(_OptionalMangaResponse):
    """
    id: :class:`str`

    type: Literal[``"manga_relation"``]

    attributes: :class:`~hondana.types.MangaRelationAttributesResponse`

    relationships: :class:`~hondana.types.RelationshipResponse`
        The key is optional.
    """

    id: str
    type: Literal["manga_relation"]
    attributes: MangaRelationAttributesResponse


class MangaRelationResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    response: Literal[``"collection"``]

    data: List[:class:`~hondana.types.MangaRelation`]

    limit: :class:`int`

    offset: :class:`int`

    total: :class:`int`
    """

    result: Literal["ok", "error"]
    response: Literal["collection"]
    data: list[MangaRelation]
    limit: int
    offset: int
    total: int


class ChaptersResponse(TypedDict):
    """
    chapter: :class:`str`

    count: :class:`str`
    """

    chapter: str
    count: str


class VolumesAndChaptersResponse(TypedDict, total=False):
    """
    chapters: Dict[:class:`str`, :class:`~hondana.types.ChaptersResponse`]

    count: :class:`int`

    volume: :class:`str`
    """

    chapters: dict[str, ChaptersResponse]
    count: int
    volume: str


class GetMangaVolumesAndChaptersResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    volumes: Optional[Dict[:class:`str`, :class:`~hondana.types.VolumesAndChaptersResponse`]]
    """

    result: Literal["ok", "error"]
    volumes: Optional[dict[str, VolumesAndChaptersResponse]]


class MangaReadMarkersResponse(TypedDict):
    """
    result: Literal[``"ok"``]

    data: List[:class:`str`]
    """

    result: Literal["ok"]
    data: list[str]


class MangaGroupedReadMarkersResponse(TypedDict):
    """
    result: Literal[``"ok"``]

    data: Dict[:class:`str`, List[:class:`str`]]
    """

    result: Literal["ok"]
    data: dict[str, list[str]]


class MangaSingleReadingStatusResponse(TypedDict):
    """
    result: Literal[``"ok"``]

    status: :class:`~hondana.types.ReadingStatus`
    """

    result: Literal["ok"]
    status: ReadingStatus


class MangaMultipleReadingStatusResponse(TypedDict):
    """
    result: Literal[``"ok"``]

    statuses: Dict[str, :class:`~hondana.types.ReadingStatus`]
        Mapping of [``manga_id``: :class:`~hondana.types.ReadingStatus`]
    """

    result: Literal["ok"]
    statuses: dict[str, ReadingStatus]
