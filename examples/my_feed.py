import asyncio
import datetime

import hondana


# We need to log in with username/email and password since MangaDex does not let you create user based API tokens.
# We instead use our credentials to log in and fetch an expiring auth token.
# NOTE: You can also use the client with no credentials.
client = hondana.Client(username="my-username", password="my-password")


async def main() -> list[hondana.Chapter]:
    # Let's get the last 15 minutes of released manga
    fifteen_minutes_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=15)

    # And let's order the responses by created at descending
    order = {"createdAt": "desc"}

    # `feed` will return a list of Chapter instances.
    feed = await client.get_my_feed(
        limit=20, offset=0, translated_language=["en"], created_at_since=fifteen_minutes_ago, order=order  # type: ignore # because type-checkers can't __eq__ a dict and TypedDict
    )

    # Let's view the responses.
    print(feed)

    return feed


asyncio.run(main())
