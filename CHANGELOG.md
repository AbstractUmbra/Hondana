2.0.7

API Version 5.5.2!

# Hondana Changelog
**Fix release.**

## Added

## Changes
- Added `__repr__` to more objects for clarity if required. (d154ee298622adc5543039703bb96f05c1c81896)
- Rework exceptions internally because of DRY. (3eeb9feca5dc0277e02c765f9a085fb003be3faf)
- Exceptions now have a `.errors` attribute that is a list of `Error` sentinel types for ease of readability and access. (3eeb9feca5dc0277e02c765f9a085fb003be3faf)
- Add `response_id` attribute to Exceptions and add notes on their use in reporting errors to MangaDex. (a8af0d5fed061b155417c53baa18c7fea6949626)
- Added some notes to example and docs about using `DEBUG` level logging. (e26072ce1c321be6ce5b81f64e841e86d4e719cb)
- Performance change for `Manga.tags` where the property doesn't exist until accessed. (24cf17806adc3f1e9833433fa5e6da2cdd718388)
  - The above opens us up for further changes to these things where an objects creation would be less performance.
-

## Fixes
- Some typos in docs. (6265e8b59d3fd5c83b193888f5ae1847b9b95421)
- Actually create the enum type in `Manga.__init__`. (33d2517f73c38f49128114e52ff30c8ed9ffb0de)
- Token refresh datetime math was a little off, this has been fixed and renamed for ease of understanding. (fae516ac44f47d36a31dd4390c632ab803411575)

### Notes
