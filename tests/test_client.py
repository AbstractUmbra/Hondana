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

        assert client._http._authenticated is False
        assert client._http.username is None
        assert client._http.password is None

        client.login(username="Test", password="Test")

        assert client._http._authenticated is True
        assert client._http.username is not None
        assert client._http.password is not None

    @pytest.mark.asyncio
    async def test_refresh_token_dump(self):
        client = clone_client(auth=True)

        token = "This is a token"
        client._http._refresh_token = token

        client.dump_refresh_token(file=True, path=TOKEN_PATH, mode="w")

        text = pathlib.Path(TOKEN_PATH).read_text()
        assert text == token

        TOKEN_PATH.unlink(missing_ok=True)
