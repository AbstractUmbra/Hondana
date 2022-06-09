3.0.4

API Version 5.5.10

# Hondana Changelog

## Added
- `Client.my_chapter_read_history()` method to return the current logged in user's read history as a rich type. Also adds necessary payloads and helper objects. (8e9c00467b3342a90f932c824e9a059c5eb12e97)
- Add `update_history` parameter to `Client.mark_chapter_as_read()` and `Chapter.mark_as_read()`, adds a default of `True` so it is not breaking. (371a1e90452db30d5893d62f94fb3cbea9a2f3b2)

## Changes
- `types.LocalisedString` has been removed in favour of the already existing `types.LocalizedString`. (c1b51f923e0e68aabd8ac181a23a93ac9e8ebb52)
- `Author.biography` and `Artist.biography` were reworked as they are localised. Also added the `localized_biography` method. (681ee6f5e2a27126ad875ae2fc1915673b2def56)

## Fixes
- Add a mutex/lock around the token generation at login/re-auth stages. Fixes a rare occurrence of doubly generating tokens with asynchronous requests. (8989537d009958b4e60ef932a07cdd5805478a8b)
- Fix incorrect types in `Author/Artist` biographies when the data is empty. Thanks PHP. (80b1aa4d34a7745e7d2b439b9e32be93cb15c3f0)
- Fix library `__repr__` and `__str__` methods be all uniform. (c44b9ed9211ad976a70e995370fdd0b16da2389f)

### Notes
- The `types` submodule has been reworked to not have all items imported at the top level to avoid namespace clutter. (3ff4ff5f16953935c4aa359ba7f581ae6c735481)
    - This means that `hondana.types.MangaResponse` should now be `hondana.types.manga.MangaResponse`.


### Noted Contributors
