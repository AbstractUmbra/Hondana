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

from typing import Literal, TypedDict

__all__ = (
    "BatchGetStatisticsResponse",
    "BatchStatisticsRatingResponse",
    "BatchStatisticsResponse",
    "CommentMetaData",
    "GetCommentsStatisticsResponse",
    "GetMangaStatisticsResponse",
    "GetPersonalMangaRatingsResponse",
    "MangaStatisticsResponse",
    "PersonalMangaRatingsResponse",
    "StatisticsRatingResponse",
)


class StatisticsRatingResponse(TypedDict):
    """
    average: Optional[:class:`float`]

    bayesian: Optional[:class:`float`]

    distribution: Dict[:class:`str`, :class:`int`]
    """

    average: float | None
    bayesian: float | None
    distribution: dict[str, int]


class BatchStatisticsRatingResponse(TypedDict):
    """
    average: :class:`float`

    bayesian: :class:`float`
    """

    average: float
    bayesian: float


class MangaStatisticsResponse(TypedDict):
    """
    rating: :class:`~hondana.types_.statistics.StatisticsRatingResponse`

    follows: :class:`int`
    """

    comments: CommentMetaData | None
    rating: StatisticsRatingResponse
    follows: int
    unavailableChapterCount: int


class BatchStatisticsResponse(TypedDict):
    """
    rating: :class:`~hondana.types_.statistics.BatchStatisticsRatingResponse`

    follows: :class:`int`
    """

    rating: BatchStatisticsRatingResponse
    follows: int


class GetMangaStatisticsResponse(TypedDict):
    """
    result: Literal[``"ok"``]

    statistics: Dict[:class:`str`, :class:`~hondana.types_.statistics.StatisticsRatingResponse`]
    """

    result: Literal["ok"]
    statistics: dict[str, MangaStatisticsResponse]


class BatchGetStatisticsResponse(TypedDict):
    """
    result: Literal[``"ok"``]

    statistics: Dict[:class:`str`, :class:`~hondana.types_.statistics.BatchStatisticsResponse`]
    """

    result: Literal["ok"]
    statistics: dict[str, BatchStatisticsResponse]


class PersonalMangaRatingsResponse(TypedDict):
    """
    rating: :class:`int`

    createdAt: :class:`str`
    """

    rating: int
    createdAt: str


class GetPersonalMangaRatingsResponse(TypedDict):
    """
    result: Literal[``"ok"``]

    ratings: Dict[:class:`str`, :class:`~hondana.types_.statistics.PersonalMangaRatingsResponse`]
    """

    result: Literal["ok"]
    ratings: dict[str, PersonalMangaRatingsResponse]


class CommentMetaData(TypedDict):
    """
    threadId: :class:`int`

    repliesCount: :class:`int`
    """

    threadId: int
    repliesCount: int


class StatisticsCommentsResponse(TypedDict):
    """
    comments: Optional[:class:`~hondana.types_.statistics.CommentMetaData`]
    """

    comments: CommentMetaData | None


class GetCommentsStatisticsResponse(TypedDict):
    """
    result: Literal[``"ok"``]

    statistics: Dict[:class:`str`, :class:`~hondana.types_.statistics.StatisticsCommentsResponse`]
    """

    result: Literal["ok"]
    statistics: dict[str, StatisticsCommentsResponse]
