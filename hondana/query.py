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

from enum import Enum
from typing import TYPE_CHECKING

from .utils import to_camel_case


if TYPE_CHECKING:
    from .types.artist import ArtistIncludes as ArtistIncludesType
    from .types.author import AuthorIncludes as AuthorIncludesType
    from .types.chapter import ChapterIncludes as ChapterIncludesType
    from .types.cover import CoverIncludes as CoverIncludesType
    from .types.custom_list import CustomListIncludes as CustomListIncludesType
    from .types.manga import MangaIncludes as MangaIncludesType
    from .types.scanlator_group import (
        ScanlatorGroupIncludes as ScanlatorGroupIncludesType,
    )


__all__ = (
    "Order",
    "MangaListOrderQuery",
    "FeedOrderQuery",
    "MangaDraftListOrderQuery",
    "CoverArtListOrderQuery",
    "ScanlatorGroupListOrderQuery",
    "AuthorListOrderQuery",
    "UserListOrderQuery",
    "ArtistIncludes",
    "AuthorIncludes",
    "ChapterIncludes",
    "CoverIncludes",
    "CustomListIncludes",
    "MangaIncludes",
    "ScanlatorGroupIncludes",
)

VALID_ARTIST_INCLUDES: list[ArtistIncludesType] = ["manga"]
VALID_AUTHOR_INCLUDES: list[AuthorIncludesType] = ["manga"]
VALID_CHAPTER_INCLUDES: list[ChapterIncludesType] = ["manga", "user", "scanlation_group"]
VALID_COVER_INCLUDES: list[CoverIncludesType] = ["manga", "user"]
VALID_CUSTOMLIST_INCLUDES: list[CustomListIncludesType] = ["manga", "user", "owner"]
VALID_MANGA_INCLUDES: list[MangaIncludesType] = ["author", "artist", "cover_art", "manga"]
VALID_SCANLATORGROUP_INCLUDES: list[ScanlatorGroupIncludesType] = ["leader", "member"]
VALID_MANGA_LIST_ORDER_PARAMS: list[str] = [
    "title",
    "year",
    "created_at",
    "updated_at",
    "latest_uploaded_chapter",
    "followed_count",
    "relevance",
]
VALID_FEED_ORDER_PARAMS: list[str] = ["created_at", "updated_at", "publish_at", "volume", "chapter"]
VALID_MANGA_DRAFT_LIST_ORDER_PARAMS: list[str] = ["title", "year", "created_at", "updated_at"]
VALID_COVER_ART_LIST_ORDER_PARAMS: list[str] = ["created_at", "updated_at", "volume"]
VALID_SCANLATORGROUP_ORDER_PARAMS: list[str] = ["name", "created_at", "updated_at", "followed_count", "relevance"]
VALID_AUTHOR_LIST_ORDER_PARAMS: list[str] = ["name"]
VALID_USER_LIST_ORDER_PARAMS: list[str] = ["username"]


class Order(Enum):
    """
    A quick enum to filter by asc or desc.
    """

    ascending = "asc"
    descending = "desc"


class _OrderQuery:
    def __init__(self, *, valid: list[str], **kwargs: dict[str, Order]) -> None:
        if not kwargs:
            raise TypeError("You must pass valid kwargs.")

        _fmt = []
        for (name, value) in kwargs.items():
            if name in valid:
                _fmt.append(name)
                setattr(self, name, value)
        if not _fmt:
            raise TypeError("You must pass valid kwargs.")

    def _to_dict(self) -> dict[str, str]:
        fmt: dict[str, str] = {}
        for item in dir(self):
            if item.startswith("_"):
                continue
            if val := getattr(self, item):
                fmt[to_camel_case(str(item))] = val.value

        return fmt


class _Includes:
    def to_query(
        self,
        *,
        valid: list[str],
    ) -> list[str]:
        """Generates a list of strings based on the kwargs."""
        fmt = []
        for item in dir(self):
            if item.startswith("__"):
                continue
            if getattr(self, item) and item in valid:
                fmt.append(item)

        return fmt


