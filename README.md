# mangadex.py

A lightweight and asynchronous wrapper around the [Mangadex v5 API](https://api.mangadex.org/docs.html).

### Features
**NOTE** This library is still in development, I will list off the API methods and their progress here:

| Feature          | Implemented? | Notes                                              |
| ---------------- | ------------ | -------------------------------------------------- |
| Chapter Upload   | [ ]          | Soon:tm:                                           |
| Manga            | [/]          | Partially implemented.                             |
| Cover            | [ ]          | Soon:tm:                                           |
| Author           | [ ]          | Soon:tm:                                           |
| Search           | [ ]          | Soon:tm:                                           |
| Auth             | [x]          | Authentication is done per request, token handled. |
| Scanlation Group | [ ]          | Soon:tm:                                           |
| Feed             | [ ]          | Soon:tm:                                           |
| CustomList       | [ ]          | Soon:tm:                                           |
| AtHome           | [ ]          | Soon:tm:                                           |
| Legacy           | [ ]          | Soon:tm:                                           |
| Infrastructure   | [ ]          | Soon:tm:                                           |
| Upload           | [ ]          | Soon:tm:                                           |
| Account          | [ ]          | Soon:tm:                                           |
| User             | [ ]          | Soon:tm:                                           |
| Chapter          | [ ]          | Soon:tm:                                           |
| Report           | [ ]          | Soon:tm:                                           |
| Ratelimits?      | [ ]          | Not part of the API spec but might be handy.       |


### Examples

```py
import datetime
import mangadex

async def main():
    client = mangadex.Client(login="My login username", password="My password")  # sadly we can only use these to generate the necessary token.

    manga = await client.get_manga("Your Manga uuid4 string here")

    one_week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    my_feed = await client.get_my_feed(limit=20, offset=0, created_at_since=one_week_ago, order={"createdAt": "desc"})
    # My feed will be a list of 20 Chapters, ordered by creation date descending

    return my_feed

asyncio.run(main())
```

**NOTE**: More examples will follow as the library is developed.

### API caveats to note

- There are no API endpoints for Artist. Currently if you query a manga without the `"artist"` query includes then you will not recieve artist data.
- The tags are locally cached since you **must** pass UUIDs to the api (and I do not think you're going to memorise those), there's a convenience method for updating the local cache as `Client.update_tags`