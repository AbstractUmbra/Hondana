import asyncio

import hondana


client = hondana.Client()


async def main() -> None:
    # We can use the `.none()` classmethod to specify no includes, since the library defaults to using all of them.
    manga_list_includes = hondana.query.MangaIncludes.none()

    # Now our collection will have the minimal payload data as we don't need all the extra reference expansion data.
    collection = await client.manga_list(includes=manga_list_includes)
    print(len(collection.manga))

    # Since our default is all possible expansions, you can just call an empty constructor, and it will populate accordingly.
    chapter_list_includes = hondana.query.ChapterIncludes()
    # We also have the `all()` classmethod should you wish to use that.

    # These chapters will have all possible expansion data.
    feed = await client.chapter_list(includes=chapter_list_includes)
    print(len(feed.chapters))

    # if you wish to manually choose which to include/exclude, you can do things like so:
    custom_list_includes = hondana.query.CustomListIncludes(manga=False, user=True, owner=True)
    # The `=True` aren't necessary since they are the default, but I added for example reasons.

    # You can also edit these attributes post-creation:
    custom_list_includes.manga = True

    # Now our payload will have the necessary data as we requested.
    await client.get_custom_list("...", includes=custom_list_includes)


asyncio.run(main())
