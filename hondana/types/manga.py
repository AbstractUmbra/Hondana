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
    "MangaOrderQuery",
    "MangaLinks",
    "MangaAttributesResponse",
    "MangaResponse",
    "GetMangaResponse",
    "MangaSearchResponse",
    "ChaptersResponse",
    "VolumesAndChaptersResponse",
    "GetMangaVolumesAndChaptersResponse",
    "MangaReadMarkersResponse",
    "MangaGroupedReadMarkersResponse",
    "MangaReadingStatusResponse",
)


MangaStatus = Literal["ongoing", "completed", "hiatus", "cancelled"]
MangaIncludes = Literal["author", "artist", "cover_art"]
ReadingStatus = Literal["reading", "on_hold", "plan_to_read", "dropped", "re_reading", "completed"]


class MangaOrderQuery(TypedDict, total=False):
    volume: Literal["asc", "desc"]
    chapter: Literal["asc", "desc"]
    createdAt: Literal["asc", "desc"]
    updatedAt: Literal["asc", "desc"]
    latestUploadedChapter: Literal["asc", "desc"]


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


class MangaAttributesResponseOptional(TypedDict, total=False):
    """
    isLocked: :class:`bool`
    """

    isLocked: bool


class MangaAttributesResponse(MangaAttributesResponseOptional):
    """
    title: :class:`LocalisedString`

    altTitle: List[:class:`LocalisedString`]

    description: :class:`LocalisedString`

    links: :class:`MangaLinks`

    originalLanguage: :class:`str`

    lastVolume: Optional[:class:`str`]

    lastChapter: Optional[:class:`str`]

    publicationDemographic: Optional[:class:`PublicationDemographic`]

    status: Optional[:class:`MangaStatus`]

    year: Optional[:class:`int`]

    contentRating: Optional[:class:`ContentRating`]

    tags: List[:class:`TagResponse`]

    version: :class:`int`

    createdAt: :class:`str`

    updatedAt: :class:`str`

    isLocked: Optional[:class:`bool`]
        This key is optional
    """

    title: LocalisedString
    altTitles: list[LocalisedString]
    description: LocalisedString
    links: MangaLinks
    originalLanguage: str
    lastVolume: Optional[str]
    lastChapter: Optional[str]
    publicationDemographic: Optional[PublicationDemographic]
    status: Optional[MangaStatus]
    year: Optional[int]
    contentRating: Optional[ContentRating]
    tags: list[TagResponse]
    version: int
    createdAt: str
    updatedAt: str


class _OptionalMangaResponse(TypedDict, total=False):
    relationships: list[RelationshipResponse]


class MangaResponse(_OptionalMangaResponse):
    """
    id: :class:`str`

    type: Literal[``"manga"``]

    attributes: :class:`MangaAttributesResponse`

    relationships: List[:class:`RelationshipResponse`]
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


class MangaSearchResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    response: Literal[``"collection"``]

    data: List[:class:`MangaResponse`]

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


class ChaptersResponse(TypedDict):
    """
    chapter: :class:`str`

    count: :class:`str`
    """

    chapter: str
    count: str


class VolumesAndChaptersResponse(TypedDict, total=False):
    """
    chapters: Dict[:class:`str`, :class:`ChaptersResponse`]

    count: :class:`int`

    volume: :class:`str`
    """

    chapters: dict[str, ChaptersResponse]
    count: int
    volume: str


class GetMangaVolumesAndChaptersResponse(TypedDict):
    """
    result: Literal[``"ok"``, ``"error"``]

    volumes: Optional[Dict[:class:`str`, :class:`VolumesAndChaptersResponse`]]
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


class MangaReadingStatusResponse(TypedDict):
    """
    result: Literal[``"ok"``]

    status: :class:`ReadingStatus`
    """

    result: Literal["ok"]
    status: ReadingStatus
