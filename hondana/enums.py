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

from .utils import _REPORT_REASONS, _StrEnum


if TYPE_CHECKING:
    from typing_extensions import TypeAlias

__all__ = (
    "ContentRating",
    "PublicationDemographic",
    "CustomListVisibility",
    "ReportCategory",
    "ReportStatus",
    "MangaStatus",
    "ReadingStatus",
    "MangaState",
    "MangaRelationType",
    "AuthorReportReason",
    "ChapterReportReason",
    "ScanlationGroupReportReason",
    "MangaReportReason",
    "UserReportReason",
    "ReportReason",
)


class Order(_StrEnum):
    ascending = "asc"
    descending = "desc"


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


class ReportStatus(_StrEnum):
    waiting = "waiting"
    accepted = "accepted"
    refused = "refused"
    autoresolved = "autoresolved"


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


class AuthorReportReason(_StrEnum):
    duplicate_entry = _REPORT_REASONS["author"]["duplicate_entry"]
    information_to_correct = _REPORT_REASONS["author"]["information_to_correct"]
    other = _REPORT_REASONS["author"]["other"]
    troll_entry = _REPORT_REASONS["author"]["troll_entry"]


class ChapterReportReason(_StrEnum):
    credit_page_in_the_middle_of_the_chapter = _REPORT_REASONS["chapter"]["credit_page_in_the_middle_of_the_chapter"]
    duplicate_upload_from_same_user_or_group = _REPORT_REASONS["chapter"]["duplicate_upload_from_same_user_or_group"]
    extraneous_political_or_racebaiting_or_offensive_content = _REPORT_REASONS["chapter"][
        "extraneous_political_or_racebaiting_or_offensive_content"
    ]
    fake_or_spam_chapter = _REPORT_REASONS["chapter"]["fake_or_spam_chapter"]
    group_lock_evasion = _REPORT_REASONS["chapter"]["group_lock_evasion"]
    images_not_loading = _REPORT_REASONS["chapter"]["images_not_loading"]
    incorrect_chapter_number = _REPORT_REASONS["chapter"]["incorrect_chapter_number"]
    incorrect_group = _REPORT_REASONS["chapter"]["incorrect_group"]
    incorrect_or_duplicate_pages = _REPORT_REASONS["chapter"]["incorrect_or_duplicate_pages"]
    incorrect_or_missing_chapter_title = _REPORT_REASONS["chapter"]["incorrect_or_missing_chapter_title"]
    incorrect_or_missing_volume_number = _REPORT_REASONS["chapter"]["incorrect_or_missing_volume_number"]
    missing_pages = _REPORT_REASONS["chapter"]["missing_pages"]
    naming_rules_broken = _REPORT_REASONS["chapter"]["naming_rules_broken"]
    official_release_or_raw = _REPORT_REASONS["chapter"]["official_release_or_raw"]
    other = _REPORT_REASONS["chapter"]["other"]
    pages_out_of_order = _REPORT_REASONS["chapter"]["pages_out_of_order"]
    released_before_raws_released = _REPORT_REASONS["chapter"]["released_before_raws_released"]
    uploaded_on_wrong_manga = _REPORT_REASONS["chapter"]["uploaded_on_wrong_manga"]
    watermarked_images = _REPORT_REASONS["chapter"]["watermarked_images"]


class ScanlationGroupReportReason(_StrEnum):
    duplicate_entry = _REPORT_REASONS["scanlation_group"]["duplicate_entry"]
    group_claim_request = _REPORT_REASONS["scanlation_group"]["group_claim_request"]
    inactivity_request = _REPORT_REASONS["scanlation_group"]["inactivity_request"]
    information_to_correct = _REPORT_REASONS["scanlation_group"]["information_to_correct"]
    other = _REPORT_REASONS["scanlation_group"]["other"]
    troll_entry = _REPORT_REASONS["scanlation_group"]["troll_entry"]


class MangaReportReason(_StrEnum):
    duplicate_entry = _REPORT_REASONS["manga"]["duplicate_entry"]
    information_to_correct = _REPORT_REASONS["manga"]["information_to_correct"]
    other = _REPORT_REASONS["manga"]["other"]
    troll_entry = _REPORT_REASONS["manga"]["troll_entry"]


class UserReportReason(_StrEnum):
    offensive_username_or_biography_or_avatar = _REPORT_REASONS["user"]["offensive_username_or_biography_or_avatar"]
    other = _REPORT_REASONS["user"]["other"]
    spambot = _REPORT_REASONS["user"]["spambot"]


ReportReason: TypeAlias = Union[
    AuthorReportReason, ChapterReportReason, ScanlationGroupReportReason, MangaReportReason, UserReportReason
]
