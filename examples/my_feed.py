from __future__ import annotations

import asyncio
import datetime

import hondana
from hondana.query import FeedOrderQuery, Order


# We need to log in with username/email and password since MangaDex does not let you create user based API tokens.
# We instead use our credentials to log in and fetch an expiring auth token.
client = hondana.Client(client_id="...", client_secret="...")


async def main() -> hondana.ChapterFeed:
    # Let's login first.
    await client.login()

    # Let's get the last 15 minutes of released manga
    fifteen_minutes_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=15)

    # And let's order the responses by created at descending
    # we also coerce the type here to prevent typechecker issues. This isn't needed but if you use a typechecker this is good to do.
    order = FeedOrderQuery(created_at=Order.descending)

    # `feed` will return a ChapterFeed instance. This just has the response info and list of chapters.
    feed = await client.get_my_feed(
        limit=20, offset=0, translated_language=["en"], created_at_since=fifteen_minutes_ago, order=order
    )

    # Let's view the responses.
    print(feed)

    await client.close()

    return feed


asyncio.run(main())
