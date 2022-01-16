# NOTE: To preface, you should probably respect the rate-limits of MangaDex and do this sparingly.
# The library does its best to handle rate-limits but... c'est la vie.

import asyncio

import hondana


client = hondana.Client(username="my-username", password="my-password")


async def main():
    # Get the manga, we will need its chapters
    manga = await client.view_manga("some-manga-id-here")

    # Load the feed of the manga, that contains all chapters.
    # To note... I would filter by language here, else you'll potentially have random translations downloaded.
    feed = await manga.feed(limit=500, offset=0, translated_language=["en"])

    # This is how you recursively download the chapters.
    # The string in the `.download()` call is the path to save all the chapters in. It will recursively create it, if needed.
    for chapter in feed.chapters:
        await chapter.download(f"{manga.title}/{chapter.chapter}")


asyncio.run(main())
