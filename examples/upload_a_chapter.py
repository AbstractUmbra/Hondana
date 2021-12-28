import asyncio

import hondana


# Create your client, you must be authorised to do upload a chapter.
client = hondana.Client(username="my username", password="my password")


async def main():
    """
    In this example we are going to upload a chapter to the MangaDex API.
    """

    # Define your chapter details
    chapter = "1"
    volume = "1"
    translated_language = "en"
    title = "..."

    # Get the manga we are going to upload a chapter for.
    manga = await client.view_manga("...")

    # let's open up some images, and store their ``bytes`` in memory
    ## NOTE: The order if this list is important, this is the order in which the pages will be viewed.
    ## Please ensure you order this correctly.
    files: list[bytes] = []

    # Open our upload session
    async with hondana.ChapterUpload(
        manga, volume=volume, chapter=chapter, title=title, translated_language=translated_language
    ) as upload_session:

        # First we upload the bytes we stored in memory, adhering to the earlier note.
        await upload_session.upload_images(files)

        # Then we choose to commit that data, which returns a valid ``hondana.Chapter`` instance.
        chapter = await upload_session.commit()

    ## You can also choose not to commit manually, exiting this context manager will commit for you, and discard the chapter data.


asyncio.run(main())
