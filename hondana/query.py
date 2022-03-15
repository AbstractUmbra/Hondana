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

from typing import TYPE_CHECKING, Optional, Type

from .enums import Order as Order
from .utils import to_camel_case


if TYPE_CHECKING:
    from typing_extensions import Self


__all__ = (
    "Order",
    "MangaListOrderQuery",
    "FeedOrderQuery",
    "MangaDraftListOrderQuery",
    "CoverArtListOrderQuery",
    "ScanlatorGroupListOrderQuery",
    "AuthorListOrderQuery",
    "UserListOrderQuery",
    "ReportListOrderQuery",
    "ArtistIncludes",
    "AuthorIncludes",
    "ChapterIncludes",
    "CoverIncludes",
    "CustomListIncludes",
    "MangaIncludes",
    "ScanlatorGroupIncludes",
)


class _OrderQuery:
    __slots__ = ()

    def __init__(self, **kwargs: Optional[Order]) -> None:
        if not kwargs:
            raise TypeError("You must pass valid kwargs.")

        _fmt = []
        for (name, value) in kwargs.items():
            if name in self.__slots__:
                setattr(self, name, value)
            else:
                _fmt.append(name)

        if _fmt:
            raise TypeError(f"You have passed invalid kwargs: {', '.join(_fmt)}")

    def __repr__(self) -> str:
        opt = []
        for key in self.__slots__:
            if val := getattr(self, key, None):
                opt.append(f"{key}={val.name}")
        return f"<{self.__class__.__name__} {' '.join(opt)}>"

    def to_dict(self) -> dict[str, str]:
        fmt: dict[str, str] = {}
        for item in self.__slots__:
            if val := getattr(self, item, None):
                fmt[to_camel_case(str(item))] = val.value

        return fmt


class _Includes:
    __slots__ = ()

    def to_query(self) -> list[str]:
        """Generates a list of strings based on the kwargs.

        Returns
        --------
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
    def all(cls: Type[Self]) -> Self:
        """A factory method that returns all possible reference expansions for this type."""
        self = cls()

        for item in self.__slots__:
            setattr(self, item, True)

        return self

    @classmethod
    def none(cls: Type[Self]) -> Self:
        """A factory method that disables all possible reference expansions for this type."""
        self = cls()

        for item in self.__slots__:
            setattr(self, item, False)

        return self


class MangaListOrderQuery(_OrderQuery):
    """
    Parameters
    -----------
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
    followed_count: :class:`~hondana.query.Order`
        Ordering by followed count.
    relevance: :class:`~hondana.query.Order`
        Ordering by relevance to search query.
    """

    __slots__ = (
        "title",
        "year",
        "created_at",
        "updated_at",
        "latest_uploaded_chapter",
        "followed_count",
        "relevance",
    )

    title: Optional[Order]
    year: Optional[Order]
    created_at: Optional[Order]
    updated_at: Optional[Order]
    latest_uploaded_chapter: Optional[Order]
    followed_count: Optional[Order]
    relevance: Optional[Order]

    def __init__(self, **kwargs: Order) -> None:
        super().__init__(**kwargs)


class FeedOrderQuery(_OrderQuery):
    """
    Parameters
    -----------
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
        "created_at",
        "updated_at",
        "publish_at",  # I hate this too.
        "readable_at",
        "volume",
        "chapter",
    )

    created_at: Optional[Order]
    updated_at: Optional[Order]
    publish_at: Optional[Order]
    readable_at: Optional[Order]
    volume: Optional[Order]
    chapter: Optional[Order]

    def __init__(self, **kwargs: Order) -> None:
        super().__init__(**kwargs)


class MangaDraftListOrderQuery(_OrderQuery):
    """
    Parameters
    -----------
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
        "title",
        "year",
        "created_at",
        "updated_at",
    )

    title: Optional[Order]
    year: Optional[Order]
    created_at: Optional[Order]
    updated_at: Optional[Order]

    def __init__(self, **kwargs: Order) -> None:
        super().__init__(**kwargs)


class CoverArtListOrderQuery(_OrderQuery):
    """
    Parameters
    -----------
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

    created_at: Optional[Order]
    updated_at: Optional[Order]
    volume: Optional[Order]

    def __init__(self, **kwargs: Order) -> None:
        super().__init__(**kwargs)


