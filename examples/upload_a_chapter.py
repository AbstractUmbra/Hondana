"""

This example shows three different ways to perform this task.
Please examine all three to find a method you like.

If you ask me: I prefer the first.

"""

import asyncio
import pathlib

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
    manga = await client.get_manga("...")

    # Open our upload session
    async with client.upload_session(
        manga,
        volume=volume,
        chapter=chapter,
        title=title,
        translated_language=translated_language,
        scanlator_groups=scanlator_groups,
    ) as upload_session:

        # let's open up some files and use their paths...
        files = [*pathlib.Path("./to_upload").iterdir()]
        # the above is a quick and easy method to create a list of pathlib.Path objects based on the `./to_upload` directory.

        # First we pass the list of paths, adhering to the earlier note.
        # this method does sort them (alphabetically) by default, you can toggle this behaviour by passing `sort=False`
        # I recommend naming your files `1.png`, `2.png`, `3.png`, etc.
        data = await upload_session.upload_images(files)
        if data.has_failures:
            print(
                data.errored_files
            )  # this means the upload request has one or more errors, you may wish to restart the session once fixing the error or other steps.

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
    await upload_session._check_for_session()  # type: ignore # and it will also fail strict type checking

    # let's open up some files and use their paths...
    files = [*pathlib.Path("./to_upload").iterdir()]
    # the above is a quick and easy method to create a list of pathlib.Path objects based on the `./to_upload` directory.
    data = await upload_session.upload_images(files)
    if data.has_failures:
        print(
            data.errored_files
        )  # this means the upload request has one or more errors, you may wish to restart the session once fixing the error or other steps.

    ## NOTE: You **MUST** commit when not using the context manager.
    chapter = await upload_session.commit()


async def other_alternative_main():
    # Define your chapter details
    chapter = "1"
    volume = "1"
    translated_language = "en"
    title = "..."
    scanlator_groups = ["..."]

    # let's open up some files and use their paths...
    files = [*pathlib.Path("./to_upload").iterdir()]
    # the above is a quick and easy method to create a list of pathlib.Path objects based on the `./to_upload` directory.

    chapter = await client.upload_chapter(
        "...",
        volume=volume,
        chapter=chapter,
        title=title,
        translated_language=translated_language,
        images=files,
        scanlator_groups=scanlator_groups,
    )


asyncio.run(main())
