<div align="center">
    <h1>Hondana 『本棚』</h1>
    <p>Hondana is the Japanese word for "bookshelf".</p>
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
<br>

A lightweight and asynchronous wrapper around the [MangaDex v5 API](https://api.mangadex.org/docs.html).

## Features
**NOTE** This library is still in development, I will list off the API methods and their progress here:

| Feature          | Implemented? | Notes                                              |
| ---------------- | ------------ | -------------------------------------------------- |
| Chapter Upload   | [ ]          | Soon:tm:                                           |
| Manga            | [x]          | Done. (pending tests on some endpoints)            |
| Cover            | [x]          | Done. (pending tests on some endpoints)            |
| Author           | [/]          | Soon:tm:                                           |
| Search           | [x]          | Done.                                              |
| Auth             | [x]          | Authentication is done per request, token handled. |
| Scanlation Group | [ ]          | Soon:tm:                                           |
| Feed             | [ ]          | Soon:tm:                                           |
| CustomList       | [ ]          | Soon:tm:                                           |
| AtHome           | [ ]          | Soon:tm:                                           |
| Legacy           | [ ]          | Soon:tm:                                           |
| Infrastructure   | [ ]          | Soon:tm:                                           |
| Upload           | [ ]          | Soon:tm:                                           |
| Account          | [ ]          | Soon:tm:                                           |
| User             | [ ]          | Soon:tm:                                           |
| Chapter          | [x]          | Done. (pending tests on some endpoints)            |
| Report           | [ ]          | Soon:tm:                                           |
| Ratelimits?      | [ ]          | Not part of the API spec but might be handy.       |


### In Progress: User
| Endpoint                                | Implemented? | Notes    |
| --------------------------------------- | ------------ | -------- |
| User List                               | [ ]          | Soon:tm: |
| Get User                                | [ ]          | Soon:tm: |
| Delete User                             | [ ]          | Soon:tm: |
| Approve User Deletion                   | [ ]          | Soon:tm: |
| Update User Password                    | [ ]          | Soon:tm: |
| Update User Email                       | [ ]          | Soon:tm: |
| Logged User details                     | [ ]          | Soon:tm: |
| Get Logged In User Followed Groups      | [ ]          | Soon:tm: |
| Check if Logged In User Follows a Group | [ ]          | Soon:tm: |
| Get Logged In User Followed User List   | [ ]          | Soon:tm: |
| Check if Logged In User follows a User  | [ ]          | Soon:tm: |
| Get Logged In User Followed Manga List  | [x]          | Done     |
| Check if Logged In User follows a Manga | [ ]          | Soon:tm: |


#### To Test: Manga
| Endpoint     | Tested? | Notes                              |
| ------------ | ------- | ---------------------------------- |
| Create Manga | [ ]     | Done. Unsure if I can test this... |
| Update Manga | [ ]     | Done. Unsure if I can test this... |
| Delete Manga | [ ]     | Done. Unsure if I can test this... |


#### To Test: Chapter
| Endpoint       | Tested? | Notes                               |
| -------------- | ------- | ----------------------------------- |
| Update Chapter | [ ]     | Done. Unsure if I can test this ... |
| Delete Chapter | [ ]     | Done. Unsure if I can test this ... |


#### To Test: Cover
| Endpoint   | Tested? | Notes                              |
| ---------- | ------- | ---------------------------------- |
| Edit Cover | [ ]     | Done. Unsure if I can test this... |


## Examples
Please take a look at the [examples](../Hondana/examples/) directory for working examples.

**NOTE**: More examples will follow as the library is developed.

### API caveats to note

- There are no API endpoints for Artist. Currently, if you query a manga without the `"artist"` query includes then you will not receive artist data.
- The tags are locally cached since you **must** pass UUIDs to the api (and I do not think you're going to memorise those), there's a convenience method for updating the local cache as `Client.update_tags`
