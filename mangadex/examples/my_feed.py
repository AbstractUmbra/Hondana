import datetime

import mangadex


# We need to login with user and password (for now?) since MangaDex does not let you create user based API tokens.
# We instead use our credentials to login and fetch an expiring auth token
client = mangadex.Client(login="my login username", password="my login password")


async def get_my_feed() -> list[mangadex.Chapter]:
    # Let's get the last 15 minutes of released manga
    fifteen_minutes_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=15)

    # And let's order the responses by created at descending
    order = {"createdAt": "desc"}

    # `feed` will return a list of Chapter instances.
    feed = await client.get_my_feed(
        limit=20, offset=0, translated_languages=["en"], created_at_since=fifteen_minutes_ago, order=order  # type: ignore # because typecheckers can't __eq__ a dict and TypedDict
    )

    return feed
