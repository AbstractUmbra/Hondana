1.1.0

# Hondana Changelog

## Added

## Changes
- `hondana.*OrderQuery` has been moved to `hondana.query.*OrderQuery` (c67502bbf04d90d9485c87b75edf245b6d02fca6)
- `hondana.*Includes` has been moved to `hondana.query.*Includes`. (c67502bbf04d90d9485c87b75edf245b6d02fca6)
- Both of the above items now use `__slots__` for their internal validation, not a 'hidden' list. (c67502bbf04d90d9485c87b75edf245b6d02fca6)
## Fixes
- Some missed `__all__` defs in `client.py` caused the entire file to be exported in `__init__`, this is no longer the case. (8a4d1f6ba220a79adbb57594d1af6c4fdc2670dc)
- Docs changes for the above. (e717bb0044b4b9ba6284ed6840a9fed6e3c2f146)
- `*OrderQuery` actually didn't work when you passed only one of the params. Fixed now. (0b29d2a557b31a2e7cd0cf2129b2e105eb9d038f)

### Notes
