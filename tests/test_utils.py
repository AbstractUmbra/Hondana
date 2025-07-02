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
import pathlib
import random
import zoneinfo
from typing import TYPE_CHECKING, TypeVar

import pytest
from multidict import MultiDict

from hondana.utils import (
    MISSING,
    RelationshipResolver,
    Route,
    as_chunks,
    calculate_limits,
    clean_isoformat,
    delta_to_iso,
    iso_to_delta,
    php_query_builder,
    to_camel_case,
    to_snake_case,
    upload_file_sort,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

    from hondana.utils import MANGADEX_QUERY_PARAM_TYPE


T = TypeVar("T")


multidict_one = MultiDict[str]()
multidict_one.add("order[publishAt]", "desc")
multidict_one.add("translatedLanguages[]", "en")
multidict_one.add("translatedLanguages[]", "jp")

multidict_two = MultiDict[str]()
multidict_two.add("param[]", "a")
multidict_two.add("param[]", "b")
multidict_two.add("param[]", "c")
multidict_two.add("includes[]", "test")
multidict_two.add("includes[]", "mark")

multidict_three = MultiDict[str | int]()
multidict_three.add("sorted", "true")
multidict_three.add("value", 1)

multidict_four = MultiDict[str | int]()
multidict_four.add("sorted[]", 1)
multidict_four.add("sorted[]", 2)
multidict_four.add("includes[]", 1)
multidict_four.add("includes[]", 2)
multidict_four.add("includes[]", 3)
multidict_four.add("createdAt", "null")
multidict_four.add("value[query]", 7)


class TestUtils:
    def test_missing(self) -> None:
        assert MISSING is not None
        assert not bool(MISSING)

    @pytest.mark.parametrize(
        "route, match",
        [
            (
                Route("GET", "/chapter/{chapter_id}", chapter_id="abcd", authenticate=False),
                ("GET", "/chapter/abcd", False),
            ),
            (
                Route("POST", "/manga/{manga_id}", manga_id="some_manga", authenticate=True),
                ("POST", "/manga/some_manga", True),
            ),
        ],
    )
    def test_route(self, route: Route, match: tuple[str, str, bool]) -> None:
        verb, path, auth = match

        assert route.verb == verb

        assert route.url.scheme == "https"
        assert route.url.host == "api.mangadex.org"
        assert route.url.path == path

        assert route.auth is auth

    @pytest.mark.parametrize(
        "source, chunk_size, chunked",
        [
            ([1, 2, 3, 4, 5, 6], 2, [[1, 2], [3, 4], [5, 6]]),
            ([1, 2, 3, 4, 5, 6], 3, [[1, 2, 3], [4, 5, 6]]),
            ([1, 2, 3, 4, 5, 6], 4, [[1, 2, 3, 4], [5, 6]]),
            ([1, 2, 3, 4, 5, 6], 5, [[1, 2, 3, 4, 5], [6]]),
        ],
    )
    def test_as_chunks(self, source: Iterable[T], chunk_size: int, chunked: Iterable[Iterable[T]]) -> None:
        assert list(as_chunks(source, chunk_size)) == chunked

    @pytest.mark.parametrize(
        "limit, offset, max_limit, output",
        [
            (100, 9980, 100, (20, 9980)),
            (10, 9999, 100, (1, 9999)),
            (100, 5000, 100, (100, 5000)),
            (100, 5000, 10, (10, 5000)),
        ],
    )
    def test_calculate_limit(self, limit: int, offset: int, max_limit: int, output: tuple[int, int]) -> None:
        assert calculate_limits(limit, offset, max_limit=max_limit) == output

    @pytest.mark.parametrize(
        "input_, output",
        [
            (datetime.timedelta(hours=3, minutes=12), "T3H12M"),
            (datetime.timedelta(days=12, hours=13, minutes=27, seconds=12), "P5D1WT13H27M12S"),
            (datetime.timedelta(days=7, hours=7, minutes=13, seconds=58), "P1WT7H13M58S"),
        ],
    )
    def test_delta_to_iso(self, input_: datetime.timedelta, output: str) -> None:
        assert delta_to_iso(input_) == output

    @pytest.mark.parametrize(
        "input_, output",
        [
            ("T3H12M", datetime.timedelta(seconds=11520)),
            ("P5D1WT13H27M12S", datetime.timedelta(days=12, seconds=48432)),
            ("P1WT7H13M58S", datetime.timedelta(days=7, seconds=26038)),
        ],
    )
    def test_iso_to_delta(self, input_: str, output: datetime.timedelta) -> None:
        assert iso_to_delta(input_) == output

    @pytest.mark.parametrize(
        "input_, output",
        [
            (
                {"order": {"publishAt": "desc"}, "translatedLanguages": ["en", "jp"]},
                multidict_one,
            ),
            (
                {"param": ["a", "b", "c"], "includes": ["test", "mark"]},
                multidict_two,
            ),
            ({"sorted": True, "value": 1}, multidict_three),
            (
                {"sorted": [1, 2], "includes": [1, 2, 3], "createdAt": None, "value": {"query": 7}},
                multidict_four,
            ),
        ],
    )
    def test_query_builder(
        self,
        input_: MANGADEX_QUERY_PARAM_TYPE,
        output: MultiDict[str | int],
    ) -> None:
        assert php_query_builder(input_) == output

    @pytest.mark.parametrize(
        "input_, output",
        [("some_value", "someValue"), ("some_other_value", "someOtherValue"), ("manga_or_chapter", "mangaOrChapter")],
    )
    def test_to_camel_case(self, input_: str, output: str) -> None:
        assert to_camel_case(input_) == output

    @pytest.mark.parametrize(
        "input_, output",
        [("someValue", "some_value"), ("someOtherValue", "some_other_value"), ("mangaOrChapter", "manga_or_chapter")],
    )
    def test_to_snake_case(self, input_: str, output: str) -> None:
        assert to_snake_case(input_) == output

    @pytest.mark.parametrize(
        "input_, output",
        [
            (
                [{"type": "test", "hello": "goodbye"}],
                [{"type": "test", "hello": "goodbye"}],
            ),
            (
                [{"type": "bleh", "hello": "goodbye"}, {"type": "test", "hello": "hello"}],
                [{"type": "test", "hello": "hello"}],
            ),
            (
                [{"type": "test", "pass": "mark", "something": "anything"}, {"type": "bad"}],
                [{"type": "test", "pass": "mark", "something": "anything"}],
            ),
        ],
    )
    def test_relationship_finder(self, input_: list[dict[str, str]], output: list[dict[str, str]] | dict[str, str]) -> None:
        ret = RelationshipResolver[dict[str, str]](input_, "test").resolve()  # type: ignore[reportArgumentType] # we lie here for the test case

        assert ret is not None

        assert ret == output

    @pytest.mark.parametrize(
        "input_, output",
        [
            (
                datetime.datetime(
                    year=2022,
                    month=3,
                    day=19,
                    hour=12,
                    minute=0,
                    second=0,
                    microsecond=0,
                    tzinfo=datetime.UTC,
                ),
                "2022-03-19T12:00:00",
            ),
            (
                datetime.datetime(
                    year=2022,
                    month=3,
                    day=19,
                    hour=12,
                    minute=0,
                    second=0,
                    microsecond=0,
                    tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo"),
                ),
                "2022-03-19T03:00:00",
            ),
        ],
    )
    def test_isoformatter(self, input_: datetime.datetime, output: str) -> None:
        assert clean_isoformat(input_) == output

    @pytest.mark.parametrize(
        "input_, output",
        [
            (
                random.sample([pathlib.Path(f"{x}.png") for x in range(1, 15)], 14),
                [
                    pathlib.Path("1.png"),
                    pathlib.Path("2.png"),
                    pathlib.Path("3.png"),
                    pathlib.Path("4.png"),
                    pathlib.Path("5.png"),
                    pathlib.Path("6.png"),
                    pathlib.Path("7.png"),
                    pathlib.Path("8.png"),
                    pathlib.Path("9.png"),
                    pathlib.Path("10.png"),
                    pathlib.Path("11.png"),
                    pathlib.Path("12.png"),
                    pathlib.Path("13.png"),
                    pathlib.Path("14.png"),
                ],
            ),
            (
                [pathlib.Path("1.png"), pathlib.Path("11.png"), pathlib.Path("2.png"), pathlib.Path("22.png")],
                [pathlib.Path("1.png"), pathlib.Path("2.png"), pathlib.Path("11.png"), pathlib.Path("22.png")],
            ),
        ],
    )
    def test_path_sorter(self, input_: list[pathlib.Path], output: list[pathlib.Path]) -> None:
        assert sorted(input_, key=upload_file_sort) == output
