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

from typing import Literal, TypedDict


__all__ = (
    "PublicationDemographic",
    "ContentRating",
    "LanguageCode",
    "LocalizedString",
    "LocalisedString",
)

PublicationDemographic = Literal["shounen", "shoujo", "josei", "seinen"]
ContentRating = Literal["safe", "suggestive", "erotica", "pornographic"]
LanguageCode = Literal[
    "en",
    "ja",
    "pl",
    "sh",
    "nl",
    "it",
    "ru",
    "de",
    "hu",
    "fr",
    "fi",
    "vi",
    "el",
    "bg",
    "es",
    "pt-br",
    "pt",
    "sv",
    "ar",
    "da",
    "zh",
    "bn",
    "ro",
    "cs",
    "mn",
    "tr",
    "id",
    "ko",
    "es-la",
    "fa",
    "ms",
    "th",
    "ca",
    "tl",
    "zh-hk",
    "uk",
    "my",
    "lt",
    "he",
    "hi",
    "no",
]


class LocalizedString(TypedDict):
    """
    Examples
    ---------
    A localised string: ::

        {"en": "An english string"}
        {"fr": "Une corde française"}


    language_code: :class:`str`
        The shorthand language code for the target item.

    item: :class:`str`
        The localized item.
    """

    language_code: str
    item: str


LocalisedString = LocalizedString
