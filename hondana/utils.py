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
import logging
import pathlib
import re
import warnings
from enum import Enum
from functools import wraps
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Generic,
    Iterable,
    Literal,
    Mapping,
    Optional,
    Type,
    TypedDict,
    TypeVar,
    Union,
    overload,
)
from urllib.parse import quote as _uriquote

import aiohttp
import multidict
from yarl import URL


try:
    import orjson
except ModuleNotFoundError:
    HAS_ORJSON = False
else:
    HAS_ORJSON = True

from .errors import AuthenticationRequired


if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison
    from typing_extensions import Concatenate, ParamSpec

    from .types.artist import ArtistResponse
    from .types.author import AuthorResponse
    from .types.chapter import ChapterResponse
    from .types.cover import CoverResponse
    from .types.manga import MangaResponse
    from .types.relationship import RelationshipResponse
    from .types.scanlator_group import ScanlationGroupResponse
    from .types.user import UserResponse

C = TypeVar("C", bound="Any")
T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
if TYPE_CHECKING:
    B = ParamSpec("B")


LOGGER = logging.getLogger(__name__)

__all__ = (
    "MANGADEX_URL_REGEX",
    "MANGADEX_TIME_REGEX",
    "MISSING",
    "Route",
    "CustomRoute",
    "cached_slot_property",
    "to_json",
    "json_or_text",
    "php_query_builder",
    "deprecated",
    "to_snake_case",
    "to_camel_case",
    "get_image_mime_type",
    "as_chunks",
    "delta_to_iso",
    "iso_to_delta",
    "relationship_finder",
    "clean_isoformat",
    "MANGA_TAGS",
)

_PROJECT_DIR = pathlib.Path(__file__)
MAX_DEPTH: int = 10_000
MANGADEX_URL_REGEX = re.compile(
    r"(?:http[s]?:\/\/)?mangadex\.org\/(?P<type>title|chapter|author|tag)\/(?P<ID>[a-z0-9]{8}\-[a-z0-9]{4}\-[a-z0-9]{4}\-[a-z0-9]{4}\-[a-z0-9]{12})\/?(?P<title>.*)"
)
r"""
``r"(?:http[s]?:\/\/)?mangadex\.org\/(?P<type>title|chapter|author|tag)\/(?P<ID>[a-z0-9]{8}\-[a-z0-9]{4}\-[a-z0-9]{4}\-[a-z0-9]{4}\-[a-z0-9]{12})\/?(?P<title>.*)"``

This `regex pattern <https://docs.python.org/3/library/re.html#re-objects>`_ can be used to isolate common elements from a MangaDex URL.
This means that Manga, Chapter, Author or Tag urls can be parsed for their ``type``, ``ID`` and ``title``.
"""

