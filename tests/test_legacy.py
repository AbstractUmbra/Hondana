from __future__ import annotations

import json
import pathlib
from copy import deepcopy
from typing import TYPE_CHECKING

from hondana.legacy import LegacyItem

if TYPE_CHECKING:
    from hondana.http import HTTPClient
    from hondana.types_.legacy import GetLegacyMappingResponse


PATH: pathlib.Path = pathlib.Path(__file__).parent / "payloads" / "legacy_mapping.json"

PAYLOAD: GetLegacyMappingResponse = json.load(PATH.open())
HTTP: HTTPClient = object()  # type: ignore # this is just for test purposes.


def clone_legacy() -> LegacyItem:
    t = deepcopy(PAYLOAD)
    return LegacyItem(HTTP, t["data"][0])


class TestLegacy:
    def test_id(self) -> None:
        item = clone_legacy()
        assert item.id == PAYLOAD["data"][0]["id"]

    def test_mapping_ids(self) -> None:
        item = clone_legacy()

        assert item.obj_legacy_id == PAYLOAD["data"][0]["attributes"]["legacyId"]
        assert item.obj_new_id == PAYLOAD["data"][0]["attributes"]["newId"]
