2.1.1

API Version 5.5.7!

# Hondana Changelog

## Added
- Added `Client.check_username_available` method as per the new endpoint. (9dee5bc9e96ce5f3dbce5290a2281914275518c2)
- Added base implementations for "Settings" section of API docs. (f99430038c445655ac8f441f0afc010adb4dca23)
  - Not fully released so implementation is barebones and in need of a nicer interface, blocked on full release.

## Changes
- Internal change to how the `limit` parameter works, now that `0` is an allowed minimum value. (6719705eb7a74fa09347b9bde7d8787a3aa5d3c3)
- Updated `hondana.types.Manga.MangaLinks` type to include missing keys and added descriptions. (1d205d09886985040a8c1d28356ba2c7298896f9)
- `Manga.status` is no longer nullable or null. (6f7e2905d9ba489f0f2537e664d3016e92bde027 and 2323c44b5aa75ea04e53abafd67b9b75d7833898)

## Fixes

### Notes
- `Client.view_manga` method has been marked as deprecated in favour of `Client.view_manga` and will be removed in version 3.0. (588c2fdc2956db5435c2aa5792281d3a78ef7396)
