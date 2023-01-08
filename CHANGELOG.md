3.4.7

API Version 5.9.0

# Hondana Changelog
API Release - more below!

## Added
- Forum/Thread/Comment api capability
    - Added various objects and methods, namely `hondana.ForumThread`, `hondana.MangaComments` (also `Chapter` and `ScanlatorGroup`), `Client.create_forum_thread` and `get_statistics` on `Chapter` and `ScanlatorGroup` objects. (2ab4ab4f529fd17e2083a804f9b58e000832447e and e45fb24082d0df599f8be12ee8f55ed44fef08aa primarily)

## Changes
- Remove `Client.find_manga_statistics` in favour of combining it with `Client.get_manga_statistics` and using two optional params for singular and plural. (e45fb24082d0df599f8be12ee8f55ed44fef08aa)
- Update library dependencies. (a1e8c92f545173b8abe6666b863bfcd8e0a782f9)

## Fixes
- GH Actions now have the `--pythonversion` flag for pyright workflows as per their matrix. Probably optional but wanted to cover it. (7850d34546f37b917ff94cbfd173e079a4182925)

### Notes
Added a warning and also a section on the README about the upcoming basic authentication deprecation on MangaDex's side.
The gist of which is that user/email and pass authentication will no longer be supported at an approaching but unspecified future date.
I am actively enquiring about getting the Client Credentials oauth2 flow enabled. See the library README for more info.

### Noted Contributors
