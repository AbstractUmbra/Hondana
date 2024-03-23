# hondana supports switching to use the dev api version within MangaDex.
# we can do so by setting the HONDANA_API_DEV environment variable, or by using the kwarg in the Client constructor:-

import asyncio
import os

import hondana


async def main() -> None:
    dev_api = bool(os.getenv("HONDANA_API_DEV"))

    async with hondana.Client(dev_api=dev_api) as client:
        manga = await client.get_manga("manga_id")
        print(manga.alt_titles)


asyncio.run(main())
