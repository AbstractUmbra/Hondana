## Preface note: DEBUG logging on `hondana` (specifically it's `http` module) will result in your token as well as other information that could be sensitive
## showing to the CLI. Be careful if sharing these logs.

from __future__ import annotations

import asyncio
import datetime
import logging

import hondana
from hondana.query import FeedOrderQuery, Order

# This file just showcases the use of the `logging` module and how to enable debug logging for those that need it.

logging.basicConfig(level=logging.DEBUG)  # <---- This is the important line. It will enable logging to the CLI.

# Alternatively you can use this to log to a file, or have more control over it.
logger = logging.getLogger("hondana.http")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="hondana.log", encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)


async def main() -> None:
    async with hondana.Client() as client:
        # Let's get the last 15 minutes of released manga
        fifteen_minutes_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=15)

        # And let's order the responses by created at descending
        order = FeedOrderQuery(created_at=Order.descending)

        # `feed` will return a `hondana.ChapterFeed` instance.
        feed = await client.get_my_feed(
            limit=20, offset=0, translated_language=["en"], created_at_since=fifteen_minutes_ago, order=order
        )

        # Let's view the response repr.
        print(feed)


asyncio.run(main())
