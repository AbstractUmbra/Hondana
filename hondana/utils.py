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
from functools import wraps
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Literal, TypedDict, TypeVar, overload
from urllib.parse import quote as _uriquote

import multidict
from yarl import URL

try:
    import orjson
except ModuleNotFoundError:

    def to_json(obj: Any, /) -> str:
        """Dump a Python type to JSON object."""  # noqa: DOC201 # not part of the public API.
        return json.dumps(obj, separators=(",", ":"), ensure_ascii=True, indent=2)

    _from_json = json.loads
else:

    def to_json(obj: Any, /) -> str:
        """Dump a Python type to JSON object."""  # noqa: DOC201 # not part of the public API.
        return orjson.dumps(obj, option=orjson.OPT_INDENT_2).decode("utf-8")

    _from_json = orjson.loads

from .errors import AuthenticationRequired

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from typing import Concatenate, TypeAlias

    import aiohttp
    from _typeshed import SupportsRichComparison
    from typing_extensions import ParamSpec, Protocol

    from .http import HTTPClient
    from .types_.common import LanguageCode
    from .types_.relationship import RelationshipResponse

    class SupportsHTTP(Protocol):
        _http: HTTPClient


from_json = _from_json

MANGADEX_QUERY_PARAM_TYPE: TypeAlias = dict[str, str | int | bool | list[str] | list["LanguageCode"] | dict[str, str] | None]
C = TypeVar("C", bound="SupportsHTTP")
T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
if TYPE_CHECKING:
    B = ParamSpec("B")


LOGGER = logging.getLogger(__name__)

__all__ = (
    "MANGADEX_TIME_REGEX",
    "MANGADEX_URL_REGEX",
    "MANGA_TAGS",
    "MISSING",
    "AuthorArtistTag",
    "RelationshipResolver",
    "Route",
    "as_chunks",
    "cached_slot_property",
    "clean_isoformat",
    "delta_to_iso",
    "deprecated",
    "from_json",
    "get_image_mime_type",
    "iso_to_delta",
    "json_or_text",
    "php_query_builder",
    "to_camel_case",
    "to_json",
    "to_snake_case",
)

_PROJECT_DIR = pathlib.Path(__file__)
MAX_DEPTH: int = 10_000
MANGADEX_URL_REGEX = re.compile(
    r"(?:http[s]?:\/\/)?mangadex\.org\/(?P<type>title|chapter|author|tag)\/(?P<ID>[a-z0-9]{8}\-[a-z0-9]{4}\-[a-z0-9]{4}\-[a-z0-9]{4}\-[a-z0-9]{12})\/?(?P<title>.*)",
)
r"""
``r"(?:http[s]?:\/\/)?mangadex\.org\/(?P<type>title|chapter|author|tag)\/(?P<ID>[a-z0-9]{8}\-[a-z0-9]{4}\-[a-z0-9]{4}\-[a-z0-9]{4}\-[a-z0-9]{12})\/?(?P<title>.*)"``

This `regex pattern <https://docs.python.org/3/library/re.html#re-objects>`_ can be used to isolate common elements from a MangaDex URL.
This means that Manga, Chapter, Author or Tag urls can be parsed for their ``type``, ``ID`` and ``title``.
"""  # noqa: E501

MANGADEX_TIME_REGEX = re.compile(
    r"^(P(?P<days>[1-9]|[1-9][0-9])D)?(P?(?P<weeks>[1-9])W)?(P?T((?P<hours>[1-9]|1[0-9]|2[0-4])H)?((?P<minutes>[1-9]|[1-5][0-9]|60)M)?((?P<seconds>[1-9]|[1-5][0-9]|60)S)?)?$",
)
"""
``r"^(P([1-9]|[1-9][0-9])D)?(P?([1-9])W)?(P?T(([1-9]|1[0-9]|2[0-4])H)?(([1-9]|[1-5][0-9]|60)M)?(([1-9]|[1-5][0-9]|60)S)?)?$"``

This `regex pattern <https://docs.python.org/3/library/re.html#re-objects>`_ follows the ISO-8601 standard (MangaDex uses `PHP DateInterval <https://www.php.net/manual/en/dateinterval.construct.php>`_).
The pattern *is* usable but more meant as a guideline for your formatting.

It matches some things like: ``P1D2W`` (1 day, two weeks), ``P1D2WT3H4M`` (1 day, 2 weeks, 3 hours and 4 minutes)
"""  # noqa: E501


class AuthorArtistTag:  # noqa: D101 # technically not public
    id: str


