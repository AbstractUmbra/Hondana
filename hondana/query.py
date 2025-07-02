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

from typing import TYPE_CHECKING

from .enums import Order
from .utils import to_camel_case

if TYPE_CHECKING:
    from typing import Self


__all__ = (
    "ArtistIncludes",
    "AuthorIncludes",
    "AuthorListOrderQuery",
    "ChapterIncludes",
    "CoverArtListOrderQuery",
    "CoverIncludes",
    "CustomListIncludes",
    "FeedOrderQuery",
    "MangaDraftListOrderQuery",
    "MangaIncludes",
    "MangaListOrderQuery",
    "Order",
    "ReportListOrderQuery",
    "ScanlatorGroupIncludes",
    "ScanlatorGroupListOrderQuery",
    "SubscriptionIncludes",
    "UserListOrderQuery",
)


class _OrderQuery:
    __slots__: tuple[str, ...] = ()

    def __init__(self, **kwargs: Order) -> None:
        if not kwargs:
            msg = "You must pass valid kwargs."
            raise TypeError(msg)

        fmt: list[str] = []
        for name, value in kwargs.items():
            if name in self.__slots__:
                setattr(self, name, value.value)
            else:
                fmt.append(name)

        if fmt:
            msg = f"You have passed invalid kwargs: {', '.join(fmt)}"
            raise TypeError(msg)

    def __repr__(self) -> str:
        opt: list[str] = []
        for key in self.__slots__:
            if val := getattr(self, key, None):
                opt.append(f"{key}={val.name}")  # noqa: PERF401
        return f"<{self.__class__.__name__} {' '.join(opt)}>"

    def to_dict(self) -> dict[str, str]:
        fmt: dict[str, str] = {}
        for item in self.__slots__:
            if val := getattr(self, item, None):  # pyright: ignore[reportAssignmentType] # only Order can be assigned here
                val: str
                fmt[to_camel_case(str(item))] = val

        return fmt


class _Includes:
    __slots__: tuple[str, ...] = ()

    def to_query(self) -> list[str]:
        """Generates a list of strings based on the kwargs.

        Returns
        -------
        List[:class:`str`]
            The list of query parameters (pre-PHP formatting).
        """
        fmt: list[str] = []
        for item in dir(self):
            if item.startswith("_"):
                continue
            if getattr(self, item) and item in self.__slots__:
                fmt.append(item)

        return fmt

    def __repr__(self) -> str:
        fmt = " ".join([f"{key}={getattr(self, key, False)}" for key in self.__slots__])
        return f"<{self.__class__.__name__} {fmt}>"

    @classmethod
    def all(cls: type[Self]) -> Self:
        """A factory method that returns all possible reference expansions for this type.

        Returns
        -------
        An Includes type object with all flags set.
        """
        self = cls()

        for item in self.__slots__:
            setattr(self, item, True)

        return self

    @classmethod
    def none(cls: type[Self]) -> Self:
        """A factory method that disables all possible reference expansions for this type.

        Returns
        -------
        An Includes type object with no flags set.
        """
        self = cls()

        for item in self.__slots__:
            setattr(self, item, False)

        return self


class MangaListOrderQuery(_OrderQuery):
    """Query ordering for Manga lists.

    Parameters
    ----------
    title: :class:`~hondana.query.Order`
        Title ordering.
    year: :class:`~hondana.query.Order`
        Year ordering.
    created_at: :class:`~hondana.query.Order`
        Ordering by creation date.
    updated_at: :class:`~hondana.query.Order`
        Ordering by last updated date.
    latest_uploaded_chapter: :class:`~hondana.query.Order`
        Ordering by latest uploaded chapter.
    relevance: :class:`~hondana.query.Order`
        Ordering by relevance to search query.
    rating: :class:`~hondana.query.Order`
        Ordering by rating.
    """

    __slots__ = (
        "created_at",
        "latest_uploaded_chapter",
        "rating",
        "relevance",
        "title",
        "updated_at",
        "year",
    )

    title: Order | None
    year: Order | None
    created_at: Order | None
    updated_at: Order | None
    latest_uploaded_chapter: Order | None
    relevance: Order | None
    rating: Order | None

    def __init__(self, **kwargs: Order) -> None:
        super().__init__(**kwargs)


class FeedOrderQuery(_OrderQuery):
    """Query ordering for feeds.

    Parameters
    ----------
    created_at: :class:`~hondana.query.Order`
        Ordering by creation date.
    updated_at: :class:`~hondana.query.Order`
        Ordering by last updated date.
    publish_at: :class:`~hondana.query.Order`
        Ordering by published at date.
    readable_at: :class:`~hondana.query.Order`
        Ordering by when the chapters are readable.
    volume: :class:`~hondana.query.Order`
        Ordering by volume number.
    chapter: :class:`~hondana.query.Order`
        Ordering by chapter number.
    """

    __slots__ = (
        "chapter",
        "created_at",
        "publish_at",
        "readable_at",
        "updated_at",
        "volume",
    )

    created_at: Order | None
    updated_at: Order | None
    publish_at: Order | None
    readable_at: Order | None
    volume: Order | None
    chapter: Order | None

    def __init__(self, **kwargs: Order) -> None:
        super().__init__(**kwargs)


