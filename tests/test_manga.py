from __future__ import annotations

import datetime
import json
import pathlib
from copy import deepcopy
from typing import TYPE_CHECKING, Literal, Union, overload

from hondana.enums import MangaRelationType
from hondana.http import HTTPClient
from hondana.manga import Manga, MangaRating, MangaRelation, MangaStatistics
from hondana.utils import relationship_finder, to_snake_case


if TYPE_CHECKING:
    from hondana.types.manga import GetMangaResponse, MangaRelationResponse
    from hondana.types.statistics import GetPersonalMangaRatingsResponse, GetStatisticsResponse


PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "manga.json"
RELATION_PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "manga_relation.json"
STATISTICS_PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "manga_statistics.json"
RATING_PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "manga_ratings.json"

PAYLOAD: GetMangaResponse = json.load(open(PATH, "r"))
RELATION_PAYLOAD: MangaRelationResponse = json.load(open(RELATION_PATH, "r"))
STATISTICS_PAYLOAD: GetStatisticsResponse = json.load(open(STATISTICS_PATH, "r"))
RATING_PAYLOAD: GetPersonalMangaRatingsResponse = json.load(open(RATING_PATH, "r"))
HTTP: HTTPClient = object()  # type: ignore # this is just for test purposes.


@overload
def clone_manga(type_: Literal["manga"]) -> Manga:
    ...


@overload
def clone_manga(type_: Literal["relation"]) -> MangaRelation:
    ...


@overload
def clone_manga(type_: Literal["stats"]) -> MangaStatistics:
    ...


@overload
def clone_manga(type_: Literal["rating"]) -> MangaRating:
    ...


def clone_manga(
    type_: Literal["manga", "relation", "stats", "rating"] = "manga"
) -> Union[Manga, MangaRelation, MangaStatistics, MangaRating]:
    if type_ == "manga":
        t = deepcopy(PAYLOAD)
        return Manga(HTTP, t["data"])
    elif type_ == "relation":
        t = deepcopy(RELATION_PAYLOAD)
        return MangaRelation(HTTP, PAYLOAD["data"]["id"], t["data"][0])
    elif type_ == "stats":
        t = deepcopy(STATISTICS_PAYLOAD)
        key = next(iter(t["statistics"]))
        return MangaStatistics(HTTP, PAYLOAD["data"]["id"], t["statistics"][key])
    elif type_ == "rating":
        t = deepcopy(RATING_PAYLOAD)
        key = next(iter(t["ratings"]))
        return MangaRating(HTTP, PAYLOAD["data"]["id"], t["ratings"][key])


class TestManga:
    def test_id(self):
        manga = clone_manga("manga")
        assert manga.id == PAYLOAD["data"]["id"]

    def test_attributes(self):
        manga = clone_manga("manga")

        for item in PAYLOAD["data"]["attributes"]:
            if item == "altTitles":  # special case sane attribute renaming
                item = "alternateTitles"
            elif item == "isLocked":  # special case sane attribute renaming
                item = "locked"
            assert hasattr(manga, to_snake_case(item))

    def test_relationship_length(self):
        manga = clone_manga("manga")
        assert manga.artists is not None
        assert manga.authors is not None
        assert manga.related_manga is not None
        assert manga.cover is not None

        obj_len = len(manga.artists) + len(manga.authors) + len(manga.related_manga) + 1  # cover

        assert "relationships" in PAYLOAD["data"]

        assert obj_len == len(PAYLOAD["data"]["relationships"])

    def test_cache_slot_property(self):
        manga = clone_manga("manga")

        assert not hasattr(manga, "_cs_tags")

        manga.tags

        assert hasattr(manga, "_cs_tags")

    def test_artists_property(self):
        manga = clone_manga("manga")

        assert manga.artists is not None
        assert "relationships" in PAYLOAD["data"]
        artist_rels = relationship_finder(PAYLOAD["data"]["relationships"], "artist", limit=None)

        assert len(manga.artists) == len(artist_rels)

    def test_authors_property(self):
        manga = clone_manga("manga")

        assert manga.authors is not None
        assert "relationships" in PAYLOAD["data"]
        author_rels = relationship_finder(PAYLOAD["data"]["relationships"], "author", limit=None)

        assert len(manga.authors) == len(author_rels)

    def test_cover_property(self):
        manga = clone_manga("manga")

        assert manga.cover is not None

        assert "relationships" in PAYLOAD["data"]
        cover_rel = relationship_finder(PAYLOAD["data"]["relationships"], "cover_art", limit=1)
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

    def test_related_manga_property(self):
        manga = clone_manga("manga")

        assert manga.related_manga is not None

        assert "relationships" in PAYLOAD["data"]
        related_keys = relationship_finder(PAYLOAD["data"]["relationships"], "manga", limit=None)
        assert bool(related_keys)

        assert len(manga.related_manga) == len(related_keys)

    def test_alt_title(self):
        manga = clone_manga("manga")

        alt_titles = PAYLOAD["data"]["attributes"]["altTitles"]

        fmt: LocalizedString = {k: v for obj in alt_titles for k, v in obj.items()}  # type: ignore # silly narrowing

        for code, title in fmt.items():
            assert manga.alternate_titles.get(code) == title

    def test_localized_title(self):
        manga = clone_manga("manga")

        assert manga.title == next(iter(PAYLOAD["data"]["attributes"]["title"].values()))  # why did I need to do this

    def test_localized_description(self):
        manga = clone_manga("manga")

        for key, value in manga._description.items():
            assert manga.localized_description(key) == value  # type: ignore # can't narrow strings

    def test_date_attributes(self):
        manga = clone_manga("manga")

        assert manga.created_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["createdAt"])
        assert manga.updated_at == datetime.datetime.fromisoformat(PAYLOAD["data"]["attributes"]["updatedAt"])


class TestMangaRelation:
    def test_id(self):
        manga = clone_manga("relation")

        assert manga.source_manga_id == PAYLOAD["data"]["id"]
        assert manga.id == RELATION_PAYLOAD["data"][0]["id"]

    def test_type(self):
        manga = clone_manga("relation")

        assert str(manga.relation_type) == RELATION_PAYLOAD["data"][0]["attributes"]["relation"]
        assert manga.relation_type is MangaRelationType(RELATION_PAYLOAD["data"][0]["attributes"]["relation"])


class TestMangaStatistics:
    def test_id(self):
        manga = clone_manga("stats")

        assert manga.parent_id == PAYLOAD["data"]["id"]

    def test_follows(self):
        manga = clone_manga("stats")

        key = next(iter(STATISTICS_PAYLOAD["statistics"]))
        assert manga.follows == STATISTICS_PAYLOAD["statistics"][key]["follows"]

    def test_average(self):
        manga = clone_manga("stats")

        key = next(iter(STATISTICS_PAYLOAD["statistics"]))
        assert manga.average == STATISTICS_PAYLOAD["statistics"][key]["rating"]["average"]

    def test_bayesian(self):
        manga = clone_manga("stats")

        key = next(iter(STATISTICS_PAYLOAD["statistics"]))
        assert manga.bayesian == STATISTICS_PAYLOAD["statistics"][key]["rating"]["bayesian"]


class TestMangaRating:
    def test_id(self):
        manga = clone_manga("rating")

        assert manga.parent_id == PAYLOAD["data"]["id"]

    def test_rating(self):
        manga = clone_manga("rating")

        key = next(iter(RATING_PAYLOAD["ratings"]))
        assert manga.rating == RATING_PAYLOAD["ratings"][key]["rating"]
