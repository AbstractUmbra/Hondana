2.0.2

API Version 5.4.10!

# Hondana Changelog

## Added
- `Chapter.manga_id` property added to retrieve the parent manga id from the payload (if present). (26464a41a1e95cbe6f26fd76470924199a87b1e0)

## Changes
- Internal change for the inner MD@H report http method kwarg only. (d22cbf5033692ffe9eef7fe28d995545d71ba1fb)
- Internal change for how collection endpoints managed their logic to return feeds. (7a3828d0f790a50e5600173f107ed52585c9d94e)

## Fixes
- `includes` parameter on `Client.get_chapter` was broken, this has been resolved. (d136064c7c1d3c154b1fb8cf8768c8debe264059)
- `Chapter.uploader` and `Chapter.scanlator_groups` now correctly get the data, which was initially caused by incorrect docs. (9bb7973a692155799eb9237e49b1beda12e7da1b)
- MD@H reports were erroring out when trying to report on `uploads.mangadex.org`, this has now been fixed. (cd33a6e816a130bbbfa628371c17198bdb978ffb)
- Inner payload types were amended to account for bad docs. (97a5c6ad4731d72b22972c181a8ac6d0c0d5b847)

### Notes
