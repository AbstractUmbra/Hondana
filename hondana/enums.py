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

from enum import Enum


__all__ = (
    "ContentRating",
    "PublicationDemographic",
    "CustomListVisibility",
    "ReportCategory",
    "MangaStatus",
    "ReadingStatus",
    "MangaState",
    "MangaRelationType",
)


class _StrEnum(Enum):
    value: str

    def __str__(self) -> str:
        return self.value


class ContentRating(_StrEnum):
    safe = "safe"
    suggestive = "suggestive"
    erotica = "erotica"
    pornographic = "pornographic"


class PublicationDemographic(_StrEnum):
    shounen = "shounen"
    shoujo = "shoujo"
    josei = "josei"
    seinen = "seinen"


class CustomListVisibility(_StrEnum):
    public = "public"
    private = "private"


class ReportCategory(_StrEnum):
    manga = "manga"
    chapter = "chapter"
    scanlation_group = "scanlation_group"
    user = "user"
    author = "author"


class MangaStatus(_StrEnum):
    ongoing = "ongoing"
    completed = "completed"
    hiatus = "hiatus"
    cancelled = "cancelled"


class ReadingStatus(_StrEnum):
    reading = "reading"
    on_hold = "on_hold"
    plan_to_read = "plan_to_read"
    dropped = "dropped"
    re_reading = "re_reading"
    completed = "completed"


class MangaState(_StrEnum):
    draft = "draft"
    submitted = "submitted"
    published = "published"
    rejected = "rejected"


class MangaRelationType(_StrEnum):
    monochrome = "monochrome"
    main_story = "main_story"
    adapted_from = "adapted_from"
    based_on = "based_on"
    prequel = "prequel"
    side_story = "side_story"
    doujinshi = "doujinshi"
    same_franchise = "same_franchise"
    shared_universe = "shared_universe"
    sequel = "sequel"
    spin_off = "spin_off"
    alternate_story = "alternate_story"
    preserialization = "preserialization"
    colored = "colored"
    serialization = "serialization"
    alternate_version = "alternate_version"
