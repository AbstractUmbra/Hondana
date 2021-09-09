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

import datetime
import json
import pathlib
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Mapping, Optional, TypeVar, Union

from .errors import AuthenticationRequired


if TYPE_CHECKING:
    from typing_extensions import Concatenate, ParamSpec

    from .client import Client


C = TypeVar("C", bound="Client")
T = TypeVar("T")
if TYPE_CHECKING:
    B = ParamSpec("B")


__all__ = ("MISSING", "to_json", "to_iso_format", "php_query_builder", "TAGS")

_PROJECT_DIR = pathlib.Path(__file__)


class MissingSentinel:
    def __eq__(self, _: Any) -> bool:
        return False

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return "..."


MISSING: Any = MissingSentinel()


def require_authentication(func: Callable[Concatenate[C, B], T]) -> Callable[Concatenate[C, B], T]:
    @wraps(func)
    def wrapper(client: C, *args: B.args, **kwargs: B.kwargs) -> T:
        if not client._http._authenticated:
            raise AuthenticationRequired("This method requires you to be authenticated to the API.")

        return func(client, *args, **kwargs)

    return wrapper


def to_json(obj: Any) -> str:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=True)


def to_iso_format(in_: datetime.datetime) -> str:
    return f"{in_:%Y-%m-%dT%H:%M:%S}"


def php_query_builder(obj: Mapping[str, Optional[Union[str, int, bool, list[str], dict[str, str]]]]) -> str:
    """
    {"order": {"publishAt": "desc"}, "translatedLanguages": ["en", "jp"]}
    ->
    "order[publishAt]=desc&translatedLanguages[]=en&translatedLanguages[]=jp"
    """
    fmt = []
    for key, value in obj.items():
        if value is None or value is MISSING:
            fmt.append(f"{key}=null")
        if isinstance(value, (str, int, bool)):
            fmt.append(f"{key}={str(value)}")
        elif isinstance(value, list):
            fmt.extend(f"{key}[]={item}" for item in value)
        elif isinstance(value, dict):
            fmt.extend(f"{key}[{subkey}]={subvalue}" for subkey, subvalue in value.items())

    return "&".join(fmt)


path: pathlib.Path = _PROJECT_DIR.parent / "extras" / "tags.json"
with open(path, "r") as _fp:
    TAGS: dict[str, list[str]] = json.load(_fp)
