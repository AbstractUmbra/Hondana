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

import asyncio
import datetime
import json
import logging
import pathlib
import re
from functools import wraps
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Iterable,
    Mapping,
    Optional,
    TypeVar,
    Union,
)
from urllib.parse import quote as _uriquote

import aiohttp

from .errors import AuthenticationRequired


if TYPE_CHECKING:
    from typing_extensions import Concatenate, ParamSpec


C = TypeVar("C", bound="Any")
T = TypeVar("T")
if TYPE_CHECKING:
    B = ParamSpec("B")


LOGGER = logging.getLogger(__name__)

__all__ = (
    "MANGADEX_URL_REGEX",
    "MANGADEX_TIME_REGEX",
    "MISSING",
    "Route",
    "CustomRoute",
    "to_json",
    "json_or_text",
    "to_iso_format",
    "php_query_builder",
    "to_snake_case",
    "to_camel_case",
    "get_image_mime_type",
    "as_chunks",
    "delta_to_iso",
    "MANGA_TAGS",
)

_PROJECT_DIR = pathlib.Path(__file__)
MANGADEX_URL_REGEX = re.compile(
    r"(?:http[s]?:\/\/)?mangadex\.org\/(?P<type>title|chapter|author|tag)\/(?P<ID>[a-z0-9]{8}\-[a-z0-9]{4}\-[a-z0-9]{4}\-[a-z0-9]{4}\-[a-z0-9]{12})\/?(?P<title>.*)"
)
MANGADEX_TIME_REGEX = re.compile(
    r"^(P([1-9]|[1-9][0-9])D)?(P?([1-9])W)?(P?T(([1-9]|1[0-9]|2[0-4])H)?(([1-9]|[1-5][0-9]|60)M)?(([1-9]|[1-5][0-9]|60)S)?)?$"
)
"""
``r"^(P([1-9]|[1-9][0-9])D)?(P?([1-9])W)?(P?T(([1-9]|1[0-9]|2[0-4])H)?(([1-9]|[1-5][0-9]|60)M)?(([1-9]|[1-5][0-9]|60)S)?)?$"``

This `regex pattern <https://docs.python.org/3/library/re.html#re-objects>`_ follows the ISO-8601 standard (MangaDex uses `PHP DateInterval <https://www.php.net/manual/en/dateinterval.construct.php>`_).
The pattern *is* usable but more meant as a guideline for your formatting.

It matches some things like: ``P1D2W`` (1 day, two weeks), ``P1D2WT3H4M`` (1 day, 2 weeks, 3 hours and 4 minutes)
"""


class Route:
    """A helper class for instantiating a HTTP method to MangaDex.

    Parameters
    -----------
    verb: :class:`str`
        The HTTP verb you wish to perform, e.g. ``"POST"``
    path: :class:`str`
        The prepended path to the API endpoint you with to target.
        e.g. ``"/manga/{manga_id}"``
    parameters: Any
        This is a special cased kwargs. Anything passed to these will substitute it's key to value in the `path`.
        E.g. if your `path` is ``"/manga/{manga_id}"``, and your parameters are ``manga_id="..."``, then it will expand into the path
        making ``"manga/..."``
    """

    BASE: ClassVar[str] = "https://api.mangadex.org"

    def __init__(self, verb: str, path: str, **parameters: Any) -> None:
        self.verb: str = verb
        self.path: str = path
        url = self.BASE + self.path
        if parameters:
            url = url.format_map({k: _uriquote(v) if isinstance(v, str) else v for k, v in parameters.items()})
        self.url: str = url


class CustomRoute(Route):
    """A helper class for instantiating a HTTP method to download from MangaDex.

    Parameters
    -----------
    verb: :class:`str`
        The HTTP verb you wish to perform. E.g. ``"POST"``
    base: :class:`str`
        The base URL for the download path.
    path: :class:`str`
        The prepended path to the API endpoint you with to target.
        e.g. ``"/manga/{manga_id}"``
    parameters: Any
        This is a special cased kwargs. Anything passed to these will substitute it's key to value in the `path`.
        E.g. if your `path` is ``"/manga/{manga_id}"``, and your parameters are ``manga_id="..."``, then it will expand into the path
        making ``"manga/..."``
    """

    def __init__(self, verb: str, base: str, path: str, **parameters: Any) -> None:
        self.verb: str = verb
        self.base: str = base
        self.path: str = path
        url = self.base + self.path
        if parameters:
            url = url.format_map({k: _uriquote(v) if isinstance(v, str) else v for k, v in parameters.items()})
        self.url: str = url


class MissingSentinel:
    def __eq__(self, _: Any) -> bool:
        return False

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return "..."


MISSING: Any = MissingSentinel()


