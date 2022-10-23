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

from typing_extensions import NotRequired


if TYPE_CHECKING:
    from .common import LocalizedString, LanguageCode
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
        anilist key

    ap: Optional[:class:`str`]
        animeplanet key

    bw: Optional[:class:`str`]
        bookwalker.jp key

    mu: Optional[:class:`str`]
        mangaupdates key

    nu: Optional[:class:`str`]
        novelupdates key

    kt: Optional[:class:`str`]
        kitsu.io key

    amz: Optional[:class:`str`]
        amazon key

    ebj: Optional[:class:`str`]
        ebookjapan key

    mal: Optional[:class:`str`]
        myanimelist key

    cdj: Optional[:class:`str`]
        cdjapan key

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
    cdj: Optional[str]
    raw: Optional[str]
    engtl: Optional[str]


class MangaAttributesResponse(TypedDict):
    """
    title: :class:`~hondana.types.common.LocalizedString`

    altTitle: List[:class:`~hondana.types.common.LocalizedString`]

    description: :class:`~hondana.types.common.LocalizedString`

    isLocked: :class:`bool`

    links: :class:`~hondana.types.manga.MangaLinks`

    originalLanguage: :class:`str`

    lastVolume: Optional[:class:`str`]

    lastChapter: Optional[:class:`str`]

    publicationDemographic: Optional[:class:`~hondana.PublicationDemographic`]

    status: :class:`~hondana.MangaStatus`

    year: Optional[:class:`int`]

    contentRating: Optional[:class:`~hondana.ContentRating`]

    chapterNumbersResetOnNewVolume: :class:`bool`

    latestUploadedChapter: :class:`str`

    availableTranslatedLanguages: List[:class:`~hondana.types.common.LanguageCode`]

    tags: List[:class:`~hondana.types.tags.TagResponse`]

    state: :class:`~hondana.MangaState`

    version: :class:`int`

    createdAt: :class:`str`

    updatedAt: :class:`str`

    isLocked: Optional[:class:`bool`]
        This key is optional
    """

    title: LocalizedString
    altTitles: list[LocalizedString]
    description: LocalizedString
    isLocked: bool
    links: MangaLinks
    originalLanguage: str
    lastVolume: Optional[str]
    lastChapter: Optional[str]
    publicationDemographic: Optional[_PublicationDemographic]
    status: _MangaStatus
    year: Optional[int]
    contentRating: Optional[_ContentRating]
    chapterNumbersResetOnNewVolume: bool
    latestUploadedChapter: str
    availableTranslatedLanguages: list[LanguageCode]
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


class MangaResponse(TypedDict):
    """
    id: :class:`str`

    type: Literal[``"manga"``]

    attributes: :class:`~hondana.types.manga.MangaAttributesResponse`

    relationships: List[:class:`~hondana.types.relationship.RelationshipResponse`]
        This key is optional, in the event this payload is gotten from the "relationships" of another object.

        This key can contain minimal or full data depending on the ``includes[]`` parameter of its request.
        See here for more info: https://api.mangadex.org/docs.html#section/Reference-Expansion

    related: :class:`~hondana.MangaRelationType`
        This key is optional.
    """

    id: str
    type: Literal["manga"]
    attributes: MangaAttributesResponse
    relationships: NotRequired[list[RelationshipResponse]]
    related: NotRequired[_MangaRelationType]


class GetMangaResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    response: Literal[``"entity"``]

    data: :class:`~hondana.types.manga.MangaResponse`
    """

    result: Literal["ok", "error"]
    response: Literal["entity"]
    data: MangaResponse


class MangaRelationCreateResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    response: Literal[``"entity"``]

    data: :class:`~hondana.types.manga.MangaRelation`
    """

    result: Literal["ok", "error"]
    response: Literal["entity"]
    data: MangaRelation


class MangaSearchResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    response: Literal[``"collection"``]

    data: List[:class:`~hondana.types.manga.MangaResponse`]

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


class MangaRelation(TypedDict):
    """
    id: :class:`str`

    type: Literal[``"manga_relation"``]

    attributes: :class:`~hondana.types.manga.MangaRelationAttributesResponse`

    relationships: List[:class:`~hondana.types.relationship.RelationshipResponse`]
        This key is optional, in the event this payload is gotten from the "relationships" of another object.

        This key can contain minimal or full data depending on the ``includes[]`` parameter of its request.
        See here for more info: https://api.mangadex.org/docs.html#section/Reference-Expansion

    related: :class:`~hondana.MangaRelationType`
        This key is optional.
    """

    id: str
    type: Literal["manga_relation"]
    attributes: MangaRelationAttributesResponse
    relationships: NotRequired[list[RelationshipResponse]]
    related: NotRequired[_MangaRelationType]


class MangaRelationResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    response: Literal[``"collection"``]

    data: List[:class:`~hondana.types.manga.MangaRelation`]

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
    chapters: Dict[:class:`str`, :class:`~hondana.types.manga.ChaptersResponse`]

    count: :class:`int`

    volume: :class:`str`
    """

    chapters: dict[str, ChaptersResponse]
    count: int
    volume: str


class GetMangaVolumesAndChaptersResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    volumes: Optional[Dict[:class:`str`, :class:`~hondana.types.manga.VolumesAndChaptersResponse`]]
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
        Mapping of [``manga_id``: :class:`~hondana.ReadingStatus` value]
    """

    result: Literal["ok"]
    statuses: dict[str, _ReadingStatus]
