<div align="center">
    <h1><a href="https://jisho.org/word/%E6%9C%AC%E6%A3%9A">Hondana 『本棚』</a></h1>
    <a href='https://github.com/AbstractUmbra/Hondana/actions/workflows/build.yaml'>
        <img src='https://github.com/AbstractUmbra/Hondana/actions/workflows/build.yaml/badge.svg' alt='Build status' />
    </a>
    <a href='https://github.com/AbstractUmbra/Hondana/actions/workflows/coverage_and_lint.yaml'>
        <img src='https://github.com/AbstractUmbra/Hondana/actions/workflows/coverage_and_lint.yaml/badge.svg' alt='Linting and Typechecking' />
    </a>
</div>
<div align="center">
    <a href='https://api.mangadex.org/'>
        <img src='https://img.shields.io/website?down_color=red&down_message=offline&label=API%20Status&logo=MangaDex%20API&up_color=lime&up_message=online&url=https%3A%2F%2Fapi.mangadex.org%2Fping' alt='API Status'/>
    </a>
    <a href='https://hondana.readthedocs.io/en/latest/?badge=latest'>
        <img src='https://readthedocs.org/projects/hondana/badge/?version=latest' alt='Documentation Status' />
    </a>
</div>
<h1></h1>
<br>

A lightweight and asynchronous wrapper around the [MangaDex v5 API](https://api.mangadex.org/docs.html).
You can see our stable docs [here](https://hondana.readthedocs.io/en/stable/)!

## Features
We are currently at 100% feature compliance with the API.

## Notes
### Authenticated endpoints
Sadly (thankfully?) I am not an author on MangaDex, meaning I cannot test the creation endpoints for things like scanlators, artists, authors, manga or chapters.
I have followed the API guidelines to the letter for these, but they may not work.

Any help in testing them is greatly appreciated.

### Upload & Creation
Following the above, I can only use the public test manga for upload testing.
These are currently implemented and tested to the best of my ability.

## Examples
Please take a look at the [examples](./examples/) directory for working examples.

**NOTE**: More examples will follow as the library is developed.

### Current caveats to note
- There are no API endpoints for Artist. It seems they are not differentiated from Author types except in name only.
  - I have separated them logically, but under the hood all Artists are Authors and their `__eq__` reports as such.
- The tags and report reasons are locally cached since you **must** pass UUIDs to the api (and I do not think you're going to memorize those), there's a convenience method for updating the local cache as `Client.update_tags` and `Client.update_report_reasons` respectively.
  - I have added [an example](./examples/updating_local_tags.py) on how to do the above for tags.
  - To use these tags, you can see an example [here](./examples/search_manga.py#L17-L22).
- [Settings related endpoints](https://api.mangadex.org/docs.html#operation/get-settings-template) are not currently exposed. I have implemented their documented use, but I do not expect them to currently function.
  - Once this is exposed fully I will implement a richer interface.
- Currently, if there are any errors in a chapter upload process, the error key does not contain filenames or identifiable information on exactly what file failed upload.
  - This means that I locally compare the succeeded files with the ones missing from the full response payload. The examples have been updated with how to check for an error.
- Currently, the `Client.my_chapter_read_history` method will not work. It is disabled on MD's side due to an issue they had previously. If/when it is re-introduced the method will remain the same.

### Further information/tidbits
- For a bit more clarity on a Chapter's `readableAt` vs `publishAt`, see [this page](https://api.mangadex.org/docs/dates/#readableat) on the MangaDex docs.
- A query with the `include_future_updates` bool set to `True` will include chapters that are pending release by scanlation groups on MangaDex, but which may be available on their sites.

### Contributing
If you would like to contribute to Hondana, please take a look at [the contributing guidelines](./.github/CONTRIBUTING.md) and follow the procedure there.


If you have any question please feel free to join my Discord server:
<div align="left">
    <a href="https://discord.gg/aYGYJxwqe5">
        <img src="https://discordapp.com/api/guilds/705500489248145459/widget.png?style=banner2" alt="Discord Server"/>
    </a>
</div>
