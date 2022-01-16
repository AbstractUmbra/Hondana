2.0.0

API Version 5.4.9!

# Hondana Changelog
*** Breaking Changes ***

## Added
- Small warning (docs) on `Chapter` about how the reference expansions will work when obtained via a feed. (6fa0d71089c051e446eef868d1bd94eaf649ea06)
- Multiple `Enum` types for use all over the library and queries. (1e4b5f1b9568cfb928baef3427d49f1939e352f3)

## Changes
- Removed `user` parameter in `Client.get_manga_draft_list`. (211c0f059131d62c1ea932eede83a7f3bc58b5f9)
- Internal change on how response payloads are handled from the API to minimize object size in memory. (0b4f56c280ba0b2db4d57dc2cbdf1936b34c18cc)
- A few internal changes to pre-flight release items and type-checking items.
- Non-impacting change where `extra/tags.json` and `Client.update_tags` will now be sorted alphabetically. (23f6e1b6e0d7789123bde747988d4fba7e4e1be1)
- Any `__repr__` methods that have UUIDs in them will now present these as strings. (4d26167ae220a7d67b65d426b4375956cec99c45)
- Any endpoint that returns a `collection` type from the API now has an appropriate `Collection` return type. (498ae19a5ab9c2abaa1ee18bd09cb7aa49f8e108)
- Update the examples to account for the above. (b02a39e229c3df0d1c0b707f071f78d6f16f83fe)

## Fixes
- Fix upload process to mention that `scanlator_groups` cannot be an Optional parameter. (d9ce7b4a696d9d343f4ee3238f524a96342c77c3)
- Fix in `Manga` where `Manga.authors` raise a `NameError`. (a7738da61267105b403e3f88494c27e9aebaba54)
- Fix caching issue in `Manga` where `Manga.artists` would NOT be populated with a `Manga.get_artists`. (a7738da61267105b403e3f88494c27e9aebaba54)
- Internal fixes for logger formatting. (b1d9d9117ac89a3b0c029b27476280968f678699)
- Some docs fixes. (e69af973377e2fdeddec62b3e2282848764db208 and e8fba94b8747ecdc4562ecffdcd712fe00abd904)
- Fix how the MissingSentinel was handled in the query builder. (ee217697e108b18ed0ddc8a2a0970b1a9a06bf9b)
- Fix underlying HTTP methods for a few items. (73dee86eeed5d30a2564cb2b9b75cc9546beef43)
- Fix how bools are handled as query parameters. (c5eedd84fd2e2d8af6f5239e728dc6b8eb018b45)

### Notes
- Expect a `2.0.1` soon as the settings template change has not been finalized until the front end catches up.
