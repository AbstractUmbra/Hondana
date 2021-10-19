from __future__ import annotations

import asyncio
import datetime
from typing import TYPE_CHECKING

import hondana

if TYPE_CHECKING:
    from hondana.types.manga import MangaOrderQuery

# We need to login with username/email and password since MangaDex does not let you create user based API tokens.
# We instead use our credentials to login and fetch an expiring auth token.
# NOTE: You can also use the client with no credentials.
client = hondana.Client(username="my-username", password="my-password")


async def main() -> list[hondana.Chapter]:
    # Let's get the last 15 minutes of released manga
    fifteen_minutes_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=15)

    # And let's order the responses by created at descending
    # we also coerce the type here to prevent typechecker issues. This isn't needed but if you use a typechecker this is good to do.
    order: MangaOrderQuery = {"createdAt": "desc"}

    # `feed` will return a list of Chapter instances.
    feed = await client.get_my_feed(
        limit=20, offset=0, translated_language=["en"], created_at_since=fifteen_minutes_ago, order=order
    )

    # Let's view the responses.
    print(feed)

    return feed


asyncio.run(main())
