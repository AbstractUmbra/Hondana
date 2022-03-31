2.2.1

API Version 5.5.8!

# Hondana Changelog

## Added
- `Client.get_my_custom_list_follows()` method was added to get all of the custom lists you follow. (44d6374089680e9fc703d2a3bffeeaa6dcdfa0c6)
- `Client.check_if_following_custom_list()` method was added to check if you currentlt follow a specific custom list. (44d6374089680e9fc703d2a3bffeeaa6dcdfa0c6)
- `Client.follow_custom_list()` and `CustomList.follow()` methods were added to allow you to follow a custom list. (44d6374089680e9fc703d2a3bffeeaa6dcdfa0c6)
- `Client.unfollow_custom_list()` and `CustomList.unfollow()` methods were added to allow you to unfollow a custom list. (44d6374089680e9fc703d2a3bffeeaa6dcdfa0c6)

## Changes
- `ChapterUpload` will now raise `ValueError` on initialisation if you try to provide more than 10 scanlator groups per upload. (5861a32f2e20360ea32f14eb0baee49223e9dd7e)
- Added optional `[speedup]` extra to the library install to add `orjson` as a dependency for faster json payload parsing. (96507e0c9dec67f0fca6417cb2b12e6bf566e1d9)
- Removed the dependency for `aiofiles` as the overhead was rather unnecessary in testing. (fe9501a8fffcba631cc7ee1820052f1b69ad2b9b)

## Fixes

### Notes
- `Client.view_manga` is marked as deprecated and due for removal in version 3.0 in favour of `Client.get_manga`.

### Noted Contributors