def require_authentication(func: Callable[Concatenate[C, B], T]) -> Callable[Concatenate[C, B], T]:
    """A decorator to assure the `self` parameter of decorated methods has authentication set."""

    @wraps(func)
    def wrapper(item: C, *args: B.args, **kwargs: B.kwargs) -> T:
        if not item._http._authenticated:
            raise AuthenticationRequired("This method requires you to be authenticated to the API.")

        return func(item, *args, **kwargs)

    return wrapper


def to_json(obj: Any) -> str:
    """A quick object that dumps a Python type to JSON object."""
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=True)


async def json_or_text(response: aiohttp.ClientResponse) -> Union[dict[str, Any], str]:
    """A quick method to parse a `aiohttp.ClientResponse` and test if it's json or text."""
    text = await response.text(encoding="utf-8")
    try:
        if response.headers["content-type"] == "application/json":
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass
    except KeyError:
        pass

    return text


def to_iso_format(in_: datetime.datetime) -> str:
    """Quick function to dump a `datetime.datetime` to acceptable ISO 8601 format."""
    return f"{in_:%Y-%m-%dT%H:%M:%S}"


def php_query_builder(obj: Mapping[str, Optional[Union[str, int, bool, list[str], dict[str, str]]]]) -> str:
    """
    {"order": {"publishAt": "desc"}, "translatedLanguages": ["en", "jp"]}
    ->
    "order[publishAt]=desc&translatedLanguages[]=en&translatedLanguages[]=jp"
    """
    fmt = []
    for key, value in obj.items():
        if value is None:
            fmt.append(f"{key}=null")
        elif isinstance(value, bool):
            fmt.append(f"{key}={str(value).lower()}")
        elif isinstance(value, (str, int)):
            fmt.append(f"{key}={value}")
        elif isinstance(value, list):
            fmt.extend(f"{key}[]={item}" for item in value)
        elif isinstance(value, dict):
            fmt.extend(f"{key}[{subkey}]={subvalue}" for subkey, subvalue in value.items())

    return "&".join(fmt)


def get_image_mime_type(data: bytes) -> str:
    """Returns the image type from the first few bytes."""
    if data.startswith(b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"):
        return "image/png"
    elif data[0:3] == b"\xff\xd8\xff" or data[6:10] in (b"JFIF", b"Exif"):
        return "image/jpeg"
    elif data.startswith((b"\x47\x49\x46\x38\x37\x61", b"\x47\x49\x46\x38\x39\x61")):
        return "image/gif"
    elif data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "image/webp"
    else:
        raise ValueError("Unsupported image type given")


def to_snake_case(string: str) -> str:
    """Quick function to return snake_case from camelCase."""
    fmt: list[str] = []
    for character in string:
        if character.isupper():
            fmt.append(f"_{character.lower()}")
            continue
        fmt.append(character)
    return "".join(fmt)


def to_camel_case(string: str) -> str:
    """Quick function to return camelCase from snake_case."""
    first, *rest = string.split("_")
    chunks = [first.lower(), *map(str.capitalize, rest)]

    return "".join(chunks)


def as_chunks(iterator: Iterable[T], max_size: int) -> Iterable[list[T]]:
    ret = []
    n = 0
    for item in iterator:
        ret.append(item)
        n += 1
        if n == max_size:
            yield ret
            ret = []
            n = 0
    if ret:
        yield ret


def delta_to_iso(delta: datetime.timedelta) -> str:
    seconds = round(delta.total_seconds())
    weeks, seconds = divmod(seconds, 60 * 60 * 24 * 7)
    days, seconds = divmod(seconds, 60 * 60 * 24)
    hours, seconds = divmod(seconds, 60 * 60)
    minutes, seconds = divmod(seconds, 60)

    builder = "P" * bool(weeks or days)
    if days:
        builder += f"{days}D"
    if weeks:
        builder += f"{weeks}W"

    builder += "T" * bool(hours or minutes or seconds)

    if hours:
        builder += f"{hours}H"
    if minutes:
        builder += f"{minutes}M"
    if seconds:
        builder += f"{seconds}S"

    return builder


_path: pathlib.Path = _PROJECT_DIR.parent / "extras" / "tags.json"
with open(_path, "r") as _fp:
    MANGA_TAGS: dict[str, str] = json.load(_fp)


def __build_tags():  # type: ignore  # This is for pre-flight release usage only.
    async def build():
        from . import Client

        client = Client()
        tags = await client.update_tags()

        _diff_a = set(map(str.lower, MANGA_TAGS))
        _diff_b = set(map(str.lower, tags))

        if diff := (_diff_b ^ _diff_a):
            print(f"Tags have changed: {', '.join(diff)}")
        else:
            print("No tag changes.")

        await client.close()

    asyncio.run(build())