class Route:
    """A helper class for instantiating a HTTP method to MangaDex.

    Parameters
    ----------
    verb: :class:`str`
        The HTTP verb you wish to perform, e.g. ``"POST"``
    path: :class:`str`
        The prepended path to the API endpoint you with to target.
        e.g. ``"/manga/{manga_id}"``
    authenticate: :class:`bool`
        Whether to provide authentication headers to the resulting HTTP request, or not.
        Defaults to ``False``.
    parameters: Any
        This is a special cased kwargs. Anything passed to these will substitute it's key to value in the `path`.
        E.g. if your `path` is ``"/manga/{manga_id}"``, and your parameters are ``manga_id="..."``,
        then it will expand into the path making ``"manga/..."``
    """

    API_BASE_URL: ClassVar[str] = "https://api.mangadex.org"
    API_DEV_BASE_URL: ClassVar[str] = "https://api.mangadex.dev"

    def __init__(
        self,
        verb: str,
        path: str,
        *,
        base: str | None = None,
        authenticate: bool = False,
        **parameters: Any,
    ) -> None:
        self.verb: str = verb
        self.path: str = path
        self.auth: bool = authenticate
        url = (base or self.API_BASE_URL) + self.path
        if parameters:
            url = url.format_map({k: _uriquote(v) if isinstance(v, str) else v for k, v in parameters.items()})
        self.url: URL = URL(url, encoded=True)


class AuthRoute(Route):
    """A helper class for instantiating a HTTP method to authenticate with MangaDex.

    Parameters
    ----------
    verb: :class:`str`
        The HTTP verb you wish to perform. E.g. ``"POST"``
    base: :class:`str`
        The base URL for the download path.
    path: :class:`str`
        The prepended path to the API endpoint you with to target.
        e.g. ``"/manga/{manga_id}"``
    authenticate: :class:`bool`
        Whether to procide authentication headers to the resulting HTTP method, or not.
        Defaults to ``False``.
    parameters: Any
        This is a special cased kwargs. Anything passed to these will substitute it's key to value in the `path`.
        E.g. if your `path` is ``"/manga/{manga_id}"``, and your parameters are ``manga_id="..."``,
        then it will expand into the path making ``"manga/..."``
    """

    API_BASE_URL: ClassVar[str] = "https://auth.mangadex.org/realms/mangadex/protocol/openid-connect"
    API_DEV_BASE_URL: ClassVar[str] = "https://auth.mangadex.dev/realms/mangadex/protocol/openid-connect"


class MissingSentinel:
    def __eq__(self, _: object) -> bool:
        return False

    def __bool__(self) -> bool:
        return False

    def __hash__(self) -> int:
        return 0

    def __repr__(self) -> str:
        return "..."


MISSING: Any = MissingSentinel()


# This class and subsequent decorator have been copied from Rapptz' Discord.py
# (https://github.com/Rapptz/discord.py)
# Credit goes to Rapptz and contributors
class CachedSlotProperty(Generic[T, T_co]):
    def __init__(self, name: str, function: Callable[[T], T_co]) -> None:
        self.name: str = name
        self.function: Callable[[T], T_co] = function
        self.__doc__ = function.__doc__

    @overload
    def __get__(self, instance: None, owner: type[T]) -> CachedSlotProperty[T, T_co]: ...

    @overload
    def __get__(self, instance: T, owner: type[T]) -> T_co: ...

    def __get__(self, instance: T | None, owner: type[T]) -> Any:
        if instance is None:
            return self

        try:
            return getattr(instance, self.name)
        except AttributeError:
            value = self.function(instance)
            setattr(instance, self.name, value)
            return value


def cached_slot_property(name: str, /) -> Callable[[Callable[[T], T_co]], CachedSlotProperty[T, T_co]]:
    """A decorator to describe a cached slot property within an object.

    Returns
    -------
    :class:`CachedSlotProperty`
    """

    def decorator(func: Callable[[T], T_co]) -> CachedSlotProperty[T, T_co]:
        return CachedSlotProperty(name, func)

    return decorator


def require_authentication(func: Callable[Concatenate[C, B], T]) -> Callable[Concatenate[C, B], T]:
    """A decorator to raise on authentication methods."""  # noqa: DOC201 # not part of the public API.

    @wraps(func)
    def wrapper(item: C, *args: B.args, **kwargs: B.kwargs) -> T:
        if not item._http._authenticated:  # pyright: ignore[reportPrivateUsage] # noqa: SLF001 # we're gonna keep this private
            msg = "This method requires authentication."
            raise AuthenticationRequired(msg)

        return func(item, *args, **kwargs)

    return wrapper


