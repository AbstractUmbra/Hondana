<div align="center">
    <h1><a href="https://jisho.org/word/%E6%9C%AC%E6%A3%9A">Hondana 『本棚』</a></h1>
    <a href='https://hondana.readthedocs.io/en/latest/?badge=latest'>
        <img src='https://readthedocs.org/projects/hondana/badge/?version=latest' alt='Documentation Status' />
    </a>
    <a href='https://github.com/AbstractUmbra/Hondana/actions/workflows/build.yaml'>
        <img src='https://github.com/AbstractUmbra/Hondana/workflows/Build/badge.svg' alt='Build status' />
    </a>
    <a href='https://github.com/AbstractUmbra/Hondana/actions/workflows/lint.yaml'>
        <img src='https://github.com/AbstractUmbra/Hondana/workflows/Lint/badge.svg' alt='Build status' />
    </a>
</div>
<div align="center">
    <a href='https://api.mangadex.org/'>
        <img src='https://img.shields.io/website?down_color=red&down_message=offline&label=API%20Status&logo=MangaDex%20API&up_color=lime&up_message=online&url=https%3A%2F%2Fapi.mangadex.org%2Fping' alt='API Status'/>
    </a>
</div>
<br>

A lightweight and asynchronous wrapper around the [MangaDex v5 API](https://api.mangadex.org/docs.html).

## Features
**NOTE** This library is still in development, I will list off the API methods and their progress here:

| Feature          | Implemented? | Notes                                                                |
|------------------|--------------|----------------------------------------------------------------------|
| Chapter Upload   | [ ]          | Soon:tm:                                                             |
| Manga            | [x]          | Done.                                                                |
| Cover            | [x]          | Done.                                                                |
| Author           | [x]          | Done.                                                                |
| Search           | [x]          | Done.                                                                |
| Auth             | [x]          | Authentication is done per request, token handled.                   |
| Scanlation Group | [x]          | Done.                                                                |
| Feed             | [x]          | Done                                                                 |
| CustomList       | [x]          | Done.                                                                |
| AtHome           | [x]          | Done.                                                                |
| Legacy           | [x]          | Done.                                                                |
| Infrastructure   | [x]          | Done.                                                                |
| Upload           | [x]          | Manga creation and chapter creation exist for use now.               |
| Account          | [x]          | Done.                                                                |
| User             | [x]          | Done.                                                                |
| Chapter          | [x]          | Done.                                                                |
| Report           | [x]          | Done.                                                                |
| Ratelimits?      | [x]          | Ratelimits are handled per HTTP request following the standard flow. |


## Note about authentication
Sadly (thankfully?) I am not an author on MangaDex, meaning I cannot test the creation endpoints for things like scanlators, artists, authors, manga or chapters.
I have followed the API guidelines to the letter for these, but they may not work.

Any help in testing them is greatly appreciated.

## Note about upload/creation
Following the above, this means I also cannot test manga creation or chapter creation/upload.
These are currently a WIP.

## Examples
Please take a look at the [examples](./examples/) directory for working examples.

**NOTE**: More examples will follow as the library is developed.

### API caveats to note

- There are no API endpoints for Artist. It seems they are not differentiated from Author types except in name only.
- The tags are locally cached since you **must** pass UUIDs to the api (and I do not think you're going to memorize those), there's a convenience method for updating the local cache as `Client.update_tags`
  - I have added [an example](./examples/updating_local_tags.py) on how to do the above.
