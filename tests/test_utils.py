from __future__ import annotations

import datetime
from typing import Iterable, Mapping, Optional, TypeVar, Union

import pytest

from hondana.types.relationship import RelationshipResponse
from hondana.utils import (
    MISSING,
    CustomRoute,
    Route,
    as_chunks,
    calculate_limits,
    delta_to_iso,
    iso_to_delta,
    php_query_builder,
    relationship_finder,
    to_camel_case,
    to_snake_case,
)


T = TypeVar("T")


class TestUtils:
    def test_missing(self):
        assert MISSING is not None
        assert bool(MISSING) is False

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
        assert [x for x in as_chunks(source, chunk_size)] == chunked

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
        ("input", "output"),
        [
            ([{"type": "test", "hello": "goodbye"}], [{"type": "test", "hello": "goodbye"}]),
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
    def test_relationship_finder(self, input: list[dict[str, str]], output: list[dict[str, str]]):
        ret: list[RelationshipResponse] = []
        for item in relationship_finder(input, "test"):  # type: ignore - narrow needed but this is a test so...
            if item["type"] == "test":
                ret.append(item)

        assert ret == output
