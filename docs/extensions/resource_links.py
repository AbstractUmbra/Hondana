"""
https://github.com/Rapptz/discord.py/blob/0bcb0d0e3ce395d42a5b1dae61b0090791ee018d/docs/extensions/resourcelinks.py

The MIT License (MIT)

Copyright (c) 2015-present Rapptz

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

from typing import TYPE_CHECKING, Any

import sphinx
from docutils import nodes, utils
from sphinx.util.nodes import split_explicit_title

if TYPE_CHECKING:
    from docutils.nodes import Node, system_message
    from docutils.parsers.rst.states import Inliner
    from sphinx.application import Sphinx
    from sphinx.util.typing import RoleFunction


def make_link_role(resource_links: dict[str, str]) -> RoleFunction:
    def role(
        typ: str,
        rawtext: str,
        text: str,
        lineno: int,
        inliner: Inliner,
        options: dict[Any, Any] | None = None,
        content: list[str] | None = None,
    ) -> tuple[list[Node], list[system_message]]:
        if options is None:
            options = {}
        if content is None:
            content = []

        has_explicit_title, title, key = split_explicit_title(utils.unescape(text))
        full_url = resource_links[key]

        if not has_explicit_title:
            title = full_url

        pnode = nodes.reference(title, title, internal=False, refuri=full_url)
        return [pnode], []

    return role


def add_link_role(app: Sphinx) -> None:
    app.add_role("resource", make_link_role(app.config.resource_links))


def setup(app: Sphinx) -> dict[str, Any]:
    app.add_config_value("resource_links", {}, "env")
    app.connect("builder-inited", add_link_role)
    return {"version": sphinx.__display_version__, "parallel_read_safe": True}
