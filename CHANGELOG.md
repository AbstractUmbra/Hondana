1.1.9

API Version 5.4.7!

# Hondana Changelog

## Added
- `Client.fetch_manga_statistics` was added as a batch endpoint for manga statistics. ()

## Changes
- `Client.get_manga_statistics` was changed to only accept a single Manga ID as the parameter. ()
- `MangaStatistics.distribution` is now an Optional value due to it only being populated on the non-batch (`Client.get_manga_statistics` and `Manga.get_statistics`) endpoint. ()

## Fixes


### Notes