class MangaDraftListOrderQuery(_OrderQuery):
    """Query ordering for Manga draft lists.

    Parameters
    ----------
    title: :class:`~hondana.query.Order`
        Title ordering.
    year: :class:`~hondana.query.Order`
        Year ordering.
    created_at: :class:`~hondana.query.Order`
        Ordering by creation date.
    updated_at: :class:`~hondana.query.Order`
        Ordering by last updated date.
    """

    __slots__ = (
        "created_at",
        "title",
        "updated_at",
        "year",
    )

    title: Order | None
    year: Order | None
    created_at: Order | None
    updated_at: Order | None

    def __init__(self, **kwargs: Order) -> None:
        super().__init__(**kwargs)


class CoverArtListOrderQuery(_OrderQuery):
    """Query ordering for Cover art lists.

    Parameters
    ----------
    created_at: :class:`~hondana.query.Order`
        Ordering by creation date.
    updated_at: :class:`~hondana.query.Order`
        Ordering by last updated date.
    volume: :class:`~hondana.query.Order`
        Ordering by volume number.
    """

    __slots__ = (
        "created_at",
        "updated_at",
        "volume",
    )

    created_at: Order | None
    updated_at: Order | None
    volume: Order | None

    def __init__(self, **kwargs: Order) -> None:
        super().__init__(**kwargs)


class ScanlatorGroupListOrderQuery(_OrderQuery):
    """Query ordering for Scanlator group lists.

    Parameters
    ----------
    name: :class:`~hondana.query.Order`
        Name ordering.
    created_at: :class:`~hondana.query.Order`
        Ordering by creation date.
    updated_at: :class:`~hondana.query.Order`
        Ordering by last updated date.
    followed_count: :class:`~hondana.query.Order`
        Ordering by followed count.
    relevance: :class:`~hondana.query.Order`
        Ordering by relevance to search query.
    """

    __slots__ = (
        "created_at",
        "followed_count",
        "name",
        "relevance",
        "updated_at",
    )

    name: Order | None
    created_at: Order | None
    updated_at: Order | None
    followed_count: Order | None
    relevance: Order | None

    def __init__(self, **kwargs: Order) -> None:
        super().__init__(**kwargs)


class AuthorListOrderQuery(_OrderQuery):
    """Query ordering for Author lists.

    Parameters
    ----------
    name: :class:`~hondana.query.Order`
        Name ordering.
    """

    __slots__ = ("name",)

    name: Order | None

    def __init__(self, **kwargs: Order) -> None:
        super().__init__(**kwargs)


class UserListOrderQuery(_OrderQuery):
    """Query ordering for User lists.

    Parameters
    ----------
    username: :class:`~hondana.query.Order`
        Username ordering.
    """

    __slots__ = ("username",)

    username: Order | None

    def __init__(self, **kwargs: Order) -> None:
        super().__init__(**kwargs)


class ReportListOrderQuery(_OrderQuery):
    """Query ordering for Report lists.

    Parameters
    ----------
    created_at: :class:`~hondana.query.Order`
        Ordering by creation date.
    """

    __slots__ = ("created_at",)

    created_at: Order | None

    def __init__(self, **kwargs: Order) -> None:
        super().__init__(**kwargs)


class ArtistIncludes(_Includes):
    """
    A helper for generating the ``includes[]`` parameter for queries.

    Parameters
    ----------
    manga: :class:`bool`
        Defaults to ``True``. Whether to include manga in the relationships.
    """

    __slots__ = ("manga",)

    def __init__(self, *, manga: bool = True) -> None:
        self.manga: bool = manga

    def to_query(self) -> list[str]:
        """Generates a list of strings based on the kwargs.

        Returns
        -------
        List[:class:`str`]
            The list of query parameters (pre-PHP formatting).
        """
        return super().to_query()


class AuthorIncludes(_Includes):
    """
    A helper for generating the ``includes[]`` parameter for queries.

    Parameters
    ----------
    manga: :class:`bool`
        Defaults to ``True``. Whether to include manga in the relationships.
    """

    __slots__ = ("manga",)

    def __init__(self, *, manga: bool = True) -> None:
        self.manga: bool = manga

    def to_query(self) -> list[str]:
        """Generates a list of strings based on the kwargs.

        Returns
        -------
        List[:class:`str`]
            The list of query parameters (pre-PHP formatting).
        """
        return super().to_query()


