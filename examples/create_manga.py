from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import hondana


if TYPE_CHECKING:
    from hondana.types.common import LocalizedString

# Create your client, auth is needed for this.
client = hondana.Client(username="my username", password="my password")


async def main():
    """
    Here we will create a Manga in MangaDex.

    The process is multi-stage so I will attempt to outline them here.
    """

    # Outline the needed attributes for this manga here
    manga_title: LocalizedString = {"en": "Some neat manga!", "ja": "本棚"}
    original_language = "en"
    status = "ongoing"
    content_rating = "safe"
    version = 1

    # Create the manga with them:
    draft_manga = await client.create_manga(
        title=manga_title, original_language=original_language, status=status, content_rating=content_rating, version=version
    )

    # This manga is now created in "draft" state. This is outlined more here:
    # https://api.mangadex.org/docs.html#section/Manga-Creation
    # tl;dr it's to remove the spam creations and to ensure there's a cover on the manga... so let's do that now.
    with open("our_cover.png", "rb") as file:
        cover = file.read()

    # When we upload a cover, we need to attribute it to a manga, so lets use the draft one we created.
    uploaded_cover = await draft_manga.upload_cover(cover=cover, volume=None)

    # Now that our manga is covered and uploaded, let's submit it for approval:
    submitted_manga = await draft_manga.submit_draft(version=version)

    # NOTE: Something to note is that the version of draft MUST match the version of submitted manga during the approval stage.


asyncio.run(main())
