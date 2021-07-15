import datetime

import mangadex


# We need to login with user and password (for now?) since Mangadex does not let you create user based API tokens.
# We instead use our credentials to login and fetch an expiring auth token
client = mangadex.Client(login="my login username", password="my login password")


async def search_for_tags() -> list[mangadex.Manga]:
    # Using the tag builder for ease during a query
    # This will add a restriction to search for a manga with all 3 of these tags using logical AND
    tags = mangadex.Tags("action", "comedy", "isekai", mode="and")

    # we now perform a search with a limit of 10 (returned manga)
    # an offset of 0 (pagination needs)
    # and using our predefined tags earlier.
    manga_response = await client.search_manga(limit=10, offset=0, included_tags=tags)

    # `manga_response` will be a list of upto 10 manga that match the search criteria above.
    return manga_response


async def more_refined_search() -> list[mangadex.Manga]:
    # let's do a more refined search using many of the query parameters...

    tags = mangadex.Tags("action", "comedy", "isekai", mode="and")

    # Let's say we only way to show manga created in the last week, lets make a naive utc datetime for one week ago
    seven_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)

    # and we don't want anything but ongoing manga
    status = ["ongoing"]

    # and we probably just want shounen... right?
    demographic = ["shounen"]

    # lets try a search
    search = await client.search_manga(
        limit=10,
        offset=0,
        included_tags=tags,
        publication_demographic=demographic,  # type: ignore # typecheckers won't eval a list[str] and list[Literal[]]
        status=status,  # type: ignore # see above
        created_at_since=seven_days_ago,
    )

    # this search was empty for me at the time of writing, but the fact you get a repsonse at all means it worked.
    print(search)

    return search
