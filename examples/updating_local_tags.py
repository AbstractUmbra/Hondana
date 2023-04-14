import asyncio

import hondana


async def main():
    # Auth is not required for this process, so just a Client will work.
    async with hondana.Client() as client:
        current_tags = hondana.MANGA_TAGS
        print(current_tags)

        # Use the client convenience method to update the local cache
        # This will also update the local store of them, they will be available on next module reload.
        new_tags = await client.update_tags()

        # Show the new changes.
        print(new_tags)


asyncio.run(main())