class MangaListOrderQuery(_OrderQuery):
    """
    Parameters
    -----------
    title: :class:`~hondana.Order`
        Title ordering.
    year: :class:`~hondana.Order`
        Year ordering.
    created_at: :class:`~hondana.Order`
        Ordering by creation date.
    updated_at: :class:`~hondana.Order`
        Ordering by last updated date.
    latest_uploaded_chapter: :class:`~hondana.Order`
        Ordering by latest uploaded chapter.
    followed_count: :class:`~hondana.Order`
        Ordering by followed count.
    relevance: :class:`~hondana.Order`
        Ordering by relevance to search query.

    """

    def __init__(
        self,
        valid: list[str] = VALID_MANGA_LIST_ORDER_PARAMS,
        **kwargs: Order,
    ) -> None:
        super().__init__(valid=valid, **kwargs)


class FeedOrderQuery(_OrderQuery):
    """
    Parameters
    -----------
    created_at: :class:`~hondana.Order`
        Ordering by creation date.
    updated_at: :class:`~hondana.Order`
        Ordering by last updated date.
    publish_at: :class:`~hondana.Order`
        Ordering by published at date.
    volume: :class:`~hondana.Order`
        Ordering by volume number.
    chapter: :class:`~hondana.Order`
        Ordering by chapter number.

    """

    def __init__(self, valid: list[str] = VALID_FEED_ORDER_PARAMS, **kwargs: Order) -> None:
        super().__init__(valid=valid, **kwargs)


class MangaDraftListOrderQuery(_OrderQuery):
    """
    Parameters
    -----------
    title: :class:`~hondana.Order`
        Title ordering.
    year: :class:`~hondana.Order`
        Year ordering.
    created_at: :class:`~hondana.Order`
        Ordering by creation date.
    updated_at: :class:`~hondana.Order`
        Ordering by last updated date.

    """

    def __init__(self, valid: list[str] = VALID_MANGA_DRAFT_LIST_ORDER_PARAMS, **kwargs: Order) -> None:
        super().__init__(valid=valid, **kwargs)


class CoverArtListOrderQuery(_OrderQuery):
    """
    Parameters
    -----------
    created_at: :class:`~hondana.Order`
        Ordering by creation date.
    updated_at: :class:`~hondana.Order`
        Ordering by last updated date.
    volume: :class:`~hondana.Order`
        Ordering by volume number.
    """

    def __init__(self, valid: list[str] = VALID_COVER_ART_LIST_ORDER_PARAMS, **kwargs: Order) -> None:
        super().__init__(valid=valid, **kwargs)


class ScanlatorGroupListOrderQuery(_OrderQuery):
    """

    Parameters
    -----------
    name: :class:`~hondana.Order`
        Name ordering.
    created_at: :class:`~hondana.Order`
        Ordering by creation date.
    updated_at: :class:`~hondana.Order`
        Ordering by last updated date.
    followed_count: :class:`~hondana.Order`
        Ordering by followed count.
    relevance: :class:`~hondana.Order`
        Ordering by relevance to search query.
    """

    def __init__(self, valid: list[str] = VALID_SCANLATORGROUP_ORDER_PARAMS, **kwargs: Order) -> None:
        super().__init__(valid=valid, **kwargs)


class AuthorListOrderQuery(_OrderQuery):
    """
    Parameters
    -----------
    name: :class:`~hondana.Order`
        Name ordering.

    """

    def __init__(self, valid: list[str] = VALID_AUTHOR_LIST_ORDER_PARAMS, **kwargs: Order) -> None:
        super().__init__(valid=valid, **kwargs)


class UserListOrderQuery(_OrderQuery):
    """
    Parameters
    -----------
    username: :class:`~hondana.Order`
        Userame ordering.

    """

    def __init__(self, valid: list[str] = VALID_USER_LIST_ORDER_PARAMS, **kwargs: Order) -> None:
        super().__init__(valid=valid, **kwargs)


class ArtistIncludes(_Includes):
    """
    A helper for generating the ``includes[]`` parameter for queries.

    Parameters
    -----------
    manga: :class:`bool`
        Defaults to ``True``. Whether to include manga in the relationships.
    """

    def __init__(self, *, manga: bool = True) -> None:
        self.manga = manga
        self._valid: list[ArtistIncludesType] = VALID_ARTIST_INCLUDES

    def to_query(self) -> list[str]:
        """Retuns a list of valid query strings."""
        return super().to_query(valid=self._valid)


