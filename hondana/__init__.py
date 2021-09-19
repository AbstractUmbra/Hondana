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

__title__ = "Hondana"
__author__ = "AbstractUmbra"
__license__ = "MIT"
__copyright__ = "Copyright 2021-present AbstractUmbra"
__version__ = "0.3.2"

import logging
from typing import Literal, NamedTuple

from . import utils as utils
from .artist import Artist as Artist
from .author import Author as Author
from .chapter import Chapter as Chapter
from .client import Client as Client
from .cover import Cover as Cover
from .custom_list import *
from .errors import *
from .legacy import *
from .manga import Manga as Manga
from .report import *
from .scanlator_group import ScanlatorGroup as ScanlatorGroup
from .tags import *
from .token import *
from .user import User as User
from .utils import TAGS as MANGA_TAGS
from .utils import URL_REGEX as MANGADEX_URL_REGEX


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: Literal["alpha", "beta", "candidate", "final"]
    serial: int


version_info: VersionInfo = VersionInfo(major=0, minor=3, micro=2, releaselevel="final", serial=0)

logging.getLogger(__name__).addHandler(logging.NullHandler())
