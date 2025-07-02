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
import json
import pathlib
from copy import deepcopy
from typing import TYPE_CHECKING, Literal, overload

from hondana.enums import MangaRelationType
from hondana.manga import Manga, MangaRating, MangaRelation, MangaStatistics
from hondana.utils import RelationshipResolver, to_snake_case

if TYPE_CHECKING:
    from hondana.http import HTTPClient
    from hondana.types_.artist import ArtistResponse
    from hondana.types_.author import AuthorResponse
    from hondana.types_.common import LocalizedString
    from hondana.types_.cover import CoverResponse
    from hondana.types_.manga import GetMangaResponse, MangaRelationResponse, MangaResponse
    from hondana.types_.statistics import GetMangaStatisticsResponse, GetPersonalMangaRatingsResponse


PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "manga.json"
RELATIONS_PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "manga_relations.json"
STATISTICS_PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "manga_statistics.json"
RATING_PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "manga_ratings.json"

PAYLOAD: GetMangaResponse = json.load(PATH.open())
RELATIONS_PAYLOAD: MangaRelationResponse = json.load(RELATIONS_PATH.open())
STATISTICS_PAYLOAD: GetMangaStatisticsResponse = json.load(STATISTICS_PATH.open())
RATING_PAYLOAD: GetPersonalMangaRatingsResponse = json.load(RATING_PATH.open())
HTTP: HTTPClient = object()  # pyright: ignore[reportAssignmentType] # this is just for test purposes.


@overload
def clone_manga(type_: Literal["manga"]) -> Manga: ...


@overload
def clone_manga(type_: Literal["relation"]) -> MangaRelation: ...


@overload
def clone_manga(type_: Literal["stats"]) -> MangaStatistics: ...


@overload
def clone_manga(type_: Literal["rating"]) -> MangaRating: ...


def clone_manga(
    type_: Literal["manga", "relation", "stats", "rating"] = "manga",
) -> Manga | MangaRelation | MangaStatistics | MangaRating:
    if type_ == "manga":
        t = deepcopy(PAYLOAD)
        return Manga(HTTP, t["data"])
    if type_ == "relation":
        t = deepcopy(RELATIONS_PAYLOAD)
        return MangaRelation(HTTP, PAYLOAD["data"]["id"], t["data"][0])
    if type_ == "stats":
        t = deepcopy(STATISTICS_PAYLOAD)
        key = next(iter(t["statistics"]))
        return MangaStatistics(HTTP, PAYLOAD["data"]["id"], t["statistics"][key])
    t = deepcopy(RATING_PAYLOAD)
    key = next(iter(t["ratings"]))
    return MangaRating(HTTP, PAYLOAD["data"]["id"], t["ratings"][key])


