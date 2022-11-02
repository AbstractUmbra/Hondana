3.4.4

API Version 5.7.5

# Hondana Changelog
API Release!

## Added
- New `author_or_artist` parameter on several methods for filter by a specific UUID that related to an author or artist of your choice. (fc8db94bc7b59d198a8227cbd9c6c03802d81c59)
  - Mainly affects `Client.manga_list()`
- Added missing pagination parameters and docstring entries for `Manga.get_related_manga()` and `CustomList.get_manga()`. (28903d40630d115240dbdee35286579ee8e8c31e)
- Add new filtering on chapter list endpoint (`Client.chapter_list()`). (b1178a3ea25c831577def282fb856dcf1f43687c)

## Changes

## Fixes
- New internal type to encompass all possible report reasons is now used in all relevant places. (40620dc6dbaa65f6977c7fe9727758fc3c6199dc)
- Docstring for `utils.php_query_builder()` has been amended. (1c8da4e393d5c77979409f2f8f98d7f6d058b253)

### Notes

### Noted Contributors
