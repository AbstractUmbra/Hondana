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

from .enums import ForumThreadType

if TYPE_CHECKING:
    from .http import HTTPClient
    from .types_.forums import ForumDataResponse
    from .types_.statistics import CommentMetaData

__all__ = (
    "ChapterComments",
    "ForumThread",
    "MangaComments",
    "ScanlatorGroupComments",
)


class _Comments:
    """
    A helper object around the forum threads/comments of a type in the MangaDex API.

    Attributes
    ----------
    parent_id: :class:`str`
        The ID of the parent object (which this comment data belongs to).
    thread_id: :class:`int`
        The ID of the thread on the MangaDex forums.
    reply_count: :class:`int`
        The amount of replies (comments) this object has in total.
    """

    __slots__ = ("__thread", "_data", "_http", "parent_id", "reply_count", "thread_id")
    __inner_type__: ForumThreadType

    def __init__(self, http: HTTPClient, comment_payload: CommentMetaData, parent_id: str, /) -> None:
        self._data: CommentMetaData = comment_payload
        self._http: HTTPClient = http
        self.parent_id: str = parent_id
        self.thread_id: int = self._data["threadId"]
        self.reply_count: int = self._data["repliesCount"]
        self.__thread: ForumThread | None = None

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"thread_id={self.thread_id} "
            f"reply_count={self.reply_count} "
            f"parent_id={self.parent_id!r}>"
        )

    @property
    def thread(self) -> ForumThread | None:
        """The objects thread, if it exists.

        Returns
        -------
        Optional[:class:`~hondana.ForumThread`]
            The ForumThread relating to this object, if it exists already.
            See :meth:`fetch_thread` to fetch the thread and cache it here.
        """
        return self.__thread

    async def fetch_thread(self, *, force: bool = False) -> ForumThread:
        """|coro|

        This method will fetch a forum thread from the API.

        It does however function as a "create or fetch" API request.

        Parameters
        ----------
        force: :class:`bool`
            Whether to avoid the potentially cached thread and fetch an updated one and cache it.
            Defaults to ``False``.

        Raises
        ------
        Forbidden
            You must be authenticated to fetch/use threads/forums.
        NotFound
            The parent_id doesn't or no longer exists.

        Returns
        -------
        :class:`~hondana.ForumThread`
            The cached or fetched ForumThread.
        """  # noqa: DOC502 # raised in method call
        if self.thread and not force:
            return self.thread

        thread_payload = await self._http.create_forum_thread(thread_type=self.__inner_type__, resource_id=self.parent_id)

        forum_thread = ForumThread(self._http, thread_payload["data"])
        self.__thread = forum_thread

        return self.__thread


class MangaComments(_Comments):
    """
    A helper object around the forum threads/comments of Manga in the MangaDex API.

    Attributes
    ----------
    parent_id: :class:`str`
        The ID of the parent object (which this comment data belongs to).
    thread_id: :class:`int`
        The ID of the thread on the MangaDex forums.
    reply_count: :class:`int`
        The amount of replies (comments) this object has in total.
    """

    __inner_type__ = ForumThreadType.manga


class ChapterComments(_Comments):
    """
    A helper object around the forum threads/comments of Chapter in the MangaDex API.

    Attributes
    ----------
    parent_id: :class:`str`
        The ID of the parent object (which this comment data belongs to).
    thread_id: :class:`int`
        The ID of the thread on the MangaDex forums.
    reply_count: :class:`int`
        The amount of replies (comments) this object has in total.
    """

    __inner_type__ = ForumThreadType.chapter


class ScanlatorGroupComments(_Comments):
    """
    A helper object around the forum threads/comments of Scanlator Group in the MangaDex API.

    Attributes
    ----------
    parent_id: :class:`str`
        The ID of the parent object (which this comment data belongs to).
    thread_id: :class:`int`
        The ID of the thread on the MangaDex forums.
    reply_count: :class:`int`
        The amount of replies (comments) this object has in total.
    """

    __inner_type__ = ForumThreadType.scanlation_group


class ForumThread:
    """
    A small helper object around ForumThreads in the MangaDex API.

    Attributes
    ----------
    id: :class:`int`
        The ID relating to this thread on the forums subdomain of MangaDex.
    replies_count: :class:`int`
        The amount of comments/replies the parent object has in total.
    """

    __slots__ = (
        "_attributes",
        "_data",
        "_http",
        "id",
        "replies_count",
    )

    def __init__(self, http: HTTPClient, payload: ForumDataResponse, /) -> None:
        self._http: HTTPClient = http
        self._data: ForumDataResponse = payload
        self.id: int = self._data["id"]
        self.replies_count: int = self._data["attributes"]["repliesCount"]

    @property
    def url(self) -> str:
        """Returns the url to this objects forum.

        Returns
        -------
        :class:`str`
            The URL.
        """
        return f"https://forums.mangadex.org/threads/{self.id}"