class TestManga:
    def test_id(self) -> None:
        manga = clone_manga("manga")
        assert manga.id == PAYLOAD["data"]["id"]

    def test_attributes(self) -> None:
        manga = clone_manga("manga")

        for item in PAYLOAD["data"]["attributes"]:
            if item == "altTitles":  # special case sane attribute renaming
                item = "alternateTitles"  # noqa: PLW2901  # renaming raw payload items
            elif item == "isLocked":  # special case sane attribute renaming
                item = "locked"  # noqa: PLW2901  # renaming raw payload items
            assert hasattr(manga, to_snake_case(item))

    def test_relationship_length(self) -> None:
        manga = clone_manga("manga")
        assert manga.artists is not None
        assert manga.authors is not None
        assert manga.related_manga is not None
        assert manga.cover is not None

        obj_len = len(manga.artists) + len(manga.authors) + len(manga.related_manga) + 1  # cover

        assert "relationships" in PAYLOAD["data"]

        assert obj_len == len(PAYLOAD["data"]["relationships"])

    def test_cache_slot_property(self) -> None:
        manga = clone_manga("manga")

        assert not hasattr(manga, "_cs_tags")

        _ = manga.tags

        assert hasattr(manga, "_cs_tags")

    def test_artists_property(self) -> None:
        manga = clone_manga("manga")

        assert manga.artists is not None
        assert "relationships" in PAYLOAD["data"]
        artist_rels = RelationshipResolver["ArtistResponse"](PAYLOAD["data"]["relationships"], "artist").resolve()

        assert len(manga.artists) == len(artist_rels)

    def test_authors_property(self) -> None:
        manga = clone_manga("manga")

        assert manga.authors is not None
        assert "relationships" in PAYLOAD["data"]
        author_rels = RelationshipResolver["AuthorResponse"](PAYLOAD["data"]["relationships"], "author").resolve()

        assert len(manga.authors) == len(author_rels)

    def test_cover_property(self) -> None:
        manga = clone_manga("manga")

        assert manga.cover is not None

        assert "relationships" in PAYLOAD["data"]
        cover_rel = RelationshipResolver["CoverResponse"](PAYLOAD["data"]["relationships"], "cover_art").pop()
        assert cover_rel is not None

        assert manga.cover.id == cover_rel["id"]
        assert manga.cover_url() == f"https://uploads.mangadex.org/covers/{manga.id}/{cover_rel['attributes']['fileName']}"
        assert (
            manga.cover_url(size=256)
            == f"https://uploads.mangadex.org/covers/{manga.id}/{cover_rel['attributes']['fileName']}.256.jpg"
        )
        assert (
            manga.cover_url(size=512)
            == f"https://uploads.mangadex.org/covers/{manga.id}/{cover_rel['attributes']['fileName']}.512.jpg"
        )

    def test_related_manga_property(self) -> None:
        manga = clone_manga("manga")

        assert manga.related_manga is not None

        assert "relationships" in PAYLOAD["data"]
        related_keys = RelationshipResolver["MangaResponse"](PAYLOAD["data"]["relationships"], "manga").resolve()
        assert bool(related_keys)

        assert len(manga.related_manga) == len(related_keys)

    def test_alt_title(self) -> None:
        manga = clone_manga("manga")

        alt_titles = PAYLOAD["data"]["attributes"]["altTitles"]

        fmt: LocalizedString = {k: v for obj in alt_titles for k, v in obj.items()}  # pyright: ignore[reportAssignmentType] # TypedDict.items() is weird

        for code, title in fmt.items():
            assert manga.alternate_titles.get(code) == title

    def test_localized_title(self) -> None:
        manga = clone_manga("manga")

        assert manga.title == next(iter(PAYLOAD["data"]["attributes"]["title"].values()))  # why did I need to do this

    def test_localized_description(self) -> None:
        manga = clone_manga("manga")

        for key, value in manga._description.items():  # pyright: ignore[reportPrivateUsage] # sorry, need this for test purposes
            assert manga.localized_description(key) == value  # pyright: ignore[reportArgumentType] # can't narrow strings

    def test_date_attributes(self) -> None:
        manga = clone_manga("manga")

        assert manga.created_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["createdAt"])
        assert manga.updated_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["updatedAt"])


class TestMangaRelation:
    def test_id(self) -> None:
        manga = clone_manga("relation")

        assert manga.source_manga_id == PAYLOAD["data"]["id"]
        assert manga.id == RELATIONS_PAYLOAD["data"][0]["id"]

    def test_type(self) -> None:
        manga = clone_manga("relation")

        assert manga.relation_type.value == RELATIONS_PAYLOAD["data"][0]["attributes"]["relation"]
        assert manga.relation_type is MangaRelationType(RELATIONS_PAYLOAD["data"][0]["attributes"]["relation"])


class TestMangaStatistics:
    def test_id(self) -> None:
        manga = clone_manga("stats")

        assert manga.parent_id == PAYLOAD["data"]["id"]

    def test_bookmarks(self) -> None:
        manga = clone_manga("stats")

        key = next(iter(STATISTICS_PAYLOAD["statistics"]))
        assert manga.follows == STATISTICS_PAYLOAD["statistics"][key]["follows"]

    def test_average(self) -> None:
        manga = clone_manga("stats")

        key = next(iter(STATISTICS_PAYLOAD["statistics"]))
        assert manga.average == STATISTICS_PAYLOAD["statistics"][key]["rating"]["average"]

    def test_bayesian(self) -> None:
        manga = clone_manga("stats")

        key = next(iter(STATISTICS_PAYLOAD["statistics"]))
        assert manga.bayesian == STATISTICS_PAYLOAD["statistics"][key]["rating"]["bayesian"]


class TestMangaRating:
    def test_id(self) -> None:
        manga = clone_manga("rating")

        assert manga.parent_id == PAYLOAD["data"]["id"]

    def test_rating(self) -> None:
        manga = clone_manga("rating")

        key = next(iter(RATING_PAYLOAD["ratings"]))
        assert manga.rating == RATING_PAYLOAD["ratings"][key]["rating"]
