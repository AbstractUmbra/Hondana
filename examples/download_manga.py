### NOTE: To preface, you should probably respect the ratelimits of MangaDex and do this sparingly.
# The library does it's best to handle ratelimits but... c'est la vie.

import asyncio

import hondana


client = hondana.Client(username="my-username", password="my-password")


async def main():
    manga = await client.view_manga("some-manga-id-here")

    chapters = await manga.feed(limit=500, offset=0, translated_languages=["en"])

    for chapter in chapters:
        await chapter.download(f"{manga.title}/{chapter.chapter}")


asyncio.run(main())
