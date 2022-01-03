1.1.8

API Version 5.4.6!

# Hondana Changelog

## Added
- `Manga.status` now exists to tell you the current publication status. (7d2b8e8e1a0e86f26b69d87dced840dc80bfa686)
- `Manga.state` now exists to tell you about the release state. (7d2b8e8e1a0e86f26b69d87dced840dc80bfa686)
- `MangaStatistics.follows` now shows you the amount of total follows a manga has. (d28ae1596bf772fe7bdad167caafbbef20f90e08)
- `Chapter.pages` now exists to show the total amount of pages a chapter has, following the removal of the `data` and `dataSaver` keys from the Chapter payload. (d28ae1596bf772fe7bdad167caafbbef20f90e08)

## Changes
- `Manga.tags` is not built on the construction of `Manga` objects from their payloads. This is to offset the property running each time. (c32c7f5c87cf1c8b089209a0d0a3ead2c0dfefa7)


## Fixes


### Notes
