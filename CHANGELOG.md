2.0.12

API Version 5.5.6!

# Hondana Changelog

## Added
- `hondana.Relationship` type was added as a container type to relationship keys in payloads. (684447e75088302d42ca803ca31eee190a4aafdd)
- Added `.relationship` property to all relevant types to use the new `Relationship` container. (8d2c7584879a14a0e47fdcbe23497efe1ac8b7e7)

## Changes
- `Client.dump_refresh_token` is now kwarg only, and now accepts a `file` kwarg, which controls if it dumps to a file or not. (c5a348eaeb1a650c5ddd3efc29b3cdd8a3899772)
- Reworked internals of `Client.update_tags` to use the new `Client.get_tags`. (f4dc77aab922e8a33537be09af80763a1d40171d)

## Fixes
- Rare case where `Manga.description` can `AttributeError` due to PHP-isms. (6bc91d03ca10052038397205e8bced35734434fe)
- Add extra layer of http request handling. (18434dcd3be880660828dd3d3503f74c926fe1de)

### Notes
- `Client.view_manga` method has been marked as deprecated in favour of `Client.view_manga` and will be removed in version 3.0. (588c2fdc2956db5435c2aa5792281d3a78ef7396)
