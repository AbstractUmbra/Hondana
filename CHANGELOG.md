2.0.13

API Version 5.5.6!

# Hondana Changelog

## Added
- `hondana.Relationship` type was added as a container type to relationship keys in payloads. (684447e75088302d42ca803ca31eee190a4aafdd)
- Added `.relationship` property to all relevant types to use the new `Relationship` container. (8d2c7584879a14a0e47fdcbe23497efe1ac8b7e7)
- `Manga.raw_description` property added to access raw payload to resolve #20. (d1b5a9824e3d926a52ea319aaa89d29eacc03d10)
- `Manga.localized_title` and `Manga.localized_description` locale alternative methods. (2b1091000fb373dc72d283458464d05e60bc93ca)
- (#18) Mostly internal change with how collection types work from the API. Mostly `XFeed` classes. Also add a `.items()` method to these. (f8cf30d523e9b9264e818bad467515297c718c8a)
- Add missing `fan_box` attribute on `Author` and `Artist`. (7ab0ef0ac4c08b01a579e33a095c0578c8fdb8c9)
- Expose `Manga.alt_titles`. (dbae6aeb36022b7b8e7fcecaf9a8c9836ff31fbb)
- Added missing attributes of `ScanlatorGroup` as well as a new util for creating string formats that MangaDex accepts for publish delays. (2d15d9cc2b4573015a71250821ce9f56f4024fc1)
- First attempt at a testing suite for the library. (1755fffde40faaeed35710f9df6dcfac630bbddf)

## Changes
- `Client.dump_refresh_token` is now kwarg only, and now accepts a `file` kwarg, which controls if it dumps to a file or not. (c5a348eaeb1a650c5ddd3efc29b3cdd8a3899772)
- Reworked internals of `Client.update_tags` to use the new `Client.get_tags`. (f4dc77aab922e8a33537be09af80763a1d40171d)
- Internal change to how datetime strings are sent to MangaDex. (b9c964bcc97964b2146149469710d726bff54026)
- Flatten attributes `Manga.alternate_titles` and `Tag.descriptions` to one `LocalisedString` instead of a list of them. (278651f3bcc3397dcfe75b7ce5cf061a0227005d and 4a149d7c1b2373439a70b8779f9bab0fc28c44cf)

## Fixes
- (#19) Rare case where `Manga.description` can `AttributeError` due to PHP-isms. (6bc91d03ca10052038397205e8bced35734434fe and e56e9ce7557c330fefb1bf9964608a6bad8048e3)
- Add extra layer of http request handling. (18434dcd3be880660828dd3d3503f74c926fe1de)
- (#21) `Chapter.scanlator_groups` would only return one instance, even if many were present. `Chapter.get_scanlator_groups()` filtered for the wrong type name, so would never return results. (45b54bfaff9f611e9c21fb3c582623ff8ec4505a)
- `Manga.localised_title` now checks the correct attribute, not a single element dict. (e364dc8ec617b386ff89e6d93ef9b532db42a4ee)

### Notes
- `Client.view_manga` method has been marked as deprecated in favour of `Client.view_manga` and will be removed in version 3.0. (588c2fdc2956db5435c2aa5792281d3a78ef7396)
