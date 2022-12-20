from __future__ import annotations

import pathlib

import pytest

from hondana.client import Client


TOKEN_PATH: pathlib.Path = pathlib.Path(__file__).parent / ".client_refresh_token"


def clone_client(auth: bool = False) -> Client:
    if auth is True:
        return Client(username="Test", password="Test")
    return Client()


class TestClient:
    @pytest.mark.asyncio
    async def test_auth(self):
        client = clone_client()

        assert client._http.authenticated is False  # type: ignore # sorry, need this for test purposes
        assert client._http.username is None  # type: ignore # sorry, need this for test purposes
        assert client._http.password is None  # type: ignore # sorry, need this for test purposes

        client.login(username="Test", password="Test")

        assert client._http.authenticated is True  # type: ignore # sorry, need this for test purposes
        assert client._http.username is not None  # type: ignore # sorry, need this for test purposes
        assert client._http.password is not None  # type: ignore # sorry, need this for test purposes

    @pytest.mark.asyncio
    async def test_refresh_token_dump(self):
        client = clone_client(auth=True)

        token = "This is a token"
        client._http.refresh_token = token  # type: ignore # sorry, need this for test purposes

        client.dump_refresh_token(file=True, path=TOKEN_PATH, mode="w")

        text = pathlib.Path(TOKEN_PATH).read_text()
        assert text == token

        TOKEN_PATH.unlink(missing_ok=True)