def deprecated(alternate: str | None = None, /) -> Callable[[Callable[B, T]], Callable[B, T]]:
    """A decorator to mark a method as deprecated.

    Parameters
    ----------
    alternate: Optional[:class:`str`]
        The alternate method to use.
    """  # noqa: DOC201 # not part of the public API.

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
    ----------
    limit: :class:`int`
        The limit (or amount) of objects you are requesting.
    offset: :class:`int`
        The offset (or pagination start point) for the objects you are requesting.
    max_limit: :class:`int`
        The maximum limit value for the API Endpoint.

    Raises
    ------
    ValueError
        Exceeding the maximum pagination limit.

    Returns
    -------
    Tuple[:class:`int`, :class:`int`]
    """
    if offset >= MAX_DEPTH:
        msg = f"An offset of {MAX_DEPTH} will not return results."
        raise ValueError(msg)

    offset = max(offset, 0)

    difference = MAX_DEPTH - offset
    if difference <= max_limit:
        new_limit = difference
        new_offset = MAX_DEPTH - new_limit
        return new_limit, new_offset

    new_limit = min(max(0, limit), max_limit)
    new_offset = min(max(0, offset), MAX_DEPTH - new_limit)

    return new_limit, new_offset


async def json_or_text(response: aiohttp.ClientResponse, /) -> dict[str, Any] | str:
    """A quick method to parse a `aiohttp.ClientResponse` and test if it's json or text.

    Returns
    -------
    Union[Dict[:class:`str`, Any], str]
        The parsed json object as a dictionary, or the response text.
    """
    text = await response.text(encoding="utf-8")
    try:
        if response.headers["content-type"] == "application/json":
            return _from_json(text)
    except (KeyError, json.JSONDecodeError):
        pass

    return text


def php_query_builder(obj: MANGADEX_QUERY_PARAM_TYPE, /) -> multidict.MultiDict[str | int]:
    """
    A helper function that builds a MangaDex (PHP) query string from a mapping.

    Parameters
    ----------
    obj: Mapping[:class:`str`, Optional[Union[:class:`str`, :class:`int`, :class:`bool`, List[:class:`str`], Dict[:class:`str`, :class:`str`]]]]
        The mapping to build the query string from.

    Returns
    -------
    :class:`multidict.MultiDict`
        A dictionary/mapping type that allows for duplicate keys.
    """  # noqa: E501 # required for formatting
    fmt = multidict.MultiDict[str | int]()
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
    """Returns the image type from the first few bytes.

    Raises
    ------
    ValueError
        Unsupported image type used.

    Returns
    -------
    :class:`str`
        The mime type of the image data.
    """
    if data.startswith(b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"):
        return "image/png"
    if data[:3] == b"\xff\xd8\xff" or data[6:10] in (b"JFIF", b"Exif"):
        return "image/jpeg"
    if data.startswith((b"\x47\x49\x46\x38\x37\x61", b"\x47\x49\x46\x38\x39\x61")):
        return "image/gif"

    msg = "Unsupported image type given"
    raise ValueError(msg)


def to_snake_case(string: str, /) -> str:
    """Quick function to return snake_case from camelCase.

    Returns
    -------
    :class:`str`
        The formatted string.
    """
    fmt: list[str] = []
    for character in string:
        if character.isupper():
            fmt.append(f"_{character.lower()}")
            continue
        fmt.append(character)
    return "".join(fmt)


def to_camel_case(string: str, /) -> str:
    """Quick function to return camelCase from snake_case.

    Returns
    -------
    :class:`str`
        The formatted string.
    """
    first, *rest = string.split("_")
    chunks = [first.lower(), *map(str.capitalize, rest)]

    return "".join(chunks)


def as_chunks(iterator: Iterable[T], /, max_size: int) -> Iterable[list[T]]:
    """Quick method to take an iterable and yield smaller 'chunks' of itself.

    Yields
    ------
        List[T]
            The chunked list of T.
    """
    ret: list[T] = []
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
    ----------
    delta: :class:`datetime.timedelta`
        The timedelta to convert.

    Returns
    -------
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
    ----------
    iso: :class:`str`
        The ISO8601 datetime string to parse.

    Raises
    ------
    TypeError
        If the given string is not a valid ISO8601 string and does not match :class:`~hondana.utils.MANGADEX_TIME_REGEX`.

    Returns
    -------
    :class:`datetime.timedelta`
        The timedelta based on the parsed string.
    """
    if (match := MANGADEX_TIME_REGEX.fullmatch(iso)) is None:
        msg = "The passed string does not match the regex pattern."
        raise TypeError(msg)

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