class AuthorIncludes(_Includes):
    """
    A helper for generating the ``includes[]`` parameter for queries.

    Parameters
    -----------
    manga: :class:`bool`
        Defaults to ``True``. Whether to include manga in the relationships.
    """

    def __init__(self, *, manga: bool = True) -> None:
        self.manga = manga
        self._valid: list[AuthorIncludesType] = VALID_AUTHOR_INCLUDES

    def to_query(self) -> list[str]:
        """Retuns a list of valid query strings."""
        return super().to_query(valid=self._valid)


class ChapterIncludes(_Includes):
    """
    A helper for generating the ``includes[]`` parameter for queries.

    Parameters
    -----------
    manga: :class:`bool`
        Defaults to ``True``. Whether to include manga in the relationships.
    user: :class:`bool`
        Defaults to ``True``. Whether to include user in the relationships.
    scanlation_group: :class:`bool`
        Defaults to ``True``. Whether to include scanlator group in the relationships.
    """

    def __init__(self, *, manga: bool = True, user: bool = True, scanlation_group: bool = True) -> None:
        self.manga = manga
        self.user = user
        self.scanlation_group = scanlation_group
        self._valid: list[ChapterIncludesType] = VALID_CHAPTER_INCLUDES

    def to_query(self) -> list[str]:
        """Retuns a list of valid query strings."""
        return super().to_query(valid=self._valid)


class CoverIncludes(_Includes):
    """
    A helper for generating the ``includes[]`` parameter for queries.

    Parameters
    -----------
    manga: :class:`bool`
        Defaults to ``True``. Whether to include manga in the relationships.
    user: :class:`bool`
        Defaults to ``True``. Whether to include user in the relationships.
    """

    def __init__(self, *, manga: bool = True, user: bool = True) -> None:
        self.manga = manga
        self.user = user
        self._valid: list[CoverIncludesType] = VALID_COVER_INCLUDES

    def to_query(self) -> list[str]:
        """Retuns a list of valid query strings."""
        return super().to_query(valid=self._valid)


class CustomListIncludes(_Includes):
    """
    A helper for generating the ``includes[]`` parameter for queries.

    Parameters
    -----------
    manga: :class:`bool`
        Defaults to ``True``. Whether to include manga in the relationships.
    user: :class:`bool`
        Defaults to ``True``. Whether to include user in the relationships.
    owner: :class:`bool`
        Defaults to ``True``. Whether to include owner in the relationships.
    """

    def __init__(self, *, manga: bool = True, user: bool = True, owner: bool = True) -> None:
        self.manga = manga
        self.user = user
        self.owner = owner
        self._valid: list[CustomListIncludesType] = VALID_CUSTOMLIST_INCLUDES

    def to_query(self) -> list[str]:
        """Retuns a list of valid query strings."""
        return super().to_query(valid=self._valid)


class MangaIncludes(_Includes):
    """
    A helper for generating the ``includes[]`` parameter for queries.

    Parameters
    -----------
    author: :class:`bool`
        Defaults to ``True``. Whether to include author in the relationships.
    artist: :class:`bool`
        Defaults to ``True``. Whether to include artist in the relationships.
    cover_art: :class:`bool`
        Defaults to ``True``. Whether to include cover in the relationships.
    manga: :class:`bool`
        Defaults to ``True``. Whether to include manga in the relationships.
    """

    def __init__(self, *, author: bool = True, artist: bool = True, cover_art: bool = True, manga: bool = True) -> None:
        self.author = author
        self.artist = artist
        self.cover_art = cover_art
        self.manga = manga
        self._valid: list[MangaIncludesType] = VALID_MANGA_INCLUDES

    def to_query(self) -> list[str]:
        """Retuns a list of valid query strings."""
        return super().to_query(valid=self._valid)


class ScanlatorGroupIncludes(_Includes):
    """
    A helper for generating the ``includes[]`` parameter for queries.

    Parameters
    -----------
    leader: :class:`bool`
        Defaults to ``True``. Whether to include leader in the relationships.
    member: :class:`bool`
        Defaults to ``True``. Whether to include members in the relationships.
    """

    def __init__(self, *, leader: bool = True, member: bool = True) -> None:
        self.leader = leader
        self.member = member
        self._valid: list[ScanlatorGroupIncludesType] = VALID_SCANLATORGROUP_INCLUDES

    def to_query(self) -> list[str]:
        """Retuns a list of valid query strings."""
        return super().to_query(valid=self._valid)
