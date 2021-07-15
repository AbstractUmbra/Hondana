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

from typing import Literal, Optional, TypedDict

from .relationship import RelationshipResponse
from .tags import TagResponse


__all__ = (
    "MangaLinks",
    "MangaAttributesResponse",
    "MangaResponse",
    "ViewMangaResponse",
    "MangaSearchResponse",
    "MangaStatus",
    "PublicationDemographic",
    "ContentRating",
    "MangaIncludes",
)


MangaStatus = Literal["ongoing", "completed", "hiatus", "cancelled"]
PublicationDemographic = Literal["shounen", "shoujo", "josei", "seinen"]
ContentRating = Literal["safe", "suggestive", "erotica", "pornographic"]
MangaIncludes = list[Literal["author", "artist", "cover_art"]]


class MangaLinks(TypedDict, total=False):
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
    isLocked: bool


class MangaAttributesResponse(MangaAttributesResponseOptional):
    title: dict[str, str]
    altTitles: list[dict[str, str]]
    description: dict[str, str]
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


class MangaResponse(TypedDict):
    id: str
    type: Literal["manga"]
    attributes: MangaAttributesResponse


class ViewMangaResponse(TypedDict):
    result: Literal["ok", "error"]
    data: MangaResponse
    relationships: list[RelationshipResponse]


class MangaSearchResponse(TypedDict):
    results: list[ViewMangaResponse]
    limit: int
    offset: int
    total: int
