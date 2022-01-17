2.0.1

API Version 5.4.9!

# Hondana Changelog

## Added
- `LegacyMappingCollection` was added as it was missed with the last batch. (056925a05f36d2711c740e0ba92f7f3edf264f70)

## Changes
- `Manga.title` property now defaults to the `Manga.original_language` lookup key, not `"en"`. (64d0f703c6b491a11c946ed0b9868b3ee1c13210)
- `limit` parameter is now Optional in some endpoints to allow retrieval of maximum possible objects from the API with multiple requests. (64b383e3f970c53614f762371fedfadaa4e63f64)

## Fixes

### Notes
