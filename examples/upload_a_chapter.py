"""

This example shows three different ways to perform this task.
Please examine all three to find a method you like.

If you ask me: I prefer the first.

"""

import asyncio

import hondana


# Create your client, you must be authorised to upload a chapter.
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
    scanlator_groups = ["..."]

    # Get the manga we are going to upload a chapter for.
    manga = await client.view_manga("...")

    # let's open up some images, and store their ``bytes`` in memory
    ## NOTE: The order of this list is important, this is the order in which the pages will be presented in the finished upload.
    ## Please ensure you order this correctly.
    files: list[bytes] = []

    # Open our upload session
    async with client.upload_session(
        manga,
        volume=volume,
        chapter=chapter,
        title=title,
        translated_language=translated_language,
        scanlator_groups=scanlator_groups,
    ) as upload_session:

        # First we upload the bytes we stored in memory, adhering to the earlier note.
        await upload_session.upload_images(files)

        # Then we choose to commit that data, which returns a valid ``hondana.Chapter`` instance.
        chapter = await upload_session.commit()

    ## You can also choose not to commit manually, exiting this context manager will commit for you, and discard the returned chapter data.


async def alternative_main():
    # Define your chapter details
    chapter = "1"
    volume = "1"
    translated_language = "en"
    title = "..."
    scanlator_groups = ["..."]

    # This will create and return an instance of ``hondana.ChapterUpload``
    ## You can also use a manga ID, or a ``hondana.Manga`` instance as the first parameter
    upload_session = client.upload_session(
        "...",
        volume=volume,
        chapter=chapter,
        title=title,
        translated_language=translated_language,
        scanlator_groups=scanlator_groups,
    )

    # I recommend the context manager method, since the session checking and committing are done for you.
    await upload_session._check_for_session()

    # Create and upload your images.
    ## NOTE: The order of this list is important, this is the order in which the pages will be presented in the finished upload.
    ## Please ensure you order this correctly.
    images: list[bytes] = []
    await upload_session.upload_images(images)

    ## NOTE: You **MUST** commit when not using the context manager.
    chapter = await upload_session.commit()


async def other_alternative_main():
    # Define your chapter details
    chapter = "1"
    volume = "1"
    translated_language = "en"
    title = "..."
    scanlator_groups = ["..."]

    # Create and upload your images.
    ## NOTE: The order of this list is important, this is the order in which the pages will be presented in the finished upload.
    ## Please ensure you order this correctly.
    images: list[bytes] = []

    chapter = await client.upload_chapter(
        "...",
        volume=volume,
        chapter=chapter,
        title=title,
        translated_language=translated_language,
        images=images,
        scanlator_groups=scanlator_groups,
    )


asyncio.run(main())
