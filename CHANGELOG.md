0.4.5

# Hondana Changelog

## Added
- `ScanlatorGroup.verified` attribute.
- `Chapter.scanlator_group` property.

## Changes
- `translated_languages` parameter in some places has been renamed to `translated_language` to be inline with the API.
- `Client.create_report` - all parameters are now required, not optional.

## Fixes
- Properly clamps pagination values now.
- `ScanlatorGroup.focused_language` -> `ScanlatorGroup.focused_languages`.

### Notes
