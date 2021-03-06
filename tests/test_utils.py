from __future__ import annotations

import datetime
import pathlib
import random
import zoneinfo
from typing import Iterable, Mapping, Optional, TypeVar, Union

import pytest

from hondana.utils import (
    MISSING,
    CustomRoute,
    Route,
    as_chunks,
    calculate_limits,
    clean_isoformat,
    delta_to_iso,
    iso_to_delta,
    php_query_builder,
    relationship_finder,
    to_camel_case,
    to_snake_case,
    upload_file_sort,
)


T = TypeVar("T")


class TestUtils:
    def test_missing(self):
        assert MISSING is not None
        assert not bool(MISSING)

    def test_custom_route(self):
        route = CustomRoute("GET", "https://uploads.mangadex.org", "/chapter/{chapter_id}", chapter_id="abcd")

        assert route.base == "https://uploads.mangadex.org"
        assert route.verb == "GET"
        assert route.path == "/chapter/{chapter_id}"
        assert route.url == "https://uploads.mangadex.org/chapter/abcd"

    def test_route(self):
        route = Route("GET", "/chapter/{chapter_id}", chapter_id="efgh")

        assert route.verb == "GET"
        assert route.path == "/chapter/{chapter_id}"
        assert route.url == "https://api.mangadex.org/chapter/efgh"

    @pytest.mark.parametrize(
        ("source", "chunk_size", "chunked"),
        [
            ([1, 2, 3, 4, 5, 6], 2, [[1, 2], [3, 4], [5, 6]]),
            ([1, 2, 3, 4, 5, 6], 3, [[1, 2, 3], [4, 5, 6]]),
            ([1, 2, 3, 4, 5, 6], 4, [[1, 2, 3, 4], [5, 6]]),
            ([1, 2, 3, 4, 5, 6], 5, [[1, 2, 3, 4, 5], [6]]),
        ],
    )
    def test_as_chunks(self, source: Iterable[T], chunk_size: int, chunked: Iterable[Iterable[T]]):
        assert list(as_chunks(source, chunk_size)) == chunked

    @pytest.mark.parametrize(
        ("limit", "offset", "max_limit", "output"),
        [
            (100, 9980, 100, (20, 9980)),
            (10, 9999, 100, (1, 9999)),
            (100, 5000, 100, (100, 5000)),
            (100, 5000, 10, (10, 5000)),
        ],
    )
    def test_calculate_limit(self, limit: int, offset: int, max_limit: int, output: tuple[int, int]):
        assert calculate_limits(limit, offset, max_limit=max_limit) == output

    @pytest.mark.parametrize(
        ("input", "output"),
        [
            (datetime.timedelta(hours=3, minutes=12), "T3H12M"),
            (datetime.timedelta(days=12, hours=13, minutes=27, seconds=12), "P5D1WT13H27M12S"),
            (datetime.timedelta(days=7, hours=7, minutes=13, seconds=58), "P1WT7H13M58S"),
        ],
    )
    def test_delta_to_iso(self, input: datetime.timedelta, output: str):
        assert delta_to_iso(input) == output

    @pytest.mark.parametrize(
        ("input", "output"),
        [
            ("T3H12M", datetime.timedelta(seconds=11520)),
            ("P5D1WT13H27M12S", datetime.timedelta(days=12, seconds=48432)),
            ("P1WT7H13M58S", datetime.timedelta(days=7, seconds=26038)),
        ],
    )
    def test_iso_to_delta(self, input: str, output: datetime.timedelta):
        assert iso_to_delta(input) == output

    @pytest.mark.parametrize(
        ("input", "output"),
        [
            (
                {"order": {"publishAt": "desc"}, "translatedLanguages": ["en", "jp"]},
                "order[publishAt]=desc&translatedLanguages[]=en&translatedLanguages[]=jp",
            ),
            (
                {"param": ["a", "b", "c"], "includes": ["test", "mark"]},
                "param[]=a&param[]=b&param[]=c&includes[]=test&includes[]=mark",
            ),
            ({"sorted": True, "value": 1}, "sorted=true&value=1"),
            (
                {"sorted": [1, 2], "includes": [1, 2, 3], "createdAt": None, "value": {"query": 7}},
                "sorted[]=1&sorted[]=2&includes[]=1&includes[]=2&includes[]=3&createdAt=null&value[query]=7",
            ),
        ],
    )
    def test_query_builder(
        self, input: Mapping[str, Optional[Union[str, int, bool, list[str], dict[str, str]]]], output: str
    ):
        assert php_query_builder(input) == output

    @pytest.mark.parametrize(
        ("input", "output"),
        [("some_value", "someValue"), ("some_other_value", "someOtherValue"), ("manga_or_chapter", "mangaOrChapter")],
    )
    def test_to_camel_case(self, input: str, output: str):
        assert to_camel_case(input) == output

    @pytest.mark.parametrize(
        ("input", "output"),
        [("someValue", "some_value"), ("someOtherValue", "some_other_value"), ("mangaOrChapter", "manga_or_chapter")],
    )
    def test_to_snake_case(self, input: str, output: str):
        assert to_snake_case(input) == output

    @pytest.mark.parametrize(
        ("input", "output", "limit"),
        [
            ([{"type": "test", "hello": "goodbye"}], [{"type": "test", "hello": "goodbye"}], None),
            (
                [{"type": "bleh", "hello": "goodbye"}, {"type": "test", "hello": "hello"}],
                [{"type": "test", "hello": "hello"}],
                None,
            ),
            (
                [{"type": "test", "pass": "mark", "something": "anything"}, {"type": "bad"}],
                [{"type": "test", "pass": "mark", "something": "anything"}],
                None,
            ),
            (
                [{"type": "test", "pass": "mark", "something": "anything"}, {"type": "bad"}],
                {"type": "test", "pass": "mark", "something": "anything"},
                1,
            ),
        ],
    )
    def test_relationship_finder(
        self, input: list[dict[str, str]], output: Union[list[dict[str, str]], dict[str, str]], limit: Optional[int]
    ):
        ret = relationship_finder(input, "test", limit=limit)  # type: ignore # the types here all fail but this is only a test.

        assert ret is not None

        assert ret == output

    @pytest.mark.parametrize(
        ("input", "output"),
        [
            (
                datetime.datetime(
                    year=2022, month=3, day=19, hour=12, minute=0, second=0, microsecond=0, tzinfo=datetime.timezone.utc
                ),
                "2022-03-19T12:00:00",
            ),
            (
                datetime.datetime(year=2022, month=3, day=19, hour=12, minute=0, second=0, microsecond=0),
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
    def test_isoformatter(self, input: datetime.datetime, output: str):
        assert clean_isoformat(input) == output

    @pytest.mark.parametrize(
        ("input", "output"),
        [
            (
                random.sample([pathlib.Path(f"{x}.png") for x in range(1, 15)], 14),
                [
                    pathlib.Path(f"1.png"),
                    pathlib.Path(f"2.png"),
                    pathlib.Path(f"3.png"),
                    pathlib.Path(f"4.png"),
                    pathlib.Path(f"5.png"),
                    pathlib.Path(f"6.png"),
                    pathlib.Path(f"7.png"),
                    pathlib.Path(f"8.png"),
                    pathlib.Path(f"9.png"),
                    pathlib.Path(f"10.png"),
                    pathlib.Path(f"11.png"),
                    pathlib.Path(f"12.png"),
                    pathlib.Path(f"13.png"),
                    pathlib.Path(f"14.png"),
                ],
            ),
            (
                [pathlib.Path("1.png"), pathlib.Path("11.png"), pathlib.Path("2.png"), pathlib.Path("22.png")],
                [pathlib.Path("1.png"), pathlib.Path("2.png"), pathlib.Path("11.png"), pathlib.Path("22.png")],
            ),
        ],
    )
    def test_path_sorter(self, input: list[pathlib.Path], output: list[pathlib.Path]):
        assert sorted(input, key=upload_file_sort) == output
