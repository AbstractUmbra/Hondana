# NOTE: To preface, you should probably respect the rate-limits of MangaDex and do this sparingly.
# The library does its best to handle rate-limits but... c'est la vie.

import asyncio

import hondana


client = hondana.Client(username="my-username", password="my-password")


async def main():
    manga = await client.view_manga("some-manga-id-here")

    chapters = await manga.feed(limit=500, offset=0, translated_language=["en"])

    for chapter in chapters:
        await chapter.download(f"{manga.title}/{chapter.chapter}")


asyncio.run(main())
