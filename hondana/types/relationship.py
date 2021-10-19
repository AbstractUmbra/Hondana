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

from typing import TYPE_CHECKING, Union


if TYPE_CHECKING:
    from . import artist, author, chapter, manga, scanlator_group, user


__all__ = ("RelationshipResponse",)


RelationshipResponse = Union[
    "manga.MangaResponse",
    "chapter.ChapterResponse",
    "artist.ArtistResponse",
    "author.AuthorResponse",
    "user.UserResponse",
    "scanlator_group.ScanlationGroupResponse",
]
"""
id: :class:`str`

type: Literal[``"manga"``, ``"chapter"``, ``"scanlation_group"``, ``"author"``, ``"cover_art"``, ``"artist"``]

attributes: Dict[:class:`str`, :class:`str`]
    This key is optional

    This key can contain minimal or full data depending on the ``includes[]`` parameter of it's request.
    See here for more info: https://api.mangadex.org/docs.html#section/Reference-Expansion

relationships: List[Dict[:class:`str`, :class:`str`]]
    This key is optional

    This key will be a one level nested list of relationships for each object in the relationship.
"""
