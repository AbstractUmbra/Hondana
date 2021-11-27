0.4.12

# Hondana Changelog

## Added
- `Manga.related` attribute with optional relation type key. (643d4e68742d8d99cc7245a1272ea4e7248eb5d5)
- `Manga.related_manga` property. (643d4e68742d8d99cc7245a1272ea4e7248eb5d5)
- `Manga.get_related_manga` method which will fetch and cache the related manga. (643d4e68742d8d99cc7245a1272ea4e7248eb5d5)
- `Artist.manga` property that returns all related manga to the artist. (404fe60ed6f225f31b955164844147ca35f11deb)
- `Artist.get_manga` method that will fetch and cache all related manga to the artist.  (404fe60ed6f225f31b955164844147ca35f11deb)
- `Author.manga` property that returns all related manga to the artist. (ecfaff276ae914799ce2bd79a2035f0183bf0e8d)
- `Author.get_manga` property that returns all related manga to the artist. (ecfaff276ae914799ce2bd79a2035f0183bf0e8d)
- `Client.create_author` now has all listed properties and new `biography` property. (35e767e06adc2702b12f447bdbc4aee7aa5a5cb5)
- `Client.update_author` now has all listed properties and new `biography` property. (35e767e06adc2702b12f447bdbc4aee7aa5a5cb5)
- `Author.update` now has all listed properties and new `biography` property. (35e767e06adc2702b12f447bdbc4aee7aa5a5cb5)
- `Client.update_artist` now has all listed properties and new `biography` property. (7ec9365326d35f232db46139fba542081fc5aff4)
- `Artist.update` now has all listed properties and new `biography` property. (7ec9365326d35f232db46139fba542081fc5aff4)

## Changes
- `Manga.get_author` -> `Manga.get_authors` and also now caches response. (643d4e68742d8d99cc7245a1272ea4e7248eb5d5)
- `Manga.get_artist` -> `Manga.get_artists` and also now caches response. (643d4e68742d8d99cc7245a1272ea4e7248eb5d5)
- `Manga.author` -> `Manga.authors` (643d4e68742d8d99cc7245a1272ea4e7248eb5d5)
- `Manga.artist` -> `Manga.artists` (643d4e68742d8d99cc7245a1272ea4e7248eb5d5)
- Internal only code cleanup with chapter download code. (76d7b64c5e850014dce4d80eb3fe497553c148f7)
- Internal changes to limit and offset clamping code. (35e767e06adc2702b12f447bdbc4aee7aa5a5cb5)

## Fixes

### Notes
