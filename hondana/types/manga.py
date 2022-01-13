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
    from .common import LocalisedString
    from .relationship import RelationshipResponse
    from .tags import TagResponse

from ..enums import ContentRating as _ContentRating
from ..enums import MangaRelationType as _MangaRelationType
from ..enums import MangaState as _MangaState
from ..enums import MangaStatus as _MangaStatus
from ..enums import PublicationDemographic as _PublicationDemographic
from ..enums import ReadingStatus as _ReadingStatus


__all__ = (
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

    publicationDemographic: Optional[:class:`~hondana.PublicationDemographic`]

    status: Optional[:class:`~hondana.MangaStatus`]

    year: Optional[:class:`int`]

    contentRating: Optional[:class:`~hondana.ContentRating`]

    tags: List[:class:`~hondana.types.TagResponse`]

    state: :class:`~hondana.MangaState`

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
    publicationDemographic: Optional[_PublicationDemographic]
    status: Optional[_MangaStatus]
    year: Optional[int]
    contentRating: Optional[_ContentRating]
    tags: list[TagResponse]
    state: _MangaState
    version: int
    createdAt: str
    updatedAt: str


class MangaRelationAttributesResponse(TypedDict):
    """
    relation: :class:`~hondana.MangaRelationType`

    version: int
    """

    relation: _MangaRelationType
    version: int


class _OptionalMangaResponse(TypedDict, total=False):
    relationships: list[RelationshipResponse]
    related: _MangaRelationType


class MangaResponse(_OptionalMangaResponse):
    """
    id: :class:`str`

    type: Literal[``"manga"``]

    attributes: :class:`~hondana.types.MangaAttributesResponse`

    relationships: List[:class:`~hondana.types.RelationshipResponse`]
        This key is optional.

    related: :class:`~hondana.MangaRelationType`
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

    status: :class:`~hondana.ReadingStatus`
    """

    result: Literal["ok"]
    status: _ReadingStatus


class MangaMultipleReadingStatusResponse(TypedDict):
    """
    result: Literal[``"ok"``]

    statuses: Dict[str, :class:`~hondana.ReadingStatus`]
        Mapping of [``manga_id``: :class:`~hondana.ReadingStatus`]
    """

    result: Literal["ok"]
    statuses: dict[str, _ReadingStatus]
