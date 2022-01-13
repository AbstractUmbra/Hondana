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
    "LanguageCode",
    "LocalizedString",
    "LocalisedString",
)

LanguageCode = Literal[
    "ar",
    "bg",
    "bn",
    "ca",
    "cs",
    "da",
    "de",
    "el",
    "en",
    "es-la",
    "es",
    "fa",
    "fi",
    "fr",
    "he",
    "hi",
    "hu",
    "id",
    "it",
    "ja",
    "ja-ro",
    "ko",
    "ko-ro",
    "lt",
    "mn",
    "ms",
    "my",
    "nl",
    "no",
    "pl",
    "pt-br",
    "pt",
    "ro",
    "ru",
    "sh",
    "sv",
    "th",
    "tl",
    "tr",
    "uk",
    "vi",
    "zh-hk",
    "zh",
    "zh-ro",
]


LocalizedString = TypedDict(
    "LocalizedString",
    {
        "ar": str,
        "bg": str,
        "bn": str,
        "ca": str,
        "cs": str,
        "da": str,
        "de": str,
        "el": str,
        "en": str,
        "es-la": str,
        "es": str,
        "fa": str,
        "fi": str,
        "fr": str,
        "he": str,
        "hi": str,
        "hu": str,
        "id": str,
        "it": str,
        "ja": str,
        "ja-ro": str,
        "ko": str,
        "ko-ro": str,
        "lt": str,
        "mn": str,
        "ms": str,
        "my": str,
        "nl": str,
        "no": str,
        "pl": str,
        "pt-br": str,
        "pt": str,
        "ro": str,
        "ru": str,
        "sh": str,
        "sv": str,
        "th": str,
        "tl": str,
        "tr": str,
        "uk": str,
        "vi": str,
        "zh-hk": str,
        "zh": str,
        "zh-ro": str,
    },
    total=False,
)
"""
Examples
---------
A localised string: ::

    {"en": "An english string"}
    {"fr": "Une corde française"}

"""
LocalisedString = LocalizedString