class ChapterIncludes(_Includes):
    """
    A helper for generating the ``includes[]`` parameter for queries.

    Parameters
    ----------
    manga: :class:`bool`
        Defaults to ``True``. Whether to include manga in the relationships.
    user: :class:`bool`
        Defaults to ``True``. Whether to include user in the relationships.
    scanlation_group: :class:`bool`
        Defaults to ``True``. Whether to include scanlator group in the relationships.
    """

    __slots__ = (
        "manga",
        "scanlation_group",
        "user",
    )

    def __init__(self, *, manga: bool = True, user: bool = True, scanlation_group: bool = True) -> None:
        self.manga: bool = manga
        self.user: bool = user
        self.scanlation_group: bool = scanlation_group

    def to_query(self) -> list[str]:
        """Returns a list of valid query strings.

        Returns
        -------
        List[:class:`str`]
            The list of query parameters (pre-PHP formatting).
        """
        return super().to_query()


class CoverIncludes(_Includes):
    """
    A helper for generating the ``includes[]`` parameter for queries.

    Parameters
    ----------
    manga: :class:`bool`
        Defaults to ``True``. Whether to include manga in the relationships.
    user: :class:`bool`
        Defaults to ``True``. Whether to include user in the relationships.
    """

    __slots__ = (
        "manga",
        "user",
    )

    def __init__(self, *, manga: bool = True, user: bool = True) -> None:
        self.manga: bool = manga
        self.user: bool = user

    def to_query(self) -> list[str]:
        """Returns a list of valid query strings.

        Returns
        -------
        List[:class:`str`]
            The list of query parameters (pre-PHP formatting).
        """
        return super().to_query()


class CustomListIncludes(_Includes):
    """
    A helper for generating the ``includes[]`` parameter for queries.

    Parameters
    ----------
    manga: :class:`bool`
        Defaults to ``True``. Whether to include manga in the relationships.
    user: :class:`bool`
        Defaults to ``True``. Whether to include user in the relationships.
    owner: :class:`bool`
        Defaults to ``True``. Whether to include owner in the relationships.
    """

    __slots__ = (
        "manga",
        "owner",
        "user",
    )

    def __init__(self, *, manga: bool = True, user: bool = True, owner: bool = True) -> None:
        self.manga: bool = manga
        self.user: bool = user
        self.owner: bool = owner

    def to_query(self) -> list[str]:
        """Returns a list of valid query strings.

        Returns
        -------
        List[:class:`str`]
            The formatted query string.
        """
        return super().to_query()


class MangaIncludes(_Includes):
    """
    A helper for generating the ``includes[]`` parameter for queries.

    Parameters
    ----------
    author: :class:`bool`
        Defaults to ``True``. Whether to include author in the relationships.
    artist: :class:`bool`
        Defaults to ``True``. Whether to include artist in the relationships.
    cover_art: :class:`bool`
        Defaults to ``True``. Whether to include cover in the relationships.
    manga: :class:`bool`
        Defaults to ``True``. Whether to include manga in the relationships.
    """

    __slots__ = (
        "artist",
        "author",
        "cover_art",
        "manga",
    )

    def __init__(self, *, author: bool = True, artist: bool = True, cover_art: bool = True, manga: bool = True) -> None:
        self.author: bool = author
        self.artist: bool = artist
        self.cover_art: bool = cover_art
        self.manga: bool = manga


class ScanlatorGroupIncludes(_Includes):
    """
    A helper for generating the ``includes[]`` parameter for queries.

    Parameters
    ----------
    leader: :class:`bool`
        Defaults to ``True``. Whether to include leader in the relationships.
    member: :class:`bool`
        Defaults to ``True``. Whether to include members in the relationships.
    """

    __slots__ = (
        "leader",
        "member",
    )

    def __init__(self, *, leader: bool = True, member: bool = True) -> None:
        self.leader: bool = leader
        self.member: bool = member

    def to_query(self) -> list[str]:
        """Returns a list of valid query strings.

        Returns
        -------
        List[:class:`str`]
            The list of query parameters (pre-PHP formatting).
        """
        return super().to_query()


class UserReportIncludes(_Includes):
    """
    A helper for generating the ``includes[]`` parameter for queries.

    Parameters
    ----------
    user: :class:`bool`
        Defaults to ``True``. Whether to include user in the relationships.
    reason: :class:`bool`
        Defaults to ``True``. Whether to include report in the relationships.
    """

    __slots__ = (
        "reason",
        "user",
    )

    def __init__(self, *, user: bool = True, reason: bool = True) -> None:
        self.user: bool = user
        self.reason: bool = reason

    def to_query(self) -> list[str]:
        """Returns a list of valid query strings.

        Returns
        -------
        List[:class:`str`]
            The list of query parameters (pre-PHP formatting).
        """
        return super().to_query()


class SubscriptionIncludes(_Includes):
    """
    A helper for generating the ``includes[]`` parameter for queries.

    Parameters
    ----------
    user: :class:`bool`
        Defaults to ``True``. Whether to include user in the relationships.
    """

    __slots__ = ("user",)

    def __init__(self, *, user: bool = True) -> None:
        self.user: bool = user

    def to_query(self) -> list[str]:
        """Returns a list of valid query strings.

        Returns
        -------
        List[:class:`str`]
            The list of query parameters (pre-PHP formatting).
        """
        return super().to_query()
