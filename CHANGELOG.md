3.0.2

API Version 5.5.8!

# Hondana Changelog

## Added

## Changes
- `Client.get_chapter` has a new key word argument `fetch_full_manga`, as the Manga relationship has no relationships of it's own, so details are not present without another HTTP request. (390d47a13dd353747eef079072bdbbd1a97eca70)
- `Manga.cover_url` method's parameter was renamed from `type` to `size` to avoid a rare issue due to a reserved keyword. (26a39c272890023082b9be9aa0d39b66e938c7ef)
- Large documentation overhaul, which enabled type-hint signatures. This seems like overkill in most scenarios but it can help resolve types and defaults in the documentation. (daa063e69409cd70e4bdc2015bce77b27436c9ea)
  - More changes are intended, however I am waiting on a [bug in Sphinx](https://github.com/sphinx-doc/sphinx/issues/10305#issuecomment-1100726410) to be fixed before these can be done.
- Also added the documentation capability of showing the source code from the docs pages. (39e3283d353bd264f0f6780886bd7bd48d65ebc9)
- Allow user code to pass a custom sorting key to `ChapterUpload.upload_images`. (9a209e66fd3a7bbe97c4083bea49ebecb3e4ce2b)

## Fixes
- The underlying HTTP request method did not handle HTTP 503 errors from MangaDex, which are common when a cache lookup fails and the endpoint needs to be re-hit. This was fixed in #28. (f1a79e5b9430b529aa2bcdaddafc665393144848)
- `LegacyItem`'s `__repr__` displayed incorrect names for the attributes, this has been fixed. (17b7a73c85129b2a8202ccf14d200dacddde361f)
- Cleaned up the internal sorting method for chapter upload and removed an unneeded regex. (6264e51aa44cd8d44ce290defa4560df0736eabf)
- Added missing `includes` parameter on CustomList Manga Feed.

### Notes

### Noted Contributors
@PythonCoderAS - Fixing common errors HTTP error handling.