MANGADEX_TIME_REGEX = re.compile(
    r"^(P(?P<days>[1-9]|[1-9][0-9])D)?(P?(?P<weeks>[1-9])W)?(P?T((?P<hours>[1-9]|1[0-9]|2[0-4])H)?((?P<minutes>[1-9]|[1-5][0-9]|60)M)?((?P<seconds>[1-9]|[1-5][0-9]|60)S)?)?$"
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
        self.url: URL = URL(url, encoded=True)


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
        self.url: URL = URL(url, encoded=True)


class MissingSentinel:
    def __eq__(self, _: Any) -> bool:
        return False

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return "..."


MISSING: Any = MissingSentinel()


class _StrEnum(Enum):  # type: ignore # we import this as needed.
    value: str

    def __str__(self) -> str:
        return self.value


## This class and subsequent decorator have been copied from Rapptz' Discord.py
## (https://github.com/Rapptz/discord.py)
## Credit goes to Rapptz and contributors


class CachedSlotProperty(Generic[T, T_co]):
    def __init__(self, name: str, function: Callable[[T], T_co]) -> None:
        self.name: str = name
        self.function: Callable[[T], T_co] = function
        self.__doc__ = getattr(function, "__doc__")

    @overload
    def __get__(self, instance: None, owner: Type[T]) -> CachedSlotProperty[T, T_co]:
        ...

    @overload
    def __get__(self, instance: T, owner: Type[T]) -> T_co:
        ...

    def __get__(self, instance: Optional[T], owner: Type[T]) -> Any:
        if instance is None:
            return self

        try:
            return getattr(instance, self.name)
        except AttributeError:
            value = self.function(instance)
            setattr(instance, self.name, value)
            return value


def cached_slot_property(name: str, /) -> Callable[[Callable[[T], T_co]], CachedSlotProperty[T, T_co]]:
    def decorator(func: Callable[[T], T_co]) -> CachedSlotProperty[T, T_co]:
        return CachedSlotProperty(name, func)

    return decorator


def require_authentication(func: Callable[Concatenate[C, B], T]) -> Callable[Concatenate[C, B], T]:
    """A decorator to assure the `self` parameter of decorated methods has authentication set."""

    @wraps(func)
    def wrapper(item: C, *args: B.args, **kwargs: B.kwargs) -> T:
        if not item._http._authenticated:
            raise AuthenticationRequired("This method requires you to be authenticated to the API.")

        return func(item, *args, **kwargs)

    return wrapper


def deprecated(alternate: Optional[str] = None, /) -> Callable[[Callable[B, T]], Callable[B, T]]:
    """A decorator to mark a method as deprecated.

    Parameters
    -----------
    alternate: Optional[:class:`str`]
        The alternate method to use.
    """

    def decorator(func: Callable[B, T]) -> Callable[B, T]:
        @wraps(func)
        def wrapper(*args: B.args, **kwargs: B.kwargs) -> T:
            warnings.simplefilter("always", DeprecationWarning)  # turn off filter.
            if alternate is not None:
                fmt = "{0.__qualname__} is deprecated, use {1} instead."
            else:
                fmt = "{0.__qualname__} is deprecated."

            warnings.warn(fmt.format(func, alternate), stacklevel=2, category=DeprecationWarning)

            warnings.simplefilter("default", DeprecationWarning)  # reset filter.
            return func(*args, **kwargs)

        return wrapper

    return decorator


def calculate_limits(limit: int, offset: int, /, *, max_limit: int = 100) -> tuple[int, int]:
    """A helper function that will calculate the offset and limit parameters for API endpoints.

    Parameters
    -----------
    limit: :class:`int`
        The limit (or amount) of objects you are requesting.
    offset: :class:`int`
        The offset (or pagination start point) for the objects you are requesting.
    max_limit: :class:`int`
        The maximum limit value for the API Endpoint.

    Raises
    -------
    :exc:`ValueError`
        Exceeding the maximum pagination limit.

    Returns
    --------
    Tuple[:class:`int`, :class:`int`]
    """
    if offset >= MAX_DEPTH:
        raise ValueError(f"An offset of {MAX_DEPTH} will not return results.")

    offset = max(offset, 0)

    difference = MAX_DEPTH - offset
    if difference <= max_limit:
        new_limit = difference
        new_offset = MAX_DEPTH - new_limit
        return new_limit, new_offset

    new_limit = min(max(0, limit), max_limit)
    new_offset = min(max(0, offset), MAX_DEPTH - new_limit)

    return new_limit, new_offset


if HAS_ORJSON is True:

    def to_json(obj: Any, /) -> str:
        """A quick method that dumps a Python type to JSON object."""
        return orjson.dumps(obj).decode("utf-8")

    _from_json = orjson.loads  # type: ignore # this is guarded in an if.

else:

    def to_json(obj: Any, /) -> str:
        """A quick method that dumps a Python type to JSON object."""
        return json.dumps(obj, separators=(",", ":"), ensure_ascii=True)

    _from_json = json.loads


async def json_or_text(response: aiohttp.ClientResponse, /) -> Union[dict[str, Any], str]:
    """A quick method to parse a `aiohttp.ClientResponse` and test if it's json or text."""
    text = await response.text(encoding="utf-8")
    try:
        if response.headers["content-type"] == "application/json":
            try:
                return _from_json(text)
            except json.JSONDecodeError:
                pass
    except KeyError:
        pass

    return text


def php_query_builder(
    obj: Mapping[str, Optional[Union[str, int, bool, list[str], dict[str, str]]]], /
) -> multidict.MultiDict[Union[str, int]]:
    """
    A helper function that builds a MangaDex (PHP) query string from a mapping.

    Parameters
    -----------
    obj: Mapping[:class:`str`, Optional[Union[:class:`str`, :class:`int`, :class:`bool`, List[:class:`str`], Dict[:class:`str`, :class:`str`]]]]
        The mapping to build the query string from.

    Returns
    --------
    :class:`multidict.MultiDict`
        A dictionary/mapping type that allows for duplicate keys.
    """
    fmt = multidict.MultiDict[Union[str, int]]()
    for key, value in obj.items():
        if value is None:
            fmt.add(key, "null")
        elif isinstance(value, str):
            fmt.add(key, value)
        elif isinstance(value, bool):
            fmt.add(key, str(value).lower())
        elif isinstance(value, list):
            for item in value:
                fmt.add(f"{key}[]", item)
        elif isinstance(value, dict):
            for subkey, subvalue in value.items():
                fmt.add(f"{key}[{subkey}]", subvalue)
        else:
            fmt.add(key, value)

    return fmt


def get_image_mime_type(data: bytes, /) -> str:
    """Returns the image type from the first few bytes."""
    if data.startswith(b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"):
        return "image/png"
    elif data[:3] == b"\xff\xd8\xff" or data[6:10] in (b"JFIF", b"Exif"):
        return "image/jpeg"
    elif data.startswith((b"\x47\x49\x46\x38\x37\x61", b"\x47\x49\x46\x38\x39\x61")):
        return "image/gif"
    elif data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "image/webp"
    else:
        raise ValueError("Unsupported image type given")


def to_snake_case(string: str, /) -> str:
    """Quick function to return snake_case from camelCase."""
    fmt: list[str] = []
    for character in string:
        if character.isupper():
            fmt.append(f"_{character.lower()}")
            continue
        fmt.append(character)
    return "".join(fmt)


def to_camel_case(string: str, /) -> str:
    """Quick function to return camelCase from snake_case."""
    first, *rest = string.split("_")
    chunks = [first.lower(), *map(str.capitalize, rest)]

    return "".join(chunks)


def as_chunks(iterator: Iterable[T], /, max_size: int) -> Iterable[list[T]]:
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


def delta_to_iso(delta: datetime.timedelta, /) -> str:
    """A helper method to dump a timedelta to an ISO 8601 timedelta string.

    Parameters
    -----------
    delta: :class:`datetime.timedelta`
        The timedelta to convert.

    Returns
    --------
    :class:`str`
        The converted string.
    """
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


def iso_to_delta(iso: str, /) -> datetime.timedelta:
    """A helper method to load a timedelta from an ISO8601 string.

    Parameters
    -----------
    iso: :class:`str`
        The ISO8601 datetime string to parse.

    Raises
    -------
    :exc:`TypeError`
        If the given string is not a valid ISO8601 string and does not match :class:`~hondana.utils.MANGADEX_TIME_REGEX`.

    Returns
    --------
    :class:`datetime.timedelta`
        The timedelta based on the parsed string.
    """
    if (match := MANGADEX_TIME_REGEX.fullmatch(iso)) is None:
        raise TypeError("The passed string does not match the regex pattern.")

    match_dict = match.groupdict()

    times: dict[str, float] = {key: float(value) for key, value in match_dict.items() if value}
    return datetime.timedelta(**times)


RelType = Literal[
    "artist",
    "author",
    "chapter",
    "cover_art",
    "leader",
    "manga",
    "member",
    "scanlation_group",
    "user",
]


@overload
def relationship_finder(
    relationships: list[RelationshipResponse], relationship_type: Literal["artist"], *, limit: Literal[1]
) -> ArtistResponse:
    ...


@overload
def relationship_finder(
    relationships: list[RelationshipResponse], relationship_type: Literal["artist"], *, limit: Optional[int] = ...
) -> list[ArtistResponse]:
    ...


@overload
def relationship_finder(
    relationships: list[RelationshipResponse], relationship_type: Literal["author"], *, limit: Literal[1]
) -> AuthorResponse:
    ...


@overload
def relationship_finder(
    relationships: list[RelationshipResponse], relationship_type: Literal["author"], *, limit: Optional[int] = ...
) -> list[AuthorResponse]:
    ...


@overload
def relationship_finder(
    relationships: list[RelationshipResponse], relationship_type: Literal["chapter"], *, limit: Literal[1]
) -> ChapterResponse:
    ...


@overload
def relationship_finder(
    relationships: list[RelationshipResponse], relationship_type: Literal["chapter"], *, limit: Optional[int] = ...
) -> list[ChapterResponse]:
    ...


@overload
def relationship_finder(
    relationships: list[RelationshipResponse], relationship_type: Literal["cover_art"], *, limit: Literal[1]
) -> CoverResponse:
    ...


@overload
def relationship_finder(
    relationships: list[RelationshipResponse], relationship_type: Literal["cover_art"], *, limit: Optional[int] = ...
) -> list[CoverResponse]:
    ...


@overload
def relationship_finder(
    relationships: list[RelationshipResponse], relationship_type: Literal["leader"], *, limit: Literal[1]
) -> UserResponse:
    ...


@overload
def relationship_finder(
    relationships: list[RelationshipResponse], relationship_type: Literal["leader"], *, limit: Optional[int] = ...
) -> list[UserResponse]:
    ...


@overload
def relationship_finder(
    relationships: list[RelationshipResponse], relationship_type: Literal["manga"], *, limit: Literal[1]
) -> MangaResponse:
    ...


@overload
def relationship_finder(
    relationships: list[RelationshipResponse], relationship_type: Literal["manga"], *, limit: Optional[int] = ...
) -> list[MangaResponse]:
    ...


@overload
def relationship_finder(
    relationships: list[RelationshipResponse], relationship_type: Literal["member"], *, limit: Literal[1]
) -> UserResponse:
    ...


@overload
def relationship_finder(
    relationships: list[RelationshipResponse], relationship_type: Literal["member"], *, limit: Optional[int] = ...
) -> list[UserResponse]:
    ...


@overload
def relationship_finder(
    relationships: list[RelationshipResponse], relationship_type: Literal["scanlation_group"], *, limit: Literal[1]
) -> ScanlationGroupResponse:
    ...


@overload
def relationship_finder(
    relationships: list[RelationshipResponse], relationship_type: Literal["scanlation_group"], *, limit: Optional[int] = ...
) -> list[ScanlationGroupResponse]:
    ...


@overload
def relationship_finder(
    relationships: list[RelationshipResponse], relationship_type: Literal["user"], *, limit: Literal[1]
) -> UserResponse:
    ...


@overload
def relationship_finder(
    relationships: list[RelationshipResponse], relationship_type: Literal["user"], *, limit: Optional[int] = ...
) -> list[UserResponse]:
    ...


def relationship_finder(
    relationships: list[RelationshipResponse], relationship_type: RelType, *, limit: Optional[int] = None
) -> Optional[Union[list[Any], Any]]:
    if not relationships:
        return

    ret: list[RelationshipResponse] = []
    relationships_copy = relationships.copy()

    for relationship in relationships_copy:
        if relationship["type"] == relationship_type:
            if limit == 1:
                relationships.remove(relationship)
                return relationship
            else:
                ret.append(relationship)
            relationships.remove(relationship)

    if limit is not None:
        return ret[:limit]

    return ret


def clean_isoformat(dt: datetime.datetime, /) -> str:
    """A helper method to cleanly convert a datetime (aware or naive) to a timezone-less ISO8601 string.

    Parameters
    -----------
    dt: :class:`datetime.datetime`
        The datetime to convert.

    Returns
    --------
    :class:`str`
        The ISO8601 string.


    .. note::
        The passed datetime will have its timezone converted to UTC and then have its timezone stripped.

    """
    if dt.tzinfo != datetime.timezone.utc:
        dt = dt.astimezone(datetime.timezone.utc)

    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)

    return dt.isoformat(timespec="seconds")


_PATH_WITH_EXTRA = re.compile(r"(?P<num>\d+)(\-?(?P<extra>\w*))?\.(?P<ext>png|jpg|gif|webm)")


def upload_file_sort(key: SupportsRichComparison) -> tuple[int, str]:
    if isinstance(key, pathlib.Path):
        if match := _PATH_WITH_EXTRA.fullmatch(key.name):
            return (len(match["num"]), match["num"])

    raise ValueError("Invalid filename format given.")


_tags_path: pathlib.Path = _PROJECT_DIR.parent / "extras" / "tags.json"
with _tags_path.open("r") as _tags_fp:
    MANGA_TAGS: dict[str, str] = json.load(_tags_fp)


class _ReportReasons(TypedDict):
    manga: dict[str, str]
    chapter: dict[str, str]
    scanlation_group: dict[str, str]
    author: dict[str, str]
    user: dict[str, str]


_report_reason_path = _PROJECT_DIR.parent / "extras" / "report_reasons.json"
with _report_reason_path.open("r") as _reports_fp:
    _REPORT_REASONS: _ReportReasons = json.load(_reports_fp)
