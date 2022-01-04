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
    "StatisticsRatingResponse",
    "BatchStatisticsRatingResponse",
    "StatisticsResponse",
    "BatchStatisticsResponse",
    "GetStatisticsResponse",
    "BatchGetStatisticsResponse",
    "PersonalMangaRatingsResponse",
    "GetPersonalMangaRatingsResponse",
)


class StatisticsRatingResponse(TypedDict):
    """
    average: :class:`float`

    distribution: List[:class:`int`]
    """

    average: float
    distribution: list[int]


class BatchStatisticsRatingResponse(TypedDict):
    """
    average: :class:`float`
    """

    average: float


class StatisticsResponse(TypedDict):
    """
    rating: :class:`~hondana.types.StatisticsRatingResponse`

    follows: :class:`int`
    """

    rating: StatisticsRatingResponse
    follows: int


class BatchStatisticsResponse(TypedDict):
    """
    rating: :class:`~hondana.types.BatchStatisticsRatingResponse`

    follows: :class:`int`
    """

    rating: BatchStatisticsRatingResponse
    follows: int


class GetStatisticsResponse(TypedDict):
    """
    result: Literal[``"ok"``]

    statistics: Dict[:class:`str`, :class:`~hondana.types.StatisticsResponse`]
    """

    result: Literal["ok"]
    statistics: dict[str, StatisticsResponse]


class BatchGetStatisticsResponse(TypedDict):
    """
    result: Literal[``"ok"``]

    statistics: Dict[:class:`str`, :class:`~hondana.types.BatchStatisticsResponse`]
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

    ratings: Dict[:class:`str`, :class:`~hondana.types.PersonalMangaRatingsResponse`]
    """

    result: Literal["ok"]
    ratings: dict[str, PersonalMangaRatingsResponse]
