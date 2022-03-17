<div align="center">
    <h1><a href="https://jisho.org/word/%E6%9C%AC%E6%A3%9A">Hondana 『本棚』</a></h1>
    <a href='https://github.com/AbstractUmbra/Hondana/actions/workflows/build.yaml'>
        <img src='https://github.com/AbstractUmbra/Hondana/actions/workflows/build.yaml/badge.svg' alt='Build status' />
    </a>
    <a href='https://github.com/AbstractUmbra/Hondana/actions/workflows/coverage_and_lint.yaml'>
        <img src='https://github.com/AbstractUmbra/Hondana/actions/workflows/coverage_and_lint.yaml/badge.svg' alt='Linting and Typechecking' />
    </a>
    <a href='https://github.com/AbstractUmbra/Hondana/actions/workflows/analysis.yml'>
        <img src='https://github.com/AbstractUmbra/Hondana/actions/workflows/analysis.yml/badge.svg' alt='Code Analysis' />
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
Following the above, this means I also cannot test manga creation or chapter creation/upload.
These are currently implemented but untested.

## Examples
Please take a look at the [examples](./examples/) directory for working examples.

**NOTE**: More examples will follow as the library is developed.

### API caveats to note
- There are no API endpoints for Artist. It seems they are not differentiated from Author types except in name only.
  - I have separated them logically, but under the hood all Artists are Authors and their `__eq__` reports as such.
- The tags are locally cached since you **must** pass UUIDs to the api (and I do not think you're going to memorize those), there's a convenience method for updating the local cache as `Client.update_tags`
  - I have added [an example](./examples/updating_local_tags.py) on how to do the above.
  - To use these tags, you can see an example [here](./examples/search_manga.py#L17-L22).
- [Settings related endpoints](https://api.mangadex.org/docs.html#operation/get-settings-template) are not currently exposed. I have implemeted their documented use but I do not expect them to currently function.
  - Once this is exposed fully I will implement a richer interface.

### Contributing
If you would like to contribute to Hondana, please take a look at [the contributing guidelines](./.github/CONTRIBUTING.md) and follow the procedure there.


If you have any question please feel free to join my Discord server:
<div align="left">
    <a href="https://discord.gg/aYGYJxwqe5">
        <img src="https://discordapp.com/api/guilds/705500489248145459/widget.png?style=banner2" alt="Discord Server"/>
    </a>
</div>
