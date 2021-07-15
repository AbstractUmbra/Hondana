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
import json
import pathlib
from typing import Any, Mapping, Union


__all__ = ("to_json", "php_query_builder", "TAGS")

_PROJECT_DIR = pathlib.Path(__file__)


def to_json(obj: Any) -> str:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=True)


def php_query_builder(obj: Mapping[str, Union[str, int, bool, list[str], dict[str, str]]]) -> str:
    """
    {"order": {"publishAt": "desc"}, "translatedLanguages": ["en", "jp"]}
    ->
    "order[publishAt]=desc&translatedLanguages[]=en&translatedLanguages[]=jp"
    """
    fmt = []
    for key, value in obj.items():
        if isinstance(value, (str, int, bool)):
            fmt.append(f"{key}={value}")
        elif isinstance(value, list):
            fmt.extend(f"{key}[]={item}" for item in value)
        elif isinstance(value, dict):
            fmt.extend(f"{key}[{subkey}]={subvalue}" for subkey, subvalue in value.items())

    return "&".join(fmt)


path = _PROJECT_DIR.parent / "extras" / "tags.json"
with open(path, "r") as fp:
    TAGS: dict[str, list[str]] = json.load(fp)
