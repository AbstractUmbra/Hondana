1.1.1

# Hondana Changelog

## Added
- `Chapter.get_at_home` method has been modified and made public. This is for retrieving the `MD@H` data for the chapter. (efbe38c0eca095c1d9f3b9f80fdeb5bae940745c)

## Changes
- `Chapter.hash`, `Chapter.data` and `Chapter.data_saver` are now gone due to MangaDex data structure changes.
    The data for these can be found in the response type from `Chapter.get_at_home()` (efbe38c0eca095c1d9f3b9f80fdeb5bae940745c)

## Fixes


### Notes
- Docs updated for the above. (efbe38c0eca095c1d9f3b9f80fdeb5bae940745c)
