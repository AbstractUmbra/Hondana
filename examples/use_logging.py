import asyncio
import datetime
import logging

import hondana

## This file just showcases the use of the `logging` module and how to enable debug logging for those that need it.


# We need to login with user and password (for now?) since MangaDex does not let you create user based API tokens.
# We instead use our credentials to login and fetch an expiring auth token
client = hondana.Client(username="my-username", password="...")
logging.basicConfig(level=logging.DEBUG)  # <---- This is the import line. It will enable logging to the CLI.

# Alternatively you can use this to log to a file, or have more control over it.
logger = logging.getLogger('hondana')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='hondana.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


async def main() -> list[hondana.Chapter]:
    # Let's get the last 15 minutes of released manga
    fifteen_minutes_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=15)

    # And let's order the responses by created at descending
    order = {"createdAt": "desc"}

    # `feed` will return a list of Chapter instances.
    feed = await client.get_my_feed(
        limit=20, offset=0, translated_languages=["en"], created_at_since=fifteen_minutes_ago, order=order  # type: ignore # because typecheckers can't __eq__ a dict and TypedDict
    )

    # Let's view the responses.
    print(feed)

    await client.close()
    return feed


asyncio.run(main())
