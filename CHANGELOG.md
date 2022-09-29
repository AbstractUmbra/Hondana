3.2.0

API Version 5.7.1

# Hondana Changelog
Update to remove singular updates to (un)read markers on chapters.
This just means you must use the batch endpoint. This is noted within Hondana as `Client.batch_update_manga_read_markers`.
`Chapter.mark_as_read()` and `Chapter.mark_as_unread()` both now use the batch endpoint internallt.

## Added
`Manga.latest_uploaded_chapter` attribute has been added. (2407d39183b6191bb4a83b18aa1f7dc8231a2932)

## Changes
Deprecation of `Client.mark_chapter_as_read()` and `Client.mark_chapter_as_unread()` in favour of `Client.batch_update_manga_read_markers()`. (5b6070b55c51aae4cbe70dfe501f1ff1ab7fd06e)
Rename `Chapter.mark_chapter_as_unread()` to `Chapter.mark_as_unread()`. (3b20a5621133399a427fa85dafda366441cba730)

## Fixes
Fixed the handling of `Tag.description` as it was previously marked as the incorrect type. Handling it correctly and accouting for PHP empty-object-isms. (a2b8469690a04366b38f5cdfba20ac75a4158156)

### Notes

### Noted Contributors
