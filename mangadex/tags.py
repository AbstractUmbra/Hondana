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
from typing import Optional

from .utils import TAGS


__all__ = ("Tags",)


class Tags:
    def __init__(self, *tags: str, mode: str = "AND"):
        self._tags = list(tags)
        self.tags: Optional[list[str]] = None
        self.mode = mode.upper()
        if self.mode not in {"AND", "OR"}:
            raise TypeError("Tags mode has to be 'AND' or 'OR'.")
        self.set_tags()

    def __repr__(self) -> str:
        if self.tags is None:
            tags = self.set_tags()
        else:
            tags = self.tags

        assert self.tags is not None
        if len(self.tags) > 5:
            tags = ", ".join(self.tags[:5])
            tags += "..."
        else:
            tags = ", ".join(self.tags)
        return f"<Tags mode={self.mode}>"

    def set_tags(self) -> list[str]:
        tags = []
        for tag in self._tags:
            tags.append(TAGS.get(tag.title()))

        if not tags:
            raise ValueError("No tags passed matched any valid MangaDex tags.")

        self.tags = tags
        return self.tags