class ScanlatorGroupListOrderQuery(_OrderQuery):
    """
    Parameters
    -----------
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
        "name",
        "created_at",
        "updated_at",
        "followed_count",
        "relevance",
    )

    name: Optional[Order]
    created_at: Optional[Order]
    updated_at: Optional[Order]
    followed_count: Optional[Order]
    relevance: Optional[Order]

    def __init__(self, **kwargs: Order) -> None:
        super().__init__(**kwargs)


class AuthorListOrderQuery(_OrderQuery):
    """
    Parameters
    -----------
    name: :class:`~hondana.query.Order`
        Name ordering.
    """

    __slots__ = ("name",)

    name: Optional[Order]

    def __init__(self, **kwargs: Order) -> None:
        super().__init__(**kwargs)


class UserListOrderQuery(_OrderQuery):
    """
    Parameters
    -----------
    username: :class:`~hondana.query.Order`
        Username ordering.
    """

    __slots__ = ("username",)

    username: Optional[Order]

    def __init__(self, **kwargs: Order) -> None:
        super().__init__(**kwargs)


class ReportListOrderQuery(_OrderQuery):
    """
    Parameters
    -----------
    created_at: :class:`~hondana.query.Order`
        Ordering by creation date.
    """

    __slots__ = ("created_at",)

    created_at: Optional[Order]

    def __init__(self, **kwargs: Order) -> None:
        super().__init__(**kwargs)


class ArtistIncludes(_Includes):
    """
    A helper for generating the ``includes[]`` parameter for queries.

    Parameters
    -----------
    manga: :class:`bool`
        Defaults to ``True``. Whether to include manga in the relationships.
    """

    __slots__ = ("manga",)

    def __init__(self, *, manga: bool = True) -> None:
        self.manga: bool = manga

    def to_query(self) -> list[str]:
        """Generates a list of strings based on the kwargs.

        Returns
        --------
        List[:class:`str`]
            The list of query parameters (pre-PHP formatting).
        """
        return super().to_query()


class AuthorIncludes(_Includes):
    """
    A helper for generating the ``includes[]`` parameter for queries.

    Parameters
    -----------
    manga: :class:`bool`
        Defaults to ``True``. Whether to include manga in the relationships.
    """

    __slots__ = ("manga",)

    def __init__(self, *, manga: bool = True) -> None:
        self.manga: bool = manga

    def to_query(self) -> list[str]:
        """Generates a list of strings based on the kwargs.

        Returns
        --------
        List[:class:`str`]
            The list of query parameters (pre-PHP formatting).
        """
        return super().to_query()


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

    __slots__ = (
        "manga",
        "user",
        "scanlation_group",
    )

    def __init__(self, *, manga: bool = True, user: bool = True, scanlation_group: bool = True) -> None:
        self.manga: bool = manga
        self.user: bool = user
        self.scanlation_group: bool = scanlation_group

    def to_query(self) -> list[str]:
        """Returns a list of valid query strings.

        Returns
        --------
        List[:class:`str`]
            The list of query parameters (pre-PHP formatting).
        """
        return super().to_query()


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
        --------
        List[:class:`str`]
            The list of query parameters (pre-PHP formatting).
        """
        return super().to_query()


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

    __slots__ = (
        "manga",
        "user",
        "owner",
    )

    def __init__(self, *, manga: bool = True, user: bool = True, owner: bool = True) -> None:
        self.manga: bool = manga
        self.user: bool = user
        self.owner: bool = owner

    def to_query(self) -> list[str]:
        """Returns a list of valid query strings."""
        return super().to_query()


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

    __slots__ = (
        "author",
        "artist",
        "cover_art",
        "manga",
    )

    def __init__(self, *, author: bool = True, artist: bool = True, cover_art: bool = True, manga: bool = True) -> None:
        self.author: bool = author
        self.artist: bool = artist
        self.cover_art: bool = cover_art
        self.manga: bool = manga

    def to_query(self) -> list[str]:
        """Returns a list of valid query strings.

        Returns
        --------
        List[:class:`str`]
            The list of query parameters (pre-PHP formatting).
        """
        return super().to_query()


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
        --------
        List[:class:`str`]
            The list of query parameters (pre-PHP formatting).
        """
        return super().to_query()