class RelationshipResolver(Generic[T]):
    """Handler utility for cleanly resolving the relationship attributes in MangaDex API objects.

    Parameters
    ----------
    relationships: list[:class:`hondana.types.RelationshipResponse`]
        The relationships we wish to handle/filter.
    relationship_type: :class:`str`
        The type of relationship we want to filter by.
    """

    __slots__ = (
        "_type",
        "limit",
        "relationships",
    )

    def __init__(self, relationships: list[RelationshipResponse], relationship_type: RelType, /) -> None:
        self.relationships: list[RelationshipResponse] = relationships
        self._type: RelType = relationship_type

    @overload
    def resolve(self, *, with_fallback: Literal[False], remove_empty: bool = ...) -> list[T]: ...

    @overload
    def resolve(self, *, with_fallback: Literal[True], remove_empty: bool = ...) -> list[T | None]: ...

    @overload
    def resolve(self) -> list[T]: ...

    @overload
    def resolve(self, *, remove_empty: bool = ...) -> list[T]: ...

    def resolve(self, *, with_fallback: bool = False, remove_empty: bool = False) -> list[T] | list[T | None]:
        """Helper method to resolve the passed relationships data into a list of selected type.

        Parameters
        ----------
        with_fallback: :class:`bool`
            This (when true) will append a single ``None`` into the list if it is empty at the end of resolving.
            This is for clean indexing of the list without raising a KeyError.
            Defaults to ``False``.
        remove_empty: :class:`bool`
            This (when true) will refuse to add relationship data to the list if said data does not have it's
            inner attributes.This is the case when the necessary ``includes`` were not provided.
            Defaults to ``False``

        Returns
        -------
        Union[List[T] | List[T | None]]
            A complicated type. It will return the list of relationship type specified,
            or a list with a single ``None`` depending on the parameters above.
        """
        relationships = self.relationships.copy()

        ret: list[T | None] = []
        for relationship in relationships:
            if relationship["type"] == self._type:
                if remove_empty and not relationship.get("attributes"):
                    continue
                ret.append(relationship)  # pyright: ignore[reportArgumentType] # can't type narrow here

        if not ret and with_fallback:
            ret.append(None)
        return ret

    @overload
    def pop(self, *, with_fallback: Literal[False], remove_empty: bool = ...) -> T: ...

    @overload
    def pop(self, *, with_fallback: Literal[True], remove_empty: bool = ...) -> T | None: ...

    @overload
    def pop(self) -> T: ...

    @overload
    def pop(self, *, remove_empty: bool = ...) -> T: ...

    def pop(self, *, with_fallback: bool = False, remove_empty: bool = False) -> T | None:
        """Helper method which calls :meth:`resolve` and takes the first item from the list.

        Parameters
        ----------
        with_fallback: :class:`bool`
            This (when true) will append a single ``None`` into the list if it is empty at the end of resolving.
            This is for clean indexing of the list without raising a KeyError.
            Defaults to ``False``.
        remove_empty: :class:`bool`
            This (when true) will refuse to add relationship data to the list if said data does not have it's
            inner attributes.This is the case when the necessary ``includes`` were not provided.
            Defaults to ``False``

        Returns
        -------
        Union[List[T] | List[T | None]]
            A complicated type. It will return the list of relationship type specified,
            or a list with a single ``None`` depending on the parameters above.
        """
        return self.resolve(with_fallback=with_fallback, remove_empty=remove_empty).pop()


def clean_isoformat(dt: datetime.datetime, /) -> str:
    """Helper method to cleanly convert a datetime (aware or naive) to a timezone-less ISO8601 string.

    Parameters
    ----------
    dt: :class:`datetime.datetime`
        The datetime to convert.

    Returns
    -------
    :class:`str`
        The ISO8601 string.


    .. note::
        The passed datetime will have its timezone converted to UTC and then have its timezone stripped.

    """
    if dt.tzinfo != datetime.UTC:
        dt = dt.astimezone(datetime.UTC)

    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)

    return dt.isoformat(timespec="seconds")


_PATH_WITH_EXTRA = re.compile(r"(?P<num>\d+)(\-?(?P<extra>\w*))?\.(?P<ext>png|jpg|gif)")


def upload_file_sort(key: SupportsRichComparison) -> tuple[int, str]:
    if isinstance(key, pathlib.Path) and (match := _PATH_WITH_EXTRA.fullmatch(key.name)):
        return (len(match["num"]), match["num"])

    msg = "Invalid filename format given."
    raise ValueError(msg)


_tags_path: pathlib.Path = _PROJECT_DIR.parent / "extras" / "tags.json"
with _tags_path.open("r") as _tags_fp:
    MANGA_TAGS: dict[str, str] = _from_json(_tags_fp.read())


class _ReportReasons(TypedDict):
    manga: dict[str, str]
    chapter: dict[str, str]
    scanlation_group: dict[str, str]
    author: dict[str, str]
    user: dict[str, str]


_report_reason_path = _PROJECT_DIR.parent / "extras" / "report_reasons.json"
with _report_reason_path.open("r") as _reports_fp:
    _REPORT_REASONS: _ReportReasons = _from_json(_reports_fp.read())
